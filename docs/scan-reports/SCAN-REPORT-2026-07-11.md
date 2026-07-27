# Source-scan report — 2026-07-11 (авто-задача)

**Итог: 0 новых sourced-драфтов** (4 гипотезы остаются заблокированными — блок сегодня подтверждён **седьмым** независимым источником, впервые не tier-list'ом, а полноценным RP-гайдом: см. §2). Главное за ран: **открыт `Pri_Rog_2` — второй полноценный RP-POV гайд на AJ** (автор **Factionz**, Mal'Ganis/US-Stormstrike — тот же Factionz, что в нашем RMP 3v3-гайде; self-claim «top priest/rogue in Shadowburn», оспаривается троллями в комментах — кред брать с пометкой). 12 матчап-подстраниц под наш RP. Прочитаны: главная + 3 ключевые подстраницы + Therst/Darkalpha `Dru_Htr_vs_Pri_Rog` (закрыта последняя позиция сверки из очереди 07-10 §4) → enrichment-материал для **5 драфтов** (§3). Ничего не аппрувлено, в `kb/matchups/` ничего не мёржено, драфты не изменялись.

**Проверки (green):** `validate-kb kb/drafts/` = **51 OK** · `pytest tests/` = **146 passed** (⚠ было 113 — тест-суита выросла после Phase 4.1/v0.3.0-коммитов; счётчик драфтов в `test_kb_loader.py` = 51, совпадает) · KB не менялась → render_slang не требуется. Браузер подключён (Chrome, macOS).

**Правило дат соблюдено:** все 5 прочитанных AJ-страниц — снапшоты Wayback июль–август 2008; все использованные комменты ≤ 3 августа 2008 → до патча 3.0.2, TBC-чистые.

---

## 1. Свежий скан (WebSearch)

- Per-matchup источников по 4 заблокированным парам в открытом вебе нет. Два новых сайта в выдаче — `overgear.com` (PvP tier list) и `epiccarry.com` (PvP guide) — оба boost-селлер SEO без автора (категория koroboost/aoeah, решение 07-08 §5). **В sources не берём.**
- **Новые видео-кандидаты (RP-POV, не встречались в прошлых отчётах):** см. §5 — четыре видео + плейлист; самый ценный — Earpugs 2100 MMR **с live comms** (вербальная тактика в транскрипте).
- WebSearch-сводка сегодня без conflation-инцидентов (утверждения из сводок в дело не брались — только живые страницы).

## 2. Гипотезы: осталось 4, блок подтверждён (7-й источник, впервые POV-гайд)

| Slug | Статус сегодня |
|---|---|
| rm-vs-hunter-hpala | Faction Pri_Rog_2 (12 матчапов): пары hunter+hpala нет. Блок прежний |
| rm-vs-hunter-rsham | то же (у Faction есть только Shm_War, шаман-пары с хантером нет) |
| rp-vs-hunter-rsham | то же |
| rm-vs-mage-rdruid | у Faction есть Dru_Rog/Dru_Wlk/Dru_War/Dru_Htr — mage+rdruid нет и здесь |

Не-мета статус подтверждён: 6 tier-list сайтов + **оба AJ RP-гайда** (Mixster и Faction — 16 и 12 матчапов, целевых пар нет ни в одном). Пути прежние: mirlol Twitch-sub владельца → `arena_ingest paste`; yt-dlp транскрипты в интерактивной сессии (песочница — 403, перепроверено сегодня, все 3 ретрая).

## 3. Enrichment-предложения (НЕ применял — жду отмашки; добавляются к очереди 07-06…07-10)

### 3a. `rp-vs-hunter-rdruid` ← AJ Therst/Darkalpha `Dru_Htr_vs_Pri_Rog` (сверка с Megatf выполнена)

