# Source-scan report — 2026-07-16 (авто-задача)

**Итог: 0 новых sourced-драфтов, 0 засорсенных гипотез. KB не изменялась** (51 драфт / 16 гипотез, 4 незасорсенных), ничего не аппрувлено, в `kb/matchups/` ничего не мёржено.

**Главное за ран — Chrome БЫЛ подключён** (в отличие от 07-11…07-15). Через Chrome MCP прочитаны ПОЛНЫЕ тела трёх client-rendered страниц Warcraft Tavern, которые блокировали enrichment ~2 недели. Это переводит давно висящий enrichment-бэклог из статуса `needs-verification` в **проверенные, цитируемые, готовые к вставке правки** (§3). Разблокировать 4 гипотезы это по-прежнему не может (см. §2 — там нет источника по природе пары), поэтому новых драфтов нет, но реальный прогресс есть впервые за неделю.

**Проверки:** KB мной не менялась. В песочнице `arena_coach`/venv по-прежнему не установлены → полноценные `validate-kb` и `pytest` тут не гоняются (как и 07-15). Взамен прогнал лёгкую standalone-проверку фронтматтера (PyYAML): **51/51 драфт well-formed** (slug+composition+vs+≥1 source), **16/16 гипотез корректно source-less** (карантин не течёт в индекс бота), 4 live-незасорсенных / 12 stale-дублей — цифры сходятся с 07-15. Счётчик драфтов в `test_kb_loader.py` не трогал (драфтов не добавлял), `render_slang` не требуется.

---

## 1. Что сканировал

| Источник / запрос | Метод | Результат |
|---|---|---|
| WT `rogue-mage-rogue-arena-strategies` | **Chrome (тело прочитано)** | Comp-overview (strengths/weaknesses, counter-comps, таланты, списки видео). Per-matchup тактики нет, но есть цитируемые общие принципы (counter-comps, CC-DR Sap/Gouge/Sheep, не ломать Nova мили-уроном) |
| WT `rogue-subtlety-openers` (Sbkzor/Saeyonara) | **Chrome (тело прочитано)** | **Джекпот по опенерам.** Полный разбор: анти-mage snare/double-garrote опенеры, «не станить воина из-за Second Wind», blink-bait, анти-SP Expose-опенер, Seduce-bait vs lock, DR Sap/Gouge/Poly, Gouge под коннект мага. Всё TBC 2.4.3, ретейл-механик нет |
| WT `rogue-swap-in-arenas` | **Chrome (тело прочитано)** | Фреймворк свопа (CD/позиционка/мана), **чеклист вражеских дефанс-КД по классам**, явный пример свопа **RM vs Priest/Rogue**, scripted-swap / fake-go (в т.ч. для 3v3) |
| `rogue+mage vs hunter+rsham` | WebSearch | Подтверждает: hunter+rsham **не** в списках жизнеспособных 2v2 (Wowhead/Icy-Veins/Skill-Capped: стандарт resto-sham — с rogue/warrior/ret, не hunter). Per-matchup нет |
| `rogue+mage vs mage+rdruid` | WebSearch | **13-й conflation:** сводка снова свела `mage+rdruid` → `rogue+rdruid` («Rogue/Druid is the best 2v2…»). Реального `mage+rdruid`-контента ноль |
| RMP 3v3 opener | WebSearch | Только общий канон RMP (Sap healer first, CS-KS delete, 15s CC на чистом опенере). Совпадает с уже сорснутыми RMP-драфтами; нового источника нет |

> ⚠ Chrome-навигация была строго read-only по публичным гайд-страницам WT. Никаких логинов, форм, кликов по необратимым действиям. mirlol не трогал (paywall). yt-dlp не пробовал (в песочнице 403, нужна интерактивная сессия).

## 2. Гипотезы: 4 незасорсенных, блок держится (Chrome их НЕ разблокирует)

