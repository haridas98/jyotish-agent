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
const aiReviewQuality = read("src/lib/ai-review-quality.ts");
const aiReviewQualityCheck = read("scripts/check-ai-review-quality.mjs");
const reportsPage = read("src/app/reports/page.tsx");
const mockReviewPage = read("src/app/report-mock-review/page.tsx");

for (const marker of [
  "test:launch-readiness",
  "smoke:calculator-launch",
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
]) {
  assert(deployDocs.includes(marker), `Deploy docs missing launch marker: ${marker}`);
}

for (const marker of [
  "codex-worker must be opt-in",
  "CODEX_GENERATION_QUEUE_ENABLED to false",
  "Production browser bundle check passed",
]) {
  assert(productionCheck.includes(marker), `production-check missing safety marker: ${marker}`);
}

for (const marker of [
  "Launch smoke chart",
  "D1",
  "D9",
  "D60",
  "validateTechnicalPayload",
  "classical shadbala payload missing",
  "classical ashtakavarga payload missing",
  "classical yogas payload missing",
]) {
  assert(calculatorSmoke.includes(marker), `calculator launch smoke missing marker: ${marker}`);
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
