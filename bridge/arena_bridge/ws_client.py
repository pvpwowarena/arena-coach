"""HTTP-клиент: POST событий на backend /v1/events с bearer-auth + retry.

Используем httpx.AsyncClient (проще websockets для MVP Phase 4).
WebSocket можно добавить в Phase 4.1 если нужна двусторонняя связь.
"""

from __future__ import annotations

import asyncio
import logging

import httpx

log = logging.getLogger(__name__)

_RETRY_DELAYS = [1.0, 2.0, 5.0, 10.0]  # секунды между попытками


class EventClient:
    """Asyncio HTTP-клиент для отправки событий на backend.

    Поддерживает:
    - Bearer-аутентификацию
    - Авто-retry с экспоненциальным backoff
    - Graceful shutdown (close())
    """

    def __init__(
        self,
        backend_url: str,
        bearer_token: str,
        timeout: float = 10.0,
    ) -> None:
        self._backend_url = backend_url.rstrip("/")
        self._endpoint = f"{self._backend_url}/v1/events"
        self._headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._headers,
        )

    async def send(self, payload: dict[str, object]) -> bool:
        """Отправить одно событие на backend.

        Args:
            payload: dict, готовый для JSON-сериализации (CanonicalEnvelope.model_dump())

        Returns:
            True если сервер ответил 2xx, False иначе.
        """
        for attempt, delay in enumerate(_RETRY_DELAYS, start=1):
            try:
                resp = await self._client.post(self._endpoint, json=payload)
                if resp.is_success:
                    log.debug(
                        "Событие отправлено [%s %s]", resp.status_code, payload.get("event", {})
                    )
                    return True
                elif resp.status_code == 401:
                    log.error("Unauthorized — проверь BRIDGE_BEARER_TOKEN в .env")
                    return False
                elif resp.status_code == 403:
                    log.warning(
                        "Forbidden: игрок не в whitelist или нет роли player (%s)",
                        payload.get("player_name"),
                    )
                    return False
                else:
                    log.warning(
                        "Backend ответил %s, попытка %d/%d",
                        resp.status_code,
                        attempt,
                        len(_RETRY_DELAYS),
                    )

            except httpx.ConnectError:
                log.warning(
                    "Нет соединения с backend %s, попытка %d/%d",
                    self._endpoint,
                    attempt,
                    len(_RETRY_DELAYS),
                )
            except httpx.TimeoutException:
                log.warning(
                    "Timeout при отправке события, попытка %d/%d",
                    attempt,
                    len(_RETRY_DELAYS),
                )
            except Exception as exc:
                log.error("Неожиданная ошибка при отправке: %s", exc)
                return False

            if attempt < len(_RETRY_DELAYS):
                await asyncio.sleep(delay)

        log.error("Не удалось отправить событие после %d попыток", len(_RETRY_DELAYS))
        return False

    async def health_check(self) -> bool:
        """Проверить доступность backend (GET /health)."""
        try:
            resp = await self._client.get(f"{self._backend_url}/health")
            return resp.is_success
        except Exception as exc:
            log.warning("Backend недоступен: %s", exc)
            return False

    async def close(self) -> None:
        """Закрыть httpx-клиент."""
        await self._client.aclose()
