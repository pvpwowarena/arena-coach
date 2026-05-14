# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec для arena-bridge.exe (Windows, onefile, console).
#
# Сборка локально (из папки arena-coach/bridge/):
#   pip install pyinstaller
#   pyinstaller arena-bridge.spec
#
# Результат: dist/arena-bridge.exe
#
# В папке рядом с .exe игрок кладёт bridge.env — он автоматически подхватится.

import sys
from pathlib import Path

block_cipher = None

# Корень пакета
pkg_root = Path(SPECPATH)  # noqa: F821  — injected by PyInstaller

a = Analysis(
    [str(pkg_root / "arena_bridge" / "__main__.py")],
    pathex=[str(pkg_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # pydantic использует dynamic import для validators
        "pydantic",
        "pydantic.v1",
        "pydantic_core",
        # httpx транспорты
        "httpx._transports.default",
        "httpx._transports.asgi",
        "httpx._transports.wsgi",
        # watchdog backends (Windows)
        "watchdog.observers.winapi",
        "watchdog.observers.read_directory_changes",
        # asyncio Windows SelectorEventLoop
        "asyncio.windows_events",
        "asyncio.windows_utils",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Не нужны в CLI-демоне
        "tkinter",
        "unittest",
        "email",
        "html",
        "http.server",
        "xmlrpc",
        "pdb",
        "doctest",
        "difflib",
        "distutils",
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
    upx=True,           # Сжатие UPX если установлен (уменьшает размер ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,       # Консольное окно — игрок видит логи
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon=str(pkg_root / "assets" / "arena-bridge.ico"),  # раскомментировать если есть иконка
)
