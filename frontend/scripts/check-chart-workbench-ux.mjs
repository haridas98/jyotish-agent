import { readFileSync } from "node:fs";

function read(path) {
  return readFileSync(new URL(path, import.meta.url), "utf8");
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const page = read("../src/app/charts/[id]/page.tsx");
const component = read("../src/ui/d1-workbench/D1ChartWorkbench.tsx");
const model = read("../src/astrology/d1-workbench.ts");
const css = read("../src/app/globals.css");
const combined = [page, component, model, css].join("\n");

for (const marker of ["Рћ", "Рљ", "РЎ", "Рџ", "Р’", "В·", "В°", "�"]) {
  assert(!combined.includes(marker), `Mojibake marker found: ${marker}`);
}

for (const text of ["Северный", "Южный", "Новичок", "Астролог", "RU", "EN", "SA", "Кратко", "Обычный", "Компактный"]) {
  assert(component.includes(text), `Missing chart workbench UX control text: ${text}`);
}

for (const scope of ["D1", "D9", "D10", "D30", "D60"]) {
  assert(combined.includes(scope), `Missing scope marker: ${scope}`);
}

for (const required of [
  "SouthChart",
  "NorthChart",
  "SOUTH_SIGN_GRID",
  "SOUTH_SIGN_ORDER",
  "SOUTH_SIGN_LABELS",
  "SOUTH_GRID",
  "NORTH_POSITIONS",
  "North = house-fixed",
  "South = sign-fixed",
  "data-south-sign-fixed",
  "d1-lagna-marker",
  "grahasForRashi",
  "specialPointsForRashi",
  "EntityInspector",
  "onScopeChange",
  "fetchD1ChartWorkbench(profileId, scope)",
  "density",
  "comfortable",
  "compact",
  "data-density",
  "d1-workbench-compact",
  "data-chart-detail-polish-stage",
  "data-chart-demo-kind",
  "E108-A",
  "\u041f\u0440\u0438\u043c\u0435\u0440 D1",
  "\u0442\u043e\u043b\u044c\u043a\u043e \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440",
]) {
  assert(combined.includes(required), `Missing required chart workbench contract: ${required}`);
}

for (const oldVisibleText of [">P107-A read-only fixture<", "P107-A read-only D1 demo"]) {
  assert(!component.includes(oldVisibleText), `Internal smoke marker must not be primary visible workbench copy: ${oldVisibleText}`);
}

for (const forbidden of [
  "source.pending",
  "rawEvidence",
  "Missing calculations",
  "PrivateHistoryPage",
  "Сгенерировать AI",
  "Спросить AI",
]) {
  assert(!combined.includes(forbidden), `Forbidden chart workbench marker: ${forbidden}`);
}

assert(component.match(/<EntityInspector/g)?.length === 1, "Chart workbench must render exactly one EntityInspector.");
assert(component.includes('mode === "novice" && model.expertOnlyScopes.includes(model.scopeId)'), "Novice mode must leave expert-only scope.");
assert(css.includes("@media") && css.includes(".d1-workbench[data-density=\"compact\"]"), "Chart workbench CSS must include compact and responsive rules.");

console.log("Chart workbench UX check passed.");
