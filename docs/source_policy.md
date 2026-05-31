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

## Citation Requirement

Every interpretive claim must have one of these:

- a calculation reference;
- a jyotish shastra passage;
- a Prabhupada or Gaudiya source;
- an explicit `calculation_only` label.

