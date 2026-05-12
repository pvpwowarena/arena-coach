# Knowledge Base (KB)

Source of truth для всего, что Arena Coach знает о матчапах.

## Структура

```
kb/
├── matchups/            # Approved KB-документы (confidence != draft, reviewer заполнен)
├── drafts/              # Свежеингестированные документы, ждут human review
│   └── .rejected/       # Reject'ed драфты с reason
├── glossary/
│   ├── abilities.json   # Способности: slug, en_name, icon, spell_id, dr_category
│   └── terms.md         # Арена-жаргон (DR, premed, shatter, sap-stall, blanket CS)
├── compositions.json    # Canonical comp slugs
└── README.md            # ← этот файл
```

## Контракт KB-документа

См. [`docs/phase-0-design.md`](../docs/phase-0-design.md) §3 — полная схема.

Минимально валидный документ:

```markdown
---
slug: rm-vs-warrior-rdruid
schema_version: 1
expansion: tbc
composition: rogue+mage
vs: warrior+resto-druid
bracket: 2v2
difficulty: easy
kill_target:
  primary: druid
sources:
- type: file
  path: "WOW TBC ARENA - Rogue  Mage.md"
  lines: "11-31"
last_reviewed: '2026-05-12'
confidence: draft
---

## Opener

Тело секции. Inline-способности — [[ability:cheap-shot]] / [[ability:kidney-shot]].
```

## Поток review

1. `arena_ingest paste --file X --comp Y` → новые `.md` в `kb/drafts/`.
2. Reviewer открывает в редакторе, проверяет:
   - текст переведён / стилизован если нужно (RU prose, EN ability names);
   - `kill_target` корректен;
   - `maps_notes` заполнены (если нюансы есть);
   - `confidence` поднят до `medium`/`high`;
   - `reviewer` заполнен.
3. `arena_ingest review approve --slug <slug>` → файл переезжает в `kb/matchups/`, плюс audit log entry (Phase 2+).

## Принципы

- KB версионируется в git (через корневой `arena-coach/` репо).
- **Нет в KB → нет совета.** Код никогда не выдумывает матчап-логику.
- Каждый KB-документ цитирует source. Inline-цитаты тоже сохраняют trail.
- Изменение схемы → бамп `schema_version` + миграционный скрипт.
