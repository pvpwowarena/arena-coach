# Phase 4.5 — Voice hints в Discord voice channel

**Статус:** planned, после стабильной работы text-hint'ов в Phase 4.
**Why:** в арена-матче читать Discord-embed физически некогда — глаза на цели. Голосовая подсказка («Druid trinket → kidney up») воспринимается без отрыва от боя.

## Принципы

- TTS играет **в Discord voice channel**, где сидит команда. Тестеры всё равно в voice — добавление бота даёт нулевой setup-cost у них.
- Голос звучит для **всех в voice-канале**. Если кто-то не хочет слышать — server-mute бота на своей стороне (стандартная Discord-фича).
- Голос **класс-специфичен**: hint фразируется под класс конкретного триггерящего события. Пример: «Druid trinketed — Rogue, prep your kidney». Если в команде одновременно играют 2 рога — обоих обращением `Rogue` (без имени) пока хватит; в будущем добавим персональное обращение, если попросят.
- Голос **не дублирует** text-hint, а **заменяет** или **сопровождает** (опция per-player через `/coach voice on/off`).

## TTS-движок

Кандидаты:

| Движок | Качество | Цена | Латенси |
|--------|----------|------|---------|
| OpenAI TTS (`tts-1`) | хорошее | ~$0.015 / 1K знаков | 200-500 мс |
| ElevenLabs (Multilingual v2) | отличное | ~$0.30 / 1K знаков | 300-800 мс |
| Edge TTS (через `edge-tts` python) | приемлемое | бесплатно | 100-300 мс |
| Системные (espeak-ng / festival) | плохое для арены | бесплатно | мгновенно |

**Рекомендация:** Edge TTS на старте (бесплатно, нормальный русский голос), потом OpenAI TTS если качество мало — без переписывания pipeline'а, только swap engine.

## Архитектура

```
Phase 4 backend orchestrator
       ↓ hint synthesized (text)
       ↓
       ├─→ Discord embed (existing, Phase 4)
       └─→ VoiceManager (new in Phase 4.5)
              ↓ TTS(text, voice='ru-RU-DmitryNeural') → mp3 bytes
              ↓
           Discord voice-client (discord.py voice + ffmpeg)
              ↓
           Audio stream → voice channel members
```

`VoiceManager`:
- Один singleton на guild.
- Очередь подсказок (если два события подряд — играем по очереди, не overlap).
- Cache: одна и та же фраза не TTS'ится дважды (LRU на 256 фраз).
- Throttling: не больше 1 hint каждые 8 сек, иначе уши пухнут.

## Зависимости

- `discord.py[voice]` (libopus + ffmpeg в системе)
- `edge-tts` или `openai`
- ffmpeg на VPS (`apt install ffmpeg`)

## Per-player settings

Slash-команда `/coach voice <on|off|only>`:
- `on` — text + voice (default)
- `off` — только text
- `only` — только voice, без text-spam

Запись в SQLite `player_settings` таблица.

## Acceptance criteria Phase 4.5

1. Бот успешно входит в указанный voice channel.
2. На trigger-событие (druid trinket) бот произносит hint на русском в течение ≤2 сек после события.
3. Если voice-channel пуст — бот не входит туда (не жжёт ресурсы зря).
4. `/coach voice off` действительно глушит voice для конкретного игрока.
5. Throttling: 3 события за 5 сек → играется 1 первое, остальные дропнуты с лог-entry.

## Risks

- **Discord voice-API нестабилен.** discord.py + voice требует libopus + ffmpeg, на ARM-VPS может быть боль. Митигация: тестируем на dev-VPS перед prod.
- **Latency через WebRTC**. Discord voice ≈ 80-200 мс латенси от send до speaker → суммарный лаг от события «druid trinket» до звука «trinket up» ≈ 1.5-3 сек. Это приемлемо для «готовь kidney», но не для «нажми сейчас».
- **TTS-стоимость растёт линейно с длиной фразы**. Промпт для VoiceManager должен генерить **короткие** hint'ы (≤8 слов), отличные от text-hint'ов. Отдельный prompt-template.
