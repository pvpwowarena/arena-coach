"""Phase 4.20.2: боевой голос моста молчит, если говорит аддон.

Замер живого матча 30.07 (лог моста 18:45:15-18:45:46) — итоговая строка конвейера:
`отправлено 5/14, худший POST 0.14с, худшее отставание от лога 18.50с`. То есть сеть и
бэкенд отработали за 0.14с, а данных на диске не было 18.5 секунды: клиент сбрасывает
combat-лог блоками ~48КБ. Девять событий из четырнадцати мост выбросил сам, с
пометкой «случилось 12.1с назад — не отправляю: подсказка о нём уже не подсказка, а
помеха».

Значит при установленном говорящем аддоне (0.4.0+) голос моста не второй канал, а
эхо: то же самое, другим голосом, через 13-28 секунд. В живом тесте это звучало как
«Бей шамана!» уже после смерти шамана.

Здесь проверяется именно ПРАВИЛО ДЕФОЛТА, а не факт выключения: явную волю игрока
(флаг или переменная окружения) правило трогать не имеет права — у кого аддона нет,
у того голос по-прежнему из моста.
"""

from __future__ import annotations

import pytest

from arena_bridge.updater import ADDON_SPEAKS_SINCE, combat_voice_default


class TestDefaultFollowsTheAddon:
    @pytest.mark.parametrize("version", ["0.4.0", "0.4.1", "0.5.0", "0.5.1", "1.0.0"])
    def test_speaking_addon_turns_bridge_voice_off(self, version: str) -> None:
        assert combat_voice_default(version) is False

    @pytest.mark.parametrize("version", ["0.1.0", "0.2.1", "0.3.2"])
    def test_old_addon_keeps_bridge_voice(self, version: str) -> None:
        """До 0.4.0 голоса в аддоне не было — молчать было бы регрессом."""
        assert combat_voice_default(version) is True

    def test_no_addon_keeps_bridge_voice(self) -> None:
        """Аддон не установлен: мост — единственный источник голоса."""
        assert combat_voice_default(None) is True

    @pytest.mark.parametrize("garbage", ["", "неизвестно", "vX", "..."])
    def test_unreadable_version_keeps_voice(self, garbage: str) -> None:
        """Неразобранная версия — не повод молча отнять у игрока звук.

        Дефолт обязан ошибаться в сторону «оставить как было»: тихий мост, о котором
        игрок не просил, диагностируется в разы хуже, чем лишняя фраза.
        """
        assert combat_voice_default(garbage) is True

    def test_threshold_is_the_phase_where_addon_got_voice(self) -> None:
        """Порог привязан к факту (Phase 4.19 = аддон 0.4.0), а не к круглому числу."""
        assert ADDON_SPEAKS_SINCE == "0.4.0"
        assert combat_voice_default(ADDON_SPEAKS_SINCE) is False
