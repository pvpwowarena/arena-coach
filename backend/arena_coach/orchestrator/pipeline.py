"""End-to-end pipeline: bridge event → детерминированная подсказка (мгновенно) →
опционально LLM-разбор (фоново, вне горячего пути) → Discord DM + локальный голос.

Ключевое решение по скорости/КПД (Phase 4.7):
  • В БОЮ всё детерминированно и мгновенно — килл-таргет из frontmatter KB,
    тринкеты/дефы короткими фразами, предупреждения по классам врагов. LLM в
    горячем пути НЕ участвует (ждать модель 1-2с в арене нельзя).
  • LLM включается только при заданном ANTHROPIC_API_KEY и работает там, где даёт
    максимум пользы: (1) разбор НЕСТАНДАРТНОГО сетапа, которого нет в KB
    (mage+mage+mage, hpal+ret+rogue) — фоново, с кэшем по сигнатуре сетапа;
    (2) постматч-анализ по таймлайну. Без ключа pipeline остаётся чисто
    детерминированным.
  • Спеки врагов (из мостовых сигнатурных кастов) сужают матчап до нужного
    KB-документа; частично раскрытый состав даёт провизорный килл-таргет сразу.

События: ARENA_START (килл-таргет + опенер + угрозы), TRINKET (короткий план),
ABILITY (ключевые дефы, троттлинг), ARENA_END (постматч-разбор).

Phase 4.3: TRINKET/ABILITY (включая CC) пишутся в MatchRecorder → постматч.
Phase 4.6: короткая фраза кладётся в per-player очередь для локального голоса.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

import httpx

from arena_coach.access.advice_store import AdviceStore
from arena_coach.access.player_settings import DEFAULT_VOICE_MODE, PlayerSettingsService
from arena_coach.access.service import AccessService
from arena_coach.access.usage import UsageService
from arena_coach.kb.pronunciation import Pronouncer
from arena_coach.kb.retriever import KBRetriever
from arena_coach.kb.schema import KBDoc, Section
from arena_coach.kb.slang import SlangRenderer
from arena_coach.kb.spells import SpellCatalog
from arena_coach.orchestrator import advice as advice_mod
from arena_coach.orchestrator.advice import AdviceCache, TokenUsage, comp_signature
from arena_coach.orchestrator.hint_queue import HintQueue
from arena_coach.orchestrator.killpriority import heuristic_kill_target
from arena_coach.orchestrator.meta_comps import guess_line, likely_comps, stealth_comps
from arena_coach.orchestrator.postmatch import (
    MatchRecord,
    MatchRecorder,
    build_postmatch_report,
    parse_bridge_ts,
    timeline_digest,
    utcnow,
)
from arena_coach.orchestrator.reactions import (
    ABILITY_REACTIONS,
    HIGH,
    NORMAL,
    Reaction,
    ability_reaction,
    cast_reaction,
    category_reaction,
    trinket_reaction,
)
from arena_coach.orchestrator.threats import threat_lines, threat_voice
from arena_coach.orchestrator.voice_phrases import (
    arena_delta_phrase,
    arena_start_phrase,
    stealth_opener_phrase,
)
from arena_coach.shared.settings import Settings

log = logging.getLogger(__name__)

_HINT_EVENTS = {"ARENA_START", "TRINKET", "ABILITY"}

# ABILITY: подсказываем только на ключевые дефы/бурсты, меняющие план.
# Источник истины — таблица реакций: если на спелл нечего ответить, хинтить его
# нечем (Phase 4.10), поэтому список ключей выводится из неё, а не дублируется.
_ABILITY_HINT_KEYS = frozenset(ABILITY_REACTIONS)

_SECTION_PRIORITY: dict[str, list[str]] = {
    "ARENA_START": ["Opener", "Strategy", "Alternative opener"],
    "TRINKET": ["If enemy trinkets", "Post-trinket", "After trinket"],
    "ABILITY": ["Key cooldowns to track", "Mid-fight rotation", "Common mistakes"],
    "ARENA_END": ["Common mistakes"],
}

# Сколько фраза остаётся осмысленной в очереди локального голоса (Phase 4.11).
# Мост синтезирует речь последовательно и блокирующе, поэтому очередь реально
# простаивает: «тринкеть под кидни» через 8 секунд — уже вредный совет, а
# стартовый разбор на воротах терпит.
VOICE_TTL_HIGH_S = 10.0
VOICE_TTL_NORMAL_S = 7.0
VOICE_TTL_OPENER_S = 20.0

_ABILITY_REF_RE = re.compile(r"\[\[ability:([a-z0-9-]+)\]\]")
_PROVENANCE_RE = re.compile(r"^_Провенанс:.*?_\s*$", flags=re.MULTILINE | re.DOTALL)


class HintThrottle:
    """Анти-спам in-fight подсказок с приоритетами (Phase 4.11).

    Две итерации живого теста задали рамку:
      • 4.10 — «зациклило»: троттлинг был только на ABILITY, дубли TRINKET
        (мост поднимает 2 события на спелл: `SPELL_CAST_SUCCESS` +
        `SPELL_AURA_APPLIED`) проходили насквозь;
      • 4.11 — «старт + 1-2 реплики за матч»: интервал 20с между ABILITY плюс 5с
        тишины после любой подсказки убивали поток CC, который и есть бой.

    Поэтому здесь не «один хинт в 20 секунд», а бюджет речи:
      • тот же ключ не повторяем `repeat_s` (задаёт сама реакция: CC — 20с,
        тяжёлые КД — 60с, тринкет — 45с);
      • между репликами — `gap_s`, но `high`-приоритет пробивает его до `high_gap_s`
        (тринкет, стан под добивание, овца на хилере — решается сейчас);
      • не больше `max_per_min` реплик в минуту на игрока — потолок, чтобы
        мясорубка 3v3 не превратилась в скороговорку;
      • ARENA_START не троттлится: он дедуплицируется по сигнатуре состава выше,
        а повтор звучит короткой дельтой (`arena_delta_phrase`).
    """

    def __init__(
        self,
        gap_s: float = 5.0,
        high_gap_s: float = 2.5,
        default_repeat_s: float = 25.0,
        max_per_min: int = 12,
    ) -> None:
        self._gap_s = gap_s
        self._high_gap_s = high_gap_s
        self._default_repeat_s = default_repeat_s
        self._max_per_min = max_per_min
        self._last_any_at: dict[str, float] = {}
        self._last_key_at: dict[tuple[str, str], float] = {}
        self._recent: dict[str, deque[float]] = {}

    def allow(
        self,
        discord_id: str,
        event_type: str,
        key: str = "",
        now: float | None = None,
        priority: str = NORMAL,
        repeat_s: float | None = None,
    ) -> bool:
        """Пропускать ли подсказку. Побочный эффект: отмечает время выдачи."""
        t = time.monotonic() if now is None else now

        if event_type != "ARENA_START":
            k = (discord_id, f"{event_type}:{key.lower()}")
            last_key = self._last_key_at.get(k)
            window = self._default_repeat_s if repeat_s is None else repeat_s
            if last_key is not None and t - last_key < window:
                return False

            last_any = self._last_any_at.get(discord_id)
            gap = self._high_gap_s if priority == HIGH else self._gap_s
            if last_any is not None and t - last_any < gap:
                return False

            if not self._within_minute_budget(discord_id, t):
                return False
            self._last_key_at[k] = t

        self._mark(discord_id, t)
        return True

    def allow_ability(self, discord_id: str, spell_key: str, now: float | None = None) -> bool:
        """Совместимость со старыми вызовами/тестами."""
        return self.allow(discord_id, "ABILITY", spell_key, now)

    def note_delivered(self, discord_id: str, now: float | None = None) -> None:
        """Отметить, что игроку ушла подсказка (влияет на интервал и бюджет)."""
        self._mark(discord_id, time.monotonic() if now is None else now)

    # ── внутреннее ────────────────────────────────────────────────────────────

    def _within_minute_budget(self, discord_id: str, t: float) -> bool:
        recent = self._recent.get(discord_id)
        if recent is None:
            return True
        while recent and t - recent[0] > 60.0:
            recent.popleft()
        return len(recent) < self._max_per_min

    def _mark(self, discord_id: str, t: float) -> None:
        self._last_any_at[discord_id] = t
        recent = self._recent.setdefault(discord_id, deque())
        while recent and t - recent[0] > 60.0:
            recent.popleft()
        recent.append(t)


# ── Discord DM via REST ──────────────────────────────────────────────────────


async def _send_discord_dm(bot_token: str, discord_id: str, content: str) -> bool:
    """Отправить DM пользователю через Discord REST API."""
    headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            "https://discord.com/api/v10/users/@me/channels",
            headers=headers,
            json={"recipient_id": discord_id},
        )
        if not r.is_success:
            log.error(
                "Не удалось создать DM-канал для %s: %s %s", discord_id, r.status_code, r.text
            )
            return False
        channel_id = r.json()["id"]
        r2 = await client.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers=headers,
            json={"content": content},
        )
        if not r2.is_success:
            log.error("Не удалось отправить DM %s: %s %s", discord_id, r2.status_code, r2.text)
            return False
    log.info("Discord DM отправлен → %s", discord_id)
    return True


# ── Voice hint via bot-процесс (Phase 4.5) ───────────────────────────────────


async def _send_voice_hint(settings: Settings, text: str) -> bool:
    """POST короткой фразы в voice-приёмник bot-процесса. Строго best-effort."""
    if not settings.discord_voice_channel_id or not text:
        return False
    url = f"http://{settings.voice_http_host}:{settings.voice_http_port}/speak"
    headers = {}
    if settings.bridge_bearer_token:
        headers["Authorization"] = f"Bearer {settings.bridge_bearer_token}"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(url, json={"text": text}, headers=headers)
            return bool(resp.is_success)
    except Exception as exc:
        log.debug("Voice-хинт не доставлен (%s): %s", url, exc)
        return False


# ── KB helpers ────────────────────────────────────────────────────────────────


def _find_section(doc: KBDoc, priority: list[str]) -> Section | None:
    for target in priority:
        target_lower = target.lower()
        for sec in doc.sections:
            if target_lower in sec.title.lower():
                return sec
    return doc.sections[0] if doc.sections else None


def _clean(text: str, limit: int, slang: SlangRenderer | None = None) -> str:
    """Убрать [[ability:x]]-обёртки и провенанс, схлопнуть пустые строки, обрезать.

    С Phase 4.10 имена способностей идут через сленг-слой (`slang` не None):
    `[[ability:kidney-shot]]` → «кидни» вместо «kidney shot». Без рендерера —
    прежнее поведение (дефисы в пробелы), чтобы старые вызовы/тесты не ломались.
    """
    if slang is not None:
        cleaned = slang.render_refs(text)
    else:
        cleaned = _ABILITY_REF_RE.sub(lambda m: m.group(1).replace("-", " "), text)
    cleaned = _PROVENANCE_RE.sub("", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if len(cleaned) > limit:
        cleaned = cleaned[: limit - 1].rstrip() + "…"
    return cleaned


def _kill_target_line(doc: KBDoc) -> str:
    kt = doc.kill_target
    line = f"🎯 Килл-таргет: **{kt.primary}**"
    if kt.fallback:
        line += f" (запасной: {kt.fallback})"
    return line


def _alternates_line(candidates: list[KBDoc]) -> str | None:
    if len(candidates) < 2:
        return None
    others = ", ".join(f"`{d.composition} vs {d.vs}`" for d in candidates[1:3])
    return f"⚠️ Спек врагов не подтверждён. Если не сойдётся — смотри: {others}"


def _bracket_size(bracket: str) -> int:
    head = bracket.split("v", 1)[0].strip()
    return int(head) if head.isdigit() else 2


def _enemies_desc(classes: list[str], specs: list[str | None]) -> str:
    parts: list[str] = []
    for i, cls in enumerate(classes):
        spec = specs[i] if i < len(specs) else None
        parts.append(f"{cls}({spec})" if spec else cls)
    return ", ".join(parts) if parts else "?"


def _arena_voice(
    ctx: PipelineContext,
    player_name: str,
    session_id: str,
    enemy_classes: list[str],
    kill_target: str | None,
    threat_v: str | None,
) -> str:
    """Голос для ARENA_START: полная фраза в первый раз, дельта — при доуточнении.

    Аддон переотправляет ARENA_START, когда состав дорисовывается (выход из
    стелса, поздний зум): раньше игрок слышал всю стартовую фразу заново, включая
    предупреждение по угрозам, — именно это в живом тесте звучало как заевшая
    пластинка. Теперь второй и последующие анонсы в рамках сессии — только «Плюс
    рога. Килл таргет — прист.».
    """
    key = f"{player_name.lower()}|{session_id}"
    current = tuple(c for c in enemy_classes if c)
    previous = ctx._announced_enemies.get(key)
    ctx._announced_enemies[key] = current

    if previous is not None:
        seen = list(previous)
        fresh: list[str] = []
        for cls in current:
            if cls in seen:
                seen.remove(cls)  # мультимножество: дабл-рога остаётся дабл-рогой
            else:
                fresh.append(cls)
        return arena_delta_phrase(fresh, kill_target)

    # Угрозы (`threat_v`) в голос больше НЕ идут (Phase 4.11): стартовая фраза с
    # ними — это ~14 слов, около пяти секунд речи, а поллер моста синтезирует
    # блокирующе. Ровно в эти пять секунд летят сап/чип/нова — их реакции
    # простаивали в очереди и протухали по TTL. Предупреждения остались в DM на
    # воротах, где их и читают; в бою на те же угрозы есть отдельные реакции.
    _ = threat_v
    return arena_start_phrase(list(current), kill_target)


# ── Main pipeline ────────────────────────────────────────────────────────────


@dataclass
class PipelineContext:
    """Зависимости pipeline'а — инициализируются в lifespan FastAPI."""

    access_service: AccessService
    kb_retriever: KBRetriever
    anthropic_client: Any
    settings: Settings
    hint_throttle: HintThrottle = field(default_factory=HintThrottle)
    match_recorder: MatchRecorder = field(default_factory=MatchRecorder)
    hint_queue: HintQueue = field(default_factory=HintQueue)
    player_settings: PlayerSettingsService | None = None
    # Phase 4.7: учёт токенов (None без БД) + кэш LLM-разборов + фоновые задачи.
    usage_service: UsageService | None = None
    advice_cache: AdviceCache = field(default_factory=AdviceCache)
    advice_store: AdviceStore | None = None  # L2 персистентный кэш (None в тестах без БД)
    _bg_tasks: set[asyncio.Task[Any]] = field(default_factory=set)
    # Дедуп ARENA_START-DM: player+session → сигнатура последнего разбора.
    _last_arena_sig: dict[str, str] = field(default_factory=dict)
    # Phase 4.10: уже озвученный состав врагов (player+session → классы) —
    # чтобы доуточнение шло дельтой, а не повтором стартовой фразы.
    _announced_enemies: dict[str, tuple[str, ...]] = field(default_factory=dict)
    # Phase 4.10: сленг-рендерер (ленивая загрузка глоссария из KB).
    _slang: SlangRenderer | None = None
    # Phase 4.12: каталог способностей — что важно, решает бэкенд, а не мост.
    _spells: SpellCatalog | None = None
    # Phase 4.12: словарь произношения для TTS (ударения в сленге).
    _pronouncer: Pronouncer | None = None

    @property
    def slang(self) -> SlangRenderer:
        """Рендерер имён способностей (RU-сленг на выходе); грузится один раз."""
        if self._slang is None:
            self._slang = SlangRenderer.from_kb_path(self.settings.kb_path)
        return self._slang

    @property
    def spells(self) -> SpellCatalog:
        """Каталог realtime-способностей (id/имя → ключ+категория); грузится один раз."""
        if self._spells is None:
            self._spells = SpellCatalog.from_kb_path(self.settings.kb_path)
        return self._spells

    @property
    def pronouncer(self) -> Pronouncer:
        """Замены для TTS (ро́га, а не рога́); грузится один раз."""
        if self._pronouncer is None:
            self._pronouncer = Pronouncer.from_kb_path(self.settings.kb_path)
        return self._pronouncer

    @property
    def llm_enabled(self) -> bool:
        """LLM-слой активен только с боевым ключом (иначе — чистый детерминизм)."""
        return bool(self.settings.anthropic_api_key)

    def spawn_bg(self, coro: Any) -> None:
        """Фоновая задача (LLM вне горячего пути): не блокирует ack, ошибки логируем."""
        task = asyncio.ensure_future(coro)
        self._bg_tasks.add(task)
        task.add_done_callback(self._bg_done)

    def _bg_done(self, task: asyncio.Task[Any]) -> None:
        self._bg_tasks.discard(task)
        if not task.cancelled() and task.exception() is not None:
            log.error("Фоновая задача pipeline упала: %s", task.exception())

    async def drain_bg(self) -> None:
        """Дождаться фоновых задач (для тестов / graceful shutdown)."""
        while self._bg_tasks:
            await asyncio.gather(*list(self._bg_tasks), return_exceptions=True)