Второй enemy-POV (Therst/Darkalpha, Gorgonnash/US-Rampage; снапшот 2008-08-06, комменты ≤ 3 авг 2008). **Difficulty-вилка:** Therst «very simple combo to beat» (за Dru/Htr) — контраст с Cyclonian у Megatf («Have yet to beat Priest/Rogue 2100+»); дисент в их же комментах (Cinemaslave) «actually quite a hard combo» — RP выигрывает **агрессией на хантера с манабёрном сквозь станлок** → ПОДТВЕРЖДАЕТ вин-лайн Cyclonian из 07-10 §3b, теперь два независимых свидетельства. Их план: pillar + **Flare + Frost Trap на старте** (наш рог должен ждать/обходить, не прыгать в flare), viper-фокус на приста, кайт; «рог на хантере = 0% их шансов» (Abolish + kite) — **прямой контр-довод против rogue-on-hunter**, наша линия = прист бёрнит, рог на друиде/прессинг. Их вин-кондишны против нас (→ Common mistakes): килл их друида возможен только если рог сливает все CD, тринкет потрачен не на Blind, или хантер зафирен вне позиции; **килл их пета = наша опция** (Therst: «They can also kill your pet for a win»), контр — imp rez (Marcato); их контр-меры при спам-диспеле друида — Scatter на рога + спам Wing Clip; FD против нашего Shadowfiend (совпадает с «KITE IT» Megatf). Marcato: cyclone на ПРИСТА при жёстком хиле (чтобы не диспелил хоты) — угроза нашему присту.

### 3b. `rp-vs-rogue-mage` + `rm-vs-rogue-priest` (двойная ценность) ← AJ Faction `Pri_Rog_2_vs_Mag_Rog`

RP-POV против RM (комменты ≤ 10 июня 2008). План Faction: **атаковать мага**; если RM сел на нашего рога — прист **обязан SW:D-нуть ПЕРВЫЙ sheep** («не снял первый sheep = проигрываешь каждый раз»); механика: backlash SW:D выбивает из poly после лендинга + DR режет следующий. **Тринкет-дисциплина:** НЕ тринкетить sheep (иначе blind → рог мёртв), НЕ тринкетить sap (same DR as sheep — Factionz), беречь тринкет под KS «когда рогу нужен диспел». Аутрейндж CS; «без full-duration CC на присте они рога не убьют». Опен RM на приста «проигрывает быстро» — виабельно только sap-приста-в-центре + shatter (= ошибка позиционирования приста); контр — pillar-hug. Ragozi (альтернатива): прист бейтит опенер у пиллара, **спам r1 Holy Nova вскрывает их рога**, «no sheepy» за пилларом. Проблемные паттерны из комментов (→ Common mistakes): double-undead RM (WotF), free-cast мага пока рог в KS.
**Зеркально для `rm-vs-rogue-priest` (наш RM против RP):** Factionz сам называет контр — **«If the Mage fakes your Shadow Word: Death you lose»** → фейк-каст sheep = прямая вин-лайн нашего RM против диско-приста; + знание их тринкет-дисциплины (не тринкетят sheep/sap → наши CC-чейны планировать без ожидания раннего тринкета).

### 3c. `rp-vs-warrior-rdruid` ← AJ Faction `Pri_Rog_2_vs_Dru_War`

«Матчап №1 — гемись и спекайся именно под него» (Faction; Combat/Mutilate, хоть для остальных матчапов ShS лучше — прямая спек-рекомендация с обоснованием). **Outlast-план:** полная оборона; gouge воина рано → **бейт Berserker Rage → fear через 10с** (Dvineowns: fear воина 3-4 раза за 2 мин); Blind на воина; на друида идём ТОЛЬКО в CC воина — запрет питья; прист убивает воина при мане (Reflective Shield tank); «99.9% Dru/War возьмут бейт и сольют ману»; 10+ минут. Контр-меры хорошего врага (→ Common mistakes): воин перестаёт BR-ить гаудж после 1-2 бейтов (Fröst/Warinax), не пускает приста в fear-range друида (Arveene), дефенсивный Dru/War «не проиграет» (Arveene) — difficulty-сигнал. **Агрессивная альтернатива** (Zoripwnt + Insite, → Alternative opener): прист LoS-ит воина, рог открывает на друиде → форс barkskin/тринкет → **chain mana burns сквозь станлок** → прист чейсит друида, рог рвёт воина; Insite: «ignoring the warrior most of the time» → 50/50 против «unbeatable setup» (+ ссылка warcraftmovies id=67619 — мёртвая, не для sources, упомянута для полноты). Enemy warrior-POV (Xplcs): воин с фул-рейджем + 5 sunders за 10 мин соло-убивает приста; орк-воин аутстанит рога; его план — cyclone×2 на приста → cheat death рога → добив в feral charge bash. Rmelol (гир-зависимость): с 4/8 t6 + 4/5 s3 — просто zerg warrior + pull LoS.

