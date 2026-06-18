import { registerExistingChartCalculationModules, hasCalculationModule } from "../calculations";
import { getEntity, registerCoreEntities } from "../entities";
import { getPassage } from "./passageRegistry";
import { getSource } from "./sourceRegistry";
import { ruleDefinitions } from "./ruleRegistry";

function duplicates(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

export function validateRuleRegistry(): string[] {
  registerCoreEntities();
  registerExistingChartCalculationModules();

  const errors: string[] = [];
  for (const id of duplicates(ruleDefinitions.map((rule) => rule.id))) errors.push(`Duplicate rule id: ${id}`);
  for (const rule of ruleDefinitions) {
    for (const entityId of rule.appliesToEntityIds) {
      if (!getEntity(entityId)) errors.push(`Rule ${rule.id} references unknown entity ${entityId}`);
    }
    for (const calculationId of rule.requiredCalculationIds) {
      if (!hasCalculationModule(calculationId)) errors.push(`Rule ${rule.id} references unknown calculation ${calculationId}`);
    }
    const passages = rule.passageIds.map((passageId) => getPassage(passageId));
    for (const [index, passage] of passages.entries()) {
      if (!passage) errors.push(`Rule ${rule.id} references unknown passage ${rule.passageIds[index]}`);
    }
    if (rule.status === "verified") {
      if (!passages.length) errors.push(`Verified rule ${rule.id} needs verified passage`);
      if (passages.some((passage) => passage?.status !== "verified")) errors.push(`Verified rule ${rule.id} references unverified passage`);
      for (const passage of passages) {
        const source = passage ? getSource(passage.sourceId) : null;
        if (source?.status === "disabled") errors.push(`Verified rule ${rule.id} uses disabled source ${source.id}`);
      }
    }
    const serialized = JSON.stringify(rule);
    for (const forbidden of ["source" + ".pending", "AI prompt", "Jagannatha Hora", "Parashara's Light"]) {
      if (serialized.includes(forbidden)) errors.push(`Rule ${rule.id} contains forbidden marker ${forbidden}`);
    }
  }
  return errors;
}
