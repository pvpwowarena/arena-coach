# Source-scan report — 2026-07-14 (авто-задача)

**Итог: 0 новых sourced-драфтов, 0 засорсенных гипотез.** KB **не изменялась**, ничего не аппрувлено, в `kb/matchups/` ничего не мёржено.

**Главное за ран:** Chrome MCP оказался подключён (Browser 1, macOS) → впервые за много ранов открылись client-rendered источники. Итог двоякий:

- ✅ Найдено **4 ранее не использованных TBC-гайда на Wowhead** (серия «Arena Guide — Best Compositions, Talent Builds, Tactics», все обновлены **2026-02-10**, патч 2.5.6): **Hunter (Veramos)**, **Mage (Foolipe)**, **Resto Druid (Kyxie)** — новые; **Resto Shaman (Woah)** — уже цитировался, но его комп-секция раньше не разбиралась. Это самый качественный enrichment-материал за неделю (см. §3).
- ❌ **mirlol.pro закрыт окончательно:** `/matchups/rogue-mage` и `/matchups/rogue-priest` — не client-rendering-проблема, а **платный доступ**: «This content is exclusively for Mirlol's Twitch subscribers. Log in with Twitch». Логиниться я не могу и не буду (запрет на ввод учётных данных). `/videos` — только 12 роликов-хайлайтов, **ни одного per-matchup**. Единственный путь к mirlol-контенту — **подписка владельца** + ручной паст в ingest.

**Проверки (green):** `validate-kb kb/drafts/` = **51 OK** · `pytest tests/` = **146 passed** · KB не менялась → счётчик в `test_kb_loader.py` не трогал, `render_slang` не требуется.

---

## 1. Что сканировал

| Источник | Метод | Результат |
|---|---|---|
| `mirlol.pro` (главная, `/matchups/*`, `/videos`) | Chrome | **Paywall (Twitch-sub)**. Тир-лист на главной читается: 2v2 S+ = Rogue+Disc Priest, **Rogue+Frost Mage**, Rogue+Rogue; A+ = Rogue+Resto Druid, Rogue+Feral, Rogue+Warlock; B+ = Rogue+Ret Pala |
| `warcrafttavern.com/tbc/guides/rogue-arena-strategies/` | Chrome | Индекс прочитан. **Отдельного «Rogue/Mage 2v2 Guide» не существует** (есть только обзорная `rogue-mage-rogue-arena-strategies`, уже в sources). Новые непрочитанные страницы: `rogue-swap-in-arenas`, `rogue-subtlety-openers`, `rogue-kiting`, `rogue-healer-dps-vs-double-dps-2v2`, `rogue-resto-druid-rogue-arena-strategies` |
| `warcrafttavern.com/tbc/guides/hunter-arena-strategies/` | Chrome | **404** — WT-серии «arena strategies» есть только у рога |
| Wowhead TBC arena-серия: Hunter / Mage / Resto Druid / Resto Shaman | WebFetch + Chrome | **Прочитаны целиком** (см. §2, §3) |
| WebSearch: hunter+rsham, mage+rdruid (домены WT/silentshadows/icy-veins/wowhead/AJ) | WebSearch | Per-matchup ничего. Сводки снова сводят `mage+rdruid` → `rogue+rdruid` (**одиннадцатый conflation**) |

## 2. Гипотезы: по-прежнему 4 незасорсенных, блок подтверждён с **обеих сторон**

Раньше блок держался на tier-листах и обзорах (т.е. «этих пар нет среди топ-компов»). Сегодня появилось качественно более сильное подтверждение: **per-class комп-листы 2026-го года со стороны самих вражеских классов**.

