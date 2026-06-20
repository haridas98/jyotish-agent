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
const helperPath = "src/astrology/reports/reportReviewWorkspace.ts";
assert(existsSync(pagePath), "Mock human-review page is missing.");
assert(existsSync(helperPath), "AI human-review workspace helper is missing.");

const mojibakeMarkers = ["Рљ", "РЎ", "Рџ", "Р’", "Рћ", "В·", "В°", "�"];

if (existsSync(pagePath)) {
  const page = read(pagePath);
  assert(page.includes("debugRoutesEnabled"), "Mock review page must be hidden behind debugRoutesEnabled.");
  assert(page.includes('redirect("/charts")'), "Mock review page must redirect to /charts when debug routes are disabled.");
  assert(page.includes("runMockAiDryRun"), "Mock review page must use the offline mock provider.");
  assert(page.includes("buildAiReportRequest"), "Mock review page must build the request contract.");
  assert(page.includes("buildAiEligibilityPack"), "Mock review page must use eligibility pack.");
  assert(page.includes("resolveEvidenceProvenance"), "Mock review page must use provenance enrichment.");
  assert(page.includes("buildAiHumanReviewWorkspace"), "Mock review page must normalize dry-run data through review workspace helper.");
  assert(page.includes("Gate status"), "Mock review page must show a gate status section.");
  assert(page.includes("Provider mock"), "Mock review page must show the mock provider section.");
  assert(page.includes("Evidence readiness"), "Mock review page must show evidence readiness.");
  assert(page.includes("Validation summary"), "Mock review page must show validation summary.");
  assert(page.includes("Review items"), "Mock review page must show review items.");

  for (const forbidden of [
    "apiFetch",
    "fetch(",
    "/api/ai/report-dry-run",
    "/api/ai/report-staging-run",
    "RealAiProvider",
    "OPENAI_API_KEY",
    "AI_REAL_PROVIDER_API_KEY",
    "sk-proj",
    "ownerUserId",
    "pairKey",
    "rawEvidence",
    "JSON.stringify(",
  ]) {
    assert(!page.includes(forbidden), `Mock review page must not contain ${forbidden}`);
  }

  for (const marker of mojibakeMarkers) {
    assert(!page.includes(marker), `Mock review page contains mojibake marker ${marker}`);
  }
}

if (existsSync(helperPath)) {
  const helper = read(helperPath);
  assert(helper.includes("jyotish-ai-human-review-workspace-v1"), "Review workspace schema marker is missing.");
  assert(helper.includes("buildAiHumanReviewWorkspace"), "Review workspace builder is missing.");
  assert(helper.includes("review_ready"), "Review workspace must expose review_ready status.");
  assert(helper.includes("blocked"), "Review workspace must expose blocked status.");
  assert(helper.includes("validationSummary"), "Review workspace must expose validation summary.");
  assert(helper.includes("safetyFlags"), "Review workspace must expose safety flags.");
  assert(helper.includes("reviewItems"), "Review workspace must expose review items.");

  for (const forbidden of ["fetch(", "apiFetch", "OPENAI_API_KEY", "AI_REAL_PROVIDER_API_KEY", "rawEvidence", "ownerUserId", "pairKey"]) {
    assert(!helper.includes(forbidden), `Review workspace helper must not contain ${forbidden}`);
  }

  for (const marker of mojibakeMarkers) {
    assert(!helper.includes(marker), `Review workspace helper contains mojibake marker ${marker}`);
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
