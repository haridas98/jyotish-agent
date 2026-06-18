import { readFileSync } from "node:fs";

function read(path) {
  return readFileSync(path, "utf8");
}

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exitCode = 1;
  }
}

const files = {
  requestTypes: read("src/astrology/sources/aiRequestTypes.ts"),
  requestBuilder: read("src/astrology/sources/aiRequestBuilder.ts"),
  responseTypes: read("src/astrology/sources/aiResponseTypes.ts"),
  responseValidation: read("src/astrology/sources/aiResponseValidation.ts"),
  mockProvider: read("src/astrology/sources/mockAiProvider.ts"),
  index: read("src/astrology/sources/index.ts"),
  packageJson: read("package.json"),
};

for (const marker of [
  "AiReportRequest",
  "schemaVersion: 1",
  "eligibleItemIds",
  "citationChains",
  "excludedSummary",
]) {
  assert(files.requestTypes.includes(marker), `AI request types missing ${marker}`);
}

for (const marker of [
  "buildAiReportRequest",
  "eligibilityPack.eligibleItems",
  "excludedSummary",
  "sortAiRequestItems",
]) {
  assert(files.requestBuilder.includes(marker), `AI request builder missing ${marker}`);
}

assert(!files.requestBuilder.includes("eligibilityPack.excludedItems.map"), "Request builder must not map excluded items into the request body.");
assert(!files.requestBuilder.includes("value: item.value"), "Request builder must not include raw values as thesis material yet.");

for (const marker of [
  "AiReportResponse",
  "AiReportThesis",
  "evidenceItemIds",
  "citations",
  "confidence",
]) {
  assert(files.responseTypes.includes(marker), `AI response types missing ${marker}`);
}

for (const marker of [
  "validateAiReportResponse",
  "unknown evidence item",
  "missing citation chain",
  "schemaVersion",
]) {
  assert(files.responseValidation.includes(marker), `AI response validation missing ${marker}`);
}

for (const marker of [
  "runMockAiDryRun",
  "validateAiReportResponse",
  "request.items.map",
  "provider: \"mock\"",
]) {
  assert(files.mockProvider.includes(marker), `Mock provider missing ${marker}`);
}

for (const forbidden of [
  "fetch(",
  "OpenAI",
  "process.env.OPENAI",
  "requestCodexAnalysis",
  "requestCompatibilityCodexAnalysis",
  "Сгенерировать",
  "Спросить AI",
]) {
  for (const [name, content] of Object.entries(files)) {
    if (name === "packageJson") continue;
    assert(!content.includes(forbidden), `${name} must not contain ${forbidden}`);
  }
}

assert(files.index.includes("./aiRequestBuilder"), "Sources index must export AI request builder.");
assert(files.index.includes("./aiResponseValidation"), "Sources index must export AI response validation.");
assert(files.index.includes("./mockAiProvider"), "Sources index must export mock AI provider.");
assert(files.packageJson.includes("\"test:ai-contract\""), "package.json must expose test:ai-contract.");

if (process.exitCode) process.exit(process.exitCode);
console.log("AI request/response offline dry-run contract check passed.");
