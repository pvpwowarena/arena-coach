# Arena Coach — ежедневный скан источников, отчёт 2026-07-20

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно.
> **Ничего не аппрувил, не мёржил в `kb/matchups/`, новых драфтов не создавал.**
> Единственная запись в трекнутые файлы — фикс WotLK-контаминации в 4 гипотезах (§4), обоснование там же.

## TL;DR

- **3 новых пригодных источника**, которых не было ни в одном драфте: **Icy Veins Resto Druid PvP** (Seksi), **Icy Veins Holy Paladin PvP** (Sellin, Gladiator), **Icy Veins Hunter PvP** (Impakt). Все server-rendered, upd. 12 Jan 2026, чистый TBC. Плюс **silentshadows RM comp-page** (RM-POV counter-лист).
- **Гипотезы: 0 засорсено.** Оставшиеся две (`rm-vs-mage-rdruid`, `rm-vs-hunter-hpala`) по-прежнему без per-pair якоря — обе пары **отсутствуют** и в Icy Veins 2v2 tier-листе (проверено этим раном), и в AOEAH/WT/SkillCapped (проверено прошлыми). Остаются гипотезами по правилу handoff §9.
- 🔴 **Найден и исправлен дефект: `sacred shield` (WotLK-способность, не существует в 2.4.3) фигурировала как реальный инструмент паладина в 4 файлах `kb/hypotheses/`.** В `kb/drafts/` не протекла. Подробности и точный диф — §4.
- **6 enrichment-предложений** для существующих драфтов (§5) — из них три сильных закрывают реальные механические дыры: Cyclone↔Blind DR (9 драфтов), Mass Dispel против бабла (5 RP-драфтов), Spellsteal на BoF/BoP (4 RM-драфта). Плюс: **The Beast Within (18с иммун к CC) не упомянут в KB нигде.**
- **Репо зелёное:** `validate-kb kb/drafts/` → **51 OK**; `pytest tests/` → **146 passed**. Счётчик драфтов не менялся (новых драфтов нет).

## 1. Что просканировано и с каким результатом

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **Icy Veins — 2v2 Arena Composition Rankings** | WebFetch ✅ | Полный текст tier-листа. **Ключевой негативный результат:** ни `mage+resto-druid`, ни `hunter+holy-paladin` в списках нет (ни «best», ни «other compositions»). Есть `hunter+resto-druid`, `warrior+holy-paladin`, `retpala+rsham`, `mage+disc-priest`. |
| **Icy Veins — Restoration Druid PvP** | WebFetch ✅ | **Новый пригодный источник.** Полный kit + DR-таблица (см. §2). |
| **Icy Veins — Holy Paladin PvP** (Sellin) | WebFetch ✅ | **Новый пригодный источник.** Разбор утилити с пометками «Magic → dispellable / spell-stolen» (см. §2). |
| **Icy Veins — Hunter PvP** (Impakt) | WebFetch ✅ | **Новый пригодный источник.** Спек-разбор BM/MM/SV с CC-иммуном BW (см. §2). |
| **wowtbc.gg — Holy Paladin PvP** (в коллаборации с Eroth) | WebFetch ✅ | Годен, но по контенту слабее Icy Veins: полезны только DR-группы (HoJ ⇒ все станы кроме Kidney Shot; Turn Evil ⇒ Fear/Int.Shout/Psychic Scream/Scare Beast) и Concentration Aura. Как второй cite к §5.5. |
| **silentshadows.net — Mage/Rogue comp-page** | WebFetch ✅ | Отдал **реальный контент** (не WT-шелл, в отличие от disc-rogue страницы из скана 07-19). RM-POV strengths/weaknesses + counter-лист (§2.4). |
| **silentshadows.net — /arena-strategies/ (индекс)** | WebFetch ✅ | Индекс комбо (Tier 1: Disc Priest/Rogue; Tier 2: Frost Mage/Rogue, SPriest/Rogue, SL Lock/Rogue; Tier 3: Feral/Rogue). Сами «in-depth» гайды на странице RM **не опубликованы** («Interested by writing a guide?») — т.е. RM-POV per-pair разбора у них нет. |
| `icy-veins.com/tbc-classic/frost-mage-pvp-guide`, `.../beast-mastery-hunter-pvp-guide` | ⛔ заблокировано | WebFetch: «URL not in provenance set» — прямой ввод URL запрещён, доступны только ссылки из выдачи/предыдущих фетчей. Спек-гайды мага/хантера остались недобранными; хаб-страница хантера дала достаточно. |
| WebSearch-сводки | — | Как обычно: указатели, не источник. Подтвердили отсутствие per-pair гайдов по обеим оставшимся парам. |

