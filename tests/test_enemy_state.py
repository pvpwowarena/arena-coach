"""EnemyTracker (Phase 4.14) — реестр кулдаунов врага и карта «ник → класс».

Проверяем то, ради чего модуль появился (аудит 30.07): бот должен знать состояние,
которого игрок не видит, и не должен выдумывать секунды там, где кулдаун не
подтверждён sourced-слоем.
"""

from __future__ import annotations

from arena_coach.orchestrator.enemy_state import (
    TRINKET,
    EnemyTracker,
)


def _tracker(t: list[float]) -> EnemyTracker:
    """Трекер с инъектированными часами: `t[0]` — «сейчас», тесты не спят."""
    return EnemyTracker(clock=lambda: t[0])


class TestCooldownLedger:
    def test_spent_until_cooldown_expires(self) -> None:
        now = [100.0]
        tr = _tracker(now)
        tr.start("Vlad", "s1")
        tr.note("Vlad", "Cekraj", "vanish", wow_class="ROGUE", cooldown_s=180.0)

        assert tr.remaining_s("Vlad", "Cekraj", "vanish") == 180.0
        now[0] += 179.0
        assert tr.remaining_s("Vlad", "Cekraj", "vanish") == 1.0
        now[0] += 2.0
        assert tr.remaining_s("Vlad", "Cekraj", "vanish") == 0.0

    def test_unknown_cooldown_keeps_only_the_fact(self) -> None:
        """Кулдаун не подтверждён → «потрачено» без секунд, и это НЕ протухает."""
        now = [0.0]
        tr = _tracker(now)
        tr.start("Vlad", "s1")
        tr.note_trinket("Vlad", "Cekraj")

        assert tr.remaining_s("Vlad", "Cekraj", TRINKET) is None
        assert tr.without_trinket("Vlad") == ["Cekraj"]
        now[0] += 10_000.0
        # Секунд не знаем — значит и «вернулся» объявить не можем: молчим, но помним.
        assert tr.without_trinket("Vlad") == ["Cekraj"]
        assert tr.poll_ready_again("Vlad") == []

    def test_note_before_start_is_ignored(self) -> None:
        tr = _tracker([0.0])
        tr.note("Vlad", "Cekraj", "vanish", cooldown_s=180.0)
        assert tr.known("Vlad") == []


