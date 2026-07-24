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

## Opener

_Провенанс: состав **RL (Rogue / Warlock 2v2, SL/SL)** против зеркального двойного рога. Sourced-каркас: OwnedCore Double Rogue Guide (TBC 2.x) — «whichever team gets sapped first loses», «CC someone and blow up his partner before you run out of CC options», у double-rogue «no healing» + резеты через cloak/vanish, Sap/Blind делят 20с DR; наша сторона (Icy Veins, SL/SL Warlock/Rogue) — «Strong damage; Multiple interrupts and CC options», слабость «Low healing». Per-matchup исполнение синтезировано из механик TBC 2.4.3. Теги `synthesized-execution`/`needs-top-source` — нужна верификация топ-RL._

Ключ по источнику: **«кого сапнули первым — тот проиграл»**. Но у нас асимметрия — вместо второго рога **варлок с fear/[[ability:seduction]] и SL/SL-танковостью**. У double-rogue нет ни хила, ни tremor, ни ответа на повторный [[ability:fear]] (кроме trinket + WotF у андедов). Это наш перевес в CC-войне.

Килл-таргет — **любой из рогов** (у них «no healing», низкая танковость):

- Старт: **выиграй sap-гонку** — [[ability:sap]] их открывающего рога раньше, чем они сапнут нашего. Варлок [[ability:fear]]'ит второго рога, разрывая его [[ability:cheap-shot]] → [[ability:kidney-shot]]-цепь.
- Открываемся на одного рога: наш рог [[ability:cheap-shot]] → [[ability:kidney-shot]], варлок [[ability:curse-of-tongues]] + бёрст; [[ability:soul-link]]/[[ability:fel-armor]] держат нас в размене, которого у них нет.
- Помни: [[ability:sap]] и [[ability:blind]] делят 20с [[ability:dr]] — не трать оба на одну цель подряд.

## Alternative opener

Если сапнули нашего рога первым — не паникуй: варлок сам себе «хилер» через [[ability:soul-link]] + Master Healthstone, [[ability:fear]]'ит открывающего рога и [[ability:seduction]]'ит второго. Рог выходит [[ability:vanish]] → [[ability:sap]] для сброса и переоткрытия (их же тактика «vanish and then sap for a 10 second CC»).

## If enemy trinkets

- Рог тринкетит [[ability:kidney-shot]] и уходит в [[ability:cloak-of-shadows]] (снимает [[ability:fear]]/[[ability:curse-of-tongues]]) + [[ability:vanish]]-резет — не жги [[ability:fear]] в [[ability:cloak-of-shadows]], жди спад и фирь после.
- Второй рог тринкетит [[ability:seduction]]/стан — переведи фир-цепь на него, у double-rogue нет второго набора эскейпов после trinket+cloak.

## Common mistakes

- Проиграть sap-гонку и не среагировать — сразу варлок-[[ability:fear]] по открывающему, не тунелль урон, пока связка не восстановлена.
- Жечь [[ability:fear]] в [[ability:cloak-of-shadows]] — снимается; тайминг фиров под спад клока/ваниша.
- Тратить [[ability:sap]] + [[ability:blind]] на одну цель подряд — общий 20с [[ability:dr]], второй CC почти пустой.
- Меняться уроном в лоб — у обоих «no healing», но наш [[ability:soul-link]]/дрейн даёт sustain, которого нет у них; играй чуть длиннее и они сломаются первыми.

## Key cooldowns to track

- enemy: rogue×2 — [[ability:cloak-of-shadows]], [[ability:vanish]], [[ability:blind]], [[ability:preparation]], [[ability:kidney-shot]], [[ability:evasion]], trinket + WotF (undead).
- ours: rogue — [[ability:blind]], [[ability:vanish]], [[ability:preparation]], [[ability:cloak-of-shadows]], [[ability:evasion]], [[ability:kidney-shot]]; warlock — [[ability:fear]], [[ability:death-coil]], [[ability:howl-of-terror]], [[ability:seduction]], [[ability:spell-lock]], [[ability:soul-link]], [[ability:curse-of-tongues]], trinket.
