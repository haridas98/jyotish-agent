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

For direct LLM generation, configure:

```env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.2
```

Then call:

```http
POST /api/reports/birth-chart/draft-analysis
```

The generated text is saved as `GeneratedAnalysisDraft` with `review_status=draft`.

Alternative local/private providers:

```http
POST /api/reports/birth-chart/qwen-analysis
POST /api/reports/birth-chart/deepseek-analysis
```

- Qwen uses local FreeQwenApi at `QWEN_API_BASE_URL`.
- DeepSeek uses local FreeDeepseekAPI at `FREE_DEEPSEEK_API_BASE_URL` and stores `provider=free_deepseek`.
- DeepSeek is intentionally a compact overview, not the full Codex/Qwen report path.

DeepSeek local/server smoke:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py smoke_free_deepseek
```

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
- use `research_context` only for internal comparison and source discovery;
- never copy `research_context` text into public `citation_titles` or final quoted passages;
- compare multiple translation variants when they are present in the packet;
- cite exact work, chapter/verse if known, edition and translator for every shastra quote;
- flag translation or edition conflicts instead of hiding them;
- do not present calculation drafts as final doctrine;
- do not recommend independent demigod worship;
- reframe remedies through Krishna, sadhu-sanga, sadhana, service, and Srila Prabhupada.

Source import policy:

- public-domain scans, such as the 1905 Brhat Jataka scan, can be used as import candidates;
- modern translations of Phaladipika, Saravali, Jataka Parijata and similar works stay `copyright_review_required` until rights are checked;
- Phaladipika by V. Subrahmanya Sastri is a `private_research_only_until_approved` translation-comparison candidate until rights are verified;
- do not publish generated interpretations from unapproved passages.
