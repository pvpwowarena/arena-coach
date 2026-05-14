"""FastAPI application factory. Phase 4: /health + /v1/events.

Lifespan инициализирует PipelineContext (DB, KB, LLM-клиент),
который хранится в app.state.pipeline_ctx.

Запуск:
    uvicorn arena_coach.api.app:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Инициализация/деинициализация ресурсов при старте/остановке сервера."""
    from anthropic import AsyncAnthropic
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from arena_coach.access.models import Base
    from arena_coach.access.service import AccessService
    from arena_coach.kb.indexer import KBIndex
    from arena_coach.kb.retriever import KBRetriever
    from arena_coach.orchestrator.pipeline import PipelineContext
    from arena_coach.shared.settings import settings

    log.info("FastAPI lifespan: инициализация...")

    # ── Database ──────────────────────────────────────────────────────────
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    access_service = AccessService(session_factory)
    log.info("DB инициализирована: %s", settings.database_url)

    # ── KB ────────────────────────────────────────────────────────────────
    kb_index = KBIndex()
    kb_path = Path(settings.kb_path)
    if kb_path.exists():
        count = kb_index.load(kb_path)
        log.info("KB загружена: %d документов из %s", count, kb_path)
    else:
        log.warning("KB-путь не найден: %s — KB пуста", kb_path)

    kb_retriever = KBRetriever(kb_index)

    # ── Anthropic ─────────────────────────────────────────────────────────
    anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key or None)

    # ── PipelineContext в app.state ───────────────────────────────────────
    app.state.pipeline_ctx = PipelineContext(
        access_service=access_service,
        kb_retriever=kb_retriever,
        anthropic_client=anthropic_client,
        settings=settings,
    )
    log.info("PipelineContext готов. /v1/events активен.")

    yield

    # ── shutdown ─────────────────────────────────────────────────────────
    await engine.dispose()
    await anthropic_client.close()
    log.info("FastAPI lifespan: ресурсы освобождены")


def create_app() -> FastAPI:
    """Создать FastAPI-приложение."""
    _start_time = time.time()

    application = FastAPI(
        title="Arena Coach API",
        version="0.3.0",
        description="Backend API для Arena Coach — WoW TBC PvP коуча",
        docs_url="/docs",
        redoc_url=None,
        lifespan=_lifespan,
    )

    # ── Health ────────────────────────────────────────────────────────────

    @application.get("/health", tags=["ops"])
    async def health() -> dict[str, Any]:
        """Health check — используется мониторингом и deploy-скриптом."""
        return {
            "status": "ok",
            "uptime_s": round(time.time() - _start_time, 1),
        }

    # ── KB / whitelist stubs (Phase 2.5 TODO) ────────────────────────────

    @application.get("/v1/kb/docs", tags=["kb"])
    async def kb_list_docs() -> JSONResponse:
        """Список загруженных KB-документов. TODO: wired in Phase 2.5."""
        return JSONResponse({"docs": [], "note": "not yet wired to KBIndex"})

    @application.get("/v1/whitelist", tags=["access"])
    async def whitelist_list() -> JSONResponse:
        """Список whitelist-записей. TODO: wired in Phase 2.5."""
        return JSONResponse({"entries": [], "note": "not yet wired to AccessService"})

    # ── Bridge events (Phase 4) ───────────────────────────────────────────
    from arena_coach.api.routes.events import router as events_router

    application.include_router(events_router)

    return application


# WSGI/ASGI entrypoint для uvicorn:
#   uvicorn arena_coach.api.app:app --host 0.0.0.0 --port 8000
app = create_app()
