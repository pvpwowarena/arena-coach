# Source-scan report — 2026-07-06 (авто-задача)

**Итог:** нетто **0 новых sourced-драфтов** (бар для 6 гипотез по-прежнему не выполнен), но **главная находка за все сканы**: разблокирован архив **Arena Junkies** (Wayback Machine, снапшоты июля 2008 — оригинальный TBC S3/S4). Впервые есть **RM-POV и RMP-POV per-matchup гайды** — структурный блокер, стоявший с 06-28 («RM-POV гайда не существует»), снят для enrichment-целей. Ничего не аппрувлено, ничего не смёржено, KB не менялась.

**Проверки (green):** `validate-kb kb/drafts/` = **49 OK** · `pytest tests/` = **113 passed** · счётчик 49 не менялся. Браузер подключён (Browser 1, macOS).

---

## 1. Находка: Arena Junkies через web.archive.org (Chrome MCP)

Мёртвый сайт arenajunkies.com (закрыт ~2018, в 2013+ уже другой движок) имеет **полностью рабочие снапшоты старой strategy-вики за июль 2008** — это оригинальный TBC, ровно наша версия механик. WebFetch до них не дотягивается (provenance-ограничение) — читать через **Chrome MCP** `navigate` + `get_page_text`.

Индекс всех comp-страниц: `https://web.archive.org/web/20080720052414/http://www.arenajunkies.com/strategy`

Три гайда под НАШИ составы:

| Гайд | Автор (кред) | Матчап-подстраниц | URL-паттерн (подставлять к `https://web.archive.org/web/20080720052414/`) |
|---|---|---|---|
| **Mage/Rogue 2v2** (наш RM) | Icycake, US-Nightfall | **14** | `http://www.arenajunkies.com/strategy/2v2/Mage_Rogue_vs_<Xxx_Yyy>/` |
| **Priest/Rogue 2v2** (наш RP) | Mixster, US-Arthas/Ruin, **2404 (93-27) S2** | **16** | `http://www.arenajunkies.com/strategy/2v2/Pri_Rog/` (+ `Pri_Rog_2` — Faction-вариант, не читан) |
| **Mage/Priest/Rogue 3v3** (наш RMP) | Dvineowns + Factionz, US-Stormstrike (BG9 top-12) | **13** | `http://www.arenajunkies.com/strategy/3v3/Mag_Pri_Rog_vs_<Xxx_Yyy_Zzz>/` |

Сокращения в URL: Dru, Htr, Mag, Pal, Pri, SPri, Rog, Shm, Wlk, War (пары/тройки в алфавитном порядке, напр. `Mage_Rogue_vs_Shm_War`, `Mag_Pri_Rog_vs_Dru_Wlk_War`).

⚠ Wayback редиректит на ближайший снапшот по каждому URL — проверять, что попал в 2008, а не в 2013 (там вики мертва).

## 2. Гипотезы: 6 остаются без источника (проверено и в AJ)

Целевые пары в AJ-архиве **не разбираются** — ни подстраницами, ни в комментах:

| Slug | Проверка в AJ |
|---|---|
| rm-vs-hunter-hpala, rp-vs-hunter-hpala* | Пары hunter+holy-pala в RM/RP-гайдах нет (*RP-версия уже засорсена ранее; см. §3 — комменты дают авторский план) |
| rm-vs-hunter-rsham, rp-vs-hunter-rsham | `BMHtr_Shm` — это hunter + **ele**-шаман («two ranged DPS», билды 40/0/21) → для resto-пары НЕ источник. Использовать = source-confusion |
| rm-vs-mage-hpala, rp-vs-mage-hpala | `Mag_RPal` — mage + **ret**-paladin (другая пара). Mage+holy-pala нигде не разобран |
| rm-vs-mage-rdruid | `Moon_Mag` — **moonkin**+mage, не resto. RM-POV по mage+rdruid нет и в 14 матчапах Icycake |

Промоут = выдумка → не делал. Блокер прежний: mirlol paywall (Twitch-sub владельца) или RM/RP-POV VOD в интерактивной сессии.

