# Arena Coach — Daily Source Scan Report
**Дата:** 2026-06-27  
**Задача:** `arena-coach-daily-source-scan` (автоматическая)  
**Статус:** ✅ Завершена

---

## Итог сессии

### Новые sourced-драфты: 2

| Slug | Источники | Якорь |
|---|---|---|
| `rm-vs-warrior-mage` | AOEAH TBC 2v2 tier-list (Dec 2025) + Icy Veins 2v2 ranking (Jan 2026) | warrior+mage D-tier «No dispel. No sustain. Dies to control.» |
| `rp-vs-warrior-mage` | AOEAH TBC 2v2 tier-list (Dec 2025) + Gog123456/OwnedCore (2008 TBC) | то же D-tier; Gog: RP vs warrior — «rogue locks down the warrior» |

Гипотезы `kb/hypotheses/rm-vs-warrior-mage.md` и `kb/hypotheses/rp-vs-warrior-mage.md` помечены `status: sourced-promoted`.

---

## Проверка: 9 гипотез без источника

Ниже — все оставшиеся unverified-гипотезы. Ни в одном доступном сервер-рендеренном источнике (AOEAH, Icy Veins, OwnedCore, silentshadows) они не фигурируют как именованные комп-якоря.

| Slug | Блокер |
|---|---|
| rm-vs-hunter-hpala | hunter+hpala не найден в tier-листах как отдельная запись |
| rm-vs-hunter-rsham | то же |
| rm-vs-mage-hpala | нет tier-list anchors; источник mage/hpala vs RM не найден |
| rm-vs-mage-rdruid | нет tier-list anchors |
| rm-vs-rogue-hpala | нет tier-list anchors |
| rp-vs-hunter-rsham | нет tier-list anchors |
| rp-vs-mage-hpala | нет tier-list anchors |
| rp-vs-mage-rdruid | нет tier-list anchors |
| rp-vs-rogue-hpala | нет tier-list anchors |

**Вывод:** без нового источника (стрим, форум, VOD) эти 9 не могут быть промоутированы. Не выдумывать.

---

## Обнаруженные источники этой сессии

| URL | Тип | Что дал |
|---|---|---|
| https://www.aoeah.com/news/4283--tbc-classic-anniversary-2v2-comps-tier-list | Tier-list (Dec 2025) | warrior+mage D-tier anchor для обоих новых драфтов; общие RM/RP S-tier описания |
| https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings | Tier-list (Jan 2026) | RM best-tier, strengths/weaknesses, использован в rm-vs-warrior-mage |
| https://www.ownedcore.com/forums/world-of-warcraft/world-of-warcraft-guides/161338-... | Форум-гайд TBC 2008 | Gog123456: RP vs warrior/mage тактика, использован в rp-vs-warrior-mage |
| https://silentshadows.net/arena-strategies/mage-rogue-burning-crusade/ | Обзор RM стратегий | Только counter-comp список, без пер-матчап тактики. Не использован для новых драфтов. |

**Не доступны** (client-rendered, без Chrome MCP): wowhead.com, warcrafttavern.com, mirlol.pro.  
**Мёртвый URL:** `silentshadows.net/disc-rogue-tactics-deadlycoward/` → редирект на nav-страницу.

---

## Кандидаты в slang.json

`render_slang.py --all` выявил 6 ability-slug'ов, используемых в драфтах без slang-записи:

```
ambush, deadly-throw, expose-armor, pain-suppression, rupture, will-of-the-forsaken
```

Это не баги — просто EN-имена остаются как есть в rendered-выводе. Если нужны RU-сленг-синонимы, добавь в `kb/glossary/slang.json`.

---

## Обогащение существующих драфтов (предложения)

1. **warrior-adjacent drafts (rm/rp-vs-warrior-*):** в source-блок можно добавить AOEAH D-tier ноту про конкретный состав (warrior+rdruid, warrior+rsham, warrior+hpala уже есть в AOEAH, но не процитированы). Актуально при следующем enrichment-проходе.
2. **rm-vs-* глобально:** Icy Veins comp ranking упоминает RM как best-tier со списком weaknesses — «Low healing, No spread damage». Полезная деталь для секций "Common mistakes".

Нет срочности — существующие драфты валидны. Предложения для следующей ручной сессии.

---

## Техническое

| Проверка | Результат |
|---|---|
| `validate_directory(kb/drafts/)` | ✅ ok=46, errors=[] |
| `python -m pytest tests/` | ✅ 113/113 passed |
| `render_slang.py --all` | ✅ 46 файлов, 2255 замен |
| Тест-счётчик обновлён | 44 → 46 (test_kb_loader.py:92) |

---

## Следующие шаги для владельца

1. **Approve** новые драфты если контент устраивает:
   ```
   python -m arena_ingest review approve --slug rm-vs-warrior-mage
   python -m arena_ingest review approve --slug rp-vs-warrior-mage
   ```
2. **Источники для 9 оставшихся гипотез** — нужен стрим/VOD/форум с hunter+hpala, mage+rdruid/hpala, rogue+hpala матчапами против RM/RP. Mirlol или tbcpvp.com VOD был бы идеален (client-rendered, нужен Chrome MCP или ручное копирование).
3. **slang.json** — при желании добавить `ambush`, `rupture`, `pain-suppression`, `will-of-the-forsaken` в RU-глоссарий.