### 3d. `rp-vs-warrior-rsham` ← AJ Faction `Pri_Rog_2_vs_Shm_War`

«Ugly, ugly fight — они могут атаковать кого угодно, сделать миллион ошибок и всё равно победить» (difficulty-сигнал; наш драфт сейчас на ownedcore/mmo-champion/WT — сверить). **Три kill-target линии в источнике:** (1) Faction: **шаман** — «он выбирает heal ИЛИ purge, прист может dispel+heal одновременно»; диспел каждого Earth Shield ASAP, диспел Bloodlust с обоих ASAP, fear беречь на прерывание хила; «10-2 vs 2200+»; (2) Chingwang/Amarille/Tunks: **воин** — шаман оом «всегда быстрее» под прессингом на воина; mana tide легко сносится; (3) Skillzkillz/Treb/Gcwarrior/Imperial: **rogue-on-warrior lock + прист манабёрнит шамана**. **Enemy-POV подтверждения третьей линии:** Treb (их шаман): «нас ломает rogue-on-warrior + mana burn, фул стаки ядов не дают воину дойти до приста»; Gcwarrior (их воин): «проигрываем чаще, когда рог сидит на МНЕ — crippling+станы не дают догнать приста, рога не убить (evasion tank)». Kootz (детальный Muti-план, → Alternative opener): рог между пристом и воином вне charge-range → опен фул станы на воине → прист за пиллар → диспел ES **с воина** → 5 wounds → PWS на рога заранее (WS debuff спадает к свапу воина) → kill tremor + fear шамана → выманить воина на приста → рог blind шамана (тринкет-бейт) → **PI + mana burn ×5 без прерываний** → vanish при <50% → outlast. Контр-нюансы (→ Common mistakes): орк-шаман Blood Fury ломает стан-цепочки (Clinutin); убийство WF-тотема бесполезно, пока воин свободен — 10с на ре-дроп при 10с баффа на оружии (Clinutin); умный воин пилит на рога вовремя (Pitiless) — спам-hamstring + mace-станы снимают приста с шамана.

### 3e. Общие RP-советы ← AJ Faction `Pri_Rog_2` (главная)

Мелочи для Common mistakes нескольких RP-драфтов: прист — «heal early and often», не увлекаться mana burn в ущерб хилу; rage-fed воин соло-убивает приста — не танковать 15с между Kidney, убегать на Crippling; рог — не увлекаться пилингом vs Healer/DPS («KS→Gouge→Blind чейн с 0 дамага = их хилер напился до фула»); focus-macro на друида, Cloak+Vanish на его циклоны; Silent Resolve ценен vs lock/priest/shaman-команды (Factionz в комментах); ShS-спек защищает от RM-опенера (Enim, дисент базовому Combat/Mut-совету). Общая оценка Faction: «Priest/Rogue is a tough composition; Druid/Warrior, Shaman/Warrior и Druid/Hunter — самые тяжёлые матчапы» — сверить с difficulty трёх наших драфтов.

## 4. AJ-очередь: обновление

**Прочитано сегодня (5 стр.):** Therst/Darkalpha `Dru_Htr_vs_Pri_Rog` (последняя позиция сверки 07-10 §4 закрыта) + Faction `Pri_Rog_2` главная + `vs_Mag_Rog` + `vs_Dru_War` + `vs_Shm_War`.

**Новый остаток — 9 нечитанных подстраниц Faction Pri_Rog_2** (URL-паттерн `Pri_Rog_2_vs_<Xxx_Yyy>`): `Dru_Htr` (сверка с Mixster/Megatf/Therst), `Dru_Rog`, `Dru_Wlk`, `Htr_Pri` (⚠ ячейка hunter+priest — в KB её нет, см. ниже), `SPri_Rog` (для rp-vs-rogue-spriest), `Pri_Rog` (mirror), `Pri_Wlk`, `Rog_Rog`, `Rog_Wlk`. Приоритет: SPri_Rog / Pri_Rog-mirror / Rog_Wlk (у существующих драфтов тонкие sources) > Dru_Rog/Dru_Wlk/Dru_Htr (уже богато обогащены) > остальное.

