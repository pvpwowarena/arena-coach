"""Точка входа `python -m arena_coach`. Phase 1: только CLI-проверка KB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(prog="arena-coach", description="Arena Coach backend CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_validate = sub.add_parser("validate-kb", help="Прогнать все .md в директории через KB-схему")
    p_validate.add_argument("path", type=Path, help="Директория с .md-документами")

    args = parser.parse_args()

    if args.cmd == "validate-kb":
        from arena_coach.kb.loader import validate_directory

        ok, errors = validate_directory(args.path)
        if errors:
            print(f"FAIL: {len(errors)} ошибок валидации:", file=sys.stderr)
            for path, err in errors:
                print(f"  {path}: {err}", file=sys.stderr)
            return 1
        print(f"OK: {ok} документов прошли валидацию")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
