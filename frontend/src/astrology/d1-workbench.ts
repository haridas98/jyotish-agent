import type { EntityId } from "@/astrology";
import type { BirthChart, ChartCalculationRecord, ChartProfile, GrahaPosition, HousePlacement, JyotishUserSettings, VargaAccuracyGate, VargaPlacement, VargaScopeCategory, VargaScopeMetadata } from "@/lib/api";

export const CHART_WORKBENCH_SCOPE_IDS = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D30", "D60"] as const;
export const CHART_WORKBENCH_EXPERT_SCOPE_IDS = ["D30", "D60"] as const;
export type ChartWorkbenchScopeId = (typeof CHART_WORKBENCH_SCOPE_IDS)[number];
export type D1ChartStyle = "north" | "south";
export type D1ReaderMode = "novice" | "astrologer";
export type D1TerminologyMode = "ru" | "en" | "sa" | "short";
export type D1DataTab = "overview" | "grahas" | "houses" | "nakshatras" | "technical";

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
  supportedScopes: ChartWorkbenchScopeId[];
  expertOnlyScopes: ChartWorkbenchScopeId[];
  vargaScopes: D1VargaScopeMetadata[];
  accuracyGates: Record<string, VargaAccuracyGate>;
  technical: D1TechnicalPayload;
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
  absoluteLongitude: string;
  speedLongitude: string;
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

export type D1VargaScopeMetadata = Omit<VargaScopeMetadata, "code"> & {
  code: ChartWorkbenchScopeId;
  category: VargaScopeCategory;
};

export type D1TechnicalPayload = {
  settings: D1TechnicalSummaryRow[];
  panchanga: D1TechnicalSummaryRow[];
  dashas: D1DashaSummaryRow[];
  vargas: D1VargaTechnicalRow[];
  houseCusps: D1HouseCuspRow[];
  classical: D1TechnicalSummaryRow[];
  solarDay: D1TechnicalSummaryRow[];
};

export type D1TechnicalSummaryRow = {
  key: string;
  label: string;
  value: string;
};

export type D1DashaSummaryRow = {
  lord: string;
  startsAt: string;
  endsAt: string;
  durationYears: number;
};

export type D1VargaTechnicalRow = {
  code: ChartWorkbenchScopeId;
  name: string;
  method: string;
  status: "available" | "missing";
  placementCount: number;
};

export type D1HouseCuspRow = {
  house: number;
  longitude: string;
  rashi: string;
};

type WorkbenchApiMeta = {
  supportedScopes?: string[];
  expertOnlyScopes?: string[];
  vargaScopes?: VargaScopeMetadata[];
  accuracyGates?: Record<string, VargaAccuracyGate>;
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
  D30: "D30 Trimsamsha",
  D60: "D60 Shashtyamsha",
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
  apiMeta: WorkbenchApiMeta | null = null,
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
  if (scope.scopeId === "D30") {
    warnings.push({ code: "d30_time_precision", message: "D30 чувствительна к точности времени; используйте её только при уверенном времени рождения.", severity: "warning" });
  }
  if (scope.scopeId === "D60") {
    warnings.push({ code: "d60_birth_time_accuracy", message: "D60 is expert-only and requires exact birth time.", severity: "critical" });
  }
  if (scope.missing) {
    warnings.push({ code: `${scope.scopeId.toLowerCase()}_absent`, message: `${scope.scopeId} пока отсутствует в сохранённом расчёте.`, severity: "warning" });
  }

  const grahas = buildGrahaRows(scope);
  const specialPoints = buildSpecialPointRows(scope);
  const houses = buildHouseCells(scope, grahas, specialPoints);
  const capabilities = buildCapabilities(grahas, specialPoints);
  const rashiCount = new Set(houses.map((house) => house.rashiIndex).filter((item): item is number => item !== null)).size;
  const supportedScopes = normalizeScopeList(apiMeta?.supportedScopes, [...CHART_WORKBENCH_SCOPE_IDS]);
  const expertOnlyScopes = normalizeScopeList(apiMeta?.expertOnlyScopes, [...CHART_WORKBENCH_EXPERT_SCOPE_IDS]);
  const vargaScopes = normalizeVargaScopes(apiMeta?.vargaScopes, supportedScopes, expertOnlyScopes);

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
      readerMode: CHART_WORKBENCH_EXPERT_SCOPE_IDS.includes(scope.scopeId as typeof CHART_WORKBENCH_EXPERT_SCOPE_IDS[number])
        ? "astrologer"
        : settings?.display.terminologyMode === "sanskrit" ? "astrologer" : "novice",
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
    supportedScopes,
    expertOnlyScopes,
    vargaScopes,
    accuracyGates: apiMeta?.accuracyGates ?? {},
    technical: buildTechnicalPayload(chart, vargaScopes),
  };
}

