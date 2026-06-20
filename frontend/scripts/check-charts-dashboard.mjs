import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const page = readFileSync(new URL("../src/app/charts/page.tsx", import.meta.url), "utf8");

for (const text of [
  "Кабинет карт",
  "Всего карт",
  "Моя карта",
  "Последнее обновление",
  "Создать карту",
  "Люди",
  "Обзор",
  "Взаимодействия",
  "Транзиты",
  "Открыть",
  "Редактировать",
]) {
  assert(page.includes(text), `Missing dashboard text/action: ${text}`);
}

for (const route of ["/charts/new", "/people", "/reports", "/interactions", "/transits"]) {
  assert(page.includes(`href="${route}"`) || page.includes(`href={\`${route}`), `Missing quick route: ${route}`);
}

assert(page.includes("charts-summary-grid"), "Charts dashboard summary grid is missing.");
assert(page.includes("charts-quick-actions"), "Charts dashboard quick actions are missing.");
assert(page.includes("chart-profile-card-actions"), "Chart card actions are missing.");

for (const forbidden of ["Рљ", "Р’", "Рџ", "source.pending", "Missing calculations", "rawEvidence"]) {
  assert(!page.includes(forbidden), `Forbidden marker in charts page: ${forbidden}`);
}

console.log("Charts dashboard check passed.");
