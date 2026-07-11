#!/usr/bin/env python3
"""E2E dry-run: addon-формат → bridge → backend → pipeline, БЕЗ живой игры.

Что доказывает (на синтетическом Chat-логе, без WoW и без Discord):
  1. Строки [AC|...], которые пишет аддон, парсятся regex'ом bridge
     (включая формат WoWChatLog.txt и allies-поле аддона 0.2.0).
  2. normalizer собирает корректные CanonicalEnvelope (типы, поля,
     slug_hint, our_comp_hint, player_class).
  3. POST /v1/events проходит Bearer-аутентификацию (401 на неверном токене).
  4. Whitelist enforce-ится (no_player для игрока не из вайтлиста).
  5. Phase 4.1: ARENA_START матчит KB-документ по классам врагов → DM с опенером
     и килл-таргетом; TRINKET → post-trinket секция; ABILITY из списка ключевых
     дефов → hint, повтор → throttled; cyclone (CC-каст) и ARENA_END → skipped.
  6. Discord DM формируется и «отправляется» (замокан — без запросов к discord.com).

Запуск (из корня репо, после editable-install пакетов):
    pip install -e ./backend -e ./bridge -e ./ingest
    python tools/e2e_dryrun.py

Это smoke-тест для проверки серверной цепочки перед живым тестом на арене.
Реальные секреты/БД/Discord не используются — всё на временных данных.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAYER = "Vladislav"


def _setup_env() -> str:
    """Готовим окружение ДО импорта arena_coach (settings — синглтон)."""
    # Некоторые dev-окружения задают SOCKS-прокси в env, из-за чего httpx/Anthropic
    # падают при инициализации. Сеть тут не нужна — чистим прокси-переменные.
    for k in list(os.environ):
        if "proxy" in k.lower():
            os.environ.pop(k, None)

    from cryptography.fernet import Fernet

    tmp = tempfile.mkdtemp(prefix="arena_dryrun_")
    os.environ.update(
        {
            "BRIDGE_BEARER_TOKEN": "test-token-123",
            "DATABASE_URL": f"sqlite+aiosqlite:///{tmp}/coach.db",
            "KB_PATH": str(REPO_ROOT / "kb"),
            "AUDIT_LOG_DIR": f"{tmp}/audit",
            "ARENA_COACH_FERNET_KEY": Fernet.generate_key().decode(),
            "DISCORD_BOT_TOKEN": "dummy-bot-token",
            "ANTHROPIC_API_KEY": "",  # пусто → LLM кинет → fallback на KB-текст
        }
    )
    return tmp


def _write_synthetic_chatlog(tmp: str) -> pathlib.Path:
    """Пишем chat-лог в том же виде, в каком его создаёт WoW (whisper-to-self).

    Имя файла — стандартное WoWChatLog.txt (bridge v0.3.0 автодетектит его).
    Сценарий: враги WARRIOR+PALADIN (матчит rm-vs-warrior-hpala по классам),
    союзники ROGUE+MAGE (игрок — рога), трикет, shield_wall (hint) ×2 (второй
    должен затроттлиться), cyclone (skipped — CC-каст не в hint-списке).
    """
    logdir = pathlib.Path(tmp) / "Logs"
    logdir.mkdir(parents=True, exist_ok=True)
    chat = logdir / "WoWChatLog.txt"
    chat.write_text(
        "\n".join(
            [
                f"7/11 12:00:00.000  To {PLAYER}: "
                "[AC|ARENA_START|2v2|WARRIOR/ORC,PALADIN/BLOODELF|ROGUE/HUMAN,MAGE/UNDEAD]",
                f"7/11 12:00:05.123  To {PLAYER}: [AC|TRINKET|EnemyWarrior|42292|pvp_trinket]",
                f"7/11 12:00:06.456  To {PLAYER}: [AC|ABILITY|EnemyWarrior|871|shield_wall]",
                f"7/11 12:00:07.000  To {PLAYER}: [AC|ABILITY|EnemyWarrior|871|shield_wall]",
                f"7/11 12:00:08.500  To {PLAYER}: [AC|ABILITY|EnemyMage|33786|cyclone]",
                f"7/11 12:00:30.000  To {PLAYER}: [AC|ARENA_END|5]",
                "7/11 12:00:31.000  [2. Trade] WTS [Some Item] — мусор, должно игнориться",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return chat


def part_a(chat: pathlib.Path) -> list:
    """BRIDGE: Chat-лог → CanonicalEnvelope (тот же regex, что в ChatTailer)."""
    from arena_bridge.chat_tail import _AC_RE
    from arena_bridge.normalizer import SessionState, normalize_raw

    print("=" * 70)
    print("ЧАСТЬ A — BRIDGE: Chat-лог → CanonicalEnvelope")
    print("=" * 70)
    sess = SessionState()
    envelopes = []
    for ln in chat.read_text(encoding="utf-8").splitlines():
        m = _AC_RE.search(ln)
        if not m:
            print(f"  · игнор (не AC): {ln[:42]}…")
            continue
        env = normalize_raw(m.group(1), sess, PLAYER)
        if env is None:
            print(f"  ! не распарсилось: {m.group(1)}")
            continue
        envelopes.append(env)
        extra = {k: v for k, v in env.event.model_dump().items() if k != "type"}
        print(
            f"  ✓ {env.event.type:<12} slug_hint={env.match.matchup_slug_hint!r:<18} "
            f"our={env.match.our_comp_hint!r} cls={env.match.player_class!r} {extra}"
        )
    print(f"\n  Распарсено envelopes: {len(envelopes)}")
    return envelopes


async def _seed_whitelist() -> bool:
    """Добавляем тестового игрока (role=player) в ту же БД, что поднимет lifespan."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from arena_coach.access.models import Base, Role
    from arena_coach.access.service import AccessService

    eng = create_async_engine(os.environ["DATABASE_URL"])
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    svc = AccessService(async_sessionmaker(eng, expire_on_commit=False))
    await svc.add_entry(
        discord_id="111111111111",
        character=PLAYER,
        realm="Gorefiend",
        role=Role.PLAYER,
        added_by="owner-test",
    )
    found = await svc.find_by_character(PLAYER)
    await eng.dispose()
    return found is not None


