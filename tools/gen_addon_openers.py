#!/usr/bin/env python3
"""Компилятор KB → тактический колаут на воротах (Phase 4.20).

Зачем. Читать тактику в DM во время боя невозможно — её надо слышать, а состав
врага до открытия ворот в 2.4.3 узнать нельзя (`arena1` в prep-фазе пуст, события
`ARENA_PREP_OPPONENT_SPECIALIZATIONS` в клиенте нет). Значит тактика начинает
звучать РОВНО в момент ворот, и на неё есть 8-10 секунд — пока команды сходятся.

Почему клипы, а не TTS через мост: замер 30.07 (память: log-buffer-48kb) — клиент
сбрасывает combat-лог блоками ~48КБ, поэтому мост в бою опаздывает на 13-28с
СТРУКТУРНО. Ворота — самая тихая точка матча, там окно максимальное. Поэтому
фразы нарезаются заранее, по одной на матчап, и лежат в аддоне рядом с
`KillTargets.lua`, который уже решает килл-таргет локально из `UnitClass`.

Что генератор берёт из KB (факты) и что задано таблицами (формулировки):

| Слот | Откуда факт | Откуда слова |
|---|---|---|
| цель | frontmatter `kill_target.primary` | `_ACC` (винительный сленг) |
| сап/пре-цель | `## Opener`, `[[ability:sap]] <кого>` | `_ACC` |
| опен-комбо | `## Opener`, цепочка `[[a]] → [[b]]` | `_VOICE` (сленг-словарь) |
| кик | `## Opener`, «кикаешь …» | `_VOICE` |
| угроза | первая из `_DANGERS`, встреченная в документе | `_DANGERS` |

То есть ЧТО сказать решает KB, а КАК — вычитанные Владом таблицы. Отсюда и тон:
колаут напарника, а не зачитанный гайд.

Бюджет (Phase 4.17, tests/test_voice_budget.py): 2.8 слога/сек. Первая фраза —
цель, ≤`MAX_FIRST` слогов: игрок действует на первом слове. Весь колаут —
≤`MAX_TOTAL` слогов, лишние слоты отбрасываются с хвоста, а не режутся посередине.

    python tools/gen_addon_openers.py --dry-run          # только тексты, таблицей
    python tools/gen_addon_openers.py --dry-run --md     # то же в Markdown (на вычитку)
    python tools/gen_addon_openers.py                    # Openers.lua + манифест
    python tools/gen_addon_openers.py --check            # свежесть сгенерированного
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "backend"))

from arena_coach.kb.indexer import comp_part_to_class, comp_to_classes  # noqa: E402
from arena_coach.kb.loader import KBLoadError, load_kb_doc  # noqa: E402
from arena_coach.kb.pronunciation import Pronouncer  # noqa: E402

KB_DIRS = ("kb/drafts", "kb/matchups")
OUT_LUA = REPO / "addon" / "ArenaCoach" / "Openers.lua"
OUT_MANIFEST = REPO / "addon" / "ArenaCoach" / "sfx" / "openers.json"

# ── Бюджет речи (Phase 4.17) ────────────────────────────────────────────────
_VOWELS = "аеёиоуыэюя"
SYLLABLES_PER_SEC = 2.8
MAX_FIRST = 8  # ≈2.9с — цель обязана прозвучать в первой фразе
MAX_TOTAL = 26  # ≈9.3с — окно ворот, пока команды сходятся


def syllables(text: str) -> int:
    return sum(1 for ch in text.lower() if ch in _VOWELS)


def seconds(text: str) -> float:
    return syllables(text) / SYLLABLES_PER_SEC


# ── Словари формулировок (ВЫЧИТЫВАЮТСЯ ВЛАДОМ) ──────────────────────────────

#: Класс → винительный падеж на сленге: «бей кого».
_ACC: dict[str, str] = {
    "priest": "приста",
    "mage": "мага",
    "warlock": "лока",
    "druid": "друида",
    "shaman": "шама",
    "hunter": "ханта",
    "rogue": "рогу",
    "warrior": "вара",
    "paladin": "палу",
}

#: ability-slug → как это зовут вслух. Короткое побеждает точное: слог = 0.36с.
_VOICE: dict[str, str] = {
    "sap": "сап",
    "cheap-shot": "чип",
    "kidney-shot": "кидни",
    "shadowstep": "степ",
    "garrote": "гарота",
    "gouge": "гадж",
    "blind": "блайнд",
    "hemo": "хема",
    "shiv": "шив",
    "cloak-of-shadows": "клоак",
    "vanish": "ваниш",
    "preparation": "преп",
    "premed": "премед",
    "evisc": "эвис",
    "cyclone": "циклон",
    "entangling-roots": "корни",
    "natures-swiftness": "энэс",
    "barkskin": "кору",
    "innervate": "иннерв",
    "lifebloom": "лб",
    "rejuvenation": "реджув",
    "sheep": "овца",
    "polymorph": "овца",
    "nova": "нова",
    "blink": "блинк",
    "counterspell": "кс",
    "spell-lock": "локк",
    "fear": "фир",
    "howl-of-terror": "хаул",
    "seduction": "седа",
    "death-coil": "коил",
    "mana-burn": "бёрн",
    "curse-of-tongues": "тангс",
    "pain-suppression": "саппресс",
    "psychic-scream": "скрим",
    "hammer-of-justice": "подж",
    "repentance": "репент",
    "scatter-shot": "скаттер",
    "viper-sting": "вайпер",
    "grounding-totem": "гроунд",
    "devour-magic": "девор",
    "purge": "пурж",
    "dispel": "дисп",
    "trinket": "тринка",
    "kidney": "кидни",
    "hibernate": "хибер",
    "banish": "баниш",
    "faerie-fire": "фери",
    "natures-grasp": "грасп",
    "blessing-of-freedom": "фридом",
    "travel-form": "тревел",
    "kick": "кик",
}

#: Угрозы: (что искать в документе, как это выкрикнуть). Порядок = приоритет —
#: озвучиваем ОДНУ, ту, что чаще всего решает первые секунды. Формулировка —
#: императив, чтобы игрок не «понимал», а делал.
#: Формат: (класс-владелец, что искать, как выкрикнуть). Владелец обязателен —
#: без него «Не кучкуйся» вылезало на нашу же нову: слово `nova` есть в документе
#: и когда маг НАШ. Угроза озвучивается только если класс есть у ВРАГА.
_DANGERS: list[tuple[str, str, str]] = [
    ("hunter", r"Freezing Trap|freezing-trap", "Трап не жри."),
    ("hunter", r"ability:viper-sting", "Вайпер — в лос."),
    ("hunter", r"Deterrence", "В детер не бей."),
    ("mage", r"ability:nova", "Не кучкуйся."),
    ("priest", r"ability:mana-burn", "Бёрн — в лос."),
    ("priest", r"ability:pain-suppression", "Жди пэ-эс."),
    ("priest", r"ability:psychic-scream", "Скрим — не кучно."),
    ("shaman", r"ability:grounding-totem", "Сбей гроунд."),
    ("warlock", r"ability:devour-magic", "Девор — фейкай."),
    ("warlock", r"ability:fear|ability:howl-of-terror", "Фир — в лос."),
    ("paladin", r"Wings|Avenging Wrath", "Крылья — тринка."),
    ("paladin", r"Divine Shield|бабл", "Бабл — не сливай."),
    ("mage", r"Ice Block|ability:ice-block", "Блок — не сливай."),
    #: Без тире осознанно: тире у RHVoice = долгая пауза, и колаут RD vs Hunter/RDruid
    #: (5.3с) вылезал за 30%-допуск слоговой модели (tests/test_addon_openers.py).
    ("druid", r"ability:cyclone", "Циклон за столб."),
    ("rogue", r"ability:blind", "Блайнд — тринка."),
    ("warrior", r"Retaliation|ретка", "Ретка вара — не бей."),
]

#: Что в цепочке — контроль (сетап) или урон (добив). Цепочка `нова → овца`
#: идёт по ДРУГОМУ юниту, чем `чип → кидни`, поэтому и слоты разные.
_CC_SLUGS = {
    "sap", "sheep", "polymorph", "nova", "fear", "cyclone", "blind", "gouge",
    "hammer-of-justice", "scatter-shot", "psychic-scream", "entangling-roots",
    "seduction", "banish", "repentance", "howl-of-terror", "counterspell",
    "spell-lock", "hibernate",
}
_DMG_SLUGS = {
    "premed", "cheap-shot", "kidney-shot", "kidney", "hemo", "garrote", "evisc",
    "shiv", "shadowstep", "ambush", "backstab", "rupture", "mutilate",
}

#: Ручные колауты для матчапов, где KB описывает связку ПРОЗОЙ, а не цепочкой со
#: стрелками («[[ability:cheap-shot]] варлока в [[ability:gouge]]»). Генератор их не
#: собирает и вырождается в «Бей X!» — то есть в фолбэк 4.19. Факты взяты из самих
#: документов, формулировки вычитаны. Ключ — тот же, что у сгенерированных.
_OVERRIDES: dict[str, str] = {
    # сап палы, mana-burn вынуждает grounding+shock; рог держит рета в crippling+wound
    "2v2|priest+rogue|paladin+shaman": "Бей палу! Бёрн ману, вунды на рета.",
    # win-con документа — OOM паладина манабёрном; cleanse палы снимает яды → ре-шив
    "2v2|priest+rogue|paladin+warlock": "Сап палу, бей лока! Бёрн палу в оом.",
    # сап их приста, cheap-shot в gouge, kidney из gouge, 5 вундов весь матч
    "2v2|priest+rogue|priest+warlock": "Сап приста, бей лока! Чип, гадж, кидни. Держи вунды.",
    # рог не даёт дистанцию: garrote-силенс → чип/кидни; главная угроза — viper на присте
    "2v2|priest+rogue|hunter+paladin": "Бей ханта! Гарота, чип, кидни. Вайпер — в лос.",
    # у RM нет манабёрна → играем от бёрст-окон, кс на хил палы, бёрст без freedom/bubble
    "2v2|mage+rogue|paladin+warlock": "Бей лока! Кс хил палы, шаттер-бёрст. Не сливай в бабл.",
    # Phase 4.21.1: спек-схлопывание после драфтов rm-vs-rogue-feral / rm-vs-retpala-rogue.
    # Алфавитный выбор отдавал ключ редкому спек-варианту и ТЕРЯЛ сап/бабл-предупреждение.
    # До спек-детекта по аурам (бэклог 4.22) ключ держит мета-вариант: факты — из
    # rm-vs-rogue-rdruid и rm-vs-rogue-hpala, чьи колауты тут дословно.
    "2v2|mage+rogue|druid+rogue": "Сап друида, бей рогу! Премед, чип, кидни.",
    "2v2|mage+rogue|paladin+rogue": "Бей рогу! Чип, кидни. Бабл — не сливай.",
}

_ABILITY_RE = re.compile(r"\[\[ability:([a-z0-9-]+)\]\]")
_CHAIN_RE = re.compile(
    r"\[\[ability:[a-z0-9-]+\]\](?:\s*→\s*\[\[ability:[a-z0-9-]+\]\])+"
)
_SAP_RE = re.compile(r"\[\[ability:sap\]\]\s*(?:на\s+)?(?:их\s+)?\*{0,2}([\w']+)")
_KICK_RE = re.compile(r"кика(?:ешь|й|ем)\s+([^;.]{0,80})", re.IGNORECASE)

#: Слова из KB-прозы → класс. KB писана вживую: падежи RU и транслит
#: («shaman'а», «ret'е») встречаются в одном абзаце, поэтому обе формы.
_WORD_TO_CLASS: dict[str, str] = {
    "приста": "priest", "прист": "priest", "присту": "priest", "priest": "priest",
    "мага": "mage", "маг": "mage", "магу": "mage", "mage": "mage",
    "лока": "warlock", "лок": "warlock", "локу": "warlock", "warlock": "warlock",
    "друида": "druid", "друид": "druid", "друиду": "druid", "druid": "druid",
    "шамана": "shaman", "шаман": "shaman", "шаму": "shaman", "шама": "shaman",
    "shaman": "shaman",
    "ханта": "hunter", "хант": "hunter", "ханту": "hunter", "hunter": "hunter",
    "рога": "rogue", "рогу": "rogue", "рог": "rogue", "rogue": "rogue",
    "вара": "warrior", "вар": "warrior", "воина": "warrior", "warrior": "warrior",
    "палу": "paladin", "пал": "paladin", "рета": "paladin", "рет": "paladin",
    "paladin": "paladin", "ret": "paladin", "pala": "paladin",
    "пета": "pet", "пет": "pet",
}

#: «Кик <что>» требует винительного: «Кик овцу», а не «Кик овца».
_KICK_ACC: dict[str, str] = {
    "овца": "овцу", "нова": "нову", "хема": "хему", "гарота": "гароту",
    "кора": "кору", "тринка": "тринку",
}


# ── Разбор KB ───────────────────────────────────────────────────────────────


def _docs() -> list[object]:
    out = []
    for rel in KB_DIRS:
        d = REPO / rel
        if not d.exists():
            continue
        for path in sorted(d.glob("*.md")):
            try:
                out.append(load_kb_doc(path))
            except KBLoadError as exc:
                print(f"⚠️  пропускаю {path.name}: {exc}", file=sys.stderr)
    return out


def _section(doc, *titles: str) -> str:
    want = {t.lower() for t in titles}
    return "\n".join(s.body_md for s in doc.sections if s.title.strip().lower() in want)


def _full_text(doc) -> str:
    return "\n".join(s.body_md for s in doc.sections)


def _class_after(text: str, pos: int, window: int = 60) -> str | None:
    """Первый класс, упомянутый в `window` символов после `pos`.

    Нужно, чтобы понять, ПО КОМУ идёт контроль: «нова → овца shaman'а» — по шаману,
    а бить при этом надо паладина. Без этого колаут звучал бы «бей палу! нова, овца»
    и игрок бил бы не туда.
    """
    tail = re.sub(r"\[\[ability:[a-z0-9-]+\]\]", " ", text[pos : pos + window])
    for word in re.findall(r"[A-Za-zА-Яа-яё]+", tail):
        cls = _WORD_TO_CLASS.get(word.lower())
        if cls and cls in _ACC:
            return cls
    return None


def _sap_target(opener: str) -> str | None:
    """«Рог [[ability:sap]] приста» → 'priest'. Ранний сап — половина опенера."""
    m = _SAP_RE.search(opener)
    if not m:
        return None
    cls = _WORD_TO_CLASS.get(m.group(1).lower().strip("'"))
    if cls in _ACC:
        return cls
    return _class_after(opener, m.end())


def _chains(opener: str) -> tuple[list[str], tuple[list[str], str | None]]:
    """(комбо на добив, (цепочка контроля, по кому)).

    Комбо берём ПОСЛЕДНЕЕ и самое длинное из урона: в KB первым абзацем часто идёт
    сетап («сап под сакрифайс»), а рабочая связка описана ниже.
    """
    dmg: list[str] = []
    cc: tuple[list[str], str | None] = ([], None)
    for m in _CHAIN_RE.finditer(opener):
        slugs = _ABILITY_RE.findall(m.group(0))
        words = [_VOICE[s] for s in slugs if s in _VOICE]
        # dedup с сохранением порядка: «чип → хема → кидни → хема»
        words = list(dict.fromkeys(words))
        if not words:
            continue
        if all(s in _CC_SLUGS for s in slugs):
            if not cc[0]:
                cc = (words, _class_after(opener, m.end()))
        elif any(s in _DMG_SLUGS for s in slugs) and len(words) >= len(dmg):
            dmg = words
    return dmg, cc


def _kick(opener: str) -> str | None:
    """«кикаешь [[ability:sheep]]/[[ability:nova]]» → 'овцу'; «кикаешь хил» → 'хил'."""
    m = _KICK_RE.search(opener)
    if not m:
        return None
    span = m.group(1)
    for slug in _ABILITY_RE.findall(span):
        word = _VOICE.get(slug)
        if word:
            return _KICK_ACC.get(word, word)
    if re.search(r"\bхил", span, re.IGNORECASE):
        return "хил"
    return None


def _danger(text: str, enemy_classes: set[str], target_cls: str) -> str | None:
    for owner, pattern, phrase in _DANGERS:
        if owner not in enemy_classes:
            continue
        # Про килл-таргета и так всё сказано первой фразой — предупреждаем о ВТОРОМ.
        if owner == target_cls and len(enemy_classes) > 1:
            continue
        if re.search(pattern, text, re.IGNORECASE):
            return phrase
    return None


# ── Сборка колаута ──────────────────────────────────────────────────────────


def build_callout(doc) -> tuple[str, list[str]]:
    """(текст колаута, список отброшенных по бюджету слотов)."""
    opener = _section(doc, "opener", "strategy", "stealth game", "general")
    whole = _full_text(doc)

    target_cls = comp_part_to_class(str(doc.kill_target.primary))
    target = _ACC.get(target_cls, target_cls)
    enemies = set(comp_to_classes(doc.vs))

    # Сап/контроль применимы только к ВРАГУ: в прозе рядом с «сап» часто стоит наш
    # же класс («рог сапает», «маг ждёт»), и без этой проверки колаут велел «сап
    # мага» в матчапе, где мага у врага нет вообще.
    sap_cls = _sap_target(opener)
    if sap_cls not in enemies:
        sap_cls = None
    combo, (cc_words, cc_cls) = _chains(opener)
    if cc_cls not in enemies:
        cc_cls = None
    kick = _kick(opener)
    danger = _danger(whole, enemies, target_cls)

    # Слоты в порядке ценности: цель → чем открываем → что кикать → чего не делать.
    slots: list[tuple[str, str]] = []
    # Пре-действие в первой фразе: контроль второго врага важнее сапа (сап — способ,
    # контроль — цель), но и то и другое звучит ДО «бей», потому что нажимается до.
    pre = ""
    if cc_words and cc_cls and cc_cls != target_cls:
        pre = f"{cc_words[-1].capitalize()} {_ACC[cc_cls]}, "
    elif sap_cls and sap_cls != target_cls:
        pre = f"Сап {_ACC[sap_cls]}, "
    head = f"{pre}бей {target}!" if pre else f"Бей {target}!"
    slots.append(("head", head))
    if combo:
        slots.append(("combo", ", ".join(combo).capitalize() + "."))
    if kick:
        slots.append(("kick", f"Кик {kick}."))
    if danger:
        slots.append(("danger", danger))

    kept: list[str] = []
    dropped: list[str] = []
    for name, phrase in slots:
        candidate = " ".join([*kept, phrase])
        if syllables(candidate) > MAX_TOTAL:
            dropped.append(name)
            continue
        kept.append(phrase)
    return " ".join(kept), dropped


# ── Ключи и файлы ───────────────────────────────────────────────────────────


def _key(doc) -> str | None:
    ours = "+".join(comp_to_classes(doc.composition))
    theirs = "+".join(comp_to_classes(doc.vs))
    if not ours or not theirs:
        return None
    bracket = getattr(doc.bracket, "value", str(doc.bracket))
    return f"{bracket}|{ours}|{theirs}"


def clip_name(key: str) -> str:
    """'2v2|druid+rogue|mage+priest' → 'op_2v2_druid-rogue_mage-priest'."""
    return "op_" + key.replace("|", "_").replace("+", "-")


def build_table() -> tuple[dict[str, dict], list[str]]:
    """ключ → {text, clip, slugs, sure}; плюс список предупреждений."""
    per_key: dict[str, list[tuple[str, str]]] = defaultdict(list)
    warnings: list[str] = []
    for doc in _docs():
        key = _key(doc)
        if not key:
            continue
        text, dropped = build_callout(doc)
        if dropped:
            warnings.append(f"{doc.slug}: не влезло в бюджет — {', '.join(dropped)}")
        if syllables(text.split("!")[0]) > MAX_FIRST:
            warnings.append(f"{doc.slug}: первая фраза длиннее {MAX_FIRST} слогов")
        per_key[key].append((doc.slug, text))

    table: dict[str, dict] = {}
    for key, items in sorted(per_key.items()):
        if key in _OVERRIDES:
            table[key] = {
                "text": _OVERRIDES[key],
                "clip": clip_name(key),
                "slugs": sorted(s for s, _ in items),
                "sure": True,
                "manual": True,
            }
            continue
        texts = {t for _, t in items}
        # Схлопывание спеков в классы: если документы под одним ключом дают разные
        # колауты — берём алфавитно первый и честно помечаем неуверенность
        # (ровно как gen_addon_killtargets поступает с целью).
        text = sorted(texts)[0]
        table[key] = {
            "text": text,
            "clip": clip_name(key),
            "slugs": sorted(s for s, _ in items),
            "sure": len(texts) == 1,
            "manual": False,
        }
        if len(texts) > 1:
            warnings.append(f"{key}: {len(texts)} разных колаута после схлопывания спеков")
    for key in _OVERRIDES:
        if key not in table:
            warnings.append(f"_OVERRIDES: ключа {key} нет в KB — правка ни на что не влияет")
    return table, warnings


LUA_HEADER = """-- ArenaCoach/Openers.lua
-- СГЕНЕРИРОВАНО tools/gen_addon_openers.py — не редактировать руками.
-- Источник: kb/drafts + kb/matchups (kill_target + секция Opener).
--
-- Тактический колаут на воротах. Ключ тот же, что у KillTargets.lua:
-- "<bracket>|<наши классы>|<классы врагов>", sorted+lowercase.
-- Значение: { c = "имя клипа без .ogg", t = "текст (для панели и /ac say)" }.
-- Нет ключа → фолбэк: «Бей <класс>!» из Voice.lua + угрозы (поведение 4.19).

