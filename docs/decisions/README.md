# Architecture Decision Records

Здесь живут ADR'ы — короткие документы, фиксирующие важные архитектурные решения с контекстом, альтернативами и последствиями.

Каждый ADR неизменен после принятия. Если решение пересматривается — создаётся новый ADR со ссылкой на старый.

## Список

| ID | Заголовок | Status |
|----|-----------|--------|
| [0001](0001-python-stack.md) | Python 3.11+ как основной язык | Accepted |
| [0002](0002-sqlite-vs-postgres.md) | SQLite + FTS5 на старте | Accepted |
| [0003](0003-chatframe-realtime-channel.md) | Chat-frame mirror как realtime канал | Accepted |

## Шаблон

```markdown
# ADR-NNNN: <Короткий заголовок>

- **Status:** Proposed | Accepted | Deprecated | Superseded by ADR-MMMM
- **Date:** YYYY-MM-DD
- **Deciders:** <имена>
- **Tags:** <свободные теги>

## Context
Что вынудило принять решение. Какие constraints были.

## Decision
Что именно решили. Конкретно.

## Alternatives Considered
Что отвергли и почему.

## Consequences
Позитивные и негативные последствия. Trade-off'ы.

## Validation
Как проверим, что решение работает. Что увидим / измерим.

## Rollback plan (опционально)
Если придётся откатиться — как.
```
