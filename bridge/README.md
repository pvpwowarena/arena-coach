# Arena Coach Bridge

Локальный демон — читает WoW chat-log и отправляет события на backend.
Работает на том же компьютере, что и WoW-клиент.

---

## Установка для игроков (Windows, без Python)

### 1. Скачать `arena-bridge.exe`

Скачать последний `arena-bridge.exe` из [GitHub Releases](https://github.com/pvpwowarena/arena-coach/releases).
Положить в удобную папку, например `C:\ArenaCoach\`.

### 2. Создать `bridge.env` рядом с `.exe`

Скопировать [`bridge.env.example`](bridge.env.example) → `bridge.env` и заполнить:

```ini
WOW_INSTALL_PATH=C:\Program Files (x86)\World of Warcraft\_classic_era_
BACKEND_URL=https://coach.example.com
BRIDGE_BEARER_TOKEN=вставить-токен-от-администратора
BRIDGE_PLAYER_NAME=ИмяПерсонажа
```

> Токен и URL выдаёт администратор командой `/access add` в Discord.

### 3. Проверить конфигурацию

```bat
arena-bridge.exe --check-config
```

Ожидаемый вывод:
```
=== Arena Bridge — конфигурация ===
  Config file : C:\ArenaCoach\bridge.env
  WoW path    : C:\Program Files (x86)\World of Warcraft\_classic_era_
  Logs dir    : C:\Program Files (x86)\World of Warcraft\_classic_era_\Logs
  Backend URL : https://coach.example.com
  Player      : ИмяПерсонажа
  Token       : ***
  Poll        : 0.5s

✓ Конфигурация корректна
```

### 4. Запустить перед игрой

```bat
arena-bridge.exe
```

Оставить окно открытым. Логи идут в консоль. Завершение — Ctrl+C.

---

## Установка для разработчиков (Python 3.10+)

```bash
# Из папки arena-coach/bridge/
pip install -e .

# Создать bridge.env и запустить:
arena-bridge --env-file bridge.env --check-config
arena-bridge --env-file bridge.env
```

### Флаги CLI

| Флаг | Описание |
|------|----------|
| `--env-file PATH` | Путь к .env файлу (default: `bridge.env` рядом с `.exe`) |
| `--wow-path PATH` | Путь к WoW (переопределяет `WOW_INSTALL_PATH`) |
| `--backend-url URL` | URL backend'а (переопределяет `BACKEND_URL`) |
| `--token TOKEN` | Bearer-токен (переопределяет `BRIDGE_BEARER_TOKEN`) |
| `--player-name NAME` | Имя персонажа (переопределяет `BRIDGE_PLAYER_NAME`) |
| `--poll-interval SEC` | Интервал polling, сек (default: 0.5) |
| `--log-level LEVEL` | DEBUG / INFO / WARNING / ERROR (default: INFO) |
| `--check-config` | Проверить конфиг и выйти (без запуска демона) |

### Порядок приоритетов настроек

1. Аргументы CLI (`--token`, `--wow-path`, ...)
2. Переменные среды системы (`$BRIDGE_BEARER_TOKEN`, ...)
3. `--env-file` / авто-детект `bridge.env` рядом с `.exe`

---

## Сборка .exe (для разработчиков)

```bash
cd bridge/
pip install pyinstaller
pyinstaller arena-bridge.spec --clean --noconfirm
# Результат: dist/arena-bridge.exe
```

GitHub Actions собирает `.exe` автоматически при push тега `v*`.
Workflow: [`.github/workflows/build-bridge-exe.yml`](../.github/workflows/build-bridge-exe.yml)

---

## Архитектура

| Модуль | Роль |
|--------|------|
| `chat_tail.py` | Polling `Logs/Chat-*.txt`, yield строк `[AC|…]` |
| `normalizer.py` | Raw string → `CanonicalEnvelope`, `SessionState` |
| `ws_client.py` | HTTP POST `/v1/events` на backend, bearer-auth |
| `env_loader.py` | Минимальный dotenv-парсер (без зависимостей) |
| `__main__.py` | CLI entry point, asyncio-loop, signal handling |

## ToS / безопасность

Bridge — **read-only**: только чтение файлов клиента (`Logs/Chat-*.txt`).
Никакой модификации игрового состояния, никакого чтения памяти процесса, никаких автоматических действий за игрока.
Подробнее: [`ADR-0003`](../docs/decisions/0003-chatframe-realtime-channel.md).
