export type GrahaEntityId =
  | "graha.SU"
  | "graha.MO"
  | "graha.MA"
  | "graha.ME"
  | "graha.JU"
  | "graha.VE"
  | "graha.SA"
  | "graha.RA"
  | "graha.KE";

export type HouseEntityId = `house.${1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12}`;
export type RashiEntityId = `rashi.${string}`;
export type NakshatraEntityId = `nakshatra.${string}`;
export type VargaEntityId = `varga.${string}`;
export type PlacementEntityId = `placement.${string}.house.${number}` | `placement.${string}.rashi.${string}`;
export type DashaEntityId = `dasha.${string}`;
export type YogaEntityId = `yoga.${string}`;
export type RelationshipEntityId = `relationship.${string}`;

export type EntityId =
  | GrahaEntityId
  | HouseEntityId
  | RashiEntityId
  | NakshatraEntityId
  | VargaEntityId
  | PlacementEntityId
  | DashaEntityId
  | YogaEntityId
  | RelationshipEntityId;

export type EntityKind =
  | "graha"
  | "house"
  | "rashi"
  | "nakshatra"
  | "varga"
  | "placement"
  | "dasha"
  | "yoga"
  | "relationship";

export type EntityTermSet = {
  short: string;
  ru: string;
  en?: string;
  sa?: string;
  devanagari?: string;
};

export type EntityDefinition = {
  id: EntityId;
  kind: EntityKind;
  terms: EntityTermSet;
  summary: string;
  warning?: string;
  sourceIds?: string[];
};
