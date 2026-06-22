import { readFileSync } from "node:fs";

function read(path) {
  return readFileSync(new URL(path, import.meta.url), "utf8");
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const packageJson = read("../package.json");
const chartsPage = read("../src/app/charts/page.tsx");
const detailPage = read("../src/app/charts/[id]/page.tsx");
const fixture = read("../src/astrology/d1-workbench-smoke-fixture.ts");
const component = read("../src/ui/d1-workbench/D1ChartWorkbench.tsx");

for (const marker of [
  "test:chart-detail-smoke",
  "check-chart-detail-smoke.mjs",
]) {
  assert(packageJson.includes(marker), `Missing package chart detail smoke script marker: ${marker}`);
}

for (const marker of [
  "D1_WORKBENCH_SMOKE_CHART_ID",
  "D1_WORKBENCH_SMOKE_ROUTE",
  "D1_WORKBENCH_SMOKE_INTERNAL_MARKER",
  "D1_WORKBENCH_POLISH_STAGE",
  "D1_WORKBENCH_SMOKE_USER_STATUS",
  "buildD1WorkbenchSmokeModel",
  "P107-A",
  "E108-A",
  "\u041f\u0440\u0438\u043c\u0435\u0440 D1",
  "\u0442\u043e\u043b\u044c\u043a\u043e \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440",
  "\u043d\u0435 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u0430\u044f \u043a\u0430\u0440\u0442\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f",
  "south_indian",
  "grahas:",
  "ascendant:",
  "houses:",
]) {
  assert(fixture.includes(marker), `Missing smoke fixture contract marker: ${marker}`);
}

for (const marker of [
  "isSmokeDemoChart",
  "buildD1WorkbenchSmokeModel()",
  "D1_WORKBENCH_SMOKE_USER_STATUS",
  "D1_WORKBENCH_POLISH_STAGE",
  "readOnlyFixture",
  "D1_WORKBENCH_SMOKE_ROUTE",
]) {
  assert(detailPage.includes(marker), `Missing chart detail smoke route marker: ${marker}`);
}

for (const marker of [
  "data-chart-detail-smoke-fixture",
  "data-chart-detail-polish-stage",
  "data-chart-demo-kind",
  "d1-readonly-fixture-badge",
  "\u041f\u0440\u0438\u043c\u0435\u0440 D1",
  "\u0442\u043e\u043b\u044c\u043a\u043e \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440",
  "readOnlyFixture",
]) {
  assert(component.includes(marker), `Missing workbench smoke render hook: ${marker}`);
}

for (const marker of [
  "D1_WORKBENCH_SMOKE_ROUTE",
  "P107-A",
  "E108-A",
  "data-chart-demo-path",
  "\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0440\u0438\u043c\u0435\u0440 D1",
  "\u041f\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u043f\u0440\u0438\u043c\u0435\u0440",
]) {
  assert(chartsPage.includes(marker), `Missing charts dashboard smoke/demo open path marker: ${marker}`);
}

for (const forbiddenVisible of [
  ">P107-A read-only D1 demo<",
  ">P107-A read-only fixture<",
  'display_name: "P107-A',
]) {
  assert(![fixture, component, chartsPage].join("\n").includes(forbiddenVisible), `Internal marker is still primary visible copy: ${forbiddenVisible}`);
}

for (const forbidden of [
  "source.pending",
  "rawEvidence",
  "JHora",
  "Parashara Light",
  "ready for release",
  "release ready",
  "verified parity",
  "parity success",
  "OPENAI_API_KEY",
  "sk-",
]) {
  assert(![fixture, detailPage, component, chartsPage].join("\n").includes(forbidden), `Forbidden chart detail smoke marker: ${forbidden}`);
}

console.log("Chart detail smoke contract check passed.");
