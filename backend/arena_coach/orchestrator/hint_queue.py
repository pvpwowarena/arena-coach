"""Обратный канал бэкенд → мост (Phase 4.6): очередь персональных голосовых фраз.

Мост (`bridge/arena_bridge`) исторически односторонний: tail лога → POST /v1/events.
Для локального персонального голоса нужен обратный поток: pipeline формирует
короткую фразу (ту же, что для Discord-голоса, см. `voice_phrases.py`), кладёт её
в очередь под именем игрока, а мост игрока раз в ~1с забирает СВОИ фразы через
`GET /v1/hints?player=<name>` и озвучивает их локальным TTS.

Свойства очереди:
  • per-player: `dict[player_name → deque[LocalHint]]` (ключ — lower(player_name),
    как whitelist-lookup в pipeline);
  • TTL ~10с: в бою устаревшая подсказка вредна («тринкетни сейчас» через 8с —
    дезинформация), поэтому протухшие фразы не отдаём и дропаем;
  • кап на игрока (`deque(maxlen=...)`) — всплеск событий не раздувает память;
  • кап на число игроков — при переполнении вытесняем наименее активного.

Модуль чистый и синхронный (без discord/httpx/сети): pipeline (api-процесс)
пишет, эндпоинт (api-процесс) читает. Часы инъектируются для юнит-тестов.
"""

from __future__ import annotations

import logging
import time
from collections import OrderedDict, deque
from collections.abc import Callable
from dataclasses import dataclass

log = logging.getLogger(__name__)

#: Через сколько секунд накопленная фраза считается протухшей и не отдаётся мосту.
DEFAULT_TTL_S = 10.0
#: Сколько максимум фраз держим на одного игрока (защита от всплеска событий).
DEFAULT_MAX_PER_PLAYER = 8
#: Сколько максимум игроков держим одновременно (защита от роста при офлайн-мостах).
DEFAULT_MAX_PLAYERS = 64


@dataclass
class LocalHint:
    """Одна голосовая фраза в очереди игрока."""

    phrase: str
    created_at: float  # монотонные секунды (self._clock())


class HintQueue:
    """In-memory очередь персональных фраз: player_name → недавние фразы.

    Потокобезопасность не требуется: и запись (pipeline), и чтение (эндпоинт)
    живут в одном asyncio-loop api-процесса и не делают await между операциями
    над очередью.
    """

    def __init__(
        self,
        ttl_s: float = DEFAULT_TTL_S,
        max_per_player: int = DEFAULT_MAX_PER_PLAYER,
        max_players: int = DEFAULT_MAX_PLAYERS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._ttl_s = ttl_s
        self._max_per_player = max_per_player
        self._max_players = max_players
        self._clock = clock
        # OrderedDict — порядок = давность последней активности (move_to_end при push),
        # чтобы вытеснять наименее активного игрока (popitem(last=False)).
        self._queues: OrderedDict[str, deque[LocalHint]] = OrderedDict()

    def __len__(self) -> int:
        """Число игроков с непустой очередью (для тестов/диагностики)."""
        return len(self._queues)

    def push(self, player_name: str, phrase: str, now: float | None = None) -> None:
        """Положить фразу в очередь игрока. Пустые имя/фраза игнорируются.

        Идентичность игрока — по имени персонажа (как в POST /v1/events и в
        whitelist-lookup): ключ приводится к lower().
        """
        if not player_name or not phrase.strip():
            return
        t = self._clock() if now is None else now
        self._purge_stale(t)

        key = player_name.lower()
        dq = self._queues.get(key)
        if dq is None:
            # Новый игрок: если достигли капа — вытесняем наименее активного.
            while len(self._queues) >= self._max_players:
                evicted, _ = self._queues.popitem(last=False)
                log.debug("HintQueue: вытеснен наименее активный игрок %s (кап)", evicted)
            dq = deque(maxlen=self._max_per_player)
            self._queues[key] = dq
        dq.append(LocalHint(phrase=phrase, created_at=t))
        self._queues.move_to_end(key)  # игрок только что активен — в конец

    def pop_fresh(self, player_name: str, now: float | None = None) -> list[str]:
        """Изъять и вернуть свежие (не протухшие) фразы игрока; очередь очищается.

        Мост дренирует свою очередь этим вызовом раз в ~1с. Протухшие по TTL
        фразы отбрасываются (в бою устаревшая подсказка вредна).
        """
        if not player_name:
            return []
        t = self._clock() if now is None else now
        key = player_name.lower()
        dq = self._queues.pop(key, None)  # полностью изымаем — эндпоинт «вычищает»
        if not dq:
            return []
        return [hint.phrase for hint in dq if t - hint.created_at <= self._ttl_s]

    def _purge_stale(self, now: float) -> None:
        """Удалить игроков, у которых все фразы протухли (офлайн-мост не дренирует).

        Кап на число игроков и так ограничивает память, но чистка держит
        `__len__`/итерацию честными и освобождает слоты активным игрокам.
        """
        stale = [
            key
            for key, dq in self._queues.items()
            if not dq or all(now - hint.created_at > self._ttl_s for hint in dq)
        ]
        for key in stale:
            del self._queues[key]
