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

if (failed) {
  process.exit(1);
}

console.log("Production browser bundle check passed.");
