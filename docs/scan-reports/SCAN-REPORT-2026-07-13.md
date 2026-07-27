# Source-scan report — 2026-07-13 (авто-задача)

**Итог: 0 новых sourced-драфтов, 0 засорсенных гипотез** (4 гипотезы остаются заблокированными — блок подтверждён **девятым** независимым источником, и впервые — источником **периода 2.4.3**, см. §2). Главное за ран: найден **новый, ранее не использованный источник — GameFAQs «WoW: The Burning Crusade — Beginner Arena Guide» (doinker08, v1.0 от 14 июля 2008)**. Это единственная за последние ~10 ранов находка, которая (а) плейнтекст и полностью fetchable, (б) написана **внутри патча 2.4.3** (2.4.3 вышел 15.07.2008), (в) содержит per-class и per-comp разделы, включая **явную тактику вражеского hunter+paladin** и **секцию выбора килл-таргета/«hard targets»**. Ничего не аппрувлено, в `kb/matchups/` ничего не мёржено, драфты и гипотезы **не изменялись**.

**Проверки (green):** `validate-kb kb/drafts/` = **51 OK** · `pytest tests/` = **146 passed** · KB не менялась → счётчик драфтов в `test_kb_loader.py` не трогал, `render_slang` не требуется.

---

## 1. Свежий скан (WebSearch/WebFetch)

**Найдено и принято к разбору (1):**

- **GameFAQs, doinker08 — «World of Warcraft: The Burning Crusade — Beginner Arena Guide»**
  `https://gamefaqs.gamespot.com/pc/928901-world-of-warcraft-the-burning-crusade/faqs/53491`
  Плейнтекст (~1700 строк), server-rendered, прочитан полностью в релевантных частях (классы, 2v2/3v3-комп-листы, «Targets»/«Hard targets»). **Датировка:** в теле — «Version 1.0 — July 14, 2008; Copyright 2008 — doinker08»; в шапке страницы GameFAQs — «Version 1.01 | Updated: 01/21/2026» (косметическая правка/артефакт витрины). Содержательно **TBC-чист**: ни DK, ни глифов, ни dispersion/shadowfiend-механик; все упоминания — 2.4-реалии (resilience, BigRed BM, Dru/Rog как «новый Dru/Warr»). Уровень — **class + comp**, НЕ per-matchup.

**Отклонено (3):**

| Источник | Причина отклонения |
|---|---|
| `mmo-champion.com/threads/700315` «Rogue/Druid(resto) Guide 2v2» (screwzx, 2010-03-08) | **WotLK, не TBC.** Глифы, Nourish, Dispersion, mutilate/envenom-ротация, wowarmory 3.x talent-calc. Правило «клиент 2.4.3» → в `sources` не берём, несмотря на то, что там есть enemy-POV «Arcane mage + Rogue» и «Hunter + X» (это было бы ценно, будь оно TBC) |
| `frostyboost.com`, `overgear.com`, `accountshark.net` (новые в выдаче по RMP) | буст-/аккаунт-селлеры, категория aoeah/koroboost/ssegold — решение 07-08 §5. Ни одного автора-игрока, ни одного per-matchup |
| `forum.warmane.com/showthread.php?t=371848` («BC Rogue/Mage 2s request for guides») | тред мёртв: vBulletin отдаёт «No Topic specified» |

**Инфра-наблюдение (важно для карты источников):** `silentshadows.net/guides/tbc-rogue-pvp-tactics/` теперь **301-редиректится на `warcrafttavern.com/tbc/guides/type/classes/rogue/`** — то есть на client-rendered листинг, из которого WebFetch достаёт только шелл. Пер-комп страницы silentshadows (`/arena-strategies/<comp>/`) пока живы (ими уже пользовались). Похоже, silentshadows поглощается WT — **имеет смысл снять локальные копии тех страниц silentshadows, что уже в `sources`, пока они отдаются**.

**Conflation дня (десятый раз):** запрос про `mage+resto-druid` снова вернул сводку про **rogue**+rdruid («Rogue/Druid is the best 2v2 comp…»). Не брал.

## 2. Гипотезы: по-прежнему 4, блок подтверждён девятым источником (впервые — периодным)

Комп-листы doinker08 (полные, прочитаны целиком):

- **2v2 healer/dps:** Dru/War, Dru/Lock, Dru/Hunt, Dru/Rog, Disc/Rog, Pal/War, Sham/War
- **2v2 dps/dps:** Rog/Mage, Rog/Lock, Rog/SPriest, Rog/Rog, SPriest/Lock
- **3v3:** RMP («50% всех 2200+ 3v3»), RWD (30%), RLD, Rsham/War/Retpal, Pal/Lock/SPri, Sham/Lock/SPri, War/Pri/Dru, (Lock|Hunter)/Pri/Dru, Rog/BM-Hunter/SPriest

