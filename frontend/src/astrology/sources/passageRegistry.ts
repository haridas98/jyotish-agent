import type { PassageDefinition, PassageId } from "./passageTypes";

export const passageDefinitions: PassageDefinition[] = [
  {
    id: "passage.bphs.lagna.general",
    sourceId: "source.bphs",
    locator: { chapter: "3", verseStart: "4", verseEnd: "9", page: 5 },
    citationLabel: {
      ru: "БПХШ 3.4-9",
      en: "BPHS 3.4-9",
    },
    shortExcerpt: {
      ru: "Раздел задаёт Лагну как восходящий знак и основу чтения карты рождения.",
      en: "The section defines Lagna as the rising sign and a foundation for reading the birth chart.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public edition anchor; cites chapter, verse range and page.",
  },
  {
    id: "passage.bphs.moon.general",
    sourceId: "source.bphs",
    locator: { chapter: "3", verseStart: "12", verseEnd: "13", page: 6 },
    citationLabel: {
      ru: "БПХШ 3.12-13",
      en: "BPHS 3.12-13",
    },
    shortExcerpt: {
      ru: "Раздел описывает природные значения Солнца и Луны среди каракатв грах.",
      en: "The section describes the natural significations of the Sun and Moon among graha karakatvas.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public edition anchor; Moon rule uses this shared graha-signification passage.",
  },
  {
    id: "passage.bphs.sun.general",
    sourceId: "source.bphs",
    locator: { chapter: "3", verseStart: "12", verseEnd: "13", page: 6 },
    citationLabel: {
      ru: "БПХШ 3.12-13",
      en: "BPHS 3.12-13",
    },
    shortExcerpt: {
      ru: "Раздел описывает природные значения Солнца и Луны среди каракатв грах.",
      en: "The section describes the natural significations of the Sun and Moon among graha karakatvas.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public edition anchor; Sun rule uses this shared graha-signification passage.",
  },
  {
    id: "passage.bphs.varga.sixteen.names",
    sourceId: "source.bphs",
    locator: { chapter: "6", verseStart: "2", verseEnd: "4", page: 17 },
    citationLabel: {
      ru: "БПХШ 6.2-4",
      en: "BPHS 6.2-4",
    },
    shortExcerpt: {
      ru: "Раздел перечисляет шестнадцать варг, включая Раши и Навамшу.",
      en: "The section lists the sixteen vargas, including Rashi and Navamsha.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public edition anchor.",
  },
  {
    id: "passage.bphs.varga.uses",
    sourceId: "source.bphs",
    locator: { chapter: "7", verseStart: "1", verseEnd: "8", page: 20 },
    citationLabel: {
      ru: "БПХШ 7.1-8",
      en: "BPHS 7.1-8",
    },
    shortExcerpt: {
      ru: "Раздел задаёт области чтения варг; Лагна читается по Раши, супруг/супруга — по Навамше.",
      en: "The section assigns reading domains to vargas; Lagna is read from Rashi and spouse from Navamsha.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public edition anchor.",
  },
  {
    id: "passage.vimshottari.sequence.general",
    sourceId: "source.bphs",
    locator: { chapter: "46", verseStart: "2", verseEnd: "16", page: 138 },
    citationLabel: {
      ru: "БПХШ 46.2-16",
      en: "BPHS 46.2-16",
    },
    shortExcerpt: {
      ru: "Раздел описывает применимость Вимшоттари, порядок управителей и продолжительность махадаш.",
      en: "The section describes Vimshottari applicability, planetary order, and mahadasha durations.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public edition anchor.",
  },
];

const passageMap = new Map(passageDefinitions.map((passage) => [passage.id, passage]));

export function getPassage(id: PassageId): PassageDefinition | null {
  return passageMap.get(id) ?? null;
}

export function listPassages(): PassageDefinition[] {
  return passageDefinitions.filter((passage) => passage.status !== "disabled");
}