| Slug | Статус после 07-16 |
|---|---|
| `rm-vs-hunter-rsham` | Блок. hunter+resto-shaman **не является метовой 2v2-парой** — шаман стандартно идёт с rogue/warrior/ret. Источника по паре нет, потому что пары как меты нет. Сорсить не из чего |
| `rp-vs-hunter-rsham` | То же |
| `rm-vs-mage-rdruid` | Блок. 13-й conflation `mage+rdruid`→`rogue+rdruid`. Пары как меты не существует → источника нет |
| `rm-vs-hunter-hpala` | Блок на `## Opener` = **дизайн-решение A/B за владельцем** (открыто с 07-13), не дыра в источнике. Новый материал в помощь решению: WT-опенеры дают анти-хантер-теху («сидеть за спиной MM-хантера и спамить Gouge, чтобы кросс-контролить его Scatter/Trap на трникет»). Это можно вписать в опенер **после** выбора kill-таргета владельцем — сам не решаю |

Вывод тот же, что 07-13/14/15: эти 4 из общих гайдов не сорсятся (исчерпано). Реально разблокирует только (а) RM/RP-POV видео-транскрипт (yt-dlp/интерактив), (б) mirlol-подписка владельца + ручной паст, (в) экспертный approve владельца.

## 3. Enrichment — теперь ПРОВЕРЕНО и цитируемо (готово к вставке, НЕ применял)

Прошлые раны держали эти правки как `needs-verification`, потому что тело WT было client-rendered. Сегодня тела прочитаны — правки цитируемы. **Сам не вписывал** (пункт задачи 3 = «предложи конкретные правки»; матчап-контент видит бот). Ниже — по источникам и целевым драфтам.

### Источник A — WT «Subtlety Rogue PvP Openers», автор Sbkzor/Saeyonara
`https://www.warcrafttavern.com/tbc/guides/rogue-subtlety-openers/`
Строка для `sources:` при вставке:
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-subtlety-openers/"
  title: "Subtlety Rogue PvP Openers (Warcraft Tavern, Sbkzor/Saeyonara) — TBC 2.4.3 opener theory"
  retrieved: "2026-07-16"
```

**A1. Анти-mage опенер (snare, не stun).** Цель: любой драфт, где открываем на вражеском МАГЕ — `rm-vs-rogue-mage`, `rm-vs-mage-priest`, `rm-vs-mage-hpala`, `rm-vs-warrior-mage`, `rp-vs-mage-priest`, `rp-vs-mage-hpala`, `rp-vs-mage-rdruid`, `rp-vs-warrior-mage`, `rp-vs-rogue-mage`.
Проза (в `## Alternative opener` / нюанс к опенеру): «Типовой рог-опенер на мага — snare, а не stun: `[[ability:sap]]` → `[[ability:premed]]`, `[[ability:garrote]]` (из угла 90°, чтобы не ломать sap) → `[[ability:shiv]]` (crippling), `[[ability:evisc]]` — держит мага в мили, мешает Blink и Eviscerate сбивает Frost/Mana Shield. Двойной garrote (silence в TBC **не** делит DR) ещё жёстче лочит касты/Blink. Blink-bait: `[[ability:premed]]`, `[[ability:cheap-shot]]` → `[[ability:gouge]]` (предугадав Blink) → `[[ability:kidney-shot]]` → `[[ability:shiv]]` crippling.»
**Тип-подсказка (сильная):** «Часть магов ставит insignia на `[[ability:sap]]`, чтобы Frost Nova выбить рога из стелса — **сапай с максимальной дистанции и жди пару секунд**, смотри реакцию.» (это ровно кандидат из 07-15 §3, теперь verified).

