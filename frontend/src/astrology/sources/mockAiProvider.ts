import type { AiReportRequest } from "./aiRequestTypes";
import type { AiReportResponse } from "./aiResponseTypes";
import { validateAiReportResponse } from "./aiResponseValidation";

export type MockAiDryRunResult = {
  request: AiReportRequest;
  response: AiReportResponse;
  validation: ReturnType<typeof validateAiReportResponse>;
};

export function runMockAiDryRun(request: AiReportRequest): MockAiDryRunResult {
  const theses = request.items.map((item, index) => ({
    id: `mock.thesis.${String(index + 1).padStart(2, "0")}.${item.evidenceItemId}`,
    title: `Проверочный тезис: ${item.label}`,
    body: `Offline dry run confirms that ${item.label} can be cited from verified evidence only.`,
    evidenceItemIds: [item.evidenceItemId],
    citations: item.citationChains.map((citation) => ({
      evidenceItemId: item.evidenceItemId,
      ...citation,
    })),
    confidence: "medium" as const,
  }));

  const response: AiReportResponse = {
    schemaVersion: 1,
    requestSchemaVersion: request.schemaVersion,
    provider: "mock",
    reportRecipeId: request.reportRecipeId,
    reportTypeId: request.reportTypeId,
    theses,
  };

  return {
    request,
    response,
    validation: validateAiReportResponse(request, response),
  };
}
