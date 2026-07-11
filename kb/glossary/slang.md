# Arena Slang Glossary (RU ⇄ canonical)

> ⚠ **Авто-генерируется** из `slang.json` через `tools/gen_slang_md.py`. Не редактировать руками — правь `slang.json` и перегенери.
> Сгенерировано: 2026-06-19 · Записей: 59 · Новых canonical slug'ов: 18

**Назначение:** маппинг русского задрот-сленга команды ⇄ canonical slug ⇄ защищённый EN-термин (Phase 1.5).

- `slang[]` — все распознаваемые формы (вход: понять игрока, паста стрима, голосовая команда).
- `voice` / `register` — что бот/TTS отдаёт на **выход** (Phase 4.5): `std` = безопасно для генерации, `colloq` = понимаем на входе, в речь без нужды не суём.
- `ref` — где живёт canonical-определение: `abilities.json` (спелл-дата), `terms.md` (жаргон), `new` (концепт пока без отдельного canonical — домик в slang.json).


## Способности (29)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `blind` | blind | ослепление | блайнд, блайндить, слепить, ослепить, заблайндить | **блайнд** | std | high | abilities.json |
| `blink` | blink | блинк | блинк, блинкнуться, блинкнулся | **блинк** | std | high | new |
| `cheap-shot` | cheap shot | чип-шот | чип, чипшот, чипшотнуть | **чип** | std | high | abilities.json |
| `cloak` | cloak | клоак | клоак, кош | **клоак** | colloq | med | abilities.json |
| `counterspell` | Counterspell | кс | кс, контра, контру | **кс** | std | high | abilities.json |
| `cyclone` | cyclone | циклон | циклон, циклонить, цикл | **циклон** | std | high | abilities.json |
| `death-coil` | death coil | коил | коил, койл | **коил** | colloq | med | abilities.json |
| `evasion` | evasion | эвейжн | эвейжн | **эвейжн** | colloq | med | abilities.json |
| `evisc` | eviscerate | эвис | эвис | **эвис** | std | high | abilities.json |
| `fear` | fear | страх | фир, фирнуть, зафирить | **фир** | std | high | abilities.json |
| `garrote` | garrote | гаррота | гаррота, гарота | **гарота** | colloq | med | abilities.json |
| `gouge` | gouge | гордж | гадж, гордж, горджить | **гадж** | colloq | med | abilities.json |
| `hammer-of-justice` | hammer of justice | подж | хаммер, подж | **подж** | std | high | abilities.json |
| `hemo` | hemo | хеморрейдж | хема, хемо | **хема** | colloq | low | abilities.json |
| `ice-block` | ice block | айс-блок | блок, айсблок, ледышка, в блоке | **блок** | std | high | abilities.json |
| `icy-veins` | icy veins | ледяные вены | вены | **вены** | colloq | med | abilities.json |
| `kidney` | kidney shot | кидни-шот | кидни, кидней, почка | **кидни** | std | high | abilities.json |
| `mana-burn` | mana burn | бёрн | бёрн, манабёрн, выжечь ману, сжигать ману | **бёрн** | colloq | med | abilities.json |
| `nova` | frost nova | фрост-нова | нова, новить, зановить, новнуть | **нова** | std | high | abilities.json |
| `premed` | premed | премедиейшн | премед, премедить | **премед** | std | high | abilities.json |
| `preparation` | preparation | препарейшн | преп, препнуть, препа | **преп** | std | high | abilities.json |
| `sap` | sap | сап | сап, сапнуть, засапить, сапить, сапуля | **сап** | std | high | abilities.json |
| `scatter-shot` | scatter shot | скаттер | скаттер, скат | **скаттер** | colloq | med | abilities.json |
| `sheep` | polymorph | полиморф | поли, заполить, овца, шип | **шип** | std | high | abilities.json |
| `shiv` | shiv | шив | шив, шивнуть, шивануть | **шив** | colloq | med | abilities.json |
| `slice-and-dice` | slice and dice | слайс-энд-дайс | снд, слайс, дайсить | **снд** | colloq | med | abilities.json |
| `step` | shadowstep | шэдоустеп | степ, шедоустеп | **степ** | colloq | med | abilities.json |
| `trinket` | Trinket | тринкет | тринка, тринканул | **тринка** | std | high | new |
| `vanish` | vanish | ваниш | ваниш | **ваниш** | std | high | abilities.json |

**Заметки:**

- `blink` — mage. Нет в abilities.json — кандидат на добавление (Blink, ~spell 1953).
- `cloak` — Cloak of Shadows; «кош» = CoS.
- `counterspell` — «кик» для CS команда не использует (убрано). У вара аналог — Pummel.
- `cyclone` — друид.
- `death-coil` — лок.
- `fear` — лок/прист.
- `garrote` — Добавил «гарота» в формы под твой voice (в правке было только «гаррота»).
- `hammer-of-justice` — пал (HoJ). «подж» — основная форма; добавил в slang[], чтобы voice распознавался (в правке было только «хаммер»).
- `icy-veins` — маг бёрст-кд.
- `mana-burn` — прист.
- `premed` — +2 CP из стелса. RU оставил как в твоей правке (возможна опечатка → «премедитейшн»?).
- `preparation` — сброс кд рога; не путать с premed.
- `scatter-shot` — хант.
- `sheep` — slug=sheep (Polymorph). voice=«шип» по твоей правке.
- `step` — slug step (есть и shadowstep).
- `trinket` — Insignia/Medallion. Нет в abilities.json — кандидат (id уточнить, ~42292).


