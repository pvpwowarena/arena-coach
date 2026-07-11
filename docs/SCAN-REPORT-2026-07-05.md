# Daily source scan — 2026-07-05

Авто-задача `arena-coach-daily-source-scan`. Браузер подключён (Browser 1, macOS).
**Итог: нетто 0 новых драфтов. Ничего не аппрувлено, ничего не смёржено. Всё зелёное.**

## Проверки (green)
- `PYTHONPATH=backend python -m arena_coach validate-kb kb/drafts/` → **49 OK**
- `PYTHONPATH=backend:bridge:ingest python -m pytest tests/` → **113 passed** (~1.1s)
- Счётчик драфтов в `tests/test_kb_loader.py` = 49 (совпадает, не трогал).

## Что смотрел сегодня
| Источник | Доступ | Результат |
|---|---|---|
| WT RM-обзор `rogue-mage-rogue-arena-strategies` | Chrome `get_page_text` ✅ | Только обзор + counter-list (Rogue/Druid, Lock/Druid, **Lock/Hpala**, Human Rogue combs, Dwarf Disc+Mage/Lock). Per-pair стратегий нет. |
| `rank1academy.com/guide/mage-rogue-matchup-tbc` (Rogue/Mage POV) | WebFetch ✅ | **Пейволл 148.95 €** — вся тактика в видео-библиотеке за оплатой. Не извлечь. |
| icy-veins `/tbc-classic/2v2-arena-composition-rankings` | WebFetch ✅ (server-rendered) | Комп-уровень strengths/weaknesses. Не per-pair, но годно как enrichment-якоря. |
| silentshadows RM-mirror | WebFetch ⚠ | Отдаёт WT nav-shell (тело только через JS) — как per-pair источник не годится. |

## 6 гипотез без источника (без изменений)
Реальный per-pair источник под НАШ состав так и не найден — промоут = выдумка, запрещён.
- **RM:** `rm-vs-hunter-hpala`, `rm-vs-hunter-rsham`, `rm-vs-mage-hpala`, `rm-vs-mage-rdruid`
- **RP:** `rp-vs-hunter-rsham`, `rp-vs-mage-hpala`

Причина: WT не имеет RM-per-matchup гайда; rank1academy за пейволлом; icy-veins/skill-capped дают только комп-тир. Эти комбо (hunter+hpala, hunter+rsham, mage+hpala, mage+rdruid под RM) не названы в тир-листах как мета → нет прозы слабости под конкретную пару. Разблокирует только: (а) mirlol per-pair страница через Twitch-sub владельца → `arena_ingest paste`, или (б) видео-транскрипт RM/RP-POV (yt-dlp в интерактивной сессии — в песочнице 403).

## Предложения по обогащению существующих драфтов (НЕ применял — на approve)
Из icy-veins 2v2 (server-rendered, цитируемо) и WT RM-обзора можно добавить комп-behavior цитаты в блоки `sources:` уже засорсенных драфтов:
- `rm/rp-vs-hunter-rdruid` — icy-veins: «Great kiting potential; Mana destruction with Viper Sting; Low damage; Difficult to recover from mistakes» (усиливает existing attrition-каркас).
- `rm/rp-vs-retpala-rsham` — icy-veins: Ret/RSham «Cleanse/Purge/Freedom/BoP + Windfury/Bloodlust burst; **vulnerable to Curse of Tongues**; very limited CC; easy to kite (Frost Shock)».
- `rm/rp-vs-warrior-hpala` — icy-veins: Arms/HPala «Cleanse+Freedom keep warrior active, double plate; vulnerable to Curse of Tongues; very limited CC».
- `rm/rp-vs-mage-priest` — icy-veins: Mage/Disc «strong CC + Mana Burn; low damage; few ways to pressure outside Mana Burn».
- `rm-vs-rogue-rdruid`, `rm-vs-warlock-rdruid`, `rm-vs-warlock-hpala`, `rm-vs-rogue-rogue` — WT RM-обзор прямо называет их counter-comps RM («Rogue/Druid, Lock/Druid, Lock/Hpala, Human Rogue combs») — цитата подтверждает difficulty.

Все — комп-уровень (не per-pair execution), поэтому только как supplementary cite к уже существующему каркасу, тегом не меняют tier. Скажи, если применять — оформлю по одному и прогоню тесты.

## Housekeeping (ждёт владельца, не трогал)
10 файлов в `kb/hypotheses/` уже засорсены как драфты, но гипотеза-версии не удалены (rm: rogue-hpala/warlock-hpala/warrior-mage/warrior-rogue; rp: hunter-hpala/mage-rdruid/rogue-hpala/warlock-hpala/warrior-mage/warrior-rogue). Дубли путают счёт. Предлагаю удалить гипотеза-версии — по твоей команде.
