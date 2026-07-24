"""Мост-поллер обратного канала (Phase 4.6): GET /v1/hints → локальный TTS.

Мост исторически односторонний. Здесь — фоновый asyncio-цикл, который живёт
РЯДОМ с тейлером лога (см. `_run_bridge` в __main__.py) и раз в ~1с забирает
СВОИ накопленные фразы (`EventClient.get_hints`) и озвучивает их системным TTS
(`LocalTTS.say`). Оба зависимости инъектируются как async-колбэки, поэтому цикл
тестируется без сети и без реальной речи.

Локальный дедуп: backend-очередь может отдать одну фразу дважды (re-emit
ARENA_START, перекрытие поллов) — не проговариваем один и тот же текст повторно
в пределах окна, чтобы речь не наслаивалась.
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


async def poll_hints_once(
    fetch: HintFetcher,
    speak: Speaker,
    player_name: str,
    dedup: LocalHintDedup,
) -> int:
    """Один проход: забрать фразы игрока и озвучить свежие/недублирующиеся.

    Возвращает число реально озвученных фраз (для тестов). Речь сериализуется
    (await на каждую), чтобы реплики не наслаивались.
    """
    phrases = await fetch(player_name)
    spoken = 0
    for phrase in phrases:
        if dedup.allow(phrase):
            await speak(phrase)
            spoken += 1
    return spoken


async def run_hint_poller(
    fetch: HintFetcher,
    speak: Speaker,
    player_name: str,
    stop_event: asyncio.Event,
    interval_s: float = 1.0,
    dedup_window_s: float = 6.0,
    clock: Callable[[], float] = time.monotonic,
) -> None:
    """Фоновый цикл поллинга обратного канала до сигнала stop.

    Ошибки fetch/speak поглощаются на их стороне (get_hints и LocalTTS.say
    best-effort и не бросают); здесь дополнительно страхуемся, чтобы одиночный
    сбой не убил цикл и не уронил мост.
    """
    dedup = LocalHintDedup(dedup_window_s, clock)
    log.info("Локальный голос-поллер запущен (интервал %.1fс, игрок %s)", interval_s, player_name)
    try:
        while not stop_event.is_set():
            try:
                await poll_hints_once(fetch, speak, player_name, dedup)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # страховка: цикл не должен падать
                log.debug("Поллер подсказок: проход не удался (%s)", exc)
            # сон, прерываемый сигналом остановки
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(stop_event.wait(), timeout=interval_s)
    except asyncio.CancelledError:
        raise
    finally:
        log.info("Локальный голос-поллер остановлен")
