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

## Opener

_Провенанс: первый 3v3-драфт (фаза только заведена). Источники — tier-листы/обзоры (Skill Capped, Warcraft Tavern, koroboost), которые описывают динамику «WLD — единственная стабильная контра RMP». Наша RMP-сторона (защита прийста, сетап, kill-выбор) синтезирована из механик TBC 2.4.3. Теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`bracket-3v3-new` — нужна верификация топ-RMP перед approve._

Очень тяжёлый матчап: WLD — задокументированная главная контра RMP. Их план (источник): warlock фирит прийста, warrior вешает MS (-50% хил) на прийста, druid циклонит любого, кто пытается убить warrior'а. Они ломают наш sustain через прийста.

Наш план (синтез) — игра строится вокруг **защиты прийста** и чистого CC-сетапа:
- Рог снимает warrior'а с прийста: [[ability:gouge]] / [[ability:kidney-shot]] / [[ability:blind]]; маг [[ability:nova]]-кайтит warrior'а, [[ability:counterspell]] держит на druid heal / warlock fear.
- Сетап на kill: [[ability:sap]] druid → [[ability:sheep]] warlock (или наоборот) → [[ability:blind]]/[[ability:cheap-shot]] на kill target. Burst (shatter + [[ability:kidney-shot]]) — в окно, когда druid под CC и не может [[ability:cyclone]] протектить.
- Kill target — warlock (убираем фиры по прийсту и одного DPS) или druid (убираем cyclone-protect). Прийст играет от LoS, dispel'ит, держит [[ability:pain-suppression]] на себе под MS+burst.

## Alternative opener

Если WLD открыли на прийсте (их стандарт): рог моментально на warrior'е ([[ability:cheap-shot]]/[[ability:kidney-shot]]), маг [[ability:nova]] + [[ability:sheep]] warlock'а чтобы оборвать fear-цепочку, прийст [[ability:pain-suppression]] + уход за LoS. Снять давление с прийста — приоритет №1, иначе MS+fear+cyclone не дадут лечиться.

## If enemy trinkets

Druid трикетит [[ability:sheep]]/[[ability:kidney-shot]] и держит NS-[[ability:cyclone]] на наш kill-attempt; warlock трикетит [[ability:sheep]]/[[ability:fear]]-ловлю; warrior трикетит [[ability:kidney-shot]]. Не вкладывай burst, пока druid с трикетом+NS может оборвать kill циклоном — сначала свяжи druid'а ([[ability:sheep]]/[[ability:sap]]/[[ability:counterspell]] на его cast).

## Common mistakes

- Бурстить kill target при свободном druid'е — [[ability:cyclone]]/NS оборвут добив.
- Бросить прийста под warrior+warlock — MS+fear убивают наш sustain; рог обязан peel'ить warrior'а.
- Тратить [[ability:counterspell]] не на тот каст — держи на druid heal / warlock fear по прийсту.
- Идти в долгий размен: дай WLD стабилизироваться — их pressure+defensives отыграют. Нужен чистый CC-сетап и быстрый kill-window.

## Key cooldowns to track

- enemy: druid — [[ability:cyclone]], Nature's Swiftness, trinket, innervate, barkskin; warlock — fear + [[ability:death-coil]], Spell Lock (felhunter), healthstone, trinket; warrior — MS, intercept, spell-reflect, trinket.
- ours: [[ability:sap]], [[ability:sheep]], [[ability:blind]], [[ability:kidney-shot]], [[ability:counterspell]], [[ability:nova]], [[ability:vanish]], [[ability:ice-block]]; priest — [[ability:pain-suppression]], [[ability:mana-burn]], dispel, [[ability:fear]], trinket.
