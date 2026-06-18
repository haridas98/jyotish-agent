import { getSource } from "./sourceRegistry";
import { passageDefinitions } from "./passageRegistry";

function duplicates(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

function hasLocator(value: object): boolean {
  return Object.values(value).some((part) => part !== null && part !== undefined && String(part).trim().length > 0);
}

function hasPreciseLocator(value: { chapter?: string; verseStart?: string; page?: number }): boolean {
  return Boolean(value.page || (value.chapter && value.verseStart));
}

function locatorKey(passage: { sourceId: string; locator: { chapter?: string; verseStart?: string; verseEnd?: string; section?: string; page?: number } }): string {
  const locator = passage.locator;
  return [passage.sourceId, locator.chapter ?? "", locator.verseStart ?? "", locator.verseEnd ?? "", locator.section ?? "", locator.page ?? ""].join(":");
}

export function validatePassageRegistry(): string[] {
  const errors: string[] = [];
  for (const id of duplicates(passageDefinitions.map((passage) => passage.id))) errors.push(`Duplicate passage id: ${id}`);
  for (const key of duplicates(passageDefinitions.map((passage) => locatorKey(passage)))) errors.push(`Duplicate passage locator: ${key}`);
  for (const passage of passageDefinitions) {
    const source = getSource(passage.sourceId);
    if (!source) errors.push(`Passage ${passage.id} references unknown source ${passage.sourceId}`);
    if (passage.status === "verified" && !hasLocator(passage.locator)) errors.push(`Verified passage ${passage.id} needs locator`);
    if (passage.status === "verified" && !hasPreciseLocator(passage.locator)) errors.push(`Verified passage ${passage.id} needs chapter/verse or page locator`);
    if (passage.status === "verified" && source?.status !== "verified") errors.push(`Verified passage ${passage.id} needs verified source`);
    if (!passage.citationLabel.ru || !passage.citationLabel.en) errors.push(`Passage ${passage.id} needs citation labels`);
  }
  return errors;
}
