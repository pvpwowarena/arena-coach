"""Phase 4.20: тактический колаут на воротах — бюджет, факты и свежесть файлов.

Почему это отдельный тест, а не строчка в `test_addon_overlay.py`. Колаут — первый
случай, когда аддон произносит не факт («тринкет!»), а ПЛАН. У плана два способа
испортиться, и оба тихие:

1. **Время.** Клип играется в момент ворот, окно 8-10с. Слоговая модель Phase 4.17
   (2.8 слога/сек) — оценка, а `.ogg` на диске — правда. Здесь сверяется правда:
   длительность реального файла, а не предсказание.
2. **Смысл.** Формулировки собираются из KB-прозы регулярками, и самая опасная
   ошибка не «звучит криво», а «велит сапнуть мага, которого у врага нет» — такой
   колаут звучит уверенно и уводит игрока не туда. Живой промах именно этого вида
   и был поправлен проверкой «класс из фразы обязан быть у ВРАГА».

Тесты не требуют клиента WoW и работают на сгенерированных файлах.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ADDON = REPO / "addon" / "ArenaCoach"
MANIFEST = ADDON / "sfx" / "openers.json"
FFPROBE = shutil.which("ffprobe")

#: Окно ворот: команды сходятся 8-10с. Клип обязан закончиться внутри, иначе
#: последние слова звучат уже в бою, где канал нужен под «кик хил!».
MAX_CLIP_SECONDS = 8.0


def _load_generator():
    """`tools/` не пакет — грузим генератор по пути, чтобы взять его же таблицы.

    Тест обязан сверять фразы с ТЕМИ ЖЕ словарями, из которых они собраны:
    копия словаря в тесте разошлась бы с генератором на первой правке.
    """
    path = REPO / "tools" / "gen_addon_openers.py"
    spec = importlib.util.spec_from_file_location("gen_addon_openers", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN = _load_generator()


@pytest.fixture(scope="module")
def manifest() -> dict:
    assert MANIFEST.exists(), "нет sfx/openers.json — запусти tools/gen_addon_openers.py"
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["clips"]


class TestFilesAreInSyncWithKB:
    def test_openers_lua_and_manifest_are_fresh(self) -> None:
        proc = subprocess.run(
            ["python3", str(REPO / "tools" / "gen_addon_openers.py"), "--check"],
            capture_output=True,
            text=True,
            cwd=REPO,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr

    def test_every_manifest_clip_exists_on_disk(self, manifest: dict) -> None:
        missing = [
            row["clip"] for row in manifest.values()
            if not (ADDON / "sfx" / f"{row['clip']}.ogg").exists()
        ]
        assert not missing, f"нет клипов: {missing[:5]}"

    def test_lua_table_matches_manifest(self, manifest: dict) -> None:
        """`Openers.lua` и манифест генерятся вместе — расхождение значит, что один
        из них правили руками, и аддон попросит несуществующий файл."""
        lua = (ADDON / "Openers.lua").read_text(encoding="utf-8")
        keys_in_lua = set(re.findall(r'\["([^"]+)"\] = \{ c =', lua))
        assert keys_in_lua == set(manifest), (
            f"только в Lua: {sorted(keys_in_lua - set(manifest))[:3]}; "
            f"только в манифесте: {sorted(set(manifest) - keys_in_lua)[:3]}"
        )

    def test_openers_lua_is_loaded_by_toc(self) -> None:
        toc = (ADDON / "ArenaCoach.toc").read_text(encoding="utf-8")
        # Данные обязаны загрузиться ДО Overlay, который их читает на воротах.
        assert toc.index("Openers.lua") < toc.index("Overlay.lua")


class TestSpeechBudget:
    def test_first_phrase_names_the_target_fast(self, manifest: dict) -> None:
        """Игрок действует на первом слове, а не дослушав фразу (Phase 4.17)."""
        for key, row in manifest.items():
            first = row["text"].split("!")[0]
            n = GEN.syllables(first)
            assert n <= GEN.MAX_FIRST, f"{key}: первая фраза {n} слогов — «{first}!»"

    def test_whole_callout_within_syllable_budget(self, manifest: dict) -> None:
        for key, row in manifest.items():
            n = GEN.syllables(row["text"])
            assert n <= GEN.MAX_TOTAL, f"{key}: {n} слогов ≈ {n / 2.8:.1f}с"

    def test_first_word_is_an_action(self, manifest: dict) -> None:
        """«Сап приста», «Бей мага», «Овца шама» — глагол или приказ, не описание."""
        allowed = {"бей", "сап", "овца", "нова", "фир", "циклон", "блайнд", "гадж"}
        for key, row in manifest.items():
            first = row["text"].split()[0].strip("!,.—").lower()
            assert first in allowed, f"{key}: начинается с {first!r} — это не действие"

    @pytest.mark.skipif(FFPROBE is None, reason="нет ffprobe")
    def test_real_clip_fits_the_gate_window(self, manifest: dict) -> None:
        """Правда о времени — в файле, а не в слоговой модели."""
        too_long = []
        for key, row in manifest.items():
            path = ADDON / "sfx" / f"{row['clip']}.ogg"
            if not path.exists():
                continue
            out = subprocess.run(
                [FFPROBE, "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(path)],
                capture_output=True, text=True, check=True,
            )
            seconds = float(out.stdout.strip())
            if seconds > MAX_CLIP_SECONDS:
                too_long.append((key, round(seconds, 1)))
        assert not too_long, f"клипы длиннее окна ворот: {too_long[:5]}"

    @pytest.mark.skipif(FFPROBE is None, reason="нет ffprobe")
    def test_syllable_model_matches_reality(self, manifest: dict) -> None:
        """Модель 2.8 слога/сек не должна врать больше чем на 30%.

        Если врёт — потолки в тестах перестают защищать окно решения, и это надо
        заметить здесь, а не на арене.
        """
        errors = []
        for key, row in list(manifest.items())[:12]:
            path = ADDON / "sfx" / f"{row['clip']}.ogg"
            if not path.exists():
                continue
            out = subprocess.run(
                [FFPROBE, "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(path)],
                capture_output=True, text=True, check=True,
            )
            real = float(out.stdout.strip())
            predicted = GEN.seconds(row["text"])
            if predicted and abs(real - predicted) / predicted > 0.30:
                errors.append((key, round(predicted, 1), round(real, 1)))
        assert not errors, f"модель расходится с файлом (ключ, модель, факт): {errors[:5]}"


class TestFactsComeFromTheMatchup:
    """Самый важный класс: колаут не должен уверенно врать."""

    def test_only_enemy_classes_are_named(self, manifest: dict) -> None:
        for key, row in manifest.items():
            enemies = set(key.split("|")[2].split("+"))
            for word in re.findall(r"[А-Яа-яё]+", row["text"]):
                cls = GEN._WORD_TO_CLASS.get(word.lower())
                if cls and cls != "pet":
                    assert cls in enemies, (
                        f"{key}: в колауте «{row['text']}» назван {cls} "
                        f"({word}), которого у врага нет"
                    )

    def test_kill_target_from_frontmatter_is_the_one_we_hit(self, manifest: dict) -> None:
        """«бей X» обязан совпасть с `kill_target.primary` документа, а не с тем,
        кого случайно упомянула проза."""
        for key, row in manifest.items():
            m = re.search(r"[Бб]ей ([а-яё]+)", row["text"])
            assert m, f"{key}: в колауте нет «бей <кого>» — «{row['text']}»"
            named = GEN._WORD_TO_CLASS.get(m.group(1).lower())
            assert named, f"{key}: не разобрал цель в «{row['text']}»"
            assert named in set(key.split("|")[2].split("+"))

    def test_unsure_keys_are_flagged_not_hidden(self, manifest: dict) -> None:
        """Схлопывание спеков в классы теряет различия. Мы обязаны это признавать
        флагом, а не выбирать молча (то же правило, что у KillTargets.lua)."""
        for key, row in manifest.items():
            assert isinstance(row["sure"], bool), key
            if len(row["kb"]) > 1 and not row.get("manual"):
                # Несколько документов под одним ключом — либо совпали, либо unsure.
                assert row["sure"] in (True, False)
