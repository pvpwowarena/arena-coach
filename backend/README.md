# Arena Coach Backend

FastAPI + discord.py + LLM-оркестратор + KB-store + whitelist. Крутится на VPS.

> **Статус Phase 1:** реализованы `kb/schema.py` (pydantic-модель) и `kb/loader.py` (парсер + валидация). Остальное (API, бот, оркестратор, access) — Phase 2/4 skeleton'ы.

## Что готово в Phase 1

- `arena_coach.kb.schema` — pydantic-модель `KBDoc` со всеми полями из [phase-0-design §3](../docs/phase-0-design.md).
- `arena_coach.kb.loader` — парсер `.md` → `KBDoc`, резолвер `[[ability:slug]]` через глоссарий, CLI `python -m arena_coach validate-kb <dir>`.

## Что прибудет позже

| Модуль | Phase | Описание |
|--------|-------|----------|
| `api/` | 2 | FastAPI app, routes (kb, whitelist, audit, /ws/bridge) |
| `bot/` | 2 | discord.py: slash-команды, ephemeral, whitelist-decorators |
| `access/` | 2 | SQLAlchemy whitelist, Fernet-шифрование ников, append-only audit-JSONL |
| `orchestrator/` | 4 | Anthropic SDK wrapper, RAG-pipeline (event → matchup → retrieve → synth) |

## Демо Phase 1

```bash
cd /path/to/arena-coach
PYTHONPATH=backend python -m arena_coach validate-kb kb/drafts
# OK: 22 документов прошли валидацию
```
