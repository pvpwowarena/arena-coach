"""Тесты Phase 4.6 (мост): локальный системный TTS.

Реальную речь не запускаем — subprocess (`spawn`), детект бинаря (`which`) и
список голосов macOS (`list_voices`) инъектируются фейками. Проверяем чистый
диспетч по платформе (`build_command`) и поведение `LocalTTS.say`.
"""

from __future__ import annotations

from collections.abc import Callable

from arena_bridge.local_tts import LocalTTS, build_command

# ── build_command (чистая функция) ───────────────────────────────────────────


class TestBuildCommand:
    def test_darwin_default_milena(self) -> None:
        assert build_command("darwin", "Айсблок!") == ["say", "-v", "Milena", "Айсблок!"]

    def test_darwin_no_voice_plain_say(self) -> None:
        assert build_command("darwin", "текст", mac_voice=None) == ["say", "текст"]

    def test_darwin_custom_binary(self) -> None:
        assert build_command("darwin", "x", binary="/usr/bin/say") == [
            "/usr/bin/say",
            "-v",
            "Milena",
            "x",
        ]

    def test_win32_powershell_script(self) -> None:
        argv = build_command("win32", "Тринкет у X!")
        assert argv is not None
        assert argv[0] == "powershell"
        assert "-Command" in argv
        assert "System.Speech" in argv[-1]
        assert "Тринкет у X!" in argv[-1]

    def test_win32_escapes_quotes(self) -> None:
        argv = build_command("win32", "it's")
        assert argv is not None
        assert "it''s" in argv[-1]  # одинарная кавычка удвоена для PS

    def test_linux_espeak(self) -> None:
        assert build_command("linux", "Арена") == ["espeak-ng", "Арена"]

    def test_linux_custom_binary(self) -> None:
        assert build_command("linux", "x", binary="/usr/bin/espeak") == ["/usr/bin/espeak", "x"]

    def test_unknown_platform_none(self) -> None:
        assert build_command("freebsd", "x") is None

    def test_empty_text_none(self) -> None:
        assert build_command("darwin", "   ") is None
        assert build_command("win32", "") is None


# ── Фейки для LocalTTS ───────────────────────────────────────────────────────


def _which(mapping: dict[str, str]) -> Callable[[str], str | None]:
    return lambda cmd: mapping.get(cmd)


class _RecordingSpawn:
    def __init__(self, code: int = 0, raises: bool = False) -> None:
        self.calls: list[list[str]] = []
        self._code = code
        self._raises = raises

    async def __call__(self, argv: list[str]) -> int:
        self.calls.append(argv)
        if self._raises:
            raise OSError("subprocess boom")
        return self._code


class _Voices:
    def __init__(self, items: list[tuple[str, str]]) -> None:
        self.items = items
        self.calls = 0

    async def __call__(self) -> list[tuple[str, str]]:
        self.calls += 1
        return self.items


# ── LocalTTS.available / describe ────────────────────────────────────────────


class TestAvailability:
    def test_darwin_available(self) -> None:
        assert LocalTTS(platform="darwin", which=_which({"say": "say"})).available is True

    def test_darwin_missing_binary(self) -> None:
        assert LocalTTS(platform="darwin", which=_which({})).available is False

    def test_win32_available(self) -> None:
        assert LocalTTS(platform="win32", which=_which({"powershell": "ps"})).available is True

    def test_linux_espeak_ng(self) -> None:
        assert LocalTTS(platform="linux", which=_which({"espeak-ng": "e"})).available is True

    def test_linux_falls_back_to_espeak(self) -> None:
        tts = LocalTTS(platform="linux", which=_which({"espeak": "/usr/bin/espeak"}))
        assert tts.available is True

    def test_unknown_platform_unavailable(self) -> None:
        assert LocalTTS(platform="freebsd", which=_which({"say": "say"})).available is False

    def test_describe_labels(self) -> None:
        assert LocalTTS(platform="darwin", which=_which({"say": "s"})).describe() == "macOS say"
        assert (
            "PowerShell" in LocalTTS(platform="win32", which=_which({"powershell": "p"})).describe()
        )
        assert (
            "espeak"
            in LocalTTS(
                platform="linux", which=_which({"espeak-ng": "/usr/bin/espeak-ng"})
            ).describe()
        )


# ── LocalTTS.say ─────────────────────────────────────────────────────────────


