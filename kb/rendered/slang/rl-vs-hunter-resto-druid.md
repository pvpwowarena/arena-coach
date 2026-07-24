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

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rl-vs-hunter-resto-druid.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: состав **RL (рога / лок 2v2, SL/SL)**. Sourced-каркас: Icy Veins по хант/RDruid — «Great kiting potential; Mana destruction with Viper Sting», слабости «Low damage; Difficult to recover from mistakes»; наша сторона (SL/SL лок/рога) — сильный урон + много interrupts/CC, «Low healing». Per-matchup исполнение синтезировано из механик TBC 2.4.3. Теги `synthesized-execution`/`needs-top-source` — нужна верификация топ-RL._

Главная угроза — не их урон (он «low»), а **Viper Sting по варлоку**: наш sustain-мотор SL/SL держится на мане (фиры, Drain Life, Seduction). Осушат ману — развалимся. Второй фактор — кайт: охотник разрывает дистанцию, друид в ToL перекидывает HoT'ы.

Килл-таргет — **охотник** (источник Viper + урона, и его тяжелее рефрешить, чем друида-кайтера):

- Старт: сап охотника, открываемся всей связкой — рог чип → кидни, варлок Curse of Tongues на друида (режет инстант-хилы/циклон) и бёрст в стан-окно.
- Варлок фир/Seduction держит **друида** вне ToL — без него HoT-цепь рвётся (их слабость «difficult to recover from mistakes»).
- Как только слетит Viper Sting — рефрешь ману Life Tap'ом под Soul Link, не давай варлоку уйти в оом.

## Alternative опенер

Если охотник открывает с Scatter Shot + trap на рога — не тратим на них тринка, варлок Spell Lock'ает друида и фир'ит охотника из trap-зоны. Против кайта прижимай охотника через рог-Shadowstep (Shadowstep) и Deadly Throw на interrupt, варлок Curse of Tongues замедляет его Aimed/Steady.

## If enemy trinkets

- Охотник тринкетит кидни и уходит в feign/trap-резет — переведи фир-цепь на друида и не тунелль в feign, жди чистое окно на охотника.
- Друид тринкетит фир и льёт HoT'ы под Barkskin — продли Curse of Tongues, Faerie Fire с его стороны ломает твой restealth (планируй ваниш-резеты заранее).

## Common mistakes

- Дать Viper Sting осушить варлока — без маны RL мёртв; рефрешь Life Tap'ом, стой за пилар от повторных Viper.
- Тунеллить друида в ToL под HoT'ы — он перекидает; правильно **фир-лок друида + урон в охотника**.
- Гнаться за кайтящим охотником по открытому полю — теряешь темп; связывай через Seduction друида и прижимай охотника Shadowstep.
- Забыть про Faerie Fire — под ней рог не уходит в стелс, ваниш-резет впустую.

## Key cooldowns to track

- enemy: хант — Viper Sting, Scatter Shot, trap, feign, Deterrence, тринка; друид — Barkskin, Nature's Swiftness, циклон, Faerie Fire, Travel Form, тринка.
- ours: рога — блайнд, ваниш, преп, Cloak of Shadows, Shadowstep, кидни, Deadly Throw; лок — фир, Death Coil, Seduction, Spell Lock, Curse of Tongues, Soul Link, Drain Life, тринка.
