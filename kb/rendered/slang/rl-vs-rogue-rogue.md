---
slug: rl-vs-rogue-rogue
schema_version: 1
expansion: tbc
composition: rogue+warlock
vs: rogue+rogue
bracket: 2v2
difficulty: moderate
kill_target:
  primary: rogue
  fallback: rogue
maps_notes: {}
sources:
- type: web
  url: "https://www.ownedcore.com/forums/world-of-warcraft/world-of-warcraft-guides/111880-arena-double-rogue-guide.html"
  title: "Double Rogue Arena Guide (OwnedCore, TBC 2.x) — «whichever team gets sapped first loses», «the whole idea is to CC someone and blow up his partner before you run out of CC options», no healing, cloak/vanish resets, Sap/Blind 20s DR"
  retrieved: '2026-07-24'
- type: web
  url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings"
  title: "2v2 Arena Composition Rankings (Icy Veins) — SL/SL Warlock/Rogue: «Strong damage all around; Multiple interrupts and CC options», weakness «Low healing»"
  retrieved: '2026-07-24'
last_reviewed: '2026-07-24'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, new-comp-rl]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rl-vs-rogue-rogue.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: состав **RL (рога / лок 2v2, SL/SL)** против зеркального двойного рога. Sourced-каркас: OwnedCore Double рога Guide (TBC 2.x) — «whichever team gets sapped first loses», «CC someone and blow up his partner before you run out of CC options», у double-рога «no healing» + резеты через cloak/ваниш, сап/блайнд делят 20с др; наша сторона (Icy Veins, SL/SL лок/рога) — «Strong damage; Multiple interrupts and CC options», слабость «Low healing». Per-matchup исполнение синтезировано из механик TBC 2.4.3. Теги `synthesized-execution`/`needs-top-source` — нужна верификация топ-RL._

Ключ по источнику: **«кого сапнули первым — тот проиграл»**. Но у нас асимметрия — вместо второго рога **варлок с фир/Seduction и SL/SL-танковостью**. У double-рога нет ни хила, ни tremor, ни ответа на повторный фир (кроме тринка + WotF у андедов). Это наш перевес в CC-войне.

Килл-таргет — **любой из рогов** (у них «no healing», низкая танковость):

- Старт: **выиграй сап-гонку** — сап их открывающего рога раньше, чем они сапнут нашего. Варлок фир'ит второго рога, разрывая его чип → кидни-цепь.
- Открываемся на одного рога: наш рог чип → кидни, варлок Curse of Tongues + бёрст; Soul Link/Fel Armor держат нас в размене, которого у них нет.
- Помни: сап и блайнд делят 20с др — не трать оба на одну цель подряд.

## Alternative опенер

Если сапнули нашего рога первым — не паникуй: варлок сам себе «хилер» через Soul Link + Master Healthstone, фир'ит открывающего рога и Seduction'ит второго. Рог выходит ваниш → сап для сброса и переоткрытия (их же тактика «ваниш and then сап for a 10 second CC»).

## If enemy trinkets

- Рог тринкетит кидни и уходит в Cloak of Shadows (снимает фир/Curse of Tongues) + ваниш-резет — не жги фир в Cloak of Shadows, жди спад и фирь после.
- Второй рог тринкетит Seduction/стан — переведи фир-цепь на него, у double-рога нет второго набора эскейпов после тринка+cloak.

## Common mistakes

- Проиграть сап-гонку и не среагировать — сразу варлок-фир по открывающему, не тунелль урон, пока связка не восстановлена.
- Жечь фир в Cloak of Shadows — снимается; тайминг фиров под спад клока/ваниша.
- Тратить сап + блайнд на одну цель подряд — общий 20с др, второй CC почти пустой.
- Меняться уроном в лоб — у обоих «no healing», но наш Soul Link/дрейн даёт sustain, которого нет у них; играй чуть длиннее и они сломаются первыми.

## Key cooldowns to track

- enemy: рога×2 — Cloak of Shadows, ваниш, блайнд, преп, кидни, Evasion, тринка + WotF (undead).
- ours: рога — блайнд, ваниш, преп, Cloak of Shadows, Evasion, кидни; лок — фир, Death Coil, Howl of Terror, Seduction, Spell Lock, Soul Link, Curse of Tongues, тринка.
