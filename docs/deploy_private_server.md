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

## Required production env decisions

- `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD` must be real secrets.
- `DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL` must match the actual domain.
- `VL_DATABASE_URL` must point to the Prabhupada/VL database if source search must work on the server.
- Swiss/JPL ephemeris files must be placed in `./ephe` if JPL mode is needed.
- For DeepSeek overview generation, run FreeDeepseekAPI and set `FREE_DEEPSEEK_API_BASE_URL` in the server `.env`, usually `http://127.0.0.1:9655/v1`.
- After deploy, run `cd /srv/jyotish-agent/app/backend && ./.venv/bin/python manage.py smoke_free_deepseek` to verify server-side FreeDeepseekAPI access.

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
