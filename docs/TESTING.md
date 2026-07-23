# Тест-гайд — живой прогон Phase 3/4 (аддон + bridge)

> Подготовлено 2026-06-05. Платформы: **Mac Apple Silicon (arm64)** и **Windows**.
> Цель: проверить весь канал `аддон → bridge → backend → Discord DM` на живом клиенте.

## TL;DR — что уже сделано в этой итерации

- **Аддон починен** (блокер снят): теперь при логине автоматически включается запись чата
  в файл (`LoggingChat(true)`), без которой bridge не видел бы ни одного события.
  Добавлена команда `/ac test` — самопроверка канала без захода на арену. Версия → `0.1.1`.
- **v0.3.0 (2026-07-11):** Phase 4.1 починена (реальные KB-советы на открытии ворот,
  таргетированные под твой класс + килл-таргет), in-fight подсказки на ключевые дефы
  врага с троттлингом, аддон `0.2.0` шлёт союзников и форс-флашит chat-лог,
  bridge автодетектит `WoWChatLog.txt`/`Chat-*.txt`. См. Windows-ревью внизу.
- **Серверная цепочка проверена без игры** скриптом `tools/e2e_dryrun.py` — парсинг событий,
  Bearer-auth, whitelist, фильтрация, формирование Discord DM. Всё проходит.
- **Этот гайд** — пошаговый живой тест.

**Главная мысль:** бóльшую часть можно проверить уже сейчас, не дожидаясь 70 уровня.
Combat-log и whisper-to-self работают на любом уровне, а `/ac test` гоняет полный канал
до Discord DM прямо в открытом мире.

---

## Шаг 0 — Предусловия (один раз)

### 0.1 Backend жив

```bash
curl -s https://pvpwowarena.surprise4you.dev/health
# → {"status":"ok","uptime_s":...}
```

### 0.2 Добавить себя в whitelist — КРИТИЧНО

Без записи в whitelist backend ответит `no_player` и DM не придёт. В Discord (на сервере с ботом):

```
/access add user:@ТвойDiscord role:player character:ИмяРоги realm:Реалм
```

- **Даже владелец обязан** добавить себя: pipeline ищет игрока по имени персонажа
  (`find_by_character`), а статус owner даёт только право управлять вайтлистом, но не
  создаёт запись с персонажем.
- `character` — **точно как в игре**, регистр важен (`Шэдоустэп` ≠ `шэдоустэп`).
- `role:player` — нужен именно для real-time подсказок (`viewer` их не получает).

### 0.3 Узнать Bearer-токен для bridge

Токен **общий** для всех bridge — это `BRIDGE_BEARER_TOKEN` из `/etc/arena-coach/api.env`
на VPS (Webmin terminal):

```bash
sudo grep BRIDGE_BEARER_TOKEN /etc/arena-coach/api.env
```

> ⚠️ В `bridge.env.example` написано «выдаётся при /access add» — это неточность.
> `/access add` токен **не** выдаёт; бери его из `api.env`.

---

## Шаг 1 — Аддон (на любом уровне, ДО арены)

### 1.1 Установить

Скопировать папку `addon/ArenaCoach/` целиком в:

| ОС | Путь |
|---|---|
| **Mac** | `/Applications/World of Warcraft/_anniversary_/Interface/AddOns/ArenaCoach/` |
| **Windows** | `C:\Program Files (x86)\World of Warcraft\_anniversary_\Interface\AddOns\ArenaCoach\` |

Должен существовать файл `…/Interface/AddOns/ArenaCoach/ArenaCoach.toc`.

### 1.2 Включить

На экране выбора персонажа → **AddOns** → поставить галочку у ArenaCoach.
Если списка нет — снять галочку «Скрыть несовместимые» / «Load out of date AddOns».

### 1.3 Проверить загрузку

В игре:

```
/ac status      → должно показать "ArenaCoach v0.2.0"
/ac log         → "Запись чата: ВКЛ (Logs/WoWChatLog.txt или Chat-*.txt пишется)"
```

### 1.4 Самопроверка канала — `/ac test`

```
/ac test
```

Аддон принудительно включит логирование и отправит тестовые `ARENA_START` + `TRINKET`.
Проверь файл (открой в текстовом редакторе):

| ОС | Файл |
|---|---|
| **Mac** | `/Applications/World of Warcraft/_anniversary_/Logs/WoWChatLog.txt` (или `Chat-ГГГГ-ММ-ДД.txt`) |
| **Windows** | `C:\Program Files (x86)\World of Warcraft\_anniversary_\Logs\WoWChatLog.txt` (или `Chat-ГГГГ-ММ-ДД.txt`) |

В нём должны появиться строки вида (разделитель `#` — аддон 0.2.1+):