class TestSay:
    async def test_darwin_uses_preferred_ru_voice(self) -> None:
        spawn = _RecordingSpawn()
        tts = LocalTTS(
            platform="darwin",
            which=_which({"say": "/usr/bin/say"}),
            spawn=spawn,
            list_voices=_Voices([("Katya", "ru_RU"), ("Milena", "ru_RU"), ("Alex", "en_US")]),
        )
        assert await tts.say("Айсблок!") is True
        assert spawn.calls == [["/usr/bin/say", "-v", "Milena", "Айсблок!"]]

    async def test_darwin_any_ru_when_no_preferred(self) -> None:
        spawn = _RecordingSpawn()
        tts = LocalTTS(
            platform="darwin",
            which=_which({"say": "say"}),
            spawn=spawn,
            list_voices=_Voices([("Alyona", "ru_RU"), ("Alex", "en_US")]),
        )
        await tts.say("x")
        assert spawn.calls == [["say", "-v", "Alyona", "x"]]

    async def test_darwin_no_ru_voice_plain_say(self) -> None:
        spawn = _RecordingSpawn()
        tts = LocalTTS(
            platform="darwin",
            which=_which({"say": "say"}),
            spawn=spawn,
            list_voices=_Voices([("Alex", "en_US")]),
        )
        await tts.say("x")
        assert spawn.calls == [["say", "x"]]  # mac_voice=None → без -v

    async def test_darwin_voice_probe_cached(self) -> None:
        spawn = _RecordingSpawn()
        voices = _Voices([("Milena", "ru_RU")])
        tts = LocalTTS(
            platform="darwin", which=_which({"say": "say"}), spawn=spawn, list_voices=voices
        )
        await tts.say("раз")
        await tts.say("два")
        assert voices.calls == 1  # проба голосов — один раз

    async def test_darwin_probe_failure_optimistic_milena(self) -> None:
        spawn = _RecordingSpawn()

        async def _boom() -> list[tuple[str, str]]:
            raise OSError("say -v ? упал")

        tts = LocalTTS(
            platform="darwin", which=_which({"say": "say"}), spawn=spawn, list_voices=_boom
        )
        await tts.say("x")
        assert spawn.calls == [["say", "-v", "Milena", "x"]]

    async def test_win32_speaks_via_powershell(self) -> None:
        spawn = _RecordingSpawn()
        tts = LocalTTS(platform="win32", which=_which({"powershell": "C:/ps.exe"}), spawn=spawn)
        assert await tts.say("Тринкет!") is True
        assert spawn.calls[0][0] == "C:/ps.exe"
        assert "Тринкет!" in spawn.calls[0][-1]

    async def test_linux_speaks_via_espeak(self) -> None:
        spawn = _RecordingSpawn()
        tts = LocalTTS(
            platform="linux", which=_which({"espeak-ng": "/usr/bin/espeak-ng"}), spawn=spawn
        )
        await tts.say("Арена")
        assert spawn.calls == [["/usr/bin/espeak-ng", "Арена"]]

    async def test_unavailable_platform_noop(self) -> None:
        spawn = _RecordingSpawn()
        tts = LocalTTS(platform="freebsd", which=_which({}), spawn=spawn)
        assert await tts.say("x") is False
        assert spawn.calls == []  # ничего не запускали

    async def test_missing_binary_noop(self) -> None:
        spawn = _RecordingSpawn()
        tts = LocalTTS(platform="darwin", which=_which({}), spawn=spawn)
        assert await tts.say("x") is False
        assert spawn.calls == []

    async def test_empty_text_noop(self) -> None:
        spawn = _RecordingSpawn()
        tts = LocalTTS(platform="linux", which=_which({"espeak-ng": "e"}), spawn=spawn)
        assert await tts.say("   ") is False
        assert spawn.calls == []

    async def test_nonzero_exit_returns_false(self) -> None:
        spawn = _RecordingSpawn(code=1)
        tts = LocalTTS(platform="linux", which=_which({"espeak-ng": "e"}), spawn=spawn)
        assert await tts.say("x") is False
        assert spawn.calls == [["e", "x"]]  # спавн был, но код != 0

    async def test_spawn_exception_never_raises(self) -> None:
        spawn = _RecordingSpawn(raises=True)
        tts = LocalTTS(platform="linux", which=_which({"espeak-ng": "e"}), spawn=spawn)
        assert await tts.say("x") is False  # исключение проглочено
