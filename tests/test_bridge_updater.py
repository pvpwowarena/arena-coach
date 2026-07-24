"""Тесты Phase 4.4: автообновление аддона + уведомление о новой версии моста.

Сеть не трогаем — fetch_json/fetch_bytes подменяются фейками; zip'ы собираются
в памяти (включая вариант с backslash-путями, как их пишет PowerShell
Compress-Archive на windows-runner'е).
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from arena_bridge.updater import (
    ReleaseInfo,
    bridge_update_notice,
    fetch_latest_release,
    installed_addon_version,
    parse_toc_version,
    parse_version,
    run_auto_update,
    update_addon,
)

_TOC = "## Interface: 20400\n## Title: ArenaCoach\n## Version: {v}\nCore.lua\n"


def _addon_zip(version: str, sep: str = "/", extra: dict[str, str] | None = None) -> bytes:
    """ArenaCoach.zip в памяти; sep='\\\\' имитирует Compress-Archive."""
    buf = io.BytesIO()
    files = {
        f"ArenaCoach{sep}ArenaCoach.toc": _TOC.format(v=version),
        f"ArenaCoach{sep}Core.lua": f"-- ArenaCoach {version}\n",
        f"ArenaCoach{sep}Tracker.lua": "-- tracker\n",
    }
    if extra:
        files.update(extra)
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _wow(tmp_path: Path, installed_version: str | None = None) -> Path:
    wow = tmp_path / "wow"
    (wow / "Interface" / "AddOns").mkdir(parents=True)
    (wow / "Logs").mkdir()
    if installed_version is not None:
        addon = wow / "Interface" / "AddOns" / "ArenaCoach"
        addon.mkdir()
        (addon / "ArenaCoach.toc").write_text(_TOC.format(v=installed_version), encoding="utf-8")
        (addon / "Core.lua").write_text("-- old\n", encoding="utf-8")
    return wow


def _release(tag: str = "v0.5.0", with_addon: bool = True) -> ReleaseInfo:
    assets = {"arena-bridge.exe": "https://x/exe"}
    if with_addon:
        assets["ArenaCoach.zip"] = "https://x/ArenaCoach.zip"
    return ReleaseInfo(tag=tag, assets=assets)


# ── Версии ───────────────────────────────────────────────────────────────────


class TestVersions:
    def test_parse_version(self) -> None:
        assert parse_version("v0.5.0") == (0, 5, 0)
        assert parse_version("0.10.2") == (0, 10, 2)
        assert parse_version("v1.0.0-rc1") == (1, 0, 0)
        assert parse_version("мусор") is None
        assert parse_version("") is None

    def test_ordering(self) -> None:
        v = parse_version
        assert v("v0.5.0") > v("v0.4.1")  # type: ignore[operator]
        assert v("v0.10.0") > v("v0.9.9")  # type: ignore[operator]

    def test_parse_toc_version(self) -> None:
        assert parse_toc_version(_TOC.format(v="0.2.2")) == "0.2.2"
        assert parse_toc_version("## Title: X\n") is None
        assert parse_toc_version("") is None


# ── bridge_update_notice ─────────────────────────────────────────────────────


class TestBridgeNotice:
    def test_newer_release_notifies(self) -> None:
        notice = bridge_update_notice("0.4.1", _release("v0.5.0"))
        assert notice is not None
        assert "v0.5.0" in notice or "0.5.0" in notice

    def test_same_or_older_silent(self) -> None:
        assert bridge_update_notice("0.5.0", _release("v0.5.0")) is None
        assert bridge_update_notice("0.6.0", _release("v0.5.0")) is None

    def test_garbage_tag_silent(self) -> None:
        assert bridge_update_notice("0.5.0", _release("nightly")) is None


# ── fetch_latest_release ─────────────────────────────────────────────────────


class TestFetchRelease:
    def test_parses_assets(self) -> None:
        payload: dict[str, object] = {
            "tag_name": "v0.5.0",
            "assets": [
                {"name": "ArenaCoach.zip", "browser_download_url": "https://x/a.zip"},
                {"name": "arena-bridge.exe", "browser_download_url": "https://x/b.exe"},
            ],
        }
        rel = fetch_latest_release("r/r", fetch_json=lambda url: payload)
        assert rel is not None
        assert rel.tag == "v0.5.0"
        assert rel.assets["ArenaCoach.zip"] == "https://x/a.zip"

    def test_offline_returns_none(self) -> None:
        assert fetch_latest_release("r/r", fetch_json=lambda url: None) is None

    def test_missing_tag_returns_none(self) -> None:
        assert fetch_latest_release("r/r", fetch_json=lambda url: {"assets": []}) is None


# ── update_addon ─────────────────────────────────────────────────────────────


class TestUpdateAddon:
    def test_fresh_install(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path, installed_version=None)
        msg = update_addon(wow, _release(), fetch_bytes=lambda url: _addon_zip("0.3.0"))
        assert msg is not None and "установлен" in msg
        assert installed_addon_version(wow / "Interface" / "AddOns") == "0.3.0"
        assert (wow / "Interface" / "AddOns" / "ArenaCoach" / "Core.lua").is_file()

    def test_upgrade_makes_backup(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path, installed_version="0.2.2")
        msg = update_addon(wow, _release(), fetch_bytes=lambda url: _addon_zip("0.3.0"))
        assert msg is not None and "0.2.2" in msg and "0.3.0" in msg
        addons = wow / "Interface" / "AddOns"
        assert installed_addon_version(addons) == "0.3.0"
        bak_toc = addons / "ArenaCoach.bak" / "ArenaCoach.toc"
        assert parse_toc_version(bak_toc.read_text(encoding="utf-8")) == "0.2.2"
        assert not (addons / ".ArenaCoach.new").exists()  # staging убран

    def test_same_version_untouched(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path, installed_version="0.2.2")
        marker = wow / "Interface" / "AddOns" / "ArenaCoach" / "Core.lua"
        before = marker.read_text(encoding="utf-8")
        msg = update_addon(wow, _release(), fetch_bytes=lambda url: _addon_zip("0.2.2"))
        assert msg is None
        assert marker.read_text(encoding="utf-8") == before  # файлы не тронуты

    def test_backslash_zip_from_powershell(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path, installed_version="0.2.2")
        msg = update_addon(wow, _release(), fetch_bytes=lambda url: _addon_zip("0.3.0", sep="\\"))
        assert msg is not None
        addons = wow / "Interface" / "AddOns"
        assert installed_addon_version(addons) == "0.3.0"
        assert (addons / "ArenaCoach" / "Tracker.lua").is_file()
        # никаких literal-имён с backslash'ами
        assert not list(addons.glob("ArenaCoach*\\*"))

    def test_traversal_entries_skipped(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path)
        evil = {"ArenaCoach/../evil.lua": "-- evil", "/abs.lua": "-- abs", "other/x.lua": "-- x"}
        msg = update_addon(wow, _release(), fetch_bytes=lambda url: _addon_zip("0.3.0", extra=evil))
        assert msg is not None
        addons = wow / "Interface" / "AddOns"
        assert not (addons / "evil.lua").exists()
        assert not (addons.parent / "evil.lua").exists()
        assert not (addons / "other").exists()

    def test_corrupted_zip_safe(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path, installed_version="0.2.2")
        msg = update_addon(wow, _release(), fetch_bytes=lambda url: b"not a zip")
        assert msg is None
        assert installed_addon_version(wow / "Interface" / "AddOns") == "0.2.2"

    def test_download_failure_safe(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path, installed_version="0.2.2")
        msg = update_addon(wow, _release(), fetch_bytes=lambda url: None)
        assert msg is None

    def test_no_interface_dir_skips(self, tmp_path: Path) -> None:
        wow = tmp_path / "broken-wow"
        wow.mkdir()
        msg = update_addon(wow, _release(), fetch_bytes=lambda url: _addon_zip("0.3.0"))
        assert msg is None
        assert not (wow / "Interface").exists()  # ничего не насоздавали

    def test_release_without_addon_asset(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path)
        msg = update_addon(wow, _release(with_addon=False), fetch_bytes=lambda url: b"")
        assert msg is None


# ── run_auto_update ──────────────────────────────────────────────────────────


class TestRunAutoUpdate:
    def test_full_pass(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path, installed_version="0.2.2")
        payload: dict[str, object] = {
            "tag_name": "v9.9.9",
            "assets": [{"name": "ArenaCoach.zip", "browser_download_url": "https://x/a.zip"}],
        }
        notices = run_auto_update(
            wow,
            current_version="0.5.0",
            fetch_json=lambda url: payload,
            fetch_bytes=lambda url: _addon_zip("0.9.0"),
        )
        assert len(notices) == 2  # новый мост + обновлён аддон
        assert any("моста" in n for n in notices)
        assert any("Аддон" in n for n in notices)

    def test_offline_is_quiet(self, tmp_path: Path) -> None:
        wow = _wow(tmp_path)
        notices = run_auto_update(
            wow, current_version="0.5.0", fetch_json=lambda url: None, fetch_bytes=lambda url: None
        )
        assert notices == []

    def test_never_raises(self, tmp_path: Path) -> None:
        def _boom(url: str) -> dict[str, object] | None:
            raise RuntimeError("взрыв")

        notices = run_auto_update(tmp_path, current_version="0.5.0", fetch_json=_boom)
        assert notices == []
