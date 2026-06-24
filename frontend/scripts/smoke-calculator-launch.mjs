const apiBaseUrl = stripTrailingSlash(process.env.JYOTISH_API_BASE_URL || process.argv[2] || "http://127.0.0.1:8000");
const frontendBaseUrl = stripTrailingSlash(process.env.JYOTISH_FRONTEND_BASE_URL || process.argv[3] || "");
const requestTimeoutMs = positiveInt(process.env.JYOTISH_SMOKE_TIMEOUT_MS, 30000);
const requiredScopes = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"];
const jar = createCookieJar();
let checkedFrontendPages = [];

const username = `launch_smoke_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
const password = "strong-pass-108";

await ensureCsrf();

const register = await apiFetch("/api/auth/register", {
  method: "POST",
  body: {
    username,
    password,
  },
});
assert(register.user?.id, "registration did not return a user");

const create = await apiFetch("/api/charts", {
  method: "POST",
  body: {
    display_name: "Launch smoke chart",
    birth_date: "1998-04-30",
    birth_time: "13:45",
    birth_time_accuracy: "exact",
    gender: "male",
    place_name: "Sterlitamak, Bashkortostan, RU",
    timezone: "Asia/Yekaterinburg",
    latitude: 53.6304,
    longitude: 55.9308,
    country_code: "RU",
    calculation_model: "drik_siddhanta",
    ayanamsa: "lahiri",
    node_type: "mean",
    ephemeris: "swiss",
    house_system: "whole_sign",
    bhava_system: "whole_sign",
    varga_scheme: "parashara",
    sunrise_source: "noaa",
    timezone_source: "iana",
    shadbala_profile: "bphs_classical",
    is_self_profile: true,
  },
});
const profile = create.profile;
assert(profile?.id, "profile create did not return profile.id");
assert(profile.birth_time_accuracy === "exact", "profile must preserve exact birth time accuracy");

const calculation = await apiFetch(`/api/charts/profiles/${profile.id}/calculate`, { method: "POST" });
assert(calculation.calculation?.status === "complete", `calculation status must be complete, got ${calculation.calculation?.status}`);
assert(calculation.calculation?.result?.grahas?.length >= 9, "calculation must include graha placements");

const list = await apiFetch("/api/charts");
assert((list.profiles || []).some((item) => item.id === profile.id), "created profile is missing from chart list");

const detail = await apiFetch(`/api/charts/${profile.id}`);
assert(detail.profile?.id === profile.id, "chart detail did not return created profile");
assert(detail.profile?.latest_calculation?.status === "complete", "chart detail must expose complete latest calculation");

const d1Workbench = await apiFetch(`/api/charts/${profile.id}/workbench?scope=d1`);
validateWorkbench(d1Workbench, "D1");
validateTechnicalPayload(d1Workbench.result);

for (const scope of requiredScopes.filter((item) => item !== "D1")) {
  const workbench = await apiFetch(`/api/charts/${profile.id}/workbench?scope=${scope.toLowerCase()}`);
  validateWorkbench(workbench, scope);
}

if (frontendBaseUrl) {
  checkedFrontendPages = [
    "/charts/new",
    `/charts/${profile.id}`,
    `/charts/${profile.id}/edit`,
    "/charts/demo-d1",
    "/launch-status",
  ];
  await assertPageOk(`${frontendBaseUrl}/charts/new`, "new chart page");
  const chartDetailHtml = await assertPageOk(`${frontendBaseUrl}/charts/${profile.id}`, "chart detail page");
  await assertPageOk(`${frontendBaseUrl}/charts/${profile.id}/edit`, "chart edit page");
  assertPageContains(chartDetailHtml, [
    "chart-detail-autocalculate",
  ], "chart detail page");
  const demoDetailHtml = await assertPageOk(`${frontendBaseUrl}/charts/demo-d1`, "demo chart detail page");
  assertPageContains(demoDetailHtml, [
    'data-d1-technical-payload-index-stage="E145-A"',
    "chart_viewer_payload_index_opens_technical_tab=true",
    'data-d1-calculation-passport-stage="E149-A"',
    "E150-A",
    "chart_viewer_calculation_passport_visible=true",
    "calculation_passport_input_settings_visible=true",
    "calculation_passport_birth_coordinates_visible=true",
    'data-d1-classical-payload-status-stage="E151-A"',
    "chart_viewer_classical_payload_status_visible=true",
    "classical_payload_shadbala_status_visible=true",
    "classical_payload_ashtakavarga_status_visible=true",
    "classical_payload_yogas_status_visible=true",
    'data-d1-dasha-status-stage="E152-A"',
    "chart_viewer_dasha_status_visible=true",
    "dasha_payload_vimshottari_status_visible=true",
    "dasha_payload_mahadasha_count_visible=true",
  ], "demo chart detail page");
  const launchStatusHtml = await assertPageOk(`${frontendBaseUrl}/launch-status`, "launch status page");
  assertPageContains(launchStatusHtml, [
    'data-launch-status-stage="E148-A"',
    "launch_ready_technical_chart_service=true",
    "production_deploy_checkpoint_visible=true",
  ], "launch status page");
}

console.log(
  JSON.stringify(
    {
      status: "ok",
      profileId: profile.id,
      user: username,
      calculationStatus: calculation.calculation.status,
      checkedScopes: requiredScopes,
      checkedFrontendPages,
      frontendChecked: Boolean(frontendBaseUrl),
    },
    null,
    2,
  ),
);

function validateWorkbench(payload, expectedScope) {
  assert(payload.scope?.toUpperCase() === expectedScope, `workbench scope mismatch for ${expectedScope}`);
  assert(payload.profile?.id === profile.id, `workbench profile mismatch for ${expectedScope}`);
  assert(payload.calculation?.status === "complete", `workbench calculation must be complete for ${expectedScope}`);
  assert(payload.result, `workbench result is missing for ${expectedScope}`);
  assert(requiredScopes.every((scope) => payload.supportedScopes?.includes(scope)), `supportedScopes missing launch scope for ${expectedScope}`);
  assert(Array.isArray(payload.vargaScopes) && payload.vargaScopes.length >= requiredScopes.length, `varga scope metadata missing for ${expectedScope}`);

  if (expectedScope === "D1") {
    assert(Array.isArray(payload.result.houses) && payload.result.houses.length === 12, "D1 must include 12 houses");
    assert(Array.isArray(payload.result.grahas) && payload.result.grahas.length >= 9, "D1 must include grahas");
    assert(payload.result.ascendant, "D1 must include ascendant");
    return;
  }

  const varga = payload.result.vargas?.[expectedScope];
  assert(varga, `${expectedScope} varga payload missing`);
  assert(Array.isArray(varga.placements) && varga.placements.length >= 10, `${expectedScope} must include Lagna and graha placements`);
  assert(varga.method || varga.methodId, `${expectedScope} must include method metadata`);
}

function validateTechnicalPayload(result) {
  assert(result.settings?.calculation_model === "drik_siddhanta", "settings calculation_model missing");
  assert(result.settings?.ayanamsa === "lahiri", "settings ayanamsa missing");
  assert(result.panchanga?.tithi, "panchanga tithi missing");
  assert(result.panchanga?.vara, "panchanga vara missing");
  assert(result.panchanga?.yoga, "panchanga yoga missing");
  assert(result.panchanga?.karana, "panchanga karana missing");
  const moon = (result.grahas || []).find((item) => item.body === "Moon" || item.body === "Chandra");
  assert(moon?.nakshatra, "Moon nakshatra placement missing");
  assert(result.dashas?.vimshottari?.mahadashas?.length > 0, "vimshottari mahadashas missing");
  assert(requiredScopes.filter((scope) => scope !== "D1").every((scope) => result.vargas?.[scope]), "not all vargas are present in calculation");
  assert(result.classical?.shadbala, "classical shadbala payload missing");
  assert(result.classical?.ashtakavarga, "classical ashtakavarga payload missing");
  assert(result.classical?.yogas, "classical yogas payload missing");
}

async function ensureCsrf() {
  await apiFetch("/api/auth/csrf", { method: "GET", expectJson: false });
  assert(jar.get("csrftoken"), "CSRF cookie was not set");
}

async function apiFetch(path, options = {}) {
  const method = options.method || "GET";
  const headers = {
    Accept: "application/json",
    Cookie: jar.header(),
    ...(options.body ? { "Content-Type": "application/json" } : {}),
  };
  if (method !== "GET" && method !== "HEAD") {
    const token = jar.get("csrftoken");
    if (token) headers["X-CSRFToken"] = token;
    headers.Referer = `${apiBaseUrl}/`;
  }

  const response = await fetchWithTimeout(new URL(path, apiBaseUrl), {
    method,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  jar.capture(response);
  const text = await response.text();
  const data = text ? parseJson(text, path) : {};
  if (!response.ok) {
    throw new Error(`${method} ${path} failed: HTTP ${response.status} ${JSON.stringify(data).slice(0, 500)}`);
  }
  return options.expectJson === false ? {} : data;
}

async function assertPageOk(url, label) {
  const response = await fetchWithTimeout(url, {
    headers: { Accept: "text/html", Cookie: jar.header() },
  });
  if (!response.ok) {
    throw new Error(`${label} failed: HTTP ${response.status}`);
  }
  return response.text();
}

function assertPageContains(html, markers, label) {
  for (const marker of markers) {
    assert(html.includes(marker), `${label} missing marker: ${marker}`);
  }
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

function parseJson(text, path) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${path} returned non-JSON response: ${text.slice(0, 300)}`);
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function stripTrailingSlash(value) {
  return value.replace(/\/+$/, "");
}

function positiveInt(value, fallback) {
  const parsed = Number.parseInt(value || "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function createCookieJar() {
  const cookies = new Map();
  return {
    capture(response) {
      const setCookieHeaders = typeof response.headers.getSetCookie === "function"
        ? response.headers.getSetCookie()
        : splitCombinedSetCookie(response.headers.get("set-cookie"));
      for (const header of setCookieHeaders) {
        const pair = header.split(";", 1)[0];
        const separator = pair.indexOf("=");
        if (separator <= 0) continue;
        cookies.set(pair.slice(0, separator), pair.slice(separator + 1));
      }
    },
    get(name) {
      return cookies.get(name) || "";
    },
    header() {
      return [...cookies.entries()].map(([name, value]) => `${name}=${value}`).join("; ");
    },
  };
}

function splitCombinedSetCookie(value) {
  if (!value) return [];
  return value.split(/,(?=\s*[^;,]+=)/g).map((item) => item.trim()).filter(Boolean);
}
