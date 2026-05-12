# Architecture

См. [`phase-0-design.md`](phase-0-design.md) — полный design document с mermaid-диаграммой компонентов, потоков данных и обоснованием решений.

Этот файл — короткий обзор-указатель.

## Компоненты

| Артефакт | Где живёт | Язык | Phase |
|----------|-----------|------|-------|
| `addon/` | WoW client (`Interface/AddOns/ArenaCoach/`) | Lua 2.4.3 | 3 |
| `bridge/` | Игровая машина игрока | Python 3.11+ | 4 |
| `backend/` | VPS (Ubuntu 22.04) | Python 3.11+ | 2 (API+бот) / 4 (orchestrator) |
| `ingest/` | Dev-машина (CLI) | Python 3.11+ | 1 (готово) |
| `kb/` | Версионируется в git | Markdown + JSON | 1 (готово, 22 драфта) |

## Потоки данных

```
WoW client → addon (Lua)
              ↓
              SavedVariables.lua (post-match) + chat-log (realtime, см. ADR-0003)
              ↓
            bridge (Python, локально)
              ↓ WSS, bearer-auth
            backend (FastAPI на VPS)
              ↓ retrieve from KB + LLM synth (Sonnet/Haiku)
            Discord (приватный канал, player-role)
```

## Ключевые ADR

| ADR | Тема | Status |
|-----|------|--------|
| [0001](decisions/0001-python-stack.md) | Python 3.11+ как основной стек | Accepted |
| [0002](decisions/0002-sqlite-vs-postgres.md) | SQLite + FTS5 на старте | Accepted |
| [0003](decisions/0003-chatframe-realtime-channel.md) | Chat-frame mirror как realtime канал | Accepted |
