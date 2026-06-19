import type { EntityId } from "@/astrology";
import type { BirthChart, ChartCalculationRecord, ChartProfile, GrahaPosition, HousePlacement, JyotishUserSettings } from "@/lib/api";

export type D1ChartStyle = "north" | "south";
export type D1ReaderMode = "novice" | "astrologer";

export type D1WorkbenchModel = {
  schemaVersion: "d1-workbench.v1";
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
  };
  houses: D1HouseCell[];
  grahas: D1GrahaRow[];
  warnings: D1Warning[];
};

export type D1HouseCell = {
  house: number;
  houseEntityId: EntityId;
  rashiIndex: number | null;
  rashiName: string;
  rashiEntityId: EntityId | null;
  grahaCodes: string[];
};

export type D1GrahaRow = {
  body: string;
  code: string;
  label: string;
  entityId: EntityId;
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

const GRAHA_ORDER = ["AS", "SU", "MO", "MA", "ME", "JU", "VE", "SA", "RA", "KE"];

const BODY_MAP: Record<string, { code: string; entityId: EntityId; label: string }> = {
  Ascendant: { code: "AS", entityId: "house.1", label: "Лагна" },
  Lagna: { code: "AS", entityId: "house.1", label: "Лагна" },
  Sun: { code: "SU", entityId: "graha.SU", label: "Солнце" },
  Surya: { code: "SU", entityId: "graha.SU", label: "Солнце" },
  Moon: { code: "MO", entityId: "graha.MO", label: "Луна" },
  Chandra: { code: "MO", entityId: "graha.MO", label: "Луна" },
  Mars: { code: "MA", entityId: "graha.MA", label: "Марс" },
  Mangala: { code: "MA", entityId: "graha.MA", label: "Марс" },
  Mercury: { code: "ME", entityId: "graha.ME", label: "Меркурий" },
  Budha: { code: "ME", entityId: "graha.ME", label: "Меркурий" },
  Jupiter: { code: "JU", entityId: "graha.JU", label: "Юпитер" },
  Guru: { code: "JU", entityId: "graha.JU", label: "Юпитер" },
  Venus: { code: "VE", entityId: "graha.VE", label: "Венера" },
  Shukra: { code: "VE", entityId: "graha.VE", label: "Венера" },
  Saturn: { code: "SA", entityId: "graha.SA", label: "Сатурн" },
  Shani: { code: "SA", entityId: "graha.SA", label: "Сатурн" },
  Rahu: { code: "RA", entityId: "graha.RA", label: "Раху" },
  Ketu: { code: "KE", entityId: "graha.KE", label: "Кету" },
};

export function buildD1WorkbenchModel(
  profile: ChartProfile,
  settings: JyotishUserSettings | null,
  calculationResult: ChartCalculationRecord | null,
): D1WorkbenchModel {
  const chart = calculationResult?.result ?? null;
  const warnings: D1Warning[] = [];
  if (!chart) {
    warnings.push({ code: "calculation_absent", message: "Для этой карты ещё нет сохранённого расчёта.", severity: "warning" });
  }
  if (profile.birth_time_accuracy !== "exact") {
    warnings.push({ code: "birth_time_accuracy", message: "Время рождения не отмечено как точное; дома и Лагна требуют осторожности.", severity: "warning" });
  }
  if (chart && !chart.ascendant) {
    warnings.push({ code: "lagna_absent", message: "В расчёте нет Лагны.", severity: "critical" });
  }

  const grahas = buildGrahaRows(chart);
  const houses = buildHouseCells(chart, grahas);

  return {
    schemaVersion: "d1-workbench.v1",
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
    },
    houses,
    grahas,
    warnings,
  };
}

function buildGrahaRows(chart: BirthChart | null): D1GrahaRow[] {
  const placements = chart ? ([chart.ascendant ? { ...chart.ascendant, body: "Ascendant" } : null, ...chart.grahas].filter(Boolean) as GrahaPosition[]) : [];
  return placements
    .map((placement) => buildGrahaRow(chart, placement))
    .sort((a, b) => orderOf(a.code) - orderOf(b.code) || a.code.localeCompare(b.code));
}

function buildGrahaRow(chart: BirthChart | null, placement: GrahaPosition): D1GrahaRow {
  const meta = BODY_MAP[placement.body] ?? { code: placement.body.slice(0, 2).toUpperCase(), entityId: "graha.SU" as EntityId, label: placement.body };
  const rashiIndex = normalizeRashiIndex(placement.rashi_index) ?? rashiIndexByName(placement.rashi);
  const house = houseForRashiIndex(chart?.houses ?? [], rashiIndex);
  const houseEntityId = house ? (`house.${house}` as EntityId) : null;
  return {
    body: placement.body,
    code: meta.code,
    label: meta.label,
    entityId: grahaEntityId(placement.body),
    placementEntityId: house && meta.code !== "AS" ? (`placement.${meta.code}.house.${house}` as EntityId) : null,
    longitude: typeof placement.longitude === "number" ? placement.longitude : null,
    degreeInSign: typeof placement.longitude === "number" ? formatDegreeInSign(placement.longitude) : "-",
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
}

function grahaEntityId(body: string): EntityId {
  return (BODY_MAP[body]?.entityId ?? "graha.SU") as EntityId;
}

function buildHouseCells(chart: BirthChart | null, grahas: D1GrahaRow[]): D1HouseCell[] {
  const houses = Array.from({ length: 12 }, (_, index) => {
    const houseNumber = index + 1;
    const source = chart?.houses.find((item) => item.house === houseNumber) ?? null;
    const rashiIndex = normalizeRashiIndex(source?.rashi_index) ?? rashiIndexByName(source?.rashi ?? "");
    return {
      house: houseNumber,
      houseEntityId: `house.${houseNumber}` as EntityId,
      rashiIndex,
      rashiName: source?.rashi ?? "-",
      rashiEntityId: rashiEntityId(rashiIndex),
      grahaCodes: grahas.filter((graha) => graha.house === houseNumber).map((graha) => graha.code).sort((a, b) => orderOf(a) - orderOf(b)),
    } satisfies D1HouseCell;
  });
  return houses.sort((a, b) => a.house - b.house);
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
  const index = RASHI_ENTITY_NAMES.findIndex((item) => item.toLowerCase() === name.toLowerCase());
  return index >= 0 ? index + 1 : null;
}

function rashiEntityId(index: number | null): EntityId | null {
  if (!index) return null;
  return `rashi.${RASHI_ENTITY_NAMES[index - 1] ?? "Aries"}` as EntityId;
}

function orderOf(code: string): number {
  const index = GRAHA_ORDER.indexOf(code);
  return index >= 0 ? index : 99;
}

function formatDegreeInSign(longitude: number): string {
  const within = ((longitude % 30) + 30) % 30;
  const degree = Math.floor(within);
  const minute = Math.round((within - degree) * 60);
  return `${degree.toString().padStart(2, "0")}°${minute.toString().padStart(2, "0")}'`;
}