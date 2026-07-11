# Source-scan report — 2026-07-08 (авто-задача)

**Итог: 0 новых sourced-драфтов** (4 гипотезы остаются заблокированными — блок перепроверен с новой стороны, см. §2), но AJ-дочитка дала **4 страницы enrichment-материала**, включая **обе зеркальные пары** (RM vs RP и RP vs RM) — по ним у нас были худшие источники (только Mirlol-транскрипт). Плюс каталогизирован **полный 2v2/3v3-индекс AJ**: найден резерв enemy-POV гайдов (в т.ч. Megatf Druid/Hunter, WLD-POV и RLD-POV для 3v3). Ничего не аппрувлено, в `kb/matchups/` ничего не мёржено, драфты не изменялись.

**Проверки (green):** `validate-kb kb/drafts/` = **51 OK** · `pytest tests/` = **113 passed** · KB не менялась → счётчик тестов и render_slang без изменений. Браузер подключён (Browser 1, macOS).

---

## 1. AJ-дочитка (4 страницы по плану 07-07 §7)

Все четыре бьют ровно в драфты, у которых сейчас единственный источник — Mirlol-транскрипт:

| Драфт (строк) | Прочитано | Ключевое |
|---|---|---|
| `rm-vs-rogue-priest` (46) | Icycake `Mage_Rogue_vs_Pri_Rog` (snapshot 2009-02-14, комменты фев–окт 2008) | план + топ-энд комменты Sèlect (Mattyo→Houndus) |
| `rp-vs-rogue-mage` (68) | Mixster `Pri_Rog_vs_Mag_Rog` (snapshot 2008-12-10) | зеркальный POV + дерево решений Yzaron |
| `rm-vs-hunter-rdruid` (34, самый тонкий) | Icycake `Mage_Rogue_vs_Dru_Htr` (snapshot 2008-12-15) | Glacierx-опенер + pet-kill линия + 3 enemy-POV |
| `rp-vs-rogue-rogue` (40) | Mixster `Pri_Rog_vs_Rog_Rog` (snapshot 2008-12-03) | киллчейн Rng + race-зависимость difficulty |

**⚠ Правило дат для этих снапшотов:** wayback-редирект отдаёт снапшоты дек-2008/фев-2009 — в них больше комментариев, чем в июльском 20080720052414. Патч 3.0.2 (WotLK-механики) = **2008-10-14**; все использованные комменты ≤ 2008-10-13, TBC-чистые. Единственный пост-патчевый (Miniboss, 30 ноя 2008, Dru_Htr) — вопрос без механик, не использован. При будущих дочитках: комменты с датой ≥ 2008-10-14 фильтровать.

## 2. Гипотезы: осталось 4, блок подтверждён с новой стороны

Полный 2v2-индекс AJ-вики (20080720052414) перечитан целиком: гайдов **Druid/Mage (resto), Hunter/Paladin, Hunter/Shaman (resto)** не существует ни с нашей, ни с вражеской стороны («Beast Mastery Hunter/Shaman» = ele-шаман, установлено 07-06; «Moonkin Druid/Mage» = balance, НЕ якорь для mage+resto-druid). Матчап-списки обоих наших гайдов (Icycake 14, Mixster 16) этих пар тоже не содержат — перепроверено сегодня по живым страницам.

| Slug | Статус сегодня |
|---|---|
| rm-vs-hunter-hpala | AJ-индекс: пары нет нигде. Targeted-поиск — ничего нового. Блок прежний |
| rm-vs-hunter-rsham | то же; Wowhead rsham-гайд: лучшие пары rsham = RetPala/Warr/Rogue — hunter+rsham не мета (доп. подтверждение не-меты) |
| rp-vs-hunter-rsham | то же |
| rm-vs-mage-rdruid | targeted-поиск снова отдаёт conflation с rogue+rdruid (WebSearch-сводка склеила «Rogue/Druid» в ответ про mage+rdruid — классика, не использовать). Блок прежний: нужен RM-POV или пара-оценка |

Пути прежние: mirlol Twitch-sub владельца → `arena_ingest paste`; yt-dlp транскрипт `DLEZ7Yi4-jU` в интерактивной сессии (песочница — 403, известно).

## 3. Enrichment-предложения (НЕ применял — жду отмашки; добавляются к очереди 07-06/07-07)

