const healthUrl = process.env.JYOTISH_PUBLIC_HEALTH_URL || process.argv[2] || "";
const frontendBaseUrl = stripTrailingSlash(process.env.JYOTISH_PUBLIC_FRONTEND_URL || process.argv[3] || "");
const apiBaseUrl = stripTrailingSlash(process.env.JYOTISH_PUBLIC_API_BASE_URL || originFromUrl(healthUrl));
const expectedDeployCommit = process.env.JYOTISH_PUBLIC_EXPECTED_DEPLOY_COMMIT || process.argv[4] || "";
const requestTimeoutMs = positiveInt(process.env.JYOTISH_SMOKE_TIMEOUT_MS, 15000);

assert(healthUrl, "Set JYOTISH_PUBLIC_HEALTH_URL or pass health URL as argv[2].");
assert(frontendBaseUrl, "Set JYOTISH_PUBLIC_FRONTEND_URL or pass frontend URL as argv[3].");
assert(apiBaseUrl, "Set JYOTISH_PUBLIC_API_BASE_URL or use a health URL with an origin.");

const health = await fetchJson(healthUrl, "production health");
assert(health.status === "ok", `production health status must be ok, got ${health.status}`);
assert(health.service === "jyotish-agent", `production health service mismatch: ${health.service}`);
assert(health.deploy_commit, "production health must expose deploy_commit");
if (expectedDeployCommit) {
  assert(
    health.deploy_commit === expectedDeployCommit,
    `production deploy_commit mismatch: expected ${expectedDeployCommit}, got ${health.deploy_commit}`,
  );
}

const pagePaths = ["/", "/charts", "/charts/new", "/charts/demo-d1", "/launch-status", "/reports", "/dashas"];
for (const path of pagePaths) {
  await assertPageOk(`${frontendBaseUrl}${path}`, path);
}

const technicalDemoMarkers = [
  'data-d1-calculation-passport-stage="E149-A"',
  "E150-A",
  'data-d1-classical-payload-status-stage="E151-A"',
  'data-d1-dasha-status-stage="E152-A"',
  "calculation_passport_birth_coordinates_visible=true",
  "chart_viewer_classical_payload_status_visible=true",
  "chart_viewer_dasha_status_visible=true",
];
const demoHtml = await assertPageOk(`${frontendBaseUrl}/charts/demo-d1`, "/charts/demo-d1");
assertPageContains(demoHtml, technicalDemoMarkers, "/charts/demo-d1");

const launchStatusMarkers = [
  'data-launch-live-health-stage="E153-A"',
  "launch_status_live_health_check_enabled=true",
  "launch_status_live_deploy_commit_visible=true",
];
const launchStatusHtml = await assertPageOk(`${frontendBaseUrl}/launch-status`, "/launch-status");
assertPageContains(launchStatusHtml, launchStatusMarkers, "/launch-status");

await assertStatus(`${apiBaseUrl}/api/auth/csrf`, "CSRF endpoint", [200]);
await assertStatus(`${apiBaseUrl}/api/calculations/ephemeris/status`, "private calculation API gate", [200, 401, 403]);

console.log(
  JSON.stringify(
    {
      status: "ok",
      deployCommit: health.deploy_commit,
      checkedPages: pagePaths,
      checkedApi: ["/api/auth/csrf", "/api/calculations/ephemeris/status"],
      checkedMarkers: [...technicalDemoMarkers, ...launchStatusMarkers],
      writeOperations: false,
    },
    null,
    2,
  ),
);

async function fetchJson(url, label) {
  const response = await fetchWithTimeout(url, {
    headers: { Accept: "application/json" },
  });
  const text = await response.text();
  const data = parseJson(text, label);
  assert(response.ok, `${label} failed: HTTP ${response.status} ${text.slice(0, 300)}`);
  return data;
}

async function assertPageOk(url, label) {
  const response = await fetchWithTimeout(url, {
    headers: { Accept: "text/html" },
  });
  const text = await response.text();
  const contentType = response.headers.get("content-type") || "";
  assert(response.ok, `${label} page failed: HTTP ${response.status}`);
  assert(contentType.includes("text/html"), `${label} page must return HTML, got ${contentType}`);
  return text;
}

function assertPageContains(html, markers, label) {
  for (const marker of markers) {
    assert(html.includes(marker), `${label} page missing marker: ${marker}`);
  }
}

async function assertStatus(url, label, allowedStatuses) {
  const response = await fetchWithTimeout(url, {
    headers: { Accept: "application/json" },
  });
  assert(
    allowedStatuses.includes(response.status),
    `${label} returned unexpected HTTP ${response.status}; allowed: ${allowedStatuses.join(", ")}`,
  );
}

async function fetchWithTimeout(url, init) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), requestTimeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } catch (error) {
    if (error?.name === "AbortError") throw new Error(`request timed out after ${requestTimeoutMs}ms: ${url}`);
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`${label} returned non-JSON response: ${text.slice(0, 300)}`);
  }
}

function originFromUrl(value) {
  if (!value) return "";
  try {
    return new URL(value).origin;
  } catch {
    return "";
  }
}

function stripTrailingSlash(value) {
  return value.replace(/\/+$/, "");
}

function positiveInt(value, fallback) {
  const parsed = Number.parseInt(value || "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}
