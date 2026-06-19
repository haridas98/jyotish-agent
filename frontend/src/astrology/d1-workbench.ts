import type { EntityId } from "@/astrology";
import type { BirthChart, ChartCalculationRecord, ChartProfile, GrahaPosition, HousePlacement, JyotishUserSettings, VargaPlacement } from "@/lib/api";

export const CHART_WORKBENCH_SCOPE_IDS = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24"] as const;
export type ChartWorkbenchScopeId = (typeof CHART_WORKBENCH_SCOPE_IDS)[number];
export type D1ChartStyle = "north" | "south";
export type D1ReaderMode = "novice" | "astrologer";
export type D1TerminologyMode = "ru" | "en" | "sa" | "short";
export type D1DataTab = "overview" | "grahas" | "houses" | "nakshatras";

export type D1WorkbenchModel = {
  schemaVersion: "d1-workbench.v1";
  scopeId: ChartWorkbenchScopeId;
  profile: {
    id: number;
    title: string;
    birthDate: string;
    birthTime: string;
    birthTimeAccuracy: string;
    place: string;
    timezone: string;
    calculationPreset: string;
  };
  calculation: {
    status: string;
    version: string;
    updatedAt: string | null;
  };
  defaults: {
    chartStyle: D1ChartStyle;
    readerMode: D1ReaderMode;
    terminologyMode: D1TerminologyMode;
  };
  capabilities: D1WorkbenchCapabilities;
  stats: {
    houseCount: number;
    rashiCount: number;
    grahaCount: number;
    specialPointCount: number;
    chartObjectCount: number;
  };
  houses: D1HouseCell[];
  grahas: D1GrahaRow[];
  specialPoints: D1SpecialPointRow[];
  warnings: D1Warning[];
};

export type D1WorkbenchCapabilities = {
  degrees: boolean;
  nakshatrasAvailable: boolean;
  padasAvailable: boolean;
  dignityAvailable: boolean;
  retrogradeAvailable: boolean;
  navamsaAvailable: boolean;
};

export type D1HouseCell = {
  house: number;
  houseEntityId: EntityId;
  rashiIndex: number | null;
  rashiName: string;
  rashiEntityId: EntityId | null;
  grahaCodes: string[];
  specialPointCodes: string[];
};

export type D1GrahaRow = D1PlacementRow & {
  kind: "graha";
  entityId: EntityId;
};

export type D1SpecialPointRow = D1PlacementRow & {
  kind: "special_point";
  entityId: EntityId;
};

type D1PlacementRow = {
  body: string;
  code: string;
  label: string;
  shortLabel: string;
  placementEntityId: EntityId | null;
  longitude: number | null;
  degreeInSign: string;
  rashiName: string;
  rashiIndex: number | null;
  rashiEntityId: EntityId | null;
  house: number | null;
  houseEntityId: EntityId | null;
  nakshatra: string | null;
  nakshatraEntityId: EntityId | null;
  pada: number | null;
  dignity: string | null;
  retrograde: boolean;
  navamsa: string | null;
};

export type D1Warning = {
  code: string;
  message: string;
  severity: "info" | "warning" | "critical";
};

type NormalizedPlacement = Partial<GrahaPosition> & Partial<VargaPlacement> & {
  body: string;
  rashi: string;
  rashi_index?: number;
};

type ScopeSource = {
  scopeId: ChartWorkbenchScopeId;
  title: string;
  houses: HousePlacement[];
  grahaPlacements: NormalizedPlacement[];
  specialPointPlacements: NormalizedPlacement[];
  missing: boolean;
};

const RASHI_ENTITY_NAMES = [
  "Aries",
  "Taurus",
  "Gemini",
  "Cancer",
  "Leo",
  "Virgo",
  "Libra",
  "Scorpio",
  "Sagittarius",
  "Capricorn",
  "Aquarius",
  "Pisces",
] as const;

const RASHI_SANSKRIT_NAMES = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"] as const;
const GRAHA_ORDER = ["SU", "MO", "MA", "ME", "JU", "VE", "SA", "RA", "KE"];
const SPECIAL_POINT_ORDER = ["LAGNA"];

const VARGA_SCOPE_TITLES: Record<Exclude<ChartWorkbenchScopeId, "D1">, string> = {
  D2: "D2 Hora",
  D3: "D3 Drekkana",
  D4: "D4 Chaturthamsha",
  D7: "D7 Saptamsa",
  D9: "D9 Navamsa",
  D10: "D10 Dashamsa",
  D12: "D12 Dvadashamsha",
  D16: "D16 Shodashamsha",
  D20: "D20 Vimshamsha",
  D24: "D24 Siddhamsha",
};

