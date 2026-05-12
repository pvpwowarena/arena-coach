"""pydantic-settings: загрузка .env. Phase 2 skeleton (расширяется по мере фаз)."""

from __future__ import annotations

from pathlib import Path


class _PlaceholderSettings:
    """Phase 1 stub. В Phase 2 заменяется на pydantic_settings.BaseSettings."""

    kb_path: Path = Path("kb")


settings = _PlaceholderSettings()
