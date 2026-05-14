"""FastAPI application factory. Phase 2: /health + /v1/kb + /v1/whitelist (read-only).

Phase 4 добавит WebSocket endpoint для bridge.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse


def create_app() -> FastAPI:
    """Создать FastAPI-приложение с базовыми маршрутами."""
    app = FastAPI(
        title="Arena Coach API",
        version="0.2.0",
        description="Backend API для Arena Coach — WoW TBC PvP коуча",
        docs_url="/docs",
        redoc_url=None,
    )

    _start_time = time.time()

    @app.get("/health", tags=["ops"])
    async def health() -> dict[str, Any]:
        """Health check — используется мониторингом и deploy-скриптом."""
        return {
            "status": "ok",
            "uptime_s": round(time.time() - _start_time, 1),
        }

    @app.get("/v1/kb/docs", tags=["kb"])
    async def kb_list_docs() -> JSONResponse:
        """Список загруженных KB-документов (slugs). Phase 2 stub."""
        # TODO(Phase 2.5): интегрировать с KBIndex через dependency injection
        return JSONResponse({"docs": [], "note": "not yet wired to KBIndex"})

    @app.get("/v1/whitelist", tags=["access"])
    async def whitelist_list() -> JSONResponse:
        """Список whitelist-записей (admin tool). Phase 2 stub."""
        # TODO(Phase 2.5): интегрировать с AccessService через dependency injection
        return JSONResponse({"entries": [], "note": "not yet wired to AccessService"})

    return app


# WSGI/ASGI entrypoint для uvicorn:
#   uvicorn arena_coach.api.app:app
app = create_app()
