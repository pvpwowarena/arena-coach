"""Combat-лог как realtime-канал — Phase 4.2.

Почему: chat-лог в Anniversary-клиенте НЕ флашится до полного выхода из игры
(живой тест 2026-07-23: файл 2 часа лежал 0 байт при работающих whisper'ах),
а combat-лог сбрасывается на диск прямо во время боя (~48КБ буфер, в бою
события сыпятся потоком). Поэтому realtime-события (тринкеты, дефы, касты
врагов) bridge берёт из combat-лога напрямую — аддон для этого не нужен.

Имя файла: современный клиент пишет `WoWCombatLog-MMDDYY_HHMMSS.txt`
(новый файл на каждое включение /combatlog или рестарт клиента); легаси-имя
`WoWCombatLog.txt` тоже поддерживаем. Берём самый свежий по mtime и
переключаемся, когда появляется новее.

Стратегия конверсии: CLEU-события переводятся в те же AC-payload строки
(`TRINKET#Имя#42292#pvp_trinket`), что шлёт аддон, — дальше их обрабатывает
существующий normalize_raw. Совместимость с backend полная, pipeline не
меняется.

Арена-детект — по ауре «Arena Preparation» (32727/32728):
  • SPELL_AURA_APPLIED на дружественных игроков → копим нашу команду
    (prep-фаза до открытия ворот).
  • SPELL_AURA_REMOVED → ворота открылись → ARENA_START
    (bracket = размер нашей команды: 2v2/3v3/5v5).
  • Классы игроков выводим из кастов (таблица spell_id → класс) и
    re-emit'им ARENA_START с уточнением — backend сохраняет сессию и
    обновляет матч (тот же механизм, что «враг вышел из стелса»).
  • ARENA_END — 90с без hostile-активности либо новая prep-фаза.
"""

from __future__ import annotations

import asyncio
import csv
import logging
import re
from collections import deque
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

log = logging.getLogger(__name__)

# ── Константы ────────────────────────────────────────────────────────────────

ARENA_PREP_SPELL_IDS = {32727, 32728}  # Arena Preparation

# Зеркало AC.TRINKET_IDS из аддона (Tracker.lua)
TRINKET_IDS: dict[int, str] = {
    42292: "pvp_trinket",  # Medallion of the Alliance/Horde
    59752: "every_man",  # Every Man for Himself
    7744: "wotf",  # Will of the Forsaken
}

# Зеркало AC.TRACKED_SPELLS из аддона (Tracker.lua) — ключи совпадают с
# _ABILITY_HINT_KEYS пайплайна, фильтрация хинтов остаётся на бэке.
TRACKED_SPELLS: dict[int, str] = {
    # Rogue
    1856: "vanish",
    26669: "evasion",
    31224: "cloak_of_shadows",
    14185: "preparation",
    2094: "blind",
    408: "kidney_shot",
    1833: "cheap_shot",
    6770: "sap",
    # Mage
    45438: "ice_block",
    2139: "counterspell",
    118: "polymorph",
    122: "frost_nova",
    # Warrior
    871: "shield_wall",
    1161: "challenging_shout",
    5246: "intimidating_shout",
    20230: "retaliation",
    # Druid
    33786: "cyclone",
    22812: "barkskin",
    29166: "innervate",
    # Priest
    33206: "pain_suppression",
    8122: "psychic_scream",
    10060: "power_infusion",
    # Warlock
    5782: "fear",
    6789: "death_coil",
    # Paladin
    853: "hammer_of_justice",
    642: "divine_shield",
    1044: "blessing_of_freedom",
}

