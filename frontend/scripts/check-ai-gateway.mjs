import { readFileSync } from "node:fs";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exitCode = 1;
  }
}

function read(path) {
  return readFileSync(path, "utf8");
}

const backendDir = join("..", "backend");
const python = existsSync(join(backendDir, ".venv", "Scripts", "python.exe"))
  ? join(backendDir, ".venv", "Scripts", "python.exe")
  : "python";

const pytest = spawnSync(python, ["-m", "pytest", "apps/reports/test_ai_gateway.py", "-q"], {
  cwd: backendDir,
  stdio: "inherit",
  shell: false,
});

if (pytest.status !== 0) {
  process.exit(pytest.status ?? 1);
}

const gateway = read("../backend/apps/reports/ai_gateway.py");
const view = read("../backend/apps/reports/views.py");
const urls = read("../backend/apps/reports/urls.py");
const reportsPage = read("src/app/reports/page.tsx");

for (const marker of [
  "class MockAiProvider",
  "class DisabledAiProvider",
  "class AiProvider",
  "build_ai_report_request",
  "validate_ai_response",
  "excluded_summary",
  "provider_for_settings",
]) {
  assert(gateway.includes(marker), `AI gateway missing ${marker}`);
}

for (const forbidden of [
  "requests.",
  "urllib.request",
  "httpx",
  "openai",
  "OpenAI",
  "prompt",
  "raw_provider_response",
]) {
  assert(!gateway.includes(forbidden), `AI gateway must not contain ${forbidden}`);
}

assert(view.includes("AiReportDryRunView"), "AiReportDryRunView is missing.");
assert(view.includes("AI_REPORTS_ENABLED"), "AI reports feature flag guard is missing.");
assert(urls.includes("ai/report-dry-run"), "AI dry-run route is missing.");
assert(!reportsPage.includes("Сгенерировать AI"), "/reports must not expose an AI generation button.");
assert(!reportsPage.includes("Спросить AI"), "/reports must not expose Ask AI.");

if (process.exitCode) process.exit(process.exitCode);
console.log("AI gateway check passed.");
