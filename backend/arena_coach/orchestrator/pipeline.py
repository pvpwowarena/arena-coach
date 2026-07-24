"""End-to-end pipeline: bridge event → KB lookup → LLM hint → Discord DM.

Поток данных:
1. POST /v1/events получает CanonicalEnvelope от bridge
2. Валидация bearer-токена
3. Поиск игрока в whitelist по player_name (character) → discord_id
4. KB lookup по КЛАССАМ врагов + нашему составу (Phase 4.1: class-level match,
   спек с ворот не виден → кандидатов может быть несколько)
5. LLM (Haiku) синтезирует краткий совет из нужной KB-секции, таргетированный
   под класс игрока; LLM недоступен → сырой текст секции
6. Отправка Discord DM через REST API

События: ARENA_START (опенер + килл-таргет), TRINKET (post-trinket план),
ABILITY (только ключевые дефы из _ABILITY_HINT_KEYS, с троттлингом).
Нет в KB → generic DM только при ARENA_START, остальное молчим.

Phase 4.3: все TRINKET/ABILITY (включая CC, которые в реалтайме не хинтятся)
пишутся в MatchRecorder; на ARENA_END игроку уходит DM-разбор боя
(таймлайн тринкетов/дефов/CC vs KB-план) — см. orchestrator/postmatch.py.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from anthropic import AsyncAnthropic

from arena_coach.access.player_settings import DEFAULT_VOICE_MODE, PlayerSettingsService
from arena_coach.access.service import AccessService
from arena_coach.kb.retriever import KBRetriever
from arena_coach.kb.schema import KBDoc, Section
from arena_coach.orchestrator.hint_queue import HintQueue
from arena_coach.orchestrator.postmatch import (
    MatchRecorder,
    build_postmatch_report,
    parse_bridge_ts,
    utcnow,
)
from arena_coach.orchestrator.voice_phrases import (
    ability_phrase,
    arena_start_phrase,
    trinket_phrase,
)
from arena_coach.shared.settings import Settings

log = logging.getLogger(__name__)

# Типы событий, на которые вообще отвечаем
_HINT_EVENTS = {"ARENA_START", "TRINKET", "ABILITY"}

# ABILITY-события: подсказываем только на ключевые дефы/бурсты, меняющие план
# (килл-окно или его закрытие). CC-касты (fear/poly/kidney) намеренно исключены:
# подсказка пришла бы уже после того, как CC отработал.
_ABILITY_HINT_KEYS = {
    "evasion",
    "cloak_of_shadows",
    "vanish",
    "preparation",
    "blind",
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
}

# Секции KB, которые ищем для каждого типа события
_SECTION_PRIORITY: dict[str, list[str]] = {
    "ARENA_START": ["Opener", "Alternative opener"],
    "TRINKET": ["If enemy trinkets", "Post-trinket", "After trinket"],
    "ABILITY": ["Key cooldowns to track", "Mid-fight rotation", "Common mistakes"],
    "ARENA_END": ["Common mistakes"],
}


class HintThrottle:
    """Анти-спам для in-fight (ABILITY) подсказок.

    Правила (per discord_id):
      • не чаще одного ABILITY-DM в min_interval_s;
      • одинаковый spell_key не повторяем в течение repeat_window_s.
    ARENA_START и TRINKET не троттлятся — это редкие ключевые события.
    """

    def __init__(self, min_interval_s: float = 20.0, repeat_window_s: float = 60.0) -> None:
        self._min_interval_s = min_interval_s
        self._repeat_window_s = repeat_window_s
        self._last_dm_at: dict[str, float] = {}
        self._last_key_at: dict[tuple[str, str], float] = {}

    def allow_ability(self, discord_id: str, spell_key: str, now: float | None = None) -> bool:
        t = time.monotonic() if now is None else now
        last = self._last_dm_at.get(discord_id)
        if last is not None and t - last < self._min_interval_s:
            return False
        key = (discord_id, spell_key)
        last_key = self._last_key_at.get(key)
        if last_key is not None and t - last_key < self._repeat_window_s:
            return False
        self._last_dm_at[discord_id] = t
        self._last_key_at[key] = t
        return True


# ── Discord DM via REST ──────────────────────────────────────────────────────


async def _send_discord_dm(bot_token: str, discord_id: str, content: str) -> bool:
    """Отправить DM пользователю через Discord REST API."""
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Создать/получить DM-канал
        r = await client.post(
            "https://discord.com/api/v10/users/@me/channels",
            headers=headers,
            json={"recipient_id": discord_id},
        )
        if not r.is_success:
            log.error(
                "Не удалось создать DM-канал для %s: %s %s",
                discord_id,
                r.status_code,
                r.text,
            )
            return False

        channel_id = r.json()["id"]

        # 2. Отправить сообщение
        r2 = await client.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers=headers,
            json={"content": content},
        )
        if not r2.is_success:
            log.error(
                "Не удалось отправить DM %s: %s %s",
                discord_id,
                r2.status_code,
                r2.text,
            )
            return False

    log.info("Discord DM отправлен → %s", discord_id)
    return True


# ── Voice hint via bot-процесс (Phase 4.5) ───────────────────────────────────


async def _send_voice_hint(settings: Settings, text: str) -> bool:
    """POST короткой фразы в voice-приёмник bot-процесса. Строго best-effort.

    Голос выключен (DISCORD_VOICE_CHANNEL_ID=0) или bot-процесс лежит —
    молча False, текстовый канал не страдает.
    """
    if not settings.discord_voice_channel_id or not text:
        return False
    url = f"http://{settings.voice_http_host}:{settings.voice_http_port}/speak"
    headers = {}
    if settings.bridge_bearer_token:
        headers["Authorization"] = f"Bearer {settings.bridge_bearer_token}"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(url, json={"text": text}, headers=headers)
            return bool(resp.is_success)
    except Exception as exc:
        log.debug("Voice-хинт не доставлен (%s): %s", url, exc)
        return False


# ── KB section lookup ────────────────────────────────────────────────────────


def _find_section(doc: KBDoc, priority: list[str]) -> Section | None:
    """Найти первую подходящую секцию из doc по списку приоритетных заголовков."""
    for target in priority:
        target_lower = target.lower()
        for sec in doc.sections:
            if target_lower in sec.title.lower():
                return sec
    return doc.sections[0] if doc.sections else None


# ── LLM hint generation ──────────────────────────────────────────────────────

_HINT_SYSTEM = """\
Ты — тренер по PvP арене в WoW TBC Classic. Игрок в бою, у тебя 3 секунды.
Пиши только по-русски. Совет ≤ 120 слов. Никаких вводных фраз — только действие.
Советуй лично игроку: его классу, его кнопкам — не общий план команды.
Ссылайся ТОЛЬКО на текст из KB-секции. Если не знаешь — молчи."""


async def _generate_hint(
    anthropic_client: AsyncAnthropic,
    model: str,
    event_type: str,
    event_fields: dict[str, Any],
    kb_section_text: str,
    matchup: str,
    player_class: str | None = None,
) -> str:
    """Сгенерировать краткий совет через Haiku, таргетированный под класс игрока."""
    player_line = f"Игрок играет за: {player_class}\n" if player_class else ""
    user_msg = (
        f"Матчап: {matchup}\n"
        f"{player_line}"
        f"Событие: {event_type} — {event_fields}\n\n"
        f"Из KB:\n{kb_section_text}\n\n"
        "Что делать прямо сейчас? Кратко и чётко."
    )
    response = await anthropic_client.messages.create(
        model=model,
        max_tokens=300,
        system=_HINT_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    first_block = response.content[0]
    # Extract text safely for mypy
    if hasattr(first_block, "text"):
        return str(first_block.text).strip()
    return ""


# ── Постматч (Phase 4.3) ─────────────────────────────────────────────────────


async def _finish_match(ctx: PipelineContext, player_name: str) -> str:
    """ARENA_END: собрать DM-разбор боя из накопленного таймлайна.

    Ключ — player_name (см. postmatch.py: session_id в ARENA_END-envelope
    у bridge ≤ v0.4.1 уже пересоздан, по нему матч не найти).
    """
    record = ctx.match_recorder.finish(player_name)
    if record is None:
        log.debug("Постматч: у %s нет открытой записи — пропуск", player_name)
        return "skipped"
    if not record.events:
        log.info("Постматч: %s — 0 записанных событий, отчёт не шлём", player_name)
        return "skipped"

    entry = await ctx.access_service.find_by_character(player_name)
    if entry is None:
        log.warning("Постматч: игрок '%s' не найден в whitelist", player_name)
        return "no_player"

    candidates = ctx.kb_retriever.find_realtime_candidates(
        record.enemy_classes, record.our_comp_hint
    )
    doc = candidates[0] if candidates else None
    report = build_postmatch_report(record, doc)

    ok = await _send_discord_dm(ctx.settings.discord_bot_token, entry.discord_id, report)
    return "sent" if ok else "error"


# ── Main pipeline ────────────────────────────────────────────────────────────


@dataclass
class PipelineContext:
    """Зависимости pipeline'а — инициализируются в lifespan FastAPI."""

    access_service: AccessService
    kb_retriever: KBRetriever
    anthropic_client: AsyncAnthropic
    settings: Settings
    hint_throttle: HintThrottle = field(default_factory=HintThrottle)
    match_recorder: MatchRecorder = field(default_factory=MatchRecorder)
    # Phase 4.6: очередь персональных голосовых фраз для локального TTS моста
    # (обратный канал бэкенд→мост, дренируется через GET /v1/hints).
    hint_queue: HintQueue = field(default_factory=HintQueue)
    # Phase 4.5: per-player режим голоса (None в тестах/старых вызовах = 'on')
    player_settings: PlayerSettingsService | None = None


