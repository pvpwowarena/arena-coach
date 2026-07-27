"""Мастер первого запуска (Phase 4.8): настройка моста без блокнота и терминала.

Проблема UX: неопытному игроку раньше нужно было руками создать bridge.env
(токен, ник, путь к WoW) в блокноте — стена для нетехнических тестеров.

Решение: если рядом с .exe нет bridge.env и конфиг не задан переменными
окружения, мост при интерактивном запуске (двойной клик по .exe открывает
консоль) сам задаёт 3 вопроса по-русски, сам находит WoW и сам пишет
bridge.env. Дальше обычный запуск в том же процессе — игрок ничего не
настраивает и не открывает терминал.

Повторная настройка: `arena-bridge --setup` (или удалить bridge.env).

Модуль чистый: ввод/вывод и список кандидатов WoW инъектируются — тесты
гоняют мастер без TTY и без реального диска C:.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from pathlib import Path

# Публичный сервер проекта — дефолт для игроков. Продвинутые могут
# отредактировать bridge.env руками (BACKEND_URL).
DEFAULT_BACKEND_URL = "https://pvpwowarena.surprise4you.dev"

# Короткие коды составов (как в kb/compositions.json) → канонический слаг
# для $BRIDGE_OUR_COMP. Дублируем маленьким словарём: мост не тащит KB.
COMP_SHORTCUTS: dict[str, str] = {
    "rm": "rogue+mage",
    "rp": "rogue+priest",
    "rl": "rogue+warlock",
    "rd": "rogue+resto-druid",
    "rmp": "rogue+mage+priest",
    "rrd": "rogue+rogue+resto-druid",
    "rmd": "rogue+mage+resto-druid",
    "rld": "rogue+warlock+resto-druid",
}

# Типичные корни установки WoW. Сканируем сам корень и его подпапки первого
# уровня (_classic_era_ и подобные лаунчер-раскладки находятся сами).
_WINDOWS_ROOTS = [
    "C:/Program Files (x86)/World of Warcraft",
    "C:/Program Files/World of Warcraft",
    "C:/World of Warcraft",
    "C:/Games/World of Warcraft",
    "D:/World of Warcraft",
    "D:/Games/World of Warcraft",
    "E:/World of Warcraft",
    "E:/Games/World of Warcraft",
]
_MACOS_ROOTS = [
    "/Applications/World of Warcraft",
    "~/Applications/World of Warcraft",
]


def default_wow_roots(platform: str | None = None) -> list[Path]:
    """Список корней для автопоиска WoW (по платформе)."""
    plat = platform if platform is not None else sys.platform
    roots = _WINDOWS_ROOTS if plat.startswith("win") else _MACOS_ROOTS
    return [Path(r).expanduser() for r in roots]


def looks_like_wow_dir(path: Path) -> bool:
    """Папка похожа на установку WoW: есть Logs/ или Interface/."""
    try:
        return path.is_dir() and ((path / "Logs").is_dir() or (path / "Interface").is_dir())
    except OSError:
        return False


def find_wow_installs(roots: Sequence[Path]) -> list[Path]:
    """Найти кандидатов установки WoW: сами корни + их подпапки 1-го уровня."""
    found: list[Path] = []
    for root in roots:
        candidates = [root]
        try:
            if root.is_dir():
                candidates.extend(sorted(p for p in root.iterdir() if p.is_dir()))
        except OSError:
            continue
        for cand in candidates:
            if looks_like_wow_dir(cand) and cand not in found:
                found.append(cand)
    return found


def _clean(raw: str) -> str:
    """Срезать пробелы и обрамляющие кавычки (копипаст из проводника/чата)."""
    s = raw.strip()
    while len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1].strip()
    return s


def normalize_comp(raw: str) -> str | None:
    """Ввод состава → канонический слаг или None (автоопределение).

    Принимает короткий код (rl), полный слаг (rogue+warlock) или пусто.
    Непонятный ввод трактуем как «авто» — состав уточнится из игры.
    """
    s = _clean(raw).lower()
    if not s:
        return None
    if s in COMP_SHORTCUTS:
        return COMP_SHORTCUTS[s]
    if "+" in s:
        parts = [p.strip() for p in s.split("+")]
        if all(p and all(ch.isalpha() or ch == "-" for ch in p) for p in parts):
            return "+".join(parts)
    return None


def render_env(
    token: str,
    player_name: str,
    wow_path: Path,
    our_comp: str | None,
    backend_url: str = DEFAULT_BACKEND_URL,
) -> str:
    """Собрать содержимое bridge.env (совместимо с env_loader)."""
    lines = [
        "# Arena Coach — настройки моста (создано мастером первого запуска).",
        "# Изменить: правь этот файл или удали его и запусти мост заново.",
        f"BACKEND_URL={backend_url}",
        f"BRIDGE_BEARER_TOKEN={token}",
        f"BRIDGE_PLAYER_NAME={player_name}",
        f'WOW_INSTALL_PATH="{wow_path}"',
    ]
    if our_comp:
        lines.append(f"BRIDGE_OUR_COMP={our_comp}")
    else:
        lines.append("# BRIDGE_OUR_COMP=rogue+mage   # необязательно: состав придёт из игры")
    return "\n".join(lines) + "\n"


def is_interactive() -> bool:
    """Есть живая консоль (двойной клик по .exe / запуск из терминала)."""
    try:
        return bool(
            sys.stdin is not None
            and sys.stdout is not None
            and sys.stdin.isatty()
            and sys.stdout.isatty()
        )
    except (AttributeError, ValueError):
        return False


def should_run_wizard(
    env_file: Path | None,
    environ: dict[str, str],
    interactive: bool,
    *,
    force: bool = False,
    check_config: bool = False,
) -> bool:
    """Решение «запускать ли мастер» (чистая функция — под тесты).

    Мастер уместен только когда конфига нет вообще и есть кому отвечать:
    - bridge.env не найден и токен не задан через окружение;
    - консоль интерактивна (не CI-пайп, не systemd);
    - это не --check-config (CI-smoke обязан остаться неинтерактивным).
    --setup форсит мастер, но тоже только в интерактивной консоли.
    """
    if check_config:
        return False
    if not interactive:
        return False
    if force:
        return True
    return env_file is None and not environ.get("BRIDGE_BEARER_TOKEN", "").strip()


def _ask_required(
    prompt: str,
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
    error: str,
) -> str:
    while True:
        value = _clean(input_fn(prompt))
        if value:
            return value
        print_fn(error)


def _ask_wow_path(
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
    roots: Sequence[Path],
) -> Path:
    """Автопоиск WoW; при неудаче — попросить путь (сколько потребуется раз)."""
    found = find_wow_installs(roots)
    if len(found) == 1:
        print_fn(f"   Нашёл WoW сам: {found[0]}")
        return found[0]
    if found:
        print_fn("   Нашёл несколько установок WoW:")
        for i, p in enumerate(found, start=1):
            print_fn(f"     {i}) {p}")
        while True:
            raw = _clean(input_fn(f"   Номер нужной (1-{len(found)}): "))
            if raw.isdigit() and 1 <= int(raw) <= len(found):
                return found[int(raw) - 1]
            print_fn("   Введи номер из списка.")
    print_fn("   Не нашёл WoW в стандартных папках.")
    print_fn("   Открой папку с игрой, скопируй путь из адресной строки и вставь сюда.")
    while True:
        raw = _clean(input_fn("   Путь к папке WoW (где лежит Wow.exe): "))
        if raw:
            path = Path(raw).expanduser()
            if looks_like_wow_dir(path):
                return path
            print_fn("   В этой папке нет Logs/ и Interface/ — похоже, путь не тот. Попробуй ещё.")
        else:
            print_fn("   Путь пустой. Скопируй его из проводника и вставь.")


def run_wizard(
    target_dir: Path,
    *,
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
    wow_roots: Sequence[Path] | None = None,
    backend_url: str = DEFAULT_BACKEND_URL,
) -> Path | None:
    """Задать 3 вопроса, найти WoW, записать bridge.env. None = игрок прервал."""
    roots = list(wow_roots) if wow_roots is not None else default_wow_roots()
    out_path = target_dir / "bridge.env"
    try:
        print_fn("")
        print_fn("=== Arena Coach — первый запуск ===")
        print_fn("Настроим за минуту: три вопроса, дальше всё само.")
        print_fn("")
        token = _ask_required(
            "1/3 Код команды (выдал админ в Discord): ",
            input_fn,
            print_fn,
            "   Код пустой. Вставь код, который прислал админ.",
        )
        player = _ask_required(
            "2/3 Ник твоего персонажа в WoW: ",
            input_fn,
            print_fn,
            "   Ник пустой. Введи имя персонажа, за которого играешь.",
        )
        comp_raw = input_fn("3/3 Ваш состав (rm/rp/rl/rd, или Enter — определится сам): ")
        comp = normalize_comp(comp_raw)
        if _clean(comp_raw) and comp is None:
            print_fn("   Не узнал состав — не страшно, определю по игре.")
        print_fn("")
        wow = _ask_wow_path(input_fn, print_fn, roots)
        out_path.write_text(
            render_env(token, player, wow, comp, backend_url=backend_url),
            encoding="utf-8",
        )
        print_fn("")
        print_fn(f"✓ Готово! Настройки сохранены: {out_path}")
        print_fn("  Оставь это окно открытым во время игры — подсказки придут в Discord.")
        print_fn("  Перенастроить: удали bridge.env или запусти с флагом --setup.")
        print_fn("")
        return out_path
    except (KeyboardInterrupt, EOFError):
        print_fn("")
        print_fn("Настройка прервана. Запусти мост ещё раз, когда будешь готов.")
        return None


__all__ = [
    "COMP_SHORTCUTS",
    "DEFAULT_BACKEND_URL",
    "default_wow_roots",
    "find_wow_installs",
    "is_interactive",
    "looks_like_wow_dir",
    "normalize_comp",
    "render_env",
    "run_wizard",
    "should_run_wizard",
]
