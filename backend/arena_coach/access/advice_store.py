"""Персистентный кэш LLM-разборов незнакомых сетапов (Phase 4.7).

L2-кэш поверх in-memory L1 (`orchestrator.advice.AdviceCache`): переживает
рестарты/автодеплой, поэтому редкий сетап генерится ОДИН раз за всю историю,
а не заново после каждого деплоя. Хранит модель-генератор → можно точечно
перегенерить сильной моделью и прогреть популярные сетапы заранее (warm-advice).

Пишет api-процесс (фоновая генерация) и CLI warm-advice; читает api-процесс
(на cache-miss L1). Ключ — сигнатура сетапа (`advice.comp_signature`).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from arena_coach.access.models import AdviceCacheEntry


@dataclass(frozen=True)
class AdviceRow:
    text: str
    model: str


class AdviceStore:
    """CRUD-минимум вокруг таблицы advice_cache (SQLite UPSERT по sig)."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def get(self, sig: str) -> AdviceRow | None:
        if not sig:
            return None
        async with self._sf() as session:
            row = await session.get(AdviceCacheEntry, sig)
            return AdviceRow(text=row.text, model=row.model) if row is not None else None

    async def put(self, sig: str, text: str, model: str, *, now: datetime | None = None) -> None:
        if not sig or not text.strip():
            return
        n = now or datetime.now(tz=timezone.utc)
        stmt = sqlite_insert(AdviceCacheEntry).values(
            sig=sig, text=text, model=model, created_at=n, updated_at=n
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["sig"],
            set_={"text": text, "model": model, "updated_at": n},
        )
        async with self._sf() as session:
            await session.execute(stmt)
            await session.commit()

    async def count(self) -> int:
        async with self._sf() as session:
            result = await session.execute(select(func.count()).select_from(AdviceCacheEntry))
            return int(result.scalar_one())