# spell_id → класс: для вывода состава из кастов. Не исчерпывающе — достаточно
# нескольких сигнатурных спеллов на класс (TBC 2.4.3 ранги).
_CLASS_SPELLS: dict[str, set[int]] = {
    # Пополнено реальными id из живых combat-логов 2026-07-23.
    # Отдельный пласт — «баффы на воротах» (шауты/благословения/марки/стойки):
    # их жмут в первые секунды матча, это самый быстрый reveal класса
    # (вар Cekraj определялся 10с по Charge, хотя Commanding Shout был сразу).
    "ROGUE": {1856, 26669, 31224, 14185, 2094, 408, 1833, 6770, 26862, 26865, 1766, 27188},
    "MAGE": {45438, 2139, 118, 122, 27070, 27072, 30455, 12042, 11129, 27126, 23028, 31687, 12472},
    "WARRIOR": {
        871,
        1161,
        5246,
        20230,
        30330,
        25212,
        11578,
        23920,
        12292,
        469,
        2048,
        2457,
        2458,
        71,
    },
    "DRUID": {
        33786,
        22812,
        29166,
        26988,
        26985,
        26982,
        16979,
        33357,
        22570,
        33763,
        26980,
        33983,
        8983,
        9634,
        33891,
        34123,
        26990,
        26992,
        24858,
        768,
    },
    "PRIEST": {33206, 8122, 10060, 25218, 25375, 34917, 32379, 25368, 25389, 25392},
    "WARLOCK": {
        5782,
        6789,
        27209,
        27216,
        30414,
        30546,
        19647,
        28189,
        688,
        691,
        697,
        712,
        30146,
        18708,
        29858,
    },
    "PALADIN": {
        853,
        642,
        1044,
        27136,
        27137,
        31884,
        20066,
        24275,
        25898,
        27140,
        27142,
        27143,
        31842,
        35395,
    },
    "HUNTER": {27065, 34026, 27018, 19503, 19386, 14311, 27044, 34490, 1543, 883, 982, 27046},
    "SHAMAN": {
        25454,
        2825,
        16166,
        8177,
        8012,
        25457,
        25396,
        32182,
        25423,
        25505,
        8143,
        2484,
        8166,
        8170,
        2894,
        2062,
        17364,
    },
}
SPELL_TO_CLASS: dict[int, str] = {sid: cls for cls, ids in _CLASS_SPELLS.items() for sid in ids}

# spell_id → спек: уточнение класса до специализации (Phase 4.7). Тонкости спеков
# критичны (holy vs ret pala, resto vs feral, fire vs frost), а class-level матчинг
# их терял. ВСЕ id ниже — уже валидированные в _CLASS_SPELLS (из живых логов /
# курирования), поэтому риск мисклассификации нулевой: спелл лишь дополнительно
# помечает спек уже опознанного класса.
#
# STRONG — talent-defining спеллы: перекрывают и лочат спек (Pyroblast = точно fire,
# даже если маг до этого кастовал frostbolt в shatter-сетапе PoM-Pyro).
_SPELL_TO_SPEC_STRONG: dict[int, str] = {
    30330: "arms-warrior",  # Mortal Strike
    27070: "fire-mage",  # Pyroblast
    11129: "fire-mage",  # Combustion
    33983: "feral-druid",  # Mangle (Cat)
    8983: "feral-druid",  # Bash
    9634: "feral-druid",  # Dire Bear Form
    33763: "resto-druid",  # Lifebloom
    34917: "shadow-priest",  # Vampiric Touch
    10060: "discipline-priest",  # Power Infusion
    20066: "ret-paladin",  # Repentance (51-й талант ret)
    25423: "resto-shaman",  # Chain Heal
    16166: "ele-shaman",  # Elemental Mastery
    # Phase 4.9 (pet/totem-инференс): talent-defining саммоны и 41-очковые кнопки.
    31687: "frost-mage",  # Summon Water Elemental — элементаль = точно фрост
    12472: "frost-mage",  # Icy Veins
    33206: "discipline-priest",  # Pain Suppression (41 диск)
    33891: "resto-druid",  # Tree of Life (41 рестор)
    24858: "balance-druid",  # Moonkin Form
    31842: "holy-paladin",  # Divine Illumination (41 холи)
    35395: "ret-paladin",  # Crusader Strike (41 рет)
    17364: "enh-shaman",  # Stormstrike
    30146: "demo-warlock",  # Summon Felguard (41 демонолог)
}
# WEAK — спек-намёк: ставится, только если спек ещё неизвестен, и перекрывается
# любым STRONG (frostbolt кастует и fire-маг ради shatter → frost НЕ лочим).
_SPELL_TO_SPEC_WEAK: dict[int, str] = {
    27072: "frost-mage",  # Frostbolt
    26980: "resto-druid",  # Regrowth
    768: "feral-druid",  # Cat Form (рестор изредка бегает кошкой — не лочим)
}

