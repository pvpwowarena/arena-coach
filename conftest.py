"""Корневой conftest — общие фикстуры для всех test-наборов (backend, ingest).

Расположен на корне `arena-coach/`, чтобы избежать конфликта одноимённых `tests/`
пакетов в backend/ и ingest/.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    """Корень репо `arena-coach/`."""
    return Path(__file__).resolve().parent


@pytest.fixture
def kb_dir(repo_root: Path) -> Path:
    return repo_root / "kb"


@pytest.fixture
def glossary_path(kb_dir: Path) -> Path:
    return kb_dir / "glossary" / "abilities.json"


@pytest.fixture
def drafts_dir(kb_dir: Path) -> Path:
    return kb_dir / "drafts"


@pytest.fixture
def matchups_dir(kb_dir: Path) -> Path:
    return kb_dir / "matchups"


@pytest.fixture
def fixtures_dir(repo_root: Path) -> Path:
    """Тестовые фикстуры backend'а."""
    return repo_root / "backend" / "tests" / "fixtures"


@pytest.fixture
def workspace_parent(repo_root: Path) -> Path:
    """Родительская папка репо — где лежат исходные Mirlol-файлы."""
    return repo_root.parent


@pytest.fixture
def mirlol_rm_file(workspace_parent: Path) -> Path:
    p = workspace_parent / "WOW TBC ARENA - Rogue  Mage.md"
    if not p.is_file():
        pytest.skip(f"Mirlol RM file not found at {p}")
    return p


@pytest.fixture
def mirlol_rp_file(workspace_parent: Path) -> Path:
    p = workspace_parent / "WOW TBC ARENA - Rogue Priest.md"
    if not p.is_file():
        pytest.skip(f"Mirlol RP file not found at {p}")
    return p
