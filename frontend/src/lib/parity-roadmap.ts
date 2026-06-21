import type { WitnessSummary } from "@/lib/api";

type ParitySummary = {
  case_count: number;
  comparable_count: number;
  passed_count: number;
  failed_count: number;
  missing_witness_count: number;
  not_reviewed_count: number;
  not_comparable_count: number;
  target_reviewed_count: number;
  target_met: boolean;
};

type ParityPayload = {
  available: boolean;
  target_met?: boolean;
  summary?: ParitySummary;
  [key: string]: unknown;
};

type ParityKey =
  | "witness_core_parity"
  | "witness_varga_parity"
  | "witness_dasha_parity"
  | "witness_panchanga_parity"
  | "witness_ashtakavarga_parity"
  | "witness_strengths_parity"
  | "witness_yoga_parity"
  | "witness_special_points_parity"
  | "witness_argala_parity"
  | "witness_avastha_parity"
  | "witness_drishti_parity"
  | "witness_transit_coordinate_parity"
  | "witness_compatibility_parity"
  | "witness_muhurta_parity"
  | "witness_tithi_pravesha_parity"
  | "witness_tajaka_parity"
  | "witness_prashna_parity"
  | "witness_jaimini_karaka_parity"
  | "witness_jaimini_varga_parity";

export type ParityRoadmapState = "ready" | "review" | "waiting";

export type ParityRoadmapRow = {
  key: ParityKey;
  label: string;
  state: ParityRoadmapState;
  passed: number;
  target: number;
  failed: number;
  missing: number;
  skipped: number;
  readinessGaps: number;
  action: "ready for demo" | "review witness rows" | "collect report";
};

export type ParityCollectionChecklistRow = ParityRoadmapRow & {
  collectionHint: string;
};

export type ParityCollectionChecklistTotals = {
  ready: number;
  review: number;
  waiting: number;
};

export type ReleaseGateActionSummary = {
  totals: {
    collectReports: number;
    reviewRows: number;
    readyDemo: number;
  };
  smokeMatrixStatus: "ready";
  smokeMatrixText: "command smoke matrix: ready";
  collectReportRows: ParityCollectionChecklistRow[];
  reviewRows: ParityCollectionChecklistRow[];
  readyRows: ParityCollectionChecklistRow[];
};

export type CollectionPlanSnapshotRunbook = {
  schemaVersion: "witness-parity-collection-plan.v1";
  commandHint: "manage.py build_witness_parity_collection_plan_report --output <report-json>";
  dryRunCopy: "dry-run plan";
  noCollectionCopy: "does not collect or generate reports";
  releaseGateStatus: "blocked" | "ready";
  totals: {
    domainCount: number;
    collectReports: number;
    reviewRows: number;
    readyDemo: number;
  };
};

export type ArtifactAvailabilityCheckpoint = {
  title: "Artifact availability checkpoint";
  environmentCopy: "environment artifact availability";
  localDevCopy: "local dev can show 19/19/0";
  productionCopy: "production can show 19/19/0";
  environmentDetailCopy: "committed artifact availability is aligned; release remains blocked by review witness rows";
  releaseGateStatus: "blocked" | "ready";
  commandSmokeMatrixStatus: "ready";
  commandSmokeMatrixText: "command smoke matrix: ready";
  totals: {
    domainCount: number;
    availableReviewRows: number;
    missingReports: number;
    collectReports: number;
    reviewRows: number;
    readyDemo: number;
  };
};

