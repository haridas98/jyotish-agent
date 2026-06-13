#!/usr/bin/env bash
set -euo pipefail

APP_PATH="${JYOTISH_APP_PATH:-/srv/jyotish-agent/app}"
ENV_FILE="${JYOTISH_ENV_FILE:-$APP_PATH/.env}"
BACKUP_DIR="${JYOTISH_BACKUP_DIR:-/srv/jyotish-agent/backups/postgres}"
RETENTION_DAYS="${JYOTISH_BACKUP_RETENTION_DAYS:-14}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

DATABASE_URL="$(grep -m 1 '^DATABASE_URL=' "$ENV_FILE" | cut -d= -f2- | sed -e 's/^["'\'']//' -e 's/["'\'']$//')"

if [[ -z "$DATABASE_URL" || "$DATABASE_URL" != postgres://* ]]; then
  echo "DATABASE_URL must be postgres://... for production backup." >&2
  exit 1
fi

eval "$(
  DATABASE_URL="$DATABASE_URL" python3 -c 'import os, shlex; from urllib.parse import urlparse, unquote; url = urlparse(os.environ["DATABASE_URL"]); print("export PGHOST=" + shlex.quote(url.hostname or "127.0.0.1")); print("export PGPORT=" + shlex.quote(str(url.port or 5432))); print("export PGDATABASE=" + shlex.quote((url.path or "/").lstrip("/"))); print("export PGUSER=" + shlex.quote(unquote(url.username or ""))); print("export PGPASSWORD=" + shlex.quote(unquote(url.password or "")))'
)"

if [[ -z "${PGDATABASE:-}" || -z "${PGUSER:-}" ]]; then
  echo "Cannot parse PGDATABASE/PGUSER from DATABASE_URL." >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="$BACKUP_DIR/${PGDATABASE}-${timestamp}.dump"
tmp_target="$target.partial"
latest_link="$BACKUP_DIR/latest.dump"

pg_dump --format=custom --compress=9 --no-owner --no-acl --file="$tmp_target"
pg_restore --list "$tmp_target" >/dev/null
mv "$tmp_target" "$target"
ln -sfn "$target" "$latest_link"
chmod 600 "$target"

find "$BACKUP_DIR" -type f -name "${PGDATABASE}-*.dump" -mtime +"$RETENTION_DAYS" -delete

echo "PostgreSQL backup complete: $target"
