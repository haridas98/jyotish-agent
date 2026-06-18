import { existsSync, readFileSync } from "node:fs";
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

const pytest = spawnSync(python, ["-m", "pytest", "apps/reports/test_ai_staging_smoke.py", "-q"], {
  cwd: backendDir,
  stdio: "inherit",
  shell: false,
});

if (pytest.status !== 0) {
  process.exit(pytest.status ?? 1);
}

const command = read("../backend/apps/reports/management/commands/smoke_ai_staging.py");
const packageJson = read("package.json");

for (const marker of [
  "rawContentStored",
  "piiAudit",
  "citationValidation",
  "responseValidation",
  "InsufficientVerifiedEvidence",
  "build_provider_payload",
]) {
  assert(command.includes(marker), `Staging smoke command missing ${marker}`);
}

for (const forbidden of ["rawPrompt", "rawResponse"]) {
  assert(!command.includes(`\"${forbidden}\"`), `Safe receipt must not expose ${forbidden}`);
}

assert(packageJson.includes("smoke:ai-staging"), "Package script smoke:ai-staging is missing.");

if (process.exitCode) process.exit(process.exitCode);
console.log("AI staging smoke check passed.");
