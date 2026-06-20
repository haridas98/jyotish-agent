import { existsSync, readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exitCode = 1;
  }
}

function read(path) {
  assert(existsSync(path), `Missing file: ${path}`);
  return existsSync(path) ? readFileSync(path, "utf8") : "";
}

const helper = read("src/astrology/reports/reportGenerationWorkspace.ts");
const page = read("src/app/reports/page.tsx");
const productionCheck = read("scripts/production-check.mjs");
const packageJson = read("package.json");

for (const marker of [
  "REPORT_WORKSPACE_SCHEMA_VERSION",
  "jyotish-report-workspace-v1",
  "reportIntents",
  "guidanceModes",
  "buildReportWorkspaceReadiness",
  "requestDraft",
  "blockedReasons",
]) {
  assert(helper.includes(marker), `Report workspace helper missing marker: ${marker}`);
}

for (const intent of [
  "short_report",
  "deep_report",
  "question_answer",
  "relationship_report",
  "business_timing",
]) {
  assert(helper.includes(`"${intent}"`), `Report workspace helper missing intent: ${intent}`);
}

for (const mode of ["general", "devotee"]) {
  assert(helper.includes(`"${mode}"`), `Report workspace helper missing guidance mode: ${mode}`);
}

for (const label of ["Короткий отчет", "Глубокий отчет", "Вопрос", "Отношения", "Деловое время", "Общий", "Преданный"]) {
  assert(helper.includes(label), `Report workspace helper missing label: ${label}`);
}

for (const marker of [
  "buildReportWorkspaceReadiness",
  "reportIntents",
  "reportIntents.map",
  "guidanceModes",
  "guidanceModes.map",
  "selectedIntentId",
  "guidanceModeId",
  "questionText",
  "readiness",
  "workspace-readiness-panel",
  "Вопрос",
  "Готовность запроса",
]) {
  assert(page.includes(marker), `/reports missing workspace marker: ${marker}`);
}

for (const forbidden of [
  "fetch(\"/api/ai",
  "fetch('/api/ai",
  "report-dry-run",
  "report-staging-run",
  "Сгенерировать AI",
  "Спросить AI",
  "eligibleItems",
  "excludedItems",
  "rawEvidence",
  "ownerUserId",
  "pairKey",
  "OPENAI_API_KEY",
  "DEEPSEEK",
  "QWEN",
  "sk-proj",
  "source.pending",
  "Рљ",
  "РЎ",
  "Рџ",
  "Р’",
  "В·",
  "�",
]) {
  assert(!helper.includes(forbidden), `Report workspace helper contains forbidden marker: ${forbidden}`);
  assert(!page.includes(forbidden), `/reports contains forbidden marker: ${forbidden}`);
}

assert(productionCheck.includes("src/astrology/reports"), "production-check must scan report helpers.");
assert(productionCheck.includes("src/app/reports/page.tsx"), "production-check must scan /reports page.");
assert(packageJson.includes("\"test:ai-report-workspace\""), "package.json must expose test:ai-report-workspace.");

if (process.exitCode) process.exit(process.exitCode);
console.log("AI report workspace check passed.");
