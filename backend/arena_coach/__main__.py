"""Точка входа `python -m arena_coach`.

Команды:
  validate-kb <path>   — проверить .md-документы через KB-схему (Phase 1)
  run-bot              — запустить Discord-бот (Phase 2)
  gen-key              — сгенерировать Fernet-ключ (утилита)
  warm-advice <file>   — прогреть кэш LLM-разборов для списка сетапов (Phase 4.7)
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


def _parse_warm_line(raw: str) -> tuple[str | None, list[tuple[str, str | None]]]:
    """'rogue+mage vs ret-paladin+warrior' → ('rogue+mage', [('PALADIN','ret-paladin'),('WARRIOR',None)]).

    Токен-враг = класс ('mage') или спек-slug ('ret-paladin'); спек сводится к
    (базовый_класс_UPPER, спек), класс — к (класс_UPPER, None), чтобы сигнатура
    совпала с той, что строит мост в бою.
    """
    from arena_coach.kb.indexer import comp_part_to_class

    our_part, _, enemy_part = raw.partition(" vs ")
    if not enemy_part:
        our_part, enemy_part = "", raw
    our = our_part.strip() or None
    tokens = [t.strip().lower() for t in enemy_part.replace(" ", "").split("+") if t.strip()]
    enemies: list[tuple[str, str | None]] = []
    for tok in tokens:
        base = comp_part_to_class(tok)
        if base != tok:
            enemies.append((base.upper(), tok))  # спек-slug
        else:
            enemies.append((tok.upper(), None))  # базовый класс
    return our, enemies


def _cmd_warm_advice(comps_file: Path, model_override: str | None) -> int:
    import asyncio
    import logging

    from anthropic import AsyncAnthropic
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from arena_coach.access.advice_store import AdviceStore
    from arena_coach.access.models import Base
    from arena_coach.orchestrator import advice as advice_mod
    from arena_coach.orchestrator.advice import comp_signature
    from arena_coach.shared.settings import settings

    logging.basicConfig(level=logging.WARNING)
    if not settings.anthropic_api_key:
        print("ERROR: ANTHROPIC_API_KEY не задан — нечем генерировать", file=sys.stderr)
        return 1
    if not comps_file.is_file():
        print(f"ERROR: файл со списком сетапов не найден: {comps_file}", file=sys.stderr)
        return 1

    model = model_override or settings.anthropic_model_advice
    raw_lines = comps_file.read_text(encoding="utf-8").splitlines()
    comps = [ln.strip() for ln in raw_lines if ln.strip() and not ln.strip().startswith("#")]
    if not comps:
        print("Список сетапов пуст.", file=sys.stderr)
        return 1

    print(f"Прогрев {len(comps)} сетапов моделью {model} → {settings.database_url}")

    async def _run() -> int:
        engine = create_async_engine(settings.database_url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        store = AdviceStore(async_sessionmaker(engine, expire_on_commit=False))
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        done = 0
        try:
            for raw in comps:
                our, enemies = _parse_warm_line(raw)
                if not enemies:
                    print(f"  ⚠ пропуск (не разобрал врагов): {raw}", file=sys.stderr)
                    continue
                classes = [c for c, _ in enemies]
                specs: list[str | None] = [s for _, s in enemies]
                bracket = f"{len(classes)}v{len(classes)}"
                sig = comp_signature(our, classes, specs, bracket)
                desc = ", ".join(f"{c}({s})" if s else c for c, s in enemies)
                try:
                    res = await advice_mod.generate_comp_advice(
                        client,
                        model,
                        bracket=bracket,
                        enemy_desc=desc,
                        our_comp=our,
                        player_class=None,
                    )
                except Exception as exc:
                    print(f"  ✗ {raw}: {exc}", file=sys.stderr)
                    continue
                if res.text:
                    await store.put(sig, res.text, model)
                    done += 1
                    print(f"  ✓ {raw}")
        finally:
            await client.close()
            await engine.dispose()
        print(f"Готово: прогрето {done}/{len(comps)} сетапов моделью {model}.")
        return 0

    return asyncio.run(_run())


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

    # warm-advice
    p_warm = sub.add_parser(
        "warm-advice",
        help="Прогреть кэш LLM-разборов для списка сетапов (по строке 'our vs enemy')",
    )
    p_warm.add_argument("comps_file", type=Path, help="Файл: строки 'rogue+mage vs mage+mage'")
    p_warm.add_argument(
        "--model", default=None, help="Модель (по умолч. ANTHROPIC_MODEL_ADVICE); напр. Sonnet"
    )

    args = parser.parse_args()

    if args.cmd == "validate-kb":
        return _cmd_validate_kb(args.path)
    if args.cmd == "run-bot":
        return _cmd_run_bot()
    if args.cmd == "gen-key":
        return _cmd_gen_key()
    if args.cmd == "warm-advice":
        return _cmd_warm_advice(args.comps_file, args.model)

    return 2


if __name__ == "__main__":
    sys.exit(main())
