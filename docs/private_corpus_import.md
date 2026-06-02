# Private Corpus Import

Full book text for research should stay outside git in `.private_corpus/`.

Supported input now: `.txt` and `.md`. Convert PDF/OCR to text first, then import it as `research_only`.

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py import_private_corpus ..\.private_corpus\jyotish-private-manifest.json
```

Digital source candidates:

| Work | Digital source | Import status |
| --- | --- | --- |
| Brhat Jataka, N. Chidambaram Aiyar, 1905 | <https://archive.org/details/brihatjataka00varaiala>; <https://commons.wikimedia.org/wiki/File:The_Brihat_jataka_(IA_brihatjataka00varaiala).pdf> | public-domain candidate |
| Phaladeepika, V. Subrahmanya Sastri | <https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation>; <https://openlibrary.org/works/OL1038542W/Mantreswara%27s_phaladeepika> | private research / rights review |
| Jataka Parijata, V. Subrahmanya Sastri | WisdomLib has previews/buy references; full text source still needs clean source | private research if user supplies file |
| Brihat Parashara Hora Shastra | Shyamasundara Dasa warns to use with caution; modern editions need rights review | private research / conditional authority |

Rules:

- imported chunks are always `research_only`;
- public reports cannot quote imported chunks until a passage is manually approved;
- source metadata keeps `rights_status` and `public_quote_policy`;
- do not commit `.private_corpus/`.