| Slug | Статус сегодня |
|---|---|
| rm-vs-hunter-hpala | пары нет в комп-листе; **но** есть первый в истории скана **позитивный** сигнал по паре (§2a) |
| rm-vs-hunter-rsham | шаман у doinker08 только в Sham/War и Rsham/War/Retpal — пары нет. Блок прежний |
| rp-vs-hunter-rsham | то же |
| rm-vs-mage-rdruid | друид-пары: War/Lock/Hunt/Rog — mage+rdruid нет и здесь. Блок прежний |

Итого не-мета статус этих четырёх пар подтверждают уже **9 независимых источников** (6 tier-list сайтов + 2 AJ RP-POV гайда + периодный doinker08), причём последний — **современник патча**, а не ретроспектива. Это самое сильное подтверждение из имеющихся.

### 2a. Почему я всё же НЕ написал `rm-vs-hunter-hpala`

doinker08 впервые даёт **прямые утверждения именно про вражеский hunter+paladin**:

- **Hard target:** «resto druids / **hunters w/ paladins** — blessing of freedom helps the two best kiting classes kite even better» → прямой **difficulty-сигнал** (в нашей гипотезе стоит `hard` — совпадает).
- **Их коронный план против мили:** survival-хантер роняет snare trap, паладин вешает на него BoF, хантер «танцует» вокруг трапа (Entrapment проки рута), мили-цель заперта в зоне трапа и получает стрелы, не догоняя.
- **Паладин как цель:** «even more helpless against casters… bubble makes them immune to everything, **but if it's mass dispelled the paladin is in deep trouble**»; «mages/paladins **w/ no mass dispel** — 5 секунд хила и они снова на фулле» → у **RM Mass Dispel'а нет** (это прист-спелл) → паладин для RM — плохой килл-таргет.
- **Хантер как цель:** min-range/dead-zone и LoS — «начни его бить, и его dps падает: без дистанции он не перевесит MS-шот, а его мили-урон ничтожен»; BM: убийство пета отменяет BigRed; MM: viper sting + silencing shot по кастеру, чтобы дрейн нельзя было снять.

Этого хватает на **kill_target, difficulty, Common mistakes и Key cooldowns** — но **не хватает на `## Opener`** (источник не даёт ни опенера, ни trinket-плея для этой пары). Написать опенер «из механик» = синтез = нарушение железного правила → **sourced-драфт не создан**, гипотеза оставлена как есть.

**Решение за владельцем (2 варианта):**
- **A (рекомендую):** оставить гипотезой, ждать per-matchup источник (mirlol-подписка / yt-транскрипты).
- **B:** явно разрешить «partially-sourced» драфт с тегом `synthesized-execution` (прецедент есть — `rp-vs-hunter-hpala` уже написан ровно в таком режиме: comp-level якорь + синтез исполнения, теги `community-sourced/needs-top-source/synthesized-execution`). Если B — драфт `rm-vs-hunter-hpala` можно собрать за один заход, база под него теперь сильнее, чем была у `rp-vs-hunter-hpala` на момент его написания.

## 3. Enrichment-предложения (НЕ применял — жду отмашки)

Все ниже — из doinker08, TBC-периодный, атрибутируемый. Добавляются к очереди 07-06…07-12.

### 3a. 🔴 Пробел, а не enrichment: **Mass Dispel отсутствует во ВСЕХ пяти `rp-vs-*-hpala` драфтах**
`grep` по `kb/drafts/`: `mass dispel` встречается **только в 8 RMP-драфтах**. Ни `rp-vs-warrior-hpala`, ни `rp-vs-rogue-hpala`, ни `rp-vs-mage-hpala`, ни `rp-vs-warlock-hpala`, ни `rp-vs-hunter-hpala` его не упоминают — при том, что у нашего **приста Mass Dispel есть**, а бабл паладина — центральная проблема этих матчапов. doinker08 даёт готовую формулировку («мазать бабл → паладин в глубокой беде, особенно в pve-гире»). **Предлагаю: добавить Mass Dispel в `## Key cooldowns to track (ours)` и в `## If enemy trinkets` всех пяти + в `## Common mistakes` пункт «не потратить MD впустую до бабла».** Это самая дешёвая и самая высокоценная правка за неделю.

### 3b. Хантер-драфты (`rm-vs-hunter-rdruid`, `rp-vs-hunter-rdruid`, `rp-vs-hunter-hpala`) — три правила, которых нет ни в одном
- **Dead-zone / min-range:** садиться в мили на хантера — прямой способ обрезать его dps (он не переустановит MS-шот, мили-урон ничтожен). Сейчас в драфтах это выражено как «не давать кайтить», без конкретики про минимальную дистанцию.
- **BM:** убийство пета **отменяет** BigRed (и рушит интимидейт/реген); альтернатива — LoS/разбежаться и переждать.
- **MM:** связка **viper sting → silencing shot** по нашему касту (прист/маг) — дрейн нельзя снять сразу. Слово `silencing` не встречается **ни в одном** драфте.
- **Survival:** Entrapment + BoF-танец вокруг snare-трапа (для hpala-варианта — прямая контр-мера: не заходить в зону трапа, рвать дистанцию рогом через ShS/Sprint, а не бежать напролом).

