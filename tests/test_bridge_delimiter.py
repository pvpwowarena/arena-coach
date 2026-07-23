"""Разделитель AC-формата: канонический «#» (addon >= 0.2.1) и легаси «|».

Контекст (2026-07-23, первый живой тест): современный Anniversary-клиент
запрещает сырой «|» в SendChatMessage — аддон 0.2.0 вообще не мог отправить
события. Формат переведён на «#»; bridge обязан принимать оба варианта.
"""

from __future__ import annotations

from arena_bridge.chat_tail import _AC_RE, parse_ac_line


def test_parse_hash_delimiter() -> None:
    assert parse_ac_line("TRINKET#EnemyName#42292#pvp_trinket") == [
        "TRINKET",
        "EnemyName",
        "42292",
        "pvp_trinket",
    ]


def test_parse_legacy_pipe_delimiter() -> None:
    assert parse_ac_line("TRINKET|EnemyName|42292|pvp_trinket") == [
        "TRINKET",
        "EnemyName",
        "42292",
        "pvp_trinket",
    ]


def test_regex_extracts_hash_payload() -> None:
    line = "7/23 13:02:01.000  To Arenacoach: [AC#ARENA_START#2v2#ROGUE/HUMAN,MAGE/GNOME]"
    m = _AC_RE.search(line)
    assert m is not None
    assert m.group(1) == "ARENA_START#2v2#ROGUE/HUMAN,MAGE/GNOME"


def test_regex_extracts_legacy_pipe_payload() -> None:
    line = "7/23 13:02:01.000  To Arenacoach: [AC|TRINKET|EnemyName|42292|pvp_trinket]"
    m = _AC_RE.search(line)
    assert m is not None
    assert m.group(1) == "TRINKET|EnemyName|42292|pvp_trinket"


def test_regex_ignores_non_ac_lines() -> None:
    assert _AC_RE.search("7/23 13:02:05.000  [2. Trade] WTS [Some Item]") is None


def test_end_to_end_hash_line_parses_same_as_pipe() -> None:
    hash_payload = _AC_RE.search("To X: [AC#ARENA_END#5]")
    pipe_payload = _AC_RE.search("To X: [AC|ARENA_END|5]")
    assert hash_payload is not None and pipe_payload is not None
    assert (
        parse_ac_line(hash_payload.group(1))
        == parse_ac_line(pipe_payload.group(1))
        == [
            "ARENA_END",
            "5",
        ]
    )