async def _record_usage(ctx: PipelineContext, purpose: str, model: str, usage: TokenUsage) -> None:
    """Best-effort запись расхода токенов (не должно ронять доставку)."""
    if ctx.usage_service is None:
        return
    try:
        await ctx.usage_service.record(purpose, model, usage.input_tokens, usage.output_tokens)
    except Exception as exc:
        log.warning("Не удалось записать usage (%s/%s): %s", purpose, model, exc)


async def _deliver(
    ctx: PipelineContext,
    discord_id: str,
    player_name: str,
    dm_text: str,
    voice_text: str | None,
    voice_mode: str,
    voice_ttl_s: float = VOICE_TTL_NORMAL_S,
) -> str:
    """Общая доставка: локальный голос (очередь + best-effort Discord-voice) + текст.

    `voice_ttl_s` — сколько фраза имеет смысл. Мост синтезирует речь блокирующе,
    очередь может простоять: советы по CC протухают быстро, стартовый разбор — нет.
    """
    voice_sent = False
    if voice_mode != "off" and voice_text:
        # Ударения правим только в голосе: в DM человек читает нормальный текст.
        spoken = ctx.pronouncer.apply(voice_text)
        ctx.hint_queue.push(player_name, spoken, ttl_s=voice_ttl_s)
        voice_sent = await _send_voice_hint(ctx.settings, spoken)
    if voice_mode == "only" and voice_sent:
        return "sent"
    ok = await _send_discord_dm(ctx.settings.discord_bot_token, discord_id, dm_text)
    return "sent" if ok or voice_sent else "error"


