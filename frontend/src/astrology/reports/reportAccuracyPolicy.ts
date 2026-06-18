import type { CalculationId } from "../calculations";
import type { ReportCalculationFactor, ReportCondition } from "./reportRecipeTypes";

export function isD60Calculation(calculationId: CalculationId): boolean {
  return calculationId === "calc.varga.D60";
}

export function hasAccuracyCondition(conditions: ReportCondition[] | undefined): boolean {
  return (conditions ?? []).some((condition) => condition.type === "birth_time_accuracy");
}

export function resolveReportD60Visibility(input: {
  mode: "novice" | "astrologer";
  primaryBirthTimeAccuracy?: string | null;
  relationshipBirthTimeAccuracies?: Array<string | null | undefined>;
}): { visible: boolean; warningRequired: boolean } {
  if (input.mode !== "astrologer") return { visible: false, warningRequired: false };
  const primaryExact = input.primaryBirthTimeAccuracy === "exact";
  const relationshipExact = (input.relationshipBirthTimeAccuracies ?? []).every((accuracy) => accuracy === "exact");
  return { visible: primaryExact && relationshipExact, warningRequired: true };
}

export function validateD60Factor(factor: ReportCalculationFactor): string[] {
  if (!isD60Calculation(factor.calculationId)) return [];
  const errors: string[] = [];
  if (factor.required) errors.push("D60 calculation cannot be required");
  if (factor.priority === "primary") errors.push("D60 calculation cannot be primary");
  if (factor.visibleInModes.includes("novice")) errors.push("D60 calculation cannot be visible in novice mode");
  if (!hasAccuracyCondition(factor.conditions)) errors.push("D60 calculation must have birth time accuracy condition");
  return errors;
}