export const parityRoadmapItems: Array<{ key: ParityKey; label: string }> = [
  { key: "witness_core_parity", label: "Core parity" },
  { key: "witness_varga_parity", label: "Varga parity" },
  { key: "witness_dasha_parity", label: "Dasha parity" },
  { key: "witness_panchanga_parity", label: "Panchanga parity" },
  { key: "witness_ashtakavarga_parity", label: "Ashtakavarga parity" },
  { key: "witness_strengths_parity", label: "Strengths parity" },
  { key: "witness_yoga_parity", label: "Yoga parity" },
  { key: "witness_special_points_parity", label: "Special points parity" },
  { key: "witness_argala_parity", label: "Argala parity" },
  { key: "witness_avastha_parity", label: "Avastha parity" },
  { key: "witness_drishti_parity", label: "Drishti parity" },
  { key: "witness_transit_coordinate_parity", label: "Transit coordinate parity" },
  { key: "witness_compatibility_parity", label: "Compatibility parity" },
  { key: "witness_muhurta_parity", label: "Muhurta parity" },
  { key: "witness_tithi_pravesha_parity", label: "Tithi Pravesha parity" },
  { key: "witness_tajaka_parity", label: "Tajaka parity" },
  { key: "witness_prashna_parity", label: "Prashna parity" },
  { key: "witness_jaimini_karaka_parity", label: "Jaimini karaka parity" },
  { key: "witness_jaimini_varga_parity", label: "Jaimini varga parity" },
];

const parityCollectionCommandByKey: Record<ParityKey, string> = {
  witness_core_parity: "build_witness_core_parity_report",
  witness_varga_parity: "build_witness_varga_parity_report",
  witness_dasha_parity: "build_witness_dasha_parity_report",
  witness_panchanga_parity: "build_witness_panchanga_parity_report",
  witness_ashtakavarga_parity: "build_witness_ashtakavarga_parity_report",
  witness_strengths_parity: "build_witness_strengths_parity_report",
  witness_yoga_parity: "build_witness_yoga_parity_report",
  witness_special_points_parity: "build_witness_special_points_parity_report",
  witness_argala_parity: "build_witness_argala_parity_report",
  witness_avastha_parity: "build_witness_avastha_parity_report",
  witness_drishti_parity: "build_witness_drishti_parity_report",
  witness_transit_coordinate_parity: "build_witness_transit_coordinates_parity_report",
  witness_compatibility_parity: "build_witness_compatibility_parity_report",
  witness_muhurta_parity: "build_witness_muhurta_parity_report",
  witness_tithi_pravesha_parity: "build_witness_tithi_pravesha_parity_report",
  witness_tajaka_parity: "build_witness_tajaka_parity_report",
  witness_prashna_parity: "build_witness_prashna_parity_report",
  witness_jaimini_karaka_parity: "build_witness_jaimini_karaka_parity_report",
  witness_jaimini_varga_parity: "build_witness_jaimini_varga_parity_report",
};

export function buildParityRoadmapRows(witnessSummary: WitnessSummary | null): ParityRoadmapRow[] {
  return parityRoadmapItems.map((item) => {
    const payload = witnessSummary?.[item.key] as ParityPayload | undefined;
    const summary = payload?.summary;
    const passed = safeNumber(summary?.passed_count);
    const target = safeNumber(summary?.target_reviewed_count);
    const failed = safeNumber(summary?.failed_count);
    const missing =
      safeNumber(summary?.missing_witness_count) +
      safeNumber(summary?.not_reviewed_count) +
      safeNumber(summary?.not_comparable_count);
    const skipped = payload ? skippedCount(payload) : 0;
    const readinessGaps = payload ? readinessGapCount(payload) : 0;
    const targetMet = Boolean(payload?.target_met ?? summary?.target_met);
    const ready = Boolean(payload?.available) && targetMet && failed === 0 && missing === 0;
    const state: ParityRoadmapState = payload?.available ? (ready ? "ready" : "review") : "waiting";

    return {
      key: item.key,
      label: item.label,
      state,
      passed,
      target,
      failed,
      missing,
      skipped,
      readinessGaps,
      action: state === "ready" ? "ready for demo" : state === "review" ? "review witness rows" : "collect report",
    };
  });
}

export function buildParityCollectionChecklistRows(rows: ParityRoadmapRow[]): ParityCollectionChecklistRow[] {
  return rows.map((row) => ({
    ...row,
    collectionHint: `manage.py ${parityCollectionCommandByKey[row.key]} --output <report-json>`,
  }));
}

