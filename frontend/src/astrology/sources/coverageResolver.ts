import type { RuleDefinition } from "./ruleTypes";
import type { PassageDefinition } from "./passageTypes";

export type EvidenceCoverage = "verified" | "partial" | "needs_source" | "unsupported";

export type CoverageSummary = {
  totalItems: number;
  verifiedItems: number;
  partialItems: number;
  needsSourceItems: number;
  unsupportedItems: number;
};

export function resolveRuleCoverage(rules: RuleDefinition[], passages: PassageDefinition[]): EvidenceCoverage {
  if (!rules.length) return "unsupported";
  const verifiedRules = rules.filter((rule) => rule.status === "verified");
  if (verifiedRules.length && verifiedRules.every((rule) => rule.passageIds.every((passageId) => passages.find((passage) => passage.id === passageId)?.status === "verified"))) {
    return rules.length === verifiedRules.length ? "verified" : "partial";
  }
  if (verifiedRules.length) return "partial";
  return "needs_source";
}

export function summarizeCoverage(coverages: EvidenceCoverage[]): CoverageSummary {
  return {
    totalItems: coverages.length,
    verifiedItems: coverages.filter((coverage) => coverage === "verified").length,
    partialItems: coverages.filter((coverage) => coverage === "partial").length,
    needsSourceItems: coverages.filter((coverage) => coverage === "needs_source").length,
    unsupportedItems: coverages.filter((coverage) => coverage === "unsupported").length,
  };
}
