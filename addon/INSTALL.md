# ArenaCoach Addon — Инструкция по установке

Аддон работает с **WoW: Burning Crusade Classic Anniversary** (клиент 2.4.3, Interface 20400).

---

## 1. Получить файлы аддона

Файлы находятся в ветке `main` репозитория `pvpwowarena/arena-coach`, папка `addon/ArenaCoach/`.

```
addon/ArenaCoach/
├── ArenaCoach.toc
├── Core.lua
├── Tracker.lua
└── UI.lua
```

Скачай напрямую или клонируй репозиторий:

```bash
git clone git@github.com:pvpwowarena/arena-coach.git
```

---

## 2. Найти папку AddOns в WoW клиенте

Стандартные пути (Windows):

| Лаунчер | Путь |
|---|---|
| Battle.net (TBC Classic Anniversary) | `C:\Program Files (x86)\World of Warcraft\_classic_era_\Interface\AddOns\` |
| Альтернативный клиент | Смотри настройки пути установки |

На **macOS**:
```
/Applications/World of Warcraft/_classic_era_/Interface/AddOns/
```

> **Важно:** папка `_classic_era_` может называться иначе в зависимости от версии лаунчера — главное, что внутри есть `Interface/AddOns/`.

---

## 3. Скопировать аддон

Скопируй папку `ArenaCoach` целиком в `Interface/AddOns/`:

```
Interface/
  AddOns/
    ArenaCoach/          ← вся папка сюда
      ArenaCoach.toc
      Core.lua
      Tracker.lua
      UI.lua
```

**Результат:** `Interface/AddOns/ArenaCoach/ArenaCoach.toc` должен существовать.

---

## 4. Включить аддон в игре

1. Запусти WoW и зайди на любой персонаж.
2. На экране выбора персонажа нажми **«Дополнения»** (кнопка в левом нижнем углу).
3. Убедись, что **ArenaCoach** есть в списке и галочка стоит.
4. Если аддона нет — проверь путь из шага 3.

---

## 5. Проверить работу

После входа в мир введи в чат:

```
/ac status
```

Ожидаемый ответ в чате (синий текст):
```
[ArenaCoach] ArenaCoach v0.1.0
[ArenaCoach] Сессий в DB: 0
[ArenaCoach] Активной сессии нет.
```

Также в правом верхнем углу экрана должна появиться небольшая плашка `[AC] idle`.

### Дополнительные команды

| Команда | Что делает |
|---|---|
| `/ac status` | Версия, количество сессий, активная сессия |
| `/ac sessions` | Сколько сессий в SavedVariables |
| `/ac reset` | Очистить все сохранённые сессии |
| `/ac ui` | Показать/скрыть статус-плашку |

---

## 6. Проверить запись на арене

1. Зайди на арену (2v2 или 3v3).
2. Через ~1–2 секунды после появления в зоне в чате увидишь:
   ```
   [ArenaCoach] Арена началась (2v2) — трекинг активен.
   ```
3. Плашка сменится на зелёный `[AC] 2v2 0 ev`.
4. При использовании врагом трикета:
   ```
   [ArenaCoach] ТРИКЕТ: PlayerName использовал Medallion of the Alliance
   ```
5. После выхода с арены:
   ```
   [ArenaCoach] Арена завершена. Событий записано: 42
   ```
6. Введи `/ac sessions` — счётчик должен увеличиться на 1.

---

## 7. Где хранятся данные

SavedVariables пишутся при `/reload` или выходе из игры:

```
WoW/_classic_era_/WTF/Account/<AccountName>/SavedVariables/ArenaCoachDB.lua
```

Этот файл будет читать **Phase 4 bridge** (Python-демон) для передачи событий в backend.

> SavedVariables.lua **не попадают в git** (прописаны в `.gitignore`).

---

## 8. Обновление аддона

При выходе новой версии:

```bash
cd arena-coach
git pull
# Скопировать addon/ArenaCoach/ в Interface/AddOns/ArenaCoach/ заново
# В игре: /reload
```

---

## Troubleshooting

| Симптом | Решение |
|---|---|
| `/ac` не работает, нет текста в чате | Аддон не включён — см. шаг 4 |
| `Interface\AddOns\ArenaCoach could not be loaded` | Проверь, что `.toc` в правильном месте |
| Нет сообщения при входе на арену | Убедись, что аддон enabled; попробуй `/reload` |
| Плашка `[AC]` закрывает важный UI | Перетащи её мышью (ЛКМ) |
| После `/ac reset` сессий всё равно > 0 | Нужен `/reload` для записи в SV |
