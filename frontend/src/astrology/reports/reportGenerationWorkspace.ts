export const REPORT_WORKSPACE_SCHEMA_VERSION = "jyotish-report-workspace-v1" as const;

export type ReportIntentId =
  | "short_report"
  | "deep_report"
  | "question_answer"
  | "relationship_report"
  | "business_timing";

export type GuidanceModeId = "general" | "devotee";
export type ReportWorkspaceStatus = "ready" | "blocked" | "not_available";

export type ReportWorkspaceReadinessInput = {
  selectedChartId: number | null;
  selectedRelationshipId: number | null;
  selectedReportTypeId: string;
  selectedRecipeId: string;
  intentId: ReportIntentId;
  guidanceMode: GuidanceModeId;
  questionText?: string;
};

export type ReportWorkspaceReadiness = {
  schemaVersion: typeof REPORT_WORKSPACE_SCHEMA_VERSION;
  status: ReportWorkspaceStatus;
  blockedReasons: string[];
  requiredContext: string[];
  requestDraft: {
    reportTypeId: string;
    recipeId: string;
    chartId: number | null;
    relationshipId: number | null;
    intentId: ReportIntentId;
    guidanceMode: GuidanceModeId;
    hasQuestion: boolean;
  };
};

export const reportIntents: Array<{
  id: ReportIntentId;
  label: string;
  summary: string;
  requiresQuestion?: boolean;
  requiresRelationship?: boolean;
  available?: boolean;
}> = [
  { id: "short_report", label: "Короткий отчет", summary: "Сжатый обзор по выбранной карте." },
  { id: "deep_report", label: "Глубокий отчет", summary: "Расширенная структура на основе рецепта." },
  { id: "question_answer", label: "Вопрос", summary: "Подготовка ответа на конкретный вопрос.", requiresQuestion: true },
  { id: "relationship_report", label: "Отношения", summary: "Разбор с учетом сохраненной связи.", requiresRelationship: true },
  { id: "business_timing", label: "Деловое время", summary: "Пока готовится как отдельный muhurta/transit flow.", available: false },
];

export const guidanceModes: Array<{ id: GuidanceModeId; label: string; summary: string }> = [
  { id: "general", label: "Общий", summary: "Нейтральный практический тон." },
  { id: "devotee", label: "Преданный", summary: "Контекст садханы без расширенной интерпретации." },
];

export function buildReportWorkspaceReadiness(input: ReportWorkspaceReadinessInput): ReportWorkspaceReadiness {
  const intent = reportIntents.find((item) => item.id === input.intentId) ?? reportIntents[0];
  const blockedReasons: string[] = [];
  const requiredContext = ["chart", "report_recipe"];
  const question = input.questionText?.trim() ?? "";

  if (!input.selectedChartId) blockedReasons.push("Выберите сохраненную карту.");
  if (intent.requiresQuestion) {
    requiredContext.push("question");
    if (!question) blockedReasons.push("Добавьте текст вопроса.");
  }
  if (intent.requiresRelationship) {
    requiredContext.push("relationship");
    if (!input.selectedRelationshipId) blockedReasons.push("Выберите сохраненную связь.");
  }
  if (intent.available === false) {
    requiredContext.push("business_timing_context");
    blockedReasons.push("Деловое время пока готовится в отдельном разделе.");
  }

  return {
    schemaVersion: REPORT_WORKSPACE_SCHEMA_VERSION,
    status: intent.available === false ? "not_available" : blockedReasons.length ? "blocked" : "ready",
    blockedReasons,
    requiredContext,
    requestDraft: {
      reportTypeId: input.selectedReportTypeId,
      recipeId: input.selectedRecipeId,
      chartId: input.selectedChartId,
      relationshipId: input.selectedRelationshipId,
      intentId: input.intentId,
      guidanceMode: input.guidanceMode,
      hasQuestion: Boolean(question),
    },
  };
}
