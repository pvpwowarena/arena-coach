"""Тесты учёта токенов LLM (access/usage.py, Phase 4.7)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from arena_coach.access.models import Base
from arena_coach.access.usage import UsageService


@pytest.fixture
async def usage(tmp_path: Path) -> UsageService:
    # Файловая БД (не :memory:) — record и summary в разных сессиях видят одни данные.
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/coach.db", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
    return UsageService(factory)


async def test_record_aggregates_same_bucket(usage: UsageService) -> None:
    await usage.record("advice", "haiku", 100, 50)
    await usage.record("advice", "haiku", 200, 80)
    s = await usage.summary()
    assert s.calls == 2
    assert s.input_tokens == 300
    assert s.output_tokens == 130
    assert len(s.buckets) == 1
    assert s.buckets[0].total_tokens == 430


async def test_separate_buckets_by_purpose_and_model(usage: UsageService) -> None:
    await usage.record("advice", "haiku", 100, 50)
    await usage.record("postmatch", "sonnet", 300, 200)
    s = await usage.summary()
    assert s.calls == 2
    assert {b.purpose for b in s.buckets} == {"advice", "postmatch"}
    # сортировка по суммарным токенам убыв.: postmatch(500) выше advice(150)
    assert s.buckets[0].purpose == "postmatch"


async def test_days_window_filters_old(usage: UsageService) -> None:
    old = datetime(2026, 1, 1, tzinfo=timezone.utc)
    now = datetime(2026, 1, 10, tzinfo=timezone.utc)
    await usage.record("advice", "haiku", 10, 10, now=old)
    await usage.record("advice", "haiku", 5, 5, now=now)
    assert (await usage.summary(now=now)).calls == 2
    windowed = await usage.summary(days=3, now=now)
    assert windowed.calls == 1
    assert windowed.input_tokens == 5


async def test_totals_helpers(usage: UsageService) -> None:
    await usage.record("advice", "haiku", 100, 50)
    s = await usage.summary()
    assert s.total_tokens == 150
