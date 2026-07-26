"""Учёт расхода токенов LLM (Phase 4.7) — общая точка для двух процессов.

  • api-процесс пишет через `record()` после каждого вызова модели
    (незнакомый сетап, постматч);
  • bot-процесс читает через `summary()` для админ-команды `/coach stats`.
Оба смотрят в один SQLite (coach.db). Запись атомарна (SQLite UPSERT), поэтому
одновременные матчи не теряют инкременты и не ловят гонок на unique-ключе.

Стоимость НЕ считаем здесь (цены — забота слоя отображения): храним факты —
токены (вход/выход) и число вызовов, разбитые по (день, назначение, модель).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from arena_coach.access.models import LLMUsage


@dataclass(frozen=True)
class UsageBucket:
    """Агрегат по (назначение, модель) за всё время (или за окно дней)."""

    purpose: str
    model: str
    input_tokens: int
    output_tokens: int
    calls: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class UsageSummary:
    """Сводка для админа: разбивка по назначениям/моделям + итоги."""

    buckets: list[UsageBucket]
    days: int | None  # None = за всё время

    @property
    def input_tokens(self) -> int:
        return sum(b.input_tokens for b in self.buckets)

    @property
    def output_tokens(self) -> int:
        return sum(b.output_tokens for b in self.buckets)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def calls(self) -> int:
        return sum(b.calls for b in self.buckets)


class UsageService:
    """Запись/чтение агрегата расхода токенов LLM."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    @staticmethod
    def _today(now: datetime | None = None) -> str:
        n = now or datetime.now(tz=timezone.utc)
        return n.strftime("%Y-%m-%d")

    async def record(
        self,
        purpose: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        *,
        now: datetime | None = None,
    ) -> None:
        """Прибавить один вызов модели к бакету (день, назначение, модель).

        Best-effort со стороны вызывающего: учёт токенов не должен ронять
        доставку подсказки, поэтому pipeline оборачивает вызов в try/except.
        """
        n = now or datetime.now(tz=timezone.utc)
        day = self._today(n)
        stmt = sqlite_insert(LLMUsage).values(
            day=day,
            purpose=purpose,
            model=model,
            input_tokens=max(0, input_tokens),
            output_tokens=max(0, output_tokens),
            calls=1,
            updated_at=n,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["day", "purpose", "model"],
            set_={
                "input_tokens": LLMUsage.input_tokens + stmt.excluded.input_tokens,
                "output_tokens": LLMUsage.output_tokens + stmt.excluded.output_tokens,
                "calls": LLMUsage.calls + stmt.excluded.calls,
                "updated_at": n,
            },
        )
        async with self._sf() as session:
            await session.execute(stmt)
            await session.commit()

    async def summary(
        self, days: int | None = None, *, now: datetime | None = None
    ) -> UsageSummary:
        """Агрегат по (назначение, модель). days=N → только последние N дней (UTC)."""
        async with self._sf() as session:
            rows = list((await session.execute(select(LLMUsage))).scalars().all())

        cutoff: str | None = None
        if days is not None and days > 0:
            n = now or datetime.now(tz=timezone.utc)
            cutoff = (n - timedelta(days=days - 1)).strftime("%Y-%m-%d")

        agg: dict[tuple[str, str], list[int]] = {}
        for r in rows:
            if cutoff is not None and r.day < cutoff:
                continue
            key = (r.purpose, r.model)
            acc = agg.setdefault(key, [0, 0, 0])
            acc[0] += r.input_tokens
            acc[1] += r.output_tokens
            acc[2] += r.calls

        buckets = [
            UsageBucket(purpose=p, model=m, input_tokens=i, output_tokens=o, calls=c)
            for (p, m), (i, o, c) in sorted(agg.items(), key=lambda kv: -(kv[1][0] + kv[1][1]))
        ]
        return UsageSummary(buckets=buckets, days=days)