def _voice_ttl(reaction: Reaction | None) -> float:
    """Окно годности фразы в очереди голоса — по приоритету реакции."""
    if reaction is not None and reaction.priority == HIGH:
        return VOICE_TTL_HIGH_S
    return VOICE_TTL_NORMAL_S


async def _emit_arena(
    ctx: PipelineContext,
    discord_id: str,
    player_name: str,
    session_id: str,
    sig: str,
    dm_text: str,
    voice_text: str | None,
    voice_mode: str,
) -> str:
    """ARENA_START-доставка с дедупом по сигнатуре в рамках сессии (анти-спам re-emit)."""
    sig_key = f"{player_name.lower()}|{session_id}"
    if ctx._last_arena_sig.get(sig_key) == sig:
        log.debug("ARENA_START %s не изменился (%s) — не дублируем", sig_key, sig)
        return "skipped"
    ctx._last_arena_sig[sig_key] = sig
    return await _deliver(
        ctx, discord_id, player_name, dm_text, voice_text, voice_mode, VOICE_TTL_OPENER_S
    )


# ── Постматч (Phase 4.3 + LLM 4.7) ───────────────────────────────────────────


async def _finish_match(ctx: PipelineContext, player_name: str) -> str:
    """ARENA_END: DM-разбор боя (LLM при ключе, иначе детерминированный)."""
    record = ctx.match_recorder.finish(player_name)
    if record is None:
        return "skipped"
    if not record.events:
        log.info("Постматч: %s — 0 событий, отчёт не шлём", player_name)
        return "skipped"

    entry = await ctx.access_service.find_by_character(player_name)
    if entry is None:
        log.warning("Постматч: игрок '%s' не в whitelist", player_name)
        return "no_player"

    candidates = ctx.kb_retriever.find_realtime_candidates(
        record.enemy_classes, record.our_comp_hint
    )
    doc = candidates[0] if candidates else None
    report = await _build_postmatch(ctx, record, doc)
    ok = await _send_discord_dm(ctx.settings.discord_bot_token, entry.discord_id, report)
    return "sent" if ok else "error"