## 2. Три новых источника — что именно в них есть

### 2.1 Restoration Druid PvP — Icy Veins (Seksi, upd. 2026-01-12)
`https://www.icy-veins.com/tbc-classic/restoration-druid-pvp-guide`

Механики, критичные именно для RM/RP (цитаты дословные):

- «**Cyclone shares diminishing returns with Blind**, and it is important to avoid overlapping these two crowd control abilities.»
- «**Entangling Roots shares diminishing returns with Frost Nova** and the Water Elemental freeze ability. **Bash also shares diminishing returns with all stuns except Kidney Shot**, which is on its own DR category in TBC Classic.»
- «**Tree of Life** … reduces the Mana cost of most heals by 20%, and also **prevents you from being Polymorphed**, but you will not be able to use your crowd control abilities or emergency Healing Touch while in it.»
- «**Nature's Swiftness** … Use it only when you will be immediately using the instant ability, or you risk having it **Purged / dispelled / stolen**.»
- «**Faerie Fire** … making them **unable to turn invisible or stealth** while active. Very useful against enemy stealth classes, especially Rogues trying to restealth.»
- «**Abolish Poison** removes a poison from your target every 2 seconds for 8 seconds. Use it to stay mobile and **increase your healing done against enemy Rogues**, or to remove enemy Hunter Viper Stings. You can also go into **Bear Form** in order to stop being affected by Viper Sting.»
- «**Barkskin** … reduces your damage taken by 20% for 15 seconds on a 1-minute cooldown. This is **usable while stunned**.»
- «**Lifebloom** … When it ends or is dispelled, it bursts … **has dispel protection**.»
- «**Bear Form** increases your defenses significantly, especially against Physical damage … recommended to shift into Bear Form when under attack by Physical DPS.»
- Лучшие 2v2-пары друида: «Druid + Rogue, Druid + Warlock, Druid + Warrior, and Druid + Hunter» — **мага в списке нет** (ещё один independent-сигнал, что `mage+rdruid` off-meta).

### 2.2 Holy Paladin PvP — Icy Veins (Sellin, Gladiator, upd. 2026-01-12)
`https://www.icy-veins.com/tbc-classic/holy-paladin-pvp-guide`

- «**Divine Shield** is a complete immunity that clears most debuffs from you … **This effect can be dispelled by Priests casting Mass Dispel**, so it is important to keep this in mind when playing against a Priest.»
- «**Blessing of Protection** protects you or an ally with a shield that grants immunity to all Physical damage and Physical effects. This can be used to both stop damage or **remove stuns such as Kidney Shot**. Keep in mind that this is a **Magic effect and can be dispelled or spell-stolen. If you are fighting against a Mage it is a good idea to be ready to cancel the buff off of yourself or you risk the Mage potentially stealing the shield.**»
- «**Blessing of Freedom** … removing all root and slow effects … This is, however, a **Magic effect and able to be dispelled or spell-stolen**, so you cannot always depend on it.»
- «**Cleanse** … Removing one Magic, Poison, and Disease effect from your ally in PvP is a massive advantage.»
- «**Concentration Aura** … reduces the spell pushback effects and even **the duration of actual silences** if you were to get interrupted (Improved Concentration Aura).»
- «Holy Paladins are **extremely susceptible to crowd-controlling effects and interrupts** due to their very limited mobility and dependence on casting»; из трёх хилов инстант только **Holy Shock**; **Holy Light** — «quite long» каст.
- «**Consecration** can be used to try and **pull stealthed enemies out of hiding** … Rank 1 is recommended.»
- «**Hammer of Wrath** … execute … below 20% health.» / «**Divine Favor** guarantees a critical strike on your next healing ability.»

