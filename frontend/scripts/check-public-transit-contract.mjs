const url = process.env.PUBLIC_TRANSIT_CHECK_URL || process.argv[2];
const expectedCommit = process.env.EXPECTED_DEPLOY_COMMIT || process.argv[3] || "";
const requestTimeoutMs = Number.parseInt(process.env.PUBLIC_TRANSIT_CHECK_TIMEOUT_MS || "20000", 10);
const requiredRuleIds = [
  "bphs.aspect.graha_drishti.general_7th",
  "bphs.aspect.graha_drishti.mars_special",
  "bphs.aspect.graha_drishti.jupiter_special",
  "bphs.aspect.graha_drishti.saturn_special",
];
const requiredRashiRuleIds = [
  "bphs.aspect.rashi_drishti.movable_to_fixed",
  "bphs.aspect.rashi_drishti.fixed_to_movable",
  "bphs.aspect.rashi_drishti.dual_to_dual",
  "bphs.aspect.rashi_drishti.graha_participation",
];

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exitCode = 1;
  }
}

function withParam(baseUrl, key, value) {
  const next = new URL(baseUrl);
  next.searchParams.set(key, value);
  next.searchParams.set("cb", String(Date.now()));
  return next.toString();
}

function redactUrl(value) {
  const next = new URL(value);
  if (next.searchParams.has("token")) next.searchParams.set("token", "[redacted]");
  return next.toString();
}

async function responseSnippet(response) {
  try {
    return (await response.text()).slice(0, 500).replace(/\s+/g, " ").trim();
  } catch {
    return "";
  }
}

async function fetchWithTimeout(endpointLabel, endpointUrl, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), requestTimeoutMs);
  try {
    const response = await fetch(endpointUrl, { ...options, signal: controller.signal });
    if (!response.ok) {
      const snippet = await responseSnippet(response);
      throw new Error(`${endpointLabel} failed: HTTP ${response.status}${snippet ? ` body: ${snippet}` : ""}`);
    }
    return response;
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error(`${endpointLabel} timed out after ${requestTimeoutMs}ms: ${redactUrl(endpointUrl)}`);
    }
    throw new Error(`${endpointLabel} request failed after ${requestTimeoutMs}ms: ${error.message}`);
  } finally {
    clearTimeout(timer);
  }
}

if (!url) {
  console.error("PUBLIC_TRANSIT_CHECK_URL or first CLI arg is required.");
  process.exit(1);
}

const jsonUrl = withParam(url, "format", "json");
const jsonResponse = await fetchWithTimeout("JSON endpoint", jsonUrl, {
  headers: { Accept: "application/json", "Cache-Control": "no-cache", Pragma: "no-cache" },
});
assert((jsonResponse.headers.get("cache-control") || "").includes("no-store"), "JSON endpoint must use Cache-Control: no-store.");
const payload = await jsonResponse.json();
const contract = payload.grahaDrishtiContract || {};
const rashiContract = payload.rashiDrishtiContract || {};
const aspectLayerContracts = payload.aspectLayerContracts || {};
const aspectLayers = aspectLayerContracts.layers || {};
const grahaLayer = aspectLayers.graha_drishti || {};
const rashiLayer = aspectLayers.rashi_drishti || {};

function assertUiAspectLayer(layer, methodId, label) {
  assert(layer.methodId === methodId, `${label} methodId must match its aspect contract.`);
  assert(layer.sourceStatus === "verified", `${label} sourceStatus must be verified.`);
  assert(layer.uiCapability === true, `${label} UI capability must be enabled.`);
  assert(layer.enabledByDefault === false, `${label} must be disabled by default.`);
  assert(Array.isArray(layer.availableInModes) && layer.availableInModes.length === 1 && layer.availableInModes[0] === "astrologer", `${label} must be astrologer-only.`);
  assert(layer.usesDegreeOrbs === false, `${label} must not use degree orbs.`);
  assert(layer.treatsConjunctionAsAspect === false, `${label} must not treat conjunction as an aspect event.`);
  assert(layer.aspectCount > 0, `${label} must expose calculated aspect count.`);
  assert(layer.safeForNormalUi === true, `${label} must be marked safe for normal UI.`);
  assert(layer.rawEvidence === false, `${label} must not expose raw evidence.`);
  assert(layer.ai === false, `${label} must not enable AI.`);
}

