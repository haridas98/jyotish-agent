# Private Corpus Import

Full book text for research should stay outside git in `.private_corpus/`.

Supported input now: `.txt`, `.md` and SanskritDocuments `.itx`. Convert PDF/OCR to text first, then import it as `research_only`.

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py import_private_corpus ..\.private_corpus\jyotish-private-manifest.json
```

Search imported research chunks:

```http
GET /api/sources/research/search?q=gaja%20kesari
```

Split imported chunks into review-only passage candidates:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py segment_private_corpus --max-chars 1800
```

Inspect source and condition coverage:

```http
GET /api/sources/coverage
GET /api/reports/shastra-condition-matrix
GET /api/reports/shastra-evidence
```

The birth-chart and compatibility analysis packets include matching private chunks in `research_context`. These items are not `citations`; they are evidence for internal comparison only.

The analysis packets also include `shastra_coverage` and `shastra_condition_matrix`, so Codex CLI can work through every calculation layer, report section and yoga condition against loaded shastra evidence.

Build condition-to-passage evidence:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_shastra_evidence --limit-per-condition 5 --min-score 10
```

Generate a Codex CLI draft from matched evidence:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py generate_codex_analysis `
  --birth-date 1998-04-30 `
  --birth-time 13:45 `
  --place-name "Sterlitamak, Russia" `
  --latitude 53.37 `
  --longitude 55.57 `
  --timezone Asia/Yekaterinburg `
  --as-of-date 2026-06-03 `
  --output ..\.tmp\codex-analysis-haridev.json
```

Review OCR quality with Qwen and FreeDeepseek without modifying source passages:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py review_private_corpus_ocr_with_ai `
  --work-slug vedic-astrology-integrated-approach-pvr-private `
  --providers qwen,free_deepseek `
  --limit 1 `
  --output ..\.tmp\ocr-review\pvr-textbook-chunk-0001-qwen-deepseek.json
```

The command writes provider-normalized variants and OCR issue lists to `.tmp\ocr-review`. It does not overwrite the imported private corpus; human review decides which correction becomes a trusted passage.

Digital source candidates:

| Work | Digital source | Import status |
| --- | --- | --- |
| Brhat Jataka, N. Chidambaram Aiyar, 1905 | <https://archive.org/details/brihatjataka00varaiala>; <https://commons.wikimedia.org/wiki/File:The_Brihat_jataka_(IA_brihatjataka00varaiala).pdf> | public-domain candidate |
| Phaladeepika, V. Subrahmanya Sastri | <https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation>; <https://openlibrary.org/works/OL1038542W/Mantreswara%27s_phaladeepika> | private research / rights review |
| Jataka Parijata, V. Subrahmanya Sastri | WisdomLib has previews/buy references; full text source still needs clean source | private research if user supplies file |
| Brihat Parashara Hora Shastra | Shyamasundara Dasa warns to use with caution; modern editions need rights review | private research / conditional authority |
| Vedic Astrology: An Integrated Approach, P.V.R. Narasimha Rao | <https://www.vedicastrologer.org/articles/vedic_astro_textbook.pdf> | local PDF + extracted text, private research / rights review |
| SanskritDocuments Jyotish ITX corpus | <https://sanskritdocuments.org/sanskrit/sociology_astrology/> | private research / Sanskrit ITRANS |
| GRETIL Jyotish/astronomy/math corpus | <https://gretil.sub.uni-goettingen.de/gretil.html#Jyot> | private research / Sanskrit plain text |
| Internet Archive Jyotish OCR layer | archive.org item OCR for Saravali, Sarvartha, Muhurta, Jaimini, Hora Sara, Prasna and related works | private research / OCR rights review |

Rules:

- imported chunks are always `research_only`;
- segmented candidate passages are also `research_only`;
- condition evidence maps `condition/yoga/avastha -> passage -> inferred reference -> draft interpretation prompt`;
- public reports cannot quote imported chunks until a passage is manually approved;
- source metadata keeps `rights_status` and `public_quote_policy`;
- do not commit `.private_corpus/`.
