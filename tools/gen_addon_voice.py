#!/usr/bin/env python3
"""Генератор голосовых клипов аддона — `addon/ArenaCoach/sfx/*.ogg` (Phase 4.19).

Зачем клипы, если голос уже есть. Замер 30.07 (память: log-buffer-48kb): клиент
сбрасывает combat-лог на диск блоками ~48КБ, то есть события доезжают до моста
пачками с опозданием 13-28с. Ни очередь, ни быстрый бэкенд этого не меняют — данных
нет на диске. Значит любой голос, идущий через мост, структурно опаздывает.

Аддон видит то же самое БЕЗ лога — напрямую из `COMBAT_LOG_EVENT_UNFILTERED`, в тот
же кадр. Ему не хватало только звука: TTS в клиенте нет. Решение — заранее нарезанные
клипы, которые аддон проигрывает через `PlaySoundFile`. Сети в цепочке нет вообще.

Фразы держим в бюджете Phase 4.17: полезное в ПЕРВОМ слове, 2-4 слога.

Синтез: **RHVoice, голос `elena`** (Phase 4.19.1). Первые клипы были на espeak-ng —
разборчиво, но «робот», и на фоне боя короткая фраза терялась. RHVoice даёт
нормальный русский голос; поверх него ffmpeg-обработка, чтобы клип пробивался через
звук арены: срез низа (там взрывы и музыка), компрессия и нормализация к единой
громкости — иначе «Кик хил!» звучит тише, чем «Тринкета нет!», и тише самого боя.

espeak-ng остаётся ФОЛБЭКОМ, а не выбором: в CI-образе есть он, а RHVoice нет, и
генератор не должен падать там, где клипы всё равно не коммитятся.

Требования: `RHVoice-test` (или `espeak-ng`) и `ffmpeg`. Клипы коммитятся в репо —
генератор нужен только при изменении фраз.

    python tools/gen_addon_voice.py                  # перегенерировать (RHVoice)
    python tools/gen_addon_voice.py --engine espeak  # заведомо фолбэком
    python tools/gen_addon_voice.py --check          # проверить наличие файлов
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "addon" / "ArenaCoach" / "sfx"
MANIFEST = OUT / "openers.json"

#: ключ клипа → фраза. Ключ совпадает с именем файла (`kick` → `kick.ogg`)
#: и с ключом в `Voice.lua`.
PHRASES: dict[str, str] = {
    # ── in-fight, решается аддоном мгновенно ────────────────────────────
    "kick": "Кик хил!",
    "cc": "Сбей каст!",
    "trinket": "Тринкет!",
    "vanish": "Ваниш!",
    "immune": "Иммун!",
    "notrinket": "Тринкета нет!",
    # ── на воротах: килл-таргет. Винительный падеж — «бей кого». ────────
    "target_priest": "Бей жреца!",
    "target_mage": "Бей мага!",
    "target_warlock": "Бей лока!",
    "target_druid": "Бей друида!",
    "target_shaman": "Бей шамана!",
    "target_hunter": "Бей ханта!",
    "target_rogue": "Бей рогу!",
    "target_warrior": "Бей вара!",
    "target_paladin": "Бей палу!",
}

#: RHVoice: русский голос. `elena` — самый разборчивый из бесплатных на коротких
#: командах (проверено на «Кик хил!»: у `aleksandr` первый слог смазывается).
RHVOICE_PROFILE = "elena"

#: Скорость — НЕ одна на все клипы, а по классу срочности. Замеры (RHVoice elena,
#: «Кик хил!»): r60 → 1.03с речи, r75 → 0.81с, r90 → 0.71с, r95 → 0.48с. Окно на
#: кик равно длительности каста (Flash Heal 1.5с), поэтому алерту важна скорость, а
#: не красота. На длинной фразе наоборот: 16 слогов при r60 → 5.7с (ровно 2.8
#: слога/сек — те самые, на которых построен бюджет Phase 4.17), при r90 фраза
#: превращается в скороговорку и разбирается хуже, чем молчание.
#:
#: То есть класс срочности задаёт и потолок длины (тесты), и скорость синтеза.
RHVOICE_RATE_BY_CLASS: dict[str, str] = {
    "cast": "95",  # «Кик хил!», «Сбей каст!» — внутрь чужого каста
    "state": "85",  # «Тринкет!», «Иммун!» — окно на добив, счёт на полсекунды
    "target": "80",  # «Бей жреца!» — ворота, но это первая полезная фраза матча
    "opener": "65",  # тактический колаут: 8-10с ворот, нужна разборчивость
}

#: ключ клипа → класс срочности. Префикс `op_` (колауты на воротах) — `opener`.
_CLASS_OF_KEY: dict[str, str] = {
    "kick": "cast",
    "cc": "cast",
    "trinket": "state",
    "vanish": "state",
    "immune": "state",
    "notrinket": "state",
}


def clip_class(key: str) -> str:
    if key.startswith("op_"):
        return "opener"
    if key.startswith("target_"):
        return "target"
    return _CLASS_OF_KEY.get(key, "target")


def _duration(path: Path) -> float:
    """Длительность клипа в секундах. Печатается рядом с размером: бюджет речи —
    это секунды, а не килобайты, и глазами он должен быть виден сразу."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        check=True,
        capture_output=True,
    )
    try:
        return float(out.stdout.decode().strip())
    except ValueError:
        return 0.0


