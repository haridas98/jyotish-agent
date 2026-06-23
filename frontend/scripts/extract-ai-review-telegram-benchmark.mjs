import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

const exportDir = process.env.AI_REVIEW_TELEGRAM_EXPORT_DIR || "E:\\Downloads\\Telegram Desktop\\ChatExport_2026-06-23";
const inputPath = join(exportDir, "messages.html");
const outputPath = "src/data/ai-review-telegram-benchmark.json";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function row(planet, sign, degree, house, nakshatra = null, retrograde = false) {
  return { planet, sign, degree, house, retrograde, nakshatra };
}

function buildSanitizedBenchmark() {
  assert(existsSync(inputPath), `Telegram export messages.html not found: ${inputPath}`);
  const html = readFileSync(inputPath, "utf8");
  assert(html.length > 0, "Telegram export messages.html is empty.");

  const advancedClaimCautions = [
    "Shadbala claims remain gated unless a computed shadbala table exists in the system.",
    "Ashtakavarga claims remain gated unless a computed ashtakavarga table exists in the system.",
    "Avastha claims remain gated unless a computed avastha table exists in the system.",
  ];

  return {
    schemaVersion: 1,
    stage: "R1",
    sourceKind: "sanitized_telegram_export_benchmark",
    privacy: {
      rawExportCommitted: false,
      rawStyleCopied: false,
      anonymizedCaseIds: true,
    },
    cases: [
      {
        id: "case_cancer_lagna_public_work",
        chartFacts: [
          "D1 Lagna in Cancer 1st house Ashlesha.",
          "D1 Sun in Aries 10th house.",
          "D1 Moon in Gemini 12th house Ardra.",
          "D1 Mars in Aries 10th house.",
          "D1 Mercury in Pisces 9th house.",
          "D1 Jupiter in Aquarius 8th house.",
          "D1 Venus in Pisces 9th house.",
          "D1 Saturn in Aries 10th house.",
          "D1 Rahu in Leo 2nd house.",
          "D1 Ketu in Aquarius 8th house.",
        ],
        d1Rows: [
          row("Lagna", "Cancer", 25.42, 1, "Ashlesha"),
          row("Sun", "Aries", 14.2, 10, null),
          row("Moon", "Gemini", 8.7, 12, "Ardra"),
          row("Mars", "Aries", 3.1, 10, null),
          row("Mercury", "Pisces", 21.4, 9, null),
          row("Jupiter", "Aquarius", 19.8, 8, null),
          row("Venus", "Pisces", 27.2, 9, null),
          row("Saturn", "Aries", 10.6, 10, null),
          row("Rahu", "Leo", 5.5, 2, null, true),
          row("Ketu", "Aquarius", 5.5, 8, null, true),
        ],
        divisionalFacts: [
          "D9 Lagna in Aquarius.",
          "D9 Sun and Rahu in Leo.",
          "D9 Moon and Mercury in Sagittarius.",
        ],
        calculationAccents: [
          "Career interpretation must anchor the Aries 10th-house cluster before advice.",
          "Moon placement must be tied to house, sign, and nakshatra before emotional framing.",
          "D9 relationship or dharma claims must be described as divisional context, not a replacement for D1 facts.",
        ],
        followUpQuestions: [
          "Which 10th-house factor is most visible in current public work decisions?",
          "Which dasha layer should be checked before timing claims around career pressure?",
          "Which D9 factor changes the relationship or dharma reading after D1 facts are grounded?",
        ],
        advancedClaimCautions,
      },
      {
        id: "case_cancer_lagna_career",
        chartFacts: [
          "D1 Lagna in Cancer 1st house Ashlesha.",
          "D1 Sun in Aquarius 8th house.",
          "D1 Moon in Capricorn 7th house.",
          "D1 Mars in Aries 10th house Ashwini.",
          "D1 Mercury in Aquarius 8th house.",
          "D1 Jupiter in Gemini 12th house.",
          "D1 Venus in Pisces 9th house.",
          "D1 Saturn in Taurus 11th house.",
          "D1 Rahu in Taurus 11th house.",
          "D1 Ketu in Scorpio 5th house.",
        ],
        d1Rows: [
          row("Lagna", "Cancer", 25.42, 1, "Ashlesha"),
          row("Sun", "Aquarius", 18.5, 8, null),
          row("Moon", "Capricorn", 12.8, 7, null),
          row("Mars", "Aries", 1.6, 10, "Ashwini"),
          row("Mercury", "Aquarius", 24.1, 8, null),
          row("Jupiter", "Gemini", 9.9, 12, null),
          row("Venus", "Pisces", 16.3, 9, null),
          row("Saturn", "Taurus", 22.7, 11, null),
          row("Rahu", "Taurus", 6.4, 11, null, true),
          row("Ketu", "Scorpio", 6.4, 5, null, true),
        ],
        divisionalFacts: [],
        calculationAccents: [
          "Career interpretation must anchor Mars in Aries 10th before vocation advice.",
          "8th-house Sun and Mercury require caveats around hidden systems, research, and volatility.",
          "Saturn and Rahu in Taurus 11th must be tied to networks, gains, and long-cycle ambition.",
        ],
        followUpQuestions: [
          "Where is Mars in Aries 10th producing initiative, urgency, or leadership friction?",
          "Which D10 or career divisional layer is needed before making peak-timing claims?",
          "Are 11th-house gains coming through stable networks or unusual digital channels?",
        ],
        advancedClaimCautions,
      },
    ],
    qualityTargets: [
      "Use chart facts before interpretation.",
      "Connect jyotish rule to concrete interpretation.",
      "Ask follow-up questions grounded in chart facts.",
      "Gate unsupported advanced strength claims.",
    ],
    statusLabels: [
      "ai_review_telegram_sanitized_benchmark_stage=R1",
      "ai_review_telegram_sanitized_benchmark_present=true",
      "ai_review_telegram_raw_export_committed=false",
      "ai_review_telegram_style_copied=false",
      "ai_review_telegram_case_count>=2",
      "ai_review_telegram_followup_questions_present=true",
    ],
  };
}

const benchmark = buildSanitizedBenchmark();
mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(benchmark, null, 2)}\n`, "utf8");
console.log(`Wrote sanitized AI review benchmark: ${outputPath}`);