### 3c. `rm-vs-warrior-rdruid` / `rp-vs-warrior-rdruid` — difficulty-сигнал периода
doinker08: «Rog/Mage — sheep one target, blow up another; **good against dru/warr**» и «Dru/War — самый популярный комп». Второй независимый источник под текущий `difficulty` (сверить: у нас `easy` в `rm-vs-warrior-rdruid` — совпадает).

### 3d. Друид-драфты (все `*-rdruid`) — две механики
- **Cyclone = полный иммун ко всему**, включая позитивные эффекты; «паладин не выбаблится, маг не выйдет в ice block» — единственный выход тринкет. Полезно в `## If enemy trinkets`.
- **У друида нет диспела** (единственный хилер без него) и **иннервейт можно сдиспелить** → мана-план против друида. У приста RP это прямое правило, у RM — нет.

### 3e. Шаман-драфты (`*-rsham`) — Grounding Totem
doinker08 даёт точную механику: перенаправляет **один** вредоносный спелл раз в **9 секунд**, если тотем не убит. У нас `grounding` упоминается в 7 драфтах, но (по беглому чтению) без числа 9с и без правила «сначала сжечь тотем дешёвым спеллом, потом sheep/CS». Предлагаю унифицировать формулировку по этому источнику.

### 3f. Локи-драфты (`*-warlock-*`) — два правила
- **Unstable Affliction:** диспел UA бьёт диспеллера (до 6k крит на нересил-цели) **и силенсит** → нашему присту **не диспелить UA** (у RP это критично, оно нигде явно не записано).
- **Destro + Backlash:** мили-хиты по destro-локу прокают инстант-shadowbolt/incinerate → правило для рога: под Backlash-споты не «долбить в лоб», а разменивать через gouge/kidney. Плюс felhound: **диспел + counterspell + высокие спелл-резисты** → маг RM должен учитывать пета как counterspell-угрозу.

### 3g. Глоссарий — блокер для 3a/3b
В `kb/glossary/abilities.json` **37 записей**, и в них **нет**: `mass-dispel`, `viper-sting`, `silencing-shot`, `blessing-of-freedom`, `divine-shield`, `grounding-totem`, `unstable-affliction`. Инлайн `[[ability:...]]` можно ставить только из глоссария → **прежде чем применять 3a/3b/3e/3f, нужно добавить эти 7 слагов** (spell-id + duration + DR-категория). Могу подготовить патч глоссария отдельным драфтом на утверждение.

## 4. Очереди (без изменений)

- **AJ (Wayback):** остаток Faction `Pri_Rog_2` — 1 подстраница `Dru_Htr` (низкий приоритет). Резерв: PomPyro Mage/Rogue, `Pri_Rog_vs_Mag_Wlk` (Mixster), 3v3 `Dru_Mag_Rog_vs_Mag_Pri_Rog` и др.
- **Видео (yt-dlp из песочницы = 403, нужна интерактивная сессия):** `PcfLBroowrM` (Earpugs, RP 2100 с live comms) → `qJn9rLhDLZU` → `mHgkNzlnpPQ` → `DLEZ7Yi4-jU` → `yKp5DzXgu34` → плейлист `PLrxHsk5qvXbAkVwbVj9Iqp8fvTwk0qcku`.
- **Новое в очередь:** снять локальные копии страниц `silentshadows.net/arena-strategies/*`, пока они не ушли в редирект на WT (см. §1).

## 5. Housekeeping

- Stale hypothesis-дубликаты: по-прежнему **12** — ждут удаления владельцем (07-03 §3).
- `docs/NEXT-SESSION-HANDOFF.md` датирован 06-23 (39/16) — актуально **51 драфт / 16 гипотез (4 незасорсенных)**.
- В `CLAUDE.md` и в системных инструкциях проекта счётчик тестов «113» устарел — фактически **146 passed**.
- Незакоммиченное: отчёты 07-11, 07-12 (untracked) + этот. Ждёт ручного `git add/commit/push`.

## 6. Следующие шаги (по убыванию ценности)

1. **§3a — Mass Dispel в пяти `rp-vs-*-hpala`.** Реальный пробел в KB, а не украшение. Источник готов.
2. **Решение по §2a: A или B** для `rm-vs-hunter-hpala`.
3. **§3g — патч глоссария** (7 слагов), он же разблокирует 3a/3b/3e/3f.
4. Отмашка на накопленный enrichment-бэклог (07-06…07-13).
5. Интерактивная сессия: yt-dlp транскрипты — единственный реалистичный путь разблокировать 4 гипотезы, кроме mirlol-подписки.