**Ячейка-кандидат (решение владельца):** `hunter+priest` — подстраница есть в ОБОИХ AJ RP-гайдах (Mixster и Faction), aoeah даёт MM Hunter+Disc Priest A-tier (07-09 §2). Три независимых сигнала, что пара реальна в мете. Если владелец одобрит ячейку — источник для sourced-драфта уже готов (без гипотезо-фазы).

Прежний низкоприоритетный остаток без изменений: PomPyro Mage/Rogue (спек-кандидат), `Pri_Rog_vs_Mag_Wlk` (Mixster, ячейка mage+warlock), 3v3 `Dru_Mag_Rog_vs_Mag_Pri_Rog` и `Dru_Mag_War`/`Dru_Rog_War`/`Htr_Mag_Pri`/`Pal_Shm_War` vs нас.

## 5. Видео-кандидаты (yt-dlp очередь интерактивной сессии; песочница 403 — подтверждено сегодня)

Очередь была: `qJn9rLhDLZU` (R1 SPR vs RM) → `DLEZ7Yi4-jU` → `mHgkNzlnpPQ` (Kooba). **Новые (все RP-POV, впервые в отчётах):**

| Видео | Что это | Приоритет |
|---|---|---|
| `PcfLBroowrM` | «TBC Arena 2v2 Disc Priest Rogue at 2100 MMR **w/ Live Comms!**», автор **Earpugs** (9.3k subs), ~2021-22 (TBC Classic эпоха), метаданные сняты через браузер | **Высокий** — live comms = вербальная тактика в транскрипте |
| `1_mMWxa6Njg` | «Rogue/Disc Priest 2v2 Arena TBC 2400+ mmr» (автора уточнить при yt-dlp) | Средний |
| «Rogue Disc Priest 2v2 Arena TBC 2500+ MMR», автор Netwrking (9.7k subs) | всплыл в рекомендациях; ID уточнить | Средний |
| Плейлист `PLrxHsk5qvXbAkVwbVj9Iqp8fvTwk0qcku` «TBC Rogue Priest 2v2» | сборник RP-POV | Низкий (разобрать состав) |
| `yKp5DzXgu34` | «Druid/Warrior vs Mage/Rogue — **Resto Druid POV**» — enemy-POV для `rm-vs-warrior-rdruid` | Средний |
| Twitch VOD `2617544608` (13 нояб 2025) | «TBC ARENA 2V2 ROGUE GAMEPLAY \| Multi R1 Disc» — свежий Anniversary-контент | Низкий (Twitch, транскрипта нет; смотреть только вручную) |

## 6. Housekeeping

- Stale hypothesis-дубликатов по-прежнему **12** — ждут удаления владельцем (SCAN-REPORT 07-03 §3).
- ⚠ **Счётчик тестов: 113 → 146 passed** (после Phase 4.1/bridge v0.3.0/addon v0.2.0 коммитов 07-11). Упоминания «113 тестов» в `CLAUDE.md` и системных инструкциях устарели — обновить при следующей правке CLAUDE.md.
- `docs/NEXT-SESSION-HANDOFF.md` датирован 06-23 (39/16) — актуально **51 драфт / 16 гипотез (4 незасорсенных)**; обновить в интерактивной сессии.
- Незакоммиченного на начало рана не было (репо чистое); сегодня добавился только этот отчёт.

## 7. Следующие шаги

1. **Отмашка владельца на enrichment-батчи** — очередь: 07-06 §3a-3c + 07-07 §3a-3e + 07-08 §3a-3d + 07-09 §3a-3d + 07-10 §3a-3d + **сегодняшние §3a-3e** (≈21 страница материала на ~16 драфтов). Сегодняшние — первый RP-POV пласт: 4 RP-драфта + зеркальный подарок для rm-vs-rogue-priest.
2. Интерактивная сессия: yt-dlp транскрипты — очередь выросла до 5+ видео (§5), приоритет Earpugs live comms.
3. AJ-дочитка: 9 подстраниц Faction Pri_Rog_2 (§4), приоритет SPri_Rog / mirror / Rog_Wlk.
4. Решения владельца: ячейка `hunter+priest` (три сигнала, источники готовы); удаление 12 stale-дубликатов; обновление handoff + счётчика тестов в CLAUDE.md.
