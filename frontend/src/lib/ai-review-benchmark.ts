import benchmarkData from "@/data/ai-review-telegram-benchmark.json";

export type AiReviewTelegramBenchmarkD1Row = {
  planet: string;
  sign: string;
  degree: number;
  house: number | null;
  retrograde: boolean;
  nakshatra: string | null;
};

export type AiReviewTelegramBenchmarkCase = {
  id: string;
  chartFacts: string[];
  d1Rows: AiReviewTelegramBenchmarkD1Row[];
  divisionalFacts: string[];
  calculationAccents: string[];
  followUpQuestions: string[];
  advancedClaimCautions: string[];
};

export type AiReviewTelegramSanitizedBenchmark = {
  schemaVersion: 1;
  stage: "R1";
  sourceKind: "sanitized_telegram_export_benchmark";
  privacy: {
    rawExportCommitted: false;
    rawStyleCopied: false;
    anonymizedCaseIds: true;
  };
  cases: AiReviewTelegramBenchmarkCase[];
  qualityTargets: string[];
  statusLabels: string[];
};

export function buildAiReviewTelegramSanitizedBenchmark(): AiReviewTelegramSanitizedBenchmark {
  const imported = benchmarkData as AiReviewTelegramSanitizedBenchmark | { default: AiReviewTelegramSanitizedBenchmark };
  const data = "default" in imported ? imported.default : imported;
  return structuredClone(data) as AiReviewTelegramSanitizedBenchmark;
}
