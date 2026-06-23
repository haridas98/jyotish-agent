import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const exists = (file) => fs.existsSync(path.join(root, file));

const failures = [];
function assert(condition, message) {
  if (!condition) failures.push(message);
}

const requiredFiles = [
  "src/astrology/d1-workbench.ts",
  "src/ui/d1-workbench/D1ChartWorkbench.tsx",
  "src/ui/d1-workbench/index.ts",
  "docs/d1_workbench_calculation_inventory.md",
];

for (const file of requiredFiles) assert(exists(file), `Missing ${file}`);

const page = read("src/app/charts/[id]/page.tsx");
assert(page.includes("\u041a\u0430\u0440\u0442\u0430 D1"), "chart detail initial shell must render chart title");
assert(page.includes("\u0421\u0442\u0438\u043b\u044c \u043a\u0430\u0440\u0442\u044b"), "chart detail initial shell must render style label");
assert(page.includes("\u0420\u0435\u0436\u0438\u043c"), "chart detail initial shell must render mode label");
assert(page.includes("\u041e\u0431\u044a\u044f\u0441\u043d\u0435\u043d\u0438\u0435"), "chart detail initial shell must render inspector label");
assert(!page.includes("\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u044e \u043a\u0430\u0440\u0442\u0443..."), "chart detail must not be only old loading text");
assert(page.includes("D1ChartWorkbench"), "chart detail must use D1ChartWorkbench");

if (exists("src/astrology/d1-workbench.ts")) {
  const model = read("src/astrology/d1-workbench.ts");
  assert(model.includes('schemaVersion: "d1-workbench.v1"'), "D1 model must expose schemaVersion");
  assert(model.includes("buildD1WorkbenchModel"), "D1 adapter missing");
  assert(model.includes('CHART_WORKBENCH_SCOPE_IDS = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]'), "Workbench model must expose one supported scope registry");
  assert(model.includes("buildScopeSource"), "Workbench model must normalize D1, D3, D7, D9, D10 and D12 through one scope source");
  assert(model.includes("vargas?.[scopeId]"), "Varga scopes must come from indexed saved varga payload");
  assert(model.includes("VARGA_SCOPE_TITLES"), "Varga scope labels must come from one title registry");
  assert(model.includes('CHART_WORKBENCH_EXPERT_SCOPE_IDS = ["D30", "D60"]'), "D30 must be marked as astrologer-only scope");
  for (const code of ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]) {
    assert(model.includes(`${code}:`), `${code} must be registered in the workbench title map`);
  }
  assert(model.includes("specialPoints"), "D1 model must separate special points from grahas");
  assert(model.includes("point.LAGNA"), "D1 model must use point.LAGNA for Lagna");
  assert(!model.includes('Ascendant: { code: "AS", entityId: "house.1"'), "Lagna must not be modeled as house.1 graha row");
  assert(model.includes("chartObjectCount"), "D1 model must expose total chart object count");
  assert(model.includes("technical:"), "D1 model must expose technical calculation payload");
  assert(model.includes("buildTechnicalPayload"), "D1 model must normalize panchanga, dashas, vargas, house cusps and classical payload");
  assert(model.includes('scope.code === "D1"'), "D1 technical varga summary must treat the base D1 chart as available");
  assert(model.includes("chart.grahas.length + (chart.ascendant ? 1 : 0)"), "D1 technical varga summary must count D1 grahas plus Lagna");
  assert(model.includes("speedLongitude"), "D1 graha rows must expose speed_longitude for technical review");
  assert(model.includes("absoluteLongitude"), "D1 graha rows must expose absolute longitude for technical review");
  assert(model.includes("grahaEntityId"), "D1 graha entity ids missing");
  assert(model.includes("houseEntityId"), "D1 house entity ids missing");
  assert(model.includes("rashiEntityId"), "D1 rashi entity ids missing");
  assert(model.includes("sort("), "D1 model must sort rows deterministically");
  assert(!/calculate(?:House|Nakshatra|Dasha|Varga)\s*\(/.test(model), "D1 adapter must not calculate astrology formulas");
}

