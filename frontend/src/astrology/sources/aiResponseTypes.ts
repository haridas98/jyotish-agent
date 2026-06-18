import type { AiReportRequest } from "./aiRequestTypes";

export type AiReportConfidence = "low" | "medium" | "high";

export type AiReportThesisCitation = {
  evidenceItemId: string;
  ruleId: string;
  passageId: string;
  sourceId: string;
  citationLabel: string;
};

export type AiReportThesis = {
  id: string;
  title: string;
  body: string;
  evidenceItemIds: string[];
  citations: AiReportThesisCitation[];
  confidence: AiReportConfidence;
};

export type AiReportResponse = {
  schemaVersion: 1;
  requestSchemaVersion: AiReportRequest["schemaVersion"];
  provider: "mock";
  reportRecipeId: string;
  reportTypeId: AiReportRequest["reportTypeId"];
  theses: AiReportThesis[];
};

export type AiReportResponseValidationResult = {
  ok: boolean;
  errors: string[];
};
