"""Постматч-анализ (Phase 4.3): разбор боя после ARENA_END.

Pipeline копит таймлайн событий матча (TRINKET / ABILITY врагов с таймстампами)
в in-memory MatchRecorder'е, а на ARENA_END строит текстовый разбор:

  • длительность боя (по hostile-активности) и состав врагов;
  • хронология тринкетов врагов (мм:сс от ворот);
  • дефы врагов с таймстампами (evasion / ice block / bubble / …);
  • CC врагов агрегатом (fear ×3, polymorph ×2, …);
  • сравнение с KB-планом: килл-таргет, «If enemy trinkets», «Common mistakes».

Ключ записи — player_name (у игрока один активный матч), а НЕ session_id:
bridge ≤ v0.4.1 строит ARENA_END-envelope ПОСЛЕ session.end_session(), поэтому
session_id в нём уже свежесгенерённый и матч по нему не найти. Keying по имени
делает постматч совместимым со всеми задеплоенными бриджами.

Запись событий происходит ДО хинт-фильтров pipeline'а: CC-касты (kidney, fear,
polymorph …) в реалтайме намеренно не хинтятся, но в разбор боя попадают.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from arena_coach.kb.schema import KBDoc, Section

log = logging.getLogger(__name__)

# Сколько максимум событий пишем на матч (защита от мусорных логов)
_MAX_EVENTS_PER_MATCH = 300
# Записи старше этого возраста чистятся при следующем start()
_RECORD_TTL_S = 2 * 60 * 60.0
# Максимум одновременно открытых записей (игроков)
_MAX_OPEN_RECORDS = 32

# Классификация spell_key'ев для группировки в отчёте.
# Ключи совпадают с TRACKED_SPELLS бриджа/аддона.
_DEFENSIVE_KEYS = {
    "evasion",
    "cloak_of_shadows",
    "vanish",
    "preparation",
    "ice_block",
    "divine_shield",
    "shield_wall",
    "retaliation",
    "pain_suppression",
    "power_infusion",
    "bloodlust",
    "elemental_mastery",
    "innervate",
    "barkskin",
    "blind",
}
_CC_KEYS = {
    "kidney_shot",
    "cheap_shot",
    "sap",
    "polymorph",
    "fear",
    "death_coil",
    "cyclone",
    "psychic_scream",
    "hammer_of_justice",
    "frost_nova",
    "intimidating_shout",
    "challenging_shout",
    "counterspell",
    "blessing_of_freedom",
}

_ABILITY_REF_RE = re.compile(r"\[\[ability:([a-z0-9-]+)\]\]")


def parse_bridge_ts(raw: str) -> datetime | None:
    """ISO8601 из envelope.bridge_ts ('...Z') → datetime; None при мусоре."""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def utcnow() -> datetime:
    """Текущее UTC-время (fallback, когда bridge_ts не распарсился)."""
    return datetime.now(timezone.utc)


def _fmt_offset(seconds: float) -> str:
    """41.7 → '0:41'; 272.0 → '4:32'."""
    total = max(0, int(seconds))
    return f"{total // 60}:{total % 60:02d}"


def _pretty_key(key: str) -> str:
    """'ice_block' → 'ice block' (игроки знают термины, подчёркивания — шум)."""
    return key.replace("_", " ")


def _clean_kb_text(text: str, limit: int) -> str:
    """Убрать [[ability:x]]-обёртки и маркдаун-заголовки, обрезать до limit."""
    cleaned = _ABILITY_REF_RE.sub(lambda m: m.group(1).replace("-", " "), text)
    cleaned = re.sub(r"^_Провенанс:.*?_\s*$", "", cleaned, flags=re.MULTILINE | re.DOTALL)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if len(cleaned) > limit:
        cleaned = cleaned[: limit - 1].rstrip() + "…"
    return cleaned


# ── Модель записи ────────────────────────────────────────────────────────────


@dataclass
class RecordedEvent:
    """Одно событие врага внутри матча."""

    offset_s: float  # секунды от ARENA_START
    kind: str  # "TRINKET" | "ABILITY"
    source: str  # имя врага
    key: str  # trinket_key / spell_key


@dataclass
class MatchRecord:
    """Копилка одного матча (per player)."""

    player_name: str
    session_id: str
    started_at: datetime
    bracket: str = "unknown"
    enemies: list[dict[str, str]] = field(default_factory=list)
    our_comp_hint: str | None = None
    events: list[RecordedEvent] = field(default_factory=list)
    last_event_at: datetime | None = None
    dropped_events: int = 0

    @property
    def enemy_classes(self) -> list[str]:
        return [e.get("wow_class", "") for e in self.enemies if e.get("wow_class")]

    @property
    def enemies_label(self) -> str:
        return ", ".join(self.enemy_classes) or "?"

    def duration_s(self) -> float:
        """Длительность по последней hostile-активности (ARENA_END приходит
        на ~90с позже реального конца — quiet-таймаут бриджа)."""
        if self.last_event_at is None:
            return 0.0
        return max(0.0, (self.last_event_at - self.started_at).total_seconds())


class MatchRecorder:
    """In-memory копилка матчей: player_name → MatchRecord."""

    def __init__(self) -> None:
        self._records: dict[str, MatchRecord] = {}

    def __len__(self) -> int:
        return len(self._records)

    def start(
        self,
        player_name: str,
        session_id: str,
        ts: datetime,
        bracket: str,
        enemies: list[dict[str, str]],
        our_comp_hint: str | None,
    ) -> None:
        """ARENA_START: открыть запись; re-emit той же сессии — обновить состав.

        Re-emit (враг вышел из стелса / класс уточнился по кастам) сохраняет
        started_at и уже накопленные события.
        """
        self._purge(ts)
        key = player_name.lower()
        existing = self._records.get(key)
        if existing is not None and existing.session_id == session_id:
            existing.bracket = bracket or existing.bracket
            existing.enemies = list(enemies) or existing.enemies
            existing.our_comp_hint = our_comp_hint or existing.our_comp_hint
            return
        if existing is None and len(self._records) >= _MAX_OPEN_RECORDS:
            oldest = min(self._records, key=lambda k: self._records[k].started_at)
            del self._records[oldest]
        self._records[key] = MatchRecord(
            player_name=player_name,
            session_id=session_id,
            started_at=ts,
            bracket=bracket,
            enemies=list(enemies),
            our_comp_hint=our_comp_hint,
        )

    def note(self, player_name: str, ts: datetime, kind: str, source: str, key: str) -> None:
        """TRINKET/ABILITY: дописать событие в открытую запись игрока."""
        record = self._records.get(player_name.lower())
        if record is None:
            return  # событие до ARENA_START (fallback-uuid сессия) — не пишем
        record.last_event_at = ts
        if len(record.events) >= _MAX_EVENTS_PER_MATCH:
            record.dropped_events += 1
            return
        offset = max(0.0, (ts - record.started_at).total_seconds())
        record.events.append(RecordedEvent(offset_s=offset, kind=kind, source=source, key=key))

    def finish(self, player_name: str) -> MatchRecord | None:
        """ARENA_END: изъять запись игрока (None, если матча не было)."""
        return self._records.pop(player_name.lower(), None)

    def _purge(self, now: datetime) -> None:
        stale = [
            k
            for k, r in self._records.items()
            if (now - r.started_at).total_seconds() > _RECORD_TTL_S
        ]
        for k in stale:
            log.info("Постматч: запись %s протухла без ARENA_END — удаляю", k)
            del self._records[k]


# ── Построение отчёта ────────────────────────────────────────────────────────


def _find_section(doc: KBDoc, needles: list[str]) -> Section | None:
    for needle in needles:
        low = needle.lower()
        for sec in doc.sections:
            if low in sec.title.lower():
                return sec
    return None


def _group_lines(record: MatchRecord) -> list[str]:
    """Сгруппированные строки таймлайна: тринкеты, дефы, CC, прочее."""
    trinkets: list[str] = []
    defensives: dict[str, list[str]] = {}
    cc_counts: dict[str, int] = {}
    other_counts: dict[str, int] = {}

    for ev in record.events:
        stamp = _fmt_offset(ev.offset_s)
        if ev.kind == "TRINKET":
            trinkets.append(f"{ev.source} {stamp}")
        elif ev.key in _DEFENSIVE_KEYS:
            defensives.setdefault(f"{ev.source}: {_pretty_key(ev.key)}", []).append(stamp)
        elif ev.key in _CC_KEYS:
            cc_counts[_pretty_key(ev.key)] = cc_counts.get(_pretty_key(ev.key), 0) + 1
        else:
            other_counts[_pretty_key(ev.key)] = other_counts.get(_pretty_key(ev.key), 0) + 1

    lines: list[str] = []
    if trinkets:
        lines.append(f"💎 **Тринкеты врагов ({len(trinkets)})**: " + " · ".join(trinkets))
    else:
        lines.append("💎 Тринкеты врагов: не замечены — вероятно, оба ещё на КД в конце боя")
    if defensives:
        parts = [f"{who} {', '.join(stamps)}" for who, stamps in defensives.items()]
        lines.append("🛡 **Дефы врагов**: " + " · ".join(parts))
    if cc_counts:
        parts = [f"{key} ×{n}" for key, n in sorted(cc_counts.items(), key=lambda kv: -kv[1])]
        lines.append("✋ **CC врагов**: " + " · ".join(parts))
    if other_counts:
        parts = [f"{key} ×{n}" for key, n in sorted(other_counts.items(), key=lambda kv: -kv[1])]
        lines.append("🔎 Прочее: " + " · ".join(parts))
    if record.dropped_events:
        lines.append(f"…ещё {record.dropped_events} событий не записано (кап таймлайна)")
    return lines


def timeline_digest(record: MatchRecord, limit: int = 900) -> str:
    """Компактный текст таймлайна для LLM-разбора (Phase 4.7).

    Отдаёт факты боя (тринкеты/дефы/CC/прочее с таймстампами) без markdown-эмодзи —
    вход для модели, а не для игрока. Отдельно от build_postmatch_report, чтобы
    детерминированный отчёт остался фолбэком.
    """
    head = (
        f"Брекет: {record.bracket}. Враги: {record.enemies_label}. "
        f"Наш состав: {record.our_comp_hint or '?'}. "
        f"Длительность ~{_fmt_offset(record.duration_s())}. "
        f"Событий: {len(record.events)}."
    )
    lines = [head]
    for ev in record.events:
        lines.append(f"  {_fmt_offset(ev.offset_s)} {ev.kind.lower()} {ev.source}: {ev.key}")
    text = "\n".join(lines)
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def build_postmatch_report(record: MatchRecord, doc: KBDoc | None) -> str:
    """Собрать текст DM-разбора (≤2000 символов, лимит Discord)."""
    matchup = f"{doc.composition} vs {doc.vs}" if doc else None
    header_mid = f"`{matchup}`" if matchup else f"враги: {record.enemies_label}"
    duration = record.duration_s()
    dur_part = f" | ⏱ ~{_fmt_offset(duration)}" if duration >= 5 else ""
    lines: list[str] = [
        f"🏁 **Разбор боя** | {header_mid} | {record.bracket}{dur_part}",
        f"👥 Враги: {record.enemies_label} | событий записано: {len(record.events)}",
        "",
    ]
    lines.extend(_group_lines(record))

    if doc is not None:
        lines.append("")
        kt = doc.kill_target
        kt_line = f"🎯 **KB-план был**: килл-таргет **{kt.primary}**"
        if kt.fallback:
            kt_line += f" (запасной: {kt.fallback})"
        kt_line += f", сложность {doc.difficulty.value}"
        lines.append(kt_line)

        had_trinket = any(ev.kind == "TRINKET" for ev in record.events)
        if had_trinket:
            sec = _find_section(doc, ["If enemy trinkets", "Post-trinket", "After trinket"])
            if sec is not None:
                lines.append(f"📌 **После тринкета (KB)**: {_clean_kb_text(sec.body_md, 350)}")

        mistakes = _find_section(doc, ["Common mistakes"])
        if mistakes is not None:
            lines.append(
                f"⚠️ **Сверь с типовыми ошибками (KB)**: {_clean_kb_text(mistakes.body_md, 350)}"
            )
        lines.append("")
        lines.append(f"📖 `/matchup our:{doc.composition} vs:{doc.vs}` — полный разбор")
    else:
        lines.append("")
        lines.append(
            "📚 Матчапа в KB нет — разбор только по таймлайну. `/list_comps` покажет покрытие."
        )

    report = "\n".join(lines)
    if len(report) > 2000:
        report = report[:1997] + "…"
    return report
