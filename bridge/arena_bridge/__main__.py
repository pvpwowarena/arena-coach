"""arena-bridge CLI entry point.

Phase 4 skeleton. Запускает asyncio loop:
1. sv_tail — polling ArenaCoachDB (SavedVariables.lua) для post-match summary.
2. chat_tail — watchdog/poll Logs/Chat-*.txt для realtime [AC|...] событий.
3. normalizer — raw events → canonical event schema.
4. ws_client — устойчивый WSS-коннект к backend с bearer-auth.

В Phase 1 — только заглушка: печатает конфигурацию и выходит.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(prog="arena-bridge", description="Arena Coach local bridge")
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Загрузить конфиг и распечатать его, не запускать сам demon (Phase 1 default).",
    )
    args = parser.parse_args()

    if args.check_config:
        # TODO(Phase 4): загрузить settings через pydantic-settings, валидировать пути к
        # SavedVariables.lua и Logs/, проверить токен.
        print("Arena Bridge — Phase 4 skeleton. Реализация будет позже.")
        return 0

    print("Arena Bridge demon ещё не реализован (Phase 4).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
