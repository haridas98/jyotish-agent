import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const roots = ["src/app", "src/ui"];
const patterns = [
  { id: "varga_copy", re: /\bD(?:1|3|7|9|10|12|20|24|30|60)\b|Навамша|Шаштьямша|карта брака|карма/iu },
  { id: "tutorial_copy", re: /что астролог|минимум|обучение|пояснение|подсказк|MVP|архитектур/iu },
  { id: "placement_copy", re: /Солнце в|Луна в|Марс в|Sun in|Moon in|Saturn in/iu },
  { id: "duplicated_ai_blocks", re: /AI-разбор|Codex совместимость|создать обзор|история обзоров/iu },
];

const ignored = new Set([
  "src/ui/components/EntityInspector.tsx",
  "src/astrology/entities/core.ts",
  "src/astrology/legacy/migration.ts",
]);

const findings = [];

for (const root of roots) {
  for (const file of walk(root)) {
    const rel = normalize(relative(process.cwd(), file));
    if (ignored.has(rel)) continue;
    if (!/\.(tsx?|css)$/.test(file)) continue;
    const lines = readFileSync(file, "utf8").split(/\r?\n/);
    lines.forEach((line, index) => {
      patterns.forEach((pattern) => {
        if (pattern.re.test(line)) {
          findings.push({
            file: rel,
            line: index + 1,
            pattern: pattern.id,
            text: line.trim().slice(0, 180),
          });
        }
      });
    });
  }
}

console.log(JSON.stringify({ status: "advisory", count: findings.length, findings: findings.slice(0, 80) }, null, 2));

function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    if (entry === "node_modules" || entry === ".next" || entry === "graphify-out") continue;
    const path = join(dir, entry);
    const stat = statSync(path);
    if (stat.isDirectory()) {
      yield* walk(path);
    } else {
      yield path;
    }
  }
}

function normalize(path) {
  return path.replaceAll("\\", "/");
}
