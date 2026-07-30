"""`ops/scripts/read-db-url.sh` — чтение DATABASE_URL из systemd EnvironmentFile.

Почему шаг деплоя вообще покрыт тестом: он дважды ронял прод, и оба раза МОЛЧА.

1. Инцидент 30.07.2026 (`docs/incident-2026-07-30-500-events.md`): в `vps-deploy.sh`
   стояло `alembic upgrade head 2>/dev/null || ( . api.env; alembic ... )`. Без
   `DATABASE_URL` дефолт в `Settings` — относительный `sqlite:///./coach.db`, поэтому
   alembic мигрировал файл рядом с кодом, выходил с кодом 0, и боевая БД годами
   оставалась без миграций.
2. Фикс 4.16 первой редакции добавил `. api.env` под `set -euo pipefail` — и деплой
   перестал доходить до рестарта вовсе. Причина: `api.env` это systemd
   EnvironmentFile, а не shell-скрипт. Значение вида `a(b)c` даёт
   `syntax error near unexpected token '('`.

Отсюда правило: **файл окружения systemd нельзя исполнять шеллом** — из него нужно
вычитывать значение. Тесты ниже фиксируют формат, который обязаны понимать.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ABS_URL = "sqlite+aiosqlite:////var/lib/arena-coach/coach.db"


@pytest.fixture
def script(repo_root: Path) -> Path:
    path = repo_root / "ops" / "scripts" / "read-db-url.sh"
    assert path.is_file(), path
    return path


def _run(script: Path, env_text: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    if shutil.which("bash") is None:  # pragma: no cover — bash есть и в CI, и на ВПС
        pytest.skip("bash недоступен")
    env_file = tmp_path / "api.env"
    env_file.write_text(env_text, encoding="utf-8")
    return subprocess.run(
        ["bash", str(script), str(env_file)],
        capture_output=True,
        text=True,
        check=False,
    )


class TestHappyPath:
    def test_plain_value(self, script: Path, tmp_path: Path) -> None:
        out = _run(script, f"DISCORD_BOT_TOKEN=x\nDATABASE_URL={ABS_URL}\n", tmp_path)
        assert out.returncode == 0, out.stderr
        assert out.stdout.strip() == ABS_URL

    def test_last_occurrence_wins(self, script: Path, tmp_path: Path) -> None:
        """systemd берёт последнее вхождение ключа — повторяем поведение."""
        text = f"DATABASE_URL=sqlite+aiosqlite:///./wrong.db\nDATABASE_URL={ABS_URL}\n"
        assert _run(script, text, tmp_path).stdout.strip() == ABS_URL

    @pytest.mark.parametrize("quote", ['"', "'"])
    def test_quotes_stripped(self, script: Path, tmp_path: Path, quote: str) -> None:
        out = _run(script, f"DATABASE_URL={quote}{ABS_URL}{quote}\n", tmp_path)
        assert out.stdout.strip() == ABS_URL

    def test_leading_whitespace(self, script: Path, tmp_path: Path) -> None:
        assert _run(script, f"   DATABASE_URL={ABS_URL}\n", tmp_path).stdout.strip() == ABS_URL


class TestShellHostileValues:
    """Ровно то, на чём умер `. api.env`: файл читается, а не исполняется."""

    @pytest.mark.parametrize(
        "hostile",
        [
            "WEIRD=a(b)c",
            "NOTE=hello world",
            "GREETING=don't",
            "CMD=$(rm -rf /)",
            "BACKTICK=`whoami`",
            "SEMI=a;b",
        ],
    )
    def test_survives_neighbouring_line(self, script: Path, tmp_path: Path, hostile: str) -> None:
        out = _run(script, f"{hostile}\nDATABASE_URL={ABS_URL}\n", tmp_path)
        assert out.returncode == 0, out.stderr
        assert out.stdout.strip() == ABS_URL

    def test_command_substitution_not_executed(self, script: Path, tmp_path: Path) -> None:
        """`$(...)` в значении обязан остаться текстом, а не выполниться."""
        marker = tmp_path / "pwned"
        text = f"EVIL=$(touch {marker})\nDATABASE_URL={ABS_URL}\n"
        assert _run(script, text, tmp_path).stdout.strip() == ABS_URL
        assert not marker.exists(), "значение из env-файла было ВЫПОЛНЕНО"


class TestFailsLoudly:
    def test_missing_key(self, script: Path, tmp_path: Path) -> None:
        out = _run(script, "DISCORD_BOT_TOKEN=x\n", tmp_path)
        assert out.returncode != 0
        assert "DATABASE_URL" in out.stderr

    def test_missing_file(self, script: Path, tmp_path: Path) -> None:
        out = subprocess.run(
            ["bash", str(script), str(tmp_path / "нет-такого.env")],
            capture_output=True,
            text=True,
            check=False,
        )
        assert out.returncode != 0
        assert "не читается" in out.stderr

    def test_no_argument(self, script: Path) -> None:
        out = subprocess.run(["bash", str(script)], capture_output=True, text=True, check=False)
        assert out.returncode != 0
