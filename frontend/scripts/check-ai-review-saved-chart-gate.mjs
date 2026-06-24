import { existsSync, readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function readJson(path) {
  assert(existsSync(path), `Missing file: ${path}`);
  return JSON.parse(readFileSync(path, "utf8"));
}

const fixturePath = "src/data/ai-review-saved-chart-fixture.json";
const fixture = readJson(fixturePath);
const result = fixture.calculation?.result;

assert(fixture.fixtureKind === "saved_chart_workbench_fixture", "Fixture must be a saved-chart workbench fixture.");
assert(fixture.sourceRoute?.includes("/api/charts/") && fixture.sourceRoute.includes("/workbench?scope=d1"), "Fixture must name a saved-chart workbench path.");
assert(fixture.calculation?.status === "complete", "Saved-chart fixture calculation must be complete.");
assert(fixture.provenance?.rawWitnessArtifactsCommitted === false, "Fixture must not commit raw witness artifacts.");
assert(fixture.provenance?.publicQualityClaim === false, "Fixture must not make a public quality claim.");
assert(fixture.provenance?.parityClaim === false, "Fixture must not make a parity claim.");

function text(value) {
  return typeof value === "string" ? value : "";
}

function anchor(id, kind, label, sourcePath) {
  return { id, kind, label, sourcePath };
}

function buildAnchors(chart) {
  const anchors = [];
  const passport = chart?.passport ?? {};
  for (const key of ["ayanamsa", "house_system", "varga_scheme", "timezone_source", "coordinates"]) {
    if (passport[key]) anchors.push(anchor(`passport.${key}`, "passport", `${key}: ${passport[key]}`, `calculation.result.passport.${key}`));
  }

  const lagna = chart?.ascendant;
  if (lagna?.rashi) anchors.push(anchor("lagna.rashi", "lagna", `Lagna in ${lagna.rashi}`, "calculation.result.ascendant.rashi"));
  if (lagna?.nakshatra) anchors.push(anchor("lagna.nakshatra", "lagna", `${lagna.nakshatra} pada ${lagna.pada}`, "calculation.result.ascendant.nakshatra"));

  for (const graha of chart?.grahas ?? []) {
    anchors.push(anchor(`graha.${graha.body}`, "graha", `${graha.body} in ${graha.rashi}`, `calculation.result.grahas.${graha.body}.rashi`));
    if (graha.house) anchors.push(anchor(`graha.${graha.body}.house`, "graha", `${graha.body} in the ${graha.house}th house`, `calculation.result.grahas.${graha.body}.house`));
    if (graha.dignity) anchors.push(anchor(`graha.${graha.body}.dignity`, "graha", `${graha.body} ${graha.dignity}`, `calculation.result.grahas.${graha.body}.dignity`));
  }

  const panchanga = chart?.panchanga ?? {};
  for (const [key, value] of Object.entries(panchanga)) {
    if (value?.name) anchors.push(anchor(`panchanga.${key}`, "panchanga", `${key}: ${value.name}`, `calculation.result.panchanga.${key}`));
  }

  const vimshottari = chart?.dashas?.vimshottari;
  if (vimshottari?.status) anchors.push(anchor("dasha.vimshottari.status", "dasha", `Vimshottari ${vimshottari.status}`, "calculation.result.dashas.vimshottari.status"));
  if (vimshottari?.current?.lord) anchors.push(anchor("dasha.vimshottari.current", "dasha", `Vimshottari ${vimshottari.current.lord}`, "calculation.result.dashas.vimshottari.current"));

  const vargas = chart?.vargas ?? {};
  for (const [code, value] of Object.entries(vargas)) {
    if (value?.status) anchors.push(anchor(`varga.${code}.status`, "varga", `${code} ${value.status}`, `calculation.result.vargas.${code}.status`));
    if (value?.marker) anchors.push(anchor(`varga.${code}.marker`, "varga", value.marker, `calculation.result.vargas.${code}.marker`));
  }

  const classical = chart?.classical ?? {};
  for (const key of ["shadbala", "ashtakavarga", "yogas", "avasthas"]) {
    if (classical[key]?.status) anchors.push(anchor(`classical.${key}`, "classical", `${key} ${classical[key].status}`, `calculation.result.classical.${key}.status`));
  }

  return anchors;
}

const anchors = buildAnchors(result);
const anchorsByKind = new Map();
for (const item of anchors) {
  if (!anchorsByKind.has(item.kind)) anchorsByKind.set(item.kind, []);
  anchorsByKind.get(item.kind).push(item);
}

for (const kind of ["passport", "lagna", "graha", "panchanga", "dasha", "varga", "classical"]) {
  assert((anchorsByKind.get(kind)?.length ?? 0) > 0, `Missing saved-chart anchor kind: ${kind}`);
}
assert(anchors.some((item) => item.id.startsWith("varga.D1.")), "Saved-chart gate must include D1 anchors.");
assert(anchors.some((item) => item.id.startsWith("varga.") && !item.id.startsWith("varga.D1.")), "Saved-chart gate must include at least one divisional marker beyond D1.");
assert(anchors.some((item) => item.id === "classical.shadbala"), "Saved-chart gate must include shadbala status.");
assert(anchors.some((item) => item.id === "classical.ashtakavarga"), "Saved-chart gate must include ashtakavarga status.");
assert(anchors.some((item) => item.id === "classical.yogas"), "Saved-chart gate must include yogas status.");

const forbiddenRawWitnessPatterns = [
  "ChatExport",
  "message default clearfix",
  "tgme_widget_message",
  "from_name",
  "raw transcript",
  "source audio",
  "OPENAI_API_KEY",
  "sk-proj",
];
const publicClaimPatterns = [
  "parity achieved",
  "jh/pl compatible",
  "release accuracy guaranteed",
  "public quality claim",
  "guaranteed relationship success",
  "full jh/pl parity",
  "release accuracy",
];
const genericPatterns = [
  "positive energy",
  "trust your intuition",
  "follow your heart",
  "everything will unfold",
  "many opportunities",
];
const overclaimPatterns = [
  "proves guaranteed",
  "conclusively rank",
  "settle timing",
  "without caveats",
  "without calculation anchors",
];
const advancedTerms = ["shadbala", "ashtakavarga", "yogas", "avasthas", "d9", "navamsa"];
const caveatPatterns = ["caveat", "draft-only", "not a final claim", "does not rank", "unsupported"];

function includesAny(lowerText, patterns) {
  return patterns.filter((pattern) => lowerText.includes(pattern));
}

function sentenceHasAnchor(sentence) {
  const lower = sentence.toLowerCase();
  return anchors.some((item) => {
    const label = item.label.toLowerCase();
    const parts = label.split(/[^a-z0-9]+/).filter((part) => part.length >= 3);
    return parts.length > 0 && parts.some((part) => lower.includes(part));
  });
}

function keyClaimSentences(draft) {
  return draft
    .split(/[.!?]+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean)
    .filter((sentence) => {
      const lower = sentence.toLowerCase();
      return ["lagna", "jupiter", "saturn", "moon", "vimshottari", "d9", "navamsa", "shadbala", "ashtakavarga", "yogas", "avasthas", "cancer", "capricorn", "aquarius", "virgo"].some((term) =>
        lower.includes(term),
      );
    });
}

function evaluateDraft(draftCase) {
  const draft = text(draftCase?.text);
  const lower = draft.toLowerCase();
  const rawWitnessFlags = includesAny(lower, forbiddenRawWitnessPatterns.map((pattern) => pattern.toLowerCase()));
  const publicClaimFlags = includesAny(lower, publicClaimPatterns);
  const genericFlags = includesAny(lower, genericPatterns);
  const overclaimFlags = includesAny(lower, overclaimPatterns);
  const claims = keyClaimSentences(draft);
  const unanchoredClaims = claims.filter((sentence) => !sentenceHasAnchor(sentence));
  const advancedMentioned = advancedTerms.some((term) => lower.includes(term));
  const caveatPresent = !advancedMentioned || caveatPatterns.some((pattern) => lower.includes(pattern));
  const practicalQuestionPresent = /\?/.test(draft) && /\b(which|what)\b/i.test(draft) && /(dasha|anchor|decision|checked)/i.test(draft);
  const emphasisSection = lower.match(/emphasis points:\s*(.+)$/s)?.[1] ?? "";
  const emphasisAnchorHits = anchors.filter((item) => emphasisSection && sentenceHasAnchor(`${emphasisSection} ${item.label}`)).length;
  const keyAnchorsPresent = claims.length >= 4 && unanchoredClaims.length === 0;
  const repairInstructions = [
    keyAnchorsPresent ? "" : "Add calculation anchors from the saved-chart fact packet for each key claim.",
    caveatPresent ? "" : "Add a caveat or draft-only wording for unsupported advanced claims.",
    practicalQuestionPresent ? "" : "Add one practical question tied to a calculation anchor.",
    emphasisAnchorHits >= 3 ? "" : "Add concrete emphasis points tied to saved-chart facts.",
    genericFlags.length === 0 ? "" : "Replace generic motivational prose with saved-chart facts.",
    overclaimFlags.length === 0 && publicClaimFlags.length === 0 ? "" : "Remove public quality, parity, or guaranteed-result claims.",
    rawWitnessFlags.length === 0 ? "" : "Remove raw witness artifact references.",
  ].filter(Boolean);
  const draftEligible =
    keyAnchorsPresent &&
    caveatPresent &&
    practicalQuestionPresent &&
    emphasisAnchorHits >= 3 &&
    genericFlags.length === 0 &&
    overclaimFlags.length === 0 &&
    publicClaimFlags.length === 0 &&
    rawWitnessFlags.length === 0;

  return {
    id: draftCase.id,
    draftEligible,
    keyClaimCount: claims.length,
    unanchoredClaims,
    genericFlags,
    overclaimFlags,
    publicClaimFlags,
    rawWitnessFlags,
    caveatPresent,
    practicalQuestionPresent,
    emphasisAnchorHits,
    repairInstructions,
  };
}

const grounded = evaluateDraft(fixture.drafts.grounded);
const generic = evaluateDraft(fixture.drafts.generic);
const overclaim = evaluateDraft(fixture.drafts.overclaim);

assert(grounded.draftEligible === true, "Grounded saved-chart draft must be draft-eligible.");
assert(grounded.keyClaimCount >= 4, "Grounded draft must include anchored key claims.");
assert(grounded.caveatPresent === true, "Grounded draft must include a caveat for advanced claims.");
assert(grounded.practicalQuestionPresent === true, "Grounded draft must include one practical question tied to chart facts.");
assert(grounded.emphasisAnchorHits >= 3, "Grounded draft must include concrete emphasis points tied to chart facts.");
assert(generic.draftEligible === false, "Generic draft must be blocked.");
assert(generic.genericFlags.length >= 1, "Generic draft must expose generic-language flags.");
assert(generic.repairInstructions.length >= 1, "Generic draft must include repair instructions.");
assert(overclaim.draftEligible === false, "Overclaim draft must be blocked.");
assert(overclaim.overclaimFlags.length >= 1 || overclaim.publicClaimFlags.length >= 1, "Overclaim draft must expose overclaim/public-claim flags.");
assert(overclaim.repairInstructions.length >= 1, "Overclaim draft must include repair instructions.");

const fixtureSource = JSON.stringify(fixture);
for (const pattern of forbiddenRawWitnessPatterns) {
  assert(!fixtureSource.toLowerCase().includes(pattern.toLowerCase()), `Saved-chart fixture leaked forbidden raw witness marker: ${pattern}`);
}

console.log(
  JSON.stringify(
    {
      gate: "ai_review_saved_chart_grounding_gate",
      fixturePath,
      anchorCount: anchors.length,
      anchorKinds: Array.from(anchorsByKind.keys()).sort(),
      grounded: { draftEligible: grounded.draftEligible, keyClaimCount: grounded.keyClaimCount },
      generic: { draftEligible: generic.draftEligible, repairs: generic.repairInstructions.length },
      overclaim: { draftEligible: overclaim.draftEligible, repairs: overclaim.repairInstructions.length },
    },
    null,
    2,
  ),
);
