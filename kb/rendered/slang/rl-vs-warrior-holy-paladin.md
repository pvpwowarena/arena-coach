---
slug: rl-vs-warrior-holy-paladin
schema_version: 1
expansion: tbc
composition: rogue+warlock
vs: warrior+holy-paladin
bracket: 2v2
difficulty: hard
kill_target:
  primary: warrior
  fallback: paladin
maps_notes: {}
sources:
- type: web
  url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings"
  title: "2v2 Arena Composition Rankings (Icy Veins) — Warrior/Holy Paladin: keep Warrior active with Cleanse and Blessing of Freedom, double plate survivability; weaknesses «Vulnerable to curses; Very limited crowd control»"
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

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rl-vs-warrior-holy-paladin.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: состав **RL (рога / лок 2v2, SL/SL)**. Sourced-каркас: Icy Veins тирит Warr/HPala как durable-комп («keep вар active with Cleanse and Blessing of Freedom; Double plate increases survivability»), слабости — «Vulnerable to curses; Very limited контроль»; наша сторона (SL/SL лок/рога) — «Strong damage all around; Multiple interrupts and CC options; Low healing». Per-matchup исполнение синтезировано из механик TBC 2.4.3. Теги `synthesized-execution`/`needs-top-source` — нужна верификация топ-RL._

Это **игра на истощение и CC-войну**, а не на быстрый килл: Warr/HPala переживает бёрст за счёт двойной плазы, Cleanse и Blessing of Freedom. Наш козырь — их слабость: «very limited контроль» против нашего вороха CC, и **уязвимость к curse** (паладинский Cleanse снимает magic/poison/disease, но **НЕ снимает Curse of Tongues**).

Килл-таргет — **воин**, но выигрывается матч через изоляцию пала:

- Старт: открываемся из стелса на воина — премед → чип → кидни; варлок сразу вешает Curse of Tongues на **паладина** (режет касты хила, Cleanse его не снимает) и льёт в стан-окно.
- Варлок держит паладина фир/Seduction — у Warr/HPala нет tremor, фир-цепь работает. Чередуй фир / Death Coil / Howl of Terror через др, не жги подряд.
- Blessing of Freedom снимает наши snare с воина и держит его на варлоке — под ним не трать блайнд на реактив, жди окончания.

## Alternative опенер

Если хотят затренить варлока (Warr на нём + HoJ): Soul Link + Fel Armor уже висят, рог мгновенно снимает давление блайнд по воину, варлок фир'ит паладина и каналит Drain Life из-за пилар (лос от подж). Против длинной игры следи за маной — Siphon Life висит на цели постоянно.

## If enemy trinkets

- Паладин тринкетит фир/кидни и уходит в подж + хил — тогда сразу продли Curse of Tongues и переведи фир-цепь на него: без тринка он голый ~2 минуты.
- Воин тринкетит кидни — не трать бёрст в его defensive stance/plate; свяжи паладина Seduction и переоткройся на воина через ваниш → премед.

## Common mistakes

- Тунеллить паладина в открытую под Cleanse/бабл — он вылечит; правильно — **CoT на пала + фир-лок**, а урон в воина.
- Жечь фиры подряд по паладину — делят др, уходит в иммун; чередуй с рог-станами.
- Забыть, что Cleanse НЕ снимает curse — Curse of Tongues на паладина держится и это главный рычаг против их хилов.
- Ловить Blessing of Freedom бёрстом впустую — под ним воин не снейпится, дождись окончания.

## Key cooldowns to track

- enemy: вар — тринка, Blessing of Freedom (на нём), Death Wish, Spell Reflection; пал — Blessing of Freedom, Cleanse, bubble (Divine Shield), подж, тринка.
- ours: рога — блайнд, ваниш, преп, Cloak of Shadows, Evasion, кидни; лок — фир, Death Coil, Howl of Terror, Seduction, Spell Lock, Curse of Tongues, Soul Link, Drain Life, тринка.