**A2. Не станить воина — Second Wind.** Цель: все `*-vs-warrior-*` (`rm-vs-warrior-rogue`, `rm-vs-warrior-mage`, `rm-vs-warrior-rdruid`, `rm-vs-warrior-rsham`, `rm-vs-warrior-hpala`, `rp-vs-warrior-*`).
Проза (в `## Common mistakes` + `## Opener`): «Не открывай стан-локом по воину: талант Second Wind даёт ему +20 рейджа и лечит 10% HP за 10с при КАЖДОМ Stun/Immobilize. Против воина — snare/bleed опенер: `[[ability:sap]]` → `[[ability:premed]]`, `[[ability:garrote]]`, `[[ability:rupture]]` (90°) → `[[ability:shiv]]` crippling → dead zone.»
⚠ `second-wind` НЕТ в глоссарии — вписывать как обычный текст, либо сперва патч глоссария (см. §5).

**A3. CC-DR дисциплина Gouge↔Sap↔Poly.** Цель: RM-драфты с sap+sheep+gouge сетапом (общая заметка). Проза: «`[[ability:gouge]]` делит DR с `[[ability:sap]]` и `[[ability:sheep]]`: нельзя полноценно gouge’нуть ранее сапнутую цель, и нельзя рассчитывать на полный `[[ability:sap]]`, если враг трникетнул `[[ability:kidney-shot]]`, поставленный после gouge.»

**A4. Gouge под коннект мага (RM-специфика).** Цель: RM-опенеры в целом. Проза: «`[[ability:gouge]]` может покупать время, чтобы маг успел подойти и прокастовать первый Frostbolt (прямо названо для Rogue/Mage).»

**A5. Анти-Shadow-Priest Expose-опенер.** Цель: `rm-vs-rogue-spriest`. Проза: «Против SP хорош Expose-опенер: `[[ability:premed]]`, `[[ability:cheap-shot]]`, `[[ability:expose-armor]]` (5cp) → `[[ability:gouge]]` → `[[ability:vanish]]`, `[[ability:garrote]]` → `[[ability:kidney-shot]]`. 5cp Expose даёт шанс free-combo (Ruthlessness), Hemo усилен Expose, автоатаки в cheap shot сбивают щит.»

**A6. Анти-Warlock Seduce-bait.** Цель: `rm-vs-warlock-*`, `rp-vs-warlock-*`. Проза: «Против lock’а — bait Seduce суккуба: `[[ability:sap]]`, `[[ability:cheap-shot]]` (90°) и переждать/пересидеть seduce, прежде чем коммититься.»

### Источник B — WT «Rogue PvP Arena Target Swap Guide»
`https://www.warcrafttavern.com/tbc/guides/rogue-swap-in-arenas/`
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-swap-in-arenas/"
  title: "Rogue PvP Arena Target Swap Guide (Warcraft Tavern) — TBC 2.4.3 swap framework"
  retrieved: "2026-07-16"
```

**B1. Явный своп RM vs Priest/Rogue.** Цель: `rm-vs-rogue-priest` (и `rp-vs-rogue-priest`). Проза (в `## Opener`, Option-логику дополнить): «Своп-линия из гайда: выбить трникет прийста на `[[ability:sheep]]` и трникет рога на `[[ability:kidney-shot]]`, затем свопнуть на прийста — `[[ability:blind]]` рога → `[[ability:sap]]`/`[[ability:sheep]]`, и свежий `[[ability:cheap-shot]]`→`[[ability:kidney-shot]]`+`[[ability:counterspell]]` по прийсту.» Совпадает с текущей “Option 1/2”, добавляет явную развилку по трникетам.

**B2. Чеклист вражеских дефанс-КД (в `## Key cooldowns to track`).** Из гайда: Mage — Ice Block, **Cold Snap**; Priest — Pain Suppression (+Stoneform у дворфа); Druid — **Nature’s Swiftness, Barkskin**; Rogue — Cloak, Vanish; Warlock — **Fel Domination**; Paladin — Divine Shield, BoP/Sacrifice; все — PvP trinket. Многие драфты уже перечисляют часть — можно дочистить пропуски (Cold Snap у мага, Fel Domination у лока, NS/Barkskin у друида).
⚠ `cold-snap`, `fel-domination`, `barkskin`, `natures-swiftness`, `divine-shield`, `blessing-of-protection` — НЕ в глоссарии (см. §5).

