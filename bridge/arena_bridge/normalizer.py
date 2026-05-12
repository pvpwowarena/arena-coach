"""Нормализация raw addon-событий в canonical schema для backend.

Phase 4 stub. См. docs/phase-0-design.md §6.3 — канонический JSON envelope:
{ schema_version, envelope: {event_id, session_id, actor_discord_id, ...},
  match: {bracket, map, team, enemy, matchup_slug_hint},
  event: {type, subject_name, subject_role, spell_id, details} }
"""

from __future__ import annotations


def normalize_event(raw: dict[str, object]) -> dict[str, object]:
    """TODO(Phase 4): построить envelope + bridge_ts + матчап-hint."""
    raise NotImplementedError("Phase 4")
