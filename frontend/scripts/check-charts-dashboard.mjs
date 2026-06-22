import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const page = readFileSync(new URL("../src/app/charts/page.tsx", import.meta.url), "utf8");

for (const text of [
  "\u041a\u0430\u0431\u0438\u043d\u0435\u0442 \u043a\u0430\u0440\u0442",
  "\u0412\u0441\u0435\u0433\u043e \u043a\u0430\u0440\u0442",
  "\u041c\u043e\u044f \u043a\u0430\u0440\u0442\u0430",
  "\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435",
  "\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043a\u0430\u0440\u0442\u0443",
  "\u041b\u044e\u0434\u0438",
  "\u041e\u0431\u0437\u043e\u0440",
  "\u0412\u0437\u0430\u0438\u043c\u043e\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f",
  "\u0422\u0440\u0430\u043d\u0437\u0438\u0442\u044b",
  "\u041e\u0442\u043a\u0440\u044b\u0442\u044c",
  "\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c",
]) {
  assert(page.includes(text), `Missing dashboard text/action: ${text}`);
}

for (const route of ["/charts/new", "/people", "/reports", "/interactions", "/transits"]) {
  assert(page.includes(`href="${route}"`) || page.includes(`href={\`${route}`), `Missing quick route: ${route}`);
}

assert(page.includes("charts-summary-grid"), "Charts dashboard summary grid is missing.");
assert(page.includes("charts-quick-actions"), "Charts dashboard quick actions are missing.");
assert(page.includes("chart-profile-card-actions"), "Chart card actions are missing.");
assert(page.includes("D1_WORKBENCH_SMOKE_ROUTE"), "Charts dashboard must expose the demo D1 route.");
assert(page.includes("data-chart-demo-path"), "Charts dashboard must keep a deterministic demo path hook.");
assert(page.includes("E108-A"), "Charts dashboard must keep the E108 polish marker as a hook.");
assert(page.includes("\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0440\u0438\u043c\u0435\u0440 D1"), "Charts dashboard must show product demo copy.");
assert(page.includes("\u041f\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u043f\u0440\u0438\u043c\u0435\u0440"), "Charts dashboard must show compact demo copy.");
assert(page.includes("hasLoadError"), "Charts dashboard must track API/auth load errors separately from empty saved charts.");
assert(page.includes("setProfiles([]);") && page.includes("setHasLoadError(true);"), "Charts dashboard error fallback must clear loaded profiles and expose demo affordance state.");
assert(page.includes("hasLoadError && !profiles.length"), "Charts dashboard must render a no-profiles fallback when API/auth probing fails.");
assert(page.includes('DemoD1Link label="\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0440\u0438\u043c\u0435\u0440 D1"'), "Charts dashboard error fallback must include the product demo D1 link.");
assert(!page.includes(">P107-A read-only D1 demo<"), "Internal P107 label must not be the visible demo button text.");

for (const forbidden of ["\u0420\u00a0\u0421\u2122", "\u0420\u00a0\u0432\u0402\u2122", "\u0420\u00a0\u0421\u045f", "source.pending", "Missing calculations", "rawEvidence"]) {
  assert(!page.includes(forbidden), `Forbidden marker in charts page: ${forbidden}`);
}

console.log("Charts dashboard check passed.");