if (exists("src/ui/d1-workbench/D1ChartWorkbench.tsx")) {
  const component = read("src/ui/d1-workbench/D1ChartWorkbench.tsx");
  const inspectorRenderCount = (component.match(/<EntityInspector/g) ?? []).length;
  assert(inspectorRenderCount === 1, "D1 workbench must render exactly one EntityInspector");
  assert(component.includes("specialPointsForHouse"), "D1 workbench must render special points separately from grahas");
  assert(component.includes("onScopeChange"), "D1-D60 workbench scopes must switch through the same component");
  assert(component.includes("model.supportedScopes"), "Workbench must render scopes from API-supported registry data");
  assert(component.includes("model.vargaScopes"), "Workbench must group scopes from API varga scope metadata");
  assert(component.includes("availableScopeGroupsForMode"), "Workbench must filter grouped expert-only scopes by reader mode");
  assert(component.includes('mode === "astrologer" || !expert.has(scope.code)'), "Novice selector must hide expert-only D30/D60 scopes");
  assert(component.includes('mode === "astrologer"'), "Astrologer selector must allow expert-only D30/D60 scopes");
  const modelSource = read("src/astrology/d1-workbench.ts");
  assert(modelSource.includes("d30_time_precision"), "D30 workbench must show time precision warning");
  assert(modelSource.includes("d60_birth_time_accuracy"), "D60 workbench must show exact birth-time warning");
  assert(component.includes("terminologyMode"), "D1 workbench must keep terminology mode in shared state");
  assert(component.includes("activeTab"), "D1 workbench must keep active data tab in shared state");
  assert(component.includes("chartStyle === \"north\"") && component.includes("chartStyle === \"south\""), "D1 workbench must support north/south style toggle");
  assert(component.includes("TechnicalPayloadPanel"), "D1 workbench must render a technical payload panel");
  assert(component.includes("InternalJsonSnapshot"), "D1 workbench must expose an internal JSON snapshot for reviewer debugging");
  assert(component.includes("D1TechnicalContextStrip"), "D1 workbench must render a technical context strip before the chart grid");
  assert(component.includes('data-d1-technical-context-stage="E137-A"'), "D1 technical context strip must expose the E137 marker");
  assert(component.includes("chart_viewer_scope_coverage_visible=true"), "D1 technical context strip must expose scope coverage status");
  assert(component.includes("chart_viewer_accuracy_gate_visible=true"), "D1 technical context strip must expose accuracy gate status");
  assert(component.includes("D1LaunchVisibilityStrip"), "D1 workbench must render a visible technical launch summary strip");
  assert(component.includes('data-d1-launch-visibility-stage="E140-A"'), "D1 launch visibility strip must expose the E140 marker");
  assert(component.includes("chart_viewer_visible_technical_scope_summary=true"), "D1 launch strip must expose visible technical scope summary status");
  assert(component.includes("chart_viewer_first_check_before_analysis_review=true"), "D1 launch strip must expose first-check-before-analysis status");
  assert(component.includes('activeTab: "grahas"'), "D1 workbench first viewport must default to the graha table");
  assert(component.includes("chart_viewer_all_planets_visible_first_view=true"), "D1 workbench must expose first-view all-planets marker");
  assert(component.includes("last_verified_deploy_commit=cc86830c"), "D1 workbench current launch markers must reference the latest verified production checkpoint");
  assert(component.includes("D1MobileWorkflowNav"), "D1 workbench must expose a mobile chart/table/inspector workflow nav");
  assert(component.includes('data-d1-mobile-workflow-stage="E139-A"'), "D1 mobile workflow nav must expose the E139 marker");
  assert(component.includes("d1-first-viewport-grid"), "D1 workbench must group chart and graha table in the first viewport grid");
  assert(component.includes('data-d1-first-viewport-stage="E141-A"'), "D1 first viewport grid must expose the E141 marker");
  assert(component.includes("chart_viewer_chart_and_graha_table_same_viewport=true"), "D1 first viewport marker must require chart and graha table in one viewport");
  assert(component.includes('href="#d1-chart-panel"') && component.includes('href="#d1-data-panel"') && component.includes('href="#d1-inspector-panel"'), "D1 mobile workflow nav must link chart, grahas, and inspector anchors");
  assert(component.includes('id="d1-chart-panel"') && component.includes('id="d1-data-panel"') && component.includes('id="d1-inspector-panel"'), "D1 workbench must expose stable chart, data, and inspector anchors");
  assert(component.includes("d1-graha-table-card"), "D1 graha table must expose a mobile compact-row class");
  assert(component.includes('data-label="Graha"') && component.includes('data-label="Rashi"') && component.includes('data-label="House"'), "D1 graha table must expose mobile row labels");
  assert(component.includes("graha.speedLongitude"), "D1 graha table must render speed longitude when available");
  assert(component.includes("graha.absoluteLongitude"), "D1 graha table must render absolute longitude when available");
  for (const marker of [
    'data-technical-section="settings"',
    'data-technical-section="panchanga"',
    'data-technical-section="dashas"',
    'data-technical-section="vargas"',
    'data-technical-section="house-cusps"',
    'data-technical-section="classical"',
  ]) {
    assert(component.includes(marker), `D1 technical panel missing marker: ${marker}`);
  }
  assert(component.includes("SOUTH_SIGN_GRID"), "South Indian chart must use a named sign-fixed grid map");
  assert(component.includes("SOUTH_SIGN_ORDER"), "South Indian chart must render signs in deterministic sign order");
  assert(component.includes("SOUTH_SIGN_LABELS"), "South Indian chart must expose fixed rashi/sign labels");
  assert(component.includes("grahasForRashi"), "South Indian chart must place grahas by rashi, not house position");
  assert(component.includes("specialPointsForRashi"), "South Indian chart must place Lagna/special points by rashi, not house position");
  assert(component.includes("data-south-sign-fixed"), "South Indian cells must expose sign-fixed markers");
  assert(component.includes("d1-lagna-marker"), "South Indian chart must render a clear Lagna marker");
  assert(component.includes("North = house-fixed") && component.includes("South = sign-fixed"), "D1 workbench must explain the North/South layout distinction");
  assert(component.includes("mode === \"novice\"") && component.includes("mode === \"astrologer\""), "D1 workbench must support novice/astrologer mode");
  assert(!/calculate(?:House|Nakshatra|Dasha|Varga)\s*\(/.test(component), "React component must not calculate astrology formulas");
  for (const forbidden of ["AI", "source.pending", "Missing calculations", "Block is not registered yet"]) {
    assert(!component.includes(forbidden), `D1 workbench leaks forbidden marker: ${forbidden}`);
  }
}

if (exists("src/app/settings/page.tsx")) {
  const settingsPage = read("src/app/settings/page.tsx");
  assert(settingsPage.includes("CHART_WORKBENCH_SCOPE_IDS"), "Settings D-chart list must be synchronized with Workbench scope registry");
  assert(settingsPage.includes('from "@/astrology/d1-workbench"'), "Settings must import the shared Workbench scope registry");
  assert(settingsPage.includes("CHART_WORKBENCH_EXPERT_SCOPE_IDS"), "Settings must know expert-only vargas");
  assert(!settingsPage.includes("[\"D1\", \"D9\", \"D10\", \"D60\"] as const"), "Settings must not keep the old hardcoded D1/D9/D10/D60 list");
}

if (failures.length) {
  console.error("D1 workbench check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("D1 workbench check passed.");
