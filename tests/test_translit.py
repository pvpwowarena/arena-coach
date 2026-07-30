"""Латиница → кириллица для голоса (Phase 4.14).

Русский синтезатор читает латиницу кашей, а латиница в фразе появляется штатно:
ники врагов (нужны при дублях классов) и `en_name` способностей из slang-слоя.
"""

from __future__ import annotations

from arena_coach.kb.translit import latin_to_cyrillic, translit_word


class TestTranslitWord:
    def test_keeps_capitalization(self) -> None:
        assert translit_word("Cekraj")[:1] == "К"
        assert translit_word("cekraj")[:1] == "к"

    def test_digraphs_before_letters(self) -> None:
        assert translit_word("Shadow").startswith("Ш")
        assert "ч" in translit_word("Church")
        assert translit_word("Zhora").startswith("Ж")

    def test_j_and_x(self) -> None:
        assert translit_word("Jino").startswith("Дж")
        assert translit_word("Xara").lower().startswith("кс")

    def test_empty_and_non_latin_pass_through(self) -> None:
        assert translit_word("") == ""
        assert translit_word("Рога") == "Рога"


class TestLatinToCyrillic:
    def test_cyrillic_untouched(self) -> None:
        phrase = "Тринкета нет — всё на него."
        assert latin_to_cyrillic(phrase) == phrase

    def test_mixed_phrase_only_latin_converted(self) -> None:
        out = latin_to_cyrillic("Тринкета нет у Cekraj — всё на него.")
        assert "Cekraj" not in out
        assert out.startswith("Тринкета нет у ")
        assert out.endswith(" — всё на него.")

    def test_ability_en_name_becomes_speakable(self) -> None:
        """slang для 46 слагов отдаёт en_name — именно от этого «кривоватый перевод»."""
        out = latin_to_cyrillic("Клоак — Cloak of Shadows на пять секунд.")
        assert not any("a" <= ch.lower() <= "z" for ch in out)

    def test_numbers_and_punctuation_kept(self) -> None:
        assert latin_to_cyrillic("10 секунд!") == "10 секунд!"

    def test_empty(self) -> None:
        assert latin_to_cyrillic("") == ""
