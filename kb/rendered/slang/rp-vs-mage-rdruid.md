---
slug: rp-vs-mage-rdruid
schema_version: 1
expansion: tbc
composition: rogue+priest
vs: mage+resto-druid
bracket: 2v2
difficulty: moderate
kill_target:
  primary: mage
  fallback: druid
maps_notes: {}
sources:
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/"
  title: "Rogue/Disc Priest 2v2 Guide (Deadlycoward, Infernal Gladiator DP/R) — секция «DPR vs. Druid / Frost Mage», Difficulty 5/10: «Kill mage by making him run out of mana / Kill druid after his trinket. Open with a Sap on the mage, dispels from your priest, and focus him with Mana Burns. It's pretty easy to kite and avoid CCs because your priest can dispel everything except cyclone. So OOM the mage and kill him. Also, you can kill druid in human form without trinket because your priest can dispel you.»"
  retrieved: '2026-06-28'
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-discipline-priest-rogue-arena-strategies/"
  title: "Discipline Priest/Rogue — TBC 2v2 Arena Strategies (Warcraft Tavern) — DPR strengths: «Good Mobility vs casters (dispel def vs. frost mage, druid roots, locks)», «Very useful against controls such as Sheep, Fear, Roots»; weakness: «Longer games in certain match-ups vs other healers/DPS»"
  retrieved: '2026-06-28'
last_reviewed: '2026-06-28'
reviewer: null
confidence: draft
tags: [sourced, synthesized-execution, author-guide]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rp-vs-mage-rdruid.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: матчап-якорь — in-depth DP/R-гайд Deadlycoward (Infernal Gladiator, top-10 EU DP/R season 1) на Warcraft Tavern, секция «DPR vs. друид / Frost маг» (5/10). Прямо из источника: фокус и план — сап мага, дисп прийста, оом мага манабёрном, кайт; добив друида в human form после его трикета. DPR-strengths WT подтверждают, что дисп-прийст комфортен против frost-маг и друид roots («dispel everything except циклон»). Пошаговое исполнение (роговый combo, др, тайминги трикетов) синтезировано на sourced-каркасе из механик TBC 2.4.3. Теги `sourced`/`author-guide`/`synthesized-execution` — перед approve желательно ревью топ-RP._

Матчап (источник, Deadlycoward, 5/10): frost-маг + resto-друид — каст-дамаг под кайт-хилером. Для RP это **не бурст-гонка, а игра на ману**. фокус — вражеский **маг**, которого выжимают в оом манабёрном (fallback — друид, добиваемый в human form после его трикета). Источник прямо: «kill маг by making him run out of mana / kill друид after his тринка».

Опенер (источник): рог сап вражеского **мага**, прийст диспелит его контроль — дисп-прийст снимает шип и нова-root, и вообще «dispel everything except циклон». Дальше прийст давит мага Mana Burn, команда кайтит вокруг пиллара: по источнику матч «pretty easy to kite and avoid CCs», потому что прийст чистит почти весь контроль. Рог держит мага в Gouge/кидни и Garrote (silence рвёт каст), не давая блинкать-кастовать, пока манабёрн добивает его мана-пул. Маг в оом — добиваем.

## Alternative опенер

Fallback-цель — друид (источник: «kill друид after his тринка … kill друид in human form without тринка because your прист can dispel you»). Если маг невыгодно разменял ману или спрятался в блок, свяжи мага и лови **друида в human form**: прийст диспелит с рога снейр/root, рог чип → кидни друида, бурст в окно. Лучший момент — когда трикет друида на КД, а циклон уже потрачен.

## If enemy trinkets

Друид трикетит кидни/фир и держит NS-циклон на твой добив — циклон прийст **не диспелит** (источник), поэтому не вкладывай kill-сетап, пока у друида свободен циклон. По источнику друид после трикета всё равно убиваем в human form (трикет ушёл на КД → лови с дисп-помощью прийста). Маг трикетит кидни/Garrote → блок под давление; пережди IB и продолжай Mana Burn — его мана-пул, а не HP, главный таргет.

## Common mistakes

- Играть в бурст-гонку вместо оом-плана по магу — источник описывает матч именно как кайт/мана-войну (поэтому 5/10), а не burst-kill.
- Вкладывать сетап в друида при свободном циклон — его прийст снять не может (источник).
- Не диспелить маг-контроль с напарника — весь комфорт RP здесь в том, что прийст чистит шип/root («dispel everything except циклон»).
- Дать друиду спокойно пить/innervate и затянуть матч — long game играет на их хилера (WT: «longer games vs other healers/дд»).

## Key cooldowns to track

- enemy: друид — циклон (не диспелится), Nature's Swiftness, innervate, barkskin, тринка; маг — блок, блинк, кс, шип, нова, Spellsteal, тринка.
- ours: Mana Burn, Pain Suppression, dispel, фир, сап, Garrote, Gouge, кидни, блайнд, ваниш, Cloak of Shadows, Will of the Forsaken, тринка.
