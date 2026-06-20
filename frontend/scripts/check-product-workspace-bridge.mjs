import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function readPage(path) {
  return readFileSync(new URL(path, import.meta.url), "utf8");
}

function assertIncludes(page, values, label) {
  for (const value of values) {
    assert(page.includes(value), `${label} missing: ${value}`);
  }
}

function assertClean(page, label) {
  for (const forbidden of [
    "source.pending",
    "Missing calculations",
    "Block is not registered yet",
    "rawEvidence",
    "sourceRuleIds",
    "ownerUserId",
    "pairKey",
    "Р С™",
    "Р вЂ™",
    "Р Сџ",
  ]) {
    assert(!page.includes(forbidden), `${label} contains forbidden marker: ${forbidden}`);
  }
}

const people = readPage("../src/app/people/page.tsx");
const interactions = readPage("../src/app/interactions/page.tsx");
const reports = readPage("../src/app/reports/page.tsx");

assertIncludes(
  people,
  [
    "workspace-bridge-summary",
    "workspace-bridge-actions",
    "people-card-actions",
    "people-relationship-actions",
    "href=\"/charts/new\"",
    "href=\"/charts\"",
    "href=\"/interactions\"",
    "href=\"/reports\"",
    "href=\"/transits\"",
    "href={`/charts/${profile.id}`}",
    "href={`/charts/${profile.id}/edit`}",
  ],
  "people workspace bridge",
);

assertIncludes(
  interactions,
  [
    "workspace-bridge-summary",
    "workspace-bridge-actions",
    "interaction-readiness",
    "interaction-saved-actions",
    "href=\"/people\"",
    "href=\"/charts/new\"",
    "href=\"/reports\"",
    "href=\"/compatibility\"",
    "href=\"/transits\"",
  ],
  "interactions workspace bridge",
);

assertIncludes(
  reports,
  [
    "workspace-bridge-summary",
    "workspace-bridge-actions",
    "report-readiness",
    "href=\"/charts/new\"",
    "href=\"/people\"",
    "href=\"/interactions\"",
    "href=\"/transits\"",
  ],
  "reports workspace bridge",
);

assertIncludes(
  readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8"),
  ["workspace-bridge-summary", "workspace-bridge-actions", "people-card-actions"],
  "workspace bridge css",
);

assertClean(people, "people page");
assertClean(interactions, "interactions page");
assertClean(reports, "reports page");

console.log("Product workspace bridge check passed.");