type BodyMeta = { code: string; entityId: EntityId; label: string; shortLabel: string; kind: "graha" | "special_point" };

const BODY_MAP: Record<string, BodyMeta> = {
  Ascendant: { code: "LAGNA", entityId: "point.LAGNA" as EntityId, label: "Лагна", shortLabel: "As", kind: "special_point" },
  Lagna: { code: "LAGNA", entityId: "point.LAGNA" as EntityId, label: "Лагна", shortLabel: "As", kind: "special_point" },
  Sun: { code: "SU", entityId: "graha.SU", label: "Солнце", shortLabel: "Su", kind: "graha" },
  Surya: { code: "SU", entityId: "graha.SU", label: "Солнце", shortLabel: "Su", kind: "graha" },
  Moon: { code: "MO", entityId: "graha.MO", label: "Луна", shortLabel: "Mo", kind: "graha" },
  Chandra: { code: "MO", entityId: "graha.MO", label: "Луна", shortLabel: "Mo", kind: "graha" },
  Mars: { code: "MA", entityId: "graha.MA", label: "Марс", shortLabel: "Ma", kind: "graha" },
  Mangala: { code: "MA", entityId: "graha.MA", label: "Марс", shortLabel: "Ma", kind: "graha" },
  Mercury: { code: "ME", entityId: "graha.ME", label: "Меркурий", shortLabel: "Me", kind: "graha" },
  Budha: { code: "ME", entityId: "graha.ME", label: "Меркурий", shortLabel: "Me", kind: "graha" },
  Jupiter: { code: "JU", entityId: "graha.JU", label: "Юпитер", shortLabel: "Ju", kind: "graha" },
  Guru: { code: "JU", entityId: "graha.JU", label: "Юпитер", shortLabel: "Ju", kind: "graha" },
  Venus: { code: "VE", entityId: "graha.VE", label: "Венера", shortLabel: "Ve", kind: "graha" },
  Shukra: { code: "VE", entityId: "graha.VE", label: "Венера", shortLabel: "Ve", kind: "graha" },
  Saturn: { code: "SA", entityId: "graha.SA", label: "Сатурн", shortLabel: "Sa", kind: "graha" },
  Shani: { code: "SA", entityId: "graha.SA", label: "Сатурн", shortLabel: "Sa", kind: "graha" },
  Rahu: { code: "RA", entityId: "graha.RA", label: "Раху", shortLabel: "Ra", kind: "graha" },
  Ketu: { code: "KE", entityId: "graha.KE", label: "Кету", shortLabel: "Ke", kind: "graha" },
};

export function buildD1WorkbenchModel(
  profile: ChartProfile,
  settings: JyotishUserSettings | null,
  calculationResult: ChartCalculationRecord | null,
  scopeId: ChartWorkbenchScopeId = "D1",
): D1WorkbenchModel {
  const chart = calculationResult?.result ?? null;
  const scope = buildScopeSource(chart, scopeId);
  const warnings: D1Warning[] = [];
  if (!chart) {
    warnings.push({ code: "calculation_absent", message: "Для этой карты ещё нет сохранённого расчёта.", severity: "warning" });
  }
  if (profile.birth_time_accuracy !== "exact") {
    warnings.push({ code: "birth_time_accuracy", message: "Время рождения не отмечено как точное; дома и Лагна требуют осторожности.", severity: "warning" });
  }
  if (scope.missing) {
    warnings.push({ code: `${scope.scopeId.toLowerCase()}_absent`, message: `${scope.scopeId} пока отсутствует в сохранённом расчёте.`, severity: "warning" });
  }

  const grahas = buildGrahaRows(scope);
  const specialPoints = buildSpecialPointRows(scope);
  const houses = buildHouseCells(scope, grahas, specialPoints);
  const capabilities = buildCapabilities(grahas, specialPoints);
  const rashiCount = new Set(houses.map((house) => house.rashiIndex).filter((item): item is number => item !== null)).size;

  return {
    schemaVersion: "d1-workbench.v1",
    scopeId: scope.scopeId,
    profile: {
      id: profile.id,
      title: profile.display_name,
      birthDate: profile.birth_date,
      birthTime: profile.birth_time ?? "время не указано",
      birthTimeAccuracy: profile.birth_time_accuracy,
      place: profile.place.label,
      timezone: profile.timezone,
      calculationPreset: profile.calculation_settings?.calculation_model ?? chart?.settings?.calculation_model ?? "drik_siddhanta",
    },
    calculation: {
      status: calculationResult?.status ?? profile.latest_calculation?.status ?? "not_calculated",
      version: calculationResult?.calculation_version ?? profile.latest_calculation?.calculation_version ?? "нет",
      updatedAt: calculationResult?.updated_at ?? profile.latest_calculation?.updated_at ?? null,
    },
    defaults: {
      chartStyle: settings?.display.chartStyle === "south_indian" ? "south" : "north",
      readerMode: settings?.display.terminologyMode === "sanskrit" ? "astrologer" : "novice",
      terminologyMode: terminologyDefault(settings),
    },
    capabilities,
    stats: {
      houseCount: houses.length,
      rashiCount,
      grahaCount: grahas.length,
      specialPointCount: specialPoints.length,
      chartObjectCount: grahas.length + specialPoints.length,
    },
    houses,
    grahas,
    specialPoints,
    warnings,
  };
}