## 3. Enrichment-предложения (НЕ применял — жду отмашки)

### 3a. RMP 3v3 — самое ценное (драфты сейчас на tier-якорях + synthesized-execution)

Прочитаны 4 **посвящённые** секции; парафразы планов (Factionz/Dvineowns):

- **rmp-vs-warrior-warlock-druid (WLD):** цель — варлок; прист ждёт на маунте выхода друида → фир (без трикета друид выпадает из хила); спам-диспел лока; шип воина; CS друиду при выходе из формы; фейк-касты против spell lock и Feral Charge; **прист хилит/щитует водного элементаля** (килл зависит от него); после NS друид не должен отхилить лока. NB: автор считает матчап «relatively easy» (мета 2008) — противоречит koroboost-2026 «WLD стабильно бьёт RMP»; предлагаю добавить как второй источник с пометкой о расхождении эпох, difficulty не менять. Коммент Raeko: сплит-дпс вариант (маг→вар, рог→лок) → друид тонет в хиле, открыт манабёрнам.
- **rmp-vs-rogue-mage-priest (mirror):** kill mage; шип на ИХ приста (не тратить на рога — полный шип по рогу почти нереален); свап на рога когда его vanish/cloak/trinket + прист на DR; ранний CS в мага, второй CS беречь на приста; **приоритет №1 приста — Mass Dispel на Ice Block** (пример: PS своему магу → MD их блока); альт-план vs Mutilate/41-combat рог: убивать рога, их мага фир/поли/CS — не дать Frostbolt.
- **rmp-vs-rogue-warlock-priest (RLP):** цель — ИХ прист («не сможет диспелить, пока кайтит и хилится»); шип дпс по DR; Winter's Chill стакать; **CS — варлоку, на приста CS не нужен**; фир рога каждый КД; блайнд по трикету. Коммент Flidrip: изоляционный вариант (оба в лока → рог тратит КД → после PS свап в их рога).
- **rmp-vs-warrior-mage-priest (WMP):** «зерг» приста, CC воина, блайнд воина по трикету, CS магу. Совпадает с нашим драфтом (kill priest) — добавить как named-author подтверждение.
- **rmp-vs-rogue-warlock-druid (RLD):** подстраницы нет, но в комментах главной RMP-страницы два развёрнутых плана: Exin (рог давит лока; маг CS циклоны; фиры+шипы на их рога — «выключить рога» = главное; потом жечь друида) и Cydial (консервативно; старт в лока, ice lance друиду + rank-1 frostbolt чтобы Winter's Chill защищал фир от диспела; рог → **пет**; килл пета форсит Fel Domination → CS посреди призыва). Community-tier (не автор гайда) — добавить как secondary source.
- **rmp-vs-hunter-priest-druid (HPD):** комментные планы Jaegarn (блайнд друида на выходе → трикет → фир; шип приста, бурст хантера; беречь DR шипа; iceblock от Viper Sting) и Brohan (сап хантера на старте, маг+рог в приста, поли хантера; на 50% приста — фир-бомба в друида + шаттер). Community-tier.

### 3b. RM 2v2 — первый RM-POV источник (снят блокер 06-28)

Матчапы Icycake ↔ наши драфты: Dru_Htr→`rm-vs-hunter-rdruid`, Dru_Rog→`rm-vs-rogue-rdruid`, Dru_Wlk→`rm-vs-warlock-rdruid`, Dru_War→`rm-vs-warrior-rdruid`, Mag_Rog→`rm-vs-rogue-mage`, Pal_Wlk→`rm-vs-warlock-hpala`(спек палы проверить при чтении), Pal_War→`rm-vs-warrior-hpala`, Pri_Rog→`rm-vs-rogue-priest`, SPri_Rog→`rm-vs-rogue-spriest`, Pri_Wlk→`rm-vs-warlock-priest`, Rog_Wlk→`rm-vs-warlock-rogue`, Shm_War→`rm-vs-warrior-rsham` = **12 драфтов**. Подстраницы в этом ране НЕ читались (бюджет) — дочитывать по 3-4 за следующие раны.

Уже добытое из комментов RM-страницы (community-tier, для `rm-vs-warlock-rsham` — пары нет в 14 подстраницах, а в комментах два плана): Grimgore (рог стан-лочит лока + 5-pt expose armor; маг шипит/CS шамана; по трикету шамана — sprint+blind, vanish-sap на 6-й сек блайнда) и Nadjya (детально: лок = CC-таргет, оба /focus лок; рог hard-станлок шамана CS→KS→vanish garrote; **mind numbing третьим ядом обязателен** — свап оружия в гоудж; NS-хил после трикета возвращает только ~50%; кто-то один сторожит фир лока). Также Seabreeze про ret+WF-шамана (→`rm-vs-retpala-rsham`): цель шаман; маг почти весь бой за пилларом, диспелит BoF; BoP диспелится, bubble нет; ловить жадный хил рет-палы = CS = win.

### 3c. RP 2v2 — второй named-author источник (к Deadlycoward)

16 подстраниц Mixster ↔ ~13 наших RP-драфтов (mirror, rogue-rdruid, warlock-rdruid, warrior-rdruid, rogue-mage, warlock-hpala/Pal_Wlk, warrior-hpala/Pal_War, rogue-priest, rogue-spriest, warlock-priest, rogue-rogue, warlock-rogue, warrior-rsham/Shm_War). Не читались — дочитка следующими ранами.

Из комментов главной (автор Mixster/Mickster лично):
- **`rp-vs-hunter-hpala` (уже sourced):** прямой авторский план на вопрос про MarksHunter/HolyPala — **сначала выжечь ману хантера**, потом дрейн палы; диспелить Freedom с хантера (кайт рога через трапы); агрессия+фир на палу; **килл пета ≈ game over** (держать хантера ООМ, чтобы не воскресил); диспел трапов, пить. Сильно конкретизирует текущий tier-якорь WT; предлагаю вплести + сверить kill-приоритет драфта (у нас vs у автора).
- **`rp-vs-warlock-rsham`:** рог 90% времени на локе (wounding×5 + mind numbing); прист «totem hump» + фир шамана когда tremor снят; тайминг фира под конец CoT; джук первого silence; после ООМ шамана — fear/vanish-sap/blind и бурст лока.
- General-tips: два офф-хенда для быстрого свапа ядов (mind numbing vs double-DPS); PI под манабёрны; чейн blind→vanish→sap→fear/MC.

### 3d. Новые ячейки-кандидаты (решение владельца, не трогал)

В комментах Mixster есть авторские планы против пар, которых нет в `compositions.json`: **mage+resto-shaman** (манабёрн мага в ноль; диспел ice shield; не дать evocate) и **rogue+resto-shaman** (прист выживает от рога → манабёрны шамана; water shield кормит шамана маной от ударов — сбивать диспелом). Плюс AJ-страницы недостающих пар: `Htr_Pri` (hunter+priest, RM-матчап есть), `SPri_Wlk`, `Pri_War`, `Rog_Shm`, `Shm_Wlk`. Если добавлять ячейки — источники уже готовы.

## 4. Housekeeping (без изменений)

10 stale hypothesis-дубликатов (см. SCAN-REPORT 07-03 §3) ждут удаления владельцем. Незакоммиченные изменения нескольких сессий в рабочей копии — ждут ручного `git add/commit/push` (замечание 07-02 в силе).

## 5. Следующие шаги

1. **Отмашка на enrichment-батчи** §3a (RMP — приоритет: там источники были самые тонкие) → §3b/§3c по мере дочитки подстраниц.
2. Следующие авто-раны: дочитывать AJ-подстраницы по 3-4 за ран (URL-паттерны в §1), начиная с Pal_Wlk (проверка спека палы), Shm_War (RM), и RP: Pal_War, Dru_Htr.
3. Прежние пути для 6 гипотез в силе: mirlol Twitch-sub → `arena_ingest paste`; RM/RP-POV VOD через yt-dlp в интерактивной сессии.
4. Policy-вопрос про class-handling synthesis (5-й ран подряд) — всё ещё ждёт решения владельца.
