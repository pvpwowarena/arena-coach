# Arena Slang Glossary (RU ⇄ canonical)

> ⚠ **Авто-генерируется** из `slang.json` через `tools/gen_slang_md.py`. Не редактировать руками — правь `slang.json` и перегенери.
> Сгенерировано: 2026-06-05 · Записей: 59 · Новых canonical slug'ов: 18

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
| `evasion` | evasion | эвейжн | эвейжн | ** эвейжн** | colloq | med | abilities.json |
| `evisc` | eviscerate | эвис | эвис | ** эвис** | std | high | abilities.json |
| `fear` | fear | страх | фир, фирнуть, зафирить | **фир** | std | high | abilities.json |
| `garrote` | garrote | гаррота | гаррота | **гарота** | colloq | med | abilities.json |
| `gouge` | gouge | гордж | гадж, гордж, горджить | **гадж** | colloq | med | abilities.json |
| `hammer-of-justice` | hammer of justice | подж | хаммер | **подж** | std | high | abilities.json |
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

- `blink` — mage. НЕТ в abilities.json — предлагаю добавить (Blink, ~spell 1953).
- `cloak` — Cloak of Shadows (slug cloak / cloak-of-shadows).
- `counterspell` — «кик» = прервать каст; в RM почти всегда Counterspell. У вара это Pummel, у рога Kick — контекст по классу.
- `cyclone` — друид.
- `death-coil` — лок (фир-эффект на 3 сек).
- `fear` — лок/прист.
- `garrote` — silence-гаррота используют как сайленс на каст.
- `gouge` — формы транслита разнятся — поправь под вашу пачку.
- `hammer-of-justice` — пал (HoJ).
- `hemo` — формы спорные — уточни.
- `icy-veins` — маг бёрст-кд.
- `kidney` — slug kidney (есть и kidney-shot).
- `mana-burn` — прист.
- `premed` — +2 CP из стелса. Есть и в terms.md.
- `preparation` — сброс кд рога. Не путать с premed.
- `scatter-shot` — хант.
- `sheep` — slug=sheep (en Polymorph). «овца»/«шип» — разговорные формы.
- `shiv` — обычно для crippling/mind-numbing.
- `step` — slug step (есть и shadowstep).
- `trinket` — Insignia/Medallion, снимает CC + иммун. НЕТ в abilities.json — предлагаю добавить (id уточнить, ~42292).


## Тактика (13)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `blanket-cs` | blanket CS | бланкет-кс | бланкет, бланкетнуть, кс вслепую, превентивный кс | **бланкет** | colloq | med | terms.md |
| `cc` | crowd control | контроль | сс, контроль, законтролить, в контроле, цц | **контроль** | std | high | new |
| `focus-damage` | focus / train | продавливать урон | пилить, спилить, вынести, слить, продавить, нагибать, топить | **пилить** | std | high | new |
| `kill-target` | kill target | цель фокуса | фокус, килтаргет, цель, ласт | **фокус** | std | med | terms.md |
| `los` | LoS | линия видимости | лос, лосить, за пилар, пилларить, спрятаться за колонну | **лос** | std | high | terms.md |
| `opener` | opener | опенер | опенер, опен, заход, открывашка, зайти | **опенер** | std | high | terms.md |
| `peel` | peel | пил | пил, пильнуть, отпилить, прикрыть, пильнуть с тиммейта | **пил** | std | high | terms.md |
| `post-trinket` | post-trinket | пост-тринкет | пост-трина, после трины, послетрина, пост трина | **после трины** | colloq | med | terms.md |
| `reset` | reset | ресет | ресет, решетка, разбежаться, отресетить, сбросить др | **ресет** | std | high | terms.md |
| `sap-stall` | sap-stall | сап-столл | сапстолл, застелить хила, держать в сапе, стелить хила | **сапстолл** | colloq | med | terms.md |
| `shatter` | shatter | шаттер | шаттер, шатнуть, шатер-комбо, по фрозен | **шаттер** | std | high | terms.md |
| `sticky-nova` | sticky nova | стики-нова | стики, стики нова, приклеить нову, липкая нова | **стики нова** | colloq | low | terms.md |
| `swap` | swap | свап | свап, свапнуть, переключить, перекинуть, перекид | **свап** | std | high | terms.md |

**Заметки:**

- `blanket-cs` — лок школы на 8 сек, не реактивно.
- `cc` — общий термин CC; в slang.json как новый canonical.
- `focus-damage` — «пилить» = наносить урон по цели. НЕ путать с «пил» (peel). Новый canonical.
- `kill-target` — «фокус» = по кому давим; «ласт» = добивай (низкий хп). Разные смыслы — поправь при ревью.
- `peel` — «пил» (peel = прикрыть тиммейта). НЕ путать с «пилить» (focus-damage).
- `post-trinket` — фаза после трины врага.
- `shatter` — крит по frozen-цели.
- `sticky-nova` — нова «сквозь» цель в melee.


