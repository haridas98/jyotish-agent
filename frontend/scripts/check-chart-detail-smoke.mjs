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
  "buildD1WorkbenchSmokeModel",
  "P107-A",
  "read-only D1 chart detail smoke fixture",
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
  "D1_WORKBENCH_SMOKE_STATUS",
  "readOnlyFixture",
  "D1_WORKBENCH_SMOKE_ROUTE",
]) {
  assert(detailPage.includes(marker), `Missing chart detail smoke route marker: ${marker}`);
}

for (const marker of [
  "data-chart-detail-smoke-fixture",
  "d1-readonly-fixture-badge",
  "readOnlyFixture",
]) {
  assert(component.includes(marker), `Missing workbench smoke render hook: ${marker}`);
}

for (const marker of [
  "D1_WORKBENCH_SMOKE_ROUTE",
  "P107-A",
]) {
  assert(chartsPage.includes(marker), `Missing charts dashboard smoke/demo open path marker: ${marker}`);
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
