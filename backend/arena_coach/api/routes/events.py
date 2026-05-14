"""POST /v1/events — принимает события от arena-bridge.

Аутентификация: Bearer-токен (settings.bridge_bearer_token).
Тело: CanonicalEnvelope в виде JSON (dict).
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from arena_coach.orchestrator.pipeline import PipelineContext, process_event
from arena_coach.shared.settings import settings as _settings

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["bridge"])

_bearer_scheme = HTTPBearer(auto_error=True)


def _verify_token(
    creds: HTTPAuthorizationCredentials = Depends(_bearer_scheme),  # noqa: B008
) -> str:
    """Проверить bearer-токен bridge'а. 401 если не совпадает."""
    expected = _settings.bridge_bearer_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BRIDGE_BEARER_TOKEN не задан в .env — /v1/events отключён",
        )
    if creds.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный bearer-токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return creds.credentials


@router.post(
    "/events",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Принять событие от arena-bridge",
    response_model=dict[str, str],
)
async def receive_event(
    request: Request,
    _token: str = Depends(_verify_token),
) -> dict[str, str]:
    """Обработать CanonicalEnvelope от arena-bridge.

    Тело запроса: JSON-объект с полями schema_version, bridge_ts, session_id,
    player_name, event (dict), match (dict).

    Returns:
        {"status": "sent"|"skipped"|"no_matchup"|"no_player"|"error"}
    """
    try:
        body: dict[str, Any] = await request.json()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body",
        ) from exc

    # Достаём PipelineContext из app.state (инициализируется в lifespan)
    ctx: PipelineContext | None = getattr(request.app.state, "pipeline_ctx", None)
    if ctx is None:
        log.error("PipelineContext не инициализирован в app.state")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline ещё не инициализирован",
        )

    event_type = body.get("event", {}).get("type", "?")
    player = body.get("player_name", "?")
    log.info("Event received: %s from player=%s", event_type, player)

    result = await process_event(ctx, body)
    log.info("Event processed: %s → %s", event_type, result)

    return {"status": result}
