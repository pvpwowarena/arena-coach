# Arena Coach Bridge

Локальный Python-демон. Крутится у игрока на той же машине, где WoW-клиент.

> **Статус:** Phase 4 skeleton. Конкретная реализация — в Phase 4.

## Что делает (Phase 4)

1. **sv_tail.py** — следит за `SavedVariables/ArenaCoach.lua`, диффит изменения, шлёт post-match summary.
2. **chat_tail.py** — следит за `Logs/Chat-*.txt`, ловит строки `[AC|<base64-JSON>]`, отправляет realtime события.
3. **normalizer.py** — приводит сырые события к каноническому формату из [phase-0-design §6.3](../docs/phase-0-design.md).
4. **ws_client.py** — устойчивое WSS-соединение с backend'ом, bearer-auth, авто-reconnect.

## Зачем

WoW Lua API не имеет сетевых функций, и SavedVariables пишется только на `/reload`/logout. Bridge — единственный легитимный способ перетащить телеметрию из клиента в внешний backend в реальном времени (через chat-log файл).

См. [ADR-0003](../docs/decisions/0003-chatframe-realtime-channel.md) для деталей.

## Конфиг (Phase 4)

`.env`:

```
ARENA_COACH_BACKEND_URL=wss://coach.example.com/ws
ARENA_COACH_BRIDGE_TOKEN=<per-player bearer>
ARENA_COACH_WOW_PATH=/path/to/World of Warcraft
ARENA_COACH_WOW_ACCOUNT=YOURACCOUNT
```

## ToS

Bridge — read-only: только чтение файлов клиента WoW (`SavedVariables.lua` и `Logs/Chat-*.txt`). Никакой модификации игрового стейта, никакого чтения памяти процесса, никакой автоматизации действий за игрока. См. [`docs/decisions/0003-chatframe-realtime-channel.md`](../docs/decisions/0003-chatframe-realtime-channel.md).
