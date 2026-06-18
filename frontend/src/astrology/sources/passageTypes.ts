import type { SourceId } from "./sourceTypes";

export type PassageId = string;

export type PassageLocator = {
  chapter?: string;
  verseStart?: string;
  verseEnd?: string;
  section?: string;
  page?: number;
  volume?: string;
};

export type PassageDefinition = {
  id: PassageId;
  sourceId: SourceId;
  locator: PassageLocator;
  citationLabel: {
    ru: string;
    en: string;
  };
  originalText?: string;
  translations?: {
    ru?: string;
    en?: string;
  };
  shortExcerpt?: {
    ru?: string;
    en?: string;
  };
  contentChecksum?: string;
  status: "draft" | "verified" | "disputed" | "disabled";
  verificationNotes?: string;
};