# ── Pet-проксирование (Phase 4.9) ────────────────────────────────────────────
# Каст пета выдаёт класс (и спек) ХОЗЯИНА раньше, чем хозяин кастанёт сам, —
# критично против пассивных/LoS-игроков. Пока в таблице только водный элементаль
# (id единственные и верифицированные); хант-петы (Claw/Bite) добавим после
# сверки ranked-id с живым логом — кривой id = мисклассификация, это дороже.
_PET_SPELL_TO_OWNER: dict[int, tuple[str, str | None]] = {
    31707: ("MAGE", "frost-mage"),  # Waterbolt
    33395: ("MAGE", "frost-mage"),  # Freeze (элементаль-нова)
}

# CLEU unit flags
_FLAG_TYPE_PLAYER = 0x0400
_FLAG_TYPE_PET = 0x1000
_FLAG_TYPE_GUARDIAN = 0x2000  # элементаль мага/тотемы — guardian, не pet
_FLAG_REACTION_HOSTILE = 0x0040
_FLAG_REACTION_FRIENDLY = 0x0010

_ARENA_END_QUIET_S = 90.0  # тишина активности ВРАГОВ МАТЧА → конец
_DUP_WINDOW_S = 5.0  # cast+aura одного спелла → одно событие
#: Потолок форварда НЕзнакомых кастов (Phase 4.12) — на матч, в минуту.
_FORWARD_BUDGET_PER_MIN = 90
#: Слаг имени способности: "Scatter Shot" → "scatter_shot" (зеркало backend.kb.spells).
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(name: str) -> str:
    return _SLUG_RE.sub("_", name.strip().lower()).strip("_")


_MAX_ENEMY_FALLBACK = 5  # кап ростера врагов, если размер команды не определился

_TS_FORMAT = "%m/%d/%Y %H:%M:%S.%f"


def parse_cleu_line(line: str) -> tuple[datetime, list[str]] | None:
    """Разобрать строку combat-лога в (timestamp, [event, field, ...]).

    Формат: `7/23/2026 13:50:59.5253  SPELL_AURA_APPLIED,src,...` —
    таймстамп отделён ДВУМЯ пробелами, дальше CSV (имена в кавычках,
    внутри могут быть запятые).
    """
    raw = line.strip()
    if not raw:
        return None
    sep = raw.find("  ")
    if sep < 0:
        return None
    ts_str, payload = raw[:sep], raw[sep + 2 :].strip()
    try:
        ts = datetime.strptime(ts_str, _TS_FORMAT)
    except ValueError:
        return None
    try:
        fields = next(csv.reader([payload]))
    except (csv.Error, StopIteration):
        return None
    if not fields:
        return None
    return ts, fields


def _short_name(raw_name: str) -> str:
    """«Endwõr-Spineshatter-EU» → «Endwõr» (реалм-суффикс не нужен бэку)."""
    return raw_name.split("-", 1)[0].strip('"')


def _parse_flags(raw: str) -> int:
    try:
        return int(raw, 16)
    except ValueError:
        return 0


def _is_player(flags: int) -> bool:
    return bool(flags & _FLAG_TYPE_PLAYER)


def _is_hostile_player(flags: int) -> bool:
    return _is_player(flags) and bool(flags & _FLAG_REACTION_HOSTILE)


def _is_friendly_player(flags: int) -> bool:
    return _is_player(flags) and bool(flags & _FLAG_REACTION_FRIENDLY)


