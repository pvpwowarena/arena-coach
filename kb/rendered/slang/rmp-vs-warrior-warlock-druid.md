---
slug: rmp-vs-warrior-warlock-druid
schema_version: 1
expansion: tbc
composition: rogue+mage+priest
vs: warrior+warlock+druid
bracket: 3v3
difficulty: very-hard
kill_target:
  primary: warlock
  fallback: druid
maps_notes: {}
sources:
- type: web
  url: "https://www.skill-capped.com/wowarticles/tbc/tier-lists/tbc-3v3/"
  title: "TBC Classic 3v3 Arena Tier List (Skill Capped) — WLD как контра RMP"
  retrieved: '2026-06-22'
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/3v3-arena-tier-list/"
  title: "Best 3v3 Arena Comps: Tier List (Warcraft Tavern)"
  retrieved: '2026-06-22'
- type: web
  url: "https://koroboost.com/guide/tbc-arena-guide"
  title: "TBC Arena Guide — RMP vs WLD strategy"
  retrieved: '2026-06-22'
- type: youtube
  url: "https://www.youtube.com/watch?v=XYH4C0CWtRc"
  title: "RMP 3v3 TBC Arena w/ Live Comms (Rogue Mage Priest)"
last_reviewed: '2026-06-22'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, bracket-3v3-new]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rmp-vs-warrior-warlock-druid.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: первый 3v3-драфт (фаза только заведена). Источники — tier-листы/обзоры (Skill Capped, Warcraft Tavern, koroboost), которые описывают динамику «WLD — единственная стабильная контра RMP». Наша RMP-сторона (защита прийста, сетап, kill-выбор) синтезирована из механик TBC 2.4.3. Теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`bracket-3v3-new` — нужна верификация топ-RMP перед approve._

Очень тяжёлый матчап: WLD — задокументированная главная контра RMP. Их план (источник): лок фирит прийста, вар вешает MS (-50% хил) на прийста, друид циклонит любого, кто пытается убить вар'а. Они ломают наш sustain через прийста.

Наш план (синтез) — игра строится вокруг **защиты прийста** и чистого CC-сетапа:
- Рог снимает вар'а с прийста: Gouge / кидни / блайнд; маг нова-кайтит вар'а, кс держит на друид heal / лок фир.
- Сетап на kill: сап друид → шип лок (или наоборот) → блайнд/чип на фокус. Burst (шаттер + кидни) — в окно, когда друид под CC и не может циклон протектить.
- фокус — лок (убираем фиры по прийсту и одного дд) или друид (убираем циклон-protect). Прийст играет от лос, dispel'ит, держит Pain Suppression на себе под MS+burst.

## Alternative опенер

Если WLD открыли на прийсте (их стандарт): рог моментально на вар'е (чип/кидни), маг нова + шип лок'а чтобы оборвать фир-цепочку, прийст Pain Suppression + уход за лос. Снять давление с прийста — приоритет №1, иначе MS+фир+циклон не дадут лечиться.

## If enemy trinkets

друид тринкетит шип/кидни и держит NS-циклон на наш kill-attempt; лок тринкетит шип/фир-ловлю; вар тринкетит кидни. Не вкладывай burst, пока друид с тринкетом+NS может оборвать kill циклоном — сначала свяжи друид'а (шип/сап/кс на его cast).

## Common mistakes

- Бурстить фокус при свободном друид'е — циклон/NS оборвут добив.
- Бросить прийста под вар+лок — MS+фир убивают наш sustain; рог обязан пил'ить вар'а.
- Тратить кс не на тот каст — держи на друид heal / лок фир по прийсту.
- Идти в долгий размен: дай WLD стабилизироваться — их pressure+defensives отыграют. Нужен чистый CC-сетап и быстрый kill-window.

## Key cooldowns to track

- enemy: друид — циклон, Nature's Swiftness, тринка, innervate, barkskin; лок — фир + Death Coil, Spell Lock (felhunter), healthstone, тринка; вар — MS, intercept, spell-reflect, тринка.
- ours: сап, шип, блайнд, кидни, кс, нова, ваниш, блок; прист — Pain Suppression, Mana Burn, dispel, фир, тринка.