## Статусы / механики (5)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `combo-points` | combo points | очки комбо | очки, цпшки, комбо, цп, поинты | **очки** | std | high | new |
| `cooldown` | cooldown | кулдаун | кд, кулдаун, на кд, откат, попнуть кд, скд | **кд** | std | high | new |
| `dampening` | dampening | дампенинг | дамп, дампенинг, затянули, затяжка | **дамп** | colloq | low | terms.md |
| `dr` | DR | уменьшение отдачи | др, дрнуть, в др, диминишинг, задрить | **др** | std | high | abilities.json |
| `oom` | OOM | без маны | оом, без маны, высох, пустой, на нуле маны, замана | **оом** | std | high | terms.md |

**Заметки:**

- `combo-points` — у рога. Новый canonical.
- `cooldown` — «попнуть» = использовать кд. Новый canonical.
- `dampening` — в чистом TBC механики нет — условно для затяжного матча (см. terms.md).
- `dr` — diminishing returns. Есть и в terms.md.


## Роли (2)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `dps` | DPS | дамагер | дд, дамагер, дамаг, урон | **дд** | std | high | new |
| `healer` | healer | лекарь | хил, хилка, хилер, лекарь, хиллер | **хил** | std | high | new |

**Заметки:**

- `dps` — Новый canonical.
- `healer` — частая цель сапа/контроля. Новый canonical.


## Объекты (1)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `pillar` | pillar | колонна | пилар, пиллар, столб, колонна | **пилар** | std | high | new |

**Заметки:**

- `pillar` — объект для LoS. Новый canonical.


## Классы (9)

| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |
|---|---|---|---|---|---|---|---|
| `druid` | druid | друид | друид, дру, фериа, перо | **друид** | std | med | new |
| `hunter` | hunter | охотник | хант, хантер, ха, охотник | **хант** | std | high | new |
| `mage` | mage | маг | маг, мага, фрост-маг | **маг** | std | high | new |
| `paladin` | paladin | паладин | пал, палик, паладин | **пал** | std | high | new |
| `priest` | priest | жрец | прист, шадоу, диско | **прист** | std | high | new |
| `rogue` | rogue | разбойник | рога, рожка, вор, ассасин | **рога** | std | high | new |
| `shaman` | shaman | шаман | шам, шаман | **шам** | std | high | new |
| `warlock` | warlock | чернокнижник | лок, варлок, чернокнижник | **лок** | std | high | new |
| `warrior` | warrior | воин | вар, варриор, воин | **вар** | std | high | new |

**Заметки:**

- `druid` — «перо»/«фериа» — разговорные.
- `priest` — шадоу=shadow, диско=discipline.


## Новые canonical slug'и (нет в abilities.json / terms.md)

Эти концепты получили canonical-домик прямо в `slang.json`. При желании поднять в `abilities.json` (`trinket`, `blink`) или оставить как есть (роли/классы/механики):

`blink`, `cc`, `combo-points`, `cooldown`, `dps`, `druid`, `focus-damage`, `healer`, `hunter`, `mage`, `paladin`, `pillar`, `priest`, `rogue`, `shaman`, `trinket`, `warlock`, `warrior`


## Защищённые EN-термины (для sync с Phase 1.5)

Список EN-форм, которые остаются на английском в прозе (свести с «защищённым списком» в `docs/phase-1.5-translation-plan.md`):

`Counterspell`, `DPS`, `DR`, `LoS`, `OOM`, `PvP Trinket`, `blanket CS`, `blind`, `blink`, `cheap shot`, `cloak`, `combo points`, `cooldown`, `crowd control`, `cyclone`, `dampening`, `death coil`, `druid`, `evasion`, `eviscerate`, `fear`, `focus / train`, `frost nova`, `garrote`, `gouge`, `hammer of justice`, `healer`, `hemo`, `hunter`, `ice block`, `icy veins`, `kidney shot`, `kill target`, `mage`, `mana burn`, `opener`, `paladin`, `peel`, `pillar`, `polymorph`, `post-trinket`, `premed`, `preparation`, `priest`, `reset`, `rogue`, `sap`, `sap-stall`, `scatter shot`, `shadowstep`, `shaman`, `shatter`, `shiv`, `slice and dice`, `sticky nova`, `swap`, `vanish`, `warlock`, `warrior`
