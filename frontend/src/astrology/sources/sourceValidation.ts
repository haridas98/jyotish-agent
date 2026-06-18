import { sourceDefinitions } from "./sourceRegistry";

function duplicates(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

export function validateSourceRegistry(): string[] {
  const errors: string[] = [];
  for (const id of duplicates(sourceDefinitions.map((source) => source.id))) errors.push(`Duplicate source id: ${id}`);
  for (const source of sourceDefinitions) {
    if (!source.title.ru || !source.title.en) errors.push(`Source ${source.id} needs public labels`);
    if (source.status === "verified" && !source.edition) errors.push(`Verified source ${source.id} needs edition metadata`);
  }
  return errors;
}
