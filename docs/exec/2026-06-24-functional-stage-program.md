# Functional Stage Program

Updated: 2026-06-24

## Purpose

Define the next functional milestones after the technical launch checkpoint.

Rule: do not execute this whole program in one session. Each stage gets one fresh session and one ExecPlan.

## Stage Order

### 1. Calculation / Technical Core Audit

Goal: prove what already works before implementing anything new.

Why first:

- Existing smoke already checks `D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60`.
- The risk is not only missing D charts. The risk is confusing UI visibility, API availability, saved calculation persistence, and formula/test confidence.
- This stage should produce a coverage matrix and a short next-gap list.

Output:

- technical coverage report;
- one recommended next implementation milestone;
- no formula rewrites;
- no UX/UI work.

### 2. Calculation Gap Closure

Goal: close exactly one verified technical-core gap from Stage 1.

Examples:

- one missing varga method contract;
- one missing payload status;
- one missing backend test around saved workbench scope;
- one missing panchanga/dasha/classical field contract.

Output:

- focused tests;
- minimal implementation;
- updated coverage report;
- one commit.

### 3. Chart Workflow Hardening

Goal: make create/edit/calculate/view/recalculate states impossible to confuse.

Scope:

- saved profile creation;
- calculation trigger;
- stale calculation status;
- recalculate;
- no-calculation fallback;
- edit-after-calculate behavior.

Output:

- contract tests and smoke checks;
- no visual redesign.

### 4. Accuracy Witness

Goal: add one reviewed witness packet path without parity claims.

Scope:

- JH/PL are witness-only;
- one case at a time;
- record settings, tolerances, reviewer/date/version;
- no proprietary code/data extraction.

Output:

- reviewed packet/report;
- source scan proving no parity claim leakage.

### 5. AI Review Quality

Goal: connect stable chart facts to gated review draft behavior.

Scope:

- use saved chart facts;
- require calculation anchors, evidence links, caveats, practical questions;
- block generic unsupported analysis;
- no public quality claim.

Output:

- deterministic quality gate;
- one real saved-chart fixture path;
- no raw ASR/audio/Telegram/OCR.

### 6. OCR Literature Evidence

Goal: make reviewed OCR artifacts importable as evidence with provenance.

Scope:

- validator;
- `original/`, crops, chart/table metadata;
- research-only vs approved citation gate;
- chart renderer contracts.

Output:

- rejected bad artifact test;
- accepted reviewed sample;
- provenance chain.

### 7. UX/UI

Goal: redesign only after functional truths are stable.

Scope:

- separate design session;
- audit, brief, three visual directions;
- approved visual source before code;
- no technical behavior changes.

Output:

- `docs/design` updated;
- selected visual direction;
- implementation ExecPlan.

## Helper Policy

Do not assign one helper per D chart by default.

Use helpers by responsibility:

- backend calculation coverage;
- frontend/API/workbench visibility;
- test/smoke/regression coverage;
- source/witness policy.

Helpers are read-only unless a dedicated worktree and ExecPlan are created.

## Completion Rule

After each stage:

- update `docs/status/CURRENT.md`;
- update or add handoff;
- commit;
- stop the session.

The next stage starts in a fresh session.
