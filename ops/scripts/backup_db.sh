#!/usr/bin/env bash
# Nightly SQLite snapshot. Запускать через cron на VPS.
# Phase 2.

set -euo pipefail

DB_PATH=/var/lib/arena-coach/coach.db
BACKUP_DIR=/var/lib/arena-coach/backups
DATE=$(date +%Y-%m-%d)
TARGET="$BACKUP_DIR/coach-$DATE.db"

mkdir -p "$BACKUP_DIR"
sqlite3 "$DB_PATH" ".backup '$TARGET'"
gzip -f "$TARGET"

# Retention: 30 дней (TODO Phase 2: подтвердить retention с владельцем)
find "$BACKUP_DIR" -name 'coach-*.db.gz' -mtime +30 -delete

# TODO(Phase 2): upload в S3-compatible storage (B2/R2/MinIO)
echo "backup $TARGET.gz done"
