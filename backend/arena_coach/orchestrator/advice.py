"""LLM-слой Arena Coach (Phase 4.7): разбор сетапов ВНЕ KB + постматч-анализ.

Где LLM даёт максимальный КПД (см. решение по продукту):
  1. Незнакомый/нестандартный сетап (mage+mage+mage, hpal+ret+rogue, соло-друид)
     — KB-документа нет, детерминированного килл-таргета/опенера нет. Модель
     генерит краткий разбор с нуля из классов/спеков + общих принципов TBC-арены.
     Вызывается ВНЕ горячего пути (фоново), результат кэшируется по сигнатуре
     сетапа → второй раз тот же сетап отдаётся мгновенно.
  2. Постматч-разбор — после боя времени много, есть весь таймлайн: персональный
     совет, который шаблоном не собрать.

В БОЮ (килл-таргет из KB, тринкеты, дефы) LLM НЕ участвует — там всё
детерминированно и мгновенно. Весь модуль включается только при заданном
ANTHROPIC_API_KEY; иначе pipeline остаётся чисто детерминированным.

Каждый вызов возвращает текст + TokenUsage (вход/выход) — pipeline пишет расход
в UsageService для админ-статистики. Модуль чист от discord; сеть — только
Anthropic-клиент, инъектируется.
"""

from __future__ import annotations

import logging
import time
from collections import OrderedDict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

# Назначения для UsageService (стабильные строки — по ним группируется статистика)
PURPOSE_ADVICE = "advice"
PURPOSE_POSTMATCH = "postmatch"


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class AdviceResult:
    text: str
    usage: TokenUsage


def _extract_text(response: Any) -> str:
    """Достать текст из Anthropic Message (первый text-блок)."""
    content = getattr(response, "content", None)
    if not content:
        return ""
    first = content[0]
    text = getattr(first, "text", None)
    return str(text).strip() if text is not None else ""


def _extract_usage(response: Any) -> TokenUsage:
    """Достать usage из Anthropic Message (0/0 если поля нет)."""
    usage = getattr(response, "usage", None)
    in_tok = int(getattr(usage, "input_tokens", 0) or 0)
    out_tok = int(getattr(usage, "output_tokens", 0) or 0)
    return TokenUsage(input_tokens=in_tok, output_tokens=out_tok)


# ── Сигнатура сетапа для кэша ────────────────────────────────────────────────


def comp_signature(
    our_comp: str | None,
    enemy_classes: Sequence[str],
    enemy_specs: Sequence[str | None] | None,
    bracket: str,
) -> str:
    """Стабильный ключ сетапа для кэша разборов.

    Спек приоритетнее класса ('paladin'→'ret-paladin', если известно), чтобы
    holy- и ret-версии кэшировались раздельно. Порядок врагов не важен (sorted).
    """
    specs = list(enemy_specs) if enemy_specs is not None else []
    tokens: list[str] = []
    for i, cls in enumerate(enemy_classes):
        spec = specs[i] if i < len(specs) else None
        tokens.append((spec or cls).strip().lower())
    enemy_key = ",".join(sorted(t for t in tokens if t))
    return f"{bracket}|{(our_comp or '?').lower()}|{enemy_key}"


# ── Кэш разборов (in-memory, TTL) ────────────────────────────────────────────


@dataclass
class _Entry:
    text: str
    created_at: float


