# Private Server Deploy

Цель: закрытая проверочная версия для астролога. Пользователь регистрируется, но доступ получает только после `is_active=true` в Django admin.

## Что уже заложено

- `PRIVATE_APP_REQUIRE_AUTH=true` закрывает calculation/report/source/place API.
- Новые регистрации создаются с `is_active=false`.
- В Django admin есть action `Approve selected users`.
- Фронт при `NEXT_PUBLIC_PRIVATE_APP_REQUIRE_AUTH=true` показывает только вход/регистрацию до одобрения.
- Сохранённая карта при загрузке заполняет поля рождения/места/настроек и заново строит report.

## Server files

- `docker-compose.prod.yml` - Postgres, Redis, Django gunicorn, Next production. The AI `codex-worker` is opt-in via the `ai` Docker profile.
- `deploy/prod.env.example` - шаблон production `.env`.
- `deploy/nginx-jyotish-agent.conf` - reverse proxy на `127.0.0.1:18100` и `127.0.0.1:13130`.

## Minimal deploy flow

```bash
mkdir -p /srv/jyotish-agent
cd /srv/jyotish-agent
git clone https://github.com/haridas98/jyotish-agent.git app
cd app
cp deploy/prod.env.example .env
nano .env
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

Calculator-only launch is the default. To enable queued AI reports later, set `CODEX_GENERATION_QUEUE_ENABLED=true` in `.env` and start Docker with `--profile ai`.

Then install nginx config, replace `jyotish.example.com`, enable site, and issue TLS if a domain is used.

## Current production host flow

Current host `31.76.79.2` is an archive-based systemd deploy, not a git checkout and not Docker.

- App path: `/srv/jyotish-agent/app`.
- Frontend: `jyotish-agent-frontend.service`, Next on `0.0.0.0:13130`.
- Backend: `jyotish-agent-backend.service`, gunicorn on `0.0.0.0:18100`.
- Current systemd host uses local PostgreSQL (`DATABASE_URL=postgres://...@127.0.0.1:5432/jyotish_agent`). SQLite is only an emergency rollback source and must not be used with `DJANGO_DEBUG=false` unless `ALLOW_PRODUCTION_SQLITE=true` is set deliberately.
- Gunicorn stays at `--workers 1` on the small server. Calculator-only launch should keep `CODEX_GENERATION_QUEUE_ENABLED=false`; heavy Codex analysis later must run through `CODEX_GENERATION_QUEUE_ENABLED=true` and `jyotish-agent-codex-worker.service`.
- Runtime files to preserve: `.env`, `.tmp/`, `.private_corpus/`, `ephe/`, `backend/.venv/`, `frontend/node_modules/`.
- PostgreSQL backups: `/srv/jyotish-agent/backups/postgres/latest.dump`; script: `deploy/backup-postgres.sh`.
- Deploy marker: `/srv/jyotish-agent/app/.deploy-commit`.
- Verification: `GET http://31.76.79.2:18100/api/health` must return the deployed `deploy_commit`.

Deploy from local workspace:

```powershell
git status --short --branch
git rev-parse --short HEAD
$env:JYOTISH_PUBLIC_HEALTH_URL = "http://31.76.79.2:18100/api/health"
$env:JYOTISH_PUBLIC_FRONTEND_URL = "http://31.76.79.2:13130/"
.\deploy\deploy-systemd-archive.ps1 `
  -HostName 31.76.79.2 `
  -UserName root `
  -HostKey "SHA256:..."
```

The helper creates `git archive`, uploads it with `pscp.exe`, unpacks it on the server, updates `.deploy-commit`,
runs Django checks/migrations, builds frontend, restarts systemd services, verifies local health, and checks public URLs
when `JYOTISH_PUBLIC_HEALTH_URL` / `JYOTISH_PUBLIC_FRONTEND_URL` or matching params are set. Backend health must return
the current archive commit; a stale backend/proxy now fails deploy. Pass `-BackendOnly` for backend-only changes. Set
`JYOTISH_DEPLOY_PASSWORD` locally or use Pageant/SSH keys; do not commit secrets.

Local calculator launch smoke before a deploy checkpoint:

```powershell
# Terminal 1
cd C:\Projects\jyotish-agent
$env:DJANGO_DEBUG = "true"
$env:PRIVATE_APP_REQUIRE_AUTH = "false"
backend\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:18110 --noreload

# Terminal 2
cd C:\Projects\jyotish-agent\frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:18110"
npm.cmd run dev -- --hostname 127.0.0.1 --port 3131

