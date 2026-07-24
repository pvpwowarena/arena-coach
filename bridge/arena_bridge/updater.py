"""Автообновление (Phase 4.4): аддон из GitHub Releases + уведомление о мосте.

Мост при старте (до запуска демона) выступает апдейтером аддона:

  1. GET https://api.github.com/repos/<repo>/releases/latest → tag + assets.
  2. Если tag новее собственной версии моста — заметное уведомление в консоль
     («скачай новый мост на /download»). Self-replace бинаря НЕ делаем:
     сборки не подписаны (Gatekeeper/SmartScreen), молчаливая подмена
     исполняемого файла — плохая идея; игрок обновляет мост сам.
  3. Скачивает ArenaCoach.zip из релиза, сравнивает `## Version:` в .toc
     с установленным в `<WoW>/Interface/AddOns/ArenaCoach/` и, если версия
     отличается (или аддон вообще не установлен), раскладывает свежие файлы:
     распаковка в staging-папку → бэкап старой (ArenaCoach.bak) → rename.
     После обновления игроку достаточно `/reload` (или перезапуска клиента).

Отказоустойчивость: любой сбой (нет сети, GitHub недоступен, битый zip)
логируется и НЕ мешает запуску демона — автообновление строго best-effort.
Отключение: `--no-update` или `BRIDGE_AUTO_UPDATE=0`.

SavedVariables игрока живут в `WTF/` и обновлением не затрагиваются.
"""

from __future__ import annotations

import io
import logging
import shutil
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import httpx

log = logging.getLogger(__name__)

#: Репозиторий с релизами (публичный) — источник обновлений.
UPDATE_REPO = "pvpwowarena/arena-coach"
DOWNLOAD_PAGE = "https://pvpwowarena.surprise4you.dev/download"
_ADDON_ASSET = "ArenaCoach.zip"
_ADDON_DIR = "ArenaCoach"
_HTTP_TIMEOUT = 8.0

FetchJson = Callable[[str], "dict[str, object] | None"]
FetchBytes = Callable[[str], "bytes | None"]


# ── HTTP (заменяется фейками в тестах) ───────────────────────────────────────


def _http_get_json(url: str) -> dict[str, object] | None:
    try:
        resp = httpx.get(
            url,
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={"Accept": "application/vnd.github+json"},
        )
        if not resp.is_success:
            log.warning("Автообновление: %s → HTTP %s", url, resp.status_code)
            return None
        data = resp.json()
        return data if isinstance(data, dict) else None
    except Exception as exc:  # сеть/DNS/TLS — не мешаем запуску
        log.warning("Автообновление: запрос %s не удался (%s)", url, exc)
        return None


def _http_get_bytes(url: str) -> bytes | None:
    try:
        resp = httpx.get(url, timeout=_HTTP_TIMEOUT * 4, follow_redirects=True)
        if not resp.is_success:
            log.warning("Автообновление: скачивание %s → HTTP %s", url, resp.status_code)
            return None
        return resp.content
    except Exception as exc:
        log.warning("Автообновление: скачивание %s не удалось (%s)", url, exc)
        return None


# ── Версии ───────────────────────────────────────────────────────────────────


def parse_version(raw: str) -> tuple[int, ...] | None:
    """'v0.5.0' / '0.5.0' → (0, 5, 0); None, если не похоже на версию."""
    cleaned = raw.strip().lstrip("vV")
    if not cleaned:
        return None
    parts: list[int] = []
    for chunk in cleaned.split("."):
        digits = ""
        for ch in chunk:
            if ch.isdigit():
                digits += ch
            else:
                break  # '0-rc1' → '0'
        if not digits:
            return None
        parts.append(int(digits))
    return tuple(parts)


def parse_toc_version(toc_text: str) -> str | None:
    """Достать '## Version: 0.2.2' из текста .toc-файла."""
    for line in toc_text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("## version:"):
            value = stripped.split(":", 1)[1].strip()
            return value or None
    return None


# ── Данные релиза ────────────────────────────────────────────────────────────


@dataclass
class ReleaseInfo:
    """Свежий GitHub-релиз: тег + карта asset'ов name → download URL."""

    tag: str
    assets: dict[str, str] = field(default_factory=dict)


def fetch_latest_release(
    repo: str = UPDATE_REPO, fetch_json: FetchJson = _http_get_json
) -> ReleaseInfo | None:
    """Прочитать последний релиз репо; None при любом сбое."""
    data = fetch_json(f"https://api.github.com/repos/{repo}/releases/latest")
    if data is None:
        return None
    tag = str(data.get("tag_name") or "")
    if not tag:
        return None
    assets: dict[str, str] = {}
    raw_assets = data.get("assets")
    if isinstance(raw_assets, list):
        for item in raw_assets:
            if isinstance(item, dict):
                name = str(item.get("name") or "")
                url = str(item.get("browser_download_url") or "")
                if name and url:
                    assets[name] = url
    return ReleaseInfo(tag=tag, assets=assets)


def bridge_update_notice(current_version: str, release: ReleaseInfo) -> str | None:
    """Сообщение «есть новый мост», если тег релиза новее нашей версии."""
    latest = parse_version(release.tag)
    current = parse_version(current_version)
    if latest is None or current is None or latest <= current:
        return None
    return (
        f"⬆️  Доступна новая версия моста: {release.tag} (у тебя v{current_version}). "
        f"Скачай на {DOWNLOAD_PAGE} — старый мост продолжит работать, но без новых фиксов."
    )


