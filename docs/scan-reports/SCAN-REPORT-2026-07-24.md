# Arena Coach — ежедневный скан источников, отчёт 2026-07-24

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно.
> **Ничего не аппрувил, не мёржил в `kb/matchups/`, новых драфтов не создавал, трекнутые файлы `kb/`/`tests/` не менял.**
> Единственная запись — этот отчёт в `docs/`.

## TL;DR

- **Chrome MCP подключён** (Browser 1, macOS) — как 07-23. Прочитаны **вербатим, first-hand**: WT-overview **Mage/Rogue** (RM) и **Disc Priest/Rogue** (DPR/RP) с их секциями Counter Comps. Плюс WebFetch: LootXP Holy Paladin guide (полный текст), WebSearch ×3.
- **Гипотезы: 0 засорсено.** First-hand чтение канонических WT-overview'ов подтверждает: 4 оставшиеся пары (`rm-vs-hunter-hpala`, `rm-vs-mage-rdruid`, `rm/rp-vs-hunter-rsham`) **не названы** ни в RM-, ни в RP-списках Counter Comps. Пер-пара якоря нет → промоут = conflation, запрещён.
- **Verbatim-подтверждён существующий якорь `rp-vs-hunter-hpala`:** WT DPR-overview прямым текстом — «DPR … suffers a lot against mana drainers comps such as Hunter/Druid, Hunter/Priest, or **even Hunter/HPaladin**». Это ровно источник, на котором пара засорсена 06-25. Ок.
- **Важная проверка (анти-дубль):** всплывший в поиске LootXP «Holy Paladin PvP Guide» — это **републикация уже цитируемого гайда Hesback** (Wowhead 15309), тот же автор (Hesback/Ironhand, Glad S2 Firemaw-EU). **НЕ независимый источник** — как 2-й cite добавлять нельзя. Попутно вскрыл расхождение рейтинга (см. §4).
- **mirlol.pro/matchups — за Twitch-сабскрайб-пейволом** (login-gated). Новые матчап-гайды оттуда недоступны (не авторизуюсь). Доступна только главная (тир-лист).
- **silentshadows.net через WebFetch отдаёт только nav-шелл WT** (тело статьи client-rendered) — чистым WebFetch-источником не является, нужен Chrome. Поправка к возможному предположению прошлых сканов.
- **Репо зелёное:** `validate-kb kb/drafts/` → **64 OK**; `pytest tests/` → **165 passed**. Счётчик драфтов не трогал (драфтов не добавлял).

