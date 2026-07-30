"""Очередь отправки: чтение лога НИКОГДА не ждёт сеть — Phase 4.18.

Корень 26-секундной задержки (разбор 30.07, `docs/phase-4.18-latency.md`):
`await client.send(payload)` стоял ВНУТРИ `async for raw_line in tailer.lines()`.
Каждое событие блокировало чтение на длительность POST (0.3-1.5с, а при 500-х
и ретраях — до 10с), и в бою мост отставал накопительно, не догоняя.

Здесь чтение и отправка разведены:

  тейлер → `EventSender.submit()` (без ожидания) → asyncio.Queue → воркер → POST

Переполнение очереди = drop-OLDEST. В арене свежее событие ценнее старого:
просроченная подсказка не просто бесполезна — она вредна («кик!» после каста).
По той же причине воркер отбрасывает события, пролежавшие в очереди дольше
`stale_after_s`: сеть отвалилась → догонять нечего, надо жить дальше.

Всё, что мост измеряет о задержках, считается тоже здесь (`SendStats`).
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

log = logging.getLogger(__name__)

#: Сколько событий держим в очереди. Больше держать бессмысленно: если отставание
#: дошло до десятков событий, «догонять» уже нечего — бой давно ушёл вперёд.
DEFAULT_MAX_QUEUE = 32

#: Событие старше этого возраста в очереди отправляется в мусор, а не в сеть.
DEFAULT_STALE_AFTER_S = 5.0

#: Порог, с которого задержка «лог → отправка» попадает в лог как предупреждение.
LAG_WARN_S = 1.0

#: Событие боя, пролежавшее в ЛОГЕ дольше этого, не отправляем вовсе.
#:
#: Живой тест 30.07: голос произнёс подсказку уже ПОСЛЕ выхода с арены. Механика —
#: не в голосе: мост отставал от лога на десятки секунд, бэкенд получал событие
#: свежим (TTL очереди голоса считается от момента постановки) и честно озвучивал
#: то, что случилось полминуты назад. Отставание мы уменьшили, но убрать не можем:
#: клиент буферизует запись лога на тихих фазах, и это не в нашей власти.
#: Поэтому годность считаем по времени СОБЫТИЯ, а не по времени доставки.
STALE_LOG_LAG_S = 3.0

#: Типы, которые протухают. `ARENA_START`/`ARENA_END` пропускаем всегда: состав и
#: постматч ценны и с опозданием, а вот «кик!» через 10 секунд — вредная помеха.
PERISHABLE_PREFIXES = ("ABILITY#", "TRINKET#")


def _is_perishable(label: str) -> bool:
    return label.startswith(PERISHABLE_PREFIXES)


#: `send(payload, durable=...)` — второй аргумент говорит клиенту, стоит ли упорствовать.
SendFn = Callable[..., Awaitable[bool]]


@dataclass
class SendStats:
    """Счётчики конвейера — печатаются в лог, помогают ловить регрессии вживую."""

    submitted: int = 0
    sent: int = 0
    failed: int = 0
    dropped_full: int = 0
    dropped_stale: int = 0
    dropped_late: int = 0
    max_post_s: float = 0.0
    max_lag_s: float = 0.0

    def summary(self) -> str:
        return (
            f"отправлено {self.sent}/{self.submitted}, ошибок {self.failed}, "
            f"выброшено (очередь полна/очередь протухла/лог отстал) "
            f"{self.dropped_full}/{self.dropped_stale}/{self.dropped_late}, "
            f"худший POST {self.max_post_s:.2f}с, худшее отставание от лога "
            f"{self.max_lag_s:.2f}с"
        )


@dataclass
class _Item:
    payload: dict[str, Any]
    queued_at: float
    #: Отставание «время строки в логе ↔ wall-clock» в момент постановки (сек).
    log_lag_s: float | None
    label: str
    #: Событие не протухает → пережидаем перезапуск бэкенда, а не сдаёмся сразу.
    durable: bool = False


class EventSender:
    """Фоновый отправитель событий. `submit()` не блокирует и не бросает."""

    def __init__(
        self,
        send: SendFn,
        max_queue: int = DEFAULT_MAX_QUEUE,
        stale_after_s: float = DEFAULT_STALE_AFTER_S,
    ) -> None:
        self._send = send
        self._stale_after_s = stale_after_s
        self._queue: asyncio.Queue[_Item] = asyncio.Queue(maxsize=max_queue)
        self._task: asyncio.Task[None] | None = None
        self.stats = SendStats()

    # ── жизненный цикл ──────────────────────────────────────────────────

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.ensure_future(self._worker())

    async def stop(self, drain_timeout_s: float = 2.0) -> None:
        """Дать воркеру дошептать очередь и остановиться (best-effort)."""
        if self._task is None:
            return
        try:
            await asyncio.wait_for(self._queue.join(), timeout=drain_timeout_s)
        except asyncio.TimeoutError:
            log.debug("Очередь отправки не опустела за %.1fс — выходим как есть", drain_timeout_s)
        self._task.cancel()
        with contextlib.suppress(BaseException):  # на выходе гасим всё
            await self._task
        self._task = None

    # ── вход (вызывается из цикла чтения лога) ──────────────────────────

    def submit(self, payload: dict[str, Any], log_lag_s: float | None, label: str = "") -> None:
        """Поставить событие в очередь. НИКОГДА не ждёт и не бросает исключение."""
        self.stats.submitted += 1
        if log_lag_s is not None:
            self.stats.max_lag_s = max(self.stats.max_lag_s, log_lag_s)
            if log_lag_s >= LAG_WARN_S:
                log.warning(
                    "Отставание от лога %.2fс на событии %s — читаем медленнее, чем пишет клиент",
                    log_lag_s,
                    label or "?",
                )
        if log_lag_s is not None and log_lag_s > STALE_LOG_LAG_S and _is_perishable(label):
            self.stats.dropped_late += 1
            log.warning(
                "Событие %s случилось %.1fс назад — не отправляю: подсказка о нём уже "
                "не подсказка, а помеха",
                label or "?",
                log_lag_s,
            )
            return
        item = _Item(
            payload=payload,
            queued_at=time.monotonic(),
            log_lag_s=log_lag_s,
            label=label,
            durable=not _is_perishable(label),
        )
        while True:
            try:
                self._queue.put_nowait(item)
                return
            except asyncio.QueueFull:
                try:
                    old = self._queue.get_nowait()
                except asyncio.QueueEmpty:  # pragma: no cover — гонок нет, мы однопоточны
                    continue
                self._queue.task_done()
                self.stats.dropped_full += 1
                log.warning(
                    "Очередь отправки полна — выбрасываю САМОЕ СТАРОЕ событие (%s). "
                    "Свежая подсказка важнее догоняющей.",
                    old.label or "?",
                )

    # ── воркер ──────────────────────────────────────────────────────────

    async def _worker(self) -> None:
        while True:
            item = await self._queue.get()
            try:
                await self._deliver(item)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # воркер обязан пережить любую ошибку отправки
                self.stats.failed += 1
                log.error("Отправка события упала: %s", exc)
            finally:
                self._queue.task_done()

    async def _deliver(self, item: _Item) -> None:
        waited = time.monotonic() - item.queued_at
        if waited > self._stale_after_s:
            self.stats.dropped_stale += 1
            log.warning(
                "Событие %s пролежало в очереди %.1fс — не отправляю (подсказка протухла)",
                item.label or "?",
                waited,
            )
            return
        started = time.monotonic()
        ok = await self._send(item.payload, durable=item.durable)
        post_s = time.monotonic() - started
        self.stats.max_post_s = max(self.stats.max_post_s, post_s)
        if ok:
            self.stats.sent += 1
        else:
            self.stats.failed += 1
            log.warning("Событие потеряно: %s", item.label or "?")
        total = (item.log_lag_s or 0.0) + waited + post_s
        log.debug(
            "Событие %s: лог→мост %.2fс + очередь %.2fс + POST %.2fс = %.2fс",
            item.label or "?",
            item.log_lag_s or 0.0,
            waited,
            post_s,
            total,
        )


@dataclass
class LagClock:
    """Считает «время строки в логе ↔ wall-clock».

    Combat-лог пишет локальное время без таймзоны, поэтому сравниваем с
    `datetime.now()`. Год в логе есть, так что переход через полночь не ломает.
    Отрицательную разницу (часы клиента чуть впереди) считаем нулём.
    """

    now: Callable[[], datetime] = datetime.now

    def lag_s(self, line_ts: datetime | None) -> float | None:
        if line_ts is None:
            return None
        delta = (self.now() - line_ts).total_seconds()
        return max(0.0, delta)
