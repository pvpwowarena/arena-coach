---
slug: rl-vs-hunter-resto-druid
schema_version: 1
expansion: tbc
composition: rogue+warlock
vs: hunter+resto-druid
bracket: 2v2
difficulty: moderate
kill_target:
  primary: hunter
  fallback: druid
maps_notes: {}
sources:
- type: web
  url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings"
  title: "2v2 Arena Composition Rankings (Icy Veins) — Hunter/Resto Druid: «Great kiting potential; Mana destruction with Viper Sting», weaknesses «Low damage; Difficult to recover from mistakes»"
  retrieved: '2026-07-24'
- type: web
  url: "https://www.wowhead.com/tbc/guide/warlock-dps-pvp-arena-guide-burning-crusade-classic-wow"
  title: "Warlock DPS Arena Guide (Wowhead) — Rogue/Warlock premier pairing: keep one feared/blinded/sapped, burst the other while stun-locked"
  retrieved: '2026-07-24'
last_reviewed: '2026-07-24'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, new-comp-rl]
---

## Opener

_Провенанс: состав **RL (Rogue / Warlock 2v2, SL/SL)**. Sourced-каркас: Icy Veins по Hunter/RDruid — «Great kiting potential; Mana destruction with Viper Sting», слабости «Low damage; Difficult to recover from mistakes»; наша сторона (SL/SL Warlock/Rogue) — сильный урон + много interrupts/CC, «Low healing». Per-matchup исполнение синтезировано из механик TBC 2.4.3. Теги `synthesized-execution`/`needs-top-source` — нужна верификация топ-RL._

Главная угроза — не их урон (он «low»), а **[[ability:viper-sting]] по варлоку**: наш sustain-мотор SL/SL держится на мане (фиры, [[ability:drain-life]], [[ability:seduction]]). Осушат ману — развалимся. Второй фактор — кайт: охотник разрывает дистанцию, друид в ToL перекидывает HoT'ы.

Килл-таргет — **охотник** (источник Viper + урона, и его тяжелее рефрешить, чем друида-кайтера):

- Старт: [[ability:sap]] охотника, открываемся всей связкой — рог [[ability:cheap-shot]] → [[ability:kidney-shot]], варлок [[ability:curse-of-tongues]] на друида (режет инстант-хилы/[[ability:cyclone]]) и бёрст в стан-окно.
- Варлок [[ability:fear]]/[[ability:seduction]] держит **друида** вне ToL — без него HoT-цепь рвётся (их слабость «difficult to recover from mistakes»).
- Как только слетит [[ability:viper-sting]] — рефрешь ману Life Tap'ом под [[ability:soul-link]], не давай варлоку уйти в OOM.

## Alternative opener

Если охотник открывает с [[ability:scatter-shot]] + trap на рога — не тратим на них trinket, варлок [[ability:spell-lock]]'ает друида и [[ability:fear]]'ит охотника из trap-зоны. Против кайта прижимай охотника через рог-[[ability:step]] ([[ability:shadowstep]]) и [[ability:deadly-throw]] на interrupt, варлок [[ability:curse-of-tongues]] замедляет его Aimed/Steady.

## If enemy trinkets

- Охотник тринкетит [[ability:kidney-shot]] и уходит в feign/trap-резет — переведи фир-цепь на друида и не тунелль в feign, жди чистое окно на охотника.
- Друид тринкетит [[ability:fear]] и льёт HoT'ы под [[ability:barkskin]] — продли [[ability:curse-of-tongues]], [[ability:faerie-fire]] с его стороны ломает твой restealth (планируй [[ability:vanish]]-резеты заранее).

## Common mistakes

- Дать [[ability:viper-sting]] осушить варлока — без маны RL мёртв; рефрешь Life Tap'ом, стой за pillar от повторных Viper.
- Тунеллить друида в ToL под HoT'ы — он перекидает; правильно **фир-лок друида + урон в охотника**.
- Гнаться за кайтящим охотником по открытому полю — теряешь темп; связывай через [[ability:seduction]] друида и прижимай охотника [[ability:shadowstep]].
- Забыть про [[ability:faerie-fire]] — под ней рог не уходит в стелс, [[ability:vanish]]-резет впустую.

## Key cooldowns to track

- enemy: hunter — [[ability:viper-sting]], [[ability:scatter-shot]], trap, feign, Deterrence, trinket; druid — [[ability:barkskin]], [[ability:natures-swiftness]], [[ability:cyclone]], [[ability:faerie-fire]], [[ability:travel-form]], trinket.
- ours: rogue — [[ability:blind]], [[ability:vanish]], [[ability:preparation]], [[ability:cloak-of-shadows]], [[ability:shadowstep]], [[ability:kidney-shot]], [[ability:deadly-throw]]; warlock — [[ability:fear]], [[ability:death-coil]], [[ability:seduction]], [[ability:spell-lock]], [[ability:curse-of-tongues]], [[ability:soul-link]], [[ability:drain-life]], trinket.
