import type { AiEligibilityExclusionReason, AiEligibilityPack } from "./aiEligibilityTypes";
import type { AiReportExcludedSummary, AiReportRequest, AiReportRequestItem } from "./aiRequestTypes";

export function sortAiRequestItems(items: AiReportRequestItem[]): AiReportRequestItem[] {
  return [...items].sort((a, b) => a.evidenceItemId.localeCompare(b.evidenceItemId));
}

function buildExcludedSummary(eligibilityPack: AiEligibilityPack): AiReportExcludedSummary {
  const byReason: Partial<Record<AiEligibilityExclusionReason, number>> = {};

  for (const item of eligibilityPack.excludedItems) {
    byReason[item.reason] = (byReason[item.reason] ?? 0) + 1;
  }

  return {
    total: eligibilityPack.excludedItems.length,
    byReason,
  };
}

export function buildAiReportRequest(eligibilityPack: AiEligibilityPack): AiReportRequest {
  const items = sortAiRequestItems(
    eligibilityPack.eligibleItems.map((item) => ({
      evidenceItemId: item.evidenceItemId,
      label: item.label,
      kind: item.kind,
      entityId: item.entityId,
      calculationId: item.calculationId,
      relationshipFactorId: item.relationshipFactorId,
      citationChains: [...item.citations].sort((a, b) => `${a.ruleId}:${a.passageId}`.localeCompare(`${b.ruleId}:${b.passageId}`)),
    })),
  );

  const citationChains = items
    .flatMap((item) => item.citationChains)
    .sort((a, b) => `${a.ruleId}:${a.passageId}:${a.sourceId}`.localeCompare(`${b.ruleId}:${b.passageId}:${b.sourceId}`));
  const excludedSummary = buildExcludedSummary(eligibilityPack);

  return {
    schemaVersion: 1,
    reportEvidenceSchemaVersion: eligibilityPack.reportEvidenceSchemaVersion,
    reportRecipeId: eligibilityPack.reportRecipeId,
    reportRecipeVersion: eligibilityPack.reportRecipeVersion,
    reportTypeId: eligibilityPack.reportTypeId,
    mode: eligibilityPack.mode,
    eligibleItemIds: items.map((item) => item.evidenceItemId),
    items,
    citationChains,
    excludedSummary,
  };
}