**B3. Scripted swap / fake-go.** Цель: RMP-драфты + RM double-DPS. Проза: «Fake-go: продавить трникет/дефанс на off-таргете, затем свопнуть на настоящий kill-таргет. В 3v3 — `[[ability:blind]]` друида и мгновенный командный своп в `[[ability:cheap-shot]]`→`[[ability:kidney-shot]]`.»

**B4. Мана-статус как триггер свопа/сапа.** Общая заметка: OOM-кастер = окно на `[[ability:sap]]` пока пьёт / своп-килл.

### Источник C — WT «Mage/Rogue 2v2 Strategies» (overview)
`https://www.warcrafttavern.com/tbc/guides/rogue-mage-rogue-arena-strategies/` — ценность скромная (в основном подтверждает уже известное). Пригодно как comp-level контекст: RM counter-comps = Rogue/Druid, Lock/Druid, Lock/Hpala, Human-rogue combs, Dwarf-Disc + Mage/Warlock; RM не Tier-1, но до Глада доходит; дисциплина «не ломать `[[ability:nova]]` мили-уроном».

## 4. Приоритет применения (когда владелец даст отмашку)

1. **A2 (Second Wind → не станить воина)** — самая ценная и «дырявая» правка: сейчас `rm-vs-warrior-rogue` вообще не упоминает Second Wind, а это меняет опенер против всех воинов. **6 драфтов.**
2. **A1 (анти-mage snare/max-range sap)** — второй по охвату (≈9 mage-фейсинг драфтов), verified кандидат из 07-15 §3.
3. **B1 (RM vs Priest/Rogue своп)** — точечно усиливает уже сильный драфт.
4. **A5/A6, B2, A3/A4, B3** — точечные нюансы.

## 5. Предусловие: патч глоссария (стоит на месте с 07-14 §3h)

Для инлайна `[[ability:...]]` нужны слаги, которых нет в `abilities.json`. Из сегодняшних источников всплыли: `second-wind` (воин), `cold-snap` (маг), `fel-domination` (лок), `barkskin`, `natures-swiftness`, `divine-shield`, `blessing-of-protection`, `seduce`. Без них enrichment вписывается обычным текстом (не ломает валидатор), но чище — сперва добавить слаги. Полный список ~17 отсутствующих — в 07-14 §3h.

## 6. Housekeeping

- **Stale hypothesis-дубликаты: 12** (twin-драфт существует) — ждут удаления владельцем. 4 «живых» = блок §2. (standalone-проверка сегодня подтвердила разбивку 4/12.)
- **Дрейф счётчика тестов:** «113» в `CLAUDE.md` и в системных инструкциях проекта устарело — фактически **146** (см. 07-15).
- **Незакоммичено (untracked):** отчёты 07-11…07-15 + этот (07-16). `.git/index.lock` в песочнице неудаляем (нет прав) — коммит только вручную владельцем: `git add docs/SCAN-REPORT-2026-07-*.md && git commit`.

## 7. Следующие шаги (по ценности)

1. **Отмашка на enrichment-батч §3** (начать с A2, затем A1/B1) + патч глоссария §5 как предусловие. Это уже НЕ «needs-verification» — источники прочитаны и цитируемы.
2. **Решение A/B по `rm-vs-hunter-hpala`** (висит с 07-13). Теперь есть анти-хантер-теха из WT-опенеров в помощь.
3. Пока Chrome доступен в интерактивной сессии — снять оставшуюся очередь: WT `rogue-introduction-to-arenas` (Five Pillars), `rogue-kiting`; и yt-dlp-транскрипты RM/RP-POV (`PcfLBroowrM` Earpugs RP 2100 → и далее) — единственный реалистичный путь разблокировать 4 гипотезы.
4. Mirlol: подписка владельца → паст матчапов в ingest.
