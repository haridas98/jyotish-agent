import type { AiReportRequest } from "./aiRequestTypes";
import type { AiReportResponse, AiReportResponseValidationResult } from "./aiResponseTypes";

function citationKey(citation: { ruleId: string; passageId: string; sourceId: string }): string {
  return `${citation.ruleId}:${citation.passageId}:${citation.sourceId}`;
}

export function validateAiReportResponse(request: AiReportRequest, response: AiReportResponse): AiReportResponseValidationResult {
  const errors: string[] = [];
  const knownItems = new Set(request.eligibleItemIds);
  const citationsByItem = new Map(request.items.map((item) => [item.evidenceItemId, new Set(item.citationChains.map(citationKey))]));

  if (response.schemaVersion !== 1) errors.push("schemaVersion must be 1.");
  if (response.requestSchemaVersion !== request.schemaVersion) errors.push("requestSchemaVersion does not match request.");
  if (response.reportRecipeId !== request.reportRecipeId) errors.push("reportRecipeId does not match request.");
  if (response.reportTypeId !== request.reportTypeId) errors.push("reportTypeId does not match request.");

  const seenThesisIds = new Set<string>();
  for (const thesis of response.theses) {
    if (seenThesisIds.has(thesis.id)) errors.push(`Duplicate thesis id: ${thesis.id}`);
    seenThesisIds.add(thesis.id);

    if (!thesis.evidenceItemIds.length) errors.push(`Thesis ${thesis.id} has no evidence item.`);
    if (!thesis.citations.length) errors.push(`Thesis ${thesis.id} has missing citation chain.`);

    for (const evidenceItemId of thesis.evidenceItemIds) {
      if (!knownItems.has(evidenceItemId)) errors.push(`Thesis ${thesis.id} references unknown evidence item: ${evidenceItemId}`);
    }

    for (const citation of thesis.citations) {
      if (!knownItems.has(citation.evidenceItemId)) {
        errors.push(`Thesis ${thesis.id} citation references unknown evidence item: ${citation.evidenceItemId}`);
        continue;
      }

      if (!thesis.evidenceItemIds.includes(citation.evidenceItemId)) {
        errors.push(`Thesis ${thesis.id} citation does not belong to thesis evidence: ${citation.evidenceItemId}`);
      }

      if (!citationsByItem.get(citation.evidenceItemId)?.has(citationKey(citation))) {
        errors.push(`Thesis ${thesis.id} has missing citation chain for ${citation.evidenceItemId}.`);
      }
    }
  }

  return {
    ok: errors.length === 0,
    errors,
  };
}