function buildScopeSource(chart: BirthChart | null, scopeId: ChartWorkbenchScopeId): ScopeSource {
  if (scopeId !== "D1") {
    const varga = chart?.vargas?.[scopeId] ?? null;
    const placements = (varga?.placements ?? []) as NormalizedPlacement[];
    const specialPointPlacements = placements.filter((item) => isLagnaBody(item.body));
    const grahaPlacements = placements.filter((item) => !isLagnaBody(item.body));
    return {
      scopeId,
      title: VARGA_SCOPE_TITLES[scopeId],
      houses: buildVargaHouses(specialPointPlacements[0] ?? null),
      grahaPlacements,
      specialPointPlacements,
      missing: !varga,
    };
  }
  return {
    scopeId: "D1",
    title: "D1 Rashi",
    houses: chart?.houses ?? [],
    grahaPlacements: (chart?.grahas ?? []) as NormalizedPlacement[],
    specialPointPlacements: chart?.ascendant ? [{ ...chart.ascendant, body: chart.ascendant.body || "Lagna" }] : [],
    missing: !chart,
  };
}


function buildVargaHouses(lagna: NormalizedPlacement | null): HousePlacement[] {
  const lagnaIndex = normalizeRashiIndex(lagna?.rashi_index) ?? rashiIndexByName(lagna?.rashi ?? "");
  if (!lagnaIndex) return [];
  return Array.from({ length: 12 }, (_, index) => {
    const rashiIndex = ((lagnaIndex - 1 + index) % 12) + 1;
    return { house: index + 1, rashi_index: rashiIndex - 1, rashi: RASHI_SANSKRIT_NAMES[rashiIndex - 1] };
  });
}

function buildGrahaRows(scope: ScopeSource): D1GrahaRow[] {
  return scope.grahaPlacements
    .map((placement) => buildPlacementRow(scope, placement, "graha"))
    .filter((row): row is D1GrahaRow => row.kind === "graha")
    .sort((a, b) => orderOf(a.code) - orderOf(b.code) || a.code.localeCompare(b.code));
}

function buildSpecialPointRows(scope: ScopeSource): D1SpecialPointRow[] {
  return scope.specialPointPlacements
    .map((placement) => buildPlacementRow(scope, placement, "special_point"))
    .filter((row): row is D1SpecialPointRow => row.kind === "special_point")
    .sort((a, b) => specialPointOrderOf(a.code) - specialPointOrderOf(b.code) || a.code.localeCompare(b.code));
}

function buildPlacementRow(scope: ScopeSource, placement: NormalizedPlacement, expectedKind: "graha" | "special_point"): D1GrahaRow | D1SpecialPointRow {
  const meta = BODY_MAP[placement.body] ?? { code: placement.body.slice(0, 2).toUpperCase(), entityId: "graha.SU" as EntityId, label: placement.body, shortLabel: placement.body.slice(0, 2), kind: "graha" as const };
  const rashiIndex = normalizeRashiIndex(placement.rashi_index) ?? rashiIndexByName(placement.rashi);
  const house = houseForRashiIndex(scope.houses, rashiIndex);
  const houseEntityId = house ? (`house.${house}` as EntityId) : null;
  const longitude = typeof placement.longitude === "number" ? placement.longitude : null;
  const common = {
    body: placement.body,
    code: meta.code,
    label: meta.label,
    shortLabel: meta.shortLabel,
    entityId: meta.kind === "graha" ? grahaEntityId(placement.body) : meta.entityId,
    placementEntityId: house && meta.kind === "graha" ? (`placement.${meta.code}.house.${house}` as EntityId) : null,
    longitude,
    degreeInSign: longitude !== null ? formatDegreeInSign(longitude) : "-",
    rashiName: placement.rashi,
    rashiIndex,
    rashiEntityId: rashiEntityId(rashiIndex),
    house,
    houseEntityId,
    nakshatra: placement.nakshatra || null,
    nakshatraEntityId: placement.nakshatra ? (`nakshatra.${placement.nakshatra}` as EntityId) : null,
    pada: placement.pada ?? null,
    dignity: placement.dignity ?? null,
    retrograde: Boolean(placement.retrograde),
    navamsa: placement.navamsa || null,
  };
  if (meta.kind !== expectedKind) {
    return { ...common, kind: meta.kind } as D1GrahaRow | D1SpecialPointRow;
  }
  return { ...common, kind: meta.kind } as D1GrahaRow | D1SpecialPointRow;
}

