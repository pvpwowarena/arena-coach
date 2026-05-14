"""End-to-end pipeline: bridge event → KB lookup → LLM hint → Discord DM.

Поток данных:
1. POST /v1/events получает CanonicalEnvelope от bridge
2. Валидация bearer-токена
3. Поиск игрока в whitelist по player_name (character) → discord_id
4. KB lookup по matchup_slug_hint
5. LLM (Haiku) синтезирует краткий совет (≤ 500 символов) из нужной KB-секции
6. Отправка Discord DM через REST API

Нет в KB → отвечаем только при TRINKET/ARENA_START, остальное молчим.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx
from anthropic import AsyncAnthropic

from arena_coach.access.service import AccessService
from arena_coach.kb.retriever import KBRetriever
from arena_coach.kb.schema import KBDoc, Section
from arena_coach.shared.settings import Settings

log = logging.getLogger(__name__)

# Отвечаем только на эти типы событий (избегаем спама на каждый ABILITY)
_HINT_EVENTS = {"ARENA_START", "TRINKET"}

# Секции KB, которые ищем для каждого типа события
_SECTION_PRIORITY: dict[str, list[str]] = {
    "ARENA_START": ["Opener", "Alternative opener"],
    "TRINKET": ["If enemy trinkets", "Post-trinket", "After trinket"],
    "ABILITY": ["Key cooldowns to track", "Common mistakes"],
    "ARENA_END": ["Common mistakes"],
}


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
Ссылайся ТОЛЬКО на текст из KB-секции. Если не знаешь — молчи."""


async def _generate_hint(
    anthropic_client: AsyncAnthropic,
    model: str,
    event_type: str,
    event_fields: dict[str, Any],
    kb_section_text: str,
    matchup: str,
) -> str:
    """Сгенерировать краткий совет через Haiku."""
    user_msg = (
        f"Матчап: {matchup}\n"
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


# ── Main pipeline ────────────────────────────────────────────────────────────


@dataclass
class PipelineContext:
    """Зависимости pipeline'а — инициализируются в lifespan FastAPI."""

    access_service: AccessService
    kb_retriever: KBRetriever
    anthropic_client: AsyncAnthropic
    settings: Settings


async def process_event(ctx: PipelineContext, envelope: dict[str, Any]) -> str:
    """Обработать событие из bridge.

    Args:
        ctx: зависимости (DB, KB, LLM, settings)
        envelope: dict из CanonicalEnvelope.model_dump()

    Returns:
        Статус обработки: "sent", "no_matchup", "no_player", "skipped", "error"
    """
    event = envelope.get("event", {})
    event_type = event.get("type", "")
    player_name = str(envelope.get("player_name", ""))
    match_info = envelope.get("match", {})
    slug_hint = match_info.get("matchup_slug_hint") or ""
    bracket = match_info.get("bracket", "unknown")
    enemies_raw = match_info.get("enemies", [])
    enemies_str = ", ".join(f"{e.get('wow_class', '?')}/{e.get('race', '?')}" for e in enemies_raw)

    # ── 1. Фильтр — отвечаем только на важные события ───────────────────
    if event_type not in _HINT_EVENTS:
        log.debug("Событие %s пропущено (не в _HINT_EVENTS)", event_type)
        return "skipped"

    # ── 2. Найти игрока в whitelist ──────────────────────────────────────
    entry = await ctx.access_service.find_by_character(player_name)
    if entry is None:
        log.warning("Игрок '%s' не найден в whitelist", player_name)
        return "no_player"

    discord_id = entry.discord_id

    # ── 3. KB lookup по matchup ──────────────────────────────────────────
    doc: KBDoc | None = None

    if slug_hint:
        # slug_hint = "mage-rogue" (sorted enemy classes) — ищем по enemy comp
        doc = ctx.kb_retriever.find_by_slug(slug_hint)

    if doc is None and enemies_raw:
        # Fallback: пробуем через enemy classes vs наш (пока наш неизвестен — ищем любой)
        log.debug("Прямой поиск по slug '%s' не дал результата", slug_hint)

    if doc is None:
        log.info("KB не содержит матчап '%s' (%s) — DM без совета", slug_hint, enemies_str)
        # Отправляем базовый DM без KB-совета
        plain_msg = (
            f"🏟 **Арена началась** | {bracket} | Враги: {enemies_str}\n"
            "📚 Матчап ещё не добавлен в KB. Используй /matchup для поиска!"
        )
        await _send_discord_dm(ctx.settings.discord_bot_token, discord_id, plain_msg)
        return "no_matchup"

    # ── 4. Выбрать нужную секцию KB ─────────────────────────────────────
    priority = _SECTION_PRIORITY.get(event_type, [])
    section = _find_section(doc, priority)
    section_text = section.body_md if section else "Секция не найдена."
    section_title = section.title if section else "Советы"

    # ── 5. LLM генерирует подсказку ──────────────────────────────────────
    matchup_label = f"{doc.composition} vs {doc.vs}"

    try:
        hint_text = await _generate_hint(
            anthropic_client=ctx.anthropic_client,
            model=ctx.settings.anthropic_model_classify,  # Haiku — быстрее и дешевле
            event_type=event_type,
            event_fields={k: v for k, v in event.items() if k != "type"},
            kb_section_text=section_text[:1500],  # не перегружаем контекст
            matchup=matchup_label,
        )
    except Exception as exc:
        log.error("LLM ошибка: %s — отправляю KB-текст напрямую", exc)
        hint_text = section_text[:400]

    # ── 6. Форматируем DM ────────────────────────────────────────────────
    event_emoji = {"ARENA_START": "🏟", "TRINKET": "💎", "ABILITY": "⚡", "ARENA_END": "🏁"}
    emoji = event_emoji.get(event_type, "📌")

    dm_content = (
        f"{emoji} **{matchup_label}** | {section_title}\n"
        f"{hint_text}\n"
        f"📖 `/matchup our:{doc.composition} vs:{doc.vs}` — полный гайд"
    )[:2000]  # Discord лимит

    # ── 7. Отправить DM ──────────────────────────────────────────────────
    ok = await _send_discord_dm(ctx.settings.discord_bot_token, discord_id, dm_content)
    return "sent" if ok else "error"
