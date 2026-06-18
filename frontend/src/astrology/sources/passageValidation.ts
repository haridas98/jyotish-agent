import { getSource } from "./sourceRegistry";
import { passageDefinitions } from "./passageRegistry";

function duplicates(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

function hasLocator(value: object): boolean {
  return Object.values(value).some((part) => part !== null && part !== undefined && String(part).trim().length > 0);
}

export function validatePassageRegistry(): string[] {
  const errors: string[] = [];
  for (const id of duplicates(passageDefinitions.map((passage) => passage.id))) errors.push(`Duplicate passage id: ${id}`);
  for (const passage of passageDefinitions) {
    if (!getSource(passage.sourceId)) errors.push(`Passage ${passage.id} references unknown source ${passage.sourceId}`);
    if (passage.status === "verified" && !hasLocator(passage.locator)) errors.push(`Verified passage ${passage.id} needs locator`);
    if (!passage.citationLabel.ru || !passage.citationLabel.en) errors.push(`Passage ${passage.id} needs citation labels`);
  }
  return errors;
}
