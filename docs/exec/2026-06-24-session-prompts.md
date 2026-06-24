# Session Prompts

Use these prompts in fresh sessions. Do not run them all in parallel.

## Stage 1 Prompt: Technical Core Audit

```text
Работай только над technical-core audit для Jyotish Agent.

Рабочая папка: C:\w\jt-a

Сначала прочитай:
- docs/status/CURRENT.md
- docs/roadmap/MASTER_PLAN.md
- docs/exec/2026-06-24-functional-stage-program.md
- docs/exec/2026-06-24-01-technical-core-audit.md
- docs/handoffs/2026-06-24-technical-launch.md

Не полагайся на историю старых чатов. Источник истины: repo + git.

Цель:
доказать, что именно уже работает в calculation / technical core, а что является настоящим пробелом.

Важно:
- не менять runtime code;
- не делать UX/UI;
- не деплоить;
- не claim parity с JH/PL;
- не коммитить raw audio/ASR/Telegram/OCR.

Можно использовать помощников, но только read-only:
1. backend coverage helper;
2. frontend/API visibility helper;
3. test/regression helper.

Не запускай помощника на каждую D-карту. D-карты проверяются матрицей, а не отдельными пишущими агентами.

Сделай:
1. git status;
2. baseline commit;
3. production health;
4. coverage matrix D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60;
5. payload matrix for grahas/houses/panchanga/dashas/classical;
6. focused validation commands from ExecPlan;
7. docs/handoffs/2026-06-24-technical-core-audit.md;
8. update docs/status/CURRENT.md;
9. one docs-only commit;
10. stop.
```

## Stage 2 Prompt: Calculation Gap Closure

```text
Работай только над одним gap из technical-core audit.

Сначала прочитай:
- docs/status/CURRENT.md
- docs/handoffs/2026-06-24-technical-core-audit.md
- соответствующий docs/exec/<gap>.md

Не выбирай gap сам, если CURRENT.md не называет точный next action.

Цель:
закрыть один подтверждённый calculation / technical-core gap минимальным изменением.

Правила:
- TDD: сначала failing test;
- не менять UX/UI;
- не трогать JH/PL parity claims;
- не начинать следующий gap;
- один commit.

После:
- обнови handoff;
- обнови CURRENT.md;
- запусти validation из ExecPlan;
- stop.
```

## Stage 3 Prompt: Chart Workflow Hardening

```text
Работай только над chart workflow hardening.

Цель:
сделать create/edit/calculate/view/recalculate состояния надёжными и проверяемыми.

Сначала создай/прочитай отдельный ExecPlan.

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
```

## Stage 4 Prompt: Accuracy Witness

```text
Работай только над одним witness-only accuracy packet.

JH/PL не являются authority и не дают parity claim.

Цель:
добавить один reviewed witness packet/report with settings, version, reviewer/date, tolerances, artifacts.

Out of scope:
- proprietary internals;
- bulk parity;
- UI redesign;
- AI interpretation.
```

## Stage 5 Prompt: AI Review Quality

```text
Работай только над одним AI review quality milestone.

Цель:
подключить stable saved-chart facts к gated review draft path.

Правила:
- no public quality claim;
- no raw ASR/audio/Telegram/OCR;
- require calculation anchors, evidence links, caveats, practical questions;
- unsupported/generic analysis must be blocked before display.
```

## Stage 6 Prompt: OCR Evidence Pipeline

```text
Работай только над OCR evidence pipeline milestone.

Цель:
валидировать reviewed OCR artifacts and provenance.

Правила:
- source artifact must include original/;
- chart/table crops must be referenced;
- research-only cannot become public citation;
- no crude OCR chart blocks as final artifacts.
```

## Stage 7 Prompt: UX/UI

```text
Работай только как UX/UI design session.

Сначала прочитай docs/design.

Не меняй code.

Цель:
audit /charts/:id, write brief, produce 3 distinct visual directions, stop for selection.
```
