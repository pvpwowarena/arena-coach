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

Требования: `espeak-ng` и `ffmpeg`. Клипы коммитятся в репо — генератор нужен только
при изменении фраз.

    python tools/gen_addon_voice.py           # перегенерировать
    python tools/gen_addon_voice.py --check   # проверить, что все файлы на месте
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "addon" / "ArenaCoach" / "sfx"

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

VOICE = "ru"
SPEED = "150"  # слов/мин; быстрее — теряется разборчивость коротких фраз


def _need(tool: str) -> None:
    if shutil.which(tool) is None:
        print(f"нужен {tool} (apt-get install -y espeak-ng ffmpeg)", file=sys.stderr)
        raise SystemExit(2)


def generate() -> int:
    _need("espeak-ng")
    _need("ffmpeg")
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    with tempfile.TemporaryDirectory() as tmp:
        for key, phrase in PHRASES.items():
            wav = Path(tmp) / f"{key}.wav"
            ogg = OUT / f"{key}.ogg"
            subprocess.run(
                ["espeak-ng", "-v", VOICE, "-s", SPEED, "-w", str(wav), phrase],
                check=True,
                capture_output=True,
            )
            # 22050/моно — то, что клиент читает без пересэмплирования.
            subprocess.run(
                [
                    "ffmpeg", "-loglevel", "error", "-y", "-i", str(wav),
                    "-c:a", "libvorbis", "-ar", "22050", "-ac", "1", "-q:a", "3",
                    str(ogg),
                ],
                check=True,
                capture_output=True,
            )
            total += ogg.stat().st_size
            print(f"  {key + '.ogg':22s} {ogg.stat().st_size:6d} байт  «{phrase}»")
    print(f"{len(PHRASES)} клипов, суммарно {total / 1024:.0f} КБ → {OUT.relative_to(REPO)}")
    return 0


def check() -> int:
    missing = [k for k in PHRASES if not (OUT / f"{k}.ogg").exists()]
    if missing:
        print(f"нет клипов: {', '.join(sorted(missing))}", file=sys.stderr)
        return 1
    print(f"все {len(PHRASES)} клипов на месте")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="только проверить наличие файлов")
    args = ap.parse_args()
    return check() if args.check else generate()


if __name__ == "__main__":
    raise SystemExit(main())