#: Ниже этого числа событий LLM-разбор не запускаем (Phase 4.12).
POSTMATCH_MIN_EVENTS = 3


async def _build_postmatch(ctx: PipelineContext, record: MatchRecord, doc: KBDoc | None) -> str:
    """LLM-разбор боя (если ключ есть), иначе детерминированный отчёт-таймлайн."""
    deterministic = build_postmatch_report(record, doc)
    if not ctx.llm_enabled:
        return deterministic
    if len(record.events) < POSTMATCH_MIN_EVENTS:
        # На одном событии модель начинает сочинять: живой тест 30.07 получил
        # разбор с «оба рога должны открываться на шамана» при составе
        # rogue+resto-druid и с несуществующим предметом. Мало данных — честно
        # говорим об этом, а не выдаём выдумку за анализ.
        log.info("Постматч: событий %d — LLM не зовём", len(record.events))
        return (
            f"{deterministic}\n\n"
            "🧠 Разбирать нечего: в бою записалось меньше "
            f"{POSTMATCH_MIN_EVENTS} событий. Обычно это значит, что мост стартовал "
            "позже боя или враги не использовали ничего из отслеживаемого."
        )[:2000]
    model = ctx.settings.anthropic_model_synth
    try:
        kb_plan: str | None = None
        if doc is not None:
            sec = _find_section(doc, _SECTION_PRIORITY["ARENA_START"])
            body = _clean(sec.body_md, 600) if sec else ""
            kb_plan = f"Килл-таргет: {doc.kill_target.primary}. {body}"
        result = await advice_mod.generate_postmatch_review(
            ctx.anthropic_client, model, digest=timeline_digest(record), kb_plan=kb_plan
        )
        await _record_usage(ctx, advice_mod.PURPOSE_POSTMATCH, model, result.usage)
        if not result.text:
            return deterministic
        header = deterministic.split("\n\n", 1)[0]
        return f"{header}\n\n🧠 **Разбор тренера:**\n{result.text}"[:2000]
    except Exception as exc:
        log.error("Постматч-LLM упал (%s) — детерминированный отчёт", exc)
        return deterministic