class TestClassMap:
    def test_class_learned_from_cast_and_not_overwritten(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.note("Vlad", "Cekraj", "vanish", wow_class="ROGUE")
        tr.note("Vlad", "Cekraj", "kick", wow_class="")  # без класса — не затирает
        assert [(r.name, r.wow_class) for r in tr.known("Vlad")] == [("Cekraj", "ROGUE")]

    def test_duplicated_classes_and_needs_name(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.note("Vlad", "Cekraj", "vanish", wow_class="ROGUE")
        tr.note("Vlad", "Shadow", "sap", wow_class="ROGUE")
        tr.note("Vlad", "Frosty", "ice_block", wow_class="MAGE")

        assert tr.duplicated_classes("Vlad") == {"ROGUE"}
        assert tr.needs_name("Vlad", "Cekraj") is True
        assert tr.needs_name("Vlad", "Shadow") is True
        assert tr.needs_name("Vlad", "Frosty") is False  # маг один — ник лишний
        assert sorted(tr.names_of_class("Vlad", "rogue")) == ["Cekraj", "Shadow"]

    def test_unknown_enemy_needs_no_name(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        assert tr.needs_name("Vlad", "Nobody") is False

    def test_without_trinket_filters_by_class(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.note("Vlad", "Cekraj", "vanish", wow_class="ROGUE")
        tr.note("Vlad", "Frosty", "ice_block", wow_class="MAGE")
        tr.note_trinket("Vlad", "Cekraj")
        tr.note_trinket("Vlad", "Frosty")

        assert tr.without_trinket("Vlad", "ROGUE") == ["Cekraj"]
        assert sorted(tr.without_trinket("Vlad")) == ["Cekraj", "Frosty"]


class TestOpenWindow:
    def test_needs_both_trinket_and_defensive(self) -> None:
        now = [0.0]
        tr = _tracker(now)
        tr.start("Vlad", "s1")

        tr.note_trinket("Vlad", "Cekraj")
        assert tr.poll_open_window("Vlad") is None  # только тринкет — не окно

        tr.note("Vlad", "Cekraj", "vanish", wow_class="ROGUE", cooldown_s=180.0, category="reset")
        window = tr.poll_open_window("Vlad")
        assert window is not None
        assert window.enemy == "Cekraj"
        assert window.wow_class == "ROGUE"
        assert window.spent == (TRINKET, "vanish")

    def test_announced_once_per_enemy(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.note_trinket("Vlad", "Cekraj")
        tr.note("Vlad", "Cekraj", "evasion", cooldown_s=300.0, category="defensive")

        assert tr.poll_open_window("Vlad") is not None
        assert tr.poll_open_window("Vlad") is None  # второй раз молчим

    def test_expired_defensive_no_longer_counts(self) -> None:
        now = [0.0]
        tr = _tracker(now)
        tr.start("Vlad", "s1")
        tr.note_trinket("Vlad", "Cekraj")
        tr.note("Vlad", "Cekraj", "blind", cooldown_s=60.0, category="defensive")
        now[0] += 61.0
        assert tr.poll_open_window("Vlad") is None  # блайнд вернулся — окна нет

    def test_non_defensive_category_does_not_open_window(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.note_trinket("Vlad", "Cekraj")
        tr.note("Vlad", "Cekraj", "kidney_shot", cooldown_s=0.0, category="stun")
        assert tr.poll_open_window("Vlad") is None


class TestReadyAgain:
    def test_edge_triggered_once_with_cooldown_length(self) -> None:
        now = [0.0]
        tr = _tracker(now)
        tr.start("Vlad", "s1")
        tr.note("Vlad", "Cekraj", "vanish", cooldown_s=180.0)

        assert tr.poll_ready_again("Vlad") == []
        now[0] += 180.0
        events = tr.poll_ready_again("Vlad")
        assert [(e.enemy, e.key, e.cooldown_s) for e in events] == [("Cekraj", "vanish", 180.0)]
        assert tr.poll_ready_again("Vlad") == []  # рёберный детектор


class TestLifecycle:
    def test_reemit_same_session_keeps_state(self) -> None:
        """Повторный ARENA_START (доуточнение состава) не должен обнулять учёт."""
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.note_trinket("Vlad", "Cekraj")
        tr.start("Vlad", "s1")
        assert tr.without_trinket("Vlad") == ["Cekraj"]

    def test_new_session_resets(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.note_trinket("Vlad", "Cekraj")
        tr.start("Vlad", "s2")
        assert tr.known("Vlad") == []

    def test_end_clears(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.note_trinket("Vlad", "Cekraj")
        tr.end("Vlad")
        assert tr.known("Vlad") == []

    def test_players_isolated(self) -> None:
        tr = _tracker([0.0])
        tr.start("Vlad", "s1")
        tr.start("Other", "s2")
        tr.note_trinket("Vlad", "Cekraj")
        assert tr.without_trinket("Other") == []

    def test_stale_matches_evicted(self) -> None:
        now = [0.0]
        tr = EnemyTracker(clock=lambda: now[0], ttl_s=60.0)
        tr.start("Vlad", "s1")
        tr.note_trinket("Vlad", "Cekraj")
        now[0] += 61.0
        tr.start("Other", "s2")  # любой новый матч запускает уборку
        assert tr.known("Vlad") == []

    def test_max_matches_capped(self) -> None:
        now = [0.0]
        tr = EnemyTracker(clock=lambda: now[0], max_matches=2)
        for i in range(5):
            now[0] += 1.0
            tr.start(f"P{i}", f"s{i}")
        assert len(tr.known("P4")) == 0  # без событий пусто, но матч жив
        alive = [f"P{i}" for i in range(5) if tr.without_trinket(f"P{i}") is not None]
        assert len(alive) == 5  # запрос безопасен для вытесненных