```
To ИмяРоги: [AC#ARENA_START#2v2#ROGUE/HUMAN,MAGE/UNDEAD]
To ИмяРоги: [AC#TRINKET#TestEnemy#42292#pvp_trinket]
```

> ⚠️ Аддон **0.2.0 в Anniversary-клиенте не отправлял события вовсе**: формат
> использовал разделитель `|`, а современный движок запрещает сырой `|` в
> SendChatMessage (тихая Lua-ошибка — счётчик «Событий» рос, файл оставался
> пустым; найдено на первом живом тесте 2026-07-23). С 0.2.1 разделитель `#`;
> bridge ≥ 0.3.2 принимает оба варианта.

✅ Если строки есть — канал аддон → файл работает.
❌ Если файла/строк нет — см. Troubleshooting (whisper-to-self).

---

## Шаг 2 — Bridge (сразу после шага 1, ДО арены)

Bridge запускается на **той же машине**, где WoW.
Качать со страницы `/download` или из GitHub Releases (тег **`v0.4.0`+**).

> 🔁 **Phase 4.2 (v0.4.0): канал переехал на COMBAT-лог.** Живой тест показал,
> что chat-лог в Anniversary-клиенте не сбрасывается на диск до полного выхода
> из игры — realtime через него невозможен. Bridge 0.4.0 читает
> `Logs/WoWCombatLog-*.txt` (флашится прямо в бою) и сам собирает события:
> ворота — по ауре Arena Preparation, классы — по кастам, тринкеты/дефы — по
> spell id. Аддон 0.2.2 включает запись боя при логине автоматически.
> Следствия: `/ac test` больше НЕ является проверкой realtime-канала (он гоняет
> легаси chat-путь) — **E2E-проверка теперь = скирмиш**; в `bridge.env`
> рекомендуется добавить `BRIDGE_OUR_COMP=<ваш состав>` (напр. `rogue+mage`) —
> мгновенный фильтр матчапов, пока классы союзников не раскрылись кастами.

> ⚠️ **Бинари релиза v0.3.0 битые** (и .exe, и macOS): падают на старте с
> `ImportError: attempted relative import with no known parent package`
> (`[PYI-…] Failed to execute script '__main__'`). Починено в v0.3.1
> (entry-обёртка PyInstaller). Если видишь эту ошибку — просто скачай v0.3.1+.

### 2.1 Mac (Apple Silicon arm64)

```bash
# 1. Распаковать
tar -xzf arena-bridge-macos-arm64.tar.gz
cd arena-bridge-macos-arm64

# 2. Снять карантин Gatekeeper (бинарь не подписан)
xattr -d com.apple.quarantine ./arena-bridge

# 3. Создать bridge.env рядом с бинарём (см. ниже)

# 4. Проверить конфиг
./arena-bridge --check-config

# 5. Запустить
./arena-bridge
```

`bridge.env` для Mac:

```ini
WOW_INSTALL_PATH=/Applications/World of Warcraft/_anniversary_
BACKEND_URL=https://pvpwowarena.surprise4you.dev
BRIDGE_BEARER_TOKEN=<токен из api.env>
BRIDGE_PLAYER_NAME=ИмяРоги
# Опционально: fallback-состав, если играешь со старым аддоном (<0.2.0)
# BRIDGE_OUR_COMP=rogue+mage
```