class AdviceCache:
    """LRU+TTL кэш LLM-разборов по сигнатуре сетапа (per api-процесс).

    Персистентности нет намеренно (Phase 4.7): автодеплой рестартит сервис
    часто, а Haiku-регенерация редкого сетапа дёшева. Кэш убирает и задержку, и
    расход на ПОВТОРНЫХ встречах того же сетапа внутри аптайма процесса.
    """

    def __init__(
        self,
        ttl_s: float = 24 * 3600.0,
        max_entries: int = 256,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._ttl_s = ttl_s
        self._max = max_entries
        self._clock = clock
        self._data: OrderedDict[str, _Entry] = OrderedDict()

    def get(self, key: str, now: float | None = None) -> str | None:
        t = self._clock() if now is None else now
        entry = self._data.get(key)
        if entry is None:
            return None
        if t - entry.created_at > self._ttl_s:
            del self._data[key]
            return None
        self._data.move_to_end(key)
        return entry.text

    def put(self, key: str, text: str, now: float | None = None) -> None:
        if not key or not text.strip():
            return
        t = self._clock() if now is None else now
        self._data[key] = _Entry(text=text, created_at=t)
        self._data.move_to_end(key)
        while len(self._data) > self._max:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)


# ── Промпты ──────────────────────────────────────────────────────────────────

_ADVICE_SYSTEM = """\
Ты — тренер по 2v2/3v3 арене WoW TBC Classic (2.4.3, Anniversary). Игрок вот-вот
выйдет из ворот против сетапа, которого НЕТ в базе гайдов. Дай краткий разбор с
нуля, опираясь на общие принципы TBC-арены (кто сквиши, у кого escape/иммуны, кого
реально тренить, DR, кайт, пил хилера в притеснение).

Формат ответа (только по-русски, ≤110 слов, без вступлений и воды):
🎯 Килл-таргет: <класс/спек> — 1 короткая причина.
План: 2–3 пункта опенера/приоритетов, глаголами.
Опасности: 1–2 главные угрозы врага.
Это провизорный разбор без гайда — будь конкретен, но не выдумывай фактов."""

_POSTMATCH_SYSTEM = """\
Ты — тренер по арене WoW TBC 2.4.3. Бой закончился. По таймлайну событий и
KB-плану (если есть) дай КОРОТКИЙ персональный разбор игроку: что пошло так/не так
и что поправить в следующий раз. Ссылайся на конкретные моменты таймлайна
(тринкеты, дефы, CC и их тайминги). Только по-русски, ≤140 слов, по делу, без
общих фраз. Формат: 2–4 пункта, каждый — наблюдение → корректировка."""


# ── Генерация ────────────────────────────────────────────────────────────────


async def generate_comp_advice(
    client: Any,
    model: str,
    *,
    bracket: str,
    enemy_desc: str,
    our_comp: str | None,
    player_class: str | None,
) -> AdviceResult:
    """LLM-разбор незнакомого сетапа. Бросает — вызывающий ловит и фолбэчит."""
    player_line = f"Я играю за: {player_class}.\n" if player_class else ""
    user_msg = (
        f"Брекет: {bracket}.\n"
        f"Наш состав: {our_comp or 'неизвестен'}.\n"
        f"{player_line}"
        f"Враги: {enemy_desc}.\n\n"
        "Дай разбор по формату."
    )
    response = await client.messages.create(
        model=model,
        max_tokens=400,
        system=_ADVICE_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    return AdviceResult(text=_extract_text(response), usage=_extract_usage(response))


async def generate_postmatch_review(
    client: Any,
    model: str,
    *,
    digest: str,
    kb_plan: str | None,
) -> AdviceResult:
    """LLM-разбор боя из таймлайна + KB-плана. Бросает — вызывающий фолбэчит."""
    plan_line = f"\nKB-план матчапа:\n{kb_plan}\n" if kb_plan else "\n(матчапа в KB нет)\n"
    user_msg = f"Таймлайн боя:\n{digest}\n{plan_line}\nДай персональный разбор по формату."
    response = await client.messages.create(
        model=model,
        max_tokens=500,
        system=_POSTMATCH_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    return AdviceResult(text=_extract_text(response), usage=_extract_usage(response))


__all__ = [
    "PURPOSE_ADVICE",
    "PURPOSE_POSTMATCH",
    "AdviceCache",
    "AdviceResult",
    "TokenUsage",
    "comp_signature",
    "generate_comp_advice",
    "generate_postmatch_review",
]
