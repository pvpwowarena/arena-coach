"""Pydantic-модели KB-документа.

Канон: см. `docs/phase-0-design.md` §3. Любое изменение схемы обязано:
1. Бампнуть `schema_version` и добавить миграционный скрипт в `kb/migrations/`.
2. Обновить тесты `backend/tests/unit/test_kb_schema.py`.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Difficulty(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very-hard"
    MIRROR = "mirror"


class Bracket(str, Enum):
    TWO_V_TWO = "2v2"
    THREE_V_THREE = "3v3"
    FIVE_V_FIVE = "5v5"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DRAFT = "draft"


class Expansion(str, Enum):
    TBC = "tbc"
    WOTLK = "wotlk"


# ──────────────────────────── Source types ────────────────────────────


class SourceWeb(BaseModel):
    """Источник: ссылка на публичный гайд."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["web"] = "web"
    url: str = Field(min_length=8)
    retrieved: date | None = None
    title: str | None = None


class SourceYouTube(BaseModel):
    """Источник: YouTube VOD/гайд."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["youtube"] = "youtube"
    url: str
    t: str | None = Field(default=None, description="timestamp в формате MM:SS или HH:MM:SS")
    title: str | None = None


class SourceStreamPaste(BaseModel):
    """Источник: текст, вставленный из Discord/Twitch-чата стримера."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["stream-paste"] = "stream-paste"
    author: str
    platform: Literal["twitch", "discord", "other"] | None = None
    # имя `date` теневало бы импортированный тип `date` → renamed to `recorded`
    recorded: date | None = None


class SourceFile(BaseModel):
    """Источник: локальный файл (например, исходный Mirlol-гайд из папки проекта)."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["file"] = "file"
    path: str
    lines: str | None = Field(default=None, description="Диапазон строк, например '11-31'")
    author: str | None = None
    retrieved: date | None = None


Source = Annotated[
    SourceWeb | SourceYouTube | SourceStreamPaste | SourceFile,
    Field(discriminator="type"),
]


# ──────────────────────────── Sub-structures ────────────────────────────


class KillTarget(BaseModel):
    """Цель убийства: primary + опциональный fallback."""

    model_config = ConfigDict(extra="forbid")

    primary: str = Field(min_length=2, description="Slug класса/специализации, напр. 'druid'")
    fallback: str | None = None


# ──────────────────────────── Body sections ────────────────────────────


class Section(BaseModel):
    """Одна `## H2` секция в теле KB-документа.

    Канонические title'ы (см. §3.2 design): Opener, Alternative opener,
    If enemy opens first, Mid-fight rotation, If enemy trinkets, Endgame,
    Common mistakes, Key cooldowns to track, Equipment, Notes, Reset option.
    """

    model_config = ConfigDict(extra="forbid")

    title: str
    body_md: str = Field(min_length=1, description="Тело секции в Markdown")


# ──────────────────────────── Main document ────────────────────────────


class KBDoc(BaseModel):
    """KB-документ матчапа.

    Frontmatter — поля до тела секции. Body — список Section.
    """

    model_config = ConfigDict(extra="forbid")

    # --- identity ---
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=3)
    schema_version: int = 1
    expansion: Expansion = Expansion.TBC

    # --- composition ---
    composition: str = Field(description="Наш состав, canonical slug (e.g. 'rogue+mage')")
    vs: str = Field(description="Состав противника, canonical slug (e.g. 'warrior+resto-druid')")
    bracket: Bracket = Bracket.TWO_V_TWO

    # --- classification ---
    difficulty: Difficulty
    kill_target: KillTarget
    win_condition: str | None = Field(default=None, min_length=4)

    # --- maps ---
    maps_notes: dict[str, str] = Field(
        default_factory=dict,
        description="Карта-специфичные заметки: ключ — slug карты, значение — заметка",
    )

    # --- governance ---
    sources: list[Source] = Field(min_length=1)
    last_reviewed: date
    reviewer: str | None = Field(default=None, description="Discord-id или handle ревьюера")
    confidence: Confidence = Confidence.DRAFT
    tags: list[str] = Field(default_factory=list)

    # --- body ---
    sections: list[Section] = Field(
        default_factory=list, description="Канонические секции в порядке появления"
    )

    # ---------- validators ----------

    @field_validator("composition", "vs")
    @classmethod
    def _composition_format(cls, v: str) -> str:
        """Состав = два или больше класс-slug'а, разделённых '+', нижний регистр."""
        if not v or "+" not in v:
            raise ValueError(
                f"composition/vs должен иметь формат 'class+class' или 'class+class+class', "
                f"получено: {v!r}"
            )
        parts = v.split("+")
        if len(parts) < 2 or any(not p for p in parts):
            raise ValueError(f"Невалидная композиция: {v!r}")
        return v.lower()

    @model_validator(mode="after")
    def _opener_required(self) -> KBDoc:
        """Документ обязан содержать секцию Opener (или Strategy/Stealth Game/General как синоним)."""
        canonical_openers = {"opener", "strategy", "stealth game", "general"}
        section_titles = {s.title.strip().lower() for s in self.sections}
        if not section_titles & canonical_openers:
            raise ValueError(
                "KBDoc должен содержать хотя бы одну секцию из: Opener, Strategy, "
                "Stealth Game или General. Найдено: " + ", ".join(sorted(section_titles))
            )
        return self

    @model_validator(mode="after")
    def _draft_requires_no_reviewer(self) -> KBDoc:
        """Если confidence != draft → reviewer обязателен."""
        if self.confidence != Confidence.DRAFT and not self.reviewer:
            raise ValueError(
                f"confidence={self.confidence.value} требует заполненного поля reviewer"
            )
        return self
