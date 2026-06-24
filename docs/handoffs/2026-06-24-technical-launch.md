# Handoff: Technical Launch Supervisor

Date: 2026-06-24

## Outcome

Private technical Jyotish chart launch is deployed and verified.

Production baseline:

- Commit: `8c23a784`
- URL: `https://jyotish-agent.duckdns.org/`
- Health: `deploy_commit=8c23a784`

Branch state:

- Branch: `codex/technical-launch-b`
- Latest pushed commit: `e2b7bded`
- `e2b7bded` is test-safety only and is not deployed.

## Completed

- Saved chart technical workflow is visible on `/charts/:id` and `/charts/demo-d1`.
- D1-D60 implemented scope coverage is visible in the chart workbench.
- Calculation passport shows birth input, settings, panchanga, dasha/classical status, and deploy context.
- `/launch-status` shows live health/deploy commit.
- Production read-only smoke checks E149/E150/E151/E152/E153 markers.
- Browser smoke now verifies `/launch-status` actually renders health/deploy commit after client-side fetch.

## Validation Evidence

Last deployed runtime (`8c23a784`):

- `npm.cmd run test:launch-readiness`
- `npm.cmd run test:d1-workbench`
- `npm.cmd run test:chart-workbench-ux`
- `npm.cmd run test:chart-detail-smoke`
- `npm.cmd run test:dasha-workbench`
- `npm.cmd run typecheck`
- `npm.cmd run production-check`
- `npm.cmd run build`
- production read-only smoke on IP and HTTPS

Latest test-safety commit (`e2b7bded`):

- `npm.cmd run test:launch-readiness`
- `npm.cmd run typecheck`
- `npm.cmd run smoke:launch-status-browser`
- `npm.cmd run production-check`

## Decisions

- Do not claim JH/PL parity. Treat JH/PL as witness-only.
- Do not commit raw ASR/audio or raw Telegram export.
- Keep OCR work separate from technical launch.
- Do not deploy commits that only change local/test safety unless bundled with a runtime checkpoint.
- End this long supervisor thread after handoff; use fresh sessions per milestone.

## Next Session

Start from `docs/status/CURRENT.md`.

Do not continue with generic “make it better” work. Pick exactly one milestone and create/read its `docs/exec/*.md` before editing code.
