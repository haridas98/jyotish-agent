import type { SourceDefinition, SourceId } from "./sourceTypes";

export const sourceDefinitions: SourceDefinition[] = [
  {
    id: "source.bphs",
    title: {
      original: "Brihat Parashara Hora Shastra",
      ru: "Брихат Парашара Хора Шастра",
      en: "Brihat Parashara Hora Shastra",
    },
    shortTitle: "BPHS",
    sourceType: "primary_shastra",
    language: "sanskrit",
    author: "Parashara",
    edition: {
      editor: "pilot metadata",
    },
    status: "draft",
    accessPolicy: "metadata_only",
    notes: "Pilot source metadata only; exact edition mapping is still under review.",
  },
  {
    id: "source.vimshottari.tradition",
    title: {
      ru: "Классическая традиция Вимшоттари",
      en: "Classical Vimshottari tradition",
    },
    shortTitle: "Vimshottari",
    sourceType: "internal_note",
    language: "other",
    status: "draft",
    accessPolicy: "metadata_only",
    notes: "Placeholder for structured period rules before exact source passages are verified.",
  },
];

const sourceMap = new Map(sourceDefinitions.map((source) => [source.id, source]));

export function getSource(id: SourceId): SourceDefinition | null {
  return sourceMap.get(id) ?? null;
}

export function listSources(): SourceDefinition[] {
  return sourceDefinitions.filter((source) => source.status !== "disabled");
}
