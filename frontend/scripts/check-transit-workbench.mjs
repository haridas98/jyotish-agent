import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const failures = [];
function assert(condition, message) {
  if (!condition) failures.push(message);
}

const page = read("src/app/transits/page.tsx");
const api = read("src/lib/api.ts");
const nav = read("src/app/app-navigation.tsx");

assert(page.includes('<ProductShell active="transits"'), "/transits must use shared ProductShell with active transits");
assert(!page.includes("PrivateHistoryPage"), "/transits must not be the old history page");
assert(page.includes("listChartProfiles"), "/transits must load saved charts");
assert(page.includes("fetchTransitWorkbench"), "/transits must load the transit workbench API");
assert(page.includes("D1ChartWorkbench"), "/transits must reuse existing D1/Chart Workbench renderer");
assert(!page.includes("TransitNorthChart") && !page.includes("TransitSouthChart"), "/transits must not define transit-specific chart renderers");
assert(page.includes("Натальная карта") && page.includes("Дата") && page.includes("Время") && page.includes("Часовой пояс") && page.includes("Место"), "/transits must expose moment controls");
assert(page.includes("Сейчас") && page.includes("Применить") && page.includes("Вернуться к текущему моменту"), "/transits must expose now/apply/current actions");
assert(page.includes("Стиль: Северный / Южный") && page.includes("Режим: Новичок / Астролог"), "/transits must expose chart style and mode affordances");
assert(page.includes("Термины: RU / EN / SA / Кратко"), "/transits must expose terminology modes");
assert(page.includes("Транзитная карта D1: факты без прогнозов, аспектов и AI."), "/transits must state factual-only scope");
assert(api.includes("fetchTransitWorkbench") && api.includes("/api/charts/${profileId}/transit-workbench"), "API client must expose chart-scoped transit workbench fetch");
assert(nav.includes("/transits"), "shared nav must include transits route");
for (const forbidden of ["Спросить AI", "Сгенерировать", "source.pending", "rawEvidence", "eligibleItems", "Missing calculations"]) {
  assert(!page.includes(forbidden), `/transits leaks forbidden marker: ${forbidden}`);
}

if (failures.length) {
  console.error("Transit workbench check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Transit workbench check passed.");