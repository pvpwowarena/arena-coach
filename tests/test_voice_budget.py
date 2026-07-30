"""Бюджет длины голосовых реплик (Phase 4.17).

Живой тест 30.07: «"хилер кастует кикай" — долго», «нужно быстрее принимать решение».
Замер объяснил, почему: медианная реплика была **11 слогов ≈ 3.9с речи** у Milena, а
окно на кик равно длительности каста — Flash Heal 1.5с, Holy Light 2.5с, Healing Wave 3с.
То есть фраза заканчивалась ПОЗЖЕ, чем закрывалось окно решения.

Второй, менее очевидный эффект: `SpeechChannel` в мосту не прерывает текущую речь
(`if self.busy: return`). Пока читается фраза на 3.9с, никакая новая подсказка
произнесена быть не может — отсюда «не корректирует по ходу боя». Короткая фраза
освобождает канал в разы быстрее, поэтому длина это не косметика, а пропускная
способность голоса.

Полезная информация обязана быть в ПЕРВОМ слове: игрок действует, когда фраза
начинается, а не когда заканчивается. Поэтому у критичных по времени реакций —
императив первым словом и жёсткий потолок.
"""

from __future__ import annotations

import pytest

from arena_coach.orchestrator.reactions import (
    ABILITY_REACTIONS,
    CAST_REACTIONS,
    CATEGORY_REACTIONS,
    HIGH,
    TRINKET_REACTION,
    Reaction,
)

_VOWELS = "аеёиоуыэюя"

#: Milena на дефолтной скорости — примерно 2.8 слога в секунду (эмпирика).
SYLLABLES_PER_SEC = 2.8

#: Потолки в СЛОГАХ, а не в словах: «Кик хил!» и «Не разбредайтесь» — оба два слова,
#: но по времени различаются в три раза.
MAX_SYLLABLES_CAST_ALERT = 4  # ≈1.4с — успеть внутрь самого короткого каста
MAX_SYLLABLES_HIGH = 8  # ≈2.9с — «решается сейчас»
MAX_SYLLABLES_NORMAL = 11  # ≈3.9с — можно и дослушать


def syllables(phrase: str) -> int:
    return sum(1 for ch in phrase.lower() if ch in _VOWELS)


def seconds(phrase: str) -> float:
    return syllables(phrase) / SYLLABLES_PER_SEC


class TestCastAlertsFitInsideTheCast:
    """Самый жёсткий бюджет: пока идёт каст, кик ещё возможен."""

    @pytest.mark.parametrize("key", sorted(CAST_REACTIONS))
    def test_short_enough(self, key: str) -> None:
        reaction = CAST_REACTIONS[key]
        n = syllables(reaction.voice)
        assert n <= MAX_SYLLABLES_CAST_ALERT, (
            f"{key}: {n} слогов ≈ {seconds(reaction.voice):.1f}с — "
            f"дольше, чем окно на кик (Flash Heal 1.5с)"
        )

    @pytest.mark.parametrize("key", sorted(CAST_REACTIONS))
    def test_imperative_first_word(self, key: str) -> None:
        """Игрок действует на первом слове, а не дослушав фразу."""
        first = CAST_REACTIONS[key].voice.split()[0].strip("!,.—").lower()
        assert first in {"кик", "сбей", "прерви", "ломай"}, (
            f"{key}: первое слово {first!r} — не действие"
        )

    @pytest.mark.parametrize("key", sorted(CAST_REACTIONS))
    def test_ttl_matches_cast_window(self, key: str) -> None:
        """Просроченный «кик!» — не подсказка, а помеха: TTL ≈ длине каста."""
        ttl = CAST_REACTIONS[key].voice_ttl_s
        assert ttl is not None and ttl <= 3.0, f"{key}: TTL {ttl} — переживёт сам каст"


def _all_reactions() -> list[tuple[str, Reaction]]:
    out: list[tuple[str, Reaction]] = [("TRINKET", TRINKET_REACTION)]
    out += [(f"ability:{k}", r) for k, r in ABILITY_REACTIONS.items()]
    out += [(f"category:{k}", r) for k, r in CATEGORY_REACTIONS.items()]
    return out


class TestSpeechBudget:
    @pytest.mark.parametrize(
        ("name", "reaction"), _all_reactions(), ids=lambda x: getattr(x, "", x)
    )
    def test_within_budget_for_priority(self, name: str, reaction: Reaction) -> None:
        cap = MAX_SYLLABLES_HIGH if reaction.priority == HIGH else MAX_SYLLABLES_NORMAL
        n = syllables(reaction.voice)
        assert n <= cap, (
            f"{name} ({reaction.priority}): {n} слогов ≈ {seconds(reaction.voice):.1f}с "
            f"при потолке {cap}. Разбор переносится в `dm`, голос — только действие."
        )

    def test_dm_keeps_the_nuance(self) -> None:
        """Укорачивая голос, мы не теряем смысл — он остаётся в тексте."""
        for name, reaction in _all_reactions():
            assert len(reaction.dm) > len(reaction.voice), name

    #: Медиана до Phase 4.17 — замерено на живой таблице перед правкой.
    MEDIAN_BEFORE_SYLLABLES = 11

    def test_median_at_least_twice_shorter_than_before(self) -> None:
        """Интегральная проверка: голос перестал быть монологом.

        Порог привязан к замеру ДО правки (11 слогов ≈ 3.9с), а не к круглому
        числу: смысл требования — «вдвое короче», а не «меньше двух секунд».
        """
        counts = sorted(syllables(r.voice) for _, r in _all_reactions())
        median = counts[len(counts) // 2]
        assert median * 2 <= self.MEDIAN_BEFORE_SYLLABLES + 1, (
            f"медиана {median} слогов ≈ {median / SYLLABLES_PER_SEC:.1f}с; "
            f"было {self.MEDIAN_BEFORE_SYLLABLES} ≈ "
            f"{self.MEDIAN_BEFORE_SYLLABLES / SYLLABLES_PER_SEC:.1f}с"
        )