def _is_hostile_pet(flags: int) -> bool:
    """Вражеский пет/страж (элементаль мага, фелхантер, хант-пет)."""
    return (
        not _is_player(flags)
        and bool(flags & (_FLAG_TYPE_PET | _FLAG_TYPE_GUARDIAN))
        and bool(flags & _FLAG_REACTION_HOSTILE)
    )


@dataclass
class _Unit:
    name: str
    wow_class: str | None = None
    spec: str | None = None
    spec_locked: bool = False
    proxy: bool = False  # выведен из каста ПЕТА (хозяин ещё не кастовал сам)


def _encode_enemy(u: _Unit) -> str:
    """'MAGE/UNKNOWN' или 'MAGE/UNKNOWN/fire-mage' (раса из combat-лога неизвестна).

    3-е поле (спек) — опционально: старый backend его игнорирует (from_str берёт
    первые два), новый — использует для сужения матчапа до спека.
    """
    if u.spec:
        return f"{u.wow_class}/UNKNOWN/{u.spec}"
    return f"{u.wow_class}/UNKNOWN"


@dataclass
class CombatInterpreter:
    """Конечный автомат: CLEU-события → AC-payload строки для normalize_raw.

    Args:
        player_name: имя нашего персонажа ($BRIDGE_PLAYER_NAME) — ставится
            первым в allies, backend таргетирует советы под его класс.
    """

    player_name: str = ""
    _in_prep: bool = field(default=False, init=False)
    _session: bool = field(default=False, init=False)
    _allies: dict[str, _Unit] = field(default_factory=dict, init=False)
    _enemies: dict[str, _Unit] = field(default_factory=dict, init=False)
    _last_hostile_ts: datetime | None = field(default=None, init=False)
    _recent: dict[tuple[str, int], datetime] = field(default_factory=dict, init=False)
    _event_count: int = field(default=0, init=False)
    _forwarded: deque[datetime] = field(default_factory=deque, init=False)
    _team_size: int = field(default=0, init=False)
    _last_enemies_key: str | None = field(default=None, init=False)

    # ── публичный вход ──────────────────────────────────────────────────

    def feed_line(self, line: str) -> list[str]:
        """Обработать сырую строку combat-лога, вернуть AC-payload'ы (0..n)."""
        parsed = parse_cleu_line(line)
        if parsed is None:
            return []
        ts, fields = parsed
        out: list[str] = []

        out.extend(self._check_quiet_end(ts))

        event = fields[0]
        if event in ("SPELL_AURA_APPLIED", "SPELL_AURA_REMOVED", "SPELL_CAST_SUCCESS"):
            out.extend(self._handle_spell(ts, event, fields))
        return out

    # ── prep-фаза и границы матча ───────────────────────────────────────

    def _handle_spell(self, ts: datetime, event: str, fields: list[str]) -> list[str]:
        if len(fields) < 11:
            return []
        src_guid, src_name = fields[1], _short_name(fields[2])
        src_flags = _parse_flags(fields[3])
        dst_guid, dst_name = fields[5], _short_name(fields[6])
        dst_flags = _parse_flags(fields[7])
        try:
            spell_id = int(fields[9])
        except ValueError:
            return []

        out: list[str] = []

        # Arena Preparation — границы матча
        if spell_id in ARENA_PREP_SPELL_IDS and _is_player(dst_flags):
            if event == "SPELL_AURA_APPLIED":
                if self._session:
                    out.append(self._end_session())  # новая prep = прошлый матч закончен
                if not self._in_prep:
                    self._in_prep = True
                    self._allies.clear()
                    self._enemies.clear()
                if _is_friendly_player(dst_flags):
                    self._allies.setdefault(dst_guid, _Unit(name=dst_name))
            elif event == "SPELL_AURA_REMOVED" and self._in_prep:
                self._in_prep = False
                self._session = True
                self._last_hostile_ts = ts
                self._event_count = 0
                # Размер команды фиксируем на воротах: он ограничивает ростер
                # врагов (в 2v2 их не может быть больше двух). Иначе после
                # матча ордынцы из открытого мира (тоже hostile player, 0x548)
                # записывались бы во «врагов» — реальный кейс живого теста.
                self._team_size = len(self._allies) if len(self._allies) in (2, 3, 5) else 0
                self._last_enemies_key = None
                start = self._emit_arena_start()
                if start:
                    out.append(start)
            return out

        if not self._session:
            # Вне матча классы союзников всё равно копим — пригодятся на воротах
            if _is_friendly_player(src_flags) and self._in_prep:
                self._note_class(self._allies, src_guid, src_name, spell_id)
            return out

        # ── внутри матча ────────────────────────────────────────────────
        if _is_hostile_player(src_flags):
            enemy_cap = self._team_size or _MAX_ENEMY_FALLBACK
            if src_guid not in self._enemies and len(self._enemies) >= enemy_cap:
                # Ростер полон. Если место занято pet-прокси того же класса —
                # уступаем его реальному игроку (прокси был лишь намёком).
                cls = SPELL_TO_CLASS.get(spell_id)
                if cls is None or not self._drop_proxy(cls):
                    # Иначе это hostile-игрок ВНЕ матча (мир после арены):
                    # не регистрируем, не хинтим и НЕ продлеваем сессию.
                    return out

            self._last_hostile_ts = ts
            newly_cls = self._note_class(self._enemies, src_guid, src_name, spell_id)
            if newly_cls:
                # Реальный игрок раскрыл класс — прокси того же класса больше
                # не нужен (иначе в ростере фантомный «лишний» враг).
                unit = self._enemies[src_guid]
                if unit.wow_class is not None:
                    self._drop_proxy(unit.wow_class, keep_guid=src_guid)
            newly_spec = self._note_spec(self._enemies, src_guid, spell_id)
            if newly_cls or newly_spec:
                start = self._emit_arena_start()
                if start:
                    out.append(start)  # уточнение состава/спеков врагов

            if event == "SPELL_CAST_SUCCESS" or event == "SPELL_AURA_APPLIED":
                spell_name = fields[10] if len(fields) > 10 else ""
                payload = self._emit_hostile_action(ts, src_guid, src_name, spell_id, spell_name)
                if payload:
                    out.append(payload)
        elif _is_hostile_pet(src_flags) and spell_id in _PET_SPELL_TO_OWNER:
            # Каст пета выдаёт класс хозяина раньше самого хозяина (элементаль
            # уже кастует, пока фрост-маг молчит за столбом/в позиции).
            self._last_hostile_ts = ts
            if self._note_pet_proxy(src_guid, src_name, spell_id):
                start = self._emit_arena_start()
                if start:
                    out.append(start)
        elif _is_friendly_player(src_flags):
            # Классы союзников копим для таргетинга, но re-emit НЕ делаем:
            # в DM видны только враги, и каждый такой повтор выглядел бы
            # дублем «Арена началась» (спам из живого теста 2026-07-23).
            self._note_class(self._allies, src_guid, src_name, spell_id)

        return out

    def _note_pet_proxy(self, pet_guid: str, pet_name: str, spell_id: int) -> bool:
        """Записать ХОЗЯИНА пета в ростер врагов как proxy-юнит.

        Прокси добавляется, только если класса хозяина ещё нет в ростере и есть
        свободный слот; при появлении реального игрока того же класса прокси
        уступает место (см. _drop_proxy). Ключ — guid пета: до конца матча пет
        стабилен, а повторные касты не плодят дублей.
        """
        owner_cls, owner_spec = _PET_SPELL_TO_OWNER[spell_id]
        if pet_guid in self._enemies:
            return False
        if any(u.wow_class == owner_cls for u in self._enemies.values()):
            return False  # класс уже представлен — намёк ничего не добавляет
        enemy_cap = self._team_size or _MAX_ENEMY_FALLBACK
        if len(self._enemies) >= enemy_cap:
            return False
        self._enemies[pet_guid] = _Unit(
            name=pet_name,
            wow_class=owner_cls,
            spec=owner_spec,
            spec_locked=owner_spec is not None,
            proxy=True,
        )
        log.info("Combat-канал: по касту пета %s выведен враг %s", pet_name, owner_cls)
        return True

    def _drop_proxy(self, wow_class: str, keep_guid: str | None = None) -> bool:
        """Убрать pet-прокси данного класса (реальный игрок раскрылся)."""
        for guid, unit in list(self._enemies.items()):
            if unit.proxy and unit.wow_class == wow_class and guid != keep_guid:
                del self._enemies[guid]
                log.info("Combat-канал: pet-прокси %s заменён реальным игроком", wow_class)
                return True
        return False

    def _check_quiet_end(self, ts: datetime) -> list[str]:
        if not self._session or self._last_hostile_ts is None:
            return []
        if (ts - self._last_hostile_ts).total_seconds() > _ARENA_END_QUIET_S:
            return [self._end_session()]
        return []

    def _end_session(self) -> str:
        self._session = False
        self._in_prep = False
        self._team_size = 0
        self._last_enemies_key = None
        count, self._event_count = self._event_count, 0
        self._recent.clear()
        log.info("Combat-канал: матч завершён (%d событий)", count)
        return f"ARENA_END#{count}"

    # ── события внутри матча ────────────────────────────────────────────

    def _emit_hostile_action(
        self, ts: datetime, guid: str, name: str, spell_id: int, spell_name: str = ""
    ) -> str | None:
        """Событие враждебного каста → AC-payload.

        Phase 4.12: мост больше НЕ решает, что важно. Раньше он фильтровал по
        зашитому `TRACKED_SPELLS` (27 id, семь классов из девяти — ханта и шамана
        не было вовсе), и любое расширение требовало новой сборки. Теперь
        форвардим всё, что скастовал враг: известный id отдаём каноническим
        ключом, неизвестный — слагом английского имени из лога плюс само имя
        пятым полем. Что с этим делать, решает каталог на бэкенде
        (`kb/glossary/realtime_spells.json`) — правка данных вместо релиза.

        Дедуп по (guid, spell_id) в пределах `_DUP_WINDOW_S` остаётся: клиент
        пишет cast_success и aura_applied как две строки об одном действии.
        """
        key = (guid, spell_id)
        prev = self._recent.get(key)
        if prev is not None and (ts - prev).total_seconds() < _DUP_WINDOW_S:
            return None  # cast + aura одного спелла = одно событие
        self._recent[key] = ts

        if spell_id in TRINKET_IDS:
            self._event_count += 1
            return f"TRINKET#{name}#{spell_id}#{TRINKET_IDS[spell_id]}"

        spell_key = TRACKED_SPELLS.get(spell_id) or _slugify(spell_name)
        if not spell_key:
            return None  # ни id, ни имени — форвардить нечего
        if spell_id not in TRACKED_SPELLS and not self._forward_budget_ok(ts):
            return None
        self._event_count += 1
        return f"ABILITY#{name}#{spell_id}#{spell_key}#{spell_name}"

    def _forward_budget_ok(self, ts: datetime) -> bool:
        """Потолок форварда незнакомых кастов: 90/мин на матч.

        Страховка от аномалии в логе (мультибокс, странный аддон, спам-аура):
        бэкенд всё равно троттлит речь, но трафик и БД беречь стоит.
        """
        cutoff = ts - timedelta(seconds=60)
        while self._forwarded and self._forwarded[0] < cutoff:
            self._forwarded.popleft()
        if len(self._forwarded) >= _FORWARD_BUDGET_PER_MIN:
            return False
        self._forwarded.append(ts)
        return True

    # ── состав ──────────────────────────────────────────────────────────

    def _note_class(self, side: dict[str, _Unit], guid: str, name: str, spell_id: int) -> bool:
        """Зафиксировать класс юнита по спеллу. True, если класс стал известен."""
        unit = side.setdefault(guid, _Unit(name=name))
        if unit.wow_class is not None:
            return False
        wow_class = SPELL_TO_CLASS.get(spell_id)
        if wow_class is None:
            return False
        unit.wow_class = wow_class
        log.info("Combat-канал: %s определён как %s", name, wow_class)
        return True

    def _note_spec(self, side: dict[str, _Unit], guid: str, spell_id: int) -> bool:
        """Уточнить спек юнита по сигнатурному спеллу. True, если спек изменился.

        STRONG перекрывает и лочит (Pyroblast → fire даже после frostbolt).
        WEAK ставится, только если спека ещё нет, и не лочит.
        """
        unit = side.get(guid)
        if unit is None:
            return False
        strong = _SPELL_TO_SPEC_STRONG.get(spell_id)
        if strong is not None:
            if unit.spec == strong and unit.spec_locked:
                return False
            unit.spec = strong
            unit.spec_locked = True
            log.info("Combat-канал: %s уточнён как %s", unit.name, strong)
            return True
        weak = _SPELL_TO_SPEC_WEAK.get(spell_id)
        if weak is not None and not unit.spec_locked and unit.spec != weak:
            unit.spec = weak
            log.info("Combat-канал: %s предположительно %s", unit.name, weak)
            return True
        return False

    def _emit_arena_start(self) -> str | None:
        """ARENA_START-payload; None, если состав ВРАГОВ не изменился.

        Дедуп по врагам, а не по всему payload: раскрытие класса союзника
        меняет allies-часть, но DM показывает только врагов — повтор выглядел
        бы дублем «Арена началась» (наблюдалось на живом тесте 2026-07-23).
        """
        team = max(len(self._allies), 1)
        bracket = f"{team}v{team}" if team in (2, 3, 5) else "unknown"
        enemies = ",".join(_encode_enemy(u) for u in self._enemies.values() if u.wow_class)
        if self._last_enemies_key is not None and enemies == self._last_enemies_key:
            return None
        self._last_enemies_key = enemies
        allies_units = sorted(
            self._allies.values(),
            key=lambda u: (u.name != self.player_name, u.name),
        )
        allies = ",".join(f"{u.wow_class}/UNKNOWN" for u in allies_units if u.wow_class)
        return f"ARENA_START#{bracket}#{enemies}#{allies}"


