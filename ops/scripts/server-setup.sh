#!/usr/bin/env bash
# =============================================================================
# Arena Coach — полная настройка VPS с нуля
# Ubuntu 22.04 LTS · pvpwowarena.surprise4you.dev · /opt/arena-coach
#
# Запуск (от root или через sudo):
#   bash ops/scripts/server-setup.sh
#
# Скрипт IDEMPOTENT — безопасно запускать повторно.
# =============================================================================
set -euo pipefail

DOMAIN="pvpwowarena.surprise4you.dev"
REPO_DIR="/opt/arena-coach"
DATA_DIR="/var/lib/arena-coach"
CONF_DIR="/etc/arena-coach"
NGINX_HTML_DIR="/var/www/arena-coach"
SERVICE_USER="arenacoach"
PYTHON="python3.11"
REPO_URL="https://github.com/pvpwowarena/arena-coach.git"

GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"
info()  { echo -e "${GREEN}==>${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ── Проверка root ─────────────────────────────────────────────────────────────
[[ "$EUID" -eq 0 ]] || error "Запускай от root: sudo bash server-setup.sh"

# ── 1. Пакеты ────────────────────────────────────────────────────────────────
info "Устанавливаю пакеты..."
apt-get update -qq
apt-get install -y --no-install-recommends \
    nginx \
    certbot \
    python3-certbot-nginx \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    git \
    curl \
    ufw \
    logrotate

# ── 2. Firewall ───────────────────────────────────────────────────────────────
info "Настраиваю UFW..."
# НЕ делаем reset — сохраняем существующие правила (Webmin и др.)
ufw default deny incoming  2>/dev/null || true
ufw default allow outgoing 2>/dev/null || true
ufw allow ssh              # 22/tcp
ufw allow http             # 80/tcp (ACME challenge + redirect)
ufw allow https            # 443/tcp
ufw allow 10000/tcp        # Webmin
# FastAPI слушает только на 127.0.0.1 — снаружи НЕ открываем 8000
ufw --force enable
ufw status verbose

# ── 3. Системный пользователь ────────────────────────────────────────────────
info "Создаю пользователя $SERVICE_USER..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --shell /usr/sbin/nologin --create-home \
            --home-dir "/home/$SERVICE_USER" "$SERVICE_USER"
    info "Пользователь $SERVICE_USER создан"
else
    warn "Пользователь $SERVICE_USER уже существует — пропускаю"
fi

# ── 4. Директории ────────────────────────────────────────────────────────────
info "Создаю директории..."
mkdir -p "$REPO_DIR" "$DATA_DIR" "$CONF_DIR" "$NGINX_HTML_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$REPO_DIR" "$DATA_DIR"
chown -R root:root "$CONF_DIR"
chmod 750 "$CONF_DIR"   # env-файлы с секретами читает только root и группа

# ── 5. Клонирование репозитория ──────────────────────────────────────────────
info "Клонирую/обновляю репозиторий..."
if [[ -d "$REPO_DIR/.git" ]]; then
    warn "Репозиторий уже клонирован. Делаю git pull..."
    sudo -u "$SERVICE_USER" git -C "$REPO_DIR" pull --ff-only
else
    sudo -u "$SERVICE_USER" git clone "$REPO_URL" "$REPO_DIR"
fi

# ── 6. Python venv ───────────────────────────────────────────────────────────
info "Создаю virtualenv..."
VENV="$REPO_DIR/.venv"
if [[ ! -d "$VENV" ]]; then
    sudo -u "$SERVICE_USER" "$PYTHON" -m venv "$VENV"
fi
sudo -u "$SERVICE_USER" "$VENV/bin/pip" install --upgrade pip --quiet
sudo -u "$SERVICE_USER" "$VENV/bin/pip" install -e "$REPO_DIR/backend" --quiet
info "Python зависимости установлены"

# ── 7. База данных (первый запуск Alembic) ───────────────────────────────────
info "Применяю DB миграции (если нужны)..."
# Нужен DATABASE_URL из env-файла — делаем только если файл уже есть
if [[ -f "$CONF_DIR/api.env" ]]; then
    sudo -u "$SERVICE_USER" env "$(grep -v '^#' "$CONF_DIR/api.env" | xargs)" \
        "$VENV/bin/python" -m arena_coach db upgrade || warn "alembic уже на head или api.env не полный"
else
    warn "$CONF_DIR/api.env не найден — пропускаю миграции. Создай файл и запусти: sudo -u $SERVICE_USER $VENV/bin/python -m arena_coach db upgrade"
fi

# ── 8. Env-файлы (шаблоны, если не существуют) ───────────────────────────────
info "Проверяю env-файлы..."
if [[ ! -f "$CONF_DIR/api.env" ]]; then
    cat > "$CONF_DIR/api.env" <<'EOF'
# Arena Coach API — заполни все значения, затем раскомментируй строки
# sudo systemctl restart arena-coach-api arena-coach-bot  ← применить

DISCORD_BOT_TOKEN=REPLACE_ME
DISCORD_GUILD_ID=REPLACE_ME
ARENA_COACH_OWNER_DISCORD_IDS=REPLACE_ME
ANTHROPIC_API_KEY=REPLACE_ME
ARENA_COACH_FERNET_KEY=REPLACE_ME
BRIDGE_BEARER_TOKEN=REPLACE_ME
DATABASE_URL=sqlite+aiosqlite:////var/lib/arena-coach/coach.db
KB_PATH=/opt/arena-coach/kb
EOF
    chmod 640 "$CONF_DIR/api.env"
    warn "СОЗДАН $CONF_DIR/api.env — заполни значения!"
else
    warn "$CONF_DIR/api.env уже существует — не перезаписываю"
fi

if [[ ! -f "$CONF_DIR/bot.env" ]]; then
    # Бот использует те же переменные — симлинк или дубль
    ln -sf "$CONF_DIR/api.env" "$CONF_DIR/bot.env"
    info "Создан симлинк $CONF_DIR/bot.env → api.env"
fi

# ── 9. Nginx ─────────────────────────────────────────────────────────────────
info "Настраиваю Nginx..."

# Копируем конфиг сайта
cp "$REPO_DIR/ops/nginx/$DOMAIN.conf" "/etc/nginx/sites-available/$DOMAIN"
ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"

# Удаляем default если он включён
if [[ -L /etc/nginx/sites-enabled/default ]]; then
    rm /etc/nginx/sites-enabled/default
    info "Отключён default nginx site"
fi

# Копируем статику /download
cp "$REPO_DIR/ops/nginx/html/download.html" "$NGINX_HTML_DIR/download.html"
chown -R www-data:www-data "$NGINX_HTML_DIR"
chmod 755 "$NGINX_HTML_DIR"

# Проверяем конфиг
nginx -t || error "Nginx конфиг невалиден! Проверь $REPO_DIR/ops/nginx/$DOMAIN.conf"
systemctl enable nginx
systemctl restart nginx
info "Nginx запущен"

# ── 10. Certbot (Let's Encrypt) ──────────────────────────────────────────────
info "Получаю TLS-сертификат через Certbot..."
CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
if [[ -f "$CERT_PATH" ]]; then
    warn "Сертификат уже существует — пропускаю certbot (обновление: certbot renew)"
else
    certbot --nginx \
        --non-interactive \
        --agree-tos \
        --email "admin@surprise4you.dev" \
        --domains "$DOMAIN" \
        --redirect
    info "Сертификат получен!"
fi

# Автообновление уже настроено certbot через systemd timer — проверяем:
systemctl is-active certbot.timer &>/dev/null \
    && info "certbot.timer активен — автообновление работает" \
    || warn "certbot.timer неактивен. Запусти: sudo systemctl enable --now certbot.timer"

# ── 11. Systemd сервисы ───────────────────────────────────────────────────────
info "Устанавливаю systemd юниты..."
cp "$REPO_DIR/ops/systemd/arena-coach-api.service" /etc/systemd/system/
cp "$REPO_DIR/ops/systemd/arena-coach-bot.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable arena-coach-api arena-coach-bot
info "Сервисы зарегистрированы (НЕ запущены — сначала заполни $CONF_DIR/api.env)"

# ── 12. Итоговый статус ───────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Arena Coach VPS — setup завершён!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Домен:     https://$DOMAIN"
echo "  Download:  https://$DOMAIN/download"
echo "  Данные:    $DATA_DIR"
echo "  Конфиг:    $CONF_DIR/api.env"
echo "  Лог:       journalctl -u arena-coach-api -f"
echo ""

if grep -q "REPLACE_ME" "$CONF_DIR/api.env" 2>/dev/null; then
    echo -e "${YELLOW}  НУЖНО СДЕЛАТЬ:${NC}"
    echo "  1. Заполнить $CONF_DIR/api.env (токены Discord, Anthropic, Fernet)"
    echo "  2. Запустить:"
    echo "     sudo -u $SERVICE_USER $VENV/bin/python -m arena_coach db upgrade"
    echo "     sudo systemctl start arena-coach-api arena-coach-bot"
    echo "     sudo systemctl status arena-coach-api arena-coach-bot"
    echo ""
fi

echo -e "${GREEN}  Проверка nginx:${NC}"
echo "     curl -I https://$DOMAIN/health"
echo ""
