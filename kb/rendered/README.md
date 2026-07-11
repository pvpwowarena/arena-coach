# kb/rendered/ — ПРОИЗВОДНЫЙ слой (не canonical)

Сгенерировано из `kb/drafts/` через `tools/render_slang.py`. **Не источник правды, не редактировать вручную, не индексируется ботом** (`KBIndex` сканирует только `kb/matchups/` и `kb/drafts/`).

## `slang/` — voice-рендер

Канонические драфты, переписанные в естественный разговорный сленг команды по `kb/glossary/slang.json` (слой Phase 1.5 / Phase 4.5). Замены делаются **только** для записей с `register: standard` (по схеме `colloquial` — понимаем на входе, в речь не суём, поэтому такие способности остаются читаемым EN-именем). Frontmatter копируется дословно — трейсабельность к источнику сохранена.

Перегенерация:

```bash
python tools/render_slang.py --all      # все драфты
python tools/render_slang.py --slug <slug>
python tools/render_slang.py --check     # dry-run + отчёт покрытия, без записи
```

## Статус

Прототип. `slang.json` сам по себе ещё `draft, ждёт approve` — при изменении лексикона просто перезапусти рендер. Пробелы покрытия (способности без slang-записи) печатает `--check`.