function isChartWorkbenchScopeId(value: string): value is ChartWorkbenchScopeId {
  return (CHART_WORKBENCH_SCOPE_IDS as readonly string[]).includes(value);
}

function normalizeScopeList(raw: string[] | undefined, fallback: ChartWorkbenchScopeId[]): ChartWorkbenchScopeId[] {
  const normalized = (raw ?? []).map((item) => item.toUpperCase()).filter(isChartWorkbenchScopeId);
  return normalized.length ? normalized : fallback;
}

function normalizeVargaScopes(raw: VargaScopeMetadata[] | undefined, supportedScopes: ChartWorkbenchScopeId[], expertOnlyScopes: ChartWorkbenchScopeId[]): D1VargaScopeMetadata[] {
  const supported = new Set(supportedScopes);
  const fromApi = (raw ?? [])
    .filter((item) => isChartWorkbenchScopeId(item.code) && supported.has(item.code))
    .map((item) => ({ ...item, code: item.code as ChartWorkbenchScopeId }));
  if (fromApi.length) return fromApi;
  const expert = new Set(expertOnlyScopes);
  return supportedScopes.map((code) => ({
    code,
    name: code === "D1" ? "Rashi" : VARGA_SCOPE_TITLES[code as Exclude<ChartWorkbenchScopeId, "D1">],
    category: expert.has(code) ? "expert" : code === "D10" ? "professional" : code === "D20" || code === "D24" ? "spiritual" : ["D3", "D7", "D9", "D12"].includes(code) ? "family" : "main",
    methodId: code === "D30" ? "varga.d30.parashara_unequal.v1" : code === "D60" ? "varga.d60.parashara_shashtyamsha.v1" : "varga.parashara_shodasha.v1",
    methodVersion: "1",
    calculationPreset: "parashara",
    expertOnly: expert.has(code),
    timeAccuracyRequired: code === "D60" ? "exact" : "",
  }));
}

function buildTechnicalPayload(chart: BirthChart | null, vargaScopes: D1VargaScopeMetadata[]): D1TechnicalPayload {
  if (!chart) {
    return {
      settings: [],
      panchanga: [],
      dashas: [],
      vargas: vargaScopes.map((scope) => ({
        code: scope.code,
        name: scope.name,
        method: scope.methodId,
        status: "missing",
        placementCount: 0,
      })),
      houseCusps: [],
      classical: [],
      solarDay: [],
    };
  }

  const settings = chart.settings;
  const panchanga = chart.panchanga;
  const solarDay = chart.solar_day;

  return {
    settings: compactRows([
      technicalRow("calculation_version", "Calculation version", chart.calculation_version),
      technicalRow("zodiac", "Zodiac", settings?.zodiac),
      technicalRow("ayanamsa", "Ayanamsa", settings?.ayanamsa),
      technicalRow("calculation_model", "Calculation model", settings?.calculation_model),
      technicalRow("node_type", "Node type", settings?.node_type),
      technicalRow("ephemeris", "Ephemeris", settings?.ephemeris),
      technicalRow("house_system", "House system", settings?.house_system),
      technicalRow("bhava_system", "Bhava system", settings?.bhava_system),
      technicalRow("varga_scheme", "Varga scheme", settings?.varga_scheme),
      technicalRow("sunrise_source", "Sunrise source", settings?.sunrise_source),
      technicalRow("timezone_source", "Timezone source", settings?.timezone_source),
      technicalRow("shadbala_profile", "Shadbala profile", settings?.shadbala_profile),
    ]),
    panchanga: compactRows([
      technicalRow("tithi", "Tithi", panchanga?.tithi ? `${panchanga.tithi.number}. ${panchanga.tithi.name} (${panchanga.tithi.paksha})` : undefined),
      technicalRow("vara", "Vara", panchanga?.vara?.name),
      technicalRow("nakshatra", "Nakshatra", panchanga?.nakshatra ? `${panchanga.nakshatra.name}${panchanga.nakshatra.pada ? ` pada ${panchanga.nakshatra.pada}` : ""}` : undefined),
      technicalRow("yoga", "Yoga", panchanga?.yoga ? `${panchanga.yoga.number}. ${panchanga.yoga.name}` : undefined),
      technicalRow("karana", "Karana", panchanga?.karana?.name),
    ]),
    dashas: (chart.dashas?.vimshottari?.mahadashas ?? []).slice(0, 9).map((period) => ({
      lord: period.lord,
      startsAt: period.starts_at,
      endsAt: period.ends_at,
      durationYears: period.duration_years,
    })),
    vargas: vargaScopes.map((scope) => {
      if (scope.code === "D1") {
        return {
          code: scope.code,
          name: scope.name,
          method: scope.methodId,
          status: "available",
          placementCount: chart.grahas.length + (chart.ascendant ? 1 : 0),
        };
      }
      const varga = chart.vargas?.[scope.code] ?? null;
      return {
        code: scope.code,
        name: varga?.name ?? scope.name,
        method: varga?.methodId ?? varga?.method ?? scope.methodId,
        status: varga ? "available" : "missing",
        placementCount: varga?.placements?.length ?? 0,
      };
    }),
    houseCusps: (chart.house_cusps ?? []).map((cusp) => ({
      house: cusp.house,
      longitude: formatLongitude(cusp.longitude),
      rashi: cusp.rashi,
    })),
    classical: buildClassicalRows(chart),
    solarDay: compactRows([
      technicalRow("date", "Solar date", solarDay?.date),
      technicalRow("sunrise", "Sunrise", solarDay?.sunrise),
      technicalRow("sunset", "Sunset", solarDay?.sunset),
      technicalRow("next_sunrise", "Next sunrise", solarDay?.next_sunrise),
      technicalRow("daylight_minutes", "Daylight minutes", solarDay?.daylight_minutes),
      technicalRow("night_minutes", "Night minutes", solarDay?.night_minutes),
      technicalRow("method", "Solar method", solarDay?.method),
      technicalRow("status", "Solar status", solarDay?.status),
    ]),
  };
}

