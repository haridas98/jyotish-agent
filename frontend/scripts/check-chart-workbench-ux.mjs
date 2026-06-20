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
  "SOUTH_GRID",
  "NORTH_POSITIONS",
  "EntityInspector",
  "onScopeChange",
  "fetchD1ChartWorkbench(profileId, scope)",
  "density",
  "comfortable",
  "compact",
  "data-density",
  "d1-workbench-compact",
]) {
  assert(combined.includes(required), `Missing required chart workbench contract: ${required}`);
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
