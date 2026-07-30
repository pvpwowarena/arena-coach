"""Мост-поллер обратного канала: GET /v1/hints → локальный TTS.

Мост исторически односторонний. Здесь — фоновый asyncio-цикл, который живёт
РЯДОМ с тейлером лога (см. `_run_bridge` в __main__.py) и забирает СВОИ
накопленные фразы (`EventClient.get_hints`), чтобы озвучить их системным TTS
(`LocalTTS.say`). Зависимости инъектируются как async-колбэки, поэтому цикл
тестируется без сети и без реальной речи.

**Phase 4.12 — почему тут «свежее вытесняет старое».** В живом тесте 30.07 бой
успевал закончиться, пока голос ещё зачитывал начало. Причина была прямо в этом
файле: речь синтезировалась ВНУТРИ цикла (`await speak(...)`), то есть пока
читалась фраза, мост не опрашивал бэкенд, а очередь копилась и превращалась в
монолог из прошлого. Теперь:

  • опрос и речь разведены: цикл только забирает фразы и кладёт их в
    `SpeechChannel`, речь идёт отдельной задачей — опрос больше не встаёт;
  • канал держит ОДНУ ожидающую фразу: пришла новая — старая ожидающая
    отбрасывается (в арене свежий совет отменяет прошлый, а не дополняет его);
  • просроченная фраза (`max_age_s`) не произносится вообще — «тринкеть под
    кидни» через восемь секунд вредно.

Локальный дедуп по тексту остаётся страховкой от повторов backend-очереди.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Awaitable, Callable

log = logging.getLogger(__name__)

#: Забрать фразы игрока: player_name → список фраз (best-effort, не бросает).
HintFetcher = Callable[[str], Awaitable[list[str]]]
#: Озвучить фразу локально: text → успех (best-effort, не бросает).
Speaker = Callable[[str], Awaitable[bool]]

#: Через сколько секунд ожидающая фраза считается протухшей и не произносится.
DEFAULT_MAX_AGE_S = 6.0


class LocalHintDedup:
    """Анти-дубль: не повторять одну и ту же фразу в пределах окна."""

    def __init__(self, window_s: float, clock: Callable[[], float] = time.monotonic) -> None:
        self._window_s = window_s
        self._clock = clock
        self._last_said: dict[str, float] = {}

    def allow(self, phrase: str) -> bool:
        now = self._clock()
        # чистим протухшие записи, чтобы словарь не рос
        cutoff = now - self._window_s
        for key in [k for k, t in self._last_said.items() if t < cutoff]:
            del self._last_said[key]
        last = self._last_said.get(phrase)
        if last is not None and now - last < self._window_s:
            return False
        self._last_said[phrase] = now
        return True


class SpeechChannel:
    """Канал речи: одна фраза озвучивается, одна ждёт, остальные отбрасываются.

    Это и есть лекарство от «бой кончился, а он всё говорит»: пока идёт речь,
    новые фразы не выстраиваются в очередь, а вытесняют друг друга — произнесена
    будет только самая свежая, и только если не протухла.
    """

    def __init__(
        self,
        speak: Speaker,
        clock: Callable[[], float] = time.monotonic,
        max_age_s: float = DEFAULT_MAX_AGE_S,
    ) -> None:
        self._speak = speak
        self._clock = clock
        self._max_age_s = max_age_s
        self._pending: tuple[str, float] | None = None
        self._task: asyncio.Task[None] | None = None
        self.spoken = 0
        self.dropped = 0

    @property
    def busy(self) -> bool:
        """Идёт ли сейчас речь."""
        return self._task is not None and not self._task.done()

    def offer(self, phrase: str) -> None:
        """Предложить фразу к озвучке; вытесняет предыдущую ожидающую."""
        if self._pending is not None:
            self.dropped += 1
            log.debug("Голос: ожидающая фраза вытеснена более свежей")
        self._pending = (phrase, self._clock())

    def pump(self) -> None:
        """Если канал свободен и есть свежая фраза — запустить озвучку задачей."""
        if self.busy or self._pending is None:
            return
        phrase, queued_at = self._pending
        self._pending = None
        age = self._clock() - queued_at
        if age > self._max_age_s:
            self.dropped += 1
            log.debug("Голос: фраза протухла за %.1fс, не произносим", age)
            return
        self._task = asyncio.ensure_future(self._run(phrase))

    async def _run(self, phrase: str) -> None:
        try:
            await self._speak(phrase)
            self.spoken += 1
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # TTS best-effort, мост важнее
            log.debug("Голос: не удалось произнести (%s)", exc)

    async def drain(self) -> None:
        """Дождаться конца текущей речи (тесты и graceful shutdown)."""
        if self._task is not None:
            with contextlib.suppress(Exception):
                await self._task

    def cancel(self) -> None:
        """Прервать текущую речь (остановка моста)."""
        if self.busy and self._task is not None:
            self._task.cancel()


async def poll_hints_once(
    fetch: HintFetcher,
    speak: Speaker,
    player_name: str,
    dedup: LocalHintDedup,
    channel: SpeechChannel | None = None,
) -> int:
    """Один проход: забрать фразы игрока и отдать свежие в канал речи.

    Возвращает число принятых фраз. Без переданного канала создаётся временный, и
    проход дожидается конца речи — это удобно в тестах и не меняет старый контракт.
    """
    own_channel = channel is None
    ch = channel or SpeechChannel(speak)
    phrases = await fetch(player_name)
    accepted = 0
    for phrase in phrases:
        if dedup.allow(phrase):
            ch.offer(phrase)
            accepted += 1
    ch.pump()
    if own_channel:
        await ch.drain()
    return accepted


async def run_hint_poller(
    fetch: HintFetcher,
    speak: Speaker,
    player_name: str,
    stop_event: asyncio.Event,
    interval_s: float = 0.5,
    dedup_window_s: float = 6.0,
    clock: Callable[[], float] = time.monotonic,
    max_age_s: float = DEFAULT_MAX_AGE_S,
) -> None:
    """Фоновый цикл поллинга обратного канала до сигнала stop.

    Опрос идёт независимо от речи: `SpeechChannel` озвучивает отдельной задачей,
    поэтому длинная фраза больше не тормозит следующий опрос (Phase 4.12).
    """
    dedup = LocalHintDedup(dedup_window_s, clock)
    channel = SpeechChannel(speak, clock, max_age_s)
    log.info("Локальный голос-поллер запущен (интервал %.1fс, игрок %s)", interval_s, player_name)
    try:
        while not stop_event.is_set():
            try:
                await poll_hints_once(fetch, speak, player_name, dedup, channel)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # страховка: цикл не должен падать
                log.debug("Поллер подсказок: проход не удался (%s)", exc)
            # сон, прерываемый сигналом остановки
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(stop_event.wait(), timeout=interval_s)
    except asyncio.CancelledError:
        channel.cancel()
        raise
    finally:
        log.info(
            "Локальный голос-поллер остановлен (произнесено %d, отброшено %d)",
            channel.spoken,
            channel.dropped,
        )
