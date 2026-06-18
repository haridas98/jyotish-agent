import { existsSync, readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exitCode = 1;
  }
}

function read(path) {
  return readFileSync(path, "utf8");
}

const pagePath = "src/app/report-mock-review/page.tsx";
assert(existsSync(pagePath), "Mock human-review page is missing.");

if (existsSync(pagePath)) {
  const page = read(pagePath);
  assert(page.includes("debugRoutesEnabled"), "Mock review page must be hidden behind debugRoutesEnabled.");
  assert(page.includes('redirect("/charts")'), "Mock review page must redirect to /charts when debug routes are disabled.");
  assert(page.includes("runMockAiDryRun"), "Mock review page must use the offline mock provider.");
  assert(page.includes("buildAiReportRequest"), "Mock review page must build the request contract.");
  assert(page.includes("buildAiEligibilityPack"), "Mock review page must use eligibility pack.");
  assert(page.includes("resolveEvidenceProvenance"), "Mock review page must use provenance enrichment.");

  for (const forbidden of [
    "apiFetch",
    "fetch(",
    "/api/ai/report-dry-run",
    "/api/ai/report-staging-run",
    "RealAiProvider",
    "OPENAI_API_KEY",
    "AI_REAL_PROVIDER_API_KEY",
  ]) {
    assert(!page.includes(forbidden), `Mock review page must not contain ${forbidden}`);
  }
}

const nav = read("src/app/app-navigation.tsx");
const reports = read("src/app/reports/page.tsx");
assert(!nav.includes("report-mock-review"), "Mock review page must not be in normal navigation.");
assert(!reports.includes("report-mock-review"), "Mock review page must not be linked from /reports.");
assert(!reports.includes("Сгенерировать AI"), "/reports must not expose AI generation.");
assert(!reports.includes("Спросить AI"), "/reports must not expose Ask AI.");

if (process.exitCode) process.exit(process.exitCode);
console.log("AI human-review mock check passed.");