## Тактика (13)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `blanket-cs` | blanket CS | бланкет | бланкет, бланкетнуть | **бланкет** | colloq | med | terms.md |
| `cc` | crowd control | контроль | контроль, законтролить, цц | **контроль** | std | high | new |
| `focus-damage` | focus / train | пилить | пилить, спилить, вынести, слить | **пилить** | std | high | new |
| `kill-target` | kill target | фокус | фокус, килтаргет, цель | **фокус** | std | high | terms.md |
| `los` | LoS | лос | лос, лосить, за пилар | **лос** | std | high | terms.md |
| `opener` | opener | опенер | опенер, опен, заход | **опенер** | std | high | terms.md |
| `peel` | peel | пил | пил, пильнуть, отпилить | **пил** | std | high | terms.md |
| `post-trinket` | post-trinket | пост-тринка | пост-тринка, после тринки | **после тринки** | colloq | med | terms.md |
| `reset` | reset | ресет | ресет, ресетнуть, отресетить | **ресет** | std | high | terms.md |
| `sap-stall` | sap-stall | сап-столл | сапстолл, сап-контроль | **сапстолл** | colloq | med | terms.md |
| `shatter` | shatter | шаттер | шаттер, шатнуть | **шаттер** | std | high | terms.md |
| `sticky-nova` | sticky nova | стики-нова | стики нова, стики | **стики нова** | colloq | low | terms.md |
| `swap` | swap | свап | свап, свапнуть, перекинуть | **свап** | std | high | terms.md |

**Заметки:**

- `blanket-cs` — превентивный кс вслепую (лок школы на 8 сек).
- `cc` — «сс» убрал из-за нежелательной коннотации — оставил «цц»/«контроль».
- `focus-damage` — наносить урон по цели. НЕ путать с «пил» (peel).
- `kill-target` — «ласт» убрал — это другое (команда «добивай»), а не цель фокуса.
- `peel` — peel = прикрыть тиммейта. НЕ путать с «пилить» (focus-damage).
- `post-trinket` — фаза после тринки врага (синхронизировано с trinket=тринка).
- `reset` — Убрал шуточное «решетка».
- `shatter` — крит по frozen-цели.
- `sticky-nova` — Ниша: нова «сквозь» цель в melee. Уместность под вопросом — нужна ли запись?


## Статусы / механики (5)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `combo-points` | combo points | очки | очки, цпшки, комбо | **очки** | std | high | new |
| `cooldown` | cooldown | кд | кд, на кд, выбить кд, попнуть кд | **кд** | std | high | new |
| `dampening` | dampening | дамп | дамп, затянули | **дамп** | colloq | low | terms.md |
| `dr` | DR | др | др, в др, задрить | **др** | std | high | abilities.json |
| `oom` | OOM | оом | оом, без маны, замана | **оом** | std | high | terms.md |

**Заметки:**

- `combo-points` — у рога.
- `cooldown` — «попнуть» = использовать кд.
- `dampening` — В чистом TBC механики нет — условно для затяжного матча. Нужна ли запись?
- `dr` — diminishing returns. Есть и в terms.md.


## Роли (2)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `dps` | DPS | дд | дд, дамагер, дамаг | **дд** | std | high | new |
| `healer` | healer | хил | хил, хилка, хилер | **хил** | std | high | new |

**Заметки:**

- `healer` — частая цель сапа/контроля.


## Объекты (1)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `pillar` | pillar | пилар | пилар, столб | **пилар** | std | high | new |

**Заметки:**

- `pillar` — объект для LoS.


## Классы (9)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `druid` | druid | друид | друид, дру | **друид** | std | high | new |
| `hunter` | hunter | хант | хант, хантер | **хант** | std | high | new |
| `mage` | mage | маг | маг, мага | **маг** | std | high | new |
| `paladin` | paladin | пал | пал, паладин | **пал** | std | high | new |
| `priest` | priest | прист | прист, шадоу, диско | **прист** | std | high | new |
| `rogue` | rogue | рога | рога | **рога** | std | high | new |
| `shaman` | shaman | шам | шам, шаман | **шам** | std | high | new |
| `warlock` | warlock | лок | лок, варлок | **лок** | std | high | new |
| `warrior` | warrior | вар | вар, варриор | **вар** | std | high | new |

**Заметки:**

- `priest` — шадоу=shadow, диско=discipline.


## Новые canonical slug'и (нет в abilities.json / terms.md)

Эти концепты получили canonical-домик прямо в `slang.json`. При желании поднять в `abilities.json` (`trinket`, `blink`) или оставить как есть (роли/классы/механики):

`blink`, `cc`, `combo-points`, `cooldown`, `dps`, `druid`, `focus-damage`, `healer`, `hunter`, `mage`, `paladin`, `pillar`, `priest`, `rogue`, `shaman`, `trinket`, `warlock`, `warrior`


## Защищённые EN-термины (для sync с Phase 1.5)

Список EN-форм, которые остаются на английском в прозе (свести с «защищённым списком» в `docs/phase-1.5-translation-plan.md`):

`Counterspell`, `DPS`, `DR`, `LoS`, `OOM`, `Trinket`, `blanket CS`, `blind`, `blink`, `cheap shot`, `cloak`, `combo points`, `cooldown`, `crowd control`, `cyclone`, `dampening`, `death coil`, `druid`, `evasion`, `eviscerate`, `fear`, `focus / train`, `frost nova`, `garrote`, `gouge`, `hammer of justice`, `healer`, `hemo`, `hunter`, `ice block`, `icy veins`, `kidney shot`, `kill target`, `mage`, `mana burn`, `opener`, `paladin`, `peel`, `pillar`, `polymorph`, `post-trinket`, `premed`, `preparation`, `priest`, `reset`, `rogue`, `sap`, `sap-stall`, `scatter shot`, `shadowstep`, `shaman`, `shatter`, `shiv`, `slice and dice`, `sticky nova`, `swap`, `vanish`, `warlock`, `warrior`
