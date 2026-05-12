# ADR-0002: SQLite (с FTS5) как основная БД на старте; миграция на PostgreSQL — отложена

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** Vladislav, Arena Coach Dev
- **Tags:** storage, db

## Context

Backend хранит:

- Whitelist (несколько десятков записей максимум) с шифрованными игровыми никами.
- Index для KB-документов (full-text search, в перспективе — векторный для RAG).
- Audit log: уже принято писать в append-only JSONL (см. §5.3 design), **не в БД** — это намеренное архитектурное решение для неотвергаемости.
- Опционально: кеш LLM-ответов, retrieval-метрики (Phase 4).

Размер данных: KB — десятки матчапов × ~5 KB Markdown = меньше мегабайта. Whitelist — байты. Глоссарий — десятки KB. Логи событий bridge'а складываем отдельно от БД (или в JSONL, или в отдельный лёгкий time-series store, обсудим в Phase 4).

VPS — единственная инстанция backend'а; multi-region / multi-writer не нужен.

## Decision

**SQLite 3.40+** через `aiosqlite` (для async-доступа из FastAPI) + **FTS5** (полнотекстовый поиск) для KB-индекса.

- Файл БД: `/var/lib/arena-coach/coach.db` (вне репо, в .gitignore).
- Backup: nightly `sqlite3 .backup` → gzip → upload в S3-compatible storage (B2/R2/MinIO, выбирается в Phase 2).
- Миграции через Alembic — даже для SQLite, чтобы upgrade-path на Postgres был механическим, а не «руками».

Векторный поиск (Phase 4+): начнём с `sqlite-vec` (расширение SQLite); если ограничения станут проблемой — выделим Chroma/Qdrant как отдельный сервис.

## Alternatives Considered

### PostgreSQL с нуля
- **Плюсы:** строгая типизация колонок, JSONB, pgvector для RAG, готовая база под концурентность.
- **Минусы:** требует отдельного процесса на VPS, бэкапы сложнее, dev-setup тяжелее (Docker compose или systemd unit), для одного процесса бота — overkill.
- **Вердикт:** отвергнуто на v1. Если на Phase 4 поймём, что одновременных bridge-сессий много (несколько игроков пишут одновременно) и SQLite write-lock начнёт мешать — мигрируем. Alembic-схема пишется так, чтобы это было нажатие кнопки.

### Plain JSON-файлы для whitelist
- **Плюсы:** нулевая инфраструктура.
- **Минусы:** нет транзакций → race condition'ы при concurrent admin-командах; шифровать каждую запись отдельно — самопал.
- **Вердикт:** отвергнуто. Whitelist — critical security-плоскость, лучше SQL.

### DuckDB
- **Плюсы:** аналитика, OLAP.
- **Минусы:** не наш кейс — нужен OLTP (whitelist mutate'ы, audit-вставки), а не аналитика.
- **Вердикт:** отвергнуто.

## Consequences

**Позитивные:**

- Один файл, один процесс, нулевая ops-нагрузка на старте.
- Бэкап = `cp` или `sqlite3 .backup` (атомарный).
- Полнотекст через FTS5 без отдельных индексаторов.

**Негативные / trade-off'ы:**

- Concurrent writes (несколько bridge-сессий + admin-mutate одновременно) могут давать `database is locked`. Митигация: write-операции через единственный async writer-task (queue), reads напрямую.
- `sqlite-vec` менее зрелый, чем pgvector. На Phase 4 пересматриваем, если retrieval-качество просядет.

## Validation

Phase 2: интеграционный тест 10 одновременных whitelist-чтений + 1 mutate; убеждаемся в отсутствии deadlock'ов. Phase 4: latency p95 retrieval < 100 ms на 50 KB-документах.

## Migration path (когда понадобится Postgres)

1. Alembic-схема уже совместима (избегаем SQLite-specific типов в моделях).
2. `pgloader` или ручной dump+load.
3. Изменение `DATABASE_URL` в `.env`.
4. Запуск backend на staging-VPS, full test suite.
5. Cutover. Старая `.db` сохраняется как backup.

Ожидаемый объём работы при миграции: < 1 рабочего дня.