local AC = ArenaCoach

AC.KB_OPENERS = {
"""

LUA_FOOTER = """}

AC.KB_OPENERS_COUNT = %d
"""


def render_lua(table: dict[str, dict]) -> str:
    parts = [LUA_HEADER]
    for key, row in table.items():
        text = row["text"].replace('"', "'")
        parts.append(f'    ["{key}"] = {{ c = "{row["clip"]}", t = "{text}" }},\n')
    parts.append(LUA_FOOTER % len(table))
    return "".join(parts)


def render_manifest(table: dict[str, dict]) -> str:
    """Манифест «ключ → файл»: по нему генератор клипов знает, что синтезировать."""
    pron = Pronouncer.from_kb_path(REPO / "kb")
    payload = {
        "_comment": (
            "СГЕНЕРИРОВАНО tools/gen_addon_openers.py. clip — файл в sfx/ без .ogg, "
            "text — что произносится, say — текст после Pronouncer (что уходит в TTS)."
        ),
        "syllables_per_sec": SYLLABLES_PER_SEC,
        "clips": {
            key: {
                "clip": row["clip"],
                "text": row["text"],
                "say": pron.apply(row["text"]) if hasattr(pron, "apply") else row["text"],
                "syllables": syllables(row["text"]),
                "seconds": round(seconds(row["text"]), 1),
                "sure": row["sure"],
                "manual": row.get("manual", False),
                "kb": row["slugs"],
            }
            for key, row in table.items()
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


# ── CLI ─────────────────────────────────────────────────────────────────────


def _print_table(table: dict[str, dict], markdown: bool) -> None:
    if markdown:
        print("| Матчап (наши vs враги) | Колаут | Слогов | ≈сек |")
        print("|---|---|---:|---:|")
        for key, row in table.items():
            bracket, ours, theirs = key.split("|")
            mark = "" if row["sure"] else " ⚠️"
            print(
                f"| {bracket} {ours} vs {theirs}{mark} | «{row['text']}» "
                f"| {syllables(row['text'])} | {seconds(row['text']):.1f} |"
            )
        return
    for key, row in table.items():
        print(f"{seconds(row['text']):4.1f}с {syllables(row['text']):3d}сл  {key}")
        print(f"        «{row['text']}»")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="только показать тексты")
    ap.add_argument("--md", action="store_true", help="вывод Markdown-таблицей")
    ap.add_argument("--check", action="store_true", help="сверить сгенерированное с репо")
    args = ap.parse_args()

    table, warnings = build_table()
    for w in warnings:
        print(f"⚠️  {w}", file=sys.stderr)

    if args.dry_run:
        _print_table(table, args.md)
        total = sum(seconds(r["text"]) for r in table.values())
        print(
            f"\n{len(table)} матчапов, медиана "
            f"{sorted(syllables(r['text']) for r in table.values())[len(table) // 2]} слогов, "
            f"суммарно {total:.0f}с речи",
            file=sys.stderr,
        )
        return 0

    lua, manifest = render_lua(table), render_manifest(table)
    if args.check:
        stale = [
            p.relative_to(REPO)
            for p, content in ((OUT_LUA, lua), (OUT_MANIFEST, manifest))
            if not p.exists() or p.read_text(encoding="utf-8") != content
        ]
        if stale:
            print(f"❌ устарело: {', '.join(map(str, stale))}", file=sys.stderr)
            return 1
        print(f"✅ Openers.lua и манифест актуальны ({len(table)} ключей)")
        return 0

    OUT_LUA.write_text(lua, encoding="utf-8")
    OUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OUT_MANIFEST.write_text(manifest, encoding="utf-8")
    unsure = sum(1 for r in table.values() if not r["sure"])
    print(
        f"✅ {len(table)} колаутов → {OUT_LUA.relative_to(REPO)} "
        f"+ {OUT_MANIFEST.relative_to(REPO)} (неуверенных: {unsure})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