#: espeak-ng — фолбэк для CI.
ESPEAK_VOICE = "ru"
ESPEAK_SPEED = "150"  # слов/мин; быстрее — теряется разборчивость коротких фраз

#: Обработка под звук арены. Порядок важен:
#:  highpass — убрать низ, где в игре взрывы и музыка (речь там не живёт);
#:  compand  — поднять тихие согласные: «кик» проглатывался на фоне боя;
#:  loudnorm — привести ВСЕ клипы к одной громкости (I=-14 LUFS), иначе игрок
#:             крутит громкость под самый тихий клип и глохнет от самого громкого.
#:  silenceremove — снять тишину по краям. У сырых клипов её до 0.23с в хвосте и
#:             до 0.08с в начале; начальная тишина — это буквально задержка сигнала.
FFMPEG_FILTER = (
    "highpass=f=120,"
    "compand=attacks=0:points=-70/-70|-30/-15|-20/-10|0/-4,"
    "loudnorm=I=-14:TP=-1.5:LRA=7,"
    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02"
    ":stop_periods=-1:stop_threshold=-45dB:stop_silence=0.08"
)


def _need(tool: str, hint: str) -> None:
    if shutil.which(tool) is None:
        print(f"нужен {tool} ({hint})", file=sys.stderr)
        raise SystemExit(2)


def _pick_engine(requested: str) -> str:
    """'auto' → RHVoice, если он есть; иначе espeak-ng с явным предупреждением."""
    if requested != "auto":
        return requested
    if shutil.which("RHVoice-test"):
        return "rhvoice"
    print(
        "⚠️  RHVoice-test не найден — клипы будут на espeak-ng (робот). "
        "Ставится: apt-get install -y rhvoice rhvoice-russian",
        file=sys.stderr,
    )
    return "espeak"


def _synth(engine: str, phrase: str, wav: Path, key: str = "") -> None:
    if engine == "rhvoice":
        rate = RHVOICE_RATE_BY_CLASS[clip_class(key)]
        # RHVoice-test читает текст со stdin и пишет один wav.
        subprocess.run(
            ["RHVoice-test", "-p", RHVOICE_PROFILE, "-r", rate, "-o", str(wav)],
            input=phrase.encode("utf-8"),
            check=True,
            capture_output=True,
        )
        return
    subprocess.run(
        ["espeak-ng", "-v", ESPEAK_VOICE, "-s", ESPEAK_SPEED, "-w", str(wav), phrase],
        check=True,
        capture_output=True,
    )


