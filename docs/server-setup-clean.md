# Чистая установка сервера — пошагово

Эта инструкция для **свежепереустановленного** VPS на Ubuntu 22.04 / 24.04 LTS. Подходит для Hetzner Cloud Console, Senko Digital, Vultr, DigitalOcean, любого облачного админ-панеля.

> **Перед началом:** убедись что важные данные с сервера сохранены. Reinstall стирает всё на диске.

---

## Шаг A — Переустановка через админ-панель

Точные названия пунктов меню зависят от провайдера, но логика везде одинаковая.

### Senko Digital (русский UI)

1. Авторизация → выбери сервер из списка.
2. Кнопка **«Переустановить»** или **«Reinstall»** (обычно в шапке карточки или в боковом меню).
3. Выбор образа:
   - **Ubuntu 22.04 LTS** (рекомендую — у нас в `pyproject.toml` `requires-python >= 3.10`, на 22.04 Python 3.10 системный).
   - Ubuntu 24.04 LTS тоже OK (там Python 3.12 системный — наш код совместим).
4. Способ авторизации:
   - **SSH-ключ** (если в панели можно сразу прицепить твой публичный ключ — лучший вариант, сразу логинишься без пароля).
   - Или **пароль** — панель сгенерит и покажет один раз, либо пришлёт на email.
5. Подтвердить переустановку. Процесс занимает 2-5 минут.
6. После завершения панель покажет **новый IPv4** (обычно тот же что был) и логин-данные.

### Hetzner Cloud Console (английский UI)

1. Server → выбрать сервер → таб **Rebuild**.
2. Image: Ubuntu 22.04 (или 24.04).
3. SSH key: выбрать существующий из аккаунта (или прикрепить новый через Security → SSH Keys заранее).
4. Rebuild → подтвердить.

### Общая логика для других панелей (Vultr / DO / OVH)

Ищи в меню сервера слово **Rebuild / Reinstall / Reset / Переустановка**. Обычно требует:
- Выбор OS image
- Выбор SSH ключа (рекомендуется) или подтверждение пароля
- Подтверждение что данные будут стёрты

---

## Шаг B — Первое подключение

На Mac'е в терминале:

```bash
# Если в панели прикрепил SSH-ключ
ssh root@<новый-ip>

# Если пароль (его покажет панель)
ssh root@<новый-ip>
# вводишь пароль
```

При первом подключении ssh спросит про fingerprint — отвечай `yes`.

> **Сразу проверь что подключился:** `whoami` должно вывести `root`, `cat /etc/os-release` — Ubuntu 22.04 или 24.04.

---

## Шаг C — SSH-ключ вместо пароля (если ставился пароль)

Если в панели поставил пароль, а не ключ — переключаемся на ключ для безопасности.

**На Mac'е** (отдельный терминал, **не** на сервере):

```bash
# Создать ключ если ещё нет
ls ~/.ssh/id_ed25519.pub  # если есть — пропусти ssh-keygen
ssh-keygen -t ed25519 -C "nameuser202233@gmail.com"
# Жми Enter на все вопросы, passphrase по желанию

# Скопировать публичный ключ на сервер (использует пароль один раз)
ssh-copy-id root@<твой-ip>
```

Проверь — должно зайти **без** пароля:

```bash
ssh root@<твой-ip>
```

**На сервере (под root):** отключи парольный вход:

```bash
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config

# Если есть include-папка с переопределениями (Ubuntu 24.04):
ls /etc/ssh/sshd_config.d/ 2>/dev/null

# Если там есть файлы — проверь что они не включают PasswordAuthentication yes
# например, удалить cloud-init файл если он переопределяет:
# rm /etc/ssh/sshd_config.d/50-cloud-init.conf   # ⚠️ только если уверен

systemctl reload ssh

# Тест в новом терминале на Mac'е (НЕ закрывая текущий ssh!):
ssh root@<твой-ip>
# Должно зайти по ключу. Если упало — старая сессия ещё открыта, можно
# восстановить sshd_config до изменений.
```

---

## Шаг D — Базовые пакеты

