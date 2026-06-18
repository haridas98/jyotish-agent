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
      ru: "Раздел определяет Лагну как восходящий знак и указывает, что результаты читаются на основе Лагны и грах.",
      en: "The section defines Lagna as the rising sign and says results are read from Lagna and the grahas.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public PDF anchor; cites chapter, verse range and PDF page.",
  },
  {
    id: "passage.bphs.sun_moon.karakatva",
    sourceId: "source.bphs",
    locator: { chapter: "3", verseStart: "12", verseEnd: "13", page: 6 },
    citationLabel: {
      ru: "БПХШ 3.12-13",
      en: "BPHS 3.12-13",
    },
    shortExcerpt: {
      ru: "В этом месте Солнце названо атмой, а Луна — умом.",
      en: "In this passage the Sun is named as the soul and the Moon as the mind.",
    },
    status: "verified",
    verificationNotes: "Single shared passage reused by Sun and Moon rules; broader claims require separate passages.",
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
    verificationNotes: "Verified against the selected BPHS public PDF anchor.",
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
      ru: "Раздел задаёт области чтения варг: тело через Лагну, супруг/супруга через Навамшу.",
      en: "The section assigns reading domains to vargas: body through Lagna and spouse through Navamsha.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public PDF anchor.",
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
      ru: "Раздел описывает применимость Вимшоттари, порядок управителей, длительность махадаш и остаток даши при рождении.",
      en: "The section describes Vimshottari applicability, planetary order, mahadasha durations, and the balance at birth.",
    },
    status: "verified",
    verificationNotes: "Verified against the selected BPHS public PDF anchor.",
  },
];

const passageMap = new Map(passageDefinitions.map((passage) => [passage.id, passage]));

export function getPassage(id: PassageId): PassageDefinition | null {
  return passageMap.get(id) ?? null;
}

export function listPassages(): PassageDefinition[] {
  return passageDefinitions.filter((passage) => passage.status !== "disabled");
}