| Гайд (Wowhead, 2026-02-10) | Какие 2v2-компы перечислены | Что это значит |
|---|---|---|
| **Hunter** (Veramos) | Hunter/**Druid**, Hunter/**Rogue** | Hunter+Shaman и Hunter+Paladin **не существуют** как комп со стороны хантера |
| **Resto Shaman** (Woah) | Shaman/**Warrior**, Shaman/**Ret Paladin**, Shaman/**Rogue** | Hunter+Shaman **не существует** и со стороны шамана |
| **Resto Druid** (Kyxie) | Druid/**Warlock**, Druid/**Rogue**, Druid/**Hunter** | Mage+Druid **не существует** со стороны друида |
| **Mage** (Foolipe) | Mage/**Rogue**, Mage/**Priest** | Mage+Druid **не существует** и со стороны мага |

| Slug | Статус |
|---|---|
| `rm-vs-hunter-rsham` | блок; пара отсутствует в комп-листах **обеих** сторон (hunter-гайд + shaman-гайд) |
| `rp-vs-hunter-rsham` | то же |
| `rm-vs-mage-rdruid` | блок; пара отсутствует в комп-листах **обеих** сторон (mage-гайд + druid-гайд) |
| `rm-vs-hunter-hpala` | блок на `## Opener` сохраняется (см. 07-13 §2a). Hunter-гайд паладина как партнёра не упоминает; но doinker08 (2.4.3) даёт difficulty/kill-target/mistakes. **Решение A/B за владельцем — по-прежнему открыто** |

Итого: не-мета статус этих пар подтверждают уже **~12 независимых источников**, теперь включая двусторонние комп-листы. Дальше сорсить их из общих гайдов **бессмысленно** — нужен либо RM/RP-POV видео-транскрипт, либо mirlol-подписка, либо ревью топ-игрока (тогда это не «источник», а экспертный approve владельца).

## 3. Enrichment: конкретные правки (НЕ применял — жду отмашки)

Всё ниже — **прямые утверждения из свежих Wowhead-гайдов**, с атрибуцией. Проверено `grep` по `kb/drafts/` — эти факты в KB **отсутствуют**.

### 3a. 🔴 Spellsteal — дыра в RM-драфтах (`spellsteal` есть только в 2 драфтах из 51, и оба **RP**)
Mage-гайд (Foolipe), секция Rogue/Mage: Spellsteal снимает с цели защитные баффы — **Power Word: Shield** и **HoT'ы друида**.
→ Предлагаю добавить Spellsteal в `## Key cooldowns to track (ours)` и в опенер/бурст-окно всех **RM**-драфтов против `*-rdruid` (4 шт.) и против `*-priest` (3 шт.). Сейчас у нас RM-маг не «крадёт» щит приста вообще нигде.

### 3b. 🔴 Bloodlust — дыра во всех 2v2 `*-rsham` драфтах (упомянут ровно в 1 драфте, и тот 3v3)
Shaman-гайд (Woah): в 2v2/3v3 Bloodlust «much easier for enemy **Shamans and Priests to dispel**».
→ Для **RP** (у нас прист) это прямое правило: **диспелить Bloodlust** — оно нигде не записано. Для RM — правило «пережить BL-окно» (у мага диспела нет).
Там же: **Earth Shield шаман защищает «trash buffs»** (Water Walking / Water Breathing) → диспел приста сперва снимет мусор; закладывать 2 диспела. И: **Mana Tide часто сносится totem-stomp макросом**; **Guardian Totems сокращает КД Grounding**.

### 3c. 🔴 Хантер-драфты: нет ни `bestial wrath`, ни `aimed shot`, ни `scorpid` (0 вхождений)
Hunter-гайд (Veramos):
- **BM = 18-секундное окно Bestial Wrath**; «should you fail to secure the kill it is almost always guaranteed a loss» → **пережить BW-окно = выиграть игру** (ice block / vanish / LoS). Это главный дефенс-триггер против BM-хантера, и его в KB нет.
- **Aimed Shot = Mortal Strike-эффект (−50% хила на 8с)** → для RP это прямой хил-дебафф на приста/рога.
- **Viper Sting + пет не дают пить** — мана-война; у нас `viper` есть только в 2 драфтах.
- **Scorpid Sting** держится на хилере постоянно (снижение шанса попадания).
- **LoS / пиллары Награнда** — сам гайд называет это главной болью хантера → наш пиллар-план засорсен со стороны врага.

⚠ **Коррекция к отчёту 07-13 §3b:** там предлагалось правило «dead-zone / min-range: садиться в мили на хантера». Wowhead-гайд (финальный патч) прямо пишет: **«Removal of the deadzone»**. Формулировку «dead zone» в драфты **не тащить** — либо переписать как «мили-дистанция режет его урон/кайт», либо сперва развести противоречие с doinker08. Хорошо, что не применили.

### 3d. Друид-драфты (Kyxie) — 4 факта, которых нет
- **Faerie Fire** не даёт рогу уходить в стелс (`faerie` — 1 вхождение из 51!). Прямо ломает vanish-restealth план в **любом** `*-rdruid` матчапе.
- **Feral Charge** (11 очков в Feral) = **интеррапт** в bear-form + **Bash**; у тауренов **War Stomp**. `feral charge` — **0 вхождений**.
- **Dire Bear Form** — друид уходит в медведя, **предугадывая стан рога** → наш kidney/CS впустую. `bear form` — 1 вхождение.
- **Cyclone**: цель нельзя ни лечить, ни бить, ни действовать (подтверждает doinker08); **у друида нет magic-диспела**, а его HoT'ы **пёржатся/спеллстилятся** (талант Subtlety снижает шанс).

### 3e. `rm-vs-warrior-rsham` / `rp-vs-warrior-rsham` — сильнейший сигнал за наш план (Woah)
Дословно про Shaman/Warrior: «**no defensive dispel at all**, making any sort of **root** effect completely ruin your life. This means that **Druid and Mage teams are especially nasty** to face against!»
→ Наш RM-маг: **frost nova / root-цепочка = их заявленная погибель**. Вставить в `## Opener` и `## Common mistakes` («не сбивать свой же рут»). Enemy-POV подтверждение текущего плана.

### 3f. `*-retpala-rsham` (Woah) — что ломает наш бурст
Shaman/Ret Pala: **Cleanse + Blessing of Freedom** вытаскивают из рутов; **Blessing of Protection** «instant removing the Mortal Strike effect... **if not quickly dispelled**» → у **RP** прист обязан диспелить BoP (или Mass Dispel по баблу), у **RM** — переключаться, а не долбить BoP-цель. `blessing of protection` — 1 вхождение из 51.

### 3g. `rm-vs-warrior-rdruid` (Foolipe) — периодная формулировка про гонку
Mage-гайд: без хилера против **Warrior + Resto Druid** «the game becomes somewhat of a race — you have to kill one of your two opponents fairly quickly, or they will outlast and slowly wear you down».
→ Второй независимый источник под тайминг-план RM в этом матчапе.

### 3h. Глоссарий — блокер (без изменений с 07-13, список расширился)
`kb/glossary/abilities.json` = 37 записей. Для 3a–3f нужны слаги, которых нет: `spellsteal`, `bloodlust`, `earth-shield`, `grounding-totem`, `bestial-wrath`, `aimed-shot`, `viper-sting`, `scorpid-sting`, `faerie-fire`, `feral-charge`, `bash`, `dire-bear-form`, `mass-dispel`, `blessing-of-protection`, `blessing-of-freedom`, `divine-shield`, `unstable-affliction`.
→ Инлайн `[[ability:...]]` можно ставить **только** из глоссария, поэтому **патч глоссария — первый шаг** перед применением 3a–3f. Могу подготовить его отдельным драфтом на утверждение (spell-id + duration + DR-категория).

## 4. Очереди

- **Закрыто:** mirlol (paywall, не «client-render») — вычеркнуть из списка «попробовать снова», см. память `kb-source-fetchability`.
- **Новое, непрочитанное (WT, через Chrome):** `rogue-swap-in-arenas` (target swap), `rogue-subtlety-openers` (опенеры!), `rogue-kiting`, `rogue-resto-druid-rogue-arena-strategies`, `rogue-healer-dps-vs-double-dps-2v2`. Первые две — потенциально самые ценные для секций `## Opener` во всех драфтах.
- **Wayback/AJ:** остаток `Pri_Rog_2 / Dru_Htr` (низкий приоритет).
- **Видео (yt-dlp = 403 из песочницы):** `PcfLBroowrM` (Earpugs, RP 2100 live comms) → `qJn9rLhDLZU` → `mHgkNzlnpPQ` → `DLEZ7Yi4-jU` → `yKp5DzXgu34`.
- **Silentshadows:** снять локальные копии `arena-strategies/*` пока живы (редирект на WT уже начался).

## 5. Housekeeping

- Stale hypothesis-дубликаты: **12** — ждут удаления владельцем (07-03 §3).
- Незакоммичено: отчёты 07-11…07-13 (untracked) + этот. Ждёт `git add/commit/push`.
- Счётчик тестов «113» в `CLAUDE.md` и в системных инструкциях проекта устарел — фактически **146**.

## 6. Следующие шаги (по убыванию ценности)

1. **Отмашка на enrichment-батч 3a–3g** (+ патч глоссария 3h как предусловие). Это ~10 драфтов и реальные дыры (Spellsteal, Bloodlust-диспел, BW-окно, Faerie Fire), а не косметика.
2. **Решение A/B по `rm-vs-hunter-hpala`** (висит с 07-13).
3. **Прочитать WT `rogue-subtlety-openers` + `rogue-swap-in-arenas`** через Chrome — прямой материал в `## Opener` / `## Alternative opener`.
4. Mirlol: подписка владельца → паст матчапов в ingest (единственный путь к rank-1 per-matchup контенту).
5. Интерактивная сессия для yt-dlp-транскриптов — единственный реалистичный путь разблокировать 4 гипотезы.
