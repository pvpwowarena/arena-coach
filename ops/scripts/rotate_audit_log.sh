#!/usr/bin/env bash
# Ротация audit-JSONL по месяцам. Запускать через cron 1-го числа.
# Phase 2.

set -euo pipefail

AUDIT_DIR=/var/lib/arena-coach/audit
CURRENT=$(date +%Y-%m)

cd "$AUDIT_DIR"
for f in audit-*.jsonl; do
  [ "$f" = "audit-${CURRENT}.jsonl" ] && continue
  if [ -f "$f" ]; then
    gzip -f "$f"
  fi
done

# Retention (TODO Phase 2: подтвердить retention; по умолчанию 1 год)
find "$AUDIT_DIR" -name 'audit-*.jsonl.gz' -mtime +365 -delete