def part_b(envelopes: list) -> None:
    """BACKEND: реальный FastAPI через TestClient (запускает lifespan)."""
    import arena_coach.orchestrator.pipeline as pl

    sent_dms: list[tuple[str, str]] = []

    async def fake_dm(bot_token: str, discord_id: str, content: str) -> bool:
        sent_dms.append((discord_id, content))
        return True

    pl._send_discord_dm = fake_dm  # мок Discord DM — без запросов к discord.com

    from fastapi.testclient import TestClient

    from arena_coach.api.app import app

    print("\n" + "=" * 70)
    print("ЧАСТЬ B — BACKEND: POST /v1/events (Bearer + pipeline)")
    print("=" * 70)
    rows: list[tuple[str, int, str]] = []
    with TestClient(app) as client:
        h = client.get("/health")
        print(f"  GET /health → {h.status_code} {h.json()}\n")
        headers = {"Authorization": "Bearer test-token-123"}
        for env in envelopes:
            r = client.post("/v1/events", json=env.model_dump(), headers=headers)
            rows.append((env.event.type, r.status_code, r.json().get("status")))
        bad_player = envelopes[0].model_dump()
        bad_player["player_name"] = "Randomnoob"
        r = client.post("/v1/events", json=bad_player, headers=headers)
        rows.append(("ARENA_START / чужой игрок", r.status_code, r.json().get("status")))
        r = client.post(
            "/v1/events",
            json=envelopes[0].model_dump(),
            headers={"Authorization": "Bearer WRONG"},
        )
        rows.append(("ARENA_START / неверный токен", r.status_code, str(r.json().get("detail"))[:24]))

    print("  Сценарий                         | HTTP | результат")
    print("  " + "-" * 56)
    for name, code, status in rows:
        print(f"  {name:<32} | {code:>4} | {status}")
    print(f"\n  Discord DM (замокано): {len(sent_dms)} шт.")
    for did, content in sent_dms:
        print(f"    → {did}: {content[:64].replace(chr(10), ' / ')}…")


def main() -> None:
    tmp = _setup_env()
    chat = _write_synthetic_chatlog(tmp)
    envelopes = part_a(chat)
    print(f"\n  Whitelist: '{PLAYER}' добавлен → find_by_character: {asyncio.run(_seed_whitelist())}")
    part_b(envelopes)
    print("\n" + "=" * 70)
    print("ИТОГ: addon → regex → normalizer → HTTP+Bearer → whitelist → pipeline → DM.")
    print("=" * 70)


if __name__ == "__main__":
    main()
