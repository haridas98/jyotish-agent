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

const sourceTypes = read("src/astrology/sources/sourceTypes.ts");
const passageTypes = read("src/astrology/sources/passageTypes.ts");
const ruleTypes = read("src/astrology/sources/ruleTypes.ts");
const sourceRegistry = read("src/astrology/sources/sourceRegistry.ts");
const passageRegistry = read("src/astrology/sources/passageRegistry.ts");
const ruleRegistry = read("src/astrology/sources/ruleRegistry.ts");
const sourceValidation = read("src/astrology/sources/sourceValidation.ts");
const passageValidation = read("src/astrology/sources/passageValidation.ts");
const ruleValidation = read("src/astrology/sources/ruleValidation.ts");
const sourcesPage = read("src/app/sources/page.tsx");
const packageJson = read("package.json");

assert(sourceTypes.includes("SourceDefinition"), "SourceDefinition is missing.");
assert(sourceTypes.includes("accessPolicy"), "Source access policy is missing.");
assert(sourceTypes.includes("referenceUrl"), "Source reference URL is missing.");
assert(passageTypes.includes("PassageDefinition"), "PassageDefinition is missing.");
assert(passageTypes.includes("PassageLocator"), "PassageLocator is missing.");
assert(ruleTypes.includes("RuleDefinition"), "RuleDefinition is missing.");
assert(ruleTypes.includes("RuleCondition"), "RuleCondition is missing.");
assert(ruleTypes.includes("graha_in_house"), "Typed rule conditions are missing.");

assert(sourceRegistry.includes("source.bphs"), "BPHS pilot source is missing.");
assert(sourceRegistry.includes("brihat_parashara_hora_shastra_english_v.pdf"), "Selected BPHS public edition URL is missing.");
assert(sourceRegistry.includes("metadata_only"), "Metadata-only policy is missing.");
assert(sourceRegistry.includes("locator_and_excerpt"), "Verified source locator/excerpt policy is missing.");
assert(sourceRegistry.includes("status: \"verified\""), "Selected BPHS source edition must be verified for 6C pilot citations.");
assert(passageRegistry.includes("passage.bphs.lagna.general"), "Lagna pilot passage is missing.");
assert(passageRegistry.includes("passage.bphs.moon.general"), "Moon pilot passage is missing.");
assert(passageRegistry.includes('chapter: "3", verseStart: "4", verseEnd: "9"'), "Lagna pilot needs exact BPHS chapter/verse locator.");
assert(passageRegistry.includes('chapter: "3", verseStart: "12", verseEnd: "13"'), "Sun/Moon pilot needs exact BPHS chapter/verse locator.");
assert(passageRegistry.includes('chapter: "6", verseStart: "2", verseEnd: "4"'), "Varga names pilot needs exact BPHS chapter/verse locator.");
assert(passageRegistry.includes('chapter: "7", verseStart: "1", verseEnd: "8"'), "Varga use pilot needs exact BPHS chapter/verse locator.");
assert(passageRegistry.includes('chapter: "46", verseStart: "2", verseEnd: "16"'), "Vimshottari pilot needs exact BPHS chapter/verse locator.");
assert(ruleRegistry.includes("bphs.house.1"), "House 1 pilot rule is missing.");
assert(ruleRegistry.includes("bphs.graha.mo"), "Moon pilot rule is missing.");
assert(ruleRegistry.includes("bphs.graha.su"), "Sun pilot rule is missing.");
assert(ruleRegistry.includes("jyotish.classical.varga.D1"), "D1 pilot rule is missing.");
assert(ruleRegistry.includes("jyotish.classical.varga.D9"), "D9 pilot rule is missing.");
assert(ruleRegistry.includes("vimshottari.sequence"), "Vimshottari pilot rule is missing.");
assert(/id:\s*"bphs\.house\.1"[\s\S]*?status:\s*"verified"/.test(ruleRegistry), "House 1 rule must be verified after exact citation mapping.");
assert(/id:\s*"bphs\.graha\.mo"[\s\S]*?status:\s*"verified"/.test(ruleRegistry), "Moon rule must be verified after exact citation mapping.");
assert(/id:\s*"bphs\.graha\.su"[\s\S]*?status:\s*"verified"/.test(ruleRegistry), "Sun rule must be verified after exact citation mapping.");
assert(/id:\s*"jyotish\.classical\.varga\.D1"[\s\S]*?status:\s*"verified"/.test(ruleRegistry), "D1 rule must be verified after exact citation mapping.");
assert(/id:\s*"jyotish\.classical\.varga\.D9"[\s\S]*?status:\s*"verified"/.test(ruleRegistry), "D9 rule must be verified after exact citation mapping.");
assert(/id:\s*"vimshottari\.sequence"[\s\S]*?status:\s*"verified"/.test(ruleRegistry), "Vimshottari rule must be verified after exact citation mapping.");

assert(sourceValidation.includes("validateSourceRegistry"), "Source validation is missing.");
assert(passageValidation.includes("references unknown source"), "Broken source reference validation is missing.");
assert(passageValidation.includes("needs verified source"), "Verified passage/source consistency validation is missing.");
assert(passageValidation.includes("needs chapter/verse or page locator"), "Precise verified locator validation is missing.");
assert(ruleValidation.includes("references unknown entity"), "Unknown entity validation is missing.");
assert(ruleValidation.includes("references unknown calculation"), "Unknown calculation validation is missing.");
assert(ruleValidation.includes("Verified rule"), "Verified rule validation is missing.");
assert(ruleValidation.includes("needs verified source"), "Verified rule/source consistency validation is missing.");
assert(!ruleRegistry.includes("Jagannatha Hora"), "Third-party software text must not be copied into rules.");
assert(!ruleRegistry.includes("Parashara's Light"), "Third-party software text must not be copied into rules.");
assert(!ruleRegistry.includes("AI prompt"), "Rules must not contain AI prompts.");
assert(!ruleRegistry.includes("source.pending"), "source.pending must not be used.");

assert(sourcesPage.includes("Source Explorer") === false, "English placeholder heading leaked into /sources.");
assert(sourcesPage.includes("Источники"), "/sources title is missing.");
assert(sourcesPage.includes("Шастры"), "/sources source panel is missing.");
assert(sourcesPage.includes("Места"), "/sources passage panel is missing.");
assert(sourcesPage.includes("Правила"), "/sources rule panel is missing.");
assert(sourcesPage.includes("Поиск"), "/sources search affordance is missing.");
assert(!sourcesPage.includes("будет подключена отдельным этапом"), "/sources is still a placeholder.");
assert(!sourcesPage.includes("source.pending"), "/sources must not expose source.pending.");
assert(!sourcesPage.includes("<dd>{source.id}</dd>"), "/sources normal UI must not render raw source IDs.");
assert(!sourcesPage.includes("<dd>{passage.id}</dd>"), "/sources normal UI must not render raw passage IDs.");
assert(!sourcesPage.includes("<dd>{rule.id}</dd>"), "/sources normal UI must not render raw rule IDs.");
assert(!sourcesPage.includes("checksum"), "/sources normal UI must not expose checksums.");

assert(packageJson.includes("\"test:sources\""), "test:sources script is missing.");

if (process.exitCode) process.exit(process.exitCode);
console.log("Source registry foundation check passed.");
