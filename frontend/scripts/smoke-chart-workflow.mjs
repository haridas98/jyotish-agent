const apiBaseUrl = stripTrailingSlash(process.env.JYOTISH_API_BASE_URL || process.argv[2] || "http://127.0.0.1:8000");
const frontendBaseUrl = stripTrailingSlash(process.env.JYOTISH_FRONTEND_BASE_URL || process.argv[3] || "");
const requestTimeoutMs = positiveInt(process.env.JYOTISH_SMOKE_TIMEOUT_MS, 30000);
const jar = createCookieJar();
const checkedFrontendPages = [];

const username = `workflow_smoke_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
const password = "strong-pass-108";

await ensureCsrf();

await apiFetch("/api/auth/register", {
  method: "POST",
  body: { username, password },
});

const create = await apiFetch("/api/charts", {
  method: "POST",
  body: {
    display_name: "Workflow smoke chart",
    birth_date: "1998-04-30",
    birth_time: "13:45",
    birth_time_accuracy: "exact",
    gender: "male",
    place_name: "Sterlitamak, Bashkortostan, RU",
    timezone: "Asia/Yekaterinburg",
    latitude: 53.6304,
    longitude: 55.9308,
    country_code: "RU",
    node_type: "mean",
    ayanamsa: "lahiri",
    house_system: "whole_sign",
    varga_scheme: "parashara",
  },
});
const profile = create.profile;
assert(profile?.id, "profile create did not return profile.id");
assertState(profile, "not_calculated");

const savedOnlyDetail = await apiFetch(`/api/charts/${profile.id}`);
assertState(savedOnlyDetail.profile, "not_calculated");

const calculation = await apiFetch(`/api/charts/profiles/${profile.id}/calculate`, { method: "POST" });
assert(calculation.calculation?.status === "complete", `calculation status must be complete, got ${calculation.calculation?.status}`);

const completeDetail = await apiFetch(`/api/charts/${profile.id}`);
assertState(completeDetail.profile, "complete");
assert(completeDetail.profile.latest_calculation?.status === "complete", "detail must expose complete latest calculation");

const completeWorkbench = await apiFetch(`/api/charts/${profile.id}/workbench?scope=d1`);
assertState(completeWorkbench.profile, "complete");
assert(completeWorkbench.calculation?.status === "complete", "workbench must render saved complete calculation");

const edited = await apiFetch(`/api/charts/${profile.id}`, {
  method: "PATCH",
  body: {
    birth_time: "14:05",
    node_type: "true",
  },
});
assert(edited.profile.birth_time === "14:05", "edit must preserve changed birth time");
assert(edited.profile.calculation_settings?.node_type === "true", "edit must preserve changed calculation assumption");
assertState(edited.profile, "stale");

const staleList = await apiFetch("/api/charts");
const staleListProfile = (staleList.profiles || []).find((item) => item.id === profile.id);
assertState(staleListProfile, "stale");

const staleWorkbench = await apiFetch(`/api/charts/${profile.id}/workbench?scope=d1`);
assertState(staleWorkbench.profile, "stale");

const recalculation = await apiFetch(`/api/charts/profiles/${profile.id}/calculate`, { method: "POST" });
assert(recalculation.calculation?.status === "complete", "recalculation must complete");
const recalculatedDetail = await apiFetch(`/api/charts/${profile.id}`);
assertState(recalculatedDetail.profile, "complete");

const failedCreate = await apiFetch("/api/charts", {
  method: "POST",
  body: {
    display_name: "Workflow failed chart",
    birth_date: "1998-04-30",
    birth_time: "",
    birth_time_accuracy: "exact",
    place_name: "Sterlitamak, Bashkortostan, RU",
    timezone: "Asia/Yekaterinburg",
    latitude: 53.6304,
    longitude: 55.9308,
    country_code: "RU",
  },
});
const failedCalculation = await apiFetch(`/api/charts/profiles/${failedCreate.profile.id}/calculate`, {
  method: "POST",
  allowedStatuses: [503],
});
assert(failedCalculation.calculation?.status === "failed", "failed calculation must return failed status");
assert(failedCalculation.calculation?.error || failedCalculation.calculation?.message, "failed calculation must include a useful message");
const failedDetail = await apiFetch(`/api/charts/${failedCreate.profile.id}`);
assertState(failedDetail.profile, "failed");

if (frontendBaseUrl) {
  checkedFrontendPages.push("/charts/new", `/charts/${profile.id}`, `/charts/${profile.id}/edit`, "/charts");
  const newHtml = await assertPageOk(`${frontendBaseUrl}/charts/new`, "new chart page");
  assertPageContains(newHtml, ["chart-workflow-state-calculation-requested"], "new chart page");
  const detailHtml = await assertPageOk(`${frontendBaseUrl}/charts/${profile.id}`, "chart detail page");
  assertPageContains(detailHtml, [
    "chart-workflow-state-not-calculated",
    "chart-workflow-state-complete",
    "chart-workflow-state-failed",
    "chart-workflow-state-stale",
    "chart-workflow-recalculate-complete",
  ], "chart detail page");
  const editHtml = await assertPageOk(`${frontendBaseUrl}/charts/${profile.id}/edit`, "chart edit page");
  assertPageContains(editHtml, ["chart-workflow-edit-preserves-assumptions"], "chart edit page");
  await assertPageOk(`${frontendBaseUrl}/charts`, "charts list page");
}

console.log(
  JSON.stringify(
    {
      status: "ok",
      profileId: profile.id,
      failedProfileId: failedCreate.profile.id,
      user: username,
      checkedStates: ["not_calculated", "complete", "stale", "failed", "recalculated"],
      checkedFrontendPages,
      frontendChecked: Boolean(frontendBaseUrl),
    },
    null,
    2,
  ),
);

function assertState(profile, expected) {
  assert(profile?.calculation_state?.status === expected, `expected ${expected} state, got ${profile?.calculation_state?.status}`);
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
  const allowedStatuses = options.allowedStatuses || [];
  if (!response.ok && !allowedStatuses.includes(response.status)) {
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