### 3a. `rm-vs-rogue-priest` ← AJ Icycake Mage_Rogue_vs_Pri_Rog
База Icycake: kill target — их **рог**, прист в CC; брать Shadow Sight; рог держит **Rupture на их роге** — иначе vanish→отхил; опенер garrote/premed; после blind — CS в хилы + новый sheep-цикл; элементаль на рога. Комменты: **Youdienow** — garrote переживает rupture, не дублировать: premed→garrote→shiv→KS (выбить тринкет); не стоять рядом (двойной fear). **Sèlect (со слов Mattyo→Houndus, топ-энд)**: против дефенсив-RP — garrote прист + малый шаттер → выманить их рога, мгновенный sheep; **фейк-sheep = бейт SW:D** → следом полный 8с sheep; бейт Pain Suppression ранним burst до ~60%; re-cast rank-1 frost armor — прист жжёт ману на диспелы. **Hyperz**: opener sap-прист + спам spellsteal (щит/форта/inner fire) — с поправкой **Zukias**: spellsteal ломает re-sap (combat). **Screwz**: макрос ShS+KS против evasion. Дисент-блок в Common mistakes: **Zerokelvin** — без Perception дисц-прист свободно диспелит/манабёрнит («very hard»); **Omonera/Seabreeze** — в мутилейт-рога без cheat death идти можно, в остальных cheat death + battlemaster's рушит килл.

### 3b. `rp-vs-rogue-mage` ← AJ Mixster Pri_Rog_vs_Mag_Rog (зеркало 3a!)
База Mixster: **не поймать sheep** — главное правило; LoS-дисциплина приста (не выходить хилить при CS у мага, выбить CS раньше); HoT+щит на рога постоянно; **SW:D прерывает шипы**; blind сразу после тринкета их рога; cloak на 5 wounding / под фростболты; mind-numbing+crippling на мага. Комменты: **Daghost** — SW:D-брейк собственного шипа (тайминг по кастбару) + ShS→gouge→быстрый хил на ~50%; **Yzaron** — дефенсивное дерево A/B/C (элементаль+frostbolt→fear обоих вместе с элементалем; sheep рога→мгновенный диспел; sheep приста→шаг за пиллар/SW:D), не гнаться за рогом на 1%, тринкет только на blind, диспелить новы против шаттера; **Pressured** — держать 2-3pt rupture на их роге против re-stealth (проигрывал при 15-30% HP у рога именно из-за restealth-open); **Phishyz** — спек-развилка: sstep-рог липнет к магу, mut/combat вынуждены в рога (нюанс: наш RP-драфт не фиксирует спек нашего рога — стоит отметить в тексте); **Chingwang** — бейт CS → окно flash heal.

### 3c. `rm-vs-hunter-rdruid` ← AJ Icycake Mage_Rogue_vs_Dru_Htr (драфт самый тонкий — 34 строки)
База Icycake: sheep хантер → валим друида; IB от viper/trap; blind хантера после DR поли; маг ООМ = проигранный бой (viper = таймер). **⚠ Поправка комьюнити (Haiku/Sufferer): «blind/sap хантера после шипа» у Icycake — брак**: пет держит хантера в комбате (sap невозможен) + sheep/sap на одном DR — в драфт не тащить. **Glacierx (2000-2200, ~60% побед) — конкретный опенер**: invis-маг → выпустить элементаля и **пет-атакой первым** (хантер авто-таргетит пета → silencing уходит не в мага) → pet-freeze → frostbolt-шаттер + рог jump → форс NS друида → свап на друида (тринкет хантера потрачен). Дисент **Frixeon (enemy-POV, 2156)**: FD+silencing рушит такой опенер, элементаль умирает с 2 выстрелов → ставка на CC-цикл и target-switching. **Линия pet-kill (Krooked, Zukias, 2k-2.2k)**: выжечь пета → нет пушбека, друид выходит спасать → свап; Zukias: KS по друиду только ≤70% HP (иначе хоты съедят). **Lieto**: тайминг — KS CD 20с, чейн с CS = 16с до следующего стана; blind друида в GCD-окно после NS. **Hermeswins (2050)**: рог вскрывает друида → хантер идёт CC-ить рога → sheep хантера; vanish→sap друида перед концом blind (он out of combat). **Enemy-POV на контр**: Tzatziki — sheep хантера из милишного хага (нет silencing/scatter), элементаль прятать за LoS/шип; Diableria — их план: пет на мага (форс комбата), cyclone рога out of stealth + faerie fire против vanish. Difficulty-сигнал: Tryxt «pretty much the counter comp» на 2000+ — сверить с difficulty драфта.

