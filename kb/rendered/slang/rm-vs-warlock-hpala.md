---
slug: rm-vs-warlock-hpala
schema_version: 1
expansion: tbc
composition: rogue+mage
vs: warlock+holy-paladin
bracket: 2v2
difficulty: very-hard
kill_target:
  primary: warlock
  fallback: paladin
maps_notes: {}
sources:
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/2v2-arena-tier-list/"
  title: "Best 2v2 Arena Comps: Tier List & Rankings (Warcraft Tavern) — Warlock/Holy Paladin = B-tier: «If the enemy can't keep the Paladin from healing, you will win fights. It just takes a while. A long while.» — комп выигрывает на истощении, win-con против него = не дать паладину спокойно хилить"
  retrieved: '2026-06-25'
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-mage-rogue-arena-strategies/"
  title: "Mage/Rogue — TBC 2v2 Arena Strategies (Warcraft Tavern) — «Lock / Hpala» прямо указан в списке RM Counter Comps; RM = «best double DPS» с «insane burst», но «suffers vs locks» и «cannot be considered Tier 1»"
  retrieved: '2026-06-25'
last_reviewed: '2026-06-25'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rm-vs-warlock-hpala.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: матчап-якоря — (1) tier-лист 2v2 Warcraft Tavern: лок/Holy пал = B-tier, «if the enemy can't keep the пал from healing, you will win fights — it just takes a long while» (комп заточен под истощение); (2) RM-strategies Warcraft Tavern: «Lock / Hpala» прямо в списке RM Counter Comps, RM «suffers vs locks», не Tier-1. Пошаговое исполнение синтезировано из механик TBC 2.4.3. Теги `community-sourced`/`needs-top-source`/`synthesized-execution` — нужна верификация топ-RM перед approve._

Ключ матчапа (источник: tier-лист WT) — SL/SL лок + holy пал это один из самых танковых, mana-heavy составов, заточенный под **долгую игру**: comp выигрывает «на истощении, если не помешать паладину хилить». Для RM это структурно тяжело (WT прямо относит Lock/Hpala к контр-комбо RM): у RM нет манабёрна, чтобы выжать паладина по мане, а шип на любой цели снимается cleanse'ом. Pala даёт bubble / freedom / cleanse / подж / BoP; лок — UA, фир + Death Coil, healthstone, soul link, felhunter Spell Lock.

Поэтому RM играет **не от контроля по хилеру, а от бурст-окон**: рог+маг на варлоке, маг кс держит на heal паладина, рог кидни/блайнд. Burst (шаттер нова → ice lance/frostbolt + кидни) на варлоке в окно, когда у паладина нет freedom/cleanse/bubble. Цель — варлок: убрав его, остаёшься 2v1 на паладина, который сам не убьёт.

## Alternative опенер

Если открыли на тебе: лок фир + felhunter Spell Lock на маге, подж от паладина. блок под burst, рог чип/кидни разрывает сетап. Пережил — назад к давлению на варлоке.

## If enemy trinkets

пал тринкетит шип/подж; лок тринкетит кидни/шип. Держи кс на heal-школу после тринкета паладина; не вкладывай burst, пока доступны bubble/freedom.

## Common mistakes

- Бурстить в bubble/freedom/cleanse-окне.
- Тянуть игру — источник прямо говорит, что комп сильнее в long game; без манабёрна RM не выжимает паладина по мане, ставка только на бурст в окне.
- Кидать шип по хилеру (cleanse снимет) вместо бейта КД.

## Key cooldowns to track

- enemy: пал — bubble, freedom, cleanse, подж, BoP, мана-пул, тринка; лок — UA, фир + Death Coil, Spell Lock (felhunter), healthstone, тринка.
- ours: кс, шип, нова, блайнд, кидни, ваниш, блок, тринка.
