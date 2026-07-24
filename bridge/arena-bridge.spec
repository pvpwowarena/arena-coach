# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec для arena-bridge — onefile, console.
#
# Кросс-платформенный spec:
#   • Windows  → dist/arena-bridge.exe
#   • macOS    → dist/arena-bridge  (Apple Silicon arm64, unsigned)
#
# Сборка локально (из папки arena-coach/bridge/):
#   pip install pyinstaller
#   pyinstaller arena-bridge.spec
#
# В папке рядом с бинарём игрок кладёт bridge.env — он автоматически подхватится.

import sys
from pathlib import Path

block_cipher = None

# Корень пакета
pkg_root = Path(SPECPATH)  # noqa: F821  — injected by PyInstaller

# Платформо-зависимые hidden imports.
# PyInstaller на macOS не сможет найти Windows-only модули и упадёт —
# поэтому добавляем их условно.
_common_hidden = [
    # Пакет bridge целиком: entry-скрипт (bridge_entry.py) импортирует его
    # абсолютно, а runtime-модули подгружаются лениво внутри функций —
    # перечисляем явно, чтобы Analysis гарантированно включил их в сборку.
    "arena_bridge",
    "arena_bridge.chat_tail",
    "arena_bridge.combat_tail",
    "arena_bridge.config",
    "arena_bridge.env_loader",
    "arena_bridge.hint_poller",
    "arena_bridge.local_tts",
    "arena_bridge.normalizer",
    "arena_bridge.sv_tail",
    "arena_bridge.updater",
    "arena_bridge.ws_client",
    # pydantic использует dynamic import для validators
    "pydantic",
    "pydantic.v1",
    "pydantic_core",
    # httpx транспорты
    "httpx._transports.default",
    "httpx._transports.asgi",
    "httpx._transports.wsgi",
]

if sys.platform == "win32":
    _platform_hidden = [
        # watchdog backends (Windows)
        "watchdog.observers.winapi",
        "watchdog.observers.read_directory_changes",
        # asyncio Windows SelectorEventLoop
        "asyncio.windows_events",
        "asyncio.windows_utils",
    ]
elif sys.platform == "darwin":
    _platform_hidden = [
        # watchdog backends (macOS — FSEvents)
        "watchdog.observers.fsevents",
        # asyncio Unix selectors
        "asyncio.unix_events",
        "selectors",
    ]
else:
    _platform_hidden = []

# ⚠ Entry — ТОЛЬКО обёртка bridge_entry.py. Прямой запуск
# arena_bridge/__main__.py ломает относительные импорты пакета
# (баг бинарей v0.3.0: "attempted relative import with no known parent package").
a = Analysis(
    [str(pkg_root / "bridge_entry.py")],
    pathex=[str(pkg_root)],
    binaries=[],
    datas=[],
    hiddenimports=_common_hidden + _platform_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # ⚠ Исключаем ТОЛЬКО tkinter. Прежний агрессивный список ломал
        # runtime: httpx тянет stdlib "email" (заодно "html"/"http") лениво —
        # с excludes демон падал "No module named 'email'" при первом
        # импорте ws_client. Экономия на stdlib-текстовых модулях копеечная,
        # корректность важнее.
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="arena-bridge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX повреждает Mach-O бинарники на macOS arm64 — включаем только на Windows.
    upx=(sys.platform == "win32"),
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,       # Терминальный CLI — игрок видит логи
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon=str(pkg_root / "assets" / "arena-bridge.ico"),  # раскомментировать если есть иконка
)
