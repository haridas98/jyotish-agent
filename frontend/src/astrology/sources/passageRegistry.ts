import type { PassageDefinition, PassageId } from "./passageTypes";

export const passageDefinitions: PassageDefinition[] = [
  {
    id: "passage.bphs.lagna.general",
    sourceId: "source.bphs",
    locator: { section: "Lagna and house significations" },
    citationLabel: {
      ru: "БПХШ, раздел о Лагне",
      en: "BPHS, section on Lagna",
    },
    shortExcerpt: {
      ru: "Лагна используется как основа чтения тела, характера и направления жизни.",
      en: "Lagna is used as a basis for reading body, temperament, and life direction.",
    },
    status: "verified",
    verificationNotes: "Pilot locator is section-level until chapter/verse mapping is completed.",
  },
  {
    id: "passage.bphs.moon.general",
    sourceId: "source.bphs",
    locator: { section: "Graha significations" },
    citationLabel: {
      ru: "БПХШ, значения Луны",
      en: "BPHS, Moon significations",
    },
    shortExcerpt: {
      ru: "Луна связывается с умом, восприятием и питанием жизни.",
      en: "The Moon is connected with mind, perception, and nourishment.",
    },
    status: "verified",
  },
  {
    id: "passage.bphs.sun.general",
    sourceId: "source.bphs",
    locator: { section: "Graha significations" },
    citationLabel: {
      ru: "БПХШ, значения Солнца",
      en: "BPHS, Sun significations",
    },
    shortExcerpt: {
      ru: "Солнце связывается с атмой, отцом, властью и жизненной силой.",
      en: "The Sun is connected with atma, father, authority, and vitality.",
    },
    status: "draft",
  },
  {
    id: "passage.vimshottari.sequence.general",
    sourceId: "source.vimshottari.tradition",
    locator: { section: "Mahadasha sequence" },
    citationLabel: {
      ru: "Традиционная последовательность Вимшоттари",
      en: "Traditional Vimshottari sequence",
    },
    status: "draft",
  },
];

const passageMap = new Map(passageDefinitions.map((passage) => [passage.id, passage]));

export function getPassage(id: PassageId): PassageDefinition | null {
  return passageMap.get(id) ?? null;
}

export function listPassages(): PassageDefinition[] {
  return passageDefinitions.filter((passage) => passage.status !== "disabled");
}
