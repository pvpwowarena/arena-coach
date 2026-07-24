"""ArenaCoachBot — главный Discord-клиент. Phase 2.

Жизненный цикл:
1. setup_hook(): создаём AsyncEngine + таблицы, загружаем KB, регистрируем cog'и,
   синкаем slash-команды в guild (мгновенно — не global).
2. on_ready(): логируем статус.
3. tree.error: centralised error handler — access denied, внутренние ошибки.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from arena_coach.access.models import Base
from arena_coach.access.player_settings import PlayerSettingsService
from arena_coach.access.service import AccessService
from arena_coach.bot.checks import access_denied_embed
from arena_coach.bot.voice import EdgeTTSEngine, VoiceManager, start_voice_http
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.shared.settings import Settings
from arena_coach.shared.settings import settings as _default_settings

if TYPE_CHECKING:
    from aiohttp import web

logger = logging.getLogger(__name__)


class ArenaCoachBot(commands.Bot):
    """Основной Discord-бот Арена Коуча."""

    def __init__(self, cfg: Settings | None = None) -> None:
        self.settings: Settings = cfg or _default_settings

        intents = discord.Intents.default()
        intents.members = True  # нужен для guild.get_member() в /access list

        super().__init__(
            command_prefix="!ac.",  # prefix не используется (только app commands), но обязателен
            intents=intents,
            help_command=None,
        )

        # Инициализируются в setup_hook
        self.access_service: AccessService  # type: ignore[assignment]
        self.kb_index: KBIndex  # type: ignore[assignment]
        self.kb_retriever: KBRetriever  # type: ignore[assignment]
        self._session_factory: async_sessionmaker[AsyncSession]  # type: ignore[assignment]
        self.player_settings: PlayerSettingsService  # type: ignore[assignment]
        # Phase 4.5 — None, если голос не настроен (DISCORD_VOICE_CHANNEL_ID=0)
        self.voice_manager: VoiceManager | None = None
        self._voice_http: web.AppRunner | None = None

    # ── setup_hook ────────────────────────────────────────────────────────

    async def setup_hook(self) -> None:
        """Вызывается discord.py перед login(). Инициализируем всё."""

        # 1. Database
        engine = create_async_engine(
            self.settings.database_url,
            echo=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self._session_factory = async_sessionmaker(engine, expire_on_commit=False)
        self.access_service = AccessService(self._session_factory)
        self.player_settings = PlayerSettingsService(self._session_factory)
        logger.info("Database initialised: %s", self.settings.database_url)

        # 2. KB Index
        self.kb_index = KBIndex()
        kb_path = Path(self.settings.kb_path)
        count = self.kb_index.load(kb_path)
        self.kb_retriever = KBRetriever(self.kb_index)
        logger.info("KB loaded: %d documents from %s", count, kb_path)

        # 3. Load cogs
        cog_modules = [
            "arena_coach.bot.cogs.access",
            "arena_coach.bot.cogs.matchup",
            "arena_coach.bot.cogs.glossary",
            "arena_coach.bot.cogs.coach",
        ]
        for module in cog_modules:
            await self.load_extension(module)
            logger.info("Loaded cog: %s", module)

        # 4. Wire tree error handler explicitly (discord.py tree.on_error does NOT
        #    dispatch to bot.on_app_command_error by default when method-overridden).
        self.tree.on_error = self._tree_error_handler  # type: ignore[method-assign]

        # 5. Sync commands GLOBALLY so KB-lookup commands (/matchup, /opener,
        #    /glossary, /list_comps, /source) and /coach are usable in DMs too.
        #    Guild-scoped commands are never offered in DMs (Discord rule), so a
        #    global sync is required. /access is marked guild_only (needs guild
        #    context for get_member) → Discord keeps it server-only automatically.
        #    Realtime coaching DMs are proactive messages (not commands) and are
        #    unaffected. NB: global command propagation can take up to ~1h.
        guild_id = self.settings.discord_guild_id
        if guild_id:
            # Drop any previously guild-scoped registrations so they don't linger
            # in the server alongside the new global commands.
            guild_obj = discord.Object(id=guild_id)
            self.tree.clear_commands(guild=guild_obj)
            await self.tree.sync(guild=guild_obj)
        synced = await self.tree.sync()
        logger.info("Synced %d commands globally (DM-enabled; /access guild-only)", len(synced))

        # 6. Voice (Phase 4.5) — только если канал настроен в api.env.
        #    HTTP-приёмник слушает localhost: pipeline из api-процесса POST'ит
        #    короткие фразы, мы озвучиваем их в voice-канале.
        if self.settings.discord_voice_channel_id:
            self.voice_manager = VoiceManager(
                bot=self,
                channel_id=self.settings.discord_voice_channel_id,
                engine=EdgeTTSEngine(self.settings.voice_tts_voice),
            )
            self.voice_manager.start()
            try:
                self._voice_http = await start_voice_http(
                    self.voice_manager,
                    host=self.settings.voice_http_host,
                    port=self.settings.voice_http_port,
                    bearer_token=self.settings.bridge_bearer_token,
                )
            except OSError as exc:
                logger.error("Voice HTTP-приёмник не поднялся (%s) — голос отключён", exc)
                await self.voice_manager.stop()
                self.voice_manager = None
            logger.info(
                "Voice-подсказки: %s (канал %s)",
                "ВКЛ" if self.voice_manager else "ОШИБКА",
                self.settings.discord_voice_channel_id,
            )
        else:
            logger.info("Voice-подсказки: выключены (DISCORD_VOICE_CHANNEL_ID не задан)")

    async def close(self) -> None:
        """Аккуратно гасим voice-подсистему перед закрытием gateway."""
        if self.voice_manager is not None:
            await self.voice_manager.stop()
        if self._voice_http is not None:
            await self._voice_http.cleanup()
        await super().close()

    # ── on_ready ──────────────────────────────────────────────────────────

    async def on_ready(self) -> None:
        assert self.user is not None
        logger.info(
            "ArenaCoachBot ready: %s (id=%s) | guilds=%d | KB docs=%d",
            self.user,
            self.user.id,
            len(self.guilds),
            len(self.kb_index),
        )

    # ── Error handler ─────────────────────────────────────────────────────

    async def _tree_error_handler(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ) -> None:
        """Обработчик ошибок, явно привязанный к tree.on_error в setup_hook.

        discord.py не вызывает bot.on_app_command_error для method-override,
        поэтому используем прямую привязку через self.tree.on_error.
        """
        if isinstance(error, discord.app_commands.CheckFailure):
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=access_denied_embed(), ephemeral=True)
            return

        # Внутренняя ошибка
        logger.exception(
            "App command error in /%s: %s",
            interaction.command.name if interaction.command else "?",
            error,
        )
        msg = f"⚠️ Внутренняя ошибка: `{type(error).__name__}`"
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            import contextlib

            with contextlib.suppress(Exception):
                await interaction.followup.send(msg, ephemeral=True)

    async def on_app_command_error(  # type: ignore[override]
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ) -> None:
        """Fallback — на случай если dispatch всё же дойдёт через bot event."""
        await self._tree_error_handler(interaction, error)


def create_bot(cfg: Settings | None = None) -> ArenaCoachBot:
    """Фабрика бота — используется в __main__ и тестах."""
    return ArenaCoachBot(cfg=cfg)


__all__ = ["ArenaCoachBot", "create_bot"]
