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
  assert(model.includes('scopeId: "D1" | "D9" | "D10"'), "Workbench model must support D1/D9/D10 scope union");
  assert(model.includes("buildScopeSource"), "Workbench model must normalize D1, D9 and D10 through one scope source");
  assert(model.includes("vargas?.D9"), "D9 must come from saved varga payload");
  assert(model.includes("vargas?.D10"), "D10 must come from saved varga payload");
  assert(model.includes("specialPoints"), "D1 model must separate special points from grahas");
  assert(model.includes("point.LAGNA"), "D1 model must use point.LAGNA for Lagna");
  assert(!model.includes('Ascendant: { code: "AS", entityId: "house.1"'), "Lagna must not be modeled as house.1 graha row");
  assert(model.includes("chartObjectCount"), "D1 model must expose total chart object count");
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
  assert(component.includes("onScopeChange"), "D1/D9/D10 workbench must switch scope through the same component");
  assert(component.includes('model.scopeId === "D9"'), "Workbench must expose D9 through the same shell");
  assert(component.includes('model.scopeId === "D10"'), "Workbench must expose D10 through the same shell");
  assert(component.includes("terminologyMode"), "D1 workbench must keep terminology mode in shared state");
  assert(component.includes("activeTab"), "D1 workbench must keep active data tab in shared state");
  assert(component.includes("chartStyle === \"north\"") && component.includes("chartStyle === \"south\""), "D1 workbench must support north/south style toggle");
  assert(component.includes("mode === \"novice\"") && component.includes("mode === \"astrologer\""), "D1 workbench must support novice/astrologer mode");
  assert(!/calculate(?:House|Nakshatra|Dasha|Varga)\s*\(/.test(component), "React component must not calculate astrology formulas");
  for (const forbidden of ["AI", "D60", "source.pending", "Missing calculations", "Block is not registered yet"]) {
    assert(!component.includes(forbidden), `D1 workbench leaks forbidden marker: ${forbidden}`);
  }
}

if (failures.length) {
  console.error("D1 workbench check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("D1 workbench check passed.");