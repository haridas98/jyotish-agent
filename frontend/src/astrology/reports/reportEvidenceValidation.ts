import type { ReportEvidenceItem, ReportEvidencePack, ReportEvidenceSourceRef, ReportEvidenceValidationResult } from "./reportEvidenceTypes";

function duplicateValues(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

function refKey(ref: ReportEvidenceSourceRef): string {
  return `${ref.sourceId}:${ref.ruleId}:${ref.entityId ?? ""}`;
}

function itemHasFactorIdentity(item: ReportEvidenceItem): boolean {
  if (item.kind === "entity") return Boolean(item.entityId);
  if (item.kind === "calculation") return Boolean(item.calculationId);
  if (item.kind === "relationship_factor") return Boolean(item.relationshipFactorId);
  if (item.kind === "warning") return true;
  return false;
}

export function validateReportEvidencePack(pack: ReportEvidencePack): ReportEvidenceValidationResult {
  const errors: string[] = [];

  if (pack.schemaVersion !== 1) errors.push("Evidence pack schemaVersion must be 1");
  if (!pack.reportRecipeId) errors.push("Evidence pack must include reportRecipeId");
  if (!pack.reportRecipeVersion) errors.push("Evidence pack must include reportRecipeVersion");
  if (!pack.reportTypeId) errors.push("Evidence pack must include reportTypeId");
  if (!Array.isArray(pack.items)) errors.push("Evidence pack items must be an array");

  const itemIds = pack.items.map((item) => item.id);
  for (const duplicateId of duplicateValues(itemIds)) errors.push(`Duplicate evidence item id: ${duplicateId}`);
  const sortedItemIds = [...itemIds].sort();
  if (itemIds.join("\n") !== sortedItemIds.join("\n")) errors.push("Evidence items must be deterministically sorted by id");

  for (const item of pack.items) {
    if (!item.id) errors.push("Evidence item missing id");
    if (!item.label) errors.push(`Evidence item ${item.id} missing label`);
    if (!itemHasFactorIdentity(item)) errors.push(`Evidence item ${item.id} missing factor identity`);
    if (!item.provenance) errors.push(`Evidence item ${item.id} missing provenance`);
    if (item.provenance) {
      if (!item.provenance.origin) errors.push(`Evidence item ${item.id} missing provenance origin`);
      if (item.provenance.reportRecipeId !== pack.reportRecipeId) errors.push(`Evidence item ${item.id} has mismatched reportRecipeId`);
      if (item.provenance.reportRecipeVersion !== pack.reportRecipeVersion) errors.push(`Evidence item ${item.id} has mismatched reportRecipeVersion`);
      if (item.provenance.reportTypeId !== pack.reportTypeId) errors.push(`Evidence item ${item.id} has mismatched reportTypeId`);
      if (!Array.isArray(item.provenance.ruleIds)) errors.push(`Evidence item ${item.id} ruleIds must be an array`);
      if (!Array.isArray(item.provenance.sourceRefs)) errors.push(`Evidence item ${item.id} sourceRefs must be an array`);
    }
  }

  const sourceRefKeys = pack.sourceRefs.map(refKey);
  for (const duplicateRef of duplicateValues(sourceRefKeys)) errors.push(`Duplicate source ref: ${duplicateRef}`);
  const sortedSourceRefKeys = [...sourceRefKeys].sort();
  if (sourceRefKeys.join("\n") !== sortedSourceRefKeys.join("\n")) errors.push("Evidence sourceRefs must be deterministically sorted");

  const sourceRefSet = new Set(sourceRefKeys);
  for (const item of pack.items) {
    for (const ref of item.provenance.sourceRefs) {
      if (!sourceRefSet.has(refKey(ref))) errors.push(`Evidence item ${item.id} source ref is missing from pack sourceRefs`);
    }
  }

  for (const unavailableId of pack.unavailableItemIds) {
    if (!itemIds.includes(unavailableId)) errors.push(`Unavailable id does not reference an item: ${unavailableId}`);
  }

  const serialized = JSON.stringify(pack);
  const forbiddenMarkers = [
    "source" + ".pending",
    "owner" + "UserId",
    "pair" + "Key",
    "raw " + "evidence",
    "Спросить " + "AI",
    "Сгенерировать " + "AI",
  ];
  for (const forbidden of forbiddenMarkers) {
    if (serialized.includes(forbidden)) errors.push(`Evidence pack contains forbidden marker: ${forbidden}`);
  }

  return { ok: errors.length === 0, errors };
}
