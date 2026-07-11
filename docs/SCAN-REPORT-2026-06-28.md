# Arena Coach — Daily Source Scan Report
**Дата:** 2026-06-28
**Задача:** `arena-coach-daily-source-scan` (автоматическая)
**Статус:** ✅ Завершена

---

## Итог сессии

### Новый sourced-драфт: 1

| Slug | Источник | Якорь |
|---|---|---|
| `rp-vs-mage-rdruid` | Deadlycoward in-depth DP/R guide (Warcraft Tavern), секция «DPR vs. Druid / Frost Mage» (5/10) | «Kill mage by making him run out of mana / kill druid after his trinket… Sap the mage, dispels from your priest, focus him with Mana Burns… easy to kite, your priest can dispel everything except cyclone» |

Гипотеза `kb/hypotheses/rp-vs-mage-rdruid.md` помечена `status: sourced-promoted`.
Difficulty переоценён `hard → moderate` (источник: 5/10, «pretty easy to kite»).

### 🔑 Главная находка: разблокирован Deadlycoward DP/R guide (20 матчапов)

Память `kb-source-fetchability` числила `silentshadows.net/disc-rogue-tactics-deadlycoward/` как **мёртвый URL** (WebFetch отдавал редирект на nav-страницу). Через **Chrome MCP** видно, что он **жив** и редиректит на хостинг Warcraft Tavern:

> `https://www.warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/`

Это **in-depth гайд от Deadlycoward** (Infernal Gladiator, top-10 EU DP/R season 1, 2919 рейтинг) с **20 детальными матчапами от лица DP/R**, чистый TBC 2.4.3 (WoTF, Mana Burn, Mass Dispel, Spellsteal, Cyclone, Viper Sting — без WotLK-механик). Это самый ценный RP-источник на сегодня: он даёт **прямую matchup-POV тактику** для нашего RP, а не только comp-level tier-якорь.

---

## Что засорсилось и что нет (9 гипотез)

| Slug | Итог | Причина |
|---|---|---|
| **rp-vs-mage-rdruid** | ✅ **засорсен** | Deadlycoward «DPR vs. Druid / Frost Mage» (5/10) — прямой матчап-POV |
| rp-vs-hunter-rsham | ⬜ остаётся гипотезой | Deadlycoward покрывает Druid/Hunter (10/10), но **не** Rsham/Hunter; в tier-листах hunter+rsham не назван. Есть только архетип-паттерн «hunter+healer = mana drain» — для sourced недостаточно (у rsham иные механики: тоталы/grounding/NS) |
| rp-vs-mage-hpala | ⬜ остаётся гипотезой | в Deadlycoward-гайде нет Hpala/Mage (есть DPriest/Mage и Druid/Mage); в tier-листах не назван |
| rp-vs-rogue-hpala | ⬜ остаётся гипотезой | нет Rogue/Hpala ни в гайде, ни в tier-листах |
| rm-vs-hunter-hpala | ⬜ остаётся гипотезой | RM-POV матчап-гайда не существует (на WT только обзорная RM-страница Sbkzor, без 20 матчапов); в RM counter-comps и tier-листе не назван |
| rm-vs-hunter-rsham | ⬜ остаётся гипотезой | то же |
| rm-vs-mage-hpala | ⬜ остаётся гипотезой | то же |
| rm-vs-mage-rdruid | ⬜ остаётся гипотезой | Deadlycoward-гайд — это **DP/R-POV** (план = OOM мага манабёрном + дисп), для RM не инвертируется: у RM нет ни манабёрна, ни диспа, тактика принципиально иная (shatter-burst в CC-окне). Нужен RM-POV источник |
| rm-vs-rogue-hpala | ⬜ остаётся гипотезой | RM-POV источника нет |