```bash
# На сервере под root
apt update
apt install -y python3.10-venv python3-pip git ufw fail2ban htop curl
# 22.04: python3.10 системный
# 24.04: вместо python3.10-venv — python3.12-venv (системный 3.12)

# Опционально: обновление security-патчей
unattended-upgrades --dry-run
# Если ничего критичного — apt upgrade -y делать НЕ нужно сразу,
# подождём пока проект стабилизируется.
```

---

## Шаг E — Swap 512 MB (для 1 GB RAM)

```bash
swapon --show
# Если пусто:

fallocate -l 512M /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Проверка
swapon --show
free -h
# Должно быть: Swap: 511Mi
```

---

## Шаг F — Firewall (UFW)

Чистый сервер — ставим firewall сразу.

```bash
# На сервере под root
ufw default deny incoming
ufw default allow outgoing

# Разрешаем SSH (важно ДО включения!)
ufw allow OpenSSH

# Phase 4 будет нужен HTTPS для WSS — открываем заранее
ufw allow 80/tcp
ufw allow 443/tcp

# Бот сам подключается к Discord — НЕ нужны входящие порты для Discord

ufw --force enable
ufw status verbose
```

Должно показать `Status: active` и три allow-правила.

---

## Шаг G — fail2ban (защита от SSH-перебора)

```bash
systemctl enable --now fail2ban
systemctl status fail2ban --no-pager | head -10
```

С базовым конфигом fail2ban сразу защищает SSH.

---

## Шаг H — Пользователь `arenacoach`

```bash
# Без пароля, без sudo
adduser --disabled-password --gecos "" arenacoach

# Скопировать SSH-ключ root'а для прямого ssh arenacoach@...
mkdir -p /home/arenacoach/.ssh
cp /root/.ssh/authorized_keys /home/arenacoach/.ssh/
chown -R arenacoach:arenacoach /home/arenacoach/.ssh
chmod 700 /home/arenacoach/.ssh
chmod 600 /home/arenacoach/.ssh/authorized_keys

# Директории под проект
mkdir -p /opt/arena-coach /var/lib/arena-coach /etc/arena-coach
chown -R arenacoach:arenacoach /opt/arena-coach /var/lib/arena-coach /etc/arena-coach
chmod 750 /etc/arena-coach   # секреты не для всех

# Тест что ssh-логин под arenacoach работает (из нового терминала на Mac'е)
# ssh arenacoach@<ip>
# whoami → arenacoach
```

---

## Шаг I — Deploy key для GitHub + клонирование репо

```bash
# Переключиться под arenacoach
su - arenacoach
cd /opt/arena-coach

# Сгенерировать deploy key (без passphrase, read-only)
ssh-keygen -t ed25519 -f ~/.ssh/github_deploy -N "" -C "arena-coach-deploy@$(hostname)"

# Вывести публичный ключ — добавляешь его в GitHub
cat ~/.ssh/github_deploy.pub
```

Скопируй вывод (строка `ssh-ed25519 AAAA...`) и:

