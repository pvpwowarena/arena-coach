"""POST /v1/events — принимает события от arena-bridge.

Аутентификация: Bearer-токен (settings.bridge_bearer_token).
Тело: CanonicalEnvelope в виде JSON (dict).
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from arena_coach.orchestrator.pipeline import PipelineContext, process_event
from arena_coach.shared.settings import settings as _settings

log = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["bridge"])

_bearer_scheme = HTTPBearer(auto_error=True)

#: Порог «медленной» обработки события в горячем пути (мс).
SLOW_EVENT_MS = 150.0


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
        {"status": "sent"|"skipped"|"no_matchup"|"no_player"|"throttled"|"error"}
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

    # Phase 4.18: держим обработку в горячем пути измеримой. Мост ждёт этот ответ
    # внутри своего конвейера, поэтому всё, что дольше десятков миллисекунд, —
    # дефект: сеть (Discord, LLM) обязана уходить в фон через ctx.spawn_bg/spawn_dm.
    started = time.perf_counter()
    result = await process_event(ctx, body)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if elapsed_ms > SLOW_EVENT_MS:
        log.warning(
            "Event processed SLOW: %s → %s за %.0fмс (>%.0fмс — что-то сетевое "
            "осталось в горячем пути)",
            event_type,
            result,
            elapsed_ms,
            SLOW_EVENT_MS,
        )
    else:
        log.info("Event processed: %s → %s за %.1fмс", event_type, result, elapsed_ms)

    return {"status": result}


@router.get(
    "/hints",
    summary="Забрать накопленные локальные голосовые фразы игрока",
)
async def get_hints(
    request: Request,
    player: str = Query(..., description="Имя WoW-персонажа (то же, что BRIDGE_PLAYER_NAME)"),
    _token: str = Depends(_verify_token),
) -> dict[str, object]:
    """Phase 4.6: обратный канал для локального персонального голоса.

    Мост игрока раз в ~1с забирает СВОИ накопленные фразы и озвучивает их
    системным TTS локально (без Discord voice, приватно). Идентификация игрока —
    по параметру `player` (та же модель доверия, что у POST /v1/events по
    player_name: общий bearer-токен + имя персонажа).

    Returns:
        {"player": <name>, "hints": [<фраза>, ...]} — свежие фразы игрока;
        очередь при этом очищается, протухшие по TTL фразы отбрасываются.
    """
    ctx: PipelineContext | None = getattr(request.app.state, "pipeline_ctx", None)
    if ctx is None:
        log.error("PipelineContext не инициализирован в app.state")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline ещё не инициализирован",
        )

    phrases = ctx.hint_queue.pop_fresh(player)
    if phrases:
        log.debug("Отдаю %d локальных фраз игроку %s", len(phrases), player)
    return {"player": player, "hints": phrases}
