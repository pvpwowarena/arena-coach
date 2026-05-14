"""arena-bridge CLI entry point — Phase 4.

Запускает asyncio-демон:
1. chat_tail — polling Logs/Chat-*.txt для [AC|...] событий от аддона.
2. normalizer — raw string → CanonicalEnvelope + обновление SessionState.
3. ws_client (EventClient) — POST /v1/events на backend с bearer-auth.

Запуск:
    arena-bridge --wow-path "C:/WoW" --account MyAccount \\
                 --backend-url https://coach.example.com \\
                 --token <bearer_token> --player-name Vladislav

Или через .env (рекомендуется):
    WOW_INSTALL_PATH="C:/WoW"
    ACCOUNT_NAME="MyAccount"
    BACKEND_URL="https://coach.example.com"
    BRIDGE_BEARER_TOKEN="<token>"
    BRIDGE_PLAYER_NAME="Vladislav"
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
import os
import signal
import sys
from pathlib import Path

log = logging.getLogger("arena_bridge")


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=getattr(logging, level.upper(), logging.INFO),
    )


def _load_config_from_env() -> dict[str, str]:
    """Читаем конфиг из env-переменных. Возвращаем dict с нужными ключами."""
    return {
        "wow_path": os.environ.get("WOW_INSTALL_PATH", ""),
        "account": os.environ.get("ACCOUNT_NAME", ""),
        "backend_url": os.environ.get("BACKEND_URL", ""),
        "token": os.environ.get("BRIDGE_BEARER_TOKEN", ""),
        "player_name": os.environ.get("BRIDGE_PLAYER_NAME", ""),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
        "poll_interval": os.environ.get("BRIDGE_POLL_INTERVAL", "0.5"),
    }


async def _run_bridge(
    log_dir: Path,
    backend_url: str,
    bearer_token: str,
    player_name: str,
    poll_interval: float,
    stop_event: asyncio.Event,
) -> None:
    """Основной asyncio-loop: chat_tail → normalizer → http POST."""
    # Импортируем здесь чтобы не мешать argparse при --check-config
    from .chat_tail import ChatTailer
    from .normalizer import SessionState, normalize_raw
    from .ws_client import EventClient

    session = SessionState()
    client = EventClient(backend_url, bearer_token)

    # Проверяем backend доступность при старте
    if await client.health_check():
        log.info("Backend доступен: %s", backend_url)
    else:
        log.warning("Backend недоступен при старте — буду повторять при отправке")

    tailer = ChatTailer(log_dir, poll_interval)

    log.info(
        "Arena Bridge запущен | лог: %s | игрок: %s | backend: %s",
        log_dir,
        player_name,
        backend_url,
    )

    try:
        async for raw_payload in tailer.lines():
            if stop_event.is_set():
                tailer.stop()
                break

            envelope = normalize_raw(raw_payload, session, player_name)
            if envelope is None:
                continue

            payload = envelope.model_dump()
            ok = await client.send(payload)
            if not ok:
                log.warning("Событие потеряно: %s", raw_payload)

    except asyncio.CancelledError:
        log.info("Bridge: получен CancelledError, завершаю")
        tailer.stop()
    finally:
        await client.close()
        log.info("Arena Bridge остановлен")


def main() -> int:
    env = _load_config_from_env()

    parser = argparse.ArgumentParser(
        prog="arena-bridge",
        description="Arena Coach local bridge — tail Chat-log → POST events → backend",
    )
    parser.add_argument(
        "--wow-path",
        default=env["wow_path"],
        help="Путь к корню установки WoW (содержит папку Logs/). По умолчанию: $WOW_INSTALL_PATH",
    )
    parser.add_argument(
        "--backend-url",
        default=env["backend_url"],
        help="URL backend'а (https://...). По умолчанию: $BACKEND_URL",
    )
    parser.add_argument(
        "--token",
        default=env["token"],
        help="Bearer-токен. По умолчанию: $BRIDGE_BEARER_TOKEN",
    )
    parser.add_argument(
        "--player-name",
        default=env["player_name"],
        help="Имя WoW-персонажа (для envelope). По умолчанию: $BRIDGE_PLAYER_NAME",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=float(env["poll_interval"]),
        help="Интервал polling chat-лога в секундах (default: 0.5)",
    )
    parser.add_argument(
        "--log-level",
        default=env["log_level"],
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Уровень логирования (default: INFO)",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Проверить конфигурацию и выйти (не запускать демон)",
    )

    args = parser.parse_args()
    _setup_logging(args.log_level)

    # ── Валидация ────────────────────────────────────────────────────────────
    errors: list[str] = []

    wow_path = Path(args.wow_path) if args.wow_path else None
    log_dir: Path | None = None

    if not wow_path or not wow_path.exists():
        errors.append(
            f"WoW-путь не найден: '{args.wow_path}'. Укажи --wow-path или $WOW_INSTALL_PATH."
        )
    else:
        log_dir = wow_path / "Logs"
        if not log_dir.exists():
            errors.append(f"Папка Logs/ не найдена: {log_dir}. Убедись что путь к WoW правильный.")

    if not args.backend_url:
        errors.append("URL backend'а не задан. Укажи --backend-url или $BACKEND_URL.")

    if not args.token:
        errors.append("Bearer-токен не задан. Укажи --token или $BRIDGE_BEARER_TOKEN.")

    if not args.player_name:
        errors.append("Имя персонажа не задано. Укажи --player-name или $BRIDGE_PLAYER_NAME.")

    if args.check_config:
        print("=== Arena Bridge — конфигурация ===")
        print(f"  WoW path    : {wow_path or 'НЕ ЗАДАН'}")
        print(f"  Logs dir    : {log_dir or 'НЕ НАЙДЕНА'}")
        print(f"  Backend URL : {args.backend_url or 'НЕ ЗАДАН'}")
        print(f"  Player      : {args.player_name or 'НЕ ЗАДАН'}")
        print(f"  Token       : {'***' if args.token else 'НЕ ЗАДАН'}")
        print(f"  Poll        : {args.poll_interval}s")
        if errors:
            print("\n⚠️  Ошибки конфигурации:")
            for e in errors:
                print(f"  • {e}")
            return 1
        print("\n✓ Конфигурация корректна")
        return 0

    if errors:
        for e in errors:
            log.error(e)
        return 1

    # ── Запуск asyncio ───────────────────────────────────────────────────────
    assert log_dir is not None  # гарантировано выше

    stop_event = asyncio.Event()

    def _handle_signal(sig: int) -> None:
        log.info("Получен сигнал %s, завершаю...", signal.Signals(sig).name)
        stop_event.set()

    async def _main_async() -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            with contextlib.suppress(NotImplementedError):
                # Windows не поддерживает add_signal_handler
                loop.add_signal_handler(sig, _handle_signal, sig)

        await _run_bridge(
            log_dir=log_dir,
            backend_url=args.backend_url,
            bearer_token=args.token,
            player_name=args.player_name,
            poll_interval=args.poll_interval,
            stop_event=stop_event,
        )

    try:
        asyncio.run(_main_async())
    except KeyboardInterrupt:
        log.info("Прерван пользователем")

    return 0


if __name__ == "__main__":
    sys.exit(main())