### 2.2 Windows

```bat
:: 1. Положить arena-bridge.exe и bridge.env в одну папку
:: 2. Проверить конфиг
arena-bridge.exe --check-config
:: 3. Запустить
arena-bridge.exe
```

`bridge.env` для Windows:

```ini
WOW_INSTALL_PATH=C:\Program Files (x86)\World of Warcraft\_anniversary_
BACKEND_URL=https://pvpwowarena.surprise4you.dev
BRIDGE_BEARER_TOKEN=<токен из api.env>
BRIDGE_PLAYER_NAME=ИмяРоги
```

> Путь по умолчанию в `bridge.env.example` указывает на `_classic_era_` — поправь на
> `_anniversary_` (или на ту папку, где реально стоит твой Anniversary-клиент).

При старте bridge должен написать `Backend доступен: …` и `Arena Bridge запущен`.

---

## Шаг 3 — Полный E2E без арены (главная проверка перед 70)

1. Аддон загружен, bridge запущен.
2. В игре: `/ac test`
3. В консоли bridge → строка `Event received: ARENA_START` (и `TRINKET`).
4. В Discord → приходит DM «🏟 Арена началась | 2v2 | Враги: …».

✅ Прошли все 4 пункта — **весь канал работает**, можно спокойно качаться до арены.

---

## Шаг 4 — На арене (когда дойдёшь до 70)

1. Зайти в 2v2/3v3 (скирмиш тоже годится для проверки телеметрии).
2. На старте боя (ворота открылись) → DM с **матчапом из KB**: опенер под твой класс,
   килл-таргет, сложность. Если матчапа в KB нет — generic DM с составом врагов.
   Враг вышел из стелса позже → придёт уточнённый DM.
3. Когда враг жмёт PvP-тринкет → DM с post-trinket планом из KB.
   Ключевые дефы врага (evasion, ice block, bubble…) → короткий DM (не чаще раза в ~20с).
4. После боя: `/ac sessions` — счётчик сессий вырос; `/ac status` — детали.

---

## Известные изъяны (не блокируют тест канала, но знай о них)

1. ✅ ~~Real-time KB-совет не доставляется~~ — **починено в v0.3.0 (Phase 4.1)**:
   pipeline матчит по базовым классам врагов + нашему составу. Спек с ворот не виден,
   поэтому враги `WARRIOR+PALADIN` могут дать несколько кандидатов (holy/ret) — DM покажет
   основной + предупреждение с альтернативами.
2. **LLM-подсказка отключена** (`ANTHROPIC_API_KEY` — заглушка). DM содержит сырой
   KB-текст секции, а не сжатый Haiku-совет, пока не вставишь реальный ключ. Таргетинг
   «советуй именно моему классу» полноценно работает только с LLM.
3. **realm не проверяется** в pipeline — матч только по `character`. Системные инструкции
   требуют матчить оба (`discord_id ↔ character/realm`) — TODO.
4. **Имя chat-лога не подтверждено живым тестом.** Стандартно `/chatlog` пишет в
   `Logs/WoWChatLog.txt`; изначальное допущение ADR-0003 (`Chat-YYYY-MM-DD.txt`) на живом
   клиенте не проверялось. Bridge v0.3.0 следит за **обоими** именами и сам выбирает
   растущий файл — на живом тесте просто посмотри в лог bridge, какой файл он открыл.
5. **Буферизация chat-лога.** Клиент пишет лог с задержкой (буфер). Аддон v0.2.0 после
   критических событий дёргает `LoggingChat(false→true)` — это сбрасывает буфер на диск
   (side-effect: системные сообщения о вкл/выкл логирования в чате). Если раздражает или
   не помогает — `/ac flush off` и расскажи, какая реальная задержка получилась.

---

## Windows-ревью bridge-кода (2026-07-11, v0.3.0)

Пройдено перед первым живым тестом; сборка `.exe` — только GitHub Actions (windows-latest).