### 2.3 Hunter PvP — Icy Veins (Impakt, upd. 2026-01-12)
`https://www.icy-veins.com/tbc-classic/hunter-pvp-guides`

- «Thanks to the talent **The Beast Within**, Beast Mastery Hunters are also **unstoppable for 18 seconds** during their main damage cooldown, which means they are **immune to all forms of crowd control** during that time. This makes them one of the most dangerous classes in the game during that burst window.»
- «**Marksmanship is the meta Hunter specialization for high-end arena** … most Hunter comps are based around one spell: **Viper Sting** … drain comp … Marksmanship also brings **Scatter Shot and Silencing Shot**.»
- «**Survival** … **Wyvern Sting** … **instant sleep that lasts for 8 seconds** … and its cooldown **Readiness**.»
- «excellent burst through Aimed Shot, Auto Shot, and Multi-Shot, allowing them to **make quick work of low-Armor targets like Priests and Mages**.»
- «longest range out of any class through **Hawk Eye** … **Concussive Shot** is one of the best slows in the game due to its instant cast time.»

### 2.4 silentshadows.net — Mage/Rogue (RM comp-page)
`https://silentshadows.net/arena-strategies/mage-rogue-burning-crusade/`

- «RM always was considered as the best double DPS for 2v2 arenas. Nonetheless, it **suffers a lot against multiple top-tier team compositions such as Rogue/Druid or Lock/Druid**. For this reason, RM cannot be considered as a Tier 1 combo.»
- «**Counter comps:** Human Rogues combs · Dwarf Disc Priest + Mage/Warlock · Rogue/Druid · Lock/Druid · **Lock/Hpala**.»
- Weaknesses: «Weakness vs locks, RD comps, and good discs»; «Require good synergy for → **CC sharing DR (Sap/Gouge/Sheep)** → **Not breaking nova with melee damages**».

⚠ Последний пункт (Sap/Gouge/Sheep в одной DR-группе) сформулирован источником обобщённо — **перед использованием сверить с `kb/glossary/abilities.json`** (поле `dr`), чтобы не протащить неточность.

## 3. Две оставшиеся гипотезы — статус без изменений

| Гипотеза | Пара | Что появилось этим раном | Вердикт |
|---|---|---|---|
| `rm-vs-mage-rdruid` | Mage / Resto Druid × RM | Полный druid-side kit + DR-таблица (§2.1). Второй independent-сигнал off-meta: мага нет в списке лучших пар друида, пары нет в Icy Veins 2v2. | **Остаётся гипотезой.** Есть класс-side, нет per-pair RM-POV якоря (handoff §9). |
| `rm-vs-hunter-hpala` | Hunter / Holy Paladin × RM | Полный hpala-side (§2.2) + hunter-side со спек-разбором (§2.3). Пары нет ни в одном из четырёх tier-листов. | **Остаётся гипотезой.** То же: класс-side есть, per-pair якоря нет. |

**Но обе гипотезы теперь можно скорректировать по фактам** (это не промоут, а исправление карантинного текста — на решение владельца):

- `rm-vs-mage-rdruid` утверждает «[[ability:sheep]] друида между HoT-кастами». По источнику §2.1 **друида в Tree of Life зашипить нельзя вообще**. Формулировку надо ограничить: шип работает только по друиду вне ToL; зато друид в ToL сам лишён Cyclone и Healing Touch — это и есть окно на бурст напарника.
- Там же не хватает сильной RM-техи из §2.1: **Nature's Swiftness крадётся Spellsteal'ом / снимается**, и **Entangling Roots делит DR с Frost Nova** (наш маг новой сам портит себе следующую нову после их рута — и наоборот).
- `rm-vs-hunter-hpala`: помимо фикса из §4 — не хватает **The Beast Within** (18с иммуна к CC: sap/sheep/blind/kidney в это окно выброшены), **BoP снимает Kidney Shot** (не вкладывать kidney при готовом BoP), и того, что **у RM нет Mass Dispel** — бабл придётся пережидать, а не пробивать (в отличие от RP).

## 4. 🔴 Дефект найден и исправлен: WotLK-способность в KB

