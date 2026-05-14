"""Точка входа `python -m arena_coach`.

Команды:
  validate-kb <path>   — проверить .md-документы через KB-схему (Phase 1)
  run-bot              — запустить Discord-бот (Phase 2)
  gen-key              — сгенерировать Fernet-ключ (утилита)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _cmd_validate_kb(path: Path) -> int:
    from arena_coach.kb.loader import validate_directory

    ok, errors = validate_directory(path)
    if errors:
        print(f"FAIL: {len(errors)} ошибок валидации:", file=sys.stderr)
        for p, err in errors:
            print(f"  {p}: {err}", file=sys.stderr)
        return 1
    print(f"OK: {ok} документов прошли валидацию")
    return 0


def _cmd_run_bot() -> int:
    import asyncio
    import logging

    from arena_coach.shared.settings import settings

    # Логирование
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if not settings.discord_bot_token:
        print("ERROR: DISCORD_BOT_TOKEN не задан в .env", file=sys.stderr)
        return 1
    if not settings.arena_coach_fernet_key:
        print("ERROR: ARENA_COACH_FERNET_KEY не задан в .env", file=sys.stderr)
        return 1

    from arena_coach.bot.client import create_bot

    bot = create_bot()

    async def _run() -> None:
        async with bot:
            await bot.start(settings.discord_bot_token)

    import contextlib

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(_run())
    return 0


def _cmd_gen_key() -> int:
    from cryptography.fernet import Fernet

    key = Fernet.generate_key().decode()
    print(key)
    print(
        "\nСохрани в .env:\nARENA_COACH_FERNET_KEY=" + key,
        file=sys.stderr,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="arena-coach", description="Arena Coach backend CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # validate-kb
    p_validate = sub.add_parser("validate-kb", help="Прогнать все .md в директории через KB-схему")
    p_validate.add_argument("path", type=Path, help="Директория с .md-документами")

    # run-bot
    sub.add_parser("run-bot", help="Запустить Discord-бот")

    # gen-key
    sub.add_parser("gen-key", help="Сгенерировать Fernet-ключ для .env")

    args = parser.parse_args()

    if args.cmd == "validate-kb":
        return _cmd_validate_kb(args.path)
    if args.cmd == "run-bot":
        return _cmd_run_bot()
    if args.cmd == "gen-key":
        return _cmd_gen_key()

    return 2


if __name__ == "__main__":
    sys.exit(main())
