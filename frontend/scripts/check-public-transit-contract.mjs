const url = process.env.PUBLIC_TRANSIT_CHECK_URL || process.argv[2];
const expectedCommit = process.env.EXPECTED_DEPLOY_COMMIT || process.argv[3] || "";
const requiredRuleIds = [
  "bphs.aspect.graha_drishti.general_7th",
  "bphs.aspect.graha_drishti.mars_special",
  "bphs.aspect.graha_drishti.jupiter_special",
  "bphs.aspect.graha_drishti.saturn_special",
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

if (!url) {
  console.error("PUBLIC_TRANSIT_CHECK_URL or first CLI arg is required.");
  process.exit(1);
}

const jsonUrl = withParam(url, "format", "json");
const jsonResponse = await fetch(jsonUrl, {
  headers: { Accept: "application/json", "Cache-Control": "no-cache", Pragma: "no-cache" },
});
assert(jsonResponse.ok, `JSON endpoint failed: HTTP ${jsonResponse.status}`);
assert((jsonResponse.headers.get("cache-control") || "").includes("no-store"), "JSON endpoint must use Cache-Control: no-store.");
const payload = await jsonResponse.json();
const contract = payload.grahaDrishtiContract || {};

assert(payload.schemaVersion === "transit-workbench-check.v5", "Unexpected transit workbench check schema.");
if (expectedCommit) {
  assert(payload.deployCommit === expectedCommit, `Expected deployCommit ${expectedCommit}, got ${payload.deployCommit}.`);
}
assert(contract.sourceStatus === "verified", "Graha Drishti sourceStatus must be verified.");
assert(Array.isArray(contract.sourceRuleIds), "Graha Drishti sourceRuleIds must be an array.");
assert(requiredRuleIds.every((id) => contract.sourceRuleIds.includes(id)), "Graha Drishti sourceRuleIds must include all verified BPHS rules.");
assert(Array.isArray(contract.sampleRefs) && contract.sampleRefs.length > 0, "Graha Drishti sampleRefs must be present.");
assert(contract.sampleRefs.every((item) => Array.isArray(item.sourceRuleIds) && item.sourceRuleIds.length > 0), "Each Graha Drishti sampleRef needs sourceRuleIds.");
assert(contract.sourceRuleIds.length === requiredRuleIds.length, "Graha Drishti contract must expose exactly four source rules.");

const htmlUrl = withParam(url, "format", "");
const htmlResponse = await fetch(htmlUrl, {
  headers: { Accept: "text/html", "Cache-Control": "no-cache", Pragma: "no-cache" },
});
assert(htmlResponse.ok, `HTML endpoint failed: HTTP ${htmlResponse.status}`);
assert((htmlResponse.headers.get("cache-control") || "").includes("no-store"), "HTML endpoint must use Cache-Control: no-store.");
const html = await htmlResponse.text();
assert(html.includes("verified"), "HTML endpoint must include verified source status.");
assert(!html.includes("needs_source"), "HTML endpoint must not include needs_source for Graha Drishti.");
assert(requiredRuleIds.every((id) => html.includes(id)), "HTML endpoint must include all verified Graha Drishti rule IDs.");
if (expectedCommit) {
  assert(html.includes(expectedCommit), `HTML endpoint must include deployCommit ${expectedCommit}.`);
}

if (process.exitCode) process.exit(process.exitCode);
console.log("Public transit contract check passed.");