def _opener_phrases() -> dict[str, str]:
    """Клипы тактических колаутов — из манифеста `sfx/openers.json`.

    Источник истины один: манифест генерит `tools/gen_addon_openers.py` из KB, а
    здесь мы только синтезируем.

    Берём `text`, а НЕ `say`. Поле `say` — это результат `Pronouncer`, а словарь
    произношения (`kb/glossary/voice_pronunciation.json`) писался под macOS Milena:
    он ставит ударения символом U+0301 и разворачивает «лос» в «эл-о-эс». Для другого
    движка это не улучшение, а порча: RHVoice получал «Бёрн — в эл-о-э́с» вместо
    «в лос», то есть буквенное произношение и лишние слоги там, где сленг читался бы
    как слово. Если RHVoice где-то и правда коверкает слово — заводим ОТДЕЛЬНУЮ
    карту под этот движок, а не переиспользуем чужую.
    """
    if not MANIFEST.exists():
        return {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    clips = data.get("clips", {})
    return {
        row["clip"]: row["text"]
        for row in clips.values()
        if row.get("clip")
    }


def generate(engine: str = "auto", what: str = "all") -> int:
    engine = _pick_engine(engine)
    if engine == "rhvoice":
        _need("RHVoice-test", "apt-get install -y rhvoice rhvoice-russian")
    else:
        _need("espeak-ng", "apt-get install -y espeak-ng")
    _need("ffmpeg", "apt-get install -y ffmpeg")
    OUT.mkdir(parents=True, exist_ok=True)
    todo: dict[str, str] = {}
    if what in ("all", "base"):
        todo.update(PHRASES)
    if what in ("all", "openers"):
        openers = _opener_phrases()
        if not openers and what == "openers":
            print("нет sfx/openers.json — сперва tools/gen_addon_openers.py", file=sys.stderr)
            return 2
        todo.update(openers)
    total = 0
    with tempfile.TemporaryDirectory() as tmp:
        for key, phrase in todo.items():
            wav = Path(tmp) / f"{key}.wav"
            ogg = OUT / f"{key}.ogg"
            _synth(engine, phrase, wav, key)
            # 22050/моно — то, что клиент читает без пересэмплирования.
            subprocess.run(
                [
                    "ffmpeg", "-loglevel", "error", "-y", "-i", str(wav),
                    "-af", FFMPEG_FILTER,
                    "-c:a", "libvorbis", "-ar", "22050", "-ac", "1", "-q:a", "3",
                    str(ogg),
                ],
                check=True,
                capture_output=True,
            )
            total += ogg.stat().st_size
            print(
                f"  {key + '.ogg':22s} {_duration(ogg):4.2f}с "
                f"{ogg.stat().st_size:6d} байт  [{clip_class(key)}]  «{phrase}»"
            )
    print(
        f"{len(todo)} клипов ({engine}), суммарно {total / 1024:.0f} КБ "
        f"→ {OUT.relative_to(REPO)}"
    )
    return 0


def check() -> int:
    expected = {**PHRASES, **_opener_phrases()}
    missing = [k for k in expected if not (OUT / f"{k}.ogg").exists()]
    if missing:
        print(
            f"нет {len(missing)} клипов: {', '.join(sorted(missing)[:5])}"
            + (" …" if len(missing) > 5 else ""),
            file=sys.stderr,
        )
        return 1
    #: Осиротевшие клипы — тоже дефект: они уезжают в зип аддона мёртвым весом,
    #: а после правки текста именно они звучат старой формулировкой.
    orphans = [
        p.stem for p in OUT.glob("*.ogg") if p.stem not in expected
    ]
    if orphans:
        print(
            f"лишние клипы (нет в таблицах): {', '.join(sorted(orphans)[:5])}",
            file=sys.stderr,
        )
        return 1
    print(f"все {len(expected)} клипов на месте, лишних нет")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="только проверить наличие файлов")
    ap.add_argument(
        "--engine",
        choices=("auto", "rhvoice", "espeak"),
        default="auto",
        help="движок синтеза; auto = RHVoice, если установлен",
    )
    ap.add_argument(
        "--only",
        choices=("all", "base", "openers"),
        default="all",
        help="что синтезировать: базовые фразы, колауты на воротах или всё",
    )
    args = ap.parse_args()
    return check() if args.check else generate(args.engine, args.only)


if __name__ == "__main__":
    raise SystemExit(main())
