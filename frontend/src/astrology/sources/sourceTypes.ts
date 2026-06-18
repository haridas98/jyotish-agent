export type SourceId = string;

export type SourceDefinition = {
  id: SourceId;
  title: {
    original?: string;
    ru: string;
    en: string;
  };
  shortTitle: string;
  sourceType: "primary_shastra" | "traditional_commentary" | "modern_commentary" | "research" | "internal_note";
  language: "sanskrit" | "english" | "russian" | "hindi" | "other";
  author?: string;
  referenceUrl?: string;
  retrievedAt?: string;
  fileSha256?: string;
  fileSizeBytes?: number;
  pageCount?: number;
  bibliographicStatus?: "unknown" | "partial" | "verified";
  fileIntegrityStatus?: "unverified" | "verified";
  edition?: {
    publisher?: string;
    year?: number;
    editor?: string;
    translator?: string;
    isbn?: string;
  };
  status: "draft" | "verified" | "disabled";
  accessPolicy: "metadata_only" | "locator_and_excerpt" | "full_text_allowed";
  notes?: string;
};