**Проверено — ОК:**

| Аспект | Вердикт |
|---|---|
| Пути | Везде `pathlib.Path`; `C:/...` и `C:\...` в `bridge.env` оба работают, пробелы в `Program Files (x86)` не ломают парсер |
| Чтение лога параллельно с WoW | `open("r")` — shared read, WoW не держит эксклюзивную блокировку |
| Кодировка лога | WoW пишет UTF-8 (включая кириллицу имён); `errors="replace"` страхует |
| Ctrl+C / завершение | `add_signal_handler` недоступен на Windows → подавлен, `KeyboardInterrupt` ловится |
| asyncio | ProactorEventLoop (дефолт Win) совместим с httpx и файловым polling |
| PyInstaller onefile | hiddenimports для httpx-транспортов и `asyncio.windows_events` в spec; certifi подтягивается хуком; UPX только win32 |
| `_exe_dir()` / автодетект `bridge.env` | `sys.frozen`/`sys.executable` корректны для onefile |
| Эмодзи в консоли | Python ≥3.6 на Windows использует UTF-8 console IO — не падает |

**Найдено и починено в v0.3.0:**

1. **Имя chat-файла** — bridge смотрел только `Chat-YYYY-MM-DD.txt`; стандартное имя
   `WoWChatLog.txt`. → Автодетект обоих кандидатов, выбор растущего файла.
2. **BOM в bridge.env** — Блокнот сохраняет UTF-8 с BOM → первый ключ
   (`﻿WOW_INSTALL_PATH`) молча не подхватывался. → `encoding="utf-8-sig"`.
3. **Оборванные строки** — WoW флашит буфер кусками, строка `[AC|...` могла быть прочитана
   наполовину и потеряна. → Rewind до полного `\n`.
4. **Усечение/пересоздание лога** (игрок удалил файл) — bridge зависал на старом offset.
   → Детект `size < offset`, чтение с начала.

---

## Troubleshooting

| Симптом | Причина / решение |
|---|---|
| `ImportError: attempted relative import…` + `[PYI-…] Failed to execute script '__main__'` | Битый бинарь из релиза v0.3.0 — скачай v0.3.1+. |
| `No module named 'email'` в Modules-строке check-config | Тот же битый релиз v0.3.0 (излишние excludes в spec) — скачай v0.3.1+. |
| В `Logs/` нет `[AC#…]`, а `/ac status` показывает растущий счётчик «Событий» | Аддон 0.2.0 со старым `\|`-форматом — SendChatMessage молча падает в Anniversary-клиенте. Обнови аддон до 0.2.1 (релиз v0.3.2+). |
| В `Logs/` нет `[AC#…]` | `/ac log` для принудительного включения. Если всё равно пусто — проверь whisper-to-self вручную: `/w СвоёИмя тест` (фиолетовая строка = работает). |
| bridge: `no_player` | Не добавлен в whitelist или `character` не совпадает с `BRIDGE_PLAYER_NAME` (регистр!). |
| bridge: `401 Unauthorized` | Неверный `BRIDGE_BEARER_TOKEN` — сверь с `api.env` на VPS. |
| bridge: `Forbidden 403` | Игрок есть, но роль не `player`. |
| DM не приходит, статус `sent`/`no_matchup` | В настройках Discord-сервера запрещены DM от участников. Включи «Разрешить личные сообщения». |
| Mac: «приложение нельзя открыть» | Не снят карантин: `xattr -d com.apple.quarantine ./arena-bridge`. |
| bridge: `WoW-путь не найден` | Проверь `WOW_INSTALL_PATH` — папка должна содержать подпапку `Logs/`. |

---

## Быстрый smoke-тест серверной части (без игры, для разработчика)

```bash
cd arena-coach
pip install -e ./backend -e ./bridge -e ./ingest
python tools/e2e_dryrun.py
```

Прогоняет синтетический Chat-лог через всю цепочку и печатает результаты по каждому событию.
