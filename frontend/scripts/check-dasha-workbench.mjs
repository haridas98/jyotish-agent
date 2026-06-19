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
assert(page.includes("Даши"), "/dashas must render the Dasha workspace title");
assert(page.includes("Вимшоттари"), "/dashas must expose Vimshottari as the first supported system");
assert(page.includes("Махадаша"), "/dashas must show Mahadasha as primary reading layer");
assert(page.includes("Антардаша"), "/dashas must reserve Antardasha as secondary reading layer");
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