function buildHouseCells(scope: ScopeSource, grahas: D1GrahaRow[], specialPoints: D1SpecialPointRow[]): D1HouseCell[] {
  const sourceHouses = scope.houses.length ? scope.houses : Array.from({ length: 12 }, (_, index) => ({ house: index + 1, rashi_index: index, rashi: RASHI_ENTITY_NAMES[index] }));
  const houses = sourceHouses.map((source) => {
    const houseNumber = source.house;
    const rashiIndex = normalizeRashiIndex(source.rashi_index) ?? rashiIndexByName(source.rashi ?? "");
    return {
      house: houseNumber,
      houseEntityId: `house.${houseNumber}` as EntityId,
      rashiIndex,
      rashiName: source.rashi ?? "-",
      rashiEntityId: rashiEntityId(rashiIndex),
      grahaCodes: grahas.filter((graha) => graha.house === houseNumber).map((graha) => graha.code).sort((a, b) => orderOf(a) - orderOf(b)),
      specialPointCodes: specialPoints.filter((point) => point.house === houseNumber).map((point) => point.code),
    } satisfies D1HouseCell;
  });
  return houses.sort((a, b) => a.house - b.house);
}

function buildCapabilities(grahas: D1GrahaRow[], specialPoints: D1SpecialPointRow[]): D1WorkbenchCapabilities {
  const rows = [...grahas, ...specialPoints];
  return {
    degrees: rows.some((row) => row.longitude !== null),
    nakshatrasAvailable: rows.some((row) => Boolean(row.nakshatra)),
    padasAvailable: rows.some((row) => row.pada !== null),
    dignityAvailable: grahas.some((row) => Boolean(row.dignity)),
    retrogradeAvailable: grahas.some((row) => row.retrograde),
    navamsaAvailable: rows.some((row) => Boolean(row.navamsa)),
  };
}

function terminologyDefault(settings: JyotishUserSettings | null): D1TerminologyMode {
  if (settings?.display.terminologyMode === "sanskrit") return "sa";
  return "ru";
}

function isLagnaBody(body: string): boolean {
  return body === "Lagna" || body === "Ascendant";
}

function grahaEntityId(body: string): EntityId {
  const meta = BODY_MAP[body];
  return meta?.kind === "graha" ? meta.entityId : ("graha.SU" as EntityId);
}

function houseForRashiIndex(houses: HousePlacement[], rashiIndex: number | null): number | null {
  if (!rashiIndex) return null;
  return houses.find((house) => normalizeRashiIndex(house.rashi_index) === rashiIndex)?.house ?? null;
}

function normalizeRashiIndex(index: number | null | undefined): number | null {
  if (index === null || index === undefined) return null;
  if (index >= 0 && index <= 11) return index + 1;
  if (index >= 1 && index <= 12) return index;
  return null;
}

function rashiIndexByName(name: string): number | null {
  const englishIndex = RASHI_ENTITY_NAMES.findIndex((item) => item.toLowerCase() === name.toLowerCase());
  if (englishIndex >= 0) return englishIndex + 1;
  const sanskritIndex = RASHI_SANSKRIT_NAMES.findIndex((item) => item.toLowerCase() === name.toLowerCase());
  return sanskritIndex >= 0 ? sanskritIndex + 1 : null;
}

function rashiEntityId(index: number | null): EntityId | null {
  if (!index) return null;
  return `rashi.${RASHI_ENTITY_NAMES[index - 1] ?? "Aries"}` as EntityId;
}

function orderOf(code: string): number {
  const index = GRAHA_ORDER.indexOf(code);
  return index >= 0 ? index : 99;
}

function specialPointOrderOf(code: string): number {
  const index = SPECIAL_POINT_ORDER.indexOf(code);
  return index >= 0 ? index : 99;
}

function formatDegreeInSign(longitude: number): string {
  const within = ((longitude % 30) + 30) % 30;
  const degree = Math.floor(within);
  const minute = Math.round((within - degree) * 60);
  return `${degree.toString().padStart(2, "0")}°${minute.toString().padStart(2, "0")}'`;
}