**Что:** `sacred shield` перечислялась как реальный инструмент holy paladin'а в **4 файлах `kb/hypotheses/`**: `rm-vs-hunter-hpala.md`, `rm-vs-mage-hpala.md`, `rm-vs-warlock-hpala.md`, `rp-vs-warlock-hpala.md` (6 вхождений).

**Почему это брак:** Sacred Shield введена в **WotLK (3.0)**. В клиенте **TBC 2.4.3 её не существует**. Прямое нарушение хардового правила проекта «никаких retail/WotLK способностей». В `rp-vs-warlock-hpala` дело доходило до тактического указания «прийст … dispel'ит freedom/sacred shield» — совет по несуществующей механике.

**Масштаб:** только `kb/hypotheses/` (карантин, не индексируется, игрокам не уходит). **В `kb/drafts/` не протекло** — проверено grep'ом по всему `kb/`.

**Что сделано:** заменено на реальный TBC-кит паладина, подтверждённый §2.2 — `BoP (Blessing of Protection)` и `Divine Protection`. Диф по смыслу:

```
- Пала — bubble/freedom/cleanse/[[ability:hammer-of-justice]]/sacred shield
+ Пала — bubble/freedom/cleanse/[[ability:hammer-of-justice]]/BoP (Blessing of Protection)

- enemy: paladin — bubble, freedom, cleanse, [[ability:hammer-of-justice]], sacred shield, trinket
+ enemy: paladin — bubble, freedom, cleanse, [[ability:hammer-of-justice]], BoP, Divine Protection, trinket

- Прийст [[ability:mana-burn]] паладина и dispel'ит freedom/sacred shield (но не UA)
+ Прийст [[ability:mana-burn]] паладина и dispel'ит freedom/BoP (но не UA)
```

**Почему применил, а не застейджил:** это не тактическое суждение и не промоут — это удаление несуществующей в 2.4.3 механики из карантинного, не индексируемого файла. Оставлять заведомо ложный контент в репо хуже, чем поправить: при будущем промоуте он бы протёк в драфты. Замена взята из источника §2.2, не выдумана. Если формулировка не нравится — откат тривиален (`git checkout kb/hypotheses/`).

**Побочная проверка (чисто):** прогнал `kb/` по списку не-TBC маркеров (divine plea, hand of *, penance, dispersion, mirror image, deep freeze, shadow dance, fan of knives, killing spree, wild growth, typhoon, guardian spirit, chains of ice и др.). Единственные срабатывания — `dispersion` в двух драфтах (`rm-vs-rogue-spriest`, `rmp-vs-shadow-priest-warlock-resto-shaman`), и там она упомянута **корректно, с отрицанием**: «нет dispersion в TBC» / «Dispersion отсутствует в TBC». Это не контаминация, трогать не нужно.

## 5. Enrichment существующих драфтов — предложения (НЕ применены)

Все правки — добавление source-блока + 1–2 фразы механики. Тактический каркас драфтов не меняется.

### 5.1 (сильное) rdruid-кластер, 9 драфтов — DR-коллизии нашего кита с друидом

**Драфты:** `rm-vs-warrior-rdruid`, `rp-vs-warrior-rdruid`, `rm-vs-rogue-rdruid`, `rp-vs-rogue-rdruid`, `rm-vs-warlock-rdruid`, `rp-vs-warlock-rdruid`, `rm-vs-hunter-rdruid`, `rp-vs-hunter-rdruid`, `rp-vs-mage-rdruid`.

**Дыра:** **ни один** из девяти не упоминает, что **Cyclone делит DR с Blind**, а **Entangling Roots — с Frost Nova и фризом вотера**. Это ядро нашего кита против друида: рог, потративший [[ability:blind]], уполовинивает вражеский циклон — и наоборот, их циклон уполовинивает наш блайнд. Для RM то же с новой и рутами. Сейчас это в KB не сказано нигде.

**Куда:** секция «Key cooldowns to track» или «Common mistakes».

