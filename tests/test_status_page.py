"""Smoke-тесты живой страницы статуса (tools/gen_status_page.py) + docs/prod-status.json.

Страница генерится на VPS в vps-deploy.sh (не валит деплой при ошибке), поэтому
сломанный генератор или битый prod-status.json должны ловиться ЗДЕСЬ — до пуша.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def prod_status(repo_root: Path) -> dict:
    return json.loads((repo_root / "docs" / "prod-status.json").read_text(encoding="utf-8"))


def test_prod_status_json_valid(prod_status: dict) -> None:
    """Чеклист правится руками — держим схему: phases/launch, у пунктов name + done:bool."""
    assert prod_status["phases"], "phases пуст"
    assert prod_status["launch"], "launch пуст"
    for item in prod_status["phases"] + prod_status["launch"]:
        assert isinstance(item.get("name"), str) and item["name"]
        assert isinstance(item.get("done"), bool), f"done не bool: {item}"


def test_status_page_generates(repo_root: Path, tmp_path: Path) -> None:
    out = tmp_path / "status.html"
    res = subprocess.run(
        [sys.executable, str(repo_root / "tools" / "gen_status_page.py"), "-o", str(out)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert res.returncode == 0, res.stderr
    page = out.read_text(encoding="utf-8")
    for marker in (
        "Статус проекта",
        "Готовность к запуску",
        "Вариации покрыты",
        'id="s2"',
        'id="s3"',
        'id="s5"',
        "/health",
        "prod-status.json",
    ):
        assert marker in page, f"нет маркера: {marker}"
    # Все канонические составы присутствуют в шапках матриц
    for lbl in ("RM", "RP", "RL", "RD", "RMP", "RRD"):
        assert f"<th>{lbl}</th>" in page, f"нет колонки состава {lbl}"