function buildClassicalRows(chart: BirthChart): D1TechnicalSummaryRow[] {
  const classical = chart.classical;
  if (!classical) return [];
  return compactRows([
    technicalRow("avasthas", "Avasthas", statusWithCount(classical.avasthas?.status, classical.avasthas?.baladi?.length)),
    technicalRow("vimshopaka_bala", "Vimshopaka bala", statusWithCount(classical.vimshopaka_bala?.status, classical.vimshopaka_bala?.items?.length)),
    technicalRow("ashtakavarga", "Ashtakavarga", statusWithCount(classical.ashtakavarga?.status, classical.ashtakavarga?.sarva?.scores?.length)),
    technicalRow("shadbala", "Shadbala", statusWithCount(classical.shadbala?.status, classical.shadbala?.items?.length)),
    technicalRow("yogas", "Yogas", statusWithCount(classical.yogas?.status, classical.yogas?.summary?.detected_count ?? classical.yogas?.items?.length)),
    technicalRow("argala", "Argala", statusWithCount(classical.argala?.status, classical.argala?.primary?.length)),
    technicalRow("special_points", "Special points", statusWithCount(classical.special_points?.status, classical.special_points?.vedic_points?.items?.length)),
    technicalRow("transits", "Transits", classical.transits?.status),
    technicalRow("compatibility", "Compatibility", classical.compatibility?.status),
    technicalRow("muhurta", "Muhurta", classical.muhurta?.status),
  ]);
}

function technicalRow(key: string, label: string, value: unknown): D1TechnicalSummaryRow | null {
  if (value === undefined || value === null || value === "") return null;
  return { key, label, value: String(value) };
}

function compactRows(rows: Array<D1TechnicalSummaryRow | null>): D1TechnicalSummaryRow[] {
  return rows.filter((row): row is D1TechnicalSummaryRow => row !== null);
}

function statusWithCount(status: string | undefined, count: number | undefined): string | undefined {
  if (!status && count === undefined) return undefined;
  return count === undefined ? status : `${status ?? "available"} (${count})`;
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
    absoluteLongitude: longitude !== null ? formatLongitude(longitude) : "-",
    speedLongitude: typeof placement.speed_longitude === "number" ? formatSpeed(placement.speed_longitude) : "-",
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

function formatLongitude(longitude: number): string {
  return `${longitude.toFixed(6)}°`;
}

function formatSpeed(speed: number): string {
  return `${speed.toFixed(6)}°/day`;
}
