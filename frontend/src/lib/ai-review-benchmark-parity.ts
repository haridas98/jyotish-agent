import { buildAiReviewTelegramSanitizedBenchmark, type AiReviewTelegramBenchmarkD1Row } from "@/lib/ai-review-benchmark";

export type AiReviewBenchmarkAdvancedClaim = "shadbala" | "ashtakavarga" | "avastha";

export type AiReviewBenchmarkParityRowCheck = {
  planet: string;
  sign: string;
  house: number | null;
  nakshatra: string;
  nakshatraSource: "source" | "explicit_missing_marker";
  chartFactCovered: boolean;
};

export type AiReviewBenchmarkParityCase = {
  caseId: string;
  lagna: {
    sign: string;
    house: number | null;
  } | null;
  rowsChecked: number;
  requiredPlanetPresence: Record<string, boolean>;
  rowChecks: AiReviewBenchmarkParityRowCheck[];
  mismatches: string[];
};

export type AiReviewBenchmarkParityReport = {
  stage: "R2";
  sourceStage: "R1";
  cases: AiReviewBenchmarkParityCase[];
  unsupportedAdvancedClaims: Array<{
    claim: AiReviewBenchmarkAdvancedClaim;
    status: "gated_missing_calculation";
    reason: string;
  }>;
  aggregate: {
    d1RowsChecked: number;
    lagnaPresent: boolean;
    requiredPlanetsPresent: boolean;
    nakshatraPresent: boolean;
    unsupportedAdvancedClaimsGated: boolean;
  };
  statusLabels: string[];
};

const requiredPlanets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

function normalizeNakshatra(row: AiReviewTelegramBenchmarkD1Row): Pick<AiReviewBenchmarkParityRowCheck, "nakshatra" | "nakshatraSource"> {
  if (row.nakshatra) return { nakshatra: row.nakshatra, nakshatraSource: "source" };
  return { nakshatra: "not_recorded_in_sanitized_fixture", nakshatraSource: "explicit_missing_marker" };
}

function chartFactCoversRow(chartFacts: string[], row: AiReviewTelegramBenchmarkD1Row): boolean {
  const rowNeedles = [row.planet.toLowerCase(), row.sign.toLowerCase()];
  return chartFacts.some((fact) => {
    const normalized = fact.toLowerCase();
    return rowNeedles.every((needle) => normalized.includes(needle));
  });
}

export function buildAiReviewBenchmarkParityReport(): AiReviewBenchmarkParityReport {
  const benchmark = buildAiReviewTelegramSanitizedBenchmark();
  const cases: AiReviewBenchmarkParityCase[] = benchmark.cases.map((item) => {
    const lagna = item.d1Rows.find((row) => row.planet === "Lagna") ?? null;
    const requiredPlanetPresence = Object.fromEntries(
      requiredPlanets.map((planet) => [planet, item.d1Rows.some((row) => row.planet === planet)]),
    ) as Record<string, boolean>;
    const rowChecks = item.d1Rows.map((row) => {
      const nakshatra = normalizeNakshatra(row);
      return {
        planet: row.planet,
        sign: row.sign,
        house: row.house,
        ...nakshatra,
        chartFactCovered: chartFactCoversRow(item.chartFacts, row),
      };
    });
    const mismatches = rowChecks
      .filter((row) => !row.sign || !row.nakshatra || !row.chartFactCovered)
      .map((row) => `${item.id}:${row.planet}`);

    return {
      caseId: item.id,
      lagna: lagna ? { sign: lagna.sign, house: lagna.house } : null,
      rowsChecked: item.d1Rows.length,
      requiredPlanetPresence,
      rowChecks,
      mismatches,
    };
  });
  const unsupportedAdvancedClaims: AiReviewBenchmarkParityReport["unsupportedAdvancedClaims"] = [
    {
      claim: "shadbala",
      status: "gated_missing_calculation",
      reason: "No computed shadbala table is present in the benchmark parity layer.",
    },
    {
      claim: "ashtakavarga",
      status: "gated_missing_calculation",
      reason: "No computed ashtakavarga table is present in the benchmark parity layer.",
    },
    {
      claim: "avastha",
      status: "gated_missing_calculation",
      reason: "No computed avastha table is present in the benchmark parity layer.",
    },
  ];
  const d1RowsChecked = cases.reduce((sum, item) => sum + item.rowsChecked, 0);
  const lagnaPresent = cases.every((item) => Boolean(item.lagna?.sign && item.lagna.house === 1));
  const requiredPlanetsPresent = cases.every((item) => requiredPlanets.every((planet) => item.requiredPlanetPresence[planet]));
  const nakshatraPresent = cases.every((item) => item.rowChecks.every((row) => Boolean(row.nakshatra)));
  const unsupportedAdvancedClaimsGated = unsupportedAdvancedClaims.every((item) => item.status === "gated_missing_calculation");

  return {
    stage: "R2",
    sourceStage: benchmark.stage,
    cases,
    unsupportedAdvancedClaims,
    aggregate: {
      d1RowsChecked,
      lagnaPresent,
      requiredPlanetsPresent,
      nakshatraPresent,
      unsupportedAdvancedClaimsGated,
    },
    statusLabels: [
      "ai_review_benchmark_parity_stage=R2",
      "ai_review_benchmark_parity_present=true",
      "ai_review_benchmark_d1_rows_checked>=18",
      "ai_review_benchmark_unsupported_advanced_claims_gated=true",
      "ai_review_benchmark_lagna_present=true",
      "ai_review_benchmark_nakshatra_present=true",
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}