**Вывод:** 5 RM-гипотез структурно заблокированы — на WT нет RM-POV матчап-гайда (в отличие от DP/R). Для них реальный источник = rogue-POV RM-видео (yt-dlp на сабы) или форумный POV-пост по конкретной паре. 3 RP-гипотезы (hunter+rsham, mage+hpala, rogue+hpala) не покрыты ни одним из 20 матчапов Deadlycoward и не названы в tier-листах.

---

## Обнаруженные/проверенные источники этой сессии

| URL | Тип | Что дал |
|---|---|---|
| warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/ | Author-guide (Deadlycoward, 20 матчапов) | **Прямой источник для rp-vs-mage-rdruid** + enrichment-материал для ~14 RP-драфтов (см. ниже) |
| warcrafttavern.com/tbc/guides/2v2-arena-tier-list/ | Tier-list | Полный текст добыт (Chrome MCP). Подтверждено: ни один из 5 enemy-комбо моих гипотез (hunter+hpala, hunter+rsham, mage+hpala, mage+rdruid, rogue+hpala) **не** тирован отдельно → все «C-tier or below» |
| warcrafttavern.com/tbc/guides/rogue-mage-rogue-arena-strategies/ | RM overview (Sbkzor) | RM Counter Comps: Rogue/Druid, Lock/Druid, Lock/Hpala, Human Rogue combs, Dwarf Disc+Mage/Warlock. Матчап-POV (20 матчапов, как у DP/R) **отсутствует** |
| warcrafttavern.com/tbc/guides/rogue-discipline-priest-rogue-arena-strategies/ | DPR overview | DPR Counter Comps: Hunter/Druid, Hunter/Priest, Hunter/HPaladin (mana drain). Ссылка на in-depth Deadlycoward-гайд |
| warcrafttavern.com/tbc/guides/rogue-arena-strategies/ | Rogue hub | Список rogue-комбо с in-depth гайдами: DP/R, Druid/R, FrostMage/R, SP/R, Lock/R, Feral/R, R/R |

**Инструмент:** ключевой рычаг сессии — **Chrome MCP** (`navigate` + `get_page_text`). WebFetch на этих URL отдаёт только nav-шелл (client-rendered), поэтому скан 2026-06-27 их «не видел». Browser 1 (macOS) был подключён.

---

## Обогащение существующих драфтов (предложения — НЕ применено)

Deadlycoward-гайд (DP/R POV = наш RP против их комбо) даёт прямую matchup-POV тактику для **14 существующих RP-драфтов**. Многие из них сейчас `community-sourced`/`synthesized-execution` (tier-якорь) — этот гайд **апгрейдит их до named-author матчап-источника**. Предлагаю при следующем ручном проходе добавить URL в `sources:` и вплести нюансы:

| Draft | Матчап в гайде (сложность) | Ключевой нюанс для добавления |
|---|---|---|
| rp-vs-rogue-priest | Mirror DP/R (5/10) | Focus rogue; на priest — если rogue под контролем/priest диспеллабелен. Беречься enemy Mass Dispel (втягивает в комбат → sap+dispel). CoS под Greater Heal |
| rp-vs-rogue-rdruid | Druid/Rogue (9/10) | Kill rogue на 2-м Blind; сидеть у пиллара, fear на rogue, restealth→новый опенер; стоять **далеко** от своего прийста (sap+shout) |
| rp-vs-hunter-rdruid | Druid/Hunter (10/10) | Sap хантера на исходе Flare; kill pet + mana-burn хантера; Frost Trap RNG-roots + Viper = «I mostly lose to every decent HD» (худший матчап DP/R) |
| rp-vs-warlock-rdruid | Druid/SL Lock (7/10) | Sap lock + полный дисп, стик на lock; kill pet когда друид пьёт → нет Devour Magic, фиры стикаются |
| rp-vs-warrior-rdruid | Druid/Warrior (7/10) | Sap warrior, fake Berserker Rage → re-sap; CS-KS друид пока прийст 1v1 воина для free Fear; либо train воина с bleeds+Step |
| rp-vs-warrior-hpala | Hpala/Warrior (7/10) | Открывать **паладина** CS, ждать чарж воина перед KS; kill warr 90%; чейн KS pala/Fear/Sap/Blind/Step-Kick/Vanish CS/KS. FAQ: НЕ sap pala+open warr (воин кайтит бурст) |
| rp-vs-warrior-rsham | Rsham/Warrior (5/10) | Как Hpala/Warr; train воина стан/кик, fear шамана |
| rp-vs-mage-priest | DPriest/Mage (7/10) | **Никогда не агриться**; кайт мага у пиллара + Mana Burns, restealth, OOM. «Full aggressive → no way you win» |
| rp-vs-warlock-priest | DPriest/SL Lock (7/10) | Kill priest (не если dwarf) либо lock под давлением; vs Disc/Lock бегать **длинными дистанциями**, не у пилларов (нет poison-диспа) |
| rp-vs-retpala-rsham | Rsham/Ret (7/10) | Sap pala, дисп, burns; KS pala только когда прийст застанен или pala даёт Freedom (прийст диспелит); OOM pala |
| rp-vs-rogue-mage | FrostMage/Rogue (7/10) | Избегать sap (mage Spellsteal’ит); kill rogue в основном; решение по тринкету на KS |
| rp-vs-rogue-spriest | SPriest/Rogue (5/10) | Rush SP **без** sap, kill подальше от своего прийста; «DP/R counters SP/R» — подтверждает текущий sourced-каркас |
| rp-vs-rogue-rogue | Rogue/Rogue (7/10) | Прийст спиной к стене (no garrote), ты — отдельно (no sap); burst одного rogue bleeds+Vanish-CS-Evisc |
| rp-vs-warlock-rogue | SL Lock/Rogue (7/10) | Rush lock со Sprint, избегать sap; **не** тринкетить первый KS; kill lock хардом |

Не применял правки автоматически (правило: маленькие проверяемые инкременты + approve владельцем). Готов вплести по команде.

---

## Кандидаты в slang.json (без изменений с 2026-06-27)

`render_slang.py --all` снова показал 6 ability-slug без slang-записи (остаются EN-именем, не баг):
`ambush, deadly-throw, expose-armor, pain-suppression, rupture, will-of-the-forsaken`.
Новый драфт использует `pain-suppression` и `will-of-the-forsaken` — уже в этом списке.

---

## Техническое

| Проверка | Результат |
|---|---|
| `python -m arena_coach validate-kb kb/drafts/` | ✅ 47 документов прошли валидацию |
| `python -m pytest tests/` | ✅ 113 passed |
| `python -m ruff check tests/test_kb_loader.py` | ✅ clean |
| `python tools/render_slang.py --all` | ✅ 47 файлов, 2327 замен |
| Тест-счётчик обновлён | 46 → 47 (`tests/test_kb_loader.py:94`) |

---

## Следующие шаги для владельца

1. **Approve** новый драфт, если устраивает (это единственный новый канон-кандидат сессии):
   ```
   python -m arena_ingest review approve --slug rp-vs-mage-rdruid
   ```
2. **Enrichment-проход по 14 RP-драфтам** из таблицы выше — Deadlycoward-гайд апгрейдит их с tier-якоря до named-author матчап-источника. Скажи «вплети enrichment» — подготовлю правки батчем на ревью.
3. **5 RM-гипотез** (hunter+hpala/rsham, mage+hpala/rdruid, rogue+hpala) ждут **RM-POV источника**: rogue-POV RM-видео (yt-dlp на сабы) или форумный POV. На WT RM-матчап-гайда нет.
4. **3 RP-гипотезы** (hunter+rsham, mage+hpala, rogue+hpala) — не покрыты 20 матчапами Deadlycoward; нужен отдельный источник.
5. Память `kb-source-fetchability` обновлена: deadlycoward-URL **жив** через Chrome MCP (редирект на WT).
