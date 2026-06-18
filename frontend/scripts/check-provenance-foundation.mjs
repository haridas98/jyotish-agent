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

const provenanceResolver = read("src/astrology/sources/provenanceResolver.ts");
const coverageResolver = read("src/astrology/sources/coverageResolver.ts");
const debugPage = read("src/app/report-provenance-debug/page.tsx");
const packageJson = read("package.json");

assert(provenanceResolver.includes("resolveEvidenceProvenance"), "resolveEvidenceProvenance is missing.");
assert(provenanceResolver.includes("ProvenanceEnrichedReportEvidence"), "ProvenanceEnrichedReportEvidence is missing.");
assert(provenanceResolver.includes("EvidenceProvenance"), "EvidenceProvenance is missing.");
assert(provenanceResolver.includes("ruleRefs"), "Rule refs are missing.");
assert(provenanceResolver.includes("passageRefs"), "Passage refs are missing.");
assert(provenanceResolver.includes("coverageSummary"), "Coverage summary is missing.");
assert(provenanceResolver.includes(".sort("), "Deterministic sorting is missing.");

assert(coverageResolver.includes('"verified"'), "Verified coverage is missing.");
assert(coverageResolver.includes('"partial"'), "Partial coverage is missing.");
assert(coverageResolver.includes('"needs_source"'), "Needs-source coverage is missing.");
assert(coverageResolver.includes('"unsupported"'), "Unsupported coverage is missing.");
assert(coverageResolver.includes("summarizeCoverage"), "Coverage summary resolver is missing.");

assert(debugPage.includes("debugRoutesEnabled"), "Debug route guard is missing.");
assert(debugPage.includes('redirect("/charts")'), "Production debug redirect is missing.");
assert(debugPage.includes("validateSourceRegistry"), "Debug route must show source validation in debug mode.");
assert(debugPage.includes("validatePassageRegistry"), "Debug route must show passage validation in debug mode.");
assert(debugPage.includes("validateRuleRegistry"), "Debug route must show rule validation in debug mode.");
assert(!debugPage.includes("OpenAI"), "Debug route must not call AI.");
assert(!debugPage.includes("Сгенерировать"), "Debug route must not expose generation.");

assert(packageJson.includes("\"test:provenance\""), "test:provenance script is missing.");

if (process.exitCode) process.exit(process.exitCode);
console.log("Provenance foundation check passed.");
