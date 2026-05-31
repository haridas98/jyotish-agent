# Development

## Ports

- Frontend: `http://127.0.0.1:3130`
- Backend: `http://127.0.0.1:8100`
- Postgres: `127.0.0.1:55439`
- Redis: `127.0.0.1:6382`

## Checks

Backend:

```powershell
cd backend
python -m pytest
python manage.py check
```

Frontend:

```powershell
cd frontend
npm run typecheck
npm run build
```

## VL

Set `VL_DATABASE_URL` in `.env` only. It must be a read-only connection.

