import { readFileSync } from "node:fs";

function read(path) {
  return readFileSync(path, "utf8");
}

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exitCode = 1;
  }
}

const gate = read("src/astrology/sources/aiEligibilityGate.ts");
const types = read("src/astrology/sources/aiEligibilityTypes.ts");
const debugPage = read("src/app/report-provenance-debug/page.tsx");
const packageJson = read("package.json");

assert(types.includes("AiEligibilityPack"), "AiEligibilityPack type is missing.");
assert(types.includes("AiEligibleEvidenceItem"), "Eligible item type is missing.");
assert(types.includes("AiExcludedEvidenceItem"), "Excluded item type is missing.");
assert(types.includes("missing_citation_chain"), "Missing citation-chain reason is missing.");
assert(types.includes("needs_source"), "Needs-source exclusion reason is missing.");

assert(gate.includes("buildAiEligibilityPack"), "AI eligibility builder is missing.");
assert(gate.includes("provenance.coverage === \"verified\""), "Gate must require verified coverage.");
assert(gate.includes("item.available"), "Gate must reject unavailable evidence.");
assert(gate.includes("getSource(passage.sourceId)?.status === \"verified\""), "Gate must require verified source.");
assert(gate.includes("rule.status === \"verified\""), "Gate must require verified rule.");
assert(gate.includes("passage.status === \"verified\""), "Gate must require verified passage.");
assert(gate.includes("eligibleItems"), "Gate must produce eligible items.");
assert(gate.includes("excludedItems"), "Gate must produce excluded items.");
assert(!gate.includes("fetch("), "Gate must not call network APIs.");
assert(!gate.includes("OpenAI"), "Gate must not call AI.");
assert(!gate.includes("prompt"), "Gate must not build prompts.");
assert(!gate.includes("Сгенерировать"), "Gate must not expose generation.");

assert(debugPage.includes("buildAiEligibilityPack"), "Debug route must expose eligibility only behind debug guard.");
assert(debugPage.includes("debugRoutesEnabled"), "Debug route guard is missing.");
assert(debugPage.includes('redirect("/charts")'), "Production debug redirect is missing.");
assert(packageJson.includes("\"test:ai-eligibility\""), "test:ai-eligibility script is missing.");

if (process.exitCode) process.exit(process.exitCode);
console.log("AI eligibility gate check passed.");
