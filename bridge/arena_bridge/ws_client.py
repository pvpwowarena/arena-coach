"""HTTP-клиент: POST событий на backend /v1/events с bearer-auth + retry.

Используем httpx.AsyncClient (проще websockets для MVP Phase 4).
WebSocket можно добавить в Phase 4.1 если нужна двусторонняя связь.
"""

from __future__ import annotations

import asyncio
import logging

import httpx

log = logging.getLogger(__name__)

# Ретраи realtime-события (Phase 4.18). Было [1, 2, 5, 10] — до ~18с на одно
# событие, и всё это время (до 4.18) стоял цикл чтения лога. Но подсказка в арене
# живёт доли секунды: событие, доехавшее через 18с, вредно, а не полезно. Поэтому
# одна быстрая повторная попытка на случай моргнувшей сети — и хватит.
_RETRY_DELAYS = [0.3, 0.7]  # секунды между попытками

# Ретраи для событий, которые НЕ протухают (состав на воротах, конец матча).
# Живой тест 30.07: деплой перезапустил API прямо в матче, nginx отдавал 502
# около пяти секунд, и коротких ретраев не хватило — состав врагов потерялся
# совсем. Такие события ценны и с опозданием, поэтому им даём пережить рестарт.
_RETRY_DELAYS_DURABLE = [0.5, 1.5, 3.0, 6.0]

#: Таймаут POST события. Дольше ждать нечего: см. комментарий про ретраи.
DEFAULT_TIMEOUT_S = 4.0


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
        timeout: float = DEFAULT_TIMEOUT_S,
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

    async def send(self, payload: dict[str, object], durable: bool = False) -> bool:
        """Отправить одно событие на backend.

        Args:
            payload: dict, готовый для JSON-сериализации (CanonicalEnvelope.model_dump())
            durable: событие не протухает (ARENA_START/ARENA_END) — упорствуем дольше.

        Returns:
            True если сервер ответил 2xx, False иначе.
        """
        delays = _RETRY_DELAYS_DURABLE if durable else _RETRY_DELAYS
        for attempt, delay in enumerate(delays, start=1):
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
                        len(delays),
                    )

            except httpx.ConnectError:
                log.warning(
                    "Нет соединения с backend %s, попытка %d/%d",
                    self._endpoint,
                    attempt,
                    len(delays),
                )
            except httpx.TimeoutException:
                log.warning(
                    "Timeout при отправке события, попытка %d/%d",
                    attempt,
                    len(delays),
                )
            except Exception as exc:
                log.error("Неожиданная ошибка при отправке: %s", exc)
                return False

            if attempt < len(delays):
                await asyncio.sleep(delay)

        log.error("Не удалось отправить событие после %d попыток", len(delays))
        return False

    async def health_check(self) -> bool:
        """Проверить доступность backend (GET /health)."""
        try:
            resp = await self._client.get(f"{self._backend_url}/health")
            return resp.is_success
        except Exception as exc:
            log.warning("Backend недоступен: %s", exc)
            return False

    async def get_hints(self, player_name: str) -> list[str]:
        """GET /v1/hints?player=<name> — забрать накопленные голосовые фразы.

        Обратный канал Phase 4.6: pipeline складывает персональные фразы игрока,
        мост забирает СВОИ и озвучивает их локальным TTS. Аутентификация — тот же
        bearer (в self._headers). Строго best-effort: сеть/401/404/битый JSON → [].
        """
        try:
            resp = await self._client.get(
                f"{self._backend_url}/v1/hints",
                params={"player": player_name},
            )
        except Exception as exc:
            log.debug("get_hints: запрос не удался (%s)", exc)
            return []
        if not resp.is_success:
            if resp.status_code == 401:
                log.debug("get_hints: 401 — проверь BRIDGE_BEARER_TOKEN")
            return []
        try:
            data = resp.json()
        except Exception:
            return []
        hints = data.get("hints") if isinstance(data, dict) else None
        if not isinstance(hints, list):
            return []
        return [str(h) for h in hints if isinstance(h, str) and h.strip()]

    async def close(self) -> None:
        """Закрыть httpx-клиент."""
        await self._client.aclose()
