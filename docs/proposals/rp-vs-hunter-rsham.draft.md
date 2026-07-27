---
slug: rp-vs-hunter-rsham
schema_version: 1
expansion: tbc
composition: rogue+priest
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
  title: "TBC Classic Anniversary 2v2 Comps Tier List (AOEAH, Dec 26 2025) — our comp anchor: Rogue + Discipline Priest = S-tier «Best Disc Comp – No Debate. Blind → Fear chains win games by themselves. Massive opener pressure. Rogue peels endlessly while Priest free-casts.» (enemy hunter+resto-shaman not named in list)"
  retrieved: '2026-07-19'
- type: web
  url: "https://www.icy-veins.com/tbc-classic/restoration-shaman-pvp-guide"
  title: "Restoration Shaman PvP Guide (Icy Veins, Seksi, upd. Jan 12 2026) — enemy-healer anchor: «Restoration Shamans are relatively weak in 2v2 and 3v3... reliance on high cast times... vulnerable to being interrupted or crowd controlled»; Grounding Totem «instantly nullify incoming enemy spells»; Tremor Totem removes fear «but beware totem-stomping macros or Priests fearing at the same time they attack your totem»; best 2v2 partners = RetPala/Warrior/Rogue (hunter NOT listed → off-meta pairing); mana easily lost"
  retrieved: '2026-07-19'
- type: web
  url: "https://www.ownedcore.com/forums/world-of-warcraft/world-of-warcraft-guides/83143-rogues-disc-priest-way-up-1850-rating-2v2-guide.html"
  title: "OwnedCore 83143 — «A rogues/disc priest way up to 1850 rating» (author tfortyranth, 2008 TBC S3) — hunter behaviour (Druid/Hunter): «Hunter will vipersting youre priest, kite you around, while youre rooted, frozen, Cycloned, and scattered. i would take down his pet if i can... let the priest drain... its hard, but thats basicly every team with a hunter or a mage»; vs shaman totems (Warrior/Shaman): «let youre priest use rank 1 smites on the shamans totems... make sure the Windfury totem is down»"
  retrieved: '2026-07-19'
last_reviewed: '2026-07-19'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution]
---

## Opener

_Провенанс: our-comp якорь — AOEAH (Dec 2025): Rogue + Disc Priest = S-tier («Blind → Fear chains win games, massive opener pressure, rogue peels while Priest free-casts»). Enemy-healer факты — Icy Veins Resto Shaman guide (Seksi, upd. Jan 2026): resto-шаман «relatively weak in 2v2... vulnerable to interrupt/CC», Grounding «instantly nullify incoming enemy spells», Tremor снимает fear, mana легко теряется; хантер+резто-шаман не входит в её список 2v2-партнёров (RetPala/Warrior/Rogue) → пара off-meta. Поведение хантера и мана-дрейн-вин — OwnedCore 83143 (tfortyranth, TBC S3): «hunter vipersting your priest, kite... scatter... take down his pet... let the priest drain». Пошаговое RP-исполнение синтезировано из механик TBC 2.4.3. Теги `community-sourced`/`needs-top-source`/`synthesized-execution` — нужна верификация топ-RP перед approve._

Ключ матчапа: это мана-война и борьба за отрыв хилера. Источник (Icy Veins) прямо называет resto-шамана «relatively weak in 2v2» из-за длинных кастов хила — он «vulnerable to being interrupted or crowd controlled». Наш wincon (OwnedCore-паттерн против хилеров): диско **давит и высушивает ману шамана**, рог связывает и не даёт кастовать. Kill target — **shaman** (fallback — hunter, если шаман зарывается в тоталку/NS и неубиваем).

Опенер: рог [[ability:sap]] хантера (или шамана — смотря кого нашли из stealth), открывает на шамане [[ability:premed]] → [[ability:cheap-shot]] → [[ability:kidney-shot]]; диско [[ability:mana-burn]] шамана между его кастами и держит дистанцию от freezing trap/scatter хантера (OwnedCore: хантер «kite you around... scattered»). Перед burst-окном сломай ключевые тотемы рангом-1 smite (OwnedCore, Warrior/Shaman): **grounding** иначе съест твой следующий таргет-спелл (Icy Veins: «instantly nullify incoming enemy spells»), а **tremor** мгновенно снимет твой [[ability:fear]] (Icy Veins: Tremor «removing... fear... beware... Priests fearing at the same time they attack your totem»).

## Alternative opener

Если хантер открыл scatter+trap по диско: рог [[ability:gouge]]/[[ability:kidney-shot]] хантера, чтобы снять давление; диско LoS-ит за пиллар, shield + heal, и возвращается к плану на шамана с [[ability:mana-burn]]. Можно снять часть давления, свалив пета хантера (OwnedCore: «take down his pet if i can»).

## If enemy trinkets

Шаман тринкетит [[ability:kidney-shot]] и кидает Nature's Swiftness-heal → [[ability:gouge]]/повторный stun, и [[ability:fear]] (Psychic Scream) **только если tremor totem уже сломан или далеко** (Icy Veins). Хантер: deterrence (parry/deflect — пережди), readiness (сброс трапов/CD), а главное — viper sting дрейнит ману нашего диско (OwnedCore: «hunter vipersting youre priest»), что критично в мана-войне: закрывай/дисpeлль его и не стой в открытую.

## Common mistakes

- Фир'ить рядом с tremor totem — фир снимается мгновенно (источник: Icy Veins).
- Жечь свою ману в гонку, не сломав totem-сетап и не сняв viper sting с диско.
- Тратить [[ability:fear]]/[[ability:blind]] не на kill-окно.
- Дать хантеру свободно kite'ить и тянуть игру в мана-преимущество (OwnedCore: «its hard... basicly every team with a hunter»).

## Key cooldowns to track

- enemy: shaman — Nature's Swiftness, grounding/tremor/poison-cleansing totems, purge, earth shield, frost shock, trinket; hunter — freezing trap, [[ability:scatter-shot]], deterrence, readiness, viper sting, BM-пет, trinket.
- ours: [[ability:fear]] (Psychic Scream), [[ability:mana-burn]], [[ability:pain-suppression]], dispel, [[ability:blind]], [[ability:gouge]], [[ability:kidney-shot]], [[ability:vanish]], trinket.
