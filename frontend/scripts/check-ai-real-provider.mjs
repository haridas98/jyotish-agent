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

const pytest = spawnSync(python, ["-m", "pytest", "apps/reports/test_ai_staging_gateway.py", "-q"], {
  cwd: backendDir,
  stdio: "inherit",
  shell: false,
});

if (pytest.status !== 0) {
  process.exit(pytest.status ?? 1);
}

const realProvider = read("../backend/apps/reports/ai_real_provider.py");
const gateway = read("../backend/apps/reports/ai_gateway.py");
const settings = read("../backend/config/settings.py");

for (const marker of [
  "class RealAiProvider",
  "build_provider_payload",
  "enforce_minimum_coverage",
  "post_json_bytes",
  "parse_provider_response",
  "AI_REAL_PROVIDER_API_KEY",
]) {
  assert(realProvider.includes(marker) || settings.includes(marker), `Real provider missing ${marker}`);
}

for (const marker of [
  "AI_REAL_PROVIDER_ENABLED",
  "AI_REPORTS_STAGING_ONLY",
  "AI_REPORTS_PUBLIC_UI",
  "AI_PROVIDER",
  "AI_REAL_PROVIDER_API_KEY",
]) {
  assert(settings.includes(marker), `Settings missing ${marker}`);
}

assert(gateway.includes("execute_ai_report_staging_run"), "Staging execution function is missing.");
assert(gateway.includes("production_real_provider_blocked"), "Production real-provider guard is missing.");
assert(gateway.includes("real_provider_enabled"), "Real provider feature gate is missing.");
assert(realProvider.includes("chart_id") === false, "Provider payload builder must not include chart_id.");
assert(realProvider.includes("relationship_id") === false, "Provider payload builder must not include relationship_id.");
assert(realProvider.includes("birth_date") === false, "Provider payload builder must not include birth_date.");
assert(realProvider.includes("birth_time") === false, "Provider payload builder must not include birth_time.");
assert(realProvider.includes("display_name") === false, "Provider payload builder must not include display_name.");
assert(realProvider.includes("excluded_items") === false, "Real provider must not receive excluded_items.");

if (process.exitCode) process.exit(process.exitCode);
console.log("AI real provider check passed.");
