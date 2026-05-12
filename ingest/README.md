# Arena Coach Ingest Pipeline

CLI-импортёры внешних источников в `kb/drafts/`.

## Команды (Phase 1)

```bash
# Импорт Mirlol-стиля Markdown в drafts
python -m arena_ingest paste \
  --file "../WOW TBC ARENA - Rogue  Mage.md" \
  --comp rogue+mage

# Список того, что в kb/drafts/ и kb/matchups/
python -m arena_ingest list

# Approve draft → matchups (TODO Phase 2: + audit-log entry)
python -m arena_ingest review approve --slug rm-vs-warrior-rdruid

# Reject draft с reason → kb/drafts/.rejected/
python -m arena_ingest review reject --slug rm-vs-foo --reason "duplicate"

# Сборка abilities.json skeleton из источников
python -m arena_ingest glossary extract \
  "../WOW TBC ARENA - Rogue  Mage.md" \
  "../WOW TBC ARENA - Rogue Priest.md" \
  --output kb/glossary/abilities.json
```

## Источники

- `paste` — Markdown с Mirlol-форматом inline ability ссылок. Готов.
- `mirlol` *(Phase 1.5)* — WebFetch + parser HTML с mirlol.pro.
- `tbcpvp` *(Phase 1.5)* — то же для tbcpvp.com.
- `youtube` *(Phase 1.5)* — yt-dlp + whisper → транскрипт → LLM-нормализация.

## Поток в Phase 1

```
Markdown файл
   ↓
parse_matchups()           — разбивка на матчапы по "vs / comp / difficulty"
   ↓
parse_sections()           — выделение ### Opener / ### Strategy / ...
   ↓
canonicalize_titles()      — маппинг на канонические секции KB (см. PHASE_0_DESIGN §7)
   ↓
convert_inline_abilities() — ![label](icon-url) → [[ability:slug]]
   ↓
render_kb_draft()          — frontmatter + body
   ↓
kb/drafts/<slug>.md        — ждёт human-review через `review approve`
```

## Принципы

- Парсер **не выдумывает** — только переносит то, что есть в источнике.
- Каждый draft имеет `confidence: draft` пока reviewer не сделает approve.
- Каждый draft содержит `sources: [{type: file, path: ..., lines: ...}]` — трейсабельность до исходных строк.
- Glossary `abilities.json` мерджится (preserve manual edits).
