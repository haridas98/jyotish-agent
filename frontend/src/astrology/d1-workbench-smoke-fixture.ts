import { buildD1WorkbenchModel } from "@/astrology/d1-workbench";
import type { BirthChart, ChartCalculationRecord, ChartProfile, JyotishUserSettings, VargaScopeMetadata } from "@/lib/api";

export const D1_WORKBENCH_SMOKE_CHART_ID = "demo-d1";
export const D1_WORKBENCH_SMOKE_ROUTE = "/charts/demo-d1";
export const D1_WORKBENCH_SMOKE_STATUS = "P107-A read-only D1 chart detail smoke fixture; no saved chart record is created.";

const calculationSettings: NonNullable<BirthChart["settings"]> = {
  zodiac: "sidereal",
  calculation_model: "drik_siddhanta",
  ayanamsa: "lahiri",
  node_type: "mean",
  ephemeris: "internal_smoke_fixture",
  house_system: "whole_sign",
  bhava_system: "whole_sign",
  varga_scheme: "parashara",
  sunrise_source: "not_used",
  timezone_source: "fixture",
  shadbala_profile: "not_used",
};

const profile: ChartProfile = {
  id: 107,
  display_name: "P107-A D1 smoke fixture",
  birth_date: "1990-08-15",
  birth_time: "10:24:00",
  birth_time_accuracy: "exact",
  gender: "unknown",
  timezone: "Asia/Kolkata",
  is_self_profile: false,
  notes: "read-only D1 chart detail smoke fixture",
  calculation_settings: calculationSettings,
  place: {
    id: 107,
    external_id: "p107-demo-d1",
    name: "Vrindavan",
    label: "Vrindavan, India",
    country_code: "IN",
    latitude: 27.565,
    longitude: 77.659,
    timezone: "Asia/Kolkata",
  },
  latest_calculation: {
    id: 107,
    status: "fixture_ready",
    calculation_version: "p107-d1-smoke.v1",
    graha_count: 9,
    created_at: "2026-06-23T00:00:00Z",
    updated_at: "2026-06-23T00:00:00Z",
  },
  created_at: "2026-06-23T00:00:00Z",
  updated_at: "2026-06-23T00:00:00Z",
};

