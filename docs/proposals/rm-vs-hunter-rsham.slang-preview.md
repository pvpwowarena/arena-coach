---
slug: rm-vs-hunter-rsham
schema_version: 1
expansion: tbc
composition: rogue+mage
vs: hunter+resto-shaman
bracket: 2v2
difficulty: moderate
kill_target:
  primary: shaman
  fallback: hunter
maps_notes: {}
sources:
- type: web
  url: "https://www.aoeah.com/news/4283--tbc-classic-anniversary-2v2-comps-tier-list"
  title: "TBC Classic Anniversary 2v2 Comps Tier List (AOEAH, Dec 26 2025) — our comp anchor: Rogue + Mage (Sub/Frost) = S-tier «Absolute control of the game... Best CC chain in 2v2... Excellent vs warriors, druids, priests»; shaman-side anchor: «Arms Warrior + Restoration Shaman... no reliable dispel. Shaman must hard-carry with perfect grounding/ES. Loses hard to coordinated Mage teams.» (enemy hunter+resto-shaman itself not named in list)"
  retrieved: '2026-07-19'
- type: web
  url: "https://www.icy-veins.com/tbc-classic/restoration-shaman-pvp-guide"
  title: "Restoration Shaman PvP Guide (Icy Veins, Seksi, upd. Jan 12 2026) — enemy-healer anchor: «relatively weak in 2v2 and 3v3... reliance on high cast times... vulnerable to being interrupted or crowd controlled»; Grounding Totem «instantly nullify incoming enemy spells, which is of great value against any caster team»; Purge «remove up to two beneficial magic effects... strip kill targets clean»; mana easily lost; best 2v2 partners = RetPala/Warrior/Rogue (hunter NOT listed → off-meta pairing)"
  retrieved: '2026-07-19'
- type: web
  url: "https://www.ownedcore.com/forums/world-of-warcraft/world-of-warcraft-guides/83143-rogues-disc-priest-way-up-1850-rating-2v2-guide.html"
  title: "OwnedCore 83143 (author tfortyranth, 2008 TBC S3) — hunter behaviour (Druid/Hunter): «Hunter will vipersting youre priest, kite you around, while youre rooted, frozen, Cycloned, and scattered. i would take down his pet if i can»; «its hard, but thats basicly every team with a hunter or a mage» — hunter viper-drains the caster and kites (applies to our Mage's mana)"
  retrieved: '2026-07-19'
last_reviewed: '2026-07-19'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rm-vs-hunter-rsham.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: our-comp якорь — AOEAH (Dec 2025): рога + маг = S-tier («best CC chain», «wins on setup», «excellent vs warriors, druids, priests»). шам-side якорь — AOEAH прямо про шаман-тоталку: «Arms вар + Restoration шам... no reliable dispel. шам must hard-carry with perfect grounding/ES. Loses hard to coordinated маг teams» — т.е. шаман-хилер тонет против координированных магов. Enemy-хил детали — Icy Veins Resto шам guide (Seksi, upd. Jan 2026): «relatively weak in 2v2... vulnerable to interrupt/CC», Grounding «instantly nullify incoming enemy spells... against any caster team», Purge стрипает баффы kill-таргета, mana легко теряется; хантер не в её списке 2v2-партнёров → пара off-meta. Поведение хантера — OwnedCore 83143 (tfortyranth): viper-стинг по кастеру + kite + scatter. RM-исполнение синтезировано из механик TBC 2.4.3. Теги `community-sourced`/`needs-top-source`/`synthesized-execution` — нужна верификация топ-RM перед approve._

Ключ матчапа (источник: AOEAH) — шаман-тоталка «loses hard to coordinated маг teams», а resto-шаман (Icy Veins) «relatively weak in 2v2... vulnerable to interrupt/CC». Наш RM с «best CC chain» этим и пользуется. фокус — **шам** (хилер; fallback — хант, если шаман зарылся в тоталку/NS). Главные помехи: grounding totem съедает наш таргет-спелл (Icy Veins: «instantly nullify incoming enemy spells»), purge снимает баффы мага (Icy Veins), viper sting дрейнит ману мага (OwnedCore), flare вскрывает рога. Tremor нерелевантен — у RM нет фир.

Опенер: маг давит хантера новами/cone of cold, вынуждая шамана коммититься; рог заходит на шамана премед → чип → Hemorrhage → кидни, маг шатерит (нова → ice lance) в окно kidney. **Перед burst убей/сломай grounding** — иначе кс на хил или шип уйдут в тотем (Icy Veins).

## Alternative опенер

Если хантер заскаттерил/затрапил нашего мага на старте: рог чип хантера или kite до спадания trap, маг блок под их burst. Дальше — план на шамана.

## If enemy trinkets

Шаман тринкетит кидни и кидает Nature's Swiftness-heal → повторный stun/кс на heal-школу (nature) и шип после др. Хантер: deterrence (parry/deflect — пережди), readiness (сброс трапов), scatter+trap нашего мага. Критично: viper sting сушит ману мага (OwnedCore) — не давай застинговать себя в оом перед kill-окном.

## Common mistakes

- Засендить кс в хил, не сняв grounding totem — лок уйдёт в тотем (источник: Icy Veins, grounding нуллифицирует спелл).
- Сесть на хантера, дав шаману спокойно тоталить и NS-хилить, без давления на отрыв totem-сетапа.
- Дать viper sting высушить ману мага (OwnedCore).
- Игнорировать flare — рог вскрывается и теряет рестелс.

## Key cooldowns to track

- enemy: шам — Nature's Swiftness, grounding/tremor/poison-cleansing totems, purge, earth shield, frost shock (snare), тринка; хант — freezing trap, Scatter Shot, deterrence, readiness, viper sting, BM-пет, тринка.
- ours: кс, шип, нова, кидни, блайнд, ваниш, блок, тринка.