### 3d. `rp-vs-rogue-rogue` ← AJ Mixster Pri_Rog_vs_Rog_Rog
База Mixster: исход решает опенер-sap; прист mounted (дисент **Disaster**: не маунт — липнуть к своему рогу с полными баффами, sap всё равно догонит); **не спамить fear** — pre-cloak, сидячая утка; тринкет + Pain Suppression рано; двойной UD = worst case (off-target gouge + станы обоих). **Rng — готовый киллчейн**: рог A в CS→KS → 95% тринкет в KS → **blind A → vanish → CS+gouge рога B** → прист отбегает и хилится → добив. **Lieto**: их выигрыш = пережить нашего рога 15с; двойной blind (первый — тринкет, второй — полный) + sap убивает приста — знать угрозу. **Deadlychaos** (не-UD): blind второго сразу → его тринкет → окно fear; KS первому → прист свободен. **Chingwang: race-вилка difficulty** — не-UD «pretty easy» (тринкет в первый fear → blind+sap), двойной UD «VERY hard» — кандидат в difficulty-примечание/Common mistakes. **Maraiah**: rank-1 Holy Nova против stealth-реопенеров (с дисентом Rng «рог, который не может сапнуть нову-спамера — плохой рог»).

## 4. Каталог AJ-индекса: резерв enemy-POV (новое — для будущих ранов)

Полный список comp-гайдов 2v2-индекса, чьи `vs_Mage_Rogue`/`vs_Pri_Rog` подстраницы дадут enemy-POV enrichment наших драфтов: Druid/Hunter (**Therst/Darkalpha** и **Megatf** — два отдельных гайда), Druid/Rogue (+ Dreamstate- и Feral-варианты), Druid/Warlock, Druid/Warrior (×2, один «Druid PoV»), Hunter/Shadow Priest, MM Hunter/Priest, Mage/Ret Paladin, **PomPyro Mage/Rogue** (спек-вариант нашего RM — кандидат в SPEC_VARIANTS_2V2), SPriest/Rogue (Buddhist; Lilic), SPriest/UA Warlock, Priest/Warrior, Rogue/Rogue, **Rogue/Shaman** (соседствует с кандидат-ячейкой rogue+rsham от 07-06), Rogue/Warlock (+ «Rogue PoV»), Shaman/Warrior, Warlock/Warrior, Paladin/Warlock, Paladin/Warrior.

**3v3-индекс**: Druid/Mage/Rogue, Druid/Mage/Warrior, **Druid/Rogue/Warlock (RLD-POV!)**, Druid/Rogue/Warrior, **Druid/Warlock/Warrior (WLD-POV!)**, Hunter/Mage/Priest, Mage/Priest/Rogue (наш, читается), Paladin/Shaman/Warrior. Их `vs_Mag_Pri_Rog` подстраницы — enemy-POV для соответствующих rmp-драфтов (сейчас те стоят на tier-list якорях + synthesized-execution — enemy-POV план заметно поднимет качество).

## 5. Прочее по источникам
- **koroboost.com/guide/tbc-arena-guide** (17 июн 2026, свежий) — SEO-блог буст-сервиса: comp-level тиры (RM «Very High difficulty», RP «High», RMP 2400+), ничего сверх SC/WT/Icy Veins, per-matchup контента нет → **в sources не берём** (маркетинговый текст без автора-игрока).
- WebSearch conflation-пример дня: на запрос mage+rdruid vs RM сводка выдала советы про **rogue**+rdruid — очередное подтверждение правила «сводкам не верить, только страницам».
- silentshadows RM-обзор всплыл в выдаче под заголовком WT (`silentshadows.net/arena-strategies/mage-rogue-burning-crusade/`) — уже известный cite-уровень, нового нет.

## 6. Housekeeping
- Stale hypothesis-дубликатов по-прежнему **12** — ждут удаления владельцем (SCAN-REPORT 07-03 §3).
- Незакоммиченное продолжает копиться (с 07-02); сегодня добавился только этот отчёт. Ждёт ручного `git add/commit/push`.
- `docs/NEXT-SESSION-HANDOFF.md` датирован 06-23 (цифры устарели: сейчас 51 драфт / 16 гипотез, 4 незасорсенных) — обновить в интерактивной сессии.

## 7. Следующие шаги
1. **Отмашка владельца на enrichment-батчи** — очередь выросла: 07-06 §3a-3c + 07-07 §3a-3e + сегодняшние §3a-3d. Особенно ценно: зеркальная пара 3a+3b (можно кросс-ссылать наши драфты RM vs RP / RP vs RM как «их POV на нас»).
2. AJ-дочитка (3-4/ран): остаток очереди 07-07 — RM `Dru_Rog`, `Pal_War`; RP `Dru_Rog`, `Dru_Wlk`; следом — enemy-POV из §4 (приоритет: Megatf Dru_Htr; 3v3 WLD-POV и RLD-POV `vs_Mag_Pri_Rog`).
3. Решение владельца по ячейкам-кандидатам (07-07 §4: mage+spriest готов полностью; + PomPyro-спек и rogue+rsham из §4).
4. Интерактивная сессия: yt-dlp транскрипт `DLEZ7Yi4-jU` (потенциал: rm-vs-mage-rdruid / rm-vs-hunter-*).