def _kill_target_line(doc: KBDoc) -> str:
    """'🎯 Килл-таргет: warrior (запасной: paladin)' из frontmatter документа."""
    kt = doc.kill_target
    line = f"🎯 Килл-таргет: **{kt.primary}**"
    if kt.fallback:
        line += f" (запасной: {kt.fallback})"
    return line


def _alternates_line(candidates: list[KBDoc]) -> str | None:
    """Спеки с ворот не видны — если кандидатов несколько, честно говорим об этом."""
    if len(candidates) < 2:
        return None
    others = ", ".join(f"`{d.composition} vs {d.vs}`" for d in candidates[1:3])
    return f"⚠️ Спек врагов не подтверждён. Если не сойдётся — смотри: {others}"


async def process_event(ctx: PipelineContext, envelope: dict[str, Any]) -> str:
    """Обработать событие из bridge.

    Args:
        ctx: зависимости (DB, KB, LLM, settings)
        envelope: dict из CanonicalEnvelope.model_dump()

    Returns:
        Статус: "sent", "no_matchup", "no_player", "skipped", "throttled", "error"
    """
    event = envelope.get("event", {})
    event_type = event.get("type", "")
    player_name = str(envelope.get("player_name", ""))
    match_info = envelope.get("match", {})
    bracket = match_info.get("bracket", "unknown")
    enemies_raw = match_info.get("enemies", [])
    enemies_str = ", ".join(f"{e.get('wow_class', '?')}/{e.get('race', '?')}" for e in enemies_raw)

    # ── 0. Phase 4.3: постматч-копилка (до всех хинт-фильтров) ──────────
    # CC-касты в реалтайме не хинтятся, но в разбор боя попадать должны,
    # поэтому запись — раньше фильтра по _ABILITY_HINT_KEYS.
    ts = parse_bridge_ts(str(envelope.get("bridge_ts", ""))) or utcnow()
    spell_key = str(event.get("spell_key", "") or event.get("trinket_key", ""))
    if event_type == "ARENA_START":
        ctx.match_recorder.start(
            player_name,
            str(envelope.get("session_id", "")),
            ts,
            bracket=str(bracket),
            enemies=[{str(k): str(v) for k, v in e.items()} for e in enemies_raw],
            our_comp_hint=str(match_info.get("our_comp_hint") or "") or None,
        )
    elif event_type in ("TRINKET", "ABILITY"):
        ctx.match_recorder.note(
            player_name, ts, event_type, str(event.get("source_name", "враг")), spell_key
        )
    elif event_type == "ARENA_END":
        return await _finish_match(ctx, player_name)

    # ── 1. Фильтр — отвечаем только на важные события ───────────────────
    if event_type not in _HINT_EVENTS:
        log.debug("Событие %s пропущено (не в _HINT_EVENTS)", event_type)
        return "skipped"
    if event_type == "ABILITY" and spell_key not in _ABILITY_HINT_KEYS:
        log.debug("ABILITY '%s' не в списке hint-ключей — пропуск", spell_key)
        return "skipped"

    # ── 2. Найти игрока в whitelist ──────────────────────────────────────
    entry = await ctx.access_service.find_by_character(player_name)
    if entry is None:
        log.warning("Игрок '%s' не найден в whitelist", player_name)
        return "no_player"

    discord_id = entry.discord_id

    # ── 3. Троттлинг in-fight подсказок ──────────────────────────────────
    if event_type == "ABILITY" and not ctx.hint_throttle.allow_ability(discord_id, spell_key):
        log.debug("ABILITY '%s' затроттлен для %s", spell_key, discord_id)
        return "throttled"

    # ── 4. KB lookup: классы врагов + наш состав (Phase 4.1) ─────────────
    enemy_classes = [str(e.get("wow_class", "")).lower() for e in enemies_raw if e.get("wow_class")]
    our_comp_hint = match_info.get("our_comp_hint") or None
    player_class = str(match_info.get("player_class") or "") or None

    candidates = ctx.kb_retriever.find_realtime_candidates(enemy_classes, our_comp_hint)
    doc: KBDoc | None = candidates[0] if candidates else None

    if doc is None:
        log.info("KB не содержит матчап по врагам [%s] — %s", enemies_str, event_type)
        if event_type != "ARENA_START":
            return "no_matchup"  # mid-fight generic DM — только шум
        plain_msg = (
            f"🏟 **Арена началась** | {bracket} | Враги: {enemies_str}\n"
            "📚 Матчап ещё не добавлен в KB. Используй /matchup для поиска!"
        )
        await _send_discord_dm(ctx.settings.discord_bot_token, discord_id, plain_msg)
        return "no_matchup"

    # ── 5. Выбрать нужную секцию KB ─────────────────────────────────────
    priority = _SECTION_PRIORITY.get(event_type, [])
    section = _find_section(doc, priority)
    section_text = section.body_md if section else "Секция не найдена."
    section_title = section.title if section else "Советы"

    # ── 6. LLM генерирует подсказку (таргет — класс игрока) ──────────────
    matchup_label = f"{doc.composition} vs {doc.vs}"

    try:
        hint_text = await _generate_hint(
            anthropic_client=ctx.anthropic_client,
            model=ctx.settings.anthropic_model_classify,  # Haiku — быстрее и дешевле
            event_type=event_type,
            event_fields={k: v for k, v in event.items() if k != "type"},
            kb_section_text=section_text[:1500],  # не перегружаем контекст
            matchup=matchup_label,
            player_class=player_class,
        )
    except Exception as exc:
        log.error("LLM ошибка: %s — отправляю KB-текст напрямую", exc)
        hint_text = section_text[:600]

    # ── 7. Форматируем DM ────────────────────────────────────────────────
    lines: list[str]
    if event_type == "ARENA_START":
        lines = [
            f"🏟 **{matchup_label}** | {bracket} | сложность: {doc.difficulty.value}",
            _kill_target_line(doc),
            hint_text,
        ]
        alt = _alternates_line(candidates)
        if alt:
            lines.append(alt)
    elif event_type == "TRINKET":
        source = str(event.get("source_name", "враг"))
        lines = [
            f"💎 **{source} тринкетнул!** | {matchup_label}",
            hint_text,
        ]
    else:  # ABILITY
        source = str(event.get("source_name", "враг"))
        lines = [
            f"⚡ **{source}: {spell_key}** | {section_title}",
            hint_text,
        ]

    lines.append(f"📖 `/matchup our:{doc.composition} vs:{doc.vs}` — полный гайд")
    dm_content = "\n".join(lines)[:2000]  # Discord лимит

    # ── 8. Voice-фраза (Phase 4.5) + текстовый DM ────────────────────────
    # Голос — ОТДЕЛЬНАЯ короткая фраза (≤8 слов, RU-сленг), не текстовый hint.
    voice_mode = DEFAULT_VOICE_MODE
    if ctx.player_settings is not None:
        voice_mode = await ctx.player_settings.get_voice_mode(discord_id)

    source_name = str(event.get("source_name", "враг"))
    if event_type == "ARENA_START":
        voice_text = arena_start_phrase(enemy_classes, doc.kill_target.primary)
    elif event_type == "TRINKET":
        voice_text = trinket_phrase(source_name)
    else:
        voice_text = ability_phrase(source_name, spell_key)

    voice_sent = False
    if voice_mode != "off":
        # Phase 4.6 — локальный персональный голос: та же короткая фраза кладётся
        # в очередь игрока; его мост заберёт её через GET /v1/hints и озвучит
        # системным TTS локально. Это ДОБАВОЧНЫЙ канал: на решение о тексте и о
        # Discord-голосе он НЕ влияет (backend не знает, реально ли мост поллит и
        # озвучивает — суппресить текст по факту постановки в очередь опасно,
        # игрок остался бы ни с чем). 'off' сюда не попадает — голос отключён весь.
        ctx.hint_queue.push(player_name, voice_text)
        voice_sent = await _send_voice_hint(ctx.settings, voice_text)

    if voice_mode == "only" and voice_sent:
        # Игрок просил без text-spam — голос доставлен, текст подавляем.
        return "sent"

    ok = await _send_discord_dm(ctx.settings.discord_bot_token, discord_id, dm_content)
    return "sent" if ok or voice_sent else "error"
