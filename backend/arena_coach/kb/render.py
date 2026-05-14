"""KB → Discord embed рендерер.

Правила:
- Embed field value max 1024 символов → обрезаем с «…»
- [[ability:slug]] заменяем на `slug` (inline code)
- Ссылки на источники в footer
- Цвет embed = difficulty

Phase 2: полный матчап + краткий opener-only режим.
"""

from __future__ import annotations

import re
from typing import Literal

import discord

from arena_coach.kb.schema import Difficulty, KBDoc, Source

# ── Цвета по difficulty ───────────────────────────────────────────────
_DIFFICULTY_COLORS: dict[Difficulty, discord.Color] = {
    Difficulty.EASY: discord.Color.green(),
    Difficulty.MODERATE: discord.Color.from_rgb(255, 200, 0),  # жёлтый
    Difficulty.HARD: discord.Color.orange(),
    Difficulty.VERY_HARD: discord.Color.red(),
    Difficulty.MIRROR: discord.Color.purple(),
}

# Секции которые показываем в «полном» embed
_FULL_SECTIONS = {
    "opener",
    "alternative opener",
    "if enemy opens first",
    "if enemy trinkets",
    "mid-fight rotation",
    "common mistakes",
    "key cooldowns to track",
    "endgame",
    "strategy",
    "stealth game",
    "general",
    "reset option",
}

# Секции для «opener-only» режима
_OPENER_SECTIONS = {"opener", "strategy", "stealth game", "general"}

_ABILITY_REF_RE = re.compile(r"\[\[ability:([a-z0-9-]+)\]\]")


def _clean_ability_refs(text: str) -> str:
    """Заменить [[ability:slug]] на `slug` для отображения в Discord."""
    return _ABILITY_REF_RE.sub(r"`\1`", text)


def _truncate(text: str, limit: int = 1024) -> str:
    """Обрезать текст до limit символов с «…»."""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _format_sources(sources: list[Source]) -> str:
    """Форматировать список источников в строку для footer."""
    parts: list[str] = []
    for src in sources[:3]:  # не более 3 источников в footer
        src_type = getattr(src, "type", "")
        if src_type in ("web", "youtube"):
            url = getattr(src, "url", "")
            title = getattr(src, "title", None) or src_type
            if url:
                parts.append(f"[{title}]({url})")
            else:
                parts.append(title)
        elif src_type == "stream-paste":
            author = getattr(src, "author", "unknown")
            parts.append(f"stream: {author}")
        elif src_type == "file":
            path = getattr(src, "path", "")
            author = getattr(src, "author", None) or path
            parts.append(f"file: {author}")
    return " · ".join(parts) if parts else ""


def render_matchup_embed(
    doc: KBDoc,
    mode: Literal["full", "opener"] = "full",
) -> discord.Embed:
    """Сгенерировать Discord embed из KBDoc.

    mode='full'   — все ключевые секции.
    mode='opener' — только opener/strategy/stealth-game/general.
    """
    color = _DIFFICULTY_COLORS.get(doc.difficulty, discord.Color.blurple())

    embed = discord.Embed(
        title=f"⚔️  {doc.composition}  vs  {doc.vs}",
        color=color,
    )

    # ── Header fields ─────────────────────────────────────────────────
    diff_emoji = {
        Difficulty.EASY: "🟢",
        Difficulty.MODERATE: "🟡",
        Difficulty.HARD: "🟠",
        Difficulty.VERY_HARD: "🔴",
        Difficulty.MIRROR: "🟣",
    }.get(doc.difficulty, "⚪")

    embed.add_field(
        name="Сложность",
        value=f"{diff_emoji} {doc.difficulty.value}",
        inline=True,
    )
    kill_tgt = doc.kill_target.primary
    if doc.kill_target.fallback:
        kill_tgt += f" → {doc.kill_target.fallback}"
    embed.add_field(name="Убиваем", value=kill_tgt, inline=True)
    embed.add_field(name="Уверенность", value=doc.confidence.value, inline=True)

    # ── Sections ──────────────────────────────────────────────────────
    target_titles = _OPENER_SECTIONS if mode == "opener" else _FULL_SECTIONS

    sections_added = 0
    for section in doc.sections:
        if section.title.strip().lower() not in target_titles:
            continue
        if sections_added >= 5:
            # Discord ограничивает embed до 25 полей; 5 секций + 3 header = 8
            break
        body = _clean_ability_refs(section.body_md)
        body = _truncate(body, 1024)
        embed.add_field(
            name=f"📌  {section.title}",
            value=body,
            inline=False,
        )
        sections_added += 1

    if sections_added == 0:
        embed.add_field(
            name="ℹ️ Нет контента",
            value="Секции не найдены в документе.",
            inline=False,
        )

    # ── Footer: map notes + sources ───────────────────────────────────
    footer_parts: list[str] = []

    if doc.maps_notes:
        map_lines = [f"{k}: {v}" for k, v in list(doc.maps_notes.items())[:2]]
        footer_parts.append("🗺 " + " · ".join(map_lines))

    src_str = _format_sources(doc.sources)
    if src_str:
        footer_parts.append(f"📚 {src_str}")

    footer_parts.append(f"slug: {doc.slug}")

    embed.set_footer(text="  |  ".join(footer_parts))

    return embed


def render_no_matchup_embed(our_comp: str, vs_comp: str, suggestions: list[str]) -> discord.Embed:
    """Embed-ответ когда матчап не найден в KB."""
    embed = discord.Embed(
        title="❓  Матчап не найден",
        description=(
            f"**{our_comp}** vs **{vs_comp}** отсутствует в KB.\n\n"
            "Добавь источник чтобы создать документ."
        ),
        color=discord.Color.light_gray(),  # type: ignore[misc]
    )
    if suggestions:
        embed.add_field(
            name="Похожие матчапы",
            value="\n".join(suggestions),
            inline=False,
        )
    embed.set_footer(text="KB — единственный источник правды. Бот не выдумывает советы.")
    return embed


def render_glossary_embed(term: str, definition: dict[str, object]) -> discord.Embed:
    """Embed для /glossary <term>."""
    embed = discord.Embed(
        title=f"📖  {term}",
        color=discord.Color.blurple(),
    )
    if "description" in definition:
        embed.description = str(definition["description"])
    for key in ("duration", "dr", "cd", "id"):
        if key in definition:
            embed.add_field(name=key, value=str(definition[key]), inline=True)
    return embed


__all__ = [
    "render_glossary_embed",
    "render_matchup_embed",
    "render_no_matchup_embed",
]