export function buildParityCollectionChecklistTotals(rows: ParityRoadmapRow[]): ParityCollectionChecklistTotals {
  return rows.reduce<ParityCollectionChecklistTotals>(
    (totals, row) => ({
      ...totals,
      [row.state]: totals[row.state] + 1,
    }),
    { ready: 0, review: 0, waiting: 0 },
  );
}

export function buildReleaseGateActionSummary(rows: ParityCollectionChecklistRow[]): ReleaseGateActionSummary {
  const collectReportRows = rows.filter((row) => row.action === "collect report");
  const reviewRows = rows.filter((row) => row.action === "review witness rows");
  const readyRows = rows.filter((row) => row.action === "ready for demo");
  return {
    totals: {
      collectReports: collectReportRows.length,
      reviewRows: reviewRows.length,
      readyDemo: readyRows.length,
    },
    smokeMatrixStatus: "ready",
    smokeMatrixText: "command smoke matrix: ready",
    collectReportRows,
    reviewRows,
    readyRows,
  };
}

export function buildCollectionPlanSnapshotRunbook(
  rows: ParityCollectionChecklistRow[],
  releaseGateActionSummary: ReleaseGateActionSummary,
): CollectionPlanSnapshotRunbook {
  const blocked = releaseGateActionSummary.totals.collectReports > 0 || releaseGateActionSummary.totals.reviewRows > 0;
  return {
    schemaVersion: "witness-parity-collection-plan.v1",
    commandHint: "manage.py build_witness_parity_collection_plan_report --output <report-json>",
    dryRunCopy: "dry-run plan",
    noCollectionCopy: "does not collect or generate reports",
    releaseGateStatus: blocked ? "blocked" : "ready",
    totals: {
      domainCount: rows.length,
      collectReports: releaseGateActionSummary.totals.collectReports,
      reviewRows: releaseGateActionSummary.totals.reviewRows,
      readyDemo: releaseGateActionSummary.totals.readyDemo,
    },
  };
}

export function buildArtifactAvailabilityCheckpoint(
  rows: ParityCollectionChecklistRow[],
  releaseGateActionSummary: ReleaseGateActionSummary,
): ArtifactAvailabilityCheckpoint {
  const missingReports = releaseGateActionSummary.totals.collectReports;
  const blocked = missingReports > 0 || releaseGateActionSummary.totals.reviewRows > 0;
  return {
    title: "Artifact availability checkpoint",
    environmentCopy: "environment artifact availability",
    localDevCopy: "local dev can show 19/19/0",
    productionCopy: "production can show 19/19/0",
    environmentDetailCopy: "committed artifact availability is aligned; release remains blocked by review witness rows",
    releaseGateStatus: blocked ? "blocked" : "ready",
    commandSmokeMatrixStatus: "ready",
    commandSmokeMatrixText: "command smoke matrix: ready",
    totals: {
      domainCount: rows.length,
      availableReviewRows: rows.length - missingReports,
      missingReports,
      collectReports: missingReports,
      reviewRows: releaseGateActionSummary.totals.reviewRows,
      readyDemo: releaseGateActionSummary.totals.readyDemo,
    },
  };
}

function skippedCount(payload: ParityPayload): number {
  let total = 0;
  for (const [key, value] of Object.entries(payload)) {
    if (!key.endsWith("_summary") || key === "summary" || !isRecord(value)) {
      continue;
    }
    for (const row of Object.values(value)) {
      if (isRecord(row)) {
        total += safeNumber(row.skipped);
      }
    }
  }
  return total;
}

function readinessGapCount(payload: ParityPayload): number {
  const readiness = payload.readiness_summary;
  if (!isRecord(readiness)) {
    return 0;
  }
  return Object.values(readiness).reduce<number>((total, row) => {
    if (!isRecord(row)) {
      return total;
    }
    return total + safeNumber(row.actual_missing);
  }, 0);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function safeNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}