# Terminal 3
cd C:\Projects\jyotish-agent\frontend
$env:JYOTISH_API_BASE_URL = "http://127.0.0.1:18110"
$env:JYOTISH_FRONTEND_BASE_URL = "http://127.0.0.1:3131"
npm.cmd run smoke:calculator-launch
```

The smoke registers a temporary user, creates a Sterlitamak chart, runs saved-profile calculation, checks D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D30/D60 workbench payloads, and verifies `/charts/new` plus `/charts/<id>` respond.

Manual equivalent:

```powershell
git archive --format=tar --output=.tmp\deploy-jyotish-agent-<commit>.tar HEAD
pscp .tmp\deploy-jyotish-agent-<commit>.tar root@31.76.79.2:/tmp/deploy-jyotish-agent-<commit>.tar
```

Then on the server:

```bash
cd /srv/jyotish-agent/app
cp .deploy-commit .deploy-commit.prev 2>/dev/null || true
tar -xf /tmp/deploy-jyotish-agent-<commit>.tar -C /srv/jyotish-agent/app
echo <commit> > .deploy-commit
cd backend
./.venv/bin/python manage.py check
./.venv/bin/python manage.py migrate --noinput
cd ../frontend
npm run build
systemctl restart jyotish-agent-backend.service jyotish-agent-frontend.service
curl -fsS http://127.0.0.1:18100/api/health
curl -I --max-time 15 http://127.0.0.1:13130/
```

For backend-only changes, skip the frontend build and restart only `jyotish-agent-backend.service`.

## PostgreSQL backups

Manual backup on the systemd host:

```bash
cd /srv/jyotish-agent/app
bash deploy/backup-postgres.sh
pg_restore --list /srv/jyotish-agent/backups/postgres/latest.dump | head
```

Install a daily timer:

```bash
cat >/etc/systemd/system/jyotish-agent-postgres-backup.service <<'EOF'
[Unit]
Description=Jyotish Agent PostgreSQL backup

[Service]
Type=oneshot
WorkingDirectory=/srv/jyotish-agent/app
ExecStart=/usr/bin/bash /srv/jyotish-agent/app/deploy/backup-postgres.sh
EOF

cat >/etc/systemd/system/jyotish-agent-postgres-backup.timer <<'EOF'
[Unit]
Description=Run Jyotish Agent PostgreSQL backup daily

[Timer]
OnCalendar=*-*-* 03:20:00
RandomizedDelaySec=20m
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now jyotish-agent-postgres-backup.timer
systemctl start jyotish-agent-postgres-backup.service
systemctl status jyotish-agent-postgres-backup.service --no-pager
```

Restore drill target should be a fresh database, never the live database:

```bash
createdb -O jyotish_agent jyotish_agent_restore_check
pg_restore --dbname=jyotish_agent_restore_check --no-owner --no-acl /srv/jyotish-agent/backups/postgres/latest.dump
dropdb jyotish_agent_restore_check
```

## Required production env decisions

- `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD` must be real secrets.
- Production must use PostgreSQL. `DATABASE_URL=sqlite://...` is rejected when `DJANGO_DEBUG=false`; `ALLOW_PRODUCTION_SQLITE=true` exists only for emergency rollback.
- `DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL` must match the actual domain.
- `VL_DATABASE_URL` must point to the Prabhupada/VL database if source search must work on the server.
- Swiss/JPL ephemeris files must be placed in `./ephe` if JPL mode is needed.
- `CODEX_ANALYSIS_PROVIDER=codex_cli` is the active private-build AI path. Qwen, DeepSeek and Nemotron helper services are not part of the runtime anymore.
- For calculator-only launch, keep `CODEX_GENERATION_QUEUE_ENABLED=false`. When AI reports are explicitly enabled later, set it to `true` so web requests enqueue AI work instead of running Codex CLI inline.
- The backend host/container must be able to run `codex exec` under the same user as gunicorn if AI reports are enabled.

## Codex CLI analysis

By default AI analysis path calls:

```bash
codex exec --cd <project-root> --sandbox read-only ...
```

So if `CODEX_ANALYSIS_PROVIDER=codex_cli`, the production backend host/container must have an installed and authenticated `codex` binary. If Docker is used and Codex CLI is not installed inside the backend image, Codex analysis will fail even when ordinary calculations work.

Practical options:

- Run backend on the host venv where `codex` is installed and authenticated.
- Or extend the backend image and mount a server-only Codex auth directory.
Do not configure Qwen, DeepSeek, Nemotron or OpenAI as runtime AI providers for this private build.

## Approval flow

1. User registers from the site.
2. Admin opens `/admin/`, users list.
3. Select pending users.
4. Run `Approve selected users`.
5. User logs in again and can use calculations, saved charts, compatibility and source-backed analysis.
