import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const targets = [".next/static", "public", "out", "dist"].filter((target) => existsSync(target));
const forbidden = [
  /https?:\/\/localhost/i,
  /localhost:\d+/i,
  /127\.0\.0\.1/,
  /http:\/\/31\./,
  /http:\/\/[^"'\s]+:18100/,
  /NEXT_PUBLIC_API_BASE_URL=http/,
  /31\.76\.79\.2/,
];
const sourceTargets = [
  "src/ui/components",
  "src/astrology/entities",
  "src/astrology/relationships",
  "src/app/app-navigation.tsx",
  "src/app/charts/[id]/page.tsx",
  "src/app/sources/page.tsx",
].filter((target) => existsSync(target));
const forbiddenSourceMarkers = [
  /source\.pending/,
  /Block is not registered yet/,
  /Missing calculations/,
  /D9\s+[—-]\s+карта брака/i,
  /D9 отвечает за семью/i,
  /D60\s+[—-]\s+карта кармы/i,
  /relationship\.goodCompatibility/,
  /relationship\.badCompatibility/,
  /relationship\.karmicConnection/,
  /relationship\.moonRelationship/,
  /requiredCalculationIds:\s*\[[^\]]*D60/,
  /primaryEntityIds:\s*\[[^\]]*varga\.D60/,
];

if (!targets.length) {
  console.error("No browser bundle directories found.");
  process.exit(1);
}

function* files(root) {
  for (const name of readdirSync(root)) {
    const path = join(root, name);
    const stats = statSync(path);
    if (stats.isDirectory()) {
      yield* files(path);
    } else if (stats.isFile()) {
      yield path;
    }
  }
}

let failed = false;
for (const target of targets) {
  for (const file of files(target)) {
    let content = "";
    try {
      content = readFileSync(file, "utf8");
    } catch {
      continue;
    }
    for (const pattern of forbidden) {
      if (pattern.test(content)) {
        console.error(`Forbidden browser reference found: ${pattern} in ${file}`);
        failed = true;
      }
    }
  }
}

for (const target of sourceTargets) {
  const targetFiles = statSync(target).isDirectory() ? files(target) : [target];
  for (const file of targetFiles) {
    if (!/\.(tsx?|css)$/.test(file)) continue;
    const content = readFileSync(file, "utf8");
    for (const pattern of forbiddenSourceMarkers) {
      if (pattern.test(content)) {
        console.error(`Forbidden UI marker found: ${pattern} in ${file}`);
        failed = true;
      }
    }
  }
}

if (failed) {
  process.exit(1);
}

console.log("Production browser bundle check passed.");