# ── ARENA_START ───────────────────────────────────────────────────────────────


async def _handle_arena_start(
    ctx: PipelineContext,
    discord_id: str,
    player_name: str,
    session_id: str,
    voice_mode: str,
    bracket: str,
    enemy_classes: list[str],
    enemy_specs: list[str | None],
    our_comp_hint: str | None,
    player_class: str | None,
    stealth: bool = False,
) -> str:
    candidates = ctx.kb_retriever.find_realtime_candidates(
        enemy_classes, our_comp_hint, enemy_specs=enemy_specs
    )
    doc = candidates[0] if candidates else None
    threats = threat_lines(enemy_classes, enemy_specs)
    threat_v = threat_voice(enemy_classes, enemy_specs, limit=1)

    if doc is not None:
        dm_lines = [
            f"🏟 **{doc.composition} vs {doc.vs}** | {bracket} | сложность: {doc.difficulty.value}",
            _kill_target_line(doc),
            *threats,
        ]
        sec = _find_section(doc, _SECTION_PRIORITY["ARENA_START"])
        if sec is not None:
            dm_lines.append(f"📖 Опенер: {_clean(sec.body_md, 380)}")
        alt = _alternates_line(candidates)
        if alt:
            dm_lines.append(alt)
        dm_lines.append(f"📖 `/matchup our:{doc.composition} vs:{doc.vs}` — полный гайд")
        voice_text = _arena_voice(
            ctx, player_name, session_id, enemy_classes, doc.kill_target.primary, threat_v
        )
        return await _emit_arena(
            ctx,
            discord_id,
            player_name,
            session_id,
            f"kb:{doc.slug}",
            "\n".join(dm_lines)[:2000],
            voice_text,
            voice_mode,
        )

    enemies_desc = _enemies_desc(enemy_classes, enemy_specs)
    if len(enemy_classes) < _bracket_size(bracket):
        return await _emit_partial(
            ctx,
            discord_id,
            player_name,
            session_id,
            voice_mode,
            bracket,
            enemies_desc,
            enemy_classes,
            our_comp_hint,
            threats,
            threat_v,
            stealth=stealth,
        )
    return await _emit_unknown(
        ctx,
        discord_id,
        player_name,
        session_id,
        voice_mode,
        bracket,
        enemies_desc,
        enemy_classes,
        enemy_specs,
        our_comp_hint,
        player_class,
        threats,
        threat_v,
    )


