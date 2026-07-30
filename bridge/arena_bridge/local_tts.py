"""Локальный системный TTS (Phase 4.6): персональный голос на машине игрока.

Каждый игрок слышит ТОЛЬКО свои подсказки — локально, через штатный синтезатор
речи ОС, без Discord voice-канала и без интернета. Мост-поллер забирает фразы
игрока (`GET /v1/hints`) и передаёт их сюда.

Диспетч по `sys.platform`:
  • macOS   → `say -v Milena "<текст>"` (Milena — штатный RU-голос; если не
              установлен — резолвим на дефолтный, чтобы не молчать/не падать);
  • Windows → PowerShell `System.Speech.SpeechSynthesizer` (русский голос через
              SelectVoiceByHints(ru-RU); если нет — системный дефолт);
  • Linux   → `espeak-ng` (или `espeak`), если установлен; иначе no-op.

Осознанно БЕЗ новых Python-зависимостей и БЕЗ сети: только stdlib (subprocess),
поэтому PyInstaller-бинарь не пухнет и hiddenimports не трогаем (в отличие от
edge-tts из Discord-голоса 4.5). Всё best-effort: нет бинаря / ошибка запуска —
тихий no-op, мост не падает.

Проигрывание неблокирующее для event-loop (asyncio-subprocess), но `say()`
дожидается конца проговаривания — так реплики не наслаиваются друг на друга.
"""

from __future__ import annotations

import asyncio
import logging
import re
import shutil
import sys
from collections.abc import Awaitable, Callable

log = logging.getLogger(__name__)

#: Предпочитаемые русские голоса macOS (по убыванию желания).
_MACOS_PREFERRED_VOICES = ("Milena", "Katya", "Yuri")

#: Строка `say -v ?`: "Milena              ru_RU    # ...". Имя может быть с
#: пробелом ("Bad News"), поэтому берём всё до двойного пробела перед локалью.
_VOICE_LINE_RE = re.compile(r"^(?P<name>.+?)\s{2,}(?P<locale>[a-zA-Z]{2}[-_][A-Za-z]{2})")

Spawner = Callable[[list[str]], Awaitable[int]]
VoiceLister = Callable[[], Awaitable[list[tuple[str, str]]]]
WhichFn = Callable[[str], "str | None"]


# ── Чистая сборка команды (легко тестируется, без subprocess) ────────────────


def _powershell_speak_script(text: str) -> str:
    """PS-скрипт озвучки через System.Speech; RU-голос, если доступен."""
    safe = text.replace("'", "''")  # экранируем одинарные кавычки PowerShell
    return (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "try { $s.SelectVoiceByHints("
        "[System.Speech.Synthesis.VoiceGender]::NotSet, "
        "[System.Speech.Synthesis.VoiceAge]::NotSet, 0, "
        "(New-Object System.Globalization.CultureInfo('ru-RU'))) } catch {}; "
        f"$s.Speak('{safe}')"
    )


def build_command(
    platform: str,
    text: str,
    *,
    binary: str | None = None,
    mac_voice: str | None = "Milena",
) -> list[str] | None:
    """Собрать argv системного TTS под платформу. None = TTS для платформы нет.

    Чистая функция: диспетч по платформе тестируется без запуска процессов.
    `binary` (если задан) используется как argv[0] — это which-резолвнутый путь
    (напр. espeak vs espeak-ng); иначе берётся каноническое имя команды.
    """
    clean = text.strip()
    if not clean:
        return None
    if platform == "darwin":
        exe = binary or "say"
        return [exe, "-v", mac_voice, clean] if mac_voice else [exe, clean]
    if platform == "win32":
        exe = binary or "powershell"
        return [exe, "-NoProfile", "-NonInteractive", "-Command", _powershell_speak_script(clean)]
    if platform.startswith("linux"):
        exe = binary or "espeak-ng"
        return [exe, clean]
    return None


# ── Реальные subprocess-обёртки (заменяются фейками в тестах) ─────────────────


