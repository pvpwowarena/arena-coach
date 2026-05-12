# Arena Coach Addon

WoW Lua-аддон для клиента **Burning Crusade Classic Anniversary 2.4.3**. **Phase 3 skeleton** — реальная боевая логика будет добавлена позже.

## Что это будет (Phase 3)

Read-only телеметрия арена-матчей:

- Регистрация `ARENA_OPPONENT_UPDATE`, `COMBAT_LOG_EVENT_UNFILTERED`, `UNIT_AURA`.
- Трекинг: enemy spec/race, использование трикета (spell 42292/7744), evasion/cloak/cold-blood/vanish/prep, fear/blind/sap/cyclone, defensive CDs (ice block, divine shield, lichborne).
- Запись событий в `ArenaCoachDB` (SavedVariables).
- Chat-frame mirror как realtime канал (см. [ADR-0003](../docs/decisions/0003-chatframe-realtime-channel.md)).
- Минимальный UI-фрейм со статусом — без interactive-элементов во время боя.

## Установка (когда будет реализовано)

```
World of Warcraft/Interface/AddOns/ArenaCoach/
├── ArenaCoach.toc
├── ArenaCoach.lua
├── core/...
└── ui/...
```

## Включение chat-log (обязательно для realtime канала)

В клиенте:

```
/console chatLogging 1
/reload
```

Файл `World of Warcraft/Logs/Chat-YYYY-MM-DD.txt` начнёт писаться с задержкой ~0.5-2 сек.

## Жёсткие ограничения (read-only)

- Никакой автоматизации действий игрока.
- Никакого input injection.
- Никакого чтения памяти процесса.
- Только regsiter-event + read-only API + write в свой UI-фрейм + write в SavedVariables.

См. [`docs/decisions/0003-chatframe-realtime-channel.md`](../docs/decisions/0003-chatframe-realtime-channel.md) для деталей.