async def _emit_partial(
    ctx: PipelineContext,
    discord_id: str,
    player_name: str,
    session_id: str,
    voice_mode: str,
    bracket: str,
    enemies_desc: str,
    enemy_classes: list[str],
    our_comp_hint: str | None,
    threats: list[str],
    threat_v: str | None,
    stealth: bool = False,
) -> str:
    """Состав раскрыт частично: провизорный килл-таргет, если частичные кандидаты
    сходятся; полноценный разбор придёт с полным re-emit состава."""
    if not enemy_classes:
        # Пустой состав НЕ означает инвиз (Phase 4.12). На воротах мы ещё никого
        # не видели — классы узнаются из их кастов, поэтому первый ARENA_START
        # всегда приходит пустым, и голос каждую арену объявлял стелс-опенер
        # (живой тест 30.07). Настоящий стелс мост присылает отдельным маркером
        # `phase=stealth` — только он озвучивается.
        if stealth:
            dm_lines = [
                f"🏟 **Арена** | {bracket} | врагов не видно — вероятен **стелс-опенер**",
                "🛡 Кучкуйтесь у столба, пилы наготове; тринкет не сливайте на первый стан — "
                "берегите на их килл-чейн. Состав уточню, как только кто-то откроется.",
            ]
            stealth_guess = guess_line(stealth_comps(bracket))
            if stealth_guess:
                dm_lines.append(f"{stealth_guess} — жди сап/опенер в хилера.")
            voice: str | None = stealth_opener_phrase()
            sig0 = "partial0:stealth"
        else:
            dm_lines = [
                f"🏟 **Арена** | {bracket} | состав врагов пока не раскрыт — уточню по их первым действиям",
            ]
            voice = None  # молчим: на воротах говорить ещё нечего
            sig0 = "partial0:gates"
        return await _emit_arena(
            ctx,
            discord_id,
            player_name,
            session_id,
            sig0,
            "\n".join(dm_lines)[:2000],
            voice,
            voice_mode,
        )
    partial = ctx.kb_retriever.find_partial_candidates(enemy_classes, our_comp_hint)
    kill_targets = {d.kill_target.primary for d in partial}
    dm_lines = [f"🏟 **Арена** | {bracket} | видно: {enemies_desc} _(состав уточняется…)_"]
    voice_kt: str | None = None
    if len(kill_targets) == 1:
        voice_kt = next(iter(kill_targets))
        dm_lines.append(f"🎯 Вероятный килл-таргет: **{voice_kt}** _(уточнится по мере раскрытия)_")
        sig = f"partial1:{voice_kt}"
    else:
        sig = f"partial0:{','.join(sorted(enemy_classes))}"
    meta_guess = guess_line(likely_comps(enemy_classes, bracket))
    if meta_guess:
        dm_lines.append(meta_guess)
    dm_lines.extend(threats)
    voice_text = _arena_voice(ctx, player_name, session_id, enemy_classes, voice_kt, threat_v)
    return await _emit_arena(
        ctx,
        discord_id,
        player_name,
        session_id,
        sig,
        "\n".join(dm_lines)[:2000],
        voice_text,
        voice_mode,
    )


async def _emit_unknown(
    ctx: PipelineContext,
    discord_id: str,
    player_name: str,
    session_id: str,
    voice_mode: str,
    bracket: str,
    enemies_desc: str,
    enemy_classes: list[str],
    enemy_specs: list[str | None],
    our_comp_hint: str | None,
    player_class: str | None,
    threats: list[str],
    threat_v: str | None,
) -> str:
    """Нестандартный сетап без KB: мгновенно эвристика+угрозы; при ключе — фоновой
    LLM-разбор с кэшем (второй раз тот же сетап отдаётся сразу)."""
    sig_key = comp_signature(our_comp_hint, enemy_classes, enemy_specs, bracket)
    pick = heuristic_kill_target(enemy_classes, enemy_specs)
    kt_target = pick.target if pick else None

    dm_lines = [f"🏟 **Нестандартный сетап** | {bracket} | враги: {enemies_desc}"]
    cached = ctx.advice_cache.get(sig_key)
    if cached is None and ctx.advice_store is not None:
        row = await ctx.advice_store.get(sig_key)
        if row is not None:
            cached = row.text
            ctx.advice_cache.put(sig_key, cached)  # прогреваем L1 из L2-персиста
    # Спек-фоллбэк (Wave 0): мост раскрыл спек → сигнатура сузилась и промахнулась,
    # хотя класс-уровневый разбор (офлайн-сид или прежняя генерация) уже есть.
    # Класс-тексты содержат хеджи по спекам («если шаман элем — …»), поэтому
    # отдаём их и НЕ жжём токены на почти дублирующую генерацию.
    if cached is None:
        class_sig = comp_signature(our_comp_hint, enemy_classes, None, bracket)
        if class_sig != sig_key:
            cached = ctx.advice_cache.get(class_sig)
            if cached is None and ctx.advice_store is not None:
                row = await ctx.advice_store.get(class_sig)
                if row is not None:
                    cached = row.text
            if cached is not None:
                ctx.advice_cache.put(sig_key, cached)  # спек-ключ больше не промахнётся
    if cached:
        dm_lines.append(f"🧠 {cached}")
    else:
        if kt_target:
            dm_lines.append(f"🎯 ≈ Килл-таргет (эвристика): **{kt_target}**")
        dm_lines.extend(threats)
        if ctx.llm_enabled:
            dm_lines.append("🧠 Генерю разбор под этот сетап — придёт следующим сообщением…")
        else:
            dm_lines.append(
                "📚 Матчапа в KB нет — разбор по общим принципам. Добавь через /matchup."
            )

    if ctx.llm_enabled and not cached:
        ctx.spawn_bg(
            _generate_and_send_advice(
                ctx, discord_id, sig_key, bracket, enemies_desc, our_comp_hint, player_class
            )
        )

    voice_text = _arena_voice(ctx, player_name, session_id, enemy_classes, kt_target, threat_v)
    # Дедуп по СОДЕРЖИМОМУ (без заголовка): спек-reveal меняет сигнатуру, но если
    # фоллбэк вернул тот же текст разбора — повторный DM игроку не нужен. Если же
    # содержимое реально изменилось (новые угрозы/разбор) — хеш другой, шлём.
    body_hash = hashlib.sha1("\n".join(dm_lines[1:]).encode("utf-8")).hexdigest()[:12]
    sig = f"unknown:{body_hash}"
    return await _emit_arena(
        ctx,
        discord_id,
        player_name,
        session_id,
        sig,
        "\n".join(dm_lines)[:2000],
        voice_text,
        voice_mode,
    )


