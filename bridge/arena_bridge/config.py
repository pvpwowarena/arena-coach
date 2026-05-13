"""Конфигурация bridge'а: пути к WoW-клиенту, токен, backend-URL.

Phase 4 skeleton — финальная реализация подключит pydantic-settings + автодетект путей.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class BridgeConfig(BaseModel):
    """Конфиг bridge'а. В Phase 4 заполняется из .env."""

    wow_install_path: Path = Field(description="Корень установки WoW клиента")
    account_name: str = Field(description="Имя WTF/Account/<NAME> папки")
    backend_wss_url: str = Field(
        description="WSS URL backend'а (например wss://coach.example.com/ws)"
    )
    bearer_token: str = Field(description="Per-player bearer-токен (выдаётся при /access add)")
    sv_poll_interval_sec: float = 5.0
    chat_log_poll_interval_sec: float = 0.5

    @property
    def saved_variables_path(self) -> Path:
        return (
            self.wow_install_path
            / "WTF"
            / "Account"
            / self.account_name
            / "SavedVariables"
            / "ArenaCoach.lua"
        )

    @property
    def chat_log_dir(self) -> Path:
        return self.wow_install_path / "Logs"
