# Analysis Generation

Technical generation is split into two reviewed steps.

1. Import or seed approved source anchors and interpretation rules.
2. Build an analysis packet for Codex CLI or another generator.

The packet is citation-first. A generator may use only citations listed in the packet and must keep the output as `draft` until human review.

For marriage compatibility, use the API packet instead of treating ashtakuta as the whole verdict:

```http
POST /api/reports/compatibility/analysis-packet
```

The compatibility packet includes both birth charts, ashtakuta, Lagna/Moon/7th-house/Shukra-Mangala/Guru-Shukra/dasha perspectives, citation requests for each perspective, and a Codex-ready prompt.

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py seed_shastra_catalog
.\.venv\Scripts\python manage.py seed_yoga_catalog
.\.venv\Scripts\python manage.py import_interpretation_catalog C:\path\catalog.json
.\.venv\Scripts\python manage.py build_analysis_packet `
  --birth-date 1998-04-30 `
  --birth-time 13:45 `
  --place-name "Ishimbay" `
  --timezone Asia/Yekaterinburg `
  --latitude 53.4546 `
  --longitude 56.0439 `
  --output .tmp\analysis-packet.json `
  --prompt-output .tmp\analysis-prompt.md `
  --citation-requests-output .tmp\citation-requests.json
```

Rules for generated text:

- do not invent shastra citations;
- use `citation_requests` as the checklist for missing shastra evidence;
- do not present calculation drafts as final doctrine;
- do not recommend independent demigod worship;
- reframe remedies through Krishna, sadhu-sanga, sadhana, service, and Srila Prabhupada.
