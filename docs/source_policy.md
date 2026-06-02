# Source Policy

## Source Classes

- `canonical_prabhupada`: Srila Prabhupada books, lectures, letters, conversations from `C:\Projects\vl`.
- `canonical_gaudiya`: reviewed Gaudiya Vaishnava acharya works.
- `jyotish_shastra`: reviewed jyotish classics with clear edition metadata.
- `teacher_reference`: Shyamasundara Dasa and other ISKCON-compatible jyotish materials.
- `research_only`: useful but not yet public.

## Publication Rule

A report may cite only sources with `approved` review status. Research-only or raw imported materials can support internal review but cannot appear in public reports.

## VL Integration

The VL database is the source of truth for Srila Prabhupada and existing Vaishnava corpus data. Jyotish Agent should use a read-only connection and store only citation links, not duplicate text bodies unless a cache is explicitly approved.

## Jyotish Texts

The shastra catalog may store source URLs and short review anchors immediately. Full text committed to the repository is allowed only for public-domain or explicitly licensed editions. Modern translations and PDFs from unclear mirrors must stay `copyright_review_required` and cannot be used for public generated interpretation until reviewed.

Local private full-text files may be imported from `.private_corpus/` for research-only comparison. These chunks must stay out of git, keep `review_status=research_only`, and cannot be quoted in public reports until a passage is manually approved.

When OCR quality is poor, mark the passage as research-only and use it only to locate the exact source area. A reviewed passage must be rechecked against the scan/PDF page and edition before approval.

## Citation Requirement

Every interpretive claim must have one of these:

- a calculation reference;
- a jyotish shastra passage;
- a Prabhupada or Gaudiya source;
- an explicit `calculation_only` label.
