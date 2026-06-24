# Session Prompts

Use these prompts in fresh sessions. Do not run them all in parallel.

## Stage 1 Prompt: Technical Core Audit

```text
Work only on Stage 1 Technical Core Audit for Jyotish Agent.

Workspace: C:\w\jt-a
Branch: codex/technical-launch-b

Read first:
- docs/status/CURRENT.md
- docs/roadmap/MASTER_PLAN.md
- docs/exec/2026-06-24-functional-stage-program.md
- docs/exec/2026-06-24-01-technical-core-audit.md
- docs/handoffs/2026-06-24-technical-launch.md

Do not rely on old chat history. Source of truth: repo + git.

Goal:
prove what already works in calculation / technical core and what is a real gap.

Rules:
- do not change runtime code;
- do not do UX/UI;
- do not deploy;
- do not claim JH/PL parity;
- do not commit raw audio/ASR/Telegram/OCR.

Use helpers only read-only:
1. backend coverage helper;
2. frontend/API visibility helper;
3. test/regression helper.

Do not create one helper per D-chart. Check D charts by matrix, not by separate writing agents.

Do:
1. git status;
2. baseline commit;
3. production health;
4. coverage matrix D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60;
5. payload matrix for grahas/houses/panchanga/dashas/classical;
6. focused validation commands from ExecPlan;
7. docs/handoffs/2026-06-24-technical-core-audit.md;
8. update docs/status/CURRENT.md;
9. one docs-only commit;
10. final must include READY_FOR_REVIEW, commit, tests, deploy status, git status.
```

## Stage 2 Prompt: Live Workbench Contract Gate

```text
Work only on Stage 2 Live Workbench Contract Gate for Jyotish Agent.

Workspace: C:\w\jt-a
Branch: codex/technical-launch-b

Read first:
- docs/status/CURRENT.md
- docs/handoffs/2026-06-24-technical-core-audit.md
- docs/exec/2026-06-24-functional-stage-program.md
- docs/exec/2026-06-24-02-live-workbench-contract-gate.md

Goal:
make the real saved-chart calculator smoke (npm.cmd run smoke:calculator-launch) required launch evidence for D1-D60 workbench scopes and core payload status.

Rules:
- this is test/contract work first;
- do not rewrite formulas unless the gate exposes a real runtime failure;
- do not do UX/UI;
- do not deploy test-only/docs-only changes;
- do not create production users/charts;
- keep JH/PL witness-only and make no parity claim;
- do not touch raw audio/ASR/Telegram/OCR.

Expected focus:
1. verify package scripts and launch-readiness contract;
2. harden the contract so the calculator smoke cannot be skipped from launch evidence;
3. run local calculator smoke against local services;
4. run launch-readiness, production-check, typecheck, build;
5. write docs/handoffs/2026-06-24-live-workbench-contract-gate.md;
6. update docs/status/CURRENT.md;
7. commit and push one focused milestone;
8. stop.

Final must include READY_FOR_REVIEW, commit, tests, deploy status, git status.
```

## Stage 3 Prompt: Chart Workflow Hardening

```text
Work only on chart workflow hardening.

First read docs/status/CURRENT.md and the exact Stage 3 ExecPlan named there.

Goal:
make create/edit/calculate/view/recalculate states reliable and testable.

In scope:
- create profile;
- calculate saved profile;
- no-calculation state;
- stale/recalculate state;
- edit after calculation;
- tests/smoke.

Out of scope:
- visual redesign;
- formula changes;
- AI review;
- OCR;
- JH/PL parity.

Final must include READY_FOR_REVIEW, commit, tests, deploy status, git status.
```

## Stage 4 Prompt: Accuracy Witness

```text
Work only on one witness-only accuracy packet.

JH/PL are witness-only. Do not claim parity.

Goal:
add one reviewed witness packet/report with settings, version, reviewer/date, tolerances, and artifacts.

Out of scope:
- proprietary internals;
- bulk parity;
- UI redesign;
- AI interpretation.

Final must include READY_FOR_REVIEW, commit, tests, deploy status, git status.
```

## Stage 5 Prompt: AI Review Quality

```text
Work only on one AI review quality milestone.

Goal:
connect stable saved-chart facts to a gated review draft path.

Rules:
- no public quality claim;
- no raw ASR/audio/Telegram/OCR;
- require calculation anchors, evidence links, caveats, practical questions;
- block unsupported generic analysis before display.

Final must include READY_FOR_REVIEW, commit, tests, deploy status, git status.
```

## Stage 6 Prompt: OCR Evidence Pipeline

```text
Work only on one OCR evidence pipeline milestone.

Goal:
validate reviewed OCR artifacts and provenance.

Rules:
- source artifact must include original/;
- chart/table crops must be referenced;
- research-only cannot become public citation;
- no crude OCR chart blocks as final artifacts.

Final must include READY_FOR_REVIEW, commit, tests, deploy status, git status.
```

## Stage 7 Prompt: UX/UI

```text
Work only as a UX/UI design session.

Read docs/design first.
Do not change code.

Goal:
audit /charts/:id, write a brief, produce 3 distinct visual directions, and stop for selection.

Final must include READY_FOR_REVIEW, artifacts, tests/checks if any, deploy status, git status.
```