# ── Обновление аддона ────────────────────────────────────────────────────────


def _safe_members(zf: zipfile.ZipFile) -> list[tuple[zipfile.ZipInfo, Path]]:
    """Члены архива из папки ArenaCoach/ с нормализацией и анти-traversal.

    PowerShell `Compress-Archive` пишет пути с backslash'ами — нормализуем.
    Записи вне ArenaCoach/, абсолютные и с '..' молча пропускаются.
    """
    members: list[tuple[zipfile.ZipInfo, Path]] = []
    for info in zf.infolist():
        name = info.filename.replace("\\", "/")
        if name.endswith("/"):
            continue  # директории создаём по файлам
        parts = Path(name).parts
        if not parts or parts[0] != _ADDON_DIR:
            continue
        if any(p in ("..", "") for p in parts) or Path(name).is_absolute():
            continue
        members.append((info, Path(*parts[1:])))  # путь ОТНОСИТЕЛЬНО ArenaCoach/
    return members


def _zip_toc_version(zf: zipfile.ZipFile) -> str | None:
    for info, rel in _safe_members(zf):
        if rel == Path("ArenaCoach.toc"):
            return parse_toc_version(zf.read(info).decode("utf-8", errors="replace"))
    return None


def installed_addon_version(addons_dir: Path) -> str | None:
    """Версия установленного аддона из его .toc; None, если не установлен."""
    toc = addons_dir / _ADDON_DIR / "ArenaCoach.toc"
    if not toc.is_file():
        return None
    try:
        return parse_toc_version(toc.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return None


def update_addon(
    wow_path: Path,
    release: ReleaseInfo,
    fetch_bytes: FetchBytes = _http_get_bytes,
) -> str | None:
    """Обновить/установить аддон из релиза. Возвращает сообщение или None.

    None = обновление не потребовалось (актуален) или не удалось (залогировано).
    """
    asset_url = release.assets.get(_ADDON_ASSET)
    if not asset_url:
        log.debug("Автообновление: в релизе %s нет %s", release.tag, _ADDON_ASSET)
        return None

    interface_dir = wow_path / "Interface"
    if not interface_dir.exists():
        log.warning(
            "Автообновление: %s не найдена — путь к WoW неверный? Аддон не трогаю.",
            interface_dir,
        )
        return None
    addons_dir = interface_dir / "AddOns"

    raw = fetch_bytes(asset_url)
    if raw is None:
        return None

    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        log.warning("Автообновление: %s из релиза %s повреждён", _ADDON_ASSET, release.tag)
        return None

    with zf:
        members = _safe_members(zf)
        new_version = _zip_toc_version(zf)
        if new_version is None or not members:
            log.warning(
                "Автообновление: в %s нет %s/ArenaCoach.toc — пропускаю", _ADDON_ASSET, _ADDON_DIR
            )
            return None

        current = installed_addon_version(addons_dir)
        if current == new_version:
            log.info("Аддон актуален (v%s)", current)
            return None

        # 1) staging: распаковываем во временную папку рядом
        staging = addons_dir / f".{_ADDON_DIR}.new"
        target = addons_dir / _ADDON_DIR
        backup = addons_dir / f"{_ADDON_DIR}.bak"
        try:
            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True)
            for info, rel in members:
                dest = staging / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(info))
            if not (staging / "ArenaCoach.toc").is_file():
                raise OSError("в staging нет ArenaCoach.toc")

            # 2) бэкап текущей версии и подмена
            if backup.exists():
                shutil.rmtree(backup)
            if target.exists():
                target.rename(backup)
            staging.rename(target)
        except OSError as exc:
            log.warning("Автообновление аддона не удалось: %s", exc)
            # откат: вернуть бэкап, если успели убрать рабочую папку
            if not target.exists() and backup.exists():
                backup.rename(target)
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            return None

    if current is None:
        return (
            f"📦 Аддон ArenaCoach v{new_version} установлен в {addons_dir}. "
            "Перезапусти WoW (или /reload), включи его в списке аддонов."
        )
    return (
        f"📦 Аддон обновлён: v{current} → v{new_version} (бэкап: {backup.name}). "
        "Сделай /reload в игре, чтобы подхватить."
    )


# ── Оркестратор ──────────────────────────────────────────────────────────────


def run_auto_update(
    wow_path: Path,
    current_version: str,
    repo: str = UPDATE_REPO,
    fetch_json: FetchJson = _http_get_json,
    fetch_bytes: FetchBytes = _http_get_bytes,
) -> list[str]:
    """Один проход автообновления при старте моста. Возвращает уведомления.

    Никогда не бросает: любой сбой = warning в лог + пустой список.
    """
    notices: list[str] = []
    try:
        release = fetch_latest_release(repo, fetch_json)
        if release is None:
            log.info("Автообновление: релизы недоступны (офлайн?) — пропускаю")
            return notices

        notice = bridge_update_notice(current_version, release)
        if notice:
            notices.append(notice)
            log.warning(notice)

        addon_msg = update_addon(wow_path, release, fetch_bytes)
        if addon_msg:
            notices.append(addon_msg)
            log.warning(addon_msg)
    except Exception as exc:  # страховка: апдейтер не должен ронять демон
        log.warning("Автообновление: непредвиденная ошибка (%s) — пропускаю", exc)
    return notices
