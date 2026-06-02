# Jyotish Agent

Jyotish Agent is a Gaudiya Vaishnava astrology service. The goal is accurate jyotish calculations, auditable source citations, and Krishna-centered recommendations aligned with Srila Prabhupada and ISKCON parampara.

## Current Slice

- Django/DRF backend skeleton.
- Next.js frontend skeleton.
- PostgreSQL and Redis local services.
- Health endpoints.
- First calculation primitives: Julian day, rashi, nakshatra, pada, navamsa.
- Optional Swiss Ephemeris provider interface.
- Backend place search and timezone resolution for the first curated locations.
- Authenticated birth profile API with private per-user profile listing.
- Real Swiss-backed D1 calculation basics: grahas, Lagna, whole-sign houses, panchanga.
- Vimshottari mahadasha MVP engine from Moon longitude, marked draft until JHora parity.
- Codex-ready analysis packet API and CLI for draft chart interpretation generation.
- Accuracy fixture runner for JHora-style parity cases.
- JHora `.jhd` input importer for draft parity fixtures.
- Policy docs for calculation authority, sources, JHora parity, and Vaishnava interpretation.

## Local Start

```powershell
Copy-Item .env.example .env
docker compose up -d postgres redis
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_vaishnava_interpretations
.\.venv\Scripts\python manage.py seed_shastra_catalog
.\.venv\Scripts\python manage.py seed_yoga_catalog
.\.venv\Scripts\python manage.py runserver 127.0.0.1:8100
```

Generate an analysis packet for Codex CLI:

```powershell
cd backend
.\.venv\Scripts\python manage.py build_analysis_packet `
  --birth-date 1998-04-30 `
  --birth-time 13:45 `
  --place-name "Ishimbay" `
  --output .tmp\analysis-packet.json `
  --prompt-output .tmp\analysis-prompt.md `
  --citation-requests-output .tmp\citation-requests.json
```

Frontend:

```powershell
cd frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3130
```

## Important Rules

- Do not copy or decompile Jagannatha Hora. Use it only as a functional and accuracy reference.
- Do not treat any single astrology website as final authority. Follow `docs/calculation_authority.md`.
- Do not duplicate `C:\Projects\vl` content. Query it read-only for citations.
- Do not publish unreviewed shastra imports or unapproved interpretation rules.
- Do not recommend independent demigod worship. Remedies must be Krishna-centered.
- Do not enable Swiss Ephemeris in production until licensing is resolved.
