import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

const failures = [];
function assert(condition, message) {
  if (!condition) failures.push(message);
}

const page = read("src/app/dashas/page.tsx");
assert(!page.includes("redirect("), "/dashas must be a real page, not a redirect");
assert(page.includes("ProductShell"), "/dashas must use the shared product shell");
assert(page.includes("listChartProfiles"), "/dashas must load saved charts instead of static placeholders");
assert(page.includes("calculateSavedProfile"), "/dashas must use saved chart calculations as the data source");
assert(page.includes("viewMode"), "/dashas must support tree/table/timeline view mode");
assert(page.includes('"tree"') && page.includes('"table"') && page.includes('"timeline"'), "/dashas must expose tree, table, and timeline modes");
assert(page.includes("controlDate"), "/dashas must support a control date");
assert(page.includes("jumpToCurrentPeriod"), "/dashas must jump to the current period chain");
assert(page.includes("collapsedLevels"), "/dashas must support collapsing levels");
assert(page.includes("dasha-boundary"), "/dashas must render stable period boundaries");
assert(page.includes("dasha-period-table"), "/dashas must render table mode");
assert(page.includes("dasha-timeline"), "/dashas must render timeline mode");
assert(page.includes("mahadashas.map"), "/dashas must render real Mahadasha periods");
assert(page.includes("activeMahadasha"), "/dashas must highlight the selected/current Mahadasha");
assert(page.includes("selectedAntardashas.map"), "/dashas must render Antardashas for the selected Mahadasha");
assert(page.includes("activeAntardasha"), "/dashas must keep selected/current Antardasha for the third level");
assert(page.includes("selectedPratyantardashas.map"), "/dashas must render Pratyantardashas for the selected Antardasha");
assert(page.includes("pratyantardasha"), "/dashas must route Pratyantardasha clicks through the same inspector state");
assert(page.includes("selectedEntity"), "/dashas must use one EntityInspector state for period clicks");
assert(page.includes("dasha-period-tree"), "/dashas must expose a period tree layout");
assert(page.includes("dasha-period-row"), "/dashas must render clickable period rows");
assert(page.includes("aria-pressed"), "/dashas period rows must expose active state");
assert(page.includes("Вимшоттари"), "/dashas must expose Vimshottari as the active system");
assert(page.includes("Махадаша"), "/dashas must show Mahadasha as primary reading layer");
assert(page.includes("Антардаша"), "/dashas must show Antardasha as secondary reading layer");
assert(page.includes("Пратьянтардаша"), "/dashas must show Pratyantardasha as the third reading layer");
assert(page.includes("Объяснение"), "/dashas must keep one shared inspector area");

for (const forbidden of ["Спросить AI", "Сгенерировать", "source.pending", "rawEvidence", "eligibleItems"]) {
  assert(!page.includes(forbidden), `/dashas leaks forbidden marker: ${forbidden}`);
}

if (failures.length) {
  console.error("Dasha workbench check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Dasha workbench check passed.");