"""Точка входа для PyInstaller-сборки arena-bridge.

Нельзя указывать в spec напрямую arena_bridge/__main__.py: PyInstaller
запускает entry-файл как top-level скрипт БЕЗ package-контекста, и все
относительные импорты внутри пакета падают с
"ImportError: attempted relative import with no known parent package" —
именно так были сломаны onefile-бинари релиза v0.3.0 (Windows и macOS).

Эта обёртка импортирует пакет абсолютно — у arena_bridge.__main__ появляется
нормальный package-контекст, относительные импорты работают.

Запуск из исходников не меняется: python -m arena_bridge
"""

from __future__ import annotations

import sys

from arena_bridge.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