async def _spawn(argv: list[str]) -> int:
    """Запустить процесс неблокирующе для loop; дождаться конца, вернуть код."""
    proc = await asyncio.create_subprocess_exec(
        *argv,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    return await proc.wait()


async def _list_macos_voices() -> list[tuple[str, str]]:
    """(имя, локаль) из `say -v ?`; [] при любой ошибке."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "say",
            "-v",
            "?",
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        out, _ = await proc.communicate()
    except Exception:
        return []
    result: list[tuple[str, str]] = []
    for line in out.decode("utf-8", errors="replace").splitlines():
        m = _VOICE_LINE_RE.match(line)
        if m:
            result.append((m.group("name").strip(), m.group("locale")))
    return result


# ── LocalTTS ─────────────────────────────────────────────────────────────────


class LocalTTS:
    """Обёртка над системным TTS. Синхронный `available`, асинхронный `say`.

    Все внешние эффекты (which / subprocess / список голосов) инъектируются —
    тесты подменяют их фейками и проверяют диспетч по платформе без реальной
    речи.
    """

    def __init__(
        self,
        *,
        platform: str | None = None,
        which: WhichFn | None = None,
        spawn: Spawner | None = None,
        list_voices: VoiceLister | None = None,
    ) -> None:
        self._platform = platform if platform is not None else sys.platform
        which_fn: WhichFn = which or shutil.which
        self._spawn: Spawner = spawn or _spawn
        self._list_voices: VoiceLister = list_voices or _list_macos_voices
        self._binary: str | None = self._resolve_binary(which_fn)
        self._mac_voice: str | None = None
        self._mac_voice_resolved = False

    def _resolve_binary(self, which_fn: WhichFn) -> str | None:
        if self._platform == "darwin":
            return which_fn("say")
        if self._platform == "win32":
            return which_fn("powershell") or which_fn("powershell.exe")
        if self._platform.startswith("linux"):
            return which_fn("espeak-ng") or which_fn("espeak")
        return None

    @property
    def available(self) -> bool:
        """Есть ли на этой платформе рабочий TTS-бинарь."""
        return self._binary is not None

    def describe(self) -> str:
        """Короткая метка движка для --check-config/логов."""
        if self._platform == "darwin":
            return "macOS say"
        if self._platform == "win32":
            return "Windows PowerShell System.Speech"
        if self._platform.startswith("linux"):
            return f"Linux {self._binary or 'espeak-ng'}"
        return f"нет TTS для платформы {self._platform}"

    async def resolve_voice(self) -> str | None:
        """Имя фактически выбранного голоса (macOS) — для лога и диагностики.

        Живой тест 30.07: «голос как у робота». Причина — Milena не установлена, и
        `say` читает кириллицу дефолтным английским голосом. В логе это никак не
        отражалось, поэтому поймать было нечем; теперь мост печатает, какой голос
        реально выбран, и предупреждает, если русского нет.
        """
        if self._platform != "darwin":
            return None
        if not self._mac_voice_resolved:
            self._mac_voice = await self._resolve_mac_voice()
            self._mac_voice_resolved = True
        return self._mac_voice

    async def say(self, text: str) -> bool:
        """Озвучить фразу. Никогда не бросает; False = недоступно/не удалось.

        Дожидается конца проговаривания (реплики не наслаиваются). Для macOS при
        первом вызове лениво резолвит русский голос.
        """
        if self._binary is None:
            return False
        clean = text.strip()
        if not clean:
            return False
        try:
            if self._platform == "darwin" and not self._mac_voice_resolved:
                self._mac_voice = await self._resolve_mac_voice()
                self._mac_voice_resolved = True
            argv = build_command(
                self._platform, clean, binary=self._binary, mac_voice=self._mac_voice
            )
            if argv is None:
                return False
            code = await self._spawn(argv)
            if code != 0:
                log.debug("Локальный TTS: '%s' завершился с кодом %s", argv[0], code)
            return code == 0
        except Exception as exc:  # subprocess/OS — best-effort, мост важнее
            log.debug("Локальный TTS не смог озвучить (%s)", exc)
            return False

    async def _resolve_mac_voice(self) -> str | None:
        """Выбрать русский голос macOS: preferred → любой ru → None (дефолт)."""
        try:
            voices = await self._list_voices()
        except Exception:
            return "Milena"  # проба не удалась — пробуем штатный RU-голос
        names = {name for name, _ in voices}
        for pref in _MACOS_PREFERRED_VOICES:
            if pref in names:
                return pref
        for name, locale in voices:
            if locale.lower().startswith("ru"):
                return name
        return None  # русских голосов нет — дефолтный лучше тишины/ошибки
