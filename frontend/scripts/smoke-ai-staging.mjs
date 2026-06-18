import { existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const backendDir = join("..", "backend");
const python = existsSync(join(backendDir, ".venv", "Scripts", "python.exe"))
  ? join(backendDir, ".venv", "Scripts", "python.exe")
  : "python";

const env = {
  ...process.env,
  DJANGO_DEBUG: "true",
  AI_REPORTS_ENABLED: "true",
  AI_REAL_PROVIDER_ENABLED: "true",
  AI_PROVIDER: "real",
  AI_REPORTS_PUBLIC_UI: "false",
  AI_REPORTS_STAGING_ONLY: "true",
};

const smoke = spawnSync(python, ["manage.py", "smoke_ai_staging"], {
  cwd: backendDir,
  env,
  stdio: "inherit",
  shell: false,
});

process.exit(smoke.status ?? 1);