→ https://github.com/pvpwowarena/arena-coach/settings/keys → **Add deploy key**
- Title: `<hostname>-prod` (например `senko-prod`)
- Key: вставь скопированное
- **Allow write access:** НЕ ставь (read-only достаточно для pull'а)
- **Add key**

Вернись в терминал на сервере (под arenacoach):

```bash
# SSH config для GitHub
cat >> ~/.ssh/config <<'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_deploy
    IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config

# Тест
ssh -T git@github.com
# Ожидаем: "Hi pvpwowarena/arena-coach! You've successfully authenticated..."

# Клонировать (каталог должен быть пуст)
git clone git@github.com:pvpwowarena/arena-coach.git .
ls -la
# Должны быть pyproject.toml, README.md, backend/, kb/, и т.д.
```

---

## Шаг J — Venv + установка проекта

```bash
# Под arenacoach в /opt/arena-coach
# Ubuntu 22.04: python3.10. Ubuntu 24.04: python3.12.
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e backend
pip install -e ingest

# Проверка
python -m arena_coach validate-kb kb/drafts
# Ожидаем: OK: 22 документов прошли валидацию

# Объём venv
du -sh .venv
# 150-250 MB

# Дисковое место
df -h /
```

---

## Шаг K — Конфигурация .env и запуск бота

### K1 — Сгенерировать Fernet-ключ

```bash
# Под arenacoach
source /opt/arena-coach/.venv/bin/activate
cd /opt/arena-coach
python -m arena_coach gen-key
# Вывод: случайная строка вида gAAAAAB...
# Скопируй её — вставишь ниже как ARENA_COACH_FERNET_KEY
```

### K2 — Создать /etc/arena-coach/bot.env

```bash
# Под root (файл с секретами — только root создаёт, arenacoach читает через systemd)
cat > /etc/arena-coach/bot.env <<'EOF'
# ── Discord ──────────────────────────────────────────────────────────
DISCORD_BOT_TOKEN=СЮДА_ВСТАВЬ_ТОКЕН_БОТА
DISCORD_GUILD_ID=СЮДА_ID_ТВОЕГО_СЕРВЕРА

# ── Владелец (твой Discord user ID, получить: Discord → Settings → Advanced → Developer Mode → ПКМ на себе → Copy ID) ──
ARENA_COACH_OWNER_DISCORD_IDS=СЮДА_ТВОЙ_DISCORD_ID

# ── Шифрование whitelist ─────────────────────────────────────────────
ARENA_COACH_FERNET_KEY=СЮДА_КЛЮЧ_ИЗ_gen-key

# ── Пути ────────────────────────────────────────────────────────────
DATABASE_URL=sqlite+aiosqlite:////var/lib/arena-coach/coach.db
AUDIT_LOG_DIR=/var/lib/arena-coach/audit
KB_PATH=/opt/arena-coach/kb
EOF

chmod 600 /etc/arena-coach/bot.env
chown root:arenacoach /etc/arena-coach/bot.env
# Только root и arenacoach могут читать; systemd запускает от arenacoach → OK
```

Проверь что заполнил все 4 обязательных поля (TOKEN, GUILD_ID, OWNER_IDS, FERNET_KEY).

### K3 — Создать директории для БД и audit

```bash
# Под root
mkdir -p /var/lib/arena-coach/audit
chown -R arenacoach:arenacoach /var/lib/arena-coach
chmod 750 /var/lib/arena-coach
```

### K4 — Применить миграцию Alembic (создать таблицы в SQLite)

```bash
# Под arenacoach
source /opt/arena-coach/.venv/bin/activate
cd /opt/arena-coach/backend

# Нужны переменные из bot.env (alembic читает settings → settings читает env)
export $(grep -v '^#' /etc/arena-coach/bot.env | xargs)

alembic upgrade head
# Ожидаем:
# INFO  [alembic.runtime.migration] Running upgrade  -> 0001, create whitelist_entries
```

### K5 — Установить systemd-сервис

```bash
# Под root
cp /opt/arena-coach/ops/systemd/arena-coach-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable arena-coach-bot.service
```

### K6 — Первый запуск (форграунд, для проверки)

```bash
# Под arenacoach — убеждаемся что бот стартует без ошибок
source /opt/arena-coach/.venv/bin/activate
export $(grep -v '^#' /etc/arena-coach/bot.env | xargs)
cd /opt/arena-coach
python -m arena_coach run-bot
```

В логах должно быть:
```
HH:MM:SS INFO     discord.client: logging in using static token
HH:MM:SS INFO     discord.gateway: Shard ID None has connected to Gateway
HH:MM:SS INFO     arena_coach.bot.client: KB loaded: N docs
HH:MM:SS INFO     arena_coach.bot.client: Synced N commands to guild XXXXXXX
HH:MM:SS INFO     discord.client: ArenaCoachBot#XXXX is now ready
```

Если ошибки — смотри секцию Troubleshooting ниже. Останови Ctrl+C.

### K7 — Запустить через systemd

```bash
# Под root
systemctl start arena-coach-bot.service
systemctl status arena-coach-bot.service --no-pager
# State: active (running)

# Логи
journalctl -u arena-coach-bot.service -f --no-pager | head -30
```

### K8 — Проверить в Discord

В твоём Guild набери `/` — должны появиться команды: `/matchup`, `/opener`, `/glossary`, `/list_comps`, `/source`, `/access`, `/coach`.

Проверь что бот тебя знает как owner (bypass whitelist):
```
/list_comps
```
Должен ответить (даже если KB пуста — покажет «KB пуста»).

---

## Шаг L — Acceptance check

```bash
# Под arenacoach в /opt/arena-coach
echo "── OS + Python ──"
cat /etc/os-release | grep PRETTY_NAME
python3 --version

echo "── Disk + Memory ──"
df -h /
free -h
swapon --show

echo "── Firewall ──"
ufw status 2>/dev/null || echo "UFW not available (check as root)"

echo "── User + venv ──"
whoami
ls /opt/arena-coach/ | head -10

echo "── DB + Audit dir ──"
ls -la /var/lib/arena-coach/
ls -la /var/lib/arena-coach/audit/ 2>/dev/null || echo "(audit dir пустой — норма до первого deny)"

echo "── Tests ──"
source /opt/arena-coach/.venv/bin/activate && cd /opt/arena-coach
python -m pytest -q --tb=line 2>&1 | tail -5

echo "── Git ──"
git log --oneline | head -3

echo "── Systemd ──"
systemctl is-active arena-coach-bot.service
```

---

## (Устарело) Шаг K — Pre-Phase 2 acceptance check

> Этот блок актуален только если ты проходишь шаги A-J впервые и ещё не дошёл до шага K выше (Phase 2 deploy). Если бот уже запущен — используй Шаг L вместо этого.

```bash
source /opt/arena-coach/.venv/bin/activate
cd /opt/arena-coach
python -m arena_coach validate-kb kb/drafts
python -m pytest -q --tb=line 2>&1 | tail -5
git log --oneline | head -3
```

---

## Что НЕ делаем в этом setup'е

- **Не ставим nginx / caddy / apache** — Phase 2 бот сам ходит к Discord Gateway, входящий HTTP не нужен. Phase 4 (WSS) поднимем позже, через тот же ufw.
- **Не открываем Webmin/Cockpit/панельку** — управляем через ssh.
- **Не настраиваем docker** — пока не нужен.
- **Не настраиваем backup'ы** — Phase 2 пока без БД. Backup для SQLite добавим в Phase 2.5.

---

## Troubleshooting

### ssh-copy-id ругается «no identities found»
- На Mac'е нужно создать `~/.ssh/id_ed25519` через `ssh-keygen -t ed25519`. После этого `ssh-copy-id` найдёт.

### ssh root@... падает после `PasswordAuthentication no`
- Не закрывай старую сессию пока не проверишь ключ из новой! Если упало — откатись через rescue console провайдера (в админ-панели есть Web Console).

### `apt install python3.10-venv` пишет «unable to locate package»
- На 24.04: нужен `python3.12-venv`, не `python3.10-venv`.
- Если на 22.04 не находит — `apt update` сначала.

### `git clone` падает с «Permission denied (publickey)»
- Проверь что deploy key добавлен в **именно репо** `pvpwowarena/arena-coach`, а не в личные ключи аккаунта.
- Проверь `~/.ssh/config` — у Host github.com должен быть путь к `~/.ssh/github_deploy`, и `IdentitiesOnly yes`.
- `ssh -vT git@github.com` покажет какой ключ пытается использовать.

### `pip install -e backend` падает на cryptography / aiosqlite
- Нужны системные `build-essential` и `libffi-dev`:
  ```
  sudo apt install -y build-essential libffi-dev libssl-dev
  ```
  (если нет sudo — под root, потом обратно под arenacoach).

### `validate-kb` пишет «No module named 'arena_coach'»
- venv не активирован → `source /opt/arena-coach/.venv/bin/activate`
- ИЛИ `pip install -e backend` не отработал → перезапусти.
