# kb/glossary — слой глоссария

Три файла, разные роли. KB — единственный источник правды; код не хардкодит термины.

| Файл | Что | Источник правды | Формат |
|---|---|---|---|
| `abilities.json` | спелл-дата (id, icon, DR-категория, cd, длительность, EN-алиасы для combat-log) | да | flat dict, ключ = slug |
| `terms.md` | определения арена-жаргона (DR, opener, sap-stall…) для `/glossary` | да | Markdown, `## H2` = термин |
| `slang.json` | **RU задрот-сленг ⇄ canonical slug ⇄ EN-термин** | да | flat dict, ключ = slug |
| `slang.md` | человекочитаемый вид `slang.json` | — (генерируется) | Markdown |

## slang.json — зачем

Слой между Phase 1.5 (перевод прозы) и Phase 4.5 (voice/уведомления):

- **Вход:** понять, что игрок говорит/пишет («сапни хила», паста стрима, голосовая команда) → нормализовать в canonical slug для KB-lookup.
- **Выход:** бот и TTS звучат на естественном сленге команды, а не «переводят буквально».

### Схема записи

```jsonc
"trinket": {
  "slug": "trinket",          // canonical id (переиспользуется из abilities.json/terms.md, либо новый)
  "en": "Trinket",            // защищённый EN-термин (sync с Phase 1.5)
  "category": "ability",      // ability | tactic | status | role | target | class
  "ref": "new",               // abilities.json | terms.md | new  — где живёт canonical-дефиниция
  "ru": "тринкет",            // ОСНОВНАЯ разговорная форма команды (НЕ формальный перевод)
  "slang": ["тринка","тринканул"],   // ВСЕ распознаваемые формы, вкл. словоформы (вход)
  "voice": "тринка",          // форма для TTS/уведомлений (выход); ОБЯЗАНА входить в slang[]
  "register": "standard",     // standard = можно генерить; colloquial = понимаем на входе, в речь не суём
  "confidence": "high",       // high | med | low — насколько уверены, что пачка так говорит
  "note": "…",                // дизамбигуация / контекст
  "links": ["post-trinket","swap"]
}
```

Принцип: **`ru` = основная разговорная форма команды** (как говорят/пишут, обычно транслит, не формальный
перевод). **`slang[]` — широкий (вход)** — держим тут и словоформы (блинкнулся, тринканул).
**`voice`/`register` — узкие (выход)**, причём `voice` обязана входить в `slang[]` (проверяется валидатором).

## Регенерация slang.md

```bash
python tools/gen_slang_md.py          # перегенерить slang.md + отчёт валидации
python tools/gen_slang_md.py --check  # только валидация (CI-friendly), без записи
```

Валидатор проверяет: каждый `ref:abilities.json`/`ref:terms.md` slug реально существует; ни один
RU-токен не маппится на два slug'а (иначе вход неоднозначен); `voice` входит в `slang[]`.

## Статус

v1 — **draft, ждёт approve**. Не зашит в код бота (по решению: «только файл-словарь»). Перед merge:
свести `en`-список с защищённым списком `docs/phase-1.5-translation-plan.md`, прорешать новые
canonical slug'и (`trinket`, `blink` → возможно в `abilities.json`).
