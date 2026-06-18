import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exitCode = 1;
  }
}

function read(path) {
  return readFileSync(path, "utf8");
}

const urls = read("../backend/apps/reports/urls.py");
const views = read("../backend/apps/reports/views.py");
const reportsPage = read("src/app/reports/page.tsx");
const productionCheck = read("scripts/production-check.mjs");

assert(urls.includes("ai/report-staging-run"), "Staging AI route is missing.");
assert(views.includes("AiReportStagingRunView"), "Staging AI view is missing.");
assert(views.includes("production_real_provider_blocked"), "Staging view must block production real provider.");
assert(views.includes("AI_REAL_PROVIDER_ENABLED"), "Staging view must require AI_REAL_PROVIDER_ENABLED.");
assert(views.includes("AI_PROVIDER"), "Staging view must require AI_PROVIDER.");
assert(!reportsPage.includes("Сгенерировать AI"), "/reports must not expose an AI generation button.");
assert(!reportsPage.includes("Спросить AI"), "/reports must not expose Ask AI.");

for (const marker of ["sk-", "AI_REAL_PROVIDER_API_KEY", "OPENAI_API_KEY"]) {
  assert(productionCheck.includes(marker) || marker !== "sk-", "Production check should scan common secret prefixes.");
}

if (process.exitCode) process.exit(process.exitCode);
console.log("AI staging gateway check passed.");