# ── Tail файла ───────────────────────────────────────────────────────────────


def find_combat_log(log_dir: Path) -> Path | None:
    """Свежий combat-лог: WoWCombatLog-*.txt / WoWCombatLog.txt, max по mtime."""
    candidates = list(log_dir.glob("WoWCombatLog*.txt"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


class CombatTailer:
    """Асинхронный tail combat-лога (аналог ChatTailer, тот же контракт stop())."""

    def __init__(self, log_dir: Path, poll_interval: float = 0.5) -> None:
        self._log_dir = log_dir
        self._poll = poll_interval
        self._running = True
        self._file_recheck_s = 5.0

    def stop(self) -> None:
        self._running = False

    async def lines(self) -> AsyncIterator[str]:
        """Асинхронный генератор сырых строк combat-лога."""
        current: Path | None = None
        offset = 0
        buf = ""
        since_recheck = 0.0

        while self._running:
            if current is None or since_recheck >= self._file_recheck_s:
                since_recheck = 0.0
                newest = find_combat_log(self._log_dir)
                if newest is not None and newest != current:
                    current = newest
                    offset = current.stat().st_size  # хвост: только новые события
                    buf = ""
                    log.info("Combat-канал: открыт %s (позиция %d)", current.name, offset)

            if current is None:
                await asyncio.sleep(self._poll)
                since_recheck += self._poll
                continue

            try:
                size = current.stat().st_size
                if size < offset:  # файл усечён/пересоздан
                    offset = 0
                    buf = ""
                if size > offset:
                    with current.open("r", encoding="utf-8", errors="replace") as fh:
                        fh.seek(offset)
                        chunk = fh.read(size - offset)
                        offset = fh.tell()
                    buf += chunk
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        if line.strip():
                            yield line
            except FileNotFoundError:
                current = None

            await asyncio.sleep(self._poll)
            since_recheck += self._poll