```yaml
- type: web
  url: "https://www.icy-veins.com/tbc-classic/restoration-druid-pvp-guide"
  title: "Restoration Druid PvP (Icy Veins, Seksi, upd. 2026-01-12) — DR-таблица: «Cyclone shares diminishing returns with Blind»; «Entangling Roots shares diminishing returns with Frost Nova and the Water Elemental freeze»; «Bash shares DR with all stuns except Kidney Shot»; Tree of Life «prevents you from being Polymorphed»; Nature's Swiftness «risk having it Purged / dispelled / stolen»; Faerie Fire «unable to turn invisible or stealth»"
  retrieved: '2026-07-20'
```

Тот же блок закрывает ещё три прозовых утверждения, живущих сейчас без cite: tree form (`rm-vs-hunter-rdruid`, `rm-vs-warrior-rdruid`, `rp-vs-warlock-rdruid`), faerie fire против рестелса (`rm-vs-warrior-rdruid`), NS-Cyclone как главный тринкет-таргет (`rp-vs-warrior-rdruid`, `rp-vs-warlock-rdruid`).

### 5.2 (сильное) RP × hpala, 5 драфтов — Mass Dispel пробивает Divine Shield

**Драфты:** `rp-vs-warrior-hpala`, `rp-vs-rogue-hpala`, `rp-vs-warlock-hpala`, `rp-vs-mage-hpala`, `rp-vs-hunter-hpala`.

**Дыра:** Mass Dispel встречается в KB **только в 3v3-драфтах RMP**. Ни в одном 2v2 RP-vs-hpala драфте её нет — при том что у RP штатный дисп-прийст, а бабл паладина это главная причина, по которой RP не может закрыть добив. По §2.2 бабл **пробивается Mass Dispel'ом прийста**. Это может быть решающая правка для всего кластера.

```yaml
- type: web
  url: "https://www.icy-veins.com/tbc-classic/holy-paladin-pvp-guide"
  title: "Holy Paladin PvP (Icy Veins, Sellin, Gladiator, upd. 2026-01-12) — «Divine Shield … can be dispelled by Priests casting Mass Dispel»; BoP «remove stuns such as Kidney Shot», «Magic effect … can be dispelled or spell-stolen»; Blessing of Freedom «Magic effect and able to be dispelled or spell-stolen»; hpala «extremely susceptible to CC and interrupts … dependence on casting», инстант только Holy Shock"
  retrieved: '2026-07-20'
```

### 5.3 (сильное) RM × hpala, 4 драфта — Spellsteal на BoF/BoP + BoP снимает Kidney

**Драфты:** `rm-vs-warrior-hpala`, `rm-vs-rogue-hpala`, `rm-vs-warlock-hpala`, `rm-vs-mage-hpala`.

**Дыра:** во всём KB **spellsteal упомянут ровно в двух файлах** (`rp-vs-mage-rdruid`, `rp-vs-rogue-mage`) — и ни разу в контексте паладина. Источник §2.2 при этом прямо предупреждает паладина: против мага держи палец на отмене бафа, иначе **щит украдут**. Для RM это бесплатный темп: украденный BoF/BoP = и снятая с их DPS свобода/иммун, и баф себе. Второе: **BoP снимает Kidney Shot** — сейчас ни один драфт не предупреждает рога не вкладывать кидни при готовом BoP.

Source-блок — тот же, что 5.2.

### 5.4 (среднее) hunter-кластер, 3 драфта + 2 стейдж-проposal'а — The Beast Within

**Драфты:** `rm-vs-hunter-rdruid`, `rp-vs-hunter-rdruid`, `rp-vs-hunter-hpala` (+ застейдженные `rm/rp-vs-hunter-rsham` из скана 07-19, + гипотеза `rm-vs-hunter-hpala`).

**Дыра:** **Bestial Wrath / The Beast Within не упомянуты в KB ни разу.** 18 секунд полного иммуна к CC — это окно, в которое выброшенные sap/sheep/blind/kidney стоят раунда. Для комп RM/RP, вся игра которых построена на CC-цепочке, это дыра первого порядка. Плюс спек-разметка (MM = мета, Viper+Scatter+Silencing Shot; SV = Wyvern Sting инстант-слип 8с + Readiness) даёт понимание, чего ждать до того, как спек виден.