const chart: BirthChart = {
  calculation_version: "p107-d1-smoke.v1",
  settings: calculationSettings,
  birth: {
    date: "1990-08-15",
    time: "10:24:00",
    timezone: "Asia/Kolkata",
    local_datetime: "1990-08-15T10:24:00+05:30",
    utc_datetime: "1990-08-15T04:54:00Z",
    utc_offset: "+05:30",
  },
  place: {
    id: "p107-demo-d1",
    name: "Vrindavan",
    label: "Vrindavan, India",
    country_code: "IN",
    latitude: 27.565,
    longitude: 77.659,
  },
  houses: [
    { house: 1, rashi_index: 4, rashi: "Cancer" },
    { house: 2, rashi_index: 5, rashi: "Leo" },
    { house: 3, rashi_index: 6, rashi: "Virgo" },
    { house: 4, rashi_index: 7, rashi: "Libra" },
    { house: 5, rashi_index: 8, rashi: "Scorpio" },
    { house: 6, rashi_index: 9, rashi: "Sagittarius" },
    { house: 7, rashi_index: 10, rashi: "Capricorn" },
    { house: 8, rashi_index: 11, rashi: "Aquarius" },
    { house: 9, rashi_index: 12, rashi: "Pisces" },
    { house: 10, rashi_index: 1, rashi: "Aries" },
    { house: 11, rashi_index: 2, rashi: "Taurus" },
    { house: 12, rashi_index: 3, rashi: "Gemini" },
  ],
  ascendant: { body: "Lagna", longitude: 103.25, latitude: null, speed_longitude: null, rashi: "Cancer", rashi_index: 4, nakshatra: "Pushya", nakshatra_index: 8, pada: 2, navamsa: "Virgo", navamsa_index: 6 },
  grahas: [
    { body: "Sun", longitude: 118.4, latitude: null, speed_longitude: null, rashi: "Cancer", rashi_index: 4, nakshatra: "Ashlesha", nakshatra_index: 9, pada: 1, navamsa: "Sagittarius", navamsa_index: 9 },
    { body: "Moon", longitude: 331.2, latitude: null, speed_longitude: null, rashi: "Aquarius", rashi_index: 11, nakshatra: "Purva Bhadrapada", nakshatra_index: 25, pada: 3, navamsa: "Gemini", navamsa_index: 3 },
    { body: "Mars", longitude: 64.7, latitude: null, speed_longitude: null, rashi: "Gemini", rashi_index: 3, nakshatra: "Ardra", nakshatra_index: 6, pada: 2, navamsa: "Capricorn", navamsa_index: 10 },
    { body: "Mercury", longitude: 141.8, latitude: null, speed_longitude: null, rashi: "Leo", rashi_index: 5, nakshatra: "Purva Phalguni", nakshatra_index: 11, pada: 4, navamsa: "Scorpio", navamsa_index: 8 },
    { body: "Jupiter", longitude: 91.1, latitude: null, speed_longitude: null, rashi: "Cancer", rashi_index: 4, nakshatra: "Punarvasu", nakshatra_index: 7, pada: 4, navamsa: "Cancer", navamsa_index: 4, dignity: "exalted" },
    { body: "Venus", longitude: 172.6, latitude: null, speed_longitude: null, rashi: "Virgo", rashi_index: 6, nakshatra: "Hasta", nakshatra_index: 13, pada: 2, navamsa: "Taurus", navamsa_index: 2 },
    { body: "Saturn", longitude: 281.3, latitude: null, speed_longitude: null, rashi: "Capricorn", rashi_index: 10, nakshatra: "Uttara Ashadha", nakshatra_index: 21, pada: 3, navamsa: "Aquarius", navamsa_index: 11, retrograde: true, dignity: "own" },
    { body: "Rahu", longitude: 35.5, latitude: null, speed_longitude: null, rashi: "Taurus", rashi_index: 2, nakshatra: "Rohini", nakshatra_index: 4, pada: 1, navamsa: "Aries", navamsa_index: 1, retrograde: true },
    { body: "Ketu", longitude: 215.5, latitude: null, speed_longitude: null, rashi: "Scorpio", rashi_index: 8, nakshatra: "Anuradha", nakshatra_index: 17, pada: 3, navamsa: "Libra", navamsa_index: 7, retrograde: true },
  ],
  panchanga: {},
};

const calculation: ChartCalculationRecord = {
  id: 107,
  profile_id: 107,
  calculation_version: "p107-d1-smoke.v1",
  ayanamsa: "lahiri",
  house_system: "whole_sign",
  status: "fixture_ready",
  error: "",
  result: chart,
  created_at: "2026-06-23T00:00:00Z",
  updated_at: "2026-06-23T00:00:00Z",
};

const settings: JyotishUserSettings = {
  id: 107,
  userId: 107,
  calculation: {
    ayanamsa: "lahiri",
    zodiacType: "sidereal",
    houseSystem: "whole_sign",
    nodeType: "mean",
    calculationProfile: "default",
    divisionalChartsEnabled: ["D1"],
    defaultDivisionalChart: "D1",
    timezoneMode: "birth_place_timezone",
  },
  display: {
    chartStyle: "south_indian",
    language: "en",
    terminologyMode: "mixed",
    degreeFormat: "dms",
    showSanskritNames: true,
    showTransliteration: true,
    themeMode: "system",
  },
  createdAt: "2026-06-23T00:00:00Z",
  updatedAt: "2026-06-23T00:00:00Z",
};

const vargaScopes: VargaScopeMetadata[] = [
  {
    code: "D1",
    name: "Rashi",
    category: "main",
    methodId: "p107.read_only.fixture",
    methodVersion: "1",
    calculationPreset: "smoke_fixture",
    expertOnly: false,
    timeAccuracyRequired: "exact",
  },
];

export function buildD1WorkbenchSmokeModel() {
  return buildD1WorkbenchModel(profile, settings, calculation, "D1", {
    supportedScopes: ["D1"],
    expertOnlyScopes: [],
    vargaScopes,
    accuracyGates: {
      D1: {
        scopeId: "D1",
        status: "fixture_only",
        requiredBirthTimeAccuracy: "exact",
        actualBirthTimeAccuracy: "exact",
        reason: "P107-A read-only chart detail smoke path",
      },
    },
  });
}