## 1. Что просканировано и результат

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **WT — Mage/Rogue overview** `…/rogue-mage-rogue-arena-strategies/` | **Chrome** ✅ (client-rendered) | Verbatim. **RM Counter Comps:** Human-rogue combs · Dwarf Disc+Mage/Warlock · Rogue/Druid · Lock/Druid · **Lock/Hpala**. **RM Weaknesses:** «vs locks, **RD comps**, and good discs». Hunter/Hpala, Mage/Druid, Hunter/Rsham — **не названы**. |
| **WT — Disc Priest/Rogue overview** `…/rogue-discipline-priest-rogue-arena-strategies/` | **Chrome** ✅ | Verbatim. **DPR Counter Comps:** «no real counters, but suffers a lot against mana drainers comps such as **Hunter/Druid, Hunter/Priest, or even Hunter/HPaladin**». **Weaknesses:** mana drain (Hunters), dual-melee (esp. non-Dwarf), longer games. Hunter/Rsham — **не назван**. |
| **mirlol.pro** (главная + `/matchups`) | **Chrome** ✅ | Главная = тир-лист (Sub-rogue POV): S+ Rogue+DiscPriest / Rogue+FrostMage / Rogue+Rogue; A+ Rogue+RestoDruid, Rogue+Feral, Rogue+Warlock; B+ Rogue+RetPala. **`/matchups` = Twitch-sub-пейвол** («exclusively for Mirlol's Twitch subscribers»). Пер-матчап контент недоступен. |
| **LootXP — Holy Paladin PvP Guide** (Hesback, publ. 2026-02-11) | WebFetch ✅ (verbatim) | **Републикация Wowhead-гайда Hesback 15309** (тот же автор/контент). Полная таблица W/P-матчапов, вкл. «Mage/Rogue». **Не независимый источник.** См. §4. |
| **silentshadows.net** (DPR/RM mirror) | WebFetch ⚠ / Chrome ✅ | WebFetch → 75k символов **чистого WT-nav**, тело статьи не отдаётся (client-rendered). Через Chrome тело читается (см. выше по WT-URL). |
| WebSearch ×3 (RM vs hunter/hpala; RM vs mage/rdruid; hunter+rsham 2v2) | — | Указатели, не источник; путают соседние пары. Подтвердили off-meta-статус (те же 5 тир-листов). |

**yt-dlp:** в песочнице не установлен; shell-фетч YouTube = обход web-fetch-политики. Не гонял (как 07-19…07-23). Пер-матчап видео-транскрипты по off-meta парам — задача для локального прогона владельца.

## 2. Оставшиеся 4 гипотезы — статус без изменений (теперь first-hand по WT-overview'ам)

| Гипотеза | Пара | Прямая проверка этого рана | Вердикт |
|---|---|---|---|
| `rm-vs-hunter-hpala` | Hunter/HPala × RM | RM Counter Comps (Chrome, verbatim) содержит **Lock/Hpala**, но **не Hunter/Hpala**. | **Гипотеза.** Нет RM-POV пер-пара якоря. |
| `rm-vs-mage-rdruid` | Mage/RDruid × RM | RM Weaknesses называет «**RD comps**» обобщённо + Counter Comps = Rogue/Druid, Lock/Druid. **Mage/Druid не назван.** Обобщённое «RD comps» — паттерн-поддержка сложности, **не** пер-пара якорь. | **Гипотеза.** |
| `rm-vs-hunter-rsham` | Hunter/RSham × RM | Не в RM Counter Comps. Драфт-кандидат застейджен `docs/proposals/rm-vs-hunter-rsham.draft.md` (07-19). | **Ждёт go/no-go владельца.** |
| `rp-vs-hunter-rsham` | Hunter/RSham × RP | DPR Counter Comps называет Hunter/**Druid**, Hunter/**Priest**, Hunter/**HPala** — но **не Hunter/RSham**. Паттерн «Weakness vs mana drain (Hunters)» поддерживает тезис, но пару не называет. Застейджен `docs/proposals/rp-vs-hunter-rsham.draft.md` (07-19). | **Ждёт go/no-go владельца.** |

**Вывод:** результат устойчив (20+ прошлых сканов + first-hand сегодня). Обобщённые формулировки WT («RD comps» для RM, «mana drain Hunters» для RP) — паттерн-поддержка сложности, но **не** называют конкретную пару → строгий бар (анти-conflation, урок 06-29/06-30) не пройден. Дальнейший авто-сорсинг по этим парам без **пер-пара** видео/форума бессмысленен.

## 3. Проверка LootXP «нового» источника — это дубль Hesback (не добавлять!)

WebSearch выдал `lootxphub.com/…holy-paladin-pvp-guide…` как «свежий» hpala-гайд. Прочитал вербатим:

- Автор — **«Hesback, also known as Ironhand … Gladiator S2 (5v5), 2.4+ Firemaw-EU»**. Это **тот же автор**, что уже цитируется в KB как Wowhead-гайд `holy-paladin-tbcc-pvp-guide-…-15309` (в `rm/rp-vs-warrior-hpala`, `rm/rp-vs-rogue-hpala`).
- Контент — та же W/P-таблица матчапов (Warrior/Druid, Rogue/Druid, Hunter/Druid, … **Mage/Rogue**, Double Rogue, Warrior/RSham и т.д.).
- **Не hunter+hpala-гайд** — это Warrior/Paladin POV; hunter+holy-paladin как пара там **не оценивается** (ещё одно подтверждение off-meta для `rm-vs-hunter-hpala`).

**Итог: НЕ независимый источник.** Добавлять LootXP как 2-й cite к Hesback = ложная независимость (нарушение трейсабельности). Ценность только техническая: полностью WebFetch-читаемая копия гайда (Wowhead бывает тяжело фетчить) — годится как verbatim-якорь для проверки существующих цитат Hesback.

### 3.1 Расхождение рейтинга — на ревью владельцу

Провенанс-нота в `kb/drafts/rm-vs-warrior-hpala.md` пишет: «Wowhead-гайд оценивает матчап против rogue/mage как **2/10**». Verbatim-текст Hesback (LootXP-копия): **«Mage/Rogue (Difficulty: 7/10): Use Blessing of Sacrifice to prevent the opener. Save your trinket for Blind on the Warrior and Blessing of Protection it instantly. Target the Rogue.»**

⚠ Но численная шкала гайда **внутренне противоречива**: «Double Rogue (1/10): a hard counter for us» и «Hunter/Druid (10/10): a very hard counter» — и 1/10, и 10/10 описаны как «hard counter». Т.е. цифра ненадёжна как сигнал. **Полезен тактический текст, не число.** Рекомендация: не переносить «2/10» как факт; при желании — заменить провенанс-ноту на дословную цитату тактики (BoSac против опенера, тринкет+инстант-BoP на Blind воина, цель — рог). Это правка провенанса, тело не трогать; **решение за владельцем.**

## 4. Enrichment-предложения (НЕ применены — тела/цитаты не тронуты)

### 4.1 (сильное) WT DPR-overview как независимый comp-level якорь для RP-драфтов
Многие RP-драфты держатся на **одном** источнике (транскрипция Mirlol). WT Disc-Priest/Rogue overview даёт независимую comp-level привязку (strengths: магодиспелы, CC-синергия Fear/KS/Blind/Sap, мобильность vs кастеров; weaknesses: mana-drain Hunters, dual-melee, долгие игры). Особенно — **verbatim пер-пара** упоминание для `rp-vs-hunter-hpala`.
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-discipline-priest-rogue-arena-strategies/"
  title: "Disc Priest/Rogue 2v2 overview (Warcraft Tavern) — «DPR Counter Comps: no real counters, but suffers a lot against mana drainers comps such as Hunter/Druid, Hunter/Priest, or even Hunter/HPaladin»; Weaknesses: mana drain (Hunters), dual-melee (esp. non-Dwarf), longer games vs healer/DPS; Strengths: offensive/defensive dispels, CC synergy (Fear/KS/Blind/Sap), mobility vs casters"
  retrieved: '2026-07-24'
```
Куда: `rp-vs-hunter-hpala` (пер-пара, сильно) — как 2-й якорь пары. Обвязка для прочих RP-хилер-матчапов — по усмотрению.

### 4.2 (среднее) Паттерн-поддержка застейдженного `rp-vs-hunter-rsham`
Тот же WT DPR-блок — паттерн-поддержка тезиса «hunter+healer = мана-война, слабость RP». ⚠ Называет Hunter/Druid|Priest|HPala, **не Rsham** → это усиление comp-level кейса, **не** пер-пара naming. Go/no-go по драфту всё равно за владельцем.
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-discipline-priest-rogue-arena-strategies/"
  title: "Disc Priest/Rogue 2v2 overview (Warcraft Tavern) — «Weakness vs mana drain (Hunters)»; DPR «suffers a lot against mana drainers comps such as Hunter/Druid, Hunter/Priest, or even Hunter/HPaladin». NB: hunter+resto-shaman НЕ назван поимённо — паттерн-поддержка hunter+healer мана-войны, не пер-пара якорь"
  retrieved: '2026-07-24'
  note: "Pattern-support only; не основание для промоута сам по себе."
```

### 4.3 (техническое) verbatim-якорь Hesback для hpala-драфтов
`rm/rp-vs-warrior-hpala` и `rm/rp-vs-rogue-hpala` цитируют Hesback (Wowhead 15309). LootXP — полностью читаемая копия того же гайда с точными механиками: Judgement of Blood ломает Poly/Scatter/Blind (~0.2с делэй, если цель без шилда); BoSac держится 24/7 против non-dispel rogue-команд «until Blind»; Stoneform = «essentially a second Blessing of Freedom» vs рог; r1 Might/Wisdom как dispel-байт; Turn Evil на фелхантера перед Spell Lock. **Тот же автор — не 2-й независимый cite;** годится как verbatim-справка при уточнении «If enemy trinkets»/«Common mistakes». Решение за владельцем.

## 5. Ждёт владельца (сводка с переносом)

1. **§4.1 — сильный enrichment `rp-vs-hunter-hpala`:** добавить WT DPR-overview как 2-й пер-пара якорь. Скажи «применяй» — впишу source-блок, тело не трогаю.
2. **§3.1 — расхождение рейтинга `rm-vs-warrior-hpala`** («2/10» в ноте vs «7/10» verbatim; шкала гайда противоречива). Решить: править ли провенанс-ноту на дословную цитату.
3. **Висит с 07-19:** go/no-go по 2 драфтам `rm/rp-vs-hunter-rsham` (`docs/proposals/`). §4.2 добавляет им паттерн-поддержку, но не пер-пара якорь.
4. **Висит с 07-23:** 5 enrichment'ов Deadlycoward (§4.1–4.5 отчёта 07-23) — `rp-vs-hunter-rdruid`, `rp-vs-rogue-mage`, `rp-vs-rogue-rogue`, `rp-vs-mage-priest`, `rp-vs-warlock-priest`.
5. **Висит с 07-22 / 07-20:** enrichment'ы PvPSkills (RMP-кластер) + 6 предложений по DR-коллизиям/Mass Dispel/Spellsteal.
6. **2 гипотезы** (`rm-vs-hunter-hpala`, `rm-vs-mage-rdruid`) ждут пер-пара источника (yt-dlp/форум по конкретной паре) — тир-листы и WT-overview'ы их не покрывают (проверено first-hand).
7. **Уборка (опц.):** 12 устаревших дубликат-гипотез (пары уже в `drafts/`); незакоммиченные модификации `kb/hypotheses/*hpala.md` (git status) — на усмотрение владельца.

---

_Проверка: `pip install … --break-system-packages` + `PYTHONPATH=backend:ingest:bridge` → `python -m arena_coach validate-kb kb/drafts/` = **OK: 64 документа** → `python -m pytest tests/` = **165 passed**. Трекнутые файлы `kb/`, `tests/` не изменены. Sources (this run, verbatim): WT Mage/Rogue overview, WT Disc-Priest/Rogue overview, mirlol.pro (paywall), lootxphub.com (Hesback republication)._
