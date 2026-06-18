import type { ReportEvidenceItem } from "../reports";
import { getSource } from "./sourceRegistry";
import type { AiEligibilityExclusionReason, AiEligibilityPack, AiEligibleCitation } from "./aiEligibilityTypes";
import type { EvidenceProvenance, ProvenanceEnrichedReportEvidence } from "./provenanceResolver";

function exclusionReason(item: ReportEvidenceItem, provenance: EvidenceProvenance | null): AiEligibilityExclusionReason | null {
  if (!item.available) return "not_available";
  if (!provenance) return "missing_citation_chain";
  if (provenance.coverage === "verified") return null;
  if (provenance.coverage === "needs_source") return "needs_source";
  if (provenance.coverage === "unsupported") return "unsupported";
  if (provenance.coverage === "partial") return "partial";
  return "not_verified";
}

function citationsFor(provenance: EvidenceProvenance): AiEligibleCitation[] {
  const verifiedRuleIds = new Set(provenance.ruleRefs.filter((rule) => rule.status === "verified").map((rule) => rule.ruleId));
  return provenance.passageRefs
    .filter((passage) => passage.status === "verified" && getSource(passage.sourceId)?.status === "verified")
    .flatMap((passage) =>
      Array.from(verifiedRuleIds).map((ruleId) => ({
        ruleId,
        passageId: passage.passageId,
        sourceId: passage.sourceId,
        citationLabel: passage.citationLabel,
      })),
    )
    .sort((a, b) => `${a.ruleId}:${a.passageId}`.localeCompare(`${b.ruleId}:${b.passageId}`));
}

export function buildAiEligibilityPack(sourceEvidence: ProvenanceEnrichedReportEvidence): AiEligibilityPack {
  const provenanceByItem = new Map(sourceEvidence.provenance.map((provenance) => [provenance.evidenceItemId, provenance]));
  const eligibleItems: AiEligibilityPack["eligibleItems"] = [];
  const excludedItems: AiEligibilityPack["excludedItems"] = [];

  for (const item of sourceEvidence.evidence.items) {
    const provenance = provenanceByItem.get(item.id) ?? null;
    const reason = exclusionReason(item, provenance);
    const citations = provenance ? citationsFor(provenance) : [];

    if (!reason && citations.length > 0) {
      eligibleItems.push({
        evidenceItemId: item.id,
        label: item.label,
        kind: item.kind,
        entityId: item.entityId,
        calculationId: item.calculationId,
        relationshipFactorId: item.relationshipFactorId,
        value: item.value,
        citations,
      });
    } else {
      excludedItems.push({
        evidenceItemId: item.id,
        label: item.label,
        coverage: provenance?.coverage ?? "unsupported",
        reason: reason ?? "missing_citation_chain",
      });
    }
  }

  const blockedItems = excludedItems.filter((item) => item.reason === "missing_citation_chain").length;
  return {
    schemaVersion: 1,
    reportEvidenceSchemaVersion: sourceEvidence.evidence.schemaVersion,
    reportRecipeId: sourceEvidence.evidence.reportRecipeId,
    reportRecipeVersion: sourceEvidence.evidence.reportRecipeVersion,
    reportTypeId: sourceEvidence.evidence.reportTypeId,
    mode: sourceEvidence.evidence.mode,
    status: eligibleItems.length > 0 && blockedItems === 0 ? "eligible" : eligibleItems.length > 0 ? "excluded" : "blocked",
    eligibleItems,
    excludedItems,
    summary: {
      totalItems: sourceEvidence.evidence.items.length,
      eligibleItems: eligibleItems.length,
      excludedItems: excludedItems.length,
      blockedItems,
    },
    sourceEvidence,
  };
}
