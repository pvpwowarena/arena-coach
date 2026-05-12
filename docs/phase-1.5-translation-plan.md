# Phase 1.5 — Russian prose translation

**Статус:** planned, after Phase 1 push to GitHub.
**Why:** тестеры играют на русском, английская проза из Mirlol мешает быстрому чтению hint'а в матче. Нужен русский язык для прозы, но **не** для ability/spell-имён (они в EN везде — в игре, в Lua-API, в spell-database).

## Принципы перевода

Что **переводим**:
- Прозу секций (`## Opener`, `## If enemy trinkets`, `## Mid-fight rotation`, `## Notes`).
- Поле `win_condition` в frontmatter.
- Значения `maps_notes` (карта-специфичные заметки).

Что **НЕ переводим**:
- `[[ability:slug]]` токены — остаются как есть.
- Англоязычные термины арена-жаргона (см. список ниже).
- Frontmatter-поля (slug, composition, vs, difficulty, kill_target, sources и т.д.).
- Названия способностей внутри прозы, если они написаны явно (например, «Counterspell on innervate» — оставляем).
- Названия карт (Nagrand, Lordaeron, Blade's Edge).

### Защищённый список терминов

Эти термины **остаются на английском** в любой позиции прозы:

```
opener, alt opener, post-trinket, swap, peel, reset, kill target,
sap-stall, blanket CS, premed, shatter, sticky nova, dampening,
OOM, LoS, DR, double wound, crippling, mind-numbing, MS-trinket,
clearcast, frostbite proc, mace-stun, hamstring, intercept,
spell-reflect, faerie fire, innervate, cyclone, fear, sheep, polymorph,
ice block, divine shield, bubble, lichborne, cloak, vanish, prep,
preparation, blind, cheap shot, kidney shot, garrote, eviscerate,
expose armor, hemo, rupture, shadowstep, evasion, gouge, shiv, sap
```

Этот список синхронизирован с `kb/glossary/terms.md` и `kb/glossary/abilities.json`.

## Архитектура

Новая команда CLI: `arena-ingest translate`.

```bash
# Перевести один draft
python -m arena_ingest translate --slug rm-vs-warrior-rdruid --to ru

# Перевести всю партию (топ-7)
python -m arena_ingest translate --batch top7

# Перевести всё в kb/drafts/
python -m arena_ingest translate --all
```

Поток:

```
kb/drafts/<slug>.md (EN prose)
    ↓
LLM-normalize (claude-haiku-4-5-20251001, temperature=0)
    ↓ system-prompt:
    ↓  «Переведи только prose, не трогай [[ability:X]] и список защищённых
    ↓   терминов. Сохрани Markdown-разметку. Используй естественный
    ↓   арена-сленг по-русски, не "переводи буквально".»
    ↓
kb/drafts/<slug>.md (RU prose, confidence: medium)
    ↓ human review: подправить язык, поднять confidence: high
    ↓
kb/matchups/<slug>.md
```

## Стоимость

claude-haiku-4-5-20251001:
- ~2-4K input tokens на draft (исходник + system-prompt)
- ~1-2K output tokens (русская проза)
- ~$0.001-0.002 на draft

22 драфта × ~$0.002 = **~$0.04 на полный прогон**.

Это копейки даже если переделывать перевод 10 раз во время Phase 1.5 настройки промпта.

## Acceptance criteria

1. Все 22 драфта переведены и валидны через `KBDoc`-схему.
2. Все `[[ability:slug]]` сохранены 1-в-1 (regex-проверка до/после).
3. Защищённые термины сохранены 1-в-1 (regex-проверка).
4. Frontmatter не изменён (binary-diff sources/slug/composition).
5. `confidence: medium` проставлен автоматически.
6. Human-review на минимум 1 драфте из топ-партии → если перевод OK, остальные одобряем подряд.

## Что не делает Phase 1.5

- **Не переводит UI бота.** Embed-шаблоны Discord-бота → Phase 2.
- **Не переводит глоссарий `terms.md`.** Он сейчас уже на смешанном (RU описание, EN термин) — это и есть финальный формат.
- **Не делает обратный перевод RU→EN.** Если потребуется в будущем — отдельная задача.