assert(payload.schemaVersion === "transit-workbench-check.v6", "Unexpected transit workbench check schema.");
if (expectedCommit) {
  assert(payload.deployCommit === expectedCommit, `Expected deployCommit ${expectedCommit}, got ${payload.deployCommit}.`);
}
assert(contract.sourceStatus === "verified", "Graha Drishti sourceStatus must be verified.");
assert(Array.isArray(contract.sourceRuleIds), "Graha Drishti sourceRuleIds must be an array.");
assert(requiredRuleIds.every((id) => contract.sourceRuleIds.includes(id)), "Graha Drishti sourceRuleIds must include all verified BPHS rules.");
assert(Array.isArray(contract.sampleRefs) && contract.sampleRefs.length > 0, "Graha Drishti sampleRefs must be present.");
assert(contract.sampleRefs.every((item) => Array.isArray(item.sourceRuleIds) && item.sourceRuleIds.length > 0), "Each Graha Drishti sampleRef needs sourceRuleIds.");
assert(contract.sourceRuleIds.length === requiredRuleIds.length, "Graha Drishti contract must expose exactly four source rules.");
assert(rashiContract.methodId === "aspect.rashi_drishti.parashara.v1", "Rashi Drishti contract is missing.");
assert(rashiContract.sourceStatus === "verified", "Rashi Drishti sourceStatus must be verified after citation verification.");
assert(Array.isArray(rashiContract.sourceRuleIds), "Rashi Drishti sourceRuleIds must be an array.");
assert(requiredRashiRuleIds.every((id) => rashiContract.sourceRuleIds.includes(id)), "Rashi Drishti sourceRuleIds must include all verified BPHS rules.");
assert(rashiContract.sourceRuleIds.length === requiredRashiRuleIds.length, "Rashi Drishti contract must expose exactly four source rules.");
assert(rashiContract.uiCapability === true, "Rashi Drishti UI capability must be enabled for expert layer in 9E-C.");
assert(rashiContract.enabledByDefault === false, "Rashi Drishti must stay disabled by default.");
assert(Array.isArray(rashiContract.availableInModes) && rashiContract.availableInModes.length === 1 && rashiContract.availableInModes[0] === "astrologer", "Rashi Drishti must be astrologer-only.");
assert(rashiContract.aspectCount > 0, "Rashi Drishti contract must expose calculated aspect count.");
assert(Array.isArray(rashiContract.sampleRefs) && rashiContract.sampleRefs.length > 0, "Rashi Drishti contract must expose safe sample refs.");
assert(rashiContract.sampleRefs.every((item) => Array.isArray(item.sourceRuleIds) && item.sourceRuleIds.length > 0), "Each Rashi Drishti sampleRef needs sourceRuleIds.");
assert(aspectLayerContracts.schemaVersion === "transit-aspect-layer-contracts.v1", "Aspect layer QA contract must be present.");
assert(grahaLayer.layerId === "graha_drishti", "Graha Drishti QA layer must be present.");
assert(rashiLayer.layerId === "rashi_drishti", "Rashi Drishti QA layer must be present.");
assert(grahaLayer.methodId !== rashiLayer.methodId, "Graha and Rashi Drishti method IDs must stay separate.");
assertUiAspectLayer(grahaLayer, contract.methodId, "Graha Drishti QA layer");
assertUiAspectLayer(rashiLayer, rashiContract.methodId, "Rashi Drishti QA layer");

const htmlUrl = withParam(url, "format", "");
const htmlResponse = await fetchWithTimeout("HTML endpoint", htmlUrl, {
  headers: { Accept: "text/html", "Cache-Control": "no-cache", Pragma: "no-cache" },
});
assert((htmlResponse.headers.get("cache-control") || "").includes("no-store"), "HTML endpoint must use Cache-Control: no-store.");
const html = await htmlResponse.text();
assert(html.includes("verified"), "HTML endpoint must include verified source status.");
assert(requiredRuleIds.every((id) => html.includes(id)), "HTML endpoint must include all verified Graha Drishti rule IDs.");
assert(html.includes("aspect.rashi_drishti.parashara.v1"), "HTML endpoint must include Rashi Drishti contract.");
assert(requiredRashiRuleIds.every((id) => html.includes(id)), "HTML endpoint must include all verified Rashi Drishti rule IDs.");
assert(html.includes("aspectLayerContracts"), "HTML endpoint must include aspect layer QA contracts.");
assert(html.includes("graha_drishti") && html.includes("rashi_drishti"), "HTML endpoint must include both aspect layer IDs.");
assert(html.includes("safeForNormalUi"), "HTML endpoint must expose normal-UI safety flags.");
if (expectedCommit) {
  assert(html.includes(expectedCommit), `HTML endpoint must include deployCommit ${expectedCommit}.`);
}

if (process.exitCode) process.exit(process.exitCode);
console.log("Public transit contract check passed.");