async def _generate_and_send_advice(
    ctx: PipelineContext,
    discord_id: str,
    sig_key: str,
    bracket: str,
    enemies_desc: str,
    our_comp_hint: str | None,
    player_class: str | None,
) -> None:
    """Фон: LLM-разбор незнакомого сетапа → кэш (L1+L2) → отдельный DM. Ошибки не ронят ack."""
    model = ctx.settings.anthropic_model_advice
    result = await advice_mod.generate_comp_advice(
        ctx.anthropic_client,
        model,
        bracket=bracket,
        enemy_desc=enemies_desc,
        our_comp=our_comp_hint,
        player_class=player_class,
    )
    await _record_usage(ctx, advice_mod.PURPOSE_ADVICE, model, result.usage)
    if not result.text:
        return
    ctx.advice_cache.put(sig_key, result.text)
    if ctx.advice_store is not None:
        await ctx.advice_store.put(sig_key, result.text, model)
    await _send_discord_dm(
        ctx.settings.discord_bot_token,
        discord_id,
        f"🧠 **Разбор ({enemies_desc}):**\n{result.text}"[:2000],
    )


# ── TRINKET / ABILITY (детерминированно, мгновенно) ──────────────────────────


async def _handle_trinket(
    ctx: PipelineContext,
    discord_id: str,
    player_name: str,
    voice_mode: str,
    source: str,
    doc: KBDoc | None,
) -> str:
    reaction = trinket_reaction()
    # В бою длинный план из KB не читается («огромный текст в бою читать не очень
    # удобно», живой тест 30.07) — оставляем две строки, разбор ждёт в /matchup.
    dm_lines = [f"💎 **{source} тринкетнул!**", reaction.dm]
    if doc is not None:
        dm_lines[0] += f" | {doc.composition} vs {doc.vs}"
    return await _deliver(
        ctx,
        discord_id,
        player_name,
        "\n".join(dm_lines)[:2000],
        reaction.voice,
        voice_mode,
        _voice_ttl(reaction),
    )


async def _handle_ability(
    ctx: PipelineContext,
    discord_id: str,
    player_name: str,
    voice_mode: str,
    source: str,
    spell_key: str,
    reaction: Reaction | None,
) -> str:
    # Имя способности — через сленг-слой: «кидни», а не «kidney_shot».
    name = ctx.slang.name(spell_key.replace("_", "-"))
    dm_lines = [f"⚡ **{name[:1].upper()}{name[1:]} у {source}**"]
    # Секцию «Key cooldowns to track» в бою НЕ вставляем: это перечень всех КД
    # обеих команд — ровно тот шум, из-за которого realtime-подсказки выглядели
    # «ни о чём». Ответ на конкретный КД — реакция; полный список даёт /matchup.
    if reaction is not None:
        dm_lines.append(reaction.dm)
    else:  # в _ABILITY_HINT_KEYS попадают только ключи из таблицы — страховка
        dm_lines.append("Учитывай этот КД врага в следующем размене.")
    voice = reaction.voice if reaction is not None else f"{name} у врага."
    ttl = _voice_ttl(reaction)
    return await _deliver(
        ctx, discord_id, player_name, "\n".join(dm_lines)[:2000], voice, voice_mode, ttl
    )


# ── Диспетчер ─────────────────────────────────────────────────────────────────


