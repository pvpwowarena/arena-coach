# Arena Jargon Glossary

Канонический справочник терминов для slash-команды `/glossary <term>`.

Каждый термин = `## H2` секция. Тело — короткое определение + связанные термины + примеры.

---

## DR

**Diminishing Returns.** Механика, при которой повторное применение одного типа CC на той же цели имеет уменьшенный эффект:
- 1-е применение: 100% длительности
- 2-е применение (в течение ~15 сек): 50%
- 3-е применение: 25%
- 4-е: immune (15 сек окно)

В TBC DR'ы группируются по категориям: `stun`, `incapacitate`, `disorient`, `fear`, `silence`, `root`. Cheap Shot и Kidney Shot — оба stun, делят одну DR-цепочку.

**См. также:** `dr-category` поле в abilities.json.

---

## premed

Сокращение от **Preme­ditation** (Premeditation, Rogue, spell 14183) — преварительное накопление combo-points на цель, обычно из стелса, чтобы сразу после Cheap Shot выполнить полную комбинацию (`![cheap-shot] → [[ability:premed]] → [[ability:kidney-shot]]`). Даёт +2 CP, активно 20 сек или до атаки.

**Не путать с** Preparation (`spell_shadow_antishadow`, spell 14185) — это сброс кулдаунов рога (Vanish/Sprint/Cold Blood/Premeditation/Blind), отдельный спелл.

---

## shatter

Frost Mage комбо: **Frost Nova** (или любой freeze-эффект) → следующий frost-спелл получает критический удар (механика Shatter, повышенный crit-chance на frozen-цель). Стандартное опенер-сочетание: `[[ability:nova]] → frostbolt` или `[[ability:nova]] → ice-lance`.

---

## sap-stall

Тактика: повторно сапать одну и ту же цель (обычно хила) каждый раз, когда rogue-stealth доступен (Vanish + Preparation). Цель — стелить весь матч в CC, давая команде окно убить второго противника. Особенно эффективно против druid healer'ов с пре-хотами и Resto Shaman'ов.

---

## blanket CS

**Blanket Counterspell.** CS, забрасываемый «вслепую» — не реактивно на каст, а превентивно, чтобы залочить **школу заклинаний** цели на 8 сек (см. mage talent: Improved Counterspell). Применяется:
- против healer'а во время сетапа на цели (lock holy/nature)
- против shape-cast'ов друида (`[[ability:cyclone]]`, innervate)
- ловить trinket reaction (CS at the moment of expected trinket)

---

## opener

Первые 5-10 секунд матча, обычно начинающиеся из стелса или приближения. Самая шаблонная фаза боя; матчап-гайды KB фокусируются на ней.

---

## reset

Тактический «откат»: рог уходит в стелс (vanish или LoS), мага использует Invisibility, команда расходится по карте, чтобы дать DR'ам остыть и переоткрыть бой с нуля. Часто после неудачного опенера или для смены kill-target.

---

## kill target

Игрок, на котором фокусируется давление. У большинства comp-vs-comp матчапов есть primary kill target (например, druid для RM vs Warrior/Druid) и fallback (warrior). В KB-документе зафиксировано как `kill_target.primary` / `kill_target.fallback`.

---

## peel

Прикрыть тиммейта от давления — стан/CC/slow/blind на противника, который бьёт тиммейта. Например: рог peel'ит варриора блайндом, когда варриор переходит на мага.

---

## swap

Переключение давления на другую цель. Часто после первого trinket противника: «swap to warrior» или «swap to druid».

---

## post-trinket

Фаза после того, как противник использовал PvP-trinket (Insignia of the Alliance/Horde, spell 42292). Trinket снимает любой CC и даёт 30-сек immunity к stun/charm/sleep/fear/etc — потому что resilience-cap. Cooldown трикета 2 минуты. Подсказки в KB разделяются на `## Opener` и `## If enemy trinkets`, потому что пост-трикет — отдельная тактическая фаза.

---

## OOM

Out of mana. В дампе матча (после ~5 минут) у healer'ов часто заканчивается мана; OOM хил — почти-гарантированная победа.

---

## dampening

Механика **Healing Reduction**, нарастающая с длительностью матча. В классическом TBC dampening как механики нет в чистом виде (это WotLK+ концепция), но healer'ы всё равно бьются о мана-проблемы; KB-доки используют термин условно для «матч затянулся, хил не успевает».

---

## LoS

**Line of Sight.** Прятаться за пилларом, чтобы прервать каст противника (cast requires LoS). Используется и в опенере, и в защите.

---

## sticky nova

Frost Nova, наложенная «сквозь» противника — когда цель уже в melee range, нова приклеивает её на месте даже если она пыталась убежать. Противоположность — «failed nova» или «slipping nova».
