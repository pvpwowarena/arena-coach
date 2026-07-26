"""Загрузить заранее сгенерённые разборы в персистентный кэш (advice_cache).

НЕ зовёт LLM: тексты уже готовы (сгенерены оффлайн сильной моделью). Пишет БД —
запускать под тем же юзером, что и сервисы (arenacoach), с DATABASE_URL из api.env.
Ключ Anthropic НЕ нужен.

Сигнатура строится тем же `comp_signature`, что и в бою; our_comp сортируется
(как allies-хинт моста) → кэш попадает в реальные матчи.

Использование (на VPS):
  DATABASE_URL="sqlite+aiosqlite:////var/lib/arena-coach/coach.db" \
    /opt/arena-coach/.venv/bin/python tools/load_advice.py tools/advice_seed.json
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path


async def _main(path: Path) -> int:
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from arena_coach.access.advice_store import AdviceStore
    from arena_coach.access.models import Base
    from arena_coach.orchestrator.advice import comp_signature
    from arena_coach.shared.settings import settings

    entries = json.loads(path.read_text(encoding="utf-8"))
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    store = AdviceStore(async_sessionmaker(engine, expire_on_commit=False))

    loaded = 0
    for e in entries:
        our = str(e.get("our") or "")
        our_sorted = "+".join(sorted(p for p in our.lower().split("+") if p)) or None
        classes = [str(c[0]) for c in e["enemies"]]
        specs = [(c[1] if len(c) > 1 else None) for c in e["enemies"]]
        bracket = str(e["bracket"])
        text = str(e["text"]).strip()
        if not text:
            continue
        sig = comp_signature(our_sorted, classes, specs, bracket)
        await store.put(sig, text, str(e.get("model", "claude-opus-manual")))
        loaded += 1
        print(f"  OK  {sig}")

    total = await store.count()
    await engine.dispose()
    print(f"Загружено {loaded} разборов; всего в advice_cache: {total}.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python tools/load_advice.py <seed.json>", file=sys.stderr)
        sys.exit(2)
    sys.exit(asyncio.run(_main(Path(sys.argv[1]))))
