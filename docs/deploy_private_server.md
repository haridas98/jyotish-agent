# Private Server Deploy

Цель: закрытая проверочная версия для астролога. Пользователь регистрируется, но доступ получает только после `is_active=true` в Django admin.

## Что уже заложено

- `PRIVATE_APP_REQUIRE_AUTH=true` закрывает calculation/report/source/place API.
- Новые регистрации создаются с `is_active=false`.
- В Django admin есть action `Approve selected users`.
- Фронт при `NEXT_PUBLIC_PRIVATE_APP_REQUIRE_AUTH=true` показывает только вход/регистрацию до одобрения.
- Сохранённая карта при загрузке заполняет поля рождения/места/настроек и заново строит report.

## Server files

- `docker-compose.prod.yml` - Postgres, Redis, Django gunicorn, Next production.
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

Then install nginx config, replace `jyotish.example.com`, enable site, and issue TLS if a domain is used.

## Current production host flow

Current host `31.76.79.2` is an archive-based systemd deploy, not a git checkout and not Docker.

- App path: `/srv/jyotish-agent/app`.
- Frontend: `jyotish-agent-frontend.service`, Next on `0.0.0.0:13130`.
- Backend: `jyotish-agent-backend.service`, gunicorn on `0.0.0.0:18100`.
- Runtime files to preserve: `.env`, `.tmp/`, `.private_corpus/`, `ephe/`, `backend/.venv/`, `frontend/node_modules/`.
- Deploy marker: `/srv/jyotish-agent/app/.deploy-commit`.
- Verification: `GET http://31.76.79.2:18100/api/health` must return `deploy_commit`.

Deploy from local workspace:

```powershell
git status --short --branch
git rev-parse --short HEAD
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

## Required production env decisions

- `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD` must be real secrets.
- `DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL` must match the actual domain.
- `VL_DATABASE_URL` must point to the Prabhupada/VL database if source search must work on the server.
- Swiss/JPL ephemeris files must be placed in `./ephe` if JPL mode is needed.
- For Qwen report generation, run FreeQwenApi and set `QWEN_API_BASE_URL` in the server `.env`, usually `http://127.0.0.1:3264/api`.
- For DeepSeek overview generation, run FreeDeepseekAPI and set `FREE_DEEPSEEK_API_BASE_URL` in the server `.env`, usually `http://127.0.0.1:9655/v1`.
- For Nemotron overview generation, set `NEMOTRON_ANALYSIS_ENABLED=true`, `NEXT_PUBLIC_ENABLE_NEMOTRON=true`, `OPENROUTER_API_KEY`, keep `OPENROUTER_API_BASE_URL=https://openrouter.ai/api/v1`, and set `NEMOTRON_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free`.
- After deploy, run `cd /srv/jyotish-agent/app/backend && ./.venv/bin/python manage.py smoke_free_deepseek` to verify server-side FreeDeepseekAPI access.
- To check the default local AI helpers in one shot, run `./.venv/bin/python manage.py smoke_ai_helpers --continue-on-error`.
- If a helper fails, the smoke JSON includes `setup_hint` with the missing proxy/env step.

## FreeQwenApi service

Install the proxy outside the app tree, then authenticate the Qwen Web session on the server:

```bash
git clone https://github.com/ForgetMeAI/FreeQwenApi.git /opt/FreeQwenApi
cd /opt/FreeQwenApi
npm install
npm run auth
npm run models:sync
```

Then install the service template:

```bash
cp /srv/jyotish-agent/app/deploy/free-qwen-api.service.example /etc/systemd/system/free-qwen-api.service
systemctl daemon-reload
systemctl enable --now free-qwen-api.service
curl -fsS http://127.0.0.1:3264/api/health
cd /srv/jyotish-agent/app/backend
./.venv/bin/python manage.py smoke_ai_helpers --providers qwen
```

Do not commit `session/`, tokens, browser profiles, or local Qwen auth files; they are server-local session secrets.

## FreeDeepseekAPI service

Install the proxy outside the app tree, then authenticate the DeepSeek Web session on the server:

```bash
git clone https://github.com/ForgetMeAI/FreeDeepseekAPI.git /opt/FreeDeepseekAPI
cd /opt/FreeDeepseekAPI
npm run auth
```

Then install the service template:

```bash
cp /srv/jyotish-agent/app/deploy/free-deepseek-api.service.example /etc/systemd/system/free-deepseek-api.service
systemctl daemon-reload
systemctl enable --now free-deepseek-api.service
curl -fsS http://127.0.0.1:9655/health
cd /srv/jyotish-agent/app/backend
./.venv/bin/python manage.py smoke_free_deepseek
```

Do not commit `deepseek-auth.json`; it is a server-local browser session secret.

## OpenRouter Nemotron

Backend calls OpenRouter directly, so no local proxy service is required. Put the key only in server `.env`:

```bash
OPENROUTER_API_KEY=...
OPENROUTER_HTTP_REFERER=https://jyotish.example.com
OPENROUTER_APP_TITLE=Jyotish Agent
NEMOTRON_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
```

Smoke check:

```bash
cd /srv/jyotish-agent/app/backend
./.venv/bin/python manage.py smoke_ai_helpers --providers nemotron
```

The helper repo `C:\Projects\useful-tools\openrouter-nemotron` can be installed on a server for manual CLI checks, but the Django backend does not depend on it at runtime.

## Codex CLI analysis

By default AI analysis path calls:

```bash
codex exec --cd <project-root> --sandbox read-only ...
```

So if `CODEX_ANALYSIS_PROVIDER=codex_cli`, the production backend host/container must have an installed and authenticated `codex` binary. If Docker is used and Codex CLI is not installed inside the backend image, Codex analysis will fail even when ordinary calculations work.

Practical options:

- Run backend on the host venv where `codex` is installed and authenticated.
- Or extend the backend image and mount a server-only Codex auth directory.
- Or set `CODEX_ANALYSIS_PROVIDER=openai` and provide `OPENAI_API_KEY`.

## Approval flow

1. User registers from the site.
2. Admin opens `/admin/`, users list.
3. Select pending users.
4. Run `Approve selected users`.
5. User logs in again and can use calculations, saved charts, compatibility and source-backed analysis.