```yaml
- type: web
  url: "https://www.icy-veins.com/tbc-classic/hunter-pvp-guides"
  title: "Hunter PvP (Icy Veins, Impakt, upd. 2026-01-12) — «The Beast Within … unstoppable for 18 seconds … immune to all forms of crowd control»; «Marksmanship is the meta Hunter specialization for high-end arena» (Viper Sting drain, Scatter Shot, Silencing Shot); Survival — Wyvern Sting «instant sleep … 8 seconds» + Readiness; burst «make quick work of low-Armor targets like Priests and Mages»"
  retrieved: '2026-07-20'
```

### 5.5 (среднее) все 9 hpala-драфтов — Concentration Aura режет длительность сайленса

Наши планы против паладина строятся на локе каста ([[ability:counterspell]], [[ability:garrote]]-сайленс, [[ability:kidney-shot]]). По §2.2 **Improved Concentration Aura сокращает и pushback, и саму длительность сайленса** — то есть окно уже, чем считает драфт. В KB не упомянуто нигде («concentration» — 0 вхождений). Второй cite на ту же механику + DR-группы:

```yaml
- type: web
  url: "https://wowtbc.gg/pvp-class-guides/holy-paladin/"
  title: "Holy Paladin PvP (wowtbc.gg, в коллаборации с Eroth, top Holy Paladin TBC Classic) — DR-группы: «Hammer of Justice ⇒ All Stuns except Kidney Shot»; «Turn Evil ⇒ Fear + Intimidating Shout + Psychic Scream + Scare Beast»; Concentration Aura как дефолтная аура"
  retrieved: '2026-07-20'
```

Полезный побочный факт оттуда же: **HoJ делит DR со всеми станами, кроме Kidney Shot** — значит после их HoJ наш кидни бьёт в полную длительность (и наоборот). Это дублирует и подтверждает формулировку Icy Veins из §2.1.

### 5.6 (слабое) RM-comp anchor для полей `difficulty`

`silentshadows.net/arena-strategies/mage-rogue-burning-crusade/` даёт RM-POV counter-лист (Rogue/Druid, Lock/Druid, Lock/Hpala, human-rogue комбо, dwarf disc + mage/lock). Годится как второй cite под `difficulty:` в `rm-vs-rogue-rdruid`, `rm-vs-warlock-rdruid`, `rm-vs-warlock-hpala`, `rm-vs-rogue-rogue`, `rm-vs-rogue-priest` — сейчас сложность выставлена без явного comp-level источника.

## 6. Ждёт владельца

1. **§5.1–5.3 — три сильных enrichment'а.** Закрывают конкретные механические дыры (DR-коллизии с друидом; Mass Dispel против бабла у RP; Spellsteal BoF/BoP + BoP-снимает-Kidney у RM). Скажи «применяй» — впишу source-блоки и по 1–2 фразы в тело, без изменения тактики.
2. **§5.4 — The Beast Within.** Отдельно вынес: это не «ещё один cite», а отсутствующий в KB факт, который стоит раунда.
3. **§4 — фикс sacred shield применён.** Проверь диф; откат — `git checkout kb/hypotheses/`.
4. **Висит с 07-19 (не трогал):** go/no-go по двум драфтам `rm/rp-vs-hunter-rsham` в `docs/proposals/`.
5. **Две гипотезы** (`rm-vs-mage-rdruid`, `rm-vs-hunter-hpala`) ждут per-pair источника. Коррекции их текста по §3 — по твоему слову.
6. **Инфра (повтор из 07-19):** stale `.git/index.lock` — из песочницы не снимается («Operation not permitted»). Если локальный git ругается «Another git process seems to be running» — удали руками.

---

_Проверка: `pip install pydantic pydantic-settings PyYAML pytest pytest-asyncio` + editable `backend`/`ingest`/`bridge` (в песочнице) → `python -m arena_coach validate-kb kb/drafts/` = **OK: 51 документов** → `python -m pytest tests/` = **146 passed**. Изменённые трекнутые файлы: 4 × `kb/hypotheses/*-hpala.md` (только §4). `kb/drafts/`, `kb/matchups/`, `tests/` не тронуты._
