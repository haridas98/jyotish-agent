import type { BirthChart, GrahaPosition } from "@/lib/api";
import { getEntity } from "../entities";
import { getRelationshipFactor, getRelationshipRecipe, type RecipeFocus } from "../relationships";
import type { ReportEvidenceBuilderInput, ReportEvidenceItem, ReportEvidencePack, ReportEvidenceSourceRef } from "./reportEvidenceTypes";
import type { ResolvedReportFactor } from "./reportRecipeTypes";

function isBirthChart(value: unknown): value is BirthChart {
  return Boolean(value && typeof value === "object" && Array.isArray((value as BirthChart).grahas));
}

function itemId(parts: Array<string | number | null | undefined>): string {
  return parts.filter((part) => part !== null && part !== undefined && String(part).length > 0).join(".");
}

function sourceRef(sourceId: string, ruleId: string, entityId?: string): ReportEvidenceSourceRef {
  return {
    sourceId,
    ruleId,
    entityId: entityId as ReportEvidenceSourceRef["entityId"],
    status: "needs_review",
  };
}

function entityRuleIds(entityId: string): string[] {
  if (entityId.startsWith("house.")) return [`bphs.${entityId}`];
  if (entityId.startsWith("graha.")) return [`bphs.${entityId.toLowerCase()}`];
  if (entityId.startsWith("varga.")) return [`jyotish.classical.${entityId}`];
  return [`jyotish.classical.${entityId}`];
}

function calculationRuleIds(calculationId: string): string[] {
  if (calculationId.startsWith("calc.varga.")) return [`jyotish.classical.${calculationId.replace("calc.", "")}`];
  if (calculationId === "calc.vimshottari") return ["vimshottari.sequence"];
  return [`jyotish.calculation.${calculationId}`];
}

function refsForRules(ruleIds: string[], entityId?: string): ReportEvidenceSourceRef[] {
  return ruleIds.map((ruleId) => {
    if (ruleId.startsWith("bphs.")) return sourceRef("bphs", ruleId, entityId);
    if (ruleId.startsWith("vimshottari.")) return sourceRef("tradition", ruleId, entityId);
    return sourceRef("jyotish.classical", ruleId, entityId);
  });
}

function grahaForEntity(chart: BirthChart, entityId: string): GrahaPosition | null {
  const code = entityId.replace("graha.", "");
  const names: Record<string, string[]> = {
    SU: ["Surya", "Sun"],
    MO: ["Chandra", "Moon"],
    MA: ["Mangala", "Mars"],
    ME: ["Budha", "Mercury"],
    JU: ["Guru", "Jupiter"],
    VE: ["Shukra", "Venus"],
    SA: ["Shani", "Saturn"],
    RA: ["Rahu"],
    KE: ["Ketu"],
  };
  return chart.grahas.find((graha) => (names[code] ?? []).includes(graha.body)) ?? null;
}

function valueForEntity(entityId: string, chart: BirthChart | null): unknown {
  if (!chart) return null;
  if (entityId.startsWith("house.")) {
    const houseNumber = Number(entityId.replace("house.", ""));
    return chart.houses.find((house) => house.house === houseNumber) ?? null;
  }
  if (entityId.startsWith("graha.")) return grahaForEntity(chart, entityId);
  if (entityId.startsWith("varga.")) return chart.vargas?.[entityId.replace("varga.", "")] ?? null;
  return null;
}

function valueForCalculation(calculationId: string, chart: BirthChart | null): unknown {
  if (!chart) return null;
  if (calculationId.startsWith("calc.varga.")) return chart.vargas?.[calculationId.replace("calc.varga.", "")] ?? null;
  if (calculationId === "calc.vimshottari") return chart.dashas?.vimshottari ?? null;
  if (calculationId === "calc.houses") return chart.houses;
  if (calculationId === "calc.planetPositions") return chart.grahas;
  if (calculationId === "calc.nakshatras") return chart.grahas;
  if (calculationId === "calc.panchanga") return chart.panchanga;
  if (calculationId === "calc.dignities") return chart.grahas.map((graha) => ({ body: graha.body, dignity: graha.dignity ?? null }));
  return null;
}

