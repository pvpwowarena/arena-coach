"""Голосовые подсказки в Discord voice-канале (Phase 4.5).

Архитектура (docs/phase-4.5-voice.md):

    api-процесс (pipeline) ──POST /speak──▶ bot-процесс (этот модуль)
                                              │ VoiceManager.enqueue()
                                              ▼
                     очередь → троттлинг/TTL/дедуп → TTS (edge-tts, LRU-кэш)
                                              ▼
                     Discord voice-client (FFmpegOpusAudio, нужен ffmpeg)

Почему HTTP между процессами: voice-соединение живёт только у gateway-клиента
(bot-процесс), а pipeline крутится в api-процессе — Discord REST голосом не
умеет. Слушаем строго 127.0.0.1 + Bearer (тот же BRIDGE_BEARER_TOKEN, он есть
в api.env обоих процессов).

Правила VoiceManager:
  • очередь коротких фраз; переполнение — дроп с логом (не копим отставание);
  • фраза протухает за hint_ttl_s (подсказка «тринкет» через минуту вредна);
  • не чаще одной реплики в min_interval_s («уши пухнут»);
  • одинаковая фраза не повторяется в dedupe_window_s (двое игроков одной
    команды шлют одно и то же событие со своих бриджей);
  • LRU-кэш TTS на 256 фраз;
  • в пустой voice-канал не заходим; при простое отключаемся.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import tempfile
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

import discord

if TYPE_CHECKING:
    from aiohttp import web

log = logging.getLogger(__name__)

_TTS_CACHE_SIZE = 256
_MAX_PHRASE_LEN = 200


class TTSEngine(Protocol):
    """Абстракция TTS — в тестах подменяется фейком."""

    async def synth(self, text: str) -> bytes: ...


class EdgeTTSEngine:
    """Edge TTS (бесплатный, нормальный русский голос, ~100-300мс).

    Своп на OpenAI TTS при необходимости — только замена этого класса.
    """

    def __init__(self, voice: str = "ru-RU-DmitryNeural") -> None:
        self._voice = voice

    async def synth(self, text: str) -> bytes:
        import edge_tts  # ленивый импорт: api-процессу пакет не нужен

        communicate = edge_tts.Communicate(text, self._voice)
        chunks = bytearray()
        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                data = chunk.get("data")
                if isinstance(data, bytes):
                    chunks.extend(data)
        if not chunks:
            raise RuntimeError("edge-tts вернул пустое аудио")
        return bytes(chunks)


@dataclass
class QueuedHint:
    text: str
    enqueued_at: float


@dataclass
class VoiceStats:
    """Счётчики для логов/отладки."""

    played: int = 0
    dropped_full: int = 0
    dropped_stale: int = 0
    dropped_throttled: int = 0
    dropped_duplicate: int = 0
    tts_errors: int = 0
    skipped_empty_channel: int = 0


@dataclass
class VoiceManager:
    """Очередь голосовых подсказок одного guild'а (singleton на бота)."""

    bot: discord.Client | None
    channel_id: int
    engine: TTSEngine
    min_interval_s: float = 8.0
    hint_ttl_s: float = 15.0
    dedupe_window_s: float = 10.0
    idle_disconnect_s: float = 300.0
    queue_size: int = 8
    clock: Callable[[], float] = time.monotonic

    stats: VoiceStats = field(default_factory=VoiceStats)
    _queue: asyncio.Queue[QueuedHint] = field(init=False)
    _cache: OrderedDict[str, bytes] = field(default_factory=OrderedDict, init=False)
    _last_played_at: float = field(default=0.0, init=False)
    _last_texts: dict[str, float] = field(default_factory=dict, init=False)
    _worker_task: asyncio.Task[None] | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._queue = asyncio.Queue(maxsize=self.queue_size)

    # ── жизненный цикл ──────────────────────────────────────────────────

    def start(self) -> None:
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.get_running_loop().create_task(self._worker())
            log.info("VoiceManager запущен (канал %s)", self.channel_id)

    async def stop(self) -> None:
        if self._worker_task is not None:
            self._worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker_task
            self._worker_task = None
        await self._disconnect()

    # ── вход ────────────────────────────────────────────────────────────

    def enqueue(self, text: str) -> bool:
        """Поставить фразу в очередь. False = дроп (очередь полна/пусто)."""
        text = text.strip()[:_MAX_PHRASE_LEN]
        if not text:
            return False
        try:
            self._queue.put_nowait(QueuedHint(text=text, enqueued_at=self.clock()))
            return True
        except asyncio.QueueFull:
            self.stats.dropped_full += 1
            log.warning("Voice-очередь полна — дропаю «%s»", text)
            return False

    # ── обработка ───────────────────────────────────────────────────────

    async def process_hint(self, hint: QueuedHint) -> str:
        """Обработать одну фразу; возвращает статус (для тестов и логов).

        Статусы: played | stale | throttled | duplicate | tts_error | no_audience
        """
        now = self.clock()
        if now - hint.enqueued_at > self.hint_ttl_s:
            self.stats.dropped_stale += 1
            return "stale"
        if now - self._last_played_at < self.min_interval_s:
            self.stats.dropped_throttled += 1
            log.debug("Voice-троттлинг: «%s» дропнута", hint.text)
            return "throttled"
        last_same = self._last_texts.get(hint.text)
        if last_same is not None and now - last_same < self.dedupe_window_s:
            self.stats.dropped_duplicate += 1
            return "duplicate"

        data = self._cache_get(hint.text)
        if data is None:
            try:
                data = await self.engine.synth(hint.text)
            except Exception as exc:
                self.stats.tts_errors += 1
                log.warning("TTS не удался для «%s»: %s", hint.text, exc)
                return "tts_error"
            self._cache_put(hint.text, data)

        self._last_played_at = self.clock()
        self._last_texts[hint.text] = self._last_played_at
        played = await self._play(data)
        if not played:
            self.stats.skipped_empty_channel += 1
            return "no_audience"
        self.stats.played += 1
        return "played"

    async def _worker(self) -> None:
        while True:
            try:
                hint = await asyncio.wait_for(self._queue.get(), timeout=self.idle_disconnect_s)
            except asyncio.TimeoutError:
                await self._disconnect()  # долго тихо — выходим из канала
                continue
            try:
                status = await self.process_hint(hint)
                log.debug("Voice «%s» → %s", hint.text, status)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # не даём воркеру умереть
                log.warning("Voice-воркер: ошибка на «%s»: %s", hint.text, exc)

    # ── TTS LRU-кэш ─────────────────────────────────────────────────────

    def _cache_get(self, text: str) -> bytes | None:
        data = self._cache.get(text)
        if data is not None:
            self._cache.move_to_end(text)
        return data

    def _cache_put(self, text: str, data: bytes) -> None:
        self._cache[text] = data
        self._cache.move_to_end(text)
        while len(self._cache) > _TTS_CACHE_SIZE:
            self._cache.popitem(last=False)

    # ── Discord voice (в тестах _play подменяется) ──────────────────────

    async def _ensure_connected(self) -> discord.VoiceClient | None:
        """Подключиться к настроенному каналу; None, если канал пуст/не найден.

        В пустой канал не заходим (acceptance №3) — не жжём ресурсы зря.
        """
        if self.bot is None:
            return None
        channel = self.bot.get_channel(self.channel_id)
        if not isinstance(channel, discord.VoiceChannel):
            log.warning("Voice-канал %s не найден или не voice", self.channel_id)
            return None
        humans = [m for m in channel.members if not m.bot]
        existing = channel.guild.voice_client
        voice = existing if isinstance(existing, discord.VoiceClient) else None
        if not humans:
            if voice is not None and voice.is_connected():
                await voice.disconnect(force=False)
            return None
        if voice is None or not voice.is_connected():
            try:
                voice = await channel.connect(timeout=10.0)
            except Exception as exc:
                log.warning("Не удалось зайти в voice-канал %s: %s", self.channel_id, exc)
                return None
        elif voice.channel is not None and voice.channel.id != self.channel_id:
            await voice.move_to(channel)
        return voice

    async def _play(self, data: bytes) -> bool:
        """Проиграть mp3-байты в канал. True = реально проигралось."""
        voice = await self._ensure_connected()
        if voice is None:
            return False

        # FFmpegOpusAudio читает файл — пишем во временный (нужен ffmpeg в PATH)
        fd, tmp_name = tempfile.mkstemp(suffix=".mp3", prefix="arena-voice-")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)

            finished: asyncio.Event = asyncio.Event()
            loop = asyncio.get_running_loop()

            def _after(err: Exception | None) -> None:
                if err is not None:
                    log.warning("Voice-плеер: %s", err)
                loop.call_soon_threadsafe(finished.set)

            if voice.is_playing():
                voice.stop()  # свежая подсказка важнее хвоста прошлой
            source = discord.FFmpegOpusAudio(tmp_name)
            voice.play(source, after=_after)
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(finished.wait(), timeout=30.0)
            return True
        except Exception as exc:
            log.warning("Voice-проигрывание не удалось: %s", exc)
            return False
        finally:
            with contextlib.suppress(OSError):
                os.unlink(tmp_name)

    async def _disconnect(self) -> None:
        if self.bot is None:
            return
        channel = self.bot.get_channel(self.channel_id)
        if isinstance(channel, discord.VoiceChannel):
            existing = channel.guild.voice_client
            if isinstance(existing, discord.VoiceClient) and existing.is_connected():
                log.info("Voice: простой — выхожу из канала")
                await existing.disconnect(force=False)


# ── HTTP-приёмник (в bot-процессе) ───────────────────────────────────────────


async def start_voice_http(
    manager: VoiceManager,
    host: str,
    port: int,
    bearer_token: str,
) -> web.AppRunner:
    """Поднять POST /speak на 127.0.0.1 — вход для pipeline'а из api-процесса.

    aiohttp гарантированно есть — это зависимость discord.py.
    """
    from aiohttp import web

    async def speak(request: web.Request) -> web.Response:
        if bearer_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {bearer_token}":
                return web.json_response({"error": "unauthorized"}, status=401)
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "invalid json"}, status=400)
        text = str(body.get("text", "")).strip()
        if not text:
            return web.json_response({"error": "empty text"}, status=400)
        queued = manager.enqueue(text)
        return web.json_response({"status": "queued" if queued else "dropped"})

    app = web.Application()
    app.router.add_post("/speak", speak)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    log.info("Voice HTTP-приёмник слушает %s:%s/speak", host, port)
    return runner