async def process_event(ctx: PipelineContext, envelope: dict[str, Any]) -> str:
    """Обработать событие из bridge.

    Returns:
        Статус: "sent", "no_matchup", "no_player", "skipped", "throttled", "error"
    """
    event = envelope.get("event", {})
    event_type = event.get("type", "")
    player_name = str(envelope.get("player_name", ""))
    match_info = envelope.get("match", {})
    bracket = str(match_info.get("bracket", "unknown"))
    enemies_raw = match_info.get("enemies", [])
    session_id = str(envelope.get("session_id", ""))

    # ── 0. Резолв способности (Phase 4.12) ──────────────────────────────
    # Мост больше не решает, что важно: он форвардит все касты врагов (id + slug
    # имени), а каталог `kb/glossary/realtime_spells.json` превращает это в
    # канонический ключ и категорию. Новый класс/спелл = правка данных, без релиза.
    ts = parse_bridge_ts(str(envelope.get("bridge_ts", ""))) or utcnow()
    raw_key = str(event.get("spell_key", "") or event.get("trinket_key", ""))
    spell_name = str(event.get("spell_name", ""))
    try:
        spell_id = int(event.get("spell_id", 0) or 0)
    except (TypeError, ValueError):
        spell_id = 0
    spell_key = raw_key
    # Ключ анти-спама: у именной реакции — сам спелл, у общей — категория. Иначе
    # ловушка и скаттер ханта (обе «incapacitate») прочитали бы подряд одну и ту
    # же фразу — та самая заевшая пластинка, но уже на общих репликах.
    throttle_subject = raw_key
    hint_reaction: Reaction | None = None
    cast_phase = str(event.get("cast_phase", ""))
    if event_type == "ABILITY":
        info = ctx.spells.resolve(spell_id, raw_key, spell_name)
        spell_key = info.key or raw_key
        if cast_phase == "start":
            # Каст только начался: предупреждаем лишь о том, что помечено
            # `cast_alert` (хилы и кастуемый контроль) — остальное превратилось бы
            # в поток из шоков и автоатак. Зато это единственная подсказка ДО факта.
            cast_cat = info.cast_category or info.category
            hint_reaction = cast_reaction(cast_cat) if info.cast_alert else None
            throttle_subject = f"cast:{cast_cat}"
        else:
            hint_reaction = ability_reaction(spell_key)
            throttle_subject = spell_key
            if hint_reaction is None and info.category not in ("heal", "cast_cc"):
                # Состоявшийся хил комментировать поздно — реагируем только на старт.
                hint_reaction = category_reaction(info.category)
                throttle_subject = f"cat:{info.category}"
    elif event_type == "TRINKET":
        hint_reaction = trinket_reaction()

    # ── 0b. Постматч-копилка (до хинт-фильтров) ─────────────────────────
    if event_type == "ARENA_START":
        ctx.match_recorder.start(
            player_name,
            session_id,
            ts,
            bracket=str(bracket),
            enemies=[{str(k): str(v) for k, v in e.items() if v is not None} for e in enemies_raw],
            our_comp_hint=str(match_info.get("our_comp_hint") or "") or None,
        )
    elif event_type in ("TRINKET", "ABILITY") and hint_reaction is not None:
        # Пишем только то, что каталог опознал: мост форвардит все касты, и без
        # фильтра постматч-таймлайн превратился бы в дамп боевого лога.
        ctx.match_recorder.note(
            player_name, ts, event_type, str(event.get("source_name", "враг")), spell_key
        )
    elif event_type == "ARENA_END":
        return await _finish_match(ctx, player_name)

    # ── 1. Фильтр важных событий ────────────────────────────────────────
    if event_type not in _HINT_EVENTS:
        return "skipped"
    if event_type == "ABILITY" and hint_reaction is None:
        # Способности нет ни в именной таблице, ни в категориях каталога.
        log.debug("ABILITY %s (id=%s, name=%r) не опознан — молчим", raw_key, spell_id, spell_name)
        return "skipped"

    # ── 2. Игрок в whitelist ────────────────────────────────────────────
    entry = await ctx.access_service.find_by_character(player_name)
    if entry is None:
        log.warning("Игрок '%s' не найден в whitelist", player_name)
        return "no_player"
    discord_id = entry.discord_id

    # ── 3. Троттлинг in-fight (Phase 4.11: приоритеты + бюджет речи) ────
    throttle_key = (
        throttle_subject if event_type == "ABILITY" else str(event.get("source_name", ""))
    )
    if not ctx.hint_throttle.allow(
        discord_id,
        event_type,
        throttle_key,
        priority=hint_reaction.priority if hint_reaction else NORMAL,
        repeat_s=hint_reaction.repeat_s if hint_reaction else None,
    ):
        log.debug(
            "Подсказка %s/%s для %s подавлена троттлингом", event_type, throttle_key, discord_id
        )
        return "throttled"

    # ── 4. Состав врагов: классы + спеки ────────────────────────────────
    enemy_classes = [str(e.get("wow_class", "")).upper() for e in enemies_raw if e.get("wow_class")]
    enemy_specs: list[str | None] = [
        (str(e["spec"]).lower() if e.get("spec") else None)
        for e in enemies_raw
        if e.get("wow_class")
    ]
    our_comp_hint: str | None = match_info.get("our_comp_hint") or None
    player_class: str | None = str(match_info.get("player_class") or "") or None

    # ── 5. Режим голоса ─────────────────────────────────────────────────
    voice_mode = DEFAULT_VOICE_MODE
    if ctx.player_settings is not None:
        voice_mode = await ctx.player_settings.get_voice_mode(discord_id)

    # ── 6. Диспетч ──────────────────────────────────────────────────────
    if event_type == "ARENA_START":
        return await _handle_arena_start(
            ctx,
            discord_id,
            player_name,
            session_id,
            voice_mode,
            bracket,
            enemy_classes,
            enemy_specs,
            our_comp_hint,
            player_class,
            stealth=str(event.get("phase", "")) == "stealth",
        )

    candidates = ctx.kb_retriever.find_realtime_candidates(
        enemy_classes, our_comp_hint, enemy_specs=enemy_specs
    )
    doc = candidates[0] if candidates else None
    source = str(event.get("source_name", "враг"))
    if event_type == "TRINKET":
        return await _handle_trinket(ctx, discord_id, player_name, voice_mode, source, doc)
    return await _handle_ability(
        ctx, discord_id, player_name, voice_mode, source, spell_key, hint_reaction
    )
