# Jyotish Agent

Jyotish Agent is a Gaudiya Vaishnava astrology service. The goal is accurate jyotish calculations, auditable source citations, and Krishna-centered recommendations aligned with Srila Prabhupada and ISKCON parampara.

## Current Slice

- Django/DRF backend skeleton.
- Next.js frontend skeleton.
- PostgreSQL and Redis local services.
- Health endpoints.
- First calculation primitives: Julian day, rashi, nakshatra, pada, navamsa.
- Optional Swiss Ephemeris provider interface.
- Policy docs for sources, JHora parity, and Vaishnava interpretation.

## Local Start

```powershell
Copy-Item .env.example .env
docker compose up -d postgres redis
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver 127.0.0.1:8100
```

Frontend:

```powershell
cd frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3130
```

## Important Rules

- Do not copy or decompile Jagannatha Hora. Use it only as a functional and accuracy reference.
- Do not duplicate `C:\Projects\vl` content. Query it read-only for citations.
- Do not publish unreviewed shastra imports or unapproved interpretation rules.
- Do not recommend independent demigod worship. Remedies must be Krishna-centered.
- Do not enable Swiss Ephemeris in production until licensing is resolved.
