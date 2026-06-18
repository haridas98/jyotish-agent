import type { SourceDefinition, SourceId } from "./sourceTypes";

export const sourceDefinitions: SourceDefinition[] = [
  {
    id: "source.bphs",
    title: {
      original: "Bṛhat Parāśara Horā Śāstra",
      ru: "Брихат Парашара Хора Шастра",
      en: "Brihat Parashara Hora Shastra",
    },
    shortTitle: "BPHS",
    sourceType: "primary_shastra",
    language: "english",
    author: "Parashara",
    referenceUrl: "https://vedpuran.net/wp-content/uploads/2021/04/brihat_parashara_hora_shastra_english_v.pdf",
    edition: {
      publisher: "VedPuran public PDF mirror / Internet Archive text mirror",
      editor: "R. Santhanam-style English e-text",
    },
    status: "verified",
    accessPolicy: "locator_and_excerpt",
    notes: "Verified as a concrete public edition anchor for chapter/verse/page mapping; textual authenticity review remains separate.",
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
    notes: "Reserved for non-BPHS period-rule mapping; not used as verified evidence in the pilot.",
  },
];

const sourceMap = new Map(sourceDefinitions.map((source) => [source.id, source]));

export function getSource(id: SourceId): SourceDefinition | null {
  return sourceMap.get(id) ?? null;
}

export function listSources(): SourceDefinition[] {
  return sourceDefinitions.filter((source) => source.status !== "disabled");
}
