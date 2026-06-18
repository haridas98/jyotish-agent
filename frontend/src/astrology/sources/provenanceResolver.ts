import type { ReportEvidencePack } from "../reports";
import { getPassage } from "./passageRegistry";
import { getRule } from "./ruleRegistry";
import { summarizeCoverage, resolveRuleCoverage, type CoverageSummary, type EvidenceCoverage } from "./coverageResolver";
import type { RuleDefinition, RuleId } from "./ruleTypes";
import type { PassageDefinition, PassageId } from "./passageTypes";
import type { SourceId } from "./sourceTypes";

export type EvidenceProvenance = {
  evidenceItemId: string;
  ruleRefs: Array<{
    ruleId: RuleId;
    status: RuleDefinition["status"];
  }>;
  passageRefs: Array<{
    passageId: PassageId;
    sourceId: SourceId;
    citationLabel: string;
    status: PassageDefinition["status"];
  }>;
  coverage: EvidenceCoverage;
};

export type ProvenanceEnrichedReportEvidence = {
  evidence: ReportEvidencePack;
  provenance: EvidenceProvenance[];
  coverageSummary: CoverageSummary;
};

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values)).sort();
}

export function resolveEvidenceProvenance(evidence: ReportEvidencePack): ProvenanceEnrichedReportEvidence {
  const provenance = evidence.items.map((item) => {
    const ruleIds = uniqueSorted([...item.provenance.ruleIds, ...item.provenance.sourceRefs.map((ref) => ref.ruleId)]);
    const rules = ruleIds.map((ruleId) => getRule(ruleId)).filter((rule): rule is RuleDefinition => Boolean(rule));
    const passages = uniqueSorted(rules.flatMap((rule) => rule.passageIds))
      .map((passageId) => getPassage(passageId))
      .filter((passage): passage is PassageDefinition => Boolean(passage));
    const coverage = resolveRuleCoverage(rules, passages);

    return {
      evidenceItemId: item.id,
      ruleRefs: rules.map((rule) => ({ ruleId: rule.id, status: rule.status })).sort((a, b) => a.ruleId.localeCompare(b.ruleId)),
      passageRefs: passages
        .map((passage) => ({
          passageId: passage.id,
          sourceId: passage.sourceId,
          citationLabel: passage.citationLabel.ru,
          status: passage.status,
        }))
        .sort((a, b) => a.passageId.localeCompare(b.passageId)),
      coverage,
    };
  });

  return {
    evidence,
    provenance,
    coverageSummary: summarizeCoverage(provenance.map((item) => item.coverage)),
  };
}