function ruleIdsForRelationshipFactor(factorId: string, focuses: RecipeFocus[]): string[] {
  return Array.from(new Set(focuses.filter((focus) => focus.relationshipFactorIds.includes(factorId as never)).flatMap((focus) => focus.ruleIds)));
}

function sourceRefsFromItems(items: ReportEvidenceItem[]): ReportEvidenceSourceRef[] {
  const refs = items.flatMap((item) => item.provenance.sourceRefs);
  const seen = new Set<string>();
  return refs.filter((ref) => {
    const key = `${ref.sourceId}:${ref.ruleId}:${ref.entityId ?? ""}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function buildReportEvidencePack(input: ReportEvidenceBuilderInput): ReportEvidencePack {
  const chart = isBirthChart(input.primaryChart) ? input.primaryChart : null;
  const relationshipRecipe = input.selectedRelationship ? getRelationshipRecipe(input.selectedRelationship.relationshipTypeId) : null;
  const relationshipFocuses = relationshipRecipe ? [relationshipRecipe.perspectiveAtoB, relationshipRecipe.perspectiveBtoA, relationshipRecipe.mutualFocus] : [];
  const items: ReportEvidenceItem[] = [];

  for (const section of input.resolvedRecipe.sections) {
    for (const group of section.factorGroups) {
      for (const factor of group.factors) {
        items.push(buildEvidenceItem(factor, section.sectionId, group.id, input, chart, relationshipFocuses));
      }
    }
  }

  for (const warning of input.resolvedRecipe.warnings) {
    const ruleIds = ["report.policy.birth_time_accuracy"];
    items.push({
      id: itemId(["warning", input.resolvedRecipe.recipeId, warning.type]),
      kind: "warning",
      label: warning.label.ru,
      priority: "warning",
      value: warning.label,
      available: true,
      provenance: {
        origin: "report_policy",
        reportRecipeId: input.resolvedRecipe.recipeId,
        reportRecipeVersion: input.resolvedRecipe.recipeVersion,
        reportTypeId: input.resolvedRecipe.reportTypeId,
        ruleIds,
        sourceRefs: refsForRules(ruleIds),
      },
      warnings: [],
    });
  }

  const warnings = [
    ...input.resolvedRecipe.warnings.map((warning) => warning.label.ru),
    ...items.flatMap((item) => item.warnings),
  ];

  return {
    schemaVersion: 1,
    reportRecipeId: input.resolvedRecipe.recipeId,
    reportRecipeVersion: input.resolvedRecipe.recipeVersion,
    reportTypeId: input.resolvedRecipe.reportTypeId,
    mode: input.mode,
    profileIds: [input.primaryProfileId].filter((id): id is string | number => id !== null && id !== undefined).map(String),
    relationshipId: input.selectedRelationship?.id === null || input.selectedRelationship?.id === undefined ? undefined : String(input.selectedRelationship.id),
    relationshipTypeId: input.selectedRelationship?.relationshipTypeId,
    items,
    warnings,
    unavailableItemIds: items.filter((item) => !item.available).map((item) => item.id),
    sourceRefs: sourceRefsFromItems(items),
    inputSummary: {
      hasPrimaryChart: Boolean(chart),
      hasRelationshipContext: Boolean(input.selectedRelationship),
      resolvedSectionCount: input.resolvedRecipe.sections.length,
      resolvedFactorCount: input.resolvedRecipe.sections.flatMap((section) => section.factorGroups.flatMap((group) => group.factors)).length,
    },
  };
}

function buildEvidenceItem(
  factor: ResolvedReportFactor,
  sectionId: string,
  groupId: string,
  input: ReportEvidenceBuilderInput,
  chart: BirthChart | null,
  relationshipFocuses: RecipeFocus[],
): ReportEvidenceItem {
  if (factor.kind === "entity") {
    const definition = getEntity(factor.entityId);
    const ruleIds = entityRuleIds(factor.entityId);
    const value = valueForEntity(factor.entityId, chart);
    return {
      id: itemId(["entity", sectionId, groupId, factor.entityId]),
      kind: "entity",
      label: definition?.terms.ru ?? definition?.terms.short ?? factor.entityId,
      priority: factor.priority,
      entityId: factor.entityId,
      value,
      available: value !== null,
      provenance: {
        origin: value === null ? "report_recipe" : "chart_calculation",
        reportRecipeId: input.resolvedRecipe.recipeId,
        reportRecipeVersion: input.resolvedRecipe.recipeVersion,
        reportTypeId: input.resolvedRecipe.reportTypeId,
        sectionId,
        groupId,
        ruleIds,
        sourceRefs: refsForRules(ruleIds, factor.entityId),
      },
      warnings: value === null ? ["Фактор есть в структуре отчёта, но данных карты пока нет."] : [],
    };
  }

  if (factor.kind === "calculation") {
    const ruleIds = calculationRuleIds(factor.calculationId);
    const value = valueForCalculation(factor.calculationId, chart);
    return {
      id: itemId(["calculation", sectionId, groupId, factor.calculationId]),
      kind: "calculation",
      label: factor.calculationId,
      priority: factor.priority,
      calculationId: factor.calculationId,
      value,
      available: value !== null,
      provenance: {
        origin: value === null ? "report_recipe" : "chart_calculation",
        reportRecipeId: input.resolvedRecipe.recipeId,
        reportRecipeVersion: input.resolvedRecipe.recipeVersion,
        reportTypeId: input.resolvedRecipe.reportTypeId,
        sectionId,
        groupId,
        ruleIds,
        sourceRefs: refsForRules(ruleIds),
      },
      warnings: value === null ? ["Расчёт включён в структуру, но результат пока недоступен."] : [],
    };
  }

  if (factor.kind === "relationship_factor") {
    const definition = getRelationshipFactor(factor.relationshipFactorId);
    const ruleIds = ruleIdsForRelationshipFactor(factor.relationshipFactorId, relationshipFocuses);
    return {
      id: itemId(["relationship", sectionId, groupId, factor.relationshipFactorId]),
      kind: "relationship_factor",
      label: definition?.label.ru ?? definition?.label.en ?? "Фактор связи",
      priority: factor.priority,
      relationshipFactorId: factor.relationshipFactorId,
      value: {
        relationshipTypeId: input.selectedRelationship?.relationshipTypeId,
        status: definition?.status ?? "planned",
      },
      available: Boolean(input.selectedRelationship),
      provenance: {
        origin: "relationship_recipe",
        reportRecipeId: input.resolvedRecipe.recipeId,
        reportRecipeVersion: input.resolvedRecipe.recipeVersion,
        reportTypeId: input.resolvedRecipe.reportTypeId,
        sectionId,
        groupId,
        relationshipTypeId: input.selectedRelationship?.relationshipTypeId,
        ruleIds,
        sourceRefs: refsForRules(ruleIds),
      },
      warnings: ruleIds.length ? [] : ["Для фактора связи ещё не указаны rule references."],
    };
  }

  return {
    id: itemId(["relationship-context", sectionId, groupId]),
    kind: "relationship_factor",
    label: "Контекст связи",
    priority: "optional",
    value: null,
    available: false,
    provenance: {
      origin: "report_recipe",
      reportRecipeId: input.resolvedRecipe.recipeId,
      reportRecipeVersion: input.resolvedRecipe.recipeVersion,
      reportTypeId: input.resolvedRecipe.reportTypeId,
      sectionId,
      groupId,
      ruleIds: [],
      sourceRefs: [],
    },
    warnings: ["Связь не выбрана."],
  };
}
