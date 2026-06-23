import { existsSync, readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function read(path) {
  assert(existsSync(path), `Missing file: ${path}`);
  return readFileSync(path, "utf8");
}

const moduleCache = new Map();

function loadTsModule(path) {
  if (moduleCache.has(path)) return moduleCache.get(path);
  const source = read(path);
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
      esModuleInterop: true,
      resolveJsonModule: true,
    },
  }).outputText;
  const module = { exports: {} };
  moduleCache.set(path, module.exports);
  function localRequire(specifier) {
    if (specifier === "@/lib/ai-review-benchmark") return loadTsModule("src/lib/ai-review-benchmark.ts");
    if (specifier === "@/lib/ai-review-benchmark-parity") return loadTsModule("src/lib/ai-review-benchmark-parity.ts");
    if (specifier === "@/data/ai-review-telegram-benchmark.json") return { default: JSON.parse(read("src/data/ai-review-telegram-benchmark.json")) };
    throw new Error(`Unsupported test loader import: ${specifier}`);
  }
  vm.runInNewContext(output, { exports: module.exports, module, require: localRequire, structuredClone }, { filename: path });
  return module.exports;
}

const packageJson = read("package.json");
assert(packageJson.includes('"test:ai-review-benchmark-parity"'), "package.json must expose test:ai-review-benchmark-parity.");

const parityPath = "src/lib/ai-review-benchmark-parity.ts";
const benchmarkPath = "src/lib/ai-review-benchmark.ts";
const qualityPath = "src/lib/ai-review-quality.ts";
const fixturePath = "src/data/ai-review-telegram-benchmark.json";
const docsPath = "../docs/ai_review_quality_reset.md";

const paritySource = read(parityPath);
const benchmarkSource = read(benchmarkPath);
const qualitySource = read(qualityPath);
const fixtureSource = read(fixturePath);
const docsSource = read(docsPath);
const parity = loadTsModule(parityPath);

assert(typeof parity.buildAiReviewBenchmarkParityReport === "function", "buildAiReviewBenchmarkParityReport must be exported.");

const report = parity.buildAiReviewBenchmarkParityReport();
assert(report.stage === "R2", "Parity report stage must be R2.");
assert(report.statusLabels.includes("ai_review_benchmark_parity_stage=R2"), "Missing R2 parity stage label.");
assert(report.statusLabels.includes("ai_review_benchmark_parity_present=true"), "Missing parity present label.");
assert(report.statusLabels.includes("ai_review_benchmark_d1_rows_checked>=18"), "Missing D1 rows checked label.");
assert(report.statusLabels.includes("ai_review_benchmark_unsupported_advanced_claims_gated=true"), "Missing unsupported advanced claims gated label.");
assert(report.statusLabels.includes("ai_review_benchmark_lagna_present=true"), "Missing Lagna present label.");
assert(report.statusLabels.includes("ai_review_benchmark_nakshatra_present=true"), "Missing nakshatra present label.");
assert(report.aggregate.d1RowsChecked >= 18, "Parity report must check at least 18 D1 rows.");
assert(report.aggregate.lagnaPresent === true, "Every benchmark case must include Lagna.");
assert(report.aggregate.requiredPlanetsPresent === true, "Required planets must be present when in R1 data.");
assert(report.aggregate.nakshatraPresent === true, "Every parity row must expose nakshatra or explicit missing marker.");
assert(report.aggregate.unsupportedAdvancedClaimsGated === true, "Unsupported advanced claims must be gated.");
assert(report.cases.length >= 2, "Parity report must cover at least two cases.");

for (const item of report.cases) {
  assert(item.lagna?.sign && item.lagna?.house === 1, `${item.caseId} must include Lagna sign and house.`);
  assert(item.rowsChecked >= 9, `${item.caseId} must check expected D1 rows.`);
  for (const planet of ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]) {
    assert(item.requiredPlanetPresence[planet] === true, `${item.caseId} missing required planet ${planet}.`);
  }
  for (const row of item.rowChecks) {
    assert(row.sign && typeof row.sign === "string", `${item.caseId}/${row.planet} missing sign.`);
    assert(row.nakshatra && typeof row.nakshatra === "string", `${item.caseId}/${row.planet} missing nakshatra marker.`);
  }
}

for (const claim of ["shadbala", "ashtakavarga", "avastha"]) {
  assert(
    report.unsupportedAdvancedClaims.some((item) => item.claim === claim && item.status === "gated_missing_calculation"),
    `Unsupported advanced claim must be gated: ${claim}`,
  );
}

assert(qualitySource.includes("buildAiReviewBenchmarkParityReport"), "ai-review-quality must expose parity status through quality summary.");
assert(qualitySource.includes("benchmarkParityReport"), "quality summary must include benchmarkParityReport.");

const runtimeSources = [
  { path: fixturePath, source: fixtureSource },
  { path: benchmarkPath, source: benchmarkSource },
  { path: parityPath, source: paritySource },
  { path: qualityPath, source: qualitySource },
  { path: docsPath, source: docsSource },
];
for (const fragment of [
  "ChatExport",
  "message default clearfix",
  "tgme_widget_message",
  "from_name",
  "Ваш баланс",
  "Энергия Света",
  "Выберите действие",
  '<div class="message',
  "<html",
  "Haridev",
  "Seva",
]) {
  for (const { path, source } of runtimeSources) {
    assert(!source.includes(fragment), `${path} leaked raw/private fragment: ${fragment}`);
  }
}

console.log("AI review benchmark parity check passed.");
