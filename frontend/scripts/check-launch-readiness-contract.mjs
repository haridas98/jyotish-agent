import { existsSync, readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function read(path) {
  assert(existsSync(path), `Missing file: ${path}`);
  return readFileSync(path, "utf8");
}

const packageJson = read("package.json");
const deployDocs = read("../docs/deploy_private_server.md");
const aiReviewDocs = read("../docs/ai_review_quality_reset.md");
const productionCheck = read("scripts/production-check.mjs");
const calculatorSmoke = read("scripts/smoke-calculator-launch.mjs");
const productionLiveSmoke = read("scripts/smoke-production-live.mjs");
const aiReviewQuality = read("src/lib/ai-review-quality.ts");
const aiReviewQualityCheck = read("scripts/check-ai-review-quality.mjs");
const reportsPage = read("src/app/reports/page.tsx");
const mockReviewPage = read("src/app/report-mock-review/page.tsx");
const chartsPage = read("src/app/charts/page.tsx");
const launchStatusPage = read("src/app/launch-status/page.tsx");

for (const marker of [
  "test:launch-readiness",
  "smoke:calculator-launch",
  "smoke:production-live",
  "test:ai-review-quality",
  "production-check",
  "build:prod",
]) {
  assert(packageJson.includes(`"${marker}"`), `package.json missing launch marker: ${marker}`);
}

for (const marker of [
  "CODEX_GENERATION_QUEUE_ENABLED=false",
  "Calculator-only launch is the default",
  "Local calculator launch smoke before a deploy checkpoint",
  "deploy_commit",
  "smoke:production-live",
  "JYOTISH_PUBLIC_EXPECTED_DEPLOY_COMMIT",
]) {
  assert(deployDocs.includes(marker), `Deploy docs missing launch marker: ${marker}`);
}

for (const marker of [
  "codex-worker must be opt-in",
  "CODEX_GENERATION_QUEUE_ENABLED to false",
  "Production browser bundle check passed",
  "Production live smoke is missing launch marker",
]) {
  assert(productionCheck.includes(marker), `production-check missing safety marker: ${marker}`);
}

for (const marker of [
  "expectedDeployCommit",
  "checkedPages",
  "checkedApi",
  "health.deploy_commit",
  'health.status === "ok"',
  'health.service === "jyotish-agent"',
  '"/charts"',
  "/charts/demo-d1",
  "/api/auth/csrf",
  "/api/calculations/ephemeris/status",
  "writeOperations: false",
]) {
  assert(productionLiveSmoke.includes(marker), `production live smoke missing marker: ${marker}`);
}

for (const marker of [
  "Launch smoke chart",
  "D1",
  "D9",
  "D60",
  "validateTechnicalPayload",
  "/charts/${profile.id}/edit",
  "/charts/demo-d1",
  "/launch-status",
  "chart-detail-autocalculate",
  "assertPageContains",
  "checkedFrontendPages",
  "data-d1-technical-payload-index-stage",
  "chart_viewer_payload_index_opens_technical_tab=true",
  "data-launch-status-stage",
  "classical shadbala payload missing",
  "classical ashtakavarga payload missing",
  "classical yogas payload missing",
]) {
  assert(calculatorSmoke.includes(marker), `calculator launch smoke missing marker: ${marker}`);
}

for (const marker of [
  "/launch-status",
  "Launch status",
]) {
  assert(chartsPage.includes(marker), `/charts missing launch status entry marker: ${marker}`);
}

for (const marker of [
  'data-launch-status-stage="E148-A"',
  "launch_ready_technical_chart_service=true",
  "d_scope_visibility=D1-D60",
  "ai_review_quality_contract_gated=true",
  "jh_pl_witness_only=true",
  "ocr_literature_track_separate=true",
  "production_deploy_checkpoint_visible=true",
  "production_deploy_commit_checked_by_health=true",
  "smoke:calculator-launch",
  "smoke:production-live",
]) {
  assert(launchStatusPage.includes(marker), `/launch-status missing launch status marker: ${marker}`);
}

for (const marker of [
  "E134-A",
  "buildAiReviewAudioConsultationBenchmark",
  "audio_haridas_house_walkthrough",
  "audio_govardhan_yoga_weighting",
  "rawTranscriptCommitted: false",
  "sourceAudioCommitted: false",
  "witnessOnly: true",
  "Do not treat the witness as JH/PL parity evidence",
]) {
  assert(aiReviewQuality.includes(marker), `AI review quality helper missing audio benchmark marker: ${marker}`);
  assert(aiReviewQualityCheck.includes(marker) || marker === "rawTranscriptCommitted: false" || marker === "sourceAudioCommitted: false" || marker === "witnessOnly: true", `AI review quality check missing marker: ${marker}`);
}

for (const marker of [
  "Audio consultation benchmark",
  "Local ASR witness for review structure",
  "raw transcripts and source audio are not committed",
  'data-ai-review-audio-consultation-stage="E134-A"',
]) {
  assert(reportsPage.includes(marker), `/reports missing audio benchmark marker: ${marker}`);
  assert(mockReviewPage.includes(marker), `/report-mock-review missing audio benchmark marker: ${marker}`);
}

for (const marker of [
  "sanitized Telegram benchmark",
  "No source style copying",
  "sanitized audio consultation benchmark",
  "raw ASR transcripts",
  "witness-only",
]) {
  assert(aiReviewDocs.includes(marker), `AI review docs missing benchmark policy marker: ${marker}`);
}

const combinedCommittedSource = [
  deployDocs,
  aiReviewDocs,
  aiReviewQuality,
  reportsPage,
  mockReviewPage,
].join("\n");

for (const forbidden of [
  "E:\\Downloads",
  "ChatExport_2026-06-23",
  "Астрологическая_консультация_Харидас",
  "Говардхан_9_10_утра",
  "Харрикично",
  "Рассматриваем гороскоп Говордарно",
  "parity success",
  "release ready",
  "production_deploy_executed=true",
]) {
  assert(!combinedCommittedSource.includes(forbidden), `Launch readiness source leaked forbidden marker: ${forbidden}`);
}

console.log("Launch readiness contract check passed.");
