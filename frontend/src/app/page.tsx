"use client";

import { FormEvent, useCallback, useEffect, useId, useMemo, useRef, useState, type Dispatch, type KeyboardEvent as ReactKeyboardEvent, type ReactNode, type RefObject, type SetStateAction } from "react";
import {
  askBirthCodexAnalysis,
  askCompatibilityCodexAnalysis,
  calculateBirthChart,
  calculateCompatibility,
  calculateSavedProfile,
  calculateMuhurta,
  calculateMundane,
  calculatePrashna,
  calculateTajaka,
  calculateTithiPravesha,
  calculateTransits,
  createChartProfile,
  fetchCurrentUser,
  fetchJHoraAccuracyReport,
  fetchParasharaLightPacketReport,
  fetchSourcePassages,
  fetchSourceWorks,
  fetchWitnessSummary,
  generateBirthCodexAnalysis,
  generateBirthReport,
  generateCompatibilityAnalysisPacket,
  generateCompatibilityCodexAnalysis,
  generateCurrentDayOverview,
  isAnalysisInProgressError,
  isQueuedAnalysisGeneration,
  listIncomingChartProfileRelationshipRequests,
  listChartProfiles,
  listChartProfileRelationships,
  loginUser,
  logoutUser,
  registerUser,
  searchPlaces,
  searchResearchSources,
  searchVLSources,
  updateChartProfile,
  updateChartProfileRelationshipRequest,
  upsertChartProfileRelationship,
  type BirthReport,
  type BirthChart,
  type BirthChartRequest,
  type ChartProfile,
  type ChartProfileRelationship,
  type CodexAnalysisChatMessage,
  type CompatibilityReport,
  type DayPeriod,
  type DashaPeriod,
  type GrahaPosition,
  type GeneratedDraftAnalysis,
  type JHoraAccuracyReport,
  type MundaneReport,
  type MuhurtaReport,
  type ParasharaLightPacketReport,
  type PersonSummary,
  type PlaceCandidate,
  type PrashnaReport,
  type ResearchSearchResult,
  type SourceInventory,
  type SourcePassageResult,
  type SourceWorkSummary,
  type TajakaReport,
  type TithiPraveshaReport,
  type TransitReport,
  type TransitRow,
  type User,
  type VargaPlacement,
  type WitnessSummary,
  type VLSearchResult,
} from "@/lib/api";
import {
  firstSymbolLineY,
  northIndianHouseCells,
  northIndianHousePolygons,
  safeSymbolCenterY,
} from "@/lib/northIndianChartGeometry";
import { buildArtifactAvailabilityCheckpoint, buildCollectionPlanSnapshotRunbook, buildCoreEvidenceAttachmentGate, buildCoreEvidenceAttachmentHandoff, buildCoreEvidenceAttachmentWorkOrders, buildCoreEvidenceBacklog, buildCoreEvidenceExternalIntakeContract, buildCoreEvidenceExternalReceiptGate, buildCoreEvidenceIntakePlan, buildCoreEvidenceOperatorPacketAttachmentReadiness, buildCoreEvidenceOperatorPacketQa, buildCoreEvidenceOperatorPackets, buildCoreEvidencePipeline, buildCoreEvidenceReadiness, buildCoreReviewBatchScan, buildCoreReviewPreflightBlocker, buildCoreReviewProgress, buildParityCollectionChecklistRows, buildParityCollectionChecklistTotals, buildParityRoadmapRows, buildReleaseGateActionSummary } from "@/lib/parity-roadmap";
import { INTERFACE_MODE_STORAGE_KEY, type InterfaceMode } from "@/app/interface-mode-switch";
import { AppNavigation, type AppNavKey } from "@/app/app-navigation";
import { HouseTerms, VargaTerms, requestAiExplanation, type HelpAiQuestionDetail } from "@/app/relationship-help";
import { relationshipRoleDefinitions } from "@/lib/relationshipRoles";

const PRIVATE_APP_REQUIRE_AUTH = process.env.NEXT_PUBLIC_PRIVATE_APP_REQUIRE_AUTH === "true";
const CHART_STYLE_STORAGE_KEY = "jyotish-chart-style";
const TERM_LANGUAGE_STORAGE_KEY = "jyotish-term-language";
const CHART_HOUSE_HINTS_STORAGE_KEY = "jyotish-chart-house-hints";
const FORM_DRAFT_STORAGE_KEY = "jyotish-main-form-draft-v1";
const CHART_VIEW_STORAGE_KEY = "jyotish-chart-view-v1";

type BirthFormDraft = {
  birthDate?: string;
  birthTime?: string;
  gender?: "male" | "female" | "unknown";
  placeName?: string;
  profileName?: string;
  profileIsSelf?: boolean;
  selectedPlace?: PlaceCandidate | null;
  manualTimezone?: string;
  manualLatitude?: string;
  manualLongitude?: string;
  zodiac?: string;
  calculationModel?: string;
  ayanamsa?: string;
  nodeType?: string;
  ephemeris?: string;
  houseSystem?: string;
  bhavaSystem?: string;
  vargaScheme?: string;
  sunriseSource?: string;
  timezoneSource?: string;
  shadbalaProfile?: string;
  partnerProfileName?: string;
  partnerBirthDate?: string;
  partnerBirthTime?: string;
  partnerPlaceName?: string;
  selectedPartnerPlace?: PlaceCandidate | null;
  compatibilityPersonAProfileId?: string;
  compatibilityPersonBProfileId?: string;
  compatibilityRelationshipRoleKey?: CompatibilityRelationshipRoleKey;
  activeCompatibilityRelationshipId?: string;
  relationshipBaseProfileId?: string;
  relatedProfileIds?: number[];
  showBirthEditor?: boolean;
  showAdvancedSettings?: boolean;
  currentChartDefault?: boolean;
};

function readBirthFormDraft(): BirthFormDraft | null {
  try {
    const raw = window.localStorage.getItem(FORM_DRAFT_STORAGE_KEY);
    if (!raw) return null;
    const draft = JSON.parse(raw) as BirthFormDraft;
    return draft && typeof draft === "object" ? draft : null;
  } catch {
    return null;
  }
}

function writeBirthFormDraft(draft: BirthFormDraft) {
  try {
    window.localStorage.setItem(FORM_DRAFT_STORAGE_KEY, JSON.stringify(draft));
  } catch {
    // localStorage can be unavailable in restricted browser modes.
  }
}

function browserStorageAvailable() {
  if (typeof window === "undefined") return false;
  try {
    return typeof window.localStorage !== "undefined";
  } catch {
    return false;
  }
}

function requestedAnalysisFromLocation(): AnalysisTab | null {
  if (typeof window === "undefined") return null;
  if (window.location.pathname === "/accuracy") return "accuracy";
  const requested = new URLSearchParams(window.location.search).get("analysis");
  if (!requested || requested === "calculations") return null;
  return analysisTabs.some((tab) => tab.key === requested) ? (requested as AnalysisTab) : null;
}

function localDateInputValue(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function localTimeInputValue(date = new Date()) {
  return `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}

function currentMayapurPayload(date: string, time: string, draft?: BirthFormDraft | null): BirthChartRequest {
  return {
    birth_date: date,
    birth_time: time,
    gender: "unknown",
    place_name: "Маяпур",
    zodiac: draft?.zodiac ?? "sidereal",
    calculation_model: draft?.calculationModel ?? "drik_siddhanta",
    ayanamsa: draft?.ayanamsa ?? "lahiri",
    node_type: draft?.nodeType ?? "true",
    ephemeris: draft?.ephemeris ?? "swiss",
    house_system: draft?.houseSystem ?? "whole_sign",
    bhava_system: draft?.bhavaSystem ?? "whole_sign",
    varga_scheme: draft?.vargaScheme ?? "parashara",
    sunrise_source: draft?.sunriseSource ?? "noaa",
    timezone_source: draft?.timezoneSource ?? "iana",
    shadbala_profile: draft?.shadbalaProfile ?? "bphs_classical",
    timezone: "Asia/Kolkata",
    latitude: 23.4241,
    longitude: 88.3883,
  };
}

function birthPayloadFromDraft(draft: BirthFormDraft): BirthChartRequest | null {
  const manualLat = Number(String(draft.manualLatitude ?? "").replace(",", "."));
  const manualLon = Number(String(draft.manualLongitude ?? "").replace(",", "."));
  const hasManualPlace = Boolean(draft.manualTimezone?.trim() && draft.manualLatitude?.trim() && draft.manualLongitude?.trim());
  if (hasManualPlace && (!Number.isFinite(manualLat) || !Number.isFinite(manualLon))) return null;
  const selectedPlace = draft.selectedPlace;
  return {
    birth_date: draft.birthDate || localDateInputValue(),
    birth_time: draft.birthTime || "",
    gender: draft.gender ?? "unknown",
    place_name: selectedPlace?.label ?? draft.placeName ?? "Маяпур",
    ...(Array.isArray(draft.relatedProfileIds) && draft.relatedProfileIds.length ? { related_profile_ids: draft.relatedProfileIds } : {}),
    zodiac: draft.zodiac ?? "sidereal",
    calculation_model: draft.calculationModel ?? "drik_siddhanta",
    ayanamsa: draft.ayanamsa ?? "lahiri",
    node_type: draft.nodeType ?? "true",
    ephemeris: draft.ephemeris ?? "swiss",
    house_system: draft.houseSystem ?? "whole_sign",
    bhava_system: draft.bhavaSystem ?? "whole_sign",
    varga_scheme: draft.vargaScheme ?? "parashara",
    sunrise_source: draft.sunriseSource ?? "noaa",
    timezone_source: draft.timezoneSource ?? "iana",
    shadbala_profile: draft.shadbalaProfile ?? "bphs_classical",
    ...(selectedPlace
      ? {
          place_id: selectedPlace.id,
          country_code: selectedPlace.country_code,
          timezone: selectedPlace.timezone,
          latitude: selectedPlace.latitude,
          longitude: selectedPlace.longitude,
        }
      : hasManualPlace
        ? {
            timezone: draft.manualTimezone?.trim(),
            latitude: manualLat,
            longitude: manualLon,
          }
        : {}),
  };
}

const analysisTabs = [
  { key: "overview", label: "Обзор", hint: "контекст" },
  { key: "calculations", label: "Расчёт", hint: "таблицы" },
  { key: "yogas", label: "Силы", hint: "бала, йоги" },
  { key: "timeline", label: "Даши", hint: "периоды" },
  { key: "transits", label: "Транзиты", hint: "гочара" },
  { key: "compatibility", label: "Совместимость", hint: "две карты" },
  { key: "tithiPravesha", label: "Год", hint: "tithi pravesha" },
  { key: "tajaka", label: "Таджака", hint: "годовая карта" },
  { key: "prashna", label: "Прашна", hint: "вопрос" },
  { key: "mundane", label: "Мирские", hint: "событие" },
  { key: "muhurta", label: "Мухурта", hint: "выбор времени" },
  { key: "accuracy", label: "Точность", hint: "сверка" },
  { key: "guidance", label: "Разбор", hint: "цитаты" },
  { key: "sources", label: "Источники", hint: "шастры" },
] as const;

type AnalysisTab = (typeof analysisTabs)[number]["key"];
type ChartWorkspaceTab = "essentials" | "references" | "vargas";

const primaryAnalysisTabKeys = new Set<AnalysisTab>([
  "overview",
  "yogas",
  "timeline",
  "transits",
  "guidance",
]);
const primaryAnalysisTabs = analysisTabs.filter((tab) => primaryAnalysisTabKeys.has(tab.key));
const secondaryAnalysisTabs: Array<(typeof analysisTabs)[number]> = [];
const chartWorkspaceTabs: Array<{ key: ChartWorkspaceTab; label: string; hint: string }> = [
  { key: "vargas", label: "Атлас варг", hint: "D1-D60" },
  { key: "references", label: "Отсчёты", hint: "Луна, 7/12" },
];

const stateLabels: Record<string, string> = {
  draft: "в работе",
  ready: "готово",
};

const calculationStatusLabelsRu: Record<string, string> = {
  calculated: "рассчитано",
  partial: "частично",
  draft_needs_citation: "готовится",
  draft_needs_jhora_audit: "готовится",
  calculated_needs_citation: "расчёт готов",
  calculated_needs_jhora_audit: "расчёт готов",
  calculated_needs_jhora_component_audit: "расчёт готов",
  calculated_source_backed_needs_jhora_profile_audit: "расчёт готов",
  calculated_with_tradition_profile_needs_jhora_audit: "расчёт готов",
  calculated_bphs_varga_viswa_single_jhora_profile_audited: "сверено",
  calculated_bphs_varga_viswa_weights_fixed_profile_diff_open: "расчёт готов",
  calculated_bphs_varga_viswa_jhora_fixture_matched: "сверено",
  calculated_jhora_fixture_matched: "сверено",
  calculated_single_jhora_fixture_matched_partial_catalog: "сверено",
  calculated_single_jhora_fixture_matched_core_catalog: "сверено",
  calculated_needs_jhora_split_profile: "расчёт готов",
  baseline_calculated_needs_jhora_tajaka_audit: "готово",
  baseline_calculated_needs_full_tajaka_audit: "готово",
  baseline_calculated_needs_prashna_tradition_review: "готово",
  baseline_event_chart_needs_mundane_rules_review: "готово",
  partial_extra_dasha_catalog: "частичный каталог даш",
  calculated_needs_tradition_review: "расчёт готов",
  calculated_needs_task_review: "расчёт готов",
  partial_calculated_needs_citation: "частично",
  partial_calculated_needs_jhora_audit: "частично",
  partial_calculated_needs_jhora_profile_audit: "частично рассчитано",
  calculated_needs_source_audit: "расчёт готов",
  pending_source_mapping: "источники подключаются",
  pending_jhora_audit: "ожидает",
  pending_endpoint: "ожидает",
  api_available: "готово",
  complete_baseline_needs_jhora_audit: "готово",
  multi_factor_needs_shastra_citation_review: "многофакторный расчёт",
  pending_separate_chart_pair: "ожидает вторую карту",
  pending_separate_workflow: "отдельный режим",
  signature_only: "только признак",
  missing_lagna: "нет лагны",
};

const auditStatusLabelsRu: Record<string, string> = {
  calculated: "рассчитано",
  calculated_needs_fixture_audit: "расчёт готов",
  calculated_needs_text_rule_review: "расчёт готов",
  calculated_needs_jhora_component_audit: "расчёт готов",
  calculated_jhora_profile_diff_open: "нужна сверка",
  calculated_single_jhora_fixture_matched_partial_catalog: "сверено",
  calculated_single_jhora_fixture_matched_core_catalog: "сверено",
  calculated_bphs_varga_viswa_weights_fixed_profile_diff_open: "расчёт готов",
  calculated_bphs_varga_viswa_jhora_fixture_matched: "сверено",
  calculated_needs_jhora_split_profile: "расчёт готов",
  partial: "частично",
  temporary_proxy: "временная формула",
  partial_detection_needs_citations: "частично",
  partial_gulika_only: "только Гулика",
  baseline_api_ready: "готово",
  baseline_ashtakuta: "базовая аштакута",
  baseline_scoring: "базовая оценка",
  multi_factor_calculated_needs_shastra_review: "многофакторный расчёт",
  source_backed: "есть шастра",
  source_backed_with_bphs_caution: "есть шастра, BPHS осторожно",
  source_backed_but_tradition_sensitive: "по шастрам",
  source_backed_but_pastoral_review_required: "по шастрам",
  needs_tradition_decision: "нужна проверка",
  needs_source_mapping: "источники подключаются",
  research_only: "только исследование",
};

const auditLayerLabelsRu: Record<string, string> = {
  rashi_nakshatra_navamsa: "Раши, накшатра, пада, навамша",
  vargas_d2_d60: "Варги D2-D60",
  panchanga: "Панчанга",
  vimshottari: "Вимшоттари даша",
  avasthas: "Авастхи",
  ashtakavarga: "Аштакаварга",
  shadbala: "Шадбала",
  vimshopaka: "Вимшопака бала",
  yogas: "Йоги",
  argala: "Аргала",
  upagrahas: "Упаграхи",
  special_points: "Специальные точки",
  transits: "Транзиты",
  compatibility: "Совместимость",
  muhurta: "Мухурта",
};

const auditSourceBasisRu: Record<string, string> = {
  rashi_nakshatra_navamsa: "Сиддхантическая математика координат и классические деления.",
  vargas_d2_d60: "Правила варг сверяются по классическим вариантам.",
  panchanga: "Угловые деления Солнце-Луна и правила панчанги/мухурты.",
  vimshottari: "Уду-даша от накшатры Луны, 120-летний цикл и классическая последовательность грах.",
  avasthas: "Авастхи по градусным диапазонам с учётом нечётных/чётных знаков.",
  ashtakavarga: "Brhat Jataka IX и стандартная сумма SAV 337 бинду.",
  shadbala: "Шесть групп шадбалы рассчитаны по компонентам и готовы для личного разбора.",
  vimshopaka: "BPHS веса shadvarga/sapta/dasha/shodasha рассчитаны; сверка 36/36.",
  yogas: "Показываются условия йог, но не окончательное предсказание.",
  argala: "Аргала рассчитана как дополнительный слой чтения карты.",
  upagrahas: "Гулика, Маанди и солнечные упаграхи сверены.",
  special_points: "Indu/Bhava/Hora/Ghati и upagraha core-точки сверены.",
  transits: "Транзиты рассчитаны как дополнительный слой чтения карты.",
  compatibility: "Аштакута плюс многофакторный анализ двух карт.",
  muhurta: "Базовая оценка окна, не финальная элекция.",
};

auditSourceBasisRu.shadbala =
  "Шадбала рассчитана по компонентам: Sthana, Dig, Kala, Chesta, Drik и Naisargika.";

const authorityOrderRu: Record<string, string> = {
  "older shastra and reviewed parampara instruction": "старшие шастры и проверенное наставление парампары",
  "astronomical ephemeris and timezone audit": "астрономическая точность, эфемериды и часовой пояс",
  "JHora and external services as black-box witnesses": "сверка точности",
  "internal regression fixtures": "контроль точности",
};

const compatibilityLevelLabelsRu: Record<string, string> = {
  supportive: "поддерживающе",
  mixed: "смешанно",
  caution: "контекст",
  context: "контекст",
  missing: "не хватает данных",
};

const compatibilityPerspectiveLabelsRu: Record<string, string> = {
  ashtakuta: "Ашта-кута как базовый слой",
  lagna_lagna: "Лагна и направление жизни",
  moon_mind: "Луна и эмоциональный ритм",
  seventh_house: "7 дом и способность к браку",
  shukra_mangala: "Шукра и Мангала",
  guru_shukra: "Гуру, Шукра и ценности семьи",
  dasha_context: "Контекст даш",
};

const compatibilityPerspectiveBasisRu: Record<string, string> = {
  ashtakuta: "Кута-милан по Луне и накшатре: важный слой, но не самостоятельный приговор.",
  lagna_lagna: "Сравнение лагн показывает направление жизни и практический ритм семьи.",
  moon_mind: "Сравнение Луны показывает манас, эмоциональную реакцию и бытовой комфорт.",
  seventh_house: "Проверяются 7 дом, его управитель и планеты в 7 доме в обеих картах.",
  shukra_mangala: "Шукра/Мангала дают вторичный показатель притяжения и возможного трения.",
  guru_shukra: "Гуру и Шукра показывают дхарму, совет, привязанность и ценности семьи.",
  dasha_context: "Даши рассматриваются отдельно и не должны отменять общий анализ карт.",
};

type CompatibilityRelationshipRole = {
  key: string;
  label: string;
  focus: string;
  focusHouses: number[];
  focusVargas: string[];
  promptHint: string;
};

const compatibilityRelationshipRoles: CompatibilityRelationshipRole[] = relationshipRoleDefinitions.map((role) => ({
  key: role.key,
  label: role.key === "partner" ? "Партнёр / брак" : role.key === "opponent" ? "Оппонент / враг" : role.label,
  focus: role.focus,
  focusHouses: role.houses,
  focusVargas: role.vargas,
  promptHint: role.promptHint,
}));

type CompatibilityRelationshipRoleKey = string;

function compatibilityRelationshipRole(key: string) {
  return compatibilityRelationshipRoles.find((role) => role.key === key) ?? compatibilityRelationshipRoles[0];
}

function relationshipStatusLabel(status: string | null | undefined) {
  if (status === "accepted") return "подтверждено";
  if (status === "requested") return "ожидает подтверждения";
  if (status === "declined") return "отклонено";
  if (status === "blocked") return "заблокировано";
  return "личная пометка";
}

const bodyLabelsRu: Record<string, string> = {
  Ascendant: "Асцендент",
  Lagna: "Лагна",
  Surya: "Сурья",
  Chandra: "Чандра",
  Mangala: "Мангала",
  Budha: "Будха",
  Guru: "Гуру",
  Shukra: "Шукра",
  Shani: "Шани",
  Rahu: "Раху",
  Ketu: "Кету",
  Moon: "Луна",
  Sun: "Солнце",
};

type TermLanguage = "sanskrit" | "ru" | "en";
type GrahaDignity = "exaltation" | "debilitation" | "moolatrikona";

const bodyAliases: Record<string, string> = {
  Ascendant: "Lagna",
  Lagna: "Lagna",
  Sun: "Surya",
  Surya: "Surya",
  Moon: "Chandra",
  Chandra: "Chandra",
  Mars: "Mangala",
  Mangala: "Mangala",
  Mercury: "Budha",
  Budha: "Budha",
  Jupiter: "Guru",
  Guru: "Guru",
  Venus: "Shukra",
  Shukra: "Shukra",
  Saturn: "Shani",
  Shani: "Shani",
  Rahu: "Rahu",
  Ketu: "Ketu",
};

const termBodyLabels: Record<TermLanguage, Record<string, { long: string; short: string }>> = {
  sanskrit: {
    Lagna: { long: "Lagna", short: "As" },
    Surya: { long: "Surya", short: "Su" },
    Chandra: { long: "Chandra", short: "Mo" },
    Mangala: { long: "Mangala", short: "Ma" },
    Budha: { long: "Budha", short: "Me" },
    Guru: { long: "Guru", short: "Ju" },
    Shukra: { long: "Shukra", short: "Ve" },
    Shani: { long: "Shani", short: "Sa" },
    Rahu: { long: "Rahu", short: "Ra" },
    Ketu: { long: "Ketu", short: "Ke" },
  },
  ru: {
    Lagna: { long: "Лагна", short: "Ас" },
    Surya: { long: "Солнце", short: "Сл" },
    Chandra: { long: "Луна", short: "Лн" },
    Mangala: { long: "Марс", short: "Ма" },
    Budha: { long: "Меркурий", short: "Ме" },
    Guru: { long: "Юпитер", short: "Юп" },
    Shukra: { long: "Венера", short: "Ве" },
    Shani: { long: "Сатурн", short: "Са" },
    Rahu: { long: "Раху", short: "Ра" },
    Ketu: { long: "Кету", short: "Ке" },
  },
  en: {
    Lagna: { long: "Ascendant", short: "As" },
    Surya: { long: "Sun", short: "Su" },
    Chandra: { long: "Moon", short: "Mo" },
    Mangala: { long: "Mars", short: "Ma" },
    Budha: { long: "Mercury", short: "Me" },
    Guru: { long: "Jupiter", short: "Ju" },
    Shukra: { long: "Venus", short: "Ve" },
    Shani: { long: "Saturn", short: "Sa" },
    Rahu: { long: "Rahu", short: "Ra" },
    Ketu: { long: "Ketu", short: "Ke" },
  },
};

const rashiTermLabels: Record<TermLanguage, string[]> = {
  sanskrit: ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"],
  ru: ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"],
  en: ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
};

const rashiTermShortLabels: Record<TermLanguage, string[]> = {
  sanskrit: ["Mesha", "Vrish", "Mith", "Karka", "Simha", "Kanya", "Tula", "Vrisch", "Dhanu", "Makara", "Kumbh", "Meena"],
  ru: ["Овен", "Телец", "Близн", "Рак", "Лев", "Дева", "Весы", "Скорп", "Стрел", "Козер", "Водол", "Рыбы"],
  en: ["Aries", "Taurus", "Gem", "Cancer", "Leo", "Virgo", "Libra", "Scorp", "Sag", "Cap", "Aquar", "Pisces"],
};

const exaltationSigns: Record<string, number> = {
  Surya: 0,
  Chandra: 1,
  Mangala: 9,
  Budha: 5,
  Guru: 3,
  Shukra: 11,
  Shani: 6,
};

const debilitationSigns: Record<string, number> = {
  Surya: 6,
  Chandra: 7,
  Mangala: 3,
  Budha: 11,
  Guru: 9,
  Shukra: 5,
  Shani: 0,
};

const moolatrikonaSigns: Record<string, number> = {
  Surya: 4,
  Chandra: 1,
  Mangala: 0,
  Budha: 5,
  Guru: 8,
  Shukra: 6,
  Shani: 10,
};

const summaryLabelsRu: Record<string, string> = {
  Ayanamsa: "Айанамша",
  Birth: "Рождение",
  "Calculation model": "Модель расчёта",
  Ephemeris: "Эфемериды",
  "House system": "Система домов",
  Karana: "Карана",
  Lagna: "Лагна",
  Moon: "Луна",
  "Node type": "Тип узлов",
  Panchanga: "Панчанга",
  Place: "Место",
  Sun: "Солнце",
  "Timezone source": "Источник часового пояса",
  Tithi: "Титхи",
  Vara: "Вара",
  Yoga: "Йога",
};

function labelRu(value: string) {
  return summaryLabelsRu[value] ?? bodyLabelsRu[value] ?? value;
}

function valueRu(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return "Ожидает";
  return String(value).replace(/house (\d+)/g, "дом $1");
}

function statusRu(value: string | null | undefined) {
  if (!value) return "ожидает";
  return calculationStatusLabelsRu[value] ?? value;
}

function auditStatusRu(value: string | null | undefined) {
  if (!value) return "ожидает";
  return auditStatusLabelsRu[value] ?? statusRu(value);
}

function auditAuthorityRu(value: string | null | undefined) {
  if (!value) return "частично";
  if (value.startsWith("source_backed")) return "по шастрам";
  if (value.startsWith("needs")) return "нужна проверка";
  return auditStatusRu(value);
}

function auditOrderRu(order: string[]) {
  return order.map((item) => authorityOrderRu[item] ?? item).join(" → ");
}

function auditNoteRu(key: string, fallback: string) {
  return auditSourceBasisRu[key] ?? fallback;
}

function auditCalculationReadyRu(status: string) {
  if (status.startsWith("calculated")) return "расчёт готов";
  if (status.startsWith("partial")) return "частично";
  if (status.startsWith("baseline") || status === "api_available") return "готово";
  if (status === "api_ready") return "готово";
  return auditStatusRu(status);
}

function auditInterpretationReadyRu(ready: boolean) {
  return ready ? "готово" : "готовится";
}

function generatedStatusRu(status: string | null | undefined) {
  if (status === "private_final") return "готовый личный разбор";
  if (status === "private_partial") return "неполный личный разбор";
  if (status === "draft") return "личный разбор";
  if (status === "approved") return "утверждено";
  return status || "ожидает";
}

function generatedTitleRu(status: string | null | undefined) {
  if (status === "private_final" || status === "approved") return "Готовый личный разбор";
  if (status === "private_partial") return "Неполный личный разбор";
  return "Личный разбор";
}

function workflowStatusRu(status: string | null | undefined) {
  if (!status) return "готово";
  if (status.includes("pending") || status.includes("missing")) return "ожидает данных";
  if (status.includes("calculated") || status.includes("ready") || status.includes("approved")) return "готово";
  return "частично";
}

function reportSectionStatusRu(status: string | null | undefined) {
  if (!status) return "готово";
  if (status === "calculation_only") return "расчёт";
  if (status === "private_final" || status === "approved") return "готово";
  return "готовится";
}

function compatibilityFindingRu(value: string) {
  return value
    .replace("Ashtakuta score", "Баллы аштакуты")
    .replace("Zero-score kutas:", "Нулевые куты:")
    .replace("none", "нет")
    .replace("Lagna distance", "Дистанция лагн")
    .replace("Moon distance", "Дистанция Лун")
    .replace("Moon nakshatras:", "Накшатры Луны:")
    .replace("person_a seventh house", "Карта A: 7 дом")
    .replace("person_b seventh house", "Карта B: 7 дом")
    .replace("person_a seventh lord", "Карта A: управитель 7 дома")
    .replace("person_b seventh lord", "Карта B: управитель 7 дома")
    .replace("A Shukra to B Mangala distance", "Шукра A к Мангале B")
    .replace("B Shukra to A Mangala distance", "Шукра B к Мангале A")
    .replace("person_a Guru dignity", "Карта A: достоинство Гуру")
    .replace("person_a Shukra dignity", "Карта A: достоинство Шукры")
    .replace("person_b Guru dignity", "Карта B: достоинство Гуру")
    .replace("person_b Shukra dignity", "Карта B: достоинство Шукры")
    .replace("Birth mahadasha lords:", "Махадаши рождения:")
    .replaceAll(" lord ", " управитель ")
    .replaceAll(" in house ", " в доме ")
    .replaceAll("exaltation", "экзальтация")
    .replaceAll("debilitation", "дебилитация")
    .replaceAll("own", "свой знак")
    .replaceAll("friend", "дружественный знак")
    .replaceAll("neutral", "нейтральный знак")
    .replaceAll("enemy", "враждебный знак");
}

function formatCoordinate(value: number) {
  return value.toFixed(4);
}

function normalizePlaceLabel(value: string) {
  return value.trim().toLowerCase().replace(/\s*,\s*/g, ", ").replace(/\s+/g, " ");
}

const grahaSymbols: Record<string, string> = {
  Lagna: "As",
  Ascendant: "As",
  Surya: "☉",
  Chandra: "☽",
  Mangala: "♂",
  Budha: "☿",
  Guru: "♃",
  Shukra: "♀",
  Shani: "♄",
  Rahu: "☊",
  Ketu: "☋",
};

const northGrahaLabels: Record<string, string> = {
  Lagna: "As",
  Ascendant: "As",
  Surya: "Su",
  Chandra: "Mo",
  Mangala: "Ma",
  Budha: "Me",
  Guru: "Ju",
  Shukra: "Ve",
  Shani: "Sa",
  Rahu: "Ra",
  Ketu: "Ke",
};

const rashiNames = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"];
const rashiChartLabels = ["Mesha", "Vrish", "Mith", "Karka", "Simha", "Kanya", "Tula", "Vrisch", "Dhanu", "Makara", "Kumbh", "Meena"];

const rashiNameIndices: Record<string, number> = {
  Aries: 0,
  Mesha: 0,
  Овен: 0,
  Taurus: 1,
  Vrishabha: 1,
  Vrsabha: 1,
  Телец: 1,
  Gemini: 2,
  Mithuna: 2,
  Близнецы: 2,
  Cancer: 3,
  Karka: 3,
  Karkata: 3,
  Рак: 3,
  Leo: 4,
  Simha: 4,
  Лев: 4,
  Virgo: 5,
  Kanya: 5,
  Дева: 5,
  Libra: 6,
  Tula: 6,
  Весы: 6,
  Scorpio: 7,
  Vrischika: 7,
  Vrichika: 7,
  Скорпион: 7,
  Sagittarius: 8,
  Dhanus: 8,
  Dhanu: 8,
  Стрелец: 8,
  Capricorn: 9,
  Makara: 9,
  Козерог: 9,
  Aquarius: 10,
  Kumbha: 10,
  Водолей: 10,
  Pisces: 11,
  Meena: 11,
  Mina: 11,
  Рыбы: 11,
};

type NorthIndianHouseItem = {
  house: number;
  rashi: string;
  rashiIndex: number | null;
  placements: ChartPlacement[];
};

type ActiveVargaChart = NonNullable<BirthChart["vargas"]>[string];

type ChartReference = "lagna" | "moon" | "sun" | "seventh" | "twelfth";

const chartReferenceOptions: Array<{
  key: ChartReference;
  label: string;
  hint: string;
}> = [
  { key: "lagna", label: "Лагна", hint: "D1" },
  { key: "moon", label: "Луна", hint: "Chandra" },
  { key: "sun", label: "Солнце", hint: "Surya" },
  { key: "seventh", label: "7 дом", hint: "брак" },
  { key: "twelfth", label: "12 дом", hint: "близость" },
];

const jyotishGlossary = {
  lagna: {
    label: "Lagna",
    text: "Точка восходящего знака. От нее обычно считают дома и базовую структуру карты.",
  },
  chandra_lagna: {
    label: "Chandra Lagna",
    text: "Карта от Луны. Полезна для психики, переживаний, даш и практического проявления событий.",
  },
  dasha: {
    label: "Dasha",
    text: "Планетный период времени. Даша показывает, какая граха сейчас сильнее включает свои темы и результаты в жизни человека.",
  },
  panchanga: {
    label: "Panchanga",
    text: "Пять факторов дня: титхи, вара, накшатра, йога и карана. Нужны для мухурты и качества времени.",
  },
  tithi: {
    label: "Tithi",
    text: "Лунный день, основанный на расстоянии между Солнцем и Луной. Важен для настроения дня и выбора времени.",
  },
  vara: {
    label: "Vara",
    text: "День недели и его планетарный управитель. Это один из пяти факторов панчанги.",
  },
  panchanga_yoga: {
    label: "Yoga",
    text: "Панчанга-йога, рассчитанная по сумме долгот Солнца и Луны. Показывает качество времени.",
  },
  karana: {
    label: "Karana",
    text: "Половина титхи. Используется в мухурте для оценки практической пригодности действия.",
  },
  varga_method: {
    label: "Метод варги",
    text: "Правило построения выбранной дробной карты. Для точной проверки важно видеть не только D-карту, но и метод её расчёта.",
  },
  surya_lagna: {
    label: "Surya Lagna",
    text: "Карта от Солнца. Помогает смотреть статус, волю, здоровье и внешнее проявление человека.",
  },
  transit: {
    label: "Гочара / транзиты",
    text: "Текущее движение грах по знакам. В личном обзоре дня транзиты читаются относительно натальной лагны и Луны.",
  },
  house: {
    label: "Дом",
    text: "Дом показывает сферу жизни. В северной карте положение областей фиксировано по домам, поэтому номер дома важен для чтения бхав.",
  },
  house_1: {
    label: "1 дом",
    text: "Лагна-бхава: тело, характер, здоровье, способ начинать жизнь и общий тон всей карты.",
  },
  house_2: {
    label: "2 дом",
    text: "Семья, речь, питание, накопления, ценности и то, чем человек поддерживает жизнь.",
  },
  house_3: {
    label: "3 дом",
    text: "Смелость, усилия, руки, навыки, коммуникация, младшие братья/сёстры и личная инициатива.",
  },
  house_4: {
    label: "4 дом",
    text: "Дом, мать, сердце, внутренний покой, недвижимость, транспорт и базовое чувство защищённости.",
  },
  house_5: {
    label: "5 дом",
    text: "Разум, дети, мантра, творчество, пурва-пунья, обучение и способность давать совет.",
  },
  house_6: {
    label: "6 дом",
    text: "Болезни, долги, служение, споры, конкуренты, дисциплина и способность решать трудности.",
  },
  house_7: {
    label: "7 дом",
    text: "Дом брака, партнерства, договоров и открытого взаимодействия с другими людьми.",
  },
  house_8: {
    label: "8 дом",
    text: "Кризисы, тайны, трансформация, долголетие, наследство, скрытые страхи и глубокие перемены.",
  },
  house_9: {
    label: "9 дом",
    text: "Дхарма, отец, гуру, удача, паломничества, высшее знание и благословения.",
  },
  house_10: {
    label: "10 дом",
    text: "Карьера, действие в мире, статус, обязанности, публичная роль и видимая карма.",
  },
  house_11: {
    label: "11 дом",
    text: "Доходы, друзья, старшие братья/сёстры, исполнение желаний, сети и получаемые результаты.",
  },
  house_12: {
    label: "12 дом",
    text: "Дом потерь, уединения, сна, расходов, мокши, дальних мест и скрытой стороны близости.",
  },
  graha: {
    label: "Граха",
    text: "Планетная точка в джйотише: Солнце, Луна, планеты, Раху, Кету и лагна как точка отсчёта.",
  },
  rashi: {
    label: "Rashi",
    text: "Знак зодиака. В южной карте клетки фиксированы по знакам, в северной знаки вписываются в дома.",
  },
  rashi_mesha: {
    label: "Mesha / Овен",
    text: "Огненный подвижный знак. Даёт импульс, начало, прямоту, действие и быстрое включение темы.",
  },
  rashi_vrishabha: {
    label: "Vrishabha / Телец",
    text: "Земной фиксированный знак. Даёт устойчивость, накопление, тело, речь, ценности и материальную опору.",
  },
  rashi_mithuna: {
    label: "Mithuna / Близнецы",
    text: "Воздушный двойственный знак. Даёт обмен, обучение, речь, связи, торговлю и гибкость мышления.",
  },
  rashi_karka: {
    label: "Karka / Рак",
    text: "Водный подвижный знак. Даёт заботу, дом, эмоции, защиту, память и внутреннюю безопасность.",
  },
  rashi_simha: {
    label: "Simha / Лев",
    text: "Огненный фиксированный знак. Даёт власть, достоинство, центр, лидерство, творчество и самовыражение.",
  },
  rashi_kanya: {
    label: "Kanya / Дева",
    text: "Земной двойственный знак. Даёт анализ, служение, ремесло, детали, здоровье и практический порядок.",
  },
  rashi_tula: {
    label: "Tula / Весы",
    text: "Воздушный подвижный знак. Даёт баланс, договор, партнёрство, обмен, эстетику и социальную меру.",
  },
  rashi_vrischika: {
    label: "Vrischika / Скорпион",
    text: "Водный фиксированный знак. Даёт глубину, тайну, кризис, трансформацию, контроль и скрытую силу.",
  },
  rashi_dhanu: {
    label: "Dhanu / Стрелец",
    text: "Огненный двойственный знак. Даёт дхарму, наставление, движение к смыслу, веру, знание и путь.",
  },
  rashi_makara: {
    label: "Makara / Козерог",
    text: "Земной подвижный знак. Даёт структуру, труд, ответственность, статус, ограничения и долгий результат.",
  },
  rashi_kumbha: {
    label: "Kumbha / Водолей",
    text: "Воздушный фиксированный знак. Даёт систему, общество, сеть, идею, дистанцию и нестандартное устройство.",
  },
  rashi_meena: {
    label: "Meena / Рыбы",
    text: "Водный двойственный знак. Даёт веру, растворение, сострадание, воображение, мокшу и тонкое восприятие.",
  },
  shadbala: {
    label: "Shadbala",
    text: "Шесть групп силы грахи. Это расчетная оценка, а не самостоятельный окончательный приговор.",
  },
  combustion: {
    label: "Asta / combustion",
    text: "Сожжение: граха слишком близко к Солнцу и может слабее проявлять свои качества.",
  },
  retrograde: {
    label: "Retrograde",
    text: "Ретроградность. В таблице обозначается скобками: например (Ju).",
  },
  moolatrikona: {
    label: "Moolatrikona",
    text: "Мулатрикона: сильная собственная область грахи. В таблице обозначается подчёркиванием.",
  },
  exaltation: {
    label: "Exaltation",
    text: "Экзальтация: знак максимального подъёма качества грахи. В таблице обозначается стрелкой вверх.",
  },
  debilitation: {
    label: "Debilitation",
    text: "Дебилитация: знак ослабления качества грахи. В таблице обозначается стрелкой вниз.",
  },
  dignity: {
    label: "Dignity",
    text: "Достоинство грахи: экзальтация, дебилитация, мулатрикона, собственный или иной знак.",
  },
  nakshatra: {
    label: "Nakshatra",
    text: "Лунная стоянка. В практическом разборе важна вместе с падой и управителем.",
  },
  nakshatra_lord: {
    label: "Управитель накшатры",
    text: "Граха-управитель накшатры. Это важный быстрый слой: он связывает положение точки с дашами, мотивацией и более тонким проявлением результата.",
  },
  pada: {
    label: "Pada",
    text: "Четверть накшатры. Пада уточняет навамшу и делает положение грахи более точным.",
  },
  longitude: {
    label: "Долгота",
    text: "Точная позиция точки в зодиаке. По долготе определяются знак, накшатра, пада и варги.",
  },
  calculation_table: {
    label: "Таблица расчётов",
    text: "Рабочая таблица астролога: сначала смотрят граху, знак и дом, затем управляемые дома, накшатру, D9 и силу/состояние.",
  },
  graha_condition: {
    label: "Состояние грахи",
    text: "Краткая сводка ретроградности, достоинства, сожжения и силы. Это слой диагностики, а не отдельный окончательный вывод.",
  },
  shadbala_score: {
    label: "Баллы шадбалы",
    text: "Число в вирупах по шести группам силы. Сравнивайте планеты между собой и с контекстом домов, а не по одному числу.",
  },
  karaka: {
    label: "Карака",
    text: "Показатель или сигнификатор. Карака связывает граху с конкретной темой: душа, ум, отношения, дети и другие сферы.",
  },
  navamsa: {
    label: "Navamsa / D9",
    text: "Девятая варга. Часто используется для дхармы, брака и тонкой силы положения грахи.",
  },
  d1: {
    label: "D1 / Rashi",
    text: "Основная карта рождения. Все дробные карты читаются вместе с D1, а не вместо неё.",
  },
  d3: {
    label: "D3 / Drekkana",
    text: "Дробная карта братьев, сестёр, инициативы, усилий и практической смелости.",
  },
  d6: {
    label: "D6",
    text: "Дробная карта болезней, долгов, врагов, споров и конфликтного напряжения.",
  },
  d7: {
    label: "D7 / Saptamsa",
    text: "Дробная карта детей, потомства, продолжения рода и творческого плодоношения.",
  },
  d9: {
    label: "D9 / Navamsa",
    text: "Навамша: дхарма, зрелость положения, брак, внутренняя сила грахи и качество союза.",
  },
  d10: {
    label: "D10 / Dashamsa",
    text: "Дробная карта карьеры, статуса, начальников, подчинённых и профессиональной роли.",
  },
  d12: {
    label: "D12 / Dvadashamsa",
    text: "Дробная карта родителей, родовой линии, наследственности и связи с отцом/матерью.",
  },
  d30: {
    label: "D30 / Trimshamsa",
    text: "Дробная карта скрытых неприятностей, уязвимостей, конфликтных паттернов и рисков.",
  },
  d60: {
    label: "D60 / Shashtyamsha",
    text: "Глубокий кармический слой. Требует очень точного времени рождения и читается осторожно.",
  },
  varga: {
    label: "Varga",
    text: "Дробная карта. Ее читают не отдельно, а вместе с D1 и подходящим жизненным вопросом.",
  },
  avastha: {
    label: "Avastha",
    text: "Состояние грахи. Помогает уточнять, как сила и качество грахи проявляются в конкретном положении.",
  },
  ashtakavarga: {
    label: "Ashtakavarga",
    text: "Система бинду по знакам. Используется для оценки поддержки домов, знаков и транзитов.",
  },
  argala: {
    label: "Argala",
    text: "Влияние или вмешательство домов друг на друга. Показывает, какие факторы помогают или препятствуют теме.",
  },
  vimshopaka: {
    label: "Vimshopaka Bala",
    text: "Сила по варгам: насколько граха поддержана в divisional charts.",
  },
  sav: {
    label: "Sarvashtakavarga",
    text: "Сводные бинду по знакам. Используется как быстрый слой оценки поддержки транзитов и домов.",
  },
  ruled_houses: {
    label: "Управляемые дома",
    text: "Дома, которыми управляет граха через владение знаками. В BPHS это один из главных слоёв чтения: важно не только где стоит планета, но и какие дома она приносит в это место.",
  },
  self_profile: {
    label: "Моя карта",
    text: "Основная карта владельца аккаунта. Первый личный разбор даётся именно для этой карты; чужие карты можно хранить отдельно.",
  },
  free_personal_ai: {
    label: "Первый разбор",
    text: "Бесплатный личный разбор относится к вашей собственной карте. Если разбор уже создан, повторное открытие показывает сохранённую историю.",
  },
  relationship_role: {
    label: "Роль человека",
    text: "Ракурс чтения второй карты: партнёр, отец, мать, брат, руководитель, оппонент и т.д. От роли зависят дома и D-карты, которые ассистент должен учитывать.",
  },
  relationship_status: {
    label: "Статус связи",
    text: "Показывает приватность связи: личная пометка видна только вам, запрос ждёт согласия, подтверждённая связь видна обоим зарегистрированным пользователям.",
  },
  saved_other_chart: {
    label: "Чужая сохранённая карта",
    text: "Карту другого человека можно сохранить и просматривать. Ограничение относится к разбору, а не к самому хранению карты.",
  },
  paid_other_ai: {
    label: "Разбор чужой карты",
    text: "После запуска оплаты разбор чужой карты будет платным. Сейчас бесплатный личный разбор предназначен только для собственной карты аккаунта.",
  },
  ai_context: {
    label: "Связанные карты",
    text: "Отмеченные карты можно учитывать как семейный или личный контекст при разборе.",
  },
} as const;

type GlossaryKey = keyof typeof jyotishGlossary;

function houseGlossaryKey(house: number | null | undefined): GlossaryKey {
  if (house && house >= 1 && house <= 12) return `house_${house}` as GlossaryKey;
  return "house";
}

function HouseGlossaryList({ houses }: { houses: readonly number[] }) {
  if (!houses.length) return <>-</>;
  return (
    <span className="house-glossary-list">
      {houses.map((house, index) => (
        <GlossaryTerm termKey={houseGlossaryKey(house)} key={`house-glossary-${house}-${index}`}>
          {house}
        </GlossaryTerm>
      ))}
    </span>
  );
}

function vargaGlossaryKey(code: string): GlossaryKey {
  const key = code.toLowerCase();
  if (key in jyotishGlossary) return key as GlossaryKey;
  return "varga";
}

function rashiGlossaryKey(index: number | null | undefined, fallback?: string | null): GlossaryKey {
  const normalized = index ?? rashiIndexFromName(fallback);
  const keys: GlossaryKey[] = [
    "rashi_mesha",
    "rashi_vrishabha",
    "rashi_mithuna",
    "rashi_karka",
    "rashi_simha",
    "rashi_kanya",
    "rashi_tula",
    "rashi_vrischika",
    "rashi_dhanu",
    "rashi_makara",
    "rashi_kumbha",
    "rashi_meena",
  ];
  return normalized === null ? "rashi" : keys[normalized] ?? "rashi";
}

function VargaGlossaryList({ vargas }: { vargas: readonly string[] }) {
  if (!vargas.length) return <>-</>;
  return (
    <span className="varga-glossary-list">
      {vargas.map((varga, index) => (
        <GlossaryTerm termKey={vargaGlossaryKey(varga)} key={`varga-glossary-${varga}-${index}`}>
          {varga}
        </GlossaryTerm>
      ))}
    </span>
  );
}

const referenceGlossaryKeys: Partial<Record<ChartReference, GlossaryKey>> = {
  lagna: "lagna",
  moon: "chandra_lagna",
  sun: "surya_lagna",
  seventh: "house_7",
  twelfth: "house_12",
};

function chartReferenceForRelationshipRole(role: ReturnType<typeof compatibilityRelationshipRole>): ChartReference {
  const houses = role.focusHouses as readonly number[];
  if (houses.includes(7)) return "seventh";
  if (houses.includes(12)) return "twelfth";
  return "lagna";
}

type ChartPlacement = {
  body: string;
  rashi: string;
  rashiIndex: number | null;
  isLagna: boolean;
  longitude: number | null;
  nakshatra: string | null;
  pada: number | null;
  retrograde: boolean;
  dignity: GrahaDignity | null;
};

type ChartTextLine = {
  text: string;
  kind: "rashi" | "graha";
  dignity?: GrahaDignity | null;
  retrograde?: boolean;
  placement?: ChartPlacement;
};

function normalizeRashiIndex(value: number | null | undefined) {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  return ((Math.trunc(value) % 12) + 12) % 12;
}

function rashiIndexFromName(name: string | null | undefined) {
  const key = name?.trim();
  if (!key) return null;
  return rashiNameIndices[key] ?? null;
}

const rashiLordBodies: Record<number, string> = {
  0: "Mangala",
  1: "Shukra",
  2: "Budha",
  3: "Chandra",
  4: "Surya",
  5: "Budha",
  6: "Shukra",
  7: "Mangala",
  8: "Guru",
  9: "Shani",
  10: "Shani",
  11: "Guru",
};

function houseFromRashiIndex(rashiIndex: number | null | undefined, lagnaIndex: number | null | undefined) {
  if (rashiIndex === null || rashiIndex === undefined || lagnaIndex === null || lagnaIndex === undefined) return null;
  return ((rashiIndex - lagnaIndex + 12) % 12) + 1;
}

function ruledHousesForGraha(body: string, lagnaIndex: number | null | undefined) {
  const canonical = canonicalBody(body);
  if (lagnaIndex === null || lagnaIndex === undefined || canonical === "Rahu" || canonical === "Ketu") return [];
  return Object.entries(rashiLordBodies)
    .filter(([, lord]) => lord === canonical)
    .map(([rashiIndex]) => houseFromRashiIndex(Number(rashiIndex), lagnaIndex))
    .filter((house): house is number => typeof house === "number")
    .sort((left, right) => left - right);
}

function isLagnaBody(body: string) {
  return body === "Lagna" || body === "Ascendant";
}

function canonicalBody(body: string | null | undefined) {
  const clean = body?.trim() ?? "";
  return bodyAliases[clean] ?? clean;
}

function grahaTermLabel(body: string, language: TermLanguage, mode: "short" | "long" = "long") {
  const canonical = canonicalBody(body);
  return termBodyLabels[language][canonical]?.[mode] ?? (mode === "short" ? northGrahaLabel(body) : labelRu(body));
}

function rashiTermLabel(index: number | null, fallback: string | null | undefined, language: TermLanguage, compact = false) {
  const normalized = index ?? rashiIndexFromName(fallback);
  if (normalized === null) return fallback || "-";
  return (compact ? rashiTermShortLabels[language] : rashiTermLabels[language])[normalized] ?? fallback ?? "-";
}

function rashiTermFromName(name: string | null | undefined, language: TermLanguage, compact = false) {
  return rashiTermLabel(rashiIndexFromName(name), name, language, compact);
}

function dignityForPlacement(body: string, rashiIndex: number | null, explicit?: string | null): GrahaDignity | null {
  const normalizedExplicit = explicit?.trim().toLowerCase();
  if (normalizedExplicit === "exaltation" || normalizedExplicit === "debilitation" || normalizedExplicit === "moolatrikona") {
    return normalizedExplicit;
  }
  const canonical = canonicalBody(body);
  if (rashiIndex === null || canonical === "Lagna") return null;
  if (exaltationSigns[canonical] === rashiIndex) return "exaltation";
  if (debilitationSigns[canonical] === rashiIndex) return "debilitation";
  if (moolatrikonaSigns[canonical] === rashiIndex) return "moolatrikona";
  return null;
}

function isRetrogradeGraha(graha: Pick<GrahaPosition, "speed_longitude"> & { retrograde?: boolean }) {
  return graha.retrograde === true || (typeof graha.speed_longitude === "number" && graha.speed_longitude < 0);
}

function dignitySymbol(dignity: GrahaDignity | null | undefined) {
  if (dignity === "exaltation") return "↑";
  if (dignity === "debilitation") return "↓";
  return "";
}

function dignityLabel(dignity: GrahaDignity | null | undefined) {
  if (dignity === "exaltation") return "экз.";
  if (dignity === "debilitation") return "деб.";
  if (dignity === "moolatrikona") return "мул.";
  return "";
}

function chartPlacementLabel(placement: ChartPlacement, language: TermLanguage) {
  const base = placement.isLagna ? grahaTermLabel("Lagna", language, "short") : grahaTermLabel(placement.body, language, "short");
  const retro = placement.retrograde ? `(${base})` : base;
  return `${retro}${dignitySymbol(placement.dignity)}`;
}

function activeChartPlacements(chart: BirthChart | null, varga: ActiveVargaChart | null): ChartPlacement[] {
  if (!chart) return [];

  if (varga) {
    return varga.placements.map((placement) => ({
      ...(() => {
        const rashiIndex = normalizeRashiIndex(placement.rashi_index) ?? rashiIndexFromName(placement.rashi);
        const natal = chart.grahas.find((graha) => canonicalBody(graha.body) === canonicalBody(placement.body));
        return {
          rashiIndex,
          retrograde: natal ? isRetrogradeGraha(natal) : false,
          dignity: dignityForPlacement(placement.body, rashiIndex, placement.dignity ?? natal?.dignity ?? null),
        };
      })(),
      body: placement.body,
      rashi: placement.rashi,
      isLagna: isLagnaBody(placement.body),
      longitude: null,
      nakshatra: null,
      pada: null,
    }));
  }

  const placements: ChartPlacement[] = [];
  if (chart.ascendant) {
    placements.push({
      body: "Lagna",
      rashi: chart.ascendant.rashi,
      rashiIndex: normalizeRashiIndex(chart.ascendant.rashi_index) ?? rashiIndexFromName(chart.ascendant.rashi),
      isLagna: true,
      longitude: chart.ascendant.longitude,
      nakshatra: chart.ascendant.nakshatra,
      pada: chart.ascendant.pada,
      retrograde: false,
      dignity: null,
    });
  }
  placements.push(
    ...chart.grahas.map((graha) => {
      const rashiIndex = normalizeRashiIndex(graha.rashi_index) ?? rashiIndexFromName(graha.rashi);
      return {
        body: graha.body,
        rashi: graha.rashi,
        rashiIndex,
        isLagna: false,
        longitude: graha.longitude,
        nakshatra: graha.nakshatra,
        pada: graha.pada,
        retrograde: isRetrogradeGraha(graha),
        dignity: dignityForPlacement(graha.body, rashiIndex, graha.dignity),
      };
    }),
  );
  return placements;
}

function placementsBySign(placements: ChartPlacement[]) {
  const bySign = new Map<number, ChartPlacement[]>();
  placements.forEach((placement) => {
    if (placement.rashiIndex === null) return;
    const list = bySign.get(placement.rashiIndex) ?? [];
    if (!list.some((item) => item.body === placement.body)) list.push(placement);
    bySign.set(placement.rashiIndex, list);
  });
  return bySign;
}

function lagnaRashiIndex(chart: BirthChart | null, placements: ChartPlacement[]) {
  const fromPlacements = placements.find((placement) => placement.isLagna && placement.rashiIndex !== null)?.rashiIndex;
  return fromPlacements ?? normalizeRashiIndex(chart?.ascendant?.rashi_index) ?? rashiIndexFromName(chart?.ascendant?.rashi);
}

function houseReferenceRashiIndex(chart: BirthChart | null, houseNumber: number) {
  const house = chart?.houses.find((row) => row.house === houseNumber);
  return normalizeRashiIndex(house?.rashi_index) ?? rashiIndexFromName(house?.rashi);
}

function chartReferenceRashiIndex(
  chart: BirthChart | null,
  placements: ChartPlacement[],
  reference: ChartReference,
) {
  if (reference === "moon") {
    const moon = placements.find((placement) => placement.body === "Chandra" || placement.body === "Moon");
    return moon?.rashiIndex ?? lagnaRashiIndex(chart, placements);
  }
  if (reference === "sun") {
    const sun = placements.find((placement) => placement.body === "Surya" || placement.body === "Sun");
    return sun?.rashiIndex ?? lagnaRashiIndex(chart, placements);
  }
  if (reference === "seventh") {
    return houseReferenceRashiIndex(chart, 7) ?? lagnaRashiIndex(chart, placements);
  }
  if (reference === "twelfth") {
    return houseReferenceRashiIndex(chart, 12) ?? lagnaRashiIndex(chart, placements);
  }
  return lagnaRashiIndex(chart, placements);
}

function northIndianHouseItems(
  chart: BirthChart | null,
  varga: ActiveVargaChart | null,
  chartReference: ChartReference = "lagna",
): NorthIndianHouseItem[] {
  if (!chart) {
    return Array.from({ length: 12 }, (_, index) => ({
      house: index + 1,
      rashi: "",
      rashiIndex: null,
      placements: [],
    }));
  }
  const placements = activeChartPlacements(chart, varga);
  const bySign = placementsBySign(placements);
  const referenceIndex = chartReferenceRashiIndex(chart, placements, chartReference) ?? 0;
  const rows = !varga && chartReference === "lagna" && chart.houses.length
    ? chart.houses
    : Array.from({ length: 12 }, (_, index) => ({
        house: index + 1,
        rashi_index: (referenceIndex + index) % 12,
        rashi: rashiNames[(referenceIndex + index) % 12],
      }));

  return rows.map((house) => {
    const rashiIndex = normalizeRashiIndex(house.rashi_index) ?? rashiIndexFromName(house.rashi);
    return {
      house: house.house,
      rashi: house.rashi,
      rashiIndex,
      placements: rashiIndex === null ? [] : bySign.get(rashiIndex) ?? [],
    };
  });
}

function ChartPreview({
  chart,
  varga,
  chartStyle,
  chartReference = "lagna",
  termLanguage = "sanskrit",
  houseHintsEnabled = true,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartStyle: "north" | "south";
  chartReference?: ChartReference;
  termLanguage?: TermLanguage;
  houseHintsEnabled?: boolean;
}) {
  return chartStyle === "south" ? (
    <SouthIndianChartPreview chart={chart} varga={varga} chartReference={chartReference} termLanguage={termLanguage} houseHintsEnabled={houseHintsEnabled} />
  ) : (
    <NorthIndianChartPreview chart={chart} varga={varga} chartReference={chartReference} termLanguage={termLanguage} houseHintsEnabled={houseHintsEnabled} />
  );
}

function readerExplanationForHouse({
  chart,
  varga,
  chartReference,
  house,
  termLanguage,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference: ChartReference;
  house: number;
  termLanguage: TermLanguage;
}): ReaderExplanationDetail {
  const item = jyotishGlossary[houseGlossaryKey(house)];
  const houseItem = northIndianHouseItems(chart, varga, chartReference).find((row) => row.house === house);
  const rashiIndex = houseItem?.rashiIndex ?? null;
  const rashiLabel = rashiIndex === null ? "-" : rashiTermFromName(houseItem?.rashi ?? rashiNames[rashiIndex], termLanguage);
  const lordBody = rashiIndex === null ? null : rashiLordBodies[rashiIndex];
  const placements = houseItem?.placements ?? [];
  const placementText = placements.length ? placements.map((placement) => chartPlacementLabel(placement, termLanguage)).join(", ") : "нет грах";
  const referenceLabel = chartReferenceOptions.find((option) => option.key === chartReference)?.label ?? "Лагна";
  const houseMeaning = houseShastraMeanings[house];
  return {
    title: item.label,
    context: `Карта: отсчёт ${referenceLabel}`,
    text: [
      `${houseMeaning?.theme ?? item.text}`,
      `В шастрическом чтении дом сначала показывает сферу жизни, затем знак показывает форму проявления, а хозяин знака показывает канал, через который дом реально даёт результат.`,
      `В этой карте: знак ${rashiLabel}, хозяин ${lordBody ? grahaTermLabel(lordBody, termLanguage) : "-"}. Грахи в доме: ${placementText}.`,
      placements.length
        ? "Грахи в доме прямо окрашивают бхаву своей каракатвой; дальше нужно смотреть их силу, достоинство, управляемые дома, накшатру, аспекты и дашу."
        : "Пустой дом не считается пустым по результату: его читают через хозяина, аспекты, силу диспозитора, связь с караками и дашу.",
      houseMeaning?.caution ?? "",
    ].filter(Boolean).join("\n\n"),
  };
}

function readerExplanationForRashi({
  chart,
  varga,
  chartReference,
  house,
  rashiIndex,
  rashiName,
  termLanguage,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference: ChartReference;
  house: number | null;
  rashiIndex: number | null;
  rashiName: string | null | undefined;
  termLanguage: TermLanguage;
}): ReaderExplanationDetail {
  const normalizedRashiIndex = normalizeRashiIndex(rashiIndex) ?? rashiIndexFromName(rashiName);
  const fallbackName = normalizedRashiIndex === null ? rashiName : rashiNames[normalizedRashiIndex];
  const rashiLabel = rashiTermLabel(normalizedRashiIndex, fallbackName, termLanguage);
  const glossary = jyotishGlossary[rashiGlossaryKey(normalizedRashiIndex, fallbackName)];
  const houseItem = house ? northIndianHouseItems(chart, varga, chartReference).find((row) => row.house === house) : null;
  const placements = houseItem?.placements ?? [];
  const lordBody = normalizedRashiIndex === null ? null : rashiLordBodies[normalizedRashiIndex];
  const placementsText = placements.length
    ? placements.map((placement) => chartPlacementLabel(placement, termLanguage)).join(", ")
    : "нет грах";
  const lagnaIndex = normalizeRashiIndex(chart?.ascendant?.rashi_index) ?? rashiIndexFromName(chart?.ascendant?.rashi);
  const lordGraha = lordBody && chart ? chart.grahas.find((graha) => canonicalBody(graha.body) === canonicalBody(lordBody)) : null;
  const lordHouse = lordGraha
    ? houseFromRashiIndex(normalizeRashiIndex(lordGraha.rashi_index) ?? rashiIndexFromName(lordGraha.rashi), lagnaIndex)
    : null;
  const houseText = house ? `${house} дом` : "дом не определён";
  return {
    title: rashiLabel,
    context: house ? `${houseText} карты` : "Знак",
    text: [
      glossary?.text ?? "Раши показывает среду, стиль проявления и качество, через которое действует дом или граха.",
      `В этой карте ${rashiLabel} стоит как ${houseText}. Хозяин знака: ${lordBody ? grahaTermLabel(lordBody, termLanguage) : "-"}. Грахи в знаке: ${placementsText}.`,
      lordGraha
        ? `Хозяин знака находится в ${rashiTermFromName(lordGraha.rashi, termLanguage)}${lordHouse ? `, ${lordHouse} дом` : ""}. Поэтому результат знака нужно читать через положение, силу, накшатру и достоинство его хозяина.`
        : "Если хозяин знака не показан в данных, знак читается через свою природу, грахи внутри него, аспекты и общий контекст карты.",
      "По классическому чтению знак сам по себе не заменяет дом: дом показывает сферу, знак даёт способ проявления, а хозяин знака показывает канал результата.",
    ].join("\n\n"),
  };
}

function ChartHouseHintPopover({
  chart,
  varga,
  chartReference,
  house,
  termLanguage,
  position,
  onClose,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference: ChartReference;
  house: number;
  termLanguage: TermLanguage;
  position: { x: number; y: number };
  onClose: () => void;
}) {
  const item = jyotishGlossary[houseGlossaryKey(house)];
  const houseItem = northIndianHouseItems(chart, varga, chartReference).find((row) => row.house === house);
  const rashiIndex = houseItem?.rashiIndex ?? null;
  const rashiLabel = rashiIndex === null ? "-" : rashiTermFromName(houseItem?.rashi ?? rashiNames[rashiIndex], termLanguage);
  const lordBody = rashiIndex === null ? null : rashiLordBodies[rashiIndex];
  const placements = houseItem?.placements ?? [];
  const placementText = placements.length ? placements.map((placement) => chartPlacementLabel(placement, termLanguage)).join(", ") : "нет грах";
  const referenceLabel = chartReferenceOptions.find((option) => option.key === chartReference)?.label ?? "Лагна";
  const detail = readerExplanationForHouse({ chart, varga, chartReference, house, termLanguage });
  return (
    <div
      className="chart-house-popover"
      style={{
        left: `${position.x}%`,
        top: `${position.y}%`,
        transform: `translate(${position.x < 28 ? "0" : position.x > 72 ? "-100%" : "-50%"}, ${position.y < 24 ? "0" : position.y > 76 ? "-100%" : "-50%"})`,
      }}
      role="tooltip"
      onPointerDown={(event) => event.stopPropagation()}
    >
      <div className="chart-house-popover-head">
        <strong>{item.label}</strong>
        <button type="button" onClick={onClose} aria-label="Закрыть подсказку">×</button>
      </div>
      <div className="selected-reader-text">
        {detail.text.split("\n\n").slice(0, 3).map((paragraph) => (
          <p key={paragraph}>{paragraph}</p>
        ))}
      </div>
      <dl>
        <div><dt>Знак</dt><dd>{rashiLabel}</dd></div>
        <div><dt>Хозяин</dt><dd>{lordBody ? grahaTermLabel(lordBody, termLanguage) : "-"}</dd></div>
        <div><dt>Грахи</dt><dd>{placementText}</dd></div>
      </dl>
      <em>{referenceLabel}: дом, знак, хозяин и грахи внутри.</em>
      <button
        type="button"
        className="help-ai-action chart-house-popover-ai"
        onClick={() =>
          requestAiExplanation({
            title: `${item.label} в карте`,
            text: detail.text,
          })
        }
      >
        Спросить
      </button>
    </div>
  );
}

function StartChartNotice() {
  return (
    <div className="start-chart-notice" aria-label="Карта ещё не рассчитана">
      <strong>Карта на сейчас</strong>
      <span>Если своих данных ещё нет, используется текущий день. Для личной карты введите дату, время и место рождения.</span>
      <a href="#birth-form">Перейти к данным рождения</a>
    </div>
  );
}

function ChartNotationLegend({ termLanguage }: { termLanguage: TermLanguage }) {
  const sample = {
    retrograde: `(${grahaTermLabel("Guru", termLanguage, "short")})`,
    exaltation: `${grahaTermLabel("Surya", termLanguage, "short")}↑`,
    debilitation: `${grahaTermLabel("Shukra", termLanguage, "short")}↓`,
    moolatrikona: grahaTermLabel("Mangala", termLanguage, "short"),
  };

  return (
    <div className="chart-notation-legend" aria-label="Обозначения в карте">
      <div>
        <strong>Обозначения карты</strong>
        <span>В таблице статусы написаны словами</span>
      </div>
      <span><b>{sample.retrograde}</b><GlossaryTerm termKey="retrograde">ретроградность</GlossaryTerm></span>
      <span><b className="dignity-exaltation">{sample.exaltation}</b><GlossaryTerm termKey="exaltation">экзальтация</GlossaryTerm></span>
      <span><b className="dignity-debilitation">{sample.debilitation}</b><GlossaryTerm termKey="debilitation">дебилитация</GlossaryTerm></span>
      <span><b className="dignity-moolatrikona">{sample.moolatrikona}</b><GlossaryTerm termKey="moolatrikona">мулатрикона</GlossaryTerm></span>
    </div>
  );
}

function ChartReferenceToggle({
  chart,
  value,
  onChange,
}: {
  chart: BirthChart | null;
  value: ChartReference;
  onChange: (value: ChartReference) => void;
}) {
  const [openKey, setOpenKey] = useState<ChartReference | null>(null);

  return (
    <div className="chart-reference-toggle" aria-label="Точка отсчёта домов">
      {chartReferenceOptions.map((option) => {
        const glossaryKey = referenceGlossaryKeys[option.key];
        const glossaryItem = glossaryKey ? jyotishGlossary[glossaryKey] : null;
        const isOpen = openKey === option.key;
        return (
          <button
            type="button"
            className={value === option.key ? "active" : ""}
            disabled={!chart}
            key={option.key}
            onClick={() => {
              onChange(option.key);
              setOpenKey((current) => (current === option.key ? null : option.key));
            }}
          >
            <strong>{option.label}</strong>
            <span>{option.hint}</span>
            {isOpen && glossaryItem ? (
              <em className="chart-reference-help">
                <b>{glossaryItem.label}</b>
                {glossaryItem.text}
              </em>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}

function QuickVargaSwitch({
  chart,
  chartMode,
  vargaOptions,
  onChartModeChange,
}: {
  chart: BirthChart | null;
  chartMode: string;
  vargaOptions: string[];
  onChartModeChange: (value: string) => void;
}) {
  const available = new Set(vargaOptions.length ? vargaOptions : ["D1"]);
  return (
    <div className="quick-varga-switch" aria-label="Быстрый выбор D-карты">
      {primaryVargaTabCodes.map((code) => {
        const enabled = Boolean(chart) && available.has(code);
        return (
          <button
            type="button"
            key={`quick-varga-${code}`}
            className={chartMode === code ? "active" : ""}
            disabled={!enabled}
            onClick={() => onChartModeChange(code)}
          >
            {code}
          </button>
        );
      })}
    </div>
  );
}

function ReferenceChartBoard({
  chart,
  chartStyle,
  activeReference,
  onSelect,
}: {
  chart: BirthChart | null;
  chartStyle: "north" | "south";
  activeReference: ChartReference;
  onSelect: (value: ChartReference) => void;
}) {
  return (
    <div className="reference-chart-board" aria-label="D1 от Лагны, Луны, Солнца, 7 и 12 дома">
      <div className="reference-chart-head">
        <strong>Сударшана D1</strong>
        <span>Лагна, Чандра, Сурья, 7 и 12 дома рядом</span>
      </div>
      <div className="reference-chart-grid">
        {chartReferenceOptions.map((option) => (
          <button
            type="button"
            className={`reference-chart-card${activeReference === option.key ? " active" : ""}`}
            disabled={!chart}
            key={option.key}
            onClick={() => onSelect(option.key)}
          >
            <div>
              <strong>{option.label}</strong>
              <span>{option.hint}</span>
            </div>
            <div className="reference-chart-preview">
              {chartStyle === "south" ? (
                <SouthIndianChartGrid chart={chart} varga={null} chartReference={option.key} compact />
              ) : (
                <NorthIndianChartSvg chart={chart} varga={null} chartReference={option.key} compact />
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function BhavaOverviewBoard({ chart, termLanguage }: { chart: BirthChart | null; termLanguage: TermLanguage }) {
  const grahasByHouse = new Map<number, GrahaPosition[]>();
  if (chart) {
    for (const house of chart.houses) {
      const rashiIndex = normalizeRashiIndex(house.rashi_index);
      if (rashiIndex === null) continue;
      grahasByHouse.set(
        house.house,
        chart.grahas.filter((graha) => normalizeRashiIndex(graha.rashi_index ?? rashiIndexFromName(graha.rashi)) === rashiIndex),
      );
    }
  }
  const cuspByHouse = new Map((chart?.house_cusps ?? []).map((cusp) => [cusp.house, cusp]));
  const rows = Array.from({ length: 12 }, (_, index) => {
    const house = chart?.houses.find((item) => item.house === index + 1);
    const cusp = cuspByHouse.get(index + 1);
    return {
      house: index + 1,
      rashi: house?.rashi ?? cusp?.rashi ?? "",
      cusp,
      grahas: grahasByHouse.get(index + 1) ?? [],
    };
  });

  return (
    <div className="bhava-overview-board" aria-label="Бхава и дома">
      <div className="bhava-overview-head">
        <div>
          <strong>Бхава / дома</strong>
          <span>{chart?.settings?.bhava_system === "whole_sign" ? "Whole Sign: дома совпадают со знаками" : chart?.settings?.bhava_system ?? "ожидает расчёт"}</span>
        </div>
        <em>{chart?.house_cusps?.length ? "куспиды доступны" : "без куспидов"}</em>
      </div>
      <div className="bhava-overview-grid">
        {rows.map((row) => (
          <div className={row.grahas.length ? "filled" : ""} key={row.house}>
            <span>{row.house} дом</span>
            <strong>{row.rashi ? rashiTermFromName(row.rashi, termLanguage) : "ожидает"}</strong>
            <small>{row.cusp ? formatSignDegrees(row.cusp.longitude) : "куспид -"} · {row.grahas.length ? row.grahas.map((graha) => grahaTermLabel(graha.body, termLanguage, "short")).join(" ") : "пусто"}</small>
          </div>
        ))}
      </div>
    </div>
  );
}

function NorthIndianChartPreview({
  chart,
  varga,
  chartReference = "lagna",
  termLanguage = "sanskrit",
  houseHintsEnabled = true,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference?: ChartReference;
  termLanguage?: TermLanguage;
  houseHintsEnabled?: boolean;
}) {
  const [pinnedHouse, setPinnedHouse] = useState<number | null>(null);
  useEffect(() => {
    if (!houseHintsEnabled) {
      setPinnedHouse(null);
    }
  }, [houseHintsEnabled]);
  const activeHouse = houseHintsEnabled ? pinnedHouse : null;
  const activeCell = activeHouse ? northIndianHouseCells[activeHouse] : null;
  function selectHouse(house: number) {
    setPinnedHouse((current) => (current === house ? null : house));
  }
  return (
    <>
      <div className="chart-box" aria-label="Предпросмотр североиндийской карты">
        <NorthIndianChartSvg
          chart={chart}
          varga={varga}
          chartReference={chartReference}
          termLanguage={termLanguage}
          onHouseSelect={houseHintsEnabled ? selectHouse : undefined}
          selectedHouse={activeHouse}
        />
        {houseHintsEnabled && activeHouse && activeCell ? (
          <ChartHouseHintPopover
            chart={chart}
            varga={varga}
            chartReference={chartReference}
            house={activeHouse}
            termLanguage={termLanguage}
            position={{ x: (activeCell.centerX / 400) * 100, y: (activeCell.centerY / 400) * 100 }}
            onClose={() => {
              setPinnedHouse(null);
            }}
          />
        ) : null}
      </div>
    </>
  );
}

function NorthIndianChartSvg({
  chart,
  varga,
  chartReference = "lagna",
  compact = false,
  termLanguage = "sanskrit",
  onHouseSelect,
  selectedHouse,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference?: ChartReference;
  compact?: boolean;
  termLanguage?: TermLanguage;
  onHouseSelect?: (house: number) => void;
  selectedHouse?: number | null;
}) {
  const houses = northIndianHouseItems(chart, varga, chartReference);
  return (
      <svg className={compact ? "chart-svg chart-svg-mini" : "chart-svg"} viewBox="0 0 400 400" role="img" aria-label="Североиндийская сетка карты">
        <rect x="1.5" y="1.5" width="397" height="397" fill="white" stroke="#b88a2f" strokeWidth="1.5" />
        <path d="M2 2 L398 398 M398 2 L2 398" stroke="#c99a43" strokeWidth="1" />
        <path d="M200 2 L398 200 L200 398 L2 200 Z" fill="none" stroke="#c99a43" strokeWidth="1" />
        {houses.map((house) => {
          const cell = northIndianHouseCells[house.house];
          const hitPolygon = northIndianHousePolygons[house.house];
          const signLabel = rashiChartLabel(house.rashiIndex, house.rashi, termLanguage, compact);
          const textLines = northIndianCellLines(house, compact, termLanguage);
          const lineGap = compact ? (textLines.length > 4 ? 10 : 12) : (textLines.length > 5 ? 11 : 13);
          const centerY = safeSymbolCenterY(cell.centerY, textLines.length, lineGap);
          const firstLineY = firstSymbolLineY(centerY, textLines.length, lineGap);
          return (
            <g
              className={`chart-house-group${selectedHouse === house.house ? " selected" : ""}${onHouseSelect ? " interactive" : ""}`}
              data-house={house.house}
              key={house.house}
              role={onHouseSelect ? "button" : undefined}
              aria-label={onHouseSelect ? `${house.house} дом` : undefined}
              tabIndex={onHouseSelect ? 0 : undefined}
              onClick={onHouseSelect ? () => onHouseSelect(house.house) : undefined}
              onKeyDown={
                onHouseSelect
                  ? (event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        onHouseSelect(house.house);
                      }
                    }
                  : undefined
              }
            >
              {onHouseSelect && hitPolygon ? (
                <polygon
                  className="chart-house-hit-zone"
                  points={hitPolygon.map((point) => `${point.x},${point.y}`).join(" ")}
                  onPointerDown={(event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    onHouseSelect(house.house);
                  }}
                  onClick={(event) => {
                    event.preventDefault();
                    event.stopPropagation();
                  }}
                />
              ) : null}
              <text
                className={`chart-cell-text${textLines.length > 5 ? " dense" : ""}`}
                x={cell.centerX}
                y={firstLineY}
                textAnchor="middle"
              >
                {textLines.map((line, index) => {
                  if (line.kind === "rashi") {
                    return (
                      <tspan
                        className="chart-rashi-label interactive-rashi"
                        key={`${house.house}-${line.text}-${index}`}
                        x={cell.centerX}
                        dy={index === 0 ? 0 : lineGap}
                        role="button"
                        tabIndex={0}
                        onPointerDown={(event) => {
                          event.preventDefault();
                          event.stopPropagation();
                          publishReaderExplanation(readerExplanationForRashi({
                            chart,
                            varga,
                            chartReference,
                            house: house.house,
                            rashiIndex: house.rashiIndex,
                            rashiName: house.rashi,
                            termLanguage,
                          }));
                        }}
                        onClick={(event) => {
                          event.preventDefault();
                          event.stopPropagation();
                        }}
                        onKeyDown={(event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            event.stopPropagation();
                            publishReaderExplanation(readerExplanationForRashi({
                              chart,
                              varga,
                              chartReference,
                              house: house.house,
                              rashiIndex: house.rashiIndex,
                              rashiName: house.rashi,
                              termLanguage,
                            }));
                          }
                        }}
                      >
                        {line.text}
                      </tspan>
                    );
                  }
                  return (
                    <tspan
                      className={`chart-graha-detail${line.placement ? " interactive-placement" : ""}${line.dignity ? ` dignity-${line.dignity}` : ""}${line.retrograde ? " retrograde" : ""}`}
                      key={`${house.house}-${line.text}-${index}`}
                      x={cell.centerX}
                      dy={index === 0 ? 0 : lineGap}
                      role={line.placement ? "button" : undefined}
                      tabIndex={line.placement ? 0 : undefined}
                      onPointerDown={line.placement ? (event) => {
                        event.preventDefault();
                        event.stopPropagation();
                        publishReaderExplanation(readerExplanationForPlacement({ chart, varga, placement: line.placement!, house: house.house, termLanguage }));
                      } : undefined}
                      onClick={line.placement ? (event) => {
                        event.preventDefault();
                        event.stopPropagation();
                      } : undefined}
                      onKeyDown={line.placement ? (event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.stopPropagation();
                          publishReaderExplanation(readerExplanationForPlacement({ chart, varga, placement: line.placement!, house: house.house, termLanguage }));
                        }
                      } : undefined}
                    >
                      {line.text}
                    </tspan>
                  );
                })}
              </text>
            </g>
          );
        })}
      </svg>
  );
}

const southIndianSignCells: Record<number, { row: number; col: number }> = {
  11: { row: 0, col: 0 },
  0: { row: 0, col: 1 },
  1: { row: 0, col: 2 },
  2: { row: 0, col: 3 },
  10: { row: 1, col: 0 },
  3: { row: 1, col: 3 },
  9: { row: 2, col: 0 },
  4: { row: 2, col: 3 },
  8: { row: 3, col: 0 },
  7: { row: 3, col: 1 },
  6: { row: 3, col: 2 },
  5: { row: 3, col: 3 },
};

function southIndianHouseTooltipPosition(
  chart: BirthChart | null,
  varga: ActiveVargaChart | null,
  chartReference: ChartReference,
  house: number,
) {
  const placements = activeChartPlacements(chart, varga);
  const lagnaIndex = chartReferenceRashiIndex(chart, placements, chartReference);
  if (lagnaIndex === null) return null;
  const rashiIndex = (lagnaIndex + house - 1) % 12;
  const cell = southIndianSignCells[rashiIndex];
  if (!cell) return null;
  return { x: ((cell.col + 0.5) / 4) * 100, y: ((cell.row + 0.5) / 4) * 100 };
}

function SouthIndianChartPreview({
  chart,
  varga,
  chartReference = "lagna",
  termLanguage = "sanskrit",
  houseHintsEnabled = true,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference?: ChartReference;
  termLanguage?: TermLanguage;
  houseHintsEnabled?: boolean;
}) {
  const [pinnedHouse, setPinnedHouse] = useState<number | null>(null);
  useEffect(() => {
    if (!houseHintsEnabled) {
      setPinnedHouse(null);
    }
  }, [houseHintsEnabled]);
  const activeHouse = houseHintsEnabled ? pinnedHouse : null;
  const activePosition = activeHouse ? southIndianHouseTooltipPosition(chart, varga, chartReference, activeHouse) : null;
  function selectHouse(house: number) {
    setPinnedHouse((current) => (current === house ? null : house));
  }
  return (
    <>
      <div className="chart-box south-chart-box" aria-label="Предпросмотр южноиндийской карты">
        <SouthIndianChartGrid
          chart={chart}
          varga={varga}
          chartReference={chartReference}
          termLanguage={termLanguage}
          onHouseSelect={houseHintsEnabled ? selectHouse : undefined}
          selectedHouse={activeHouse}
        />
        {houseHintsEnabled && activeHouse && activePosition ? (
          <ChartHouseHintPopover
            chart={chart}
            varga={varga}
            chartReference={chartReference}
            house={activeHouse}
            termLanguage={termLanguage}
            position={activePosition}
            onClose={() => {
              setPinnedHouse(null);
            }}
          />
        ) : null}
      </div>
    </>
  );
}

function SouthIndianChartGrid({
  chart,
  varga,
  chartReference = "lagna",
  compact = false,
  termLanguage = "sanskrit",
  onHouseSelect,
  selectedHouse,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference?: ChartReference;
  compact?: boolean;
  termLanguage?: TermLanguage;
  onHouseSelect?: (house: number) => void;
  selectedHouse?: number | null;
}) {
  const placements = activeChartPlacements(chart, varga);
  const bySign = placementsBySign(placements);
  const lagnaIndex = chartReferenceRashiIndex(chart, placements, chartReference);
  return (
    <div className={compact ? "south-chart-grid south-chart-grid-mini" : "south-chart-grid"}>
      {Array.from({ length: 16 }, (_, index) => {
        const row = Math.floor(index / 4);
        const col = index % 4;
        const signIndex = Object.entries(southIndianSignCells).find(([, cell]) => cell.row === row && cell.col === col)?.[0];
        if (signIndex === undefined) return <div className="south-chart-center" key={`center-${index}`} />;
        const rashiIndex = Number(signIndex);
        const house = lagnaIndex === null ? null : ((rashiIndex - lagnaIndex + 12) % 12) + 1;
        const cellPlacements = bySign.get(rashiIndex) ?? [];
        const interactive = Boolean(onHouseSelect && house);
        return (
          <div
            className={`south-chart-cell${selectedHouse === house ? " selected" : ""}${interactive ? " interactive" : ""}`}
            data-house={house ?? undefined}
            key={`rashi-${rashiIndex}`}
            role={interactive ? "button" : undefined}
            aria-label={interactive && house ? `${house} дом` : undefined}
            tabIndex={interactive ? 0 : undefined}
            onPointerDown={interactive && house ? (event) => {
              event.preventDefault();
              event.stopPropagation();
              onHouseSelect?.(house);
            } : undefined}
            onClick={interactive ? (event) => {
              event.preventDefault();
              event.stopPropagation();
            } : undefined}
            onKeyDown={
              interactive && house
                ? (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      onHouseSelect?.(house);
                    }
                  }
                : undefined
            }
          >
            <strong>{house ? `${house} ` : ""}{rashiChartLabel(rashiIndex, rashiNames[rashiIndex], termLanguage, compact)}</strong>
            {cellPlacements.slice(0, compact ? 4 : 7).map((placement) => (
              <span
                className={`interactive-placement${placement.dignity ? ` dignity-${placement.dignity}` : ""}${placement.retrograde ? " retrograde" : ""}`}
                key={`${rashiIndex}-${placement.body}`}
                role="button"
                tabIndex={0}
                onPointerDown={(event) => {
                  event.preventDefault();
                  event.stopPropagation();
                  publishReaderExplanation(readerExplanationForPlacement({ chart, varga, placement, house, termLanguage }));
                }}
                onClick={(event) => {
                  event.preventDefault();
                  event.stopPropagation();
                }}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    event.stopPropagation();
                    publishReaderExplanation(readerExplanationForPlacement({ chart, varga, placement, house, termLanguage }));
                  }
                }}
              >
                {chartPlacementLabel(placement, termLanguage)}
              </span>
            ))}
            {cellPlacements.length > (compact ? 4 : 7) ? <em>+{cellPlacements.length - (compact ? 4 : 7)}</em> : null}
          </div>
        );
      })}
    </div>
  );
}

function northIndianCellLines(house: NorthIndianHouseItem, compact = false, termLanguage: TermLanguage = "sanskrit"): ChartTextLine[] {
  if (house.rashiIndex === null && !house.placements.length) {
    return [];
  }
  if (compact) {
    const placements = house.placements.map((placement) => ({
      text: chartPlacementLabel(placement, termLanguage),
      kind: "graha" as const,
      dignity: placement.dignity,
      retrograde: placement.retrograde,
      placement,
    }));
    return [
      { text: `${house.house} ${rashiChartLabel(house.rashiIndex, house.rashi, termLanguage, true)}`, kind: "rashi" },
      ...placements.slice(0, 4),
      ...(placements.length > 4 ? [{ text: `+${placements.length - 4}`, kind: "graha" as const }] : []),
    ];
  }
  return [
    { text: `${house.house} ${rashiChartLabel(house.rashiIndex, house.rashi, termLanguage, true)}`, kind: "rashi" },
    ...house.placements.map((placement) => compactPlacementLine(placement, termLanguage)),
  ];
}

function compactPlacementLine(placement: ChartPlacement, termLanguage: TermLanguage): ChartTextLine {
  const label = chartPlacementLabel(placement, termLanguage);
  return {
    text: placement.longitude === null ? label : `${label} ${formatSignDegrees(placement.longitude)}`,
    kind: "graha",
    dignity: placement.dignity,
    retrograde: placement.retrograde,
    placement,
  };
}

function fullPlacementTitle(placement: ChartPlacement, termLanguage: TermLanguage = "sanskrit") {
  const label = placement.isLagna ? grahaTermLabel("Lagna", termLanguage) : grahaTermLabel(placement.body, termLanguage);
  if (placement.longitude === null) return label;
  const nakshatra = placement.nakshatra ? `, ${placement.nakshatra} ${placement.pada ?? ""}` : "";
  const dignity = dignityLabel(placement.dignity);
  const retrograde = placement.retrograde ? ", ретроградная" : "";
  return `${label}: ${formatSignDegrees(placement.longitude)}${nakshatra}${dignity ? `, ${dignity}` : ""}${retrograde}`;
}

function rashiChartLabel(index: number | null, fallback: string, termLanguage: TermLanguage = "sanskrit", compact = true) {
  return rashiTermLabel(index, fallback, termLanguage, compact);
}

function formatSignDegrees(value: number) {
  const normalized = ((value % 360) + 360) % 360;
  const withinSign = normalized % 30;
  const degrees = Math.floor(withinSign);
  const minutes = Math.round((withinSign - degrees) * 60);
  const displayDegrees = minutes === 60 ? degrees + 1 : degrees;
  const displayMinutes = minutes === 60 ? 0 : minutes;
  return `${String(displayDegrees).padStart(2, "0")}°${String(displayMinutes).padStart(2, "0")}'`;
}

function symbolLines(symbols: string[], maxPerLine?: number) {
  const limit = maxPerLine ?? (symbols.length > 2 ? 2 : 3);
  const lines: string[] = [];
  for (let index = 0; index < symbols.length; index += limit) {
    lines.push(symbols.slice(index, index + limit).join(" "));
  }
  return lines;
}

const shodashaVargaCodes = [
  "D1",
  "D2",
  "D3",
  "D4",
  "D7",
  "D9",
  "D10",
  "D12",
  "D16",
  "D20",
  "D24",
  "D27",
  "D30",
  "D40",
  "D45",
  "D60",
] as const;

const jaiminiVargaCodes = ["D5", "D6", "D8", "D11"] as const;
const vargaSnapshotCodes = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"] as const;
const jaiminiVargaCodeSet = new Set<string>(jaiminiVargaCodes);

const vargaSchemeGroups = [
  { key: "shadvarga", label: "Shad", title: "Shadvarga", hint: "D1, D2, D3, D9, D12, D30", codes: ["D1", "D2", "D3", "D9", "D12", "D30"] },
  { key: "saptavarga", label: "Sapta", title: "Saptavarga", hint: "D1, D2, D3, D7, D9, D12, D30", codes: ["D1", "D2", "D3", "D7", "D9", "D12", "D30"] },
  { key: "dashavarga", label: "Dasha", title: "Dashavarga", hint: "D1, D2, D3, D7, D9, D10, D12, D16, D30, D60", codes: ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D30", "D60"] },
  { key: "shodasha", label: "16", title: "Shodasha Varga", hint: "D1-D60", codes: shodashaVargaCodes },
  { key: "jaimini", label: "Jai", title: "Jaimini Vargas", hint: jaiminiVargaCodes.join(", "), codes: jaiminiVargaCodes },
] as const;

type VargaSchemeKey = (typeof vargaSchemeGroups)[number]["key"];

const vargaPurposeLabels: Record<string, string> = {
  D1: "Раши / тело",
  D2: "Деньги",
  D3: "Братья",
  D4: "Дом",
  D5: "Власть",
  D6: "Болезни",
  D7: "Дети",
  D8: "Внезапное",
  D9: "Навамша",
  D10: "Карьера",
  D11: "Рудра",
  D12: "Родители",
  D16: "Комфорт",
  D20: "Садхана",
  D24: "Учёба",
  D27: "Сила",
  D30: "Риски",
  D40: "Материнская линия",
  D45: "Отцовская линия",
  D60: "Карма",
};

function availableCodeForVargaCodes(chart: BirthChart | null, codes: readonly string[]) {
  return codes.find((code) => (code === "D1" ? Boolean(chart) : Boolean(chart?.vargas?.[code])));
}

function vargaCodeNumber(code: string) {
  const match = code.match(/^D(\d+)$/);
  return match ? Number(match[1]) : Number.POSITIVE_INFINITY;
}

function availableVargaCodes(chart: BirthChart | null) {
  const codes = new Set<string>();
  if (chart) codes.add("D1");
  Object.keys(chart?.vargas ?? {}).forEach((code) => codes.add(code));
  return Array.from(codes).sort((left, right) => vargaCodeNumber(left) - vargaCodeNumber(right) || left.localeCompare(right));
}

function vargaCoverage(chart: BirthChart | null) {
  const available = new Set(availableVargaCodes(chart));
  const ready = vargaSnapshotCodes.filter((code) => available.has(code));
  const missing = vargaSnapshotCodes.filter((code) => !available.has(code));
  const pendingJaimini = missing.filter((code) => jaiminiVargaCodeSet.has(code));
  return { ready, missing, pendingJaimini, total: vargaSnapshotCodes.length };
}

function unavailableVargaLabel(code: string) {
  return jaiminiVargaCodeSet.has(code) ? "позже" : "не открыто";
}

const chartQuickSwitchCodes = vargaSnapshotCodes;
const primaryVargaTabCodes = ["D1", "D9", "D10", "D12", "D30", "D60"] as const;
const secondaryVargaQuickCodes = ["D2", "D3", "D4", "D7", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"] as const;
const practitionerVargaCodes = ["D1", "D9", "D10", "D7", "D12", "D20", "D24", "D30", "D60"] as const;

function VargaAtlasBoard({
  chart,
  activeCode,
  chartStyle,
  chartReference,
  onSelect,
}: {
  chart: BirthChart | null;
  activeCode: string;
  chartStyle: "north" | "south";
  chartReference: ChartReference;
  onSelect: (code: string) => void;
}) {
  const [atlasFilter, setAtlasFilter] = useState<"all" | "готово" | "ожидает" | "jaimini">("готово");
  const items = vargaSnapshotCodes.map((code) => {
    if (code === "D1") {
      return { code, name: "Раши", available: Boolean(chart), varga: null, status: chart ? "рассчитана" : "не открыто", previewStatus: "после построения" };
    }
    const varga = chart?.vargas?.[code];
    const available = Boolean(varga);
    return {
      code,
      name: varga?.name ?? "Варга",
      available,
      varga: varga ?? null,
      status: available ? "рассчитана" : unavailableVargaLabel(code),
      previewStatus: jaiminiVargaCodeSet.has(code) ? "после проверки" : "после построения",
    };
  });
  const coverage = vargaCoverage(chart);
  const filteredItems = items.filter((item) => {
    if (item.code === activeCode) return false;
    if (atlasFilter === "готово") return item.available;
    if (atlasFilter === "ожидает") return !item.available && !jaiminiVargaCodeSet.has(item.code);
    if (atlasFilter === "jaimini") return jaiminiVargaCodeSet.has(item.code);
    return true;
  });
  const atlasFilters = [
    { key: "all", label: "Все", count: items.length },
    { key: "готово", label: "Готовые", count: coverage.ready.length },
    { key: "ожидает", label: "Ожидают", count: coverage.missing.length - coverage.pendingJaimini.length },
    { key: "jaimini", label: "Джаимини", count: coverage.pendingJaimini.length },
  ] as const;

  return (
    <div className="varga-atlas-board" aria-label="Атлас D-карт">
      <div className="varga-atlas-head">
        <div>
          <strong>Другие D-карты</strong>
        </div>
      </div>
      <div className="varga-atlas-filter" aria-label="Фильтр атласа D-карт">
        {atlasFilters.map((filter) => (
          <button
            type="button"
            className={atlasFilter === filter.key ? "active" : ""}
            key={filter.key}
            onClick={() => setAtlasFilter(filter.key)}
          >
            <span>{filter.label}</span>
            <strong>{filter.count}</strong>
          </button>
        ))}
      </div>
      <div className="varga-atlas-grid">
        {filteredItems.length ? (
          filteredItems.map((item) => (
            <button
              type="button"
              className={`varga-atlas-card${activeCode === item.code ? " active" : ""}${item.available ? " ready" : ""}${jaiminiVargaCodeSet.has(item.code) ? " jaimini" : ""}`}
              disabled={!item.available}
              key={item.code}
              onClick={() => onSelect(item.code)}
            >
              <div className="varga-atlas-title">
                <div>
                  <strong>{item.code}</strong>
                  <em>{item.status}</em>
                </div>
                <span>{vargaPurposeLabels[item.code] ?? item.name}</span>
              </div>
              <div className="varga-atlas-preview">
                {item.available ? (
                  chartStyle === "south" ? (
                    <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact />
                  ) : (
                    <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact />
                  )
                ) : (
                  <div className="varga-atlas-placeholder">
                    {chartStyle === "south" ? (
                      <SouthIndianChartGrid chart={null} varga={null} chartReference={chartReference} compact />
                    ) : (
                      <NorthIndianChartSvg chart={null} varga={null} chartReference={chartReference} compact />
                    )}
                    <em>{item.previewStatus}</em>
                  </div>
                )}
              </div>
            </button>
          ))
        ) : (
          <div className="varga-atlas-empty">
            <strong>Других D-карт в этом фильтре нет</strong>
            <button type="button" onClick={() => setAtlasFilter("all")}>Показать все</button>
          </div>
        )}
      </div>
    </div>
  );
}

function BirthCompactStrip({
  birthDate,
  birthTime,
  placeName,
  selectedPlace,
  chart,
  currentChartDefault,
  collapsed,
  onToggle,
  onUseCurrent,
}: {
  birthDate: string;
  birthTime: string;
  placeName: string;
  selectedPlace: PlaceCandidate | null;
  chart: BirthChart | null;
  currentChartDefault: boolean;
  collapsed: boolean;
  onToggle: () => void;
  onUseCurrent: () => void;
}) {
  const placeLabel = selectedPlace?.label ?? chart?.place.label ?? chart?.place.name ?? placeName;
  const utcLabel = chart?.birth.utc_offset ?? selectedPlace?.timezone ?? "ожидает";

  return (
    <div className="birth-compact-strip">
      <div>
        <span>{currentChartDefault ? "Карта на сейчас" : "Карта рождения"}</span>
        <strong>
          {birthDate} · {birthTime} · {placeLabel}
        </strong>
      </div>
      <div>
        <span>Часовой пояс</span>
        <strong>{utcLabel}</strong>
      </div>
      <button
        type="button"
        className="secondary-button current-chart-button"
        onPointerDown={(event) => {
          event.stopPropagation();
          onUseCurrent();
        }}
        onClick={(event) => event.stopPropagation()}
      >
        Сейчас
      </button>
      <button type="button" className="secondary-button" onClick={onToggle}>
        {collapsed ? "✎" : "Свернуть"}
      </button>
    </div>
  );
}

function northGrahaLabel(body: string) {
  return northGrahaLabels[body] ?? northGrahaLabels[body.trim()] ?? body.slice(0, 2);
}

function grahaSymbol(body: string) {
  return grahaSymbols[body] ?? grahaSymbols[body.trim()] ?? body.slice(0, 2);
}

function formatDegrees(value: number) {
  return `${value.toFixed(4)}°`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function formatIsoTime(value: string | null | undefined) {
  if (!value) return "";
  const match = value.match(/T(\d{2}:\d{2})/);
  return match?.[1] ?? value;
}

function formatPeriodRange(period: DayPeriod) {
  return `${period.name} ${formatIsoTime(period.starts_at)}-${formatIsoTime(period.ends_at)}`;
}

const READER_EXPLANATION_EVENT = "jyotish:reader-explanation";

type ReaderExplanationDetail = {
  title: string;
  text: string;
  context?: string;
};

function publishReaderExplanation(detail: ReaderExplanationDetail) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<ReaderExplanationDetail>(READER_EXPLANATION_EVENT, { detail }));
}

function readerExplanationForPlacement({
  chart,
  varga,
  placement,
  house,
  termLanguage,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  placement: ChartPlacement;
  house: number | null;
  termLanguage: TermLanguage;
}): ReaderExplanationDetail {
  const label = placement.isLagna ? grahaTermLabel("Lagna", termLanguage) : grahaTermLabel(placement.body, termLanguage);
  const rashiLabel = rashiTermFromName(placement.rashi, termLanguage);
  const houseText = house ? `${house} дом` : "дом не определён";
  if (placement.isLagna && chart) {
    return {
      title: `${label}: ${rashiLabel}`,
      context: "Карта",
      text: readerExplanationForHouse({ chart, varga, chartReference: "lagna", house: house ?? 1, termLanguage }).text,
    };
  }
  const natalGraha = chart?.grahas.find((graha) => canonicalBody(graha.body) === canonicalBody(placement.body));
  if (!varga && chart && natalGraha) {
    return {
      title: `${label}: ${rashiLabel}${house ? `, ${house} дом` : ""}`,
      context: "Карта D1",
      text: placementExplanationText({ graha: natalGraha, chart, house, termLanguage }),
    };
  }
  const nakshatra = placement.nakshatra ? `${placement.nakshatra}${placement.pada ? `, пада ${placement.pada}` : ""}` : "накшатра не указана";
  const dignity = dignityText(placement.dignity);
  const retrograde = placement.retrograde ? " Ретроградность усиливает возврат к теме и требует повторной проверки результата." : "";
  return {
    title: `${label}: ${rashiLabel}${house ? `, ${house} дом` : ""}`,
    context: varga ? `${varga.name ?? "D-карта"}` : "Карта",
    text: [
      `${label} расположен в ${rashiLabel}, ${houseText}. Накшатра: ${nakshatra}. ${dignity ? `Состояние: ${dignity}.` : ""}`.trim(),
      "В D-карте это уточняет плод, обещанный D1: природа грахи и её D1-управления остаются корнем, знак и диспозитор показывают канал, а дом варги показывает область проявления.",
      retrograde.trim(),
    ].filter(Boolean).join("\n\n"),
  };
}

function GlossaryTerm({ termKey, children }: { termKey: GlossaryKey; children: ReactNode }) {
  const item = jyotishGlossary[termKey];

  return (
    <span className="glossary-wrap">
      <button
        type="button"
        className="glossary-trigger"
        onClick={(event) => {
          event.stopPropagation();
          publishReaderExplanation({ title: item.label, text: item.text, context: "Справочник терминов" });
        }}
      >
        {children}
      </button>
    </span>
  );
}

function CalculationValueHelp({
  title,
  text,
  context = "Расчёт карты",
  children,
}: {
  title: string;
  text: string;
  context?: string;
  children: ReactNode;
}) {
  return (
    <span className="glossary-wrap calculation-value-help">
      <button
        type="button"
        className="glossary-trigger"
        onClick={(event) => {
          event.stopPropagation();
          publishReaderExplanation({ title, text, context });
        }}
      >
        {children}
      </button>
    </span>
  );
}

function isoDateOffset(days: number) {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function grahaDignity(graha: GrahaPosition) {
  const rashiIndex = normalizeRashiIndex(graha.rashi_index) ?? rashiIndexFromName(graha.rashi);
  return dignityForPlacement(graha.body, rashiIndex, graha.dignity);
}

function dignityText(dignity: GrahaDignity | null | undefined) {
  if (dignity === "exaltation") return "экзальтация";
  if (dignity === "debilitation") return "дебилитация";
  if (dignity === "moolatrikona") return "мулатрикона";
  return null;
}

const grahaShastraMeanings: Record<string, { nature: string; strong: string; caution: string }> = {
  Surya: {
    nature: "Сурья показывает атму, власть, отца, честь, способность вести и принимать ответственность.",
    strong: "В сильном положении даёт ясность цели, признание, самостоятельность и поддержку от старших или власти.",
    caution: "При слабости или поражении может давать гордость, сухость, конфликт с авторитетами и перегрев темы дома.",
  },
  Chandra: {
    nature: "Чандра показывает ум, мать, питание, общественную связь, восприимчивость и ежедневный ритм.",
    strong: "Сильная Луна поддерживает популярность, мягкость, заботу, память и устойчивую психику.",
    caution: "При слабости или поражении даёт переменчивость, тревожность и зависимость результата от настроения.",
  },
  Mangala: {
    nature: "Мангала показывает силу, мужество, спор, защиту, братьев, землю, технику и способность действовать.",
    strong: "Сильный Марс даёт решительность, победу в борьбе, инженерность, дисциплину и защиту своих интересов.",
    caution: "При поражении может давать резкость, травмы, конфликты, поспешность и разрушение темы дома.",
  },
  Budha: {
    nature: "Будха показывает разум, речь, счёт, обучение, торговлю, письма, анализ и способность адаптироваться.",
    strong: "Сильный Меркурий даёт ясную речь, гибкий интеллект, коммерческий навык и точность в деталях.",
    caution: "При слабости или поражении даёт нервозность, хитрость, сомнения и рассеивание внимания.",
  },
  Guru: {
    nature: "Гуру показывает дхарму, знание, наставников, детей, благословение, расширение и защиту.",
    strong: "Сильный Юпитер даёт мудрость, поддержку учителей, благочестие, рост и способность видеть смысл.",
    caution: "При слабости может давать чрезмерную доверчивость, догматизм или потерю правильного совета.",
  },
  Shukra: {
    nature: "Шукра показывает любовь, брак, комфорт, красоту, наслаждение, искусство, семя и способность к союзу.",
    strong: "Сильная Венера даёт привлекательность, гармонию, вкус, договороспособность и материальный комфорт.",
    caution: "При поражении может давать привязанность к удовольствиям, слабость в отношениях и растрату.",
  },
  Shani: {
    nature: "Шани показывает время, труд, ограничения, служение, старших, бедных, выносливость и карму задержек.",
    strong: "Сильный Сатурн даёт терпение, устойчивость, практичность, способность выдерживать долгий путь.",
    caution: "При слабости или поражении даёт страх, холодность, задержки, тяжесть и чувство нехватки.",
  },
  Rahu: {
    nature: "Раху показывает необычное, иностранное, усиление желаний, нарушение привычных границ и материальную одержимость. Раху не владеет домами как классические грахи; его плод читается через занятый дом, знак, диспозитора, накшатра-управителя, соединения и аспекты.",
    strong: "В конструктивном положении даёт нестандартный прорыв, работу с массами, техникой, чужими культурами.",
    caution: "При поражении даёт иллюзию, зависимость, чрезмерную амбицию и искажение темы дома.",
  },
  Ketu: {
    nature: "Кету показывает отсечение, мокшу, прошлый опыт, скрытую проницательность, аскезу и внутреннее отстранение. Кету не владеет домами как классические грахи; его плод читается через занятый дом, знак, диспозитора, накшатра-управителя, соединения и аспекты.",
    strong: "В конструктивном положении даёт интуицию, духовную проницательность, способность отсечь лишнее.",
    caution: "При поражении даёт разрыв, безразличие, внезапные потери или неполное проживание темы дома.",
  },
};

const houseShastraMeanings: Record<number, { theme: string; result: string; caution: string }> = {
  1: { theme: "1 дом — лагна: тело, характер, жизненная сила, направление судьбы.", result: "Граха здесь прямо окрашивает личность и способ действовать.", caution: "Поражения здесь отражаются на здоровье, уверенности и общем тоне жизни." },
  2: { theme: "2 дом — речь, семья, накопления, питание, ценности и поддерживающая среда.", result: "Граха показывает, как человек говорит, хранит ресурс и опирается на род.", caution: "Поражения дают резкость речи, траты или напряжение в семье." },
  3: { theme: "3 дом — усилие, смелость, навыки, руки, младшие родственники и личная инициатива.", result: "Граха здесь раскрывается через собственное действие и практику.", caution: "Поражения дают споры, суету или неверное применение силы." },
  4: { theme: "4 дом — мать, сердце, дом, недвижимость, внутренняя опора, образование и счастье.", result: "Граха показывает качество покоя, дома и эмоциональной основы.", caution: "Поражения тревожат сердце, жильё, мать или чувство защищённости." },
  5: { theme: "5 дом — интеллект, мантра, дети, пурва-пунья, творчество и способность давать совет.", result: "Граха здесь показывает плод прошлой заслуги и качество разумного выбора.", caution: "Поражения дают ошибки в суждении, тревоги за детей или нестабильность обучения." },
  6: { theme: "6 дом — болезни, долги, враги, служение, конкуренция и преодоление.", result: "Граха здесь показывает, чем человек борется и как побеждает препятствия.", caution: "Поражения усиливают конфликты, хронические темы и долговую нагрузку." },
  7: { theme: "7 дом — брак, партнёрство, договоры, публика и открытые отношения.", result: "Граха здесь показывает стиль союза и то, что человек встречает через других.", caution: "Поражения дают напряжение в браке, договорах и публичном взаимодействии." },
  8: { theme: "8 дом — долголетие, тайны, кризисы, наследство, трансформация и скрытая карма.", result: "Граха здесь действует глубоко, через переломы, исследование и невидимые процессы.", caution: "Поражения дают резкие перемены, страх, потери или скрытые болезни." },
  9: { theme: "9 дом — дхарма, отец, гуру, удача, паломничества, шастры и благословение.", result: "Граха здесь показывает веру, высший смысл и поддержку судьбы.", caution: "Поражения дают конфликт с учителями, отцом, традицией или законом." },
  10: { theme: "10 дом — карма, профессия, статус, власть, действие в мире и видимый результат.", result: "Граха здесь становится публичной: её природа проявляется в работе, репутации и обязанностях.", caution: "Поражения дают давление статуса, ошибки перед начальством или потерю направления в деле." },
  11: { theme: "11 дом — доходы, друзья, сети, старшие родственники, исполнение желаний и рост результатов.", result: "Граха здесь показывает, через что приходят плоды и поддержка сообщества.", caution: "Поражения дают жадность, неправильные связи или нестабильные доходы." },
  12: { theme: "12 дом — расходы, сон, уединение, дальние места, освобождение, потери и скрытая жизнь.", result: "Граха здесь уводит свою тему внутрь, за границу, в служение, аскезу или расходы.", caution: "Поражения дают утечки, изоляцию, тайные привязанности и неосознанные потери." },
};

function grahaStatusText(graha: GrahaPosition) {
  const dignity = dignityText(grahaDignity(graha));
  const parts = [...(isRetrogradeGraha(graha) ? ["ретроградная"] : []), ...(dignity ? [dignity] : [])];
  return parts.length ? parts.join(", ") : "-";
}

function topShadbalaRows(chart: BirthChart | null) {
  const rows = [...(chart?.classical?.shadbala?.items ?? [])].sort((left, right) => right.known_total - left.known_total);
  return {
    strongest: rows[0] ?? null,
    weakest: rows.at(-1) ?? null,
  };
}

function combustGrahaLabels(chart: BirthChart | null) {
  const sun = chart?.grahas.find((graha) => graha.body === "Surya");
  return (
    chart?.grahas
      .map((graha) => ({ graha, status: combustionStatus(graha, sun) }))
      .filter((item) => item.status.combust)
      .map((item) => grahaTermLabel(item.graha.body, "sanskrit", "short")) ?? []
  );
}

function currentDashaLabel(chart: BirthChart | null) {
  const today = new Date().toISOString().slice(0, 10);
  const period = chart?.dashas?.vimshottari?.mahadashas?.find((item) => item.starts_at <= today && item.ends_at >= today);
  return period?.lord ? labelRu(period.lord) : "-";
}

function AstrologerPrioritySummary({ chart, termLanguage }: { chart: BirthChart | null; termLanguage: TermLanguage }) {
  const moon = chart?.grahas.find((graha) => graha.body === "Chandra");
  const sun = chart?.grahas.find((graha) => graha.body === "Surya");
  const { strongest, weakest } = topShadbalaRows(chart);
  const combust = combustGrahaLabels(chart);
  const items = [
    {
      key: "lagna",
      label: <GlossaryTerm termKey="lagna">Лагна</GlossaryTerm>,
      value: chart?.ascendant ? `${rashiTermFromName(chart.ascendant.rashi, termLanguage)} ${formatSignDegrees(chart.ascendant.longitude)}` : "-",
      note: chart?.ascendant ? `${chart.ascendant.nakshatra} ${chart.ascendant.pada}` : "после расчёта",
    },
    {
      key: "moon",
      label: <GlossaryTerm termKey="chandra_lagna">Луна</GlossaryTerm>,
      value: moon ? `${rashiTermFromName(moon.rashi, termLanguage)} ${formatSignDegrees(moon.longitude)}` : "-",
      note: moon ? `${moon.nakshatra} ${moon.pada}` : "ум, даши, тара",
    },
    {
      key: "sun",
      label: <GlossaryTerm termKey="surya_lagna">Солнце</GlossaryTerm>,
      value: sun ? `${rashiTermFromName(sun.rashi, termLanguage)} ${formatSignDegrees(sun.longitude)}` : "-",
      note: "атма, воля, отец, власть",
    },
    {
      key: "d9-lagna",
      label: <GlossaryTerm termKey="navamsa">D9 лагны</GlossaryTerm>,
      value: chart?.ascendant?.navamsa ? rashiTermFromName(chart.ascendant.navamsa, termLanguage) : "-",
      note: "тонкая сила положения",
    },
    {
      key: "dasha",
      label: <GlossaryTerm termKey="dasha">Текущая даша</GlossaryTerm>,
      value: currentDashaLabel(chart),
      note: "первый слой времени",
    },
    {
      key: "combustion",
      label: <GlossaryTerm termKey="combustion">Сожжение</GlossaryTerm>,
      value: combust.length ? combust.join(", ") : "нет",
      note: "аста по близости к Солнцу",
    },
    {
      key: "shadbala-strong",
      label: <GlossaryTerm termKey="shadbala">Шадбала max</GlossaryTerm>,
      value: strongest ? `${grahaTermLabel(strongest.body, termLanguage, "short")} ${strongest.known_total.toFixed(1)}` : "-",
      note: "вирупы",
    },
    {
      key: "shadbala-weak",
      label: <GlossaryTerm termKey="shadbala">Шадбала min</GlossaryTerm>,
      value: weakest ? `${grahaTermLabel(weakest.body, termLanguage, "short")} ${weakest.known_total.toFixed(1)}` : "-",
      note: "слабое место",
    },
  ];

  return (
    <div className="astrologer-priority-summary" aria-label="Приоритетная сводка для чтения карты">
      {items.map((item) => (
        <div key={item.key}>
          <span>{item.label}</span>
          <strong>{item.value}</strong>
          <small>{item.note}</small>
        </div>
      ))}
    </div>
  );
}

function PanchangaDigest({ chart }: { chart: BirthChart | null }) {
  const panchanga = chart?.panchanga;
  const items = [
    {
      key: "tithi",
      label: <GlossaryTerm termKey="tithi">Титхи</GlossaryTerm>,
      value: panchanga?.tithi ? `${panchanga.tithi.paksha} ${panchanga.tithi.name}` : "-",
    },
    {
      key: "vara",
      label: <GlossaryTerm termKey="vara">Вара</GlossaryTerm>,
      value: panchanga?.vara?.name ?? "-",
    },
    {
      key: "nakshatra",
      label: <GlossaryTerm termKey="nakshatra">Накшатра</GlossaryTerm>,
      value: panchanga?.nakshatra ? `${panchanga.nakshatra.name}${panchanga.nakshatra.pada ? ` ${panchanga.nakshatra.pada}` : ""}` : "-",
    },
    {
      key: "yoga",
      label: <GlossaryTerm termKey="panchanga_yoga">Йога</GlossaryTerm>,
      value: panchanga?.yoga?.name ?? "-",
    },
    {
      key: "karana",
      label: <GlossaryTerm termKey="karana">Карана</GlossaryTerm>,
      value: panchanga?.karana?.name ?? "-",
    },
  ];

  return (
    <div className="panchanga-digest" aria-label="Панчанга для D1">
      <strong><GlossaryTerm termKey="panchanga">Панчанга</GlossaryTerm></strong>
      <div>
        {items.map((item) => (
          <span key={item.key}>
            <em>{item.label}</em>
            <b>{item.value}</b>
          </span>
        ))}
      </div>
    </div>
  );
}

function RashiValue({
  name,
  index,
  termLanguage,
  compact = false,
}: {
  name: string | null | undefined;
  index?: number | null;
  termLanguage: TermLanguage;
  compact?: boolean;
}) {
  return (
    <GlossaryTerm termKey={rashiGlossaryKey(normalizeRashiIndex(index), name)}>
      {rashiTermLabel(normalizeRashiIndex(index), name, termLanguage, compact)}
    </GlossaryTerm>
  );
}

function PlacementRashiValue({
  graha,
  chart,
  house,
  termLanguage,
  compact = false,
}: {
  graha: GrahaPosition;
  chart: BirthChart;
  house: number | null;
  termLanguage: TermLanguage;
  compact?: boolean;
}) {
  const label = grahaTermLabel(graha.body, termLanguage);
  const rashiLabel = rashiTermFromName(graha.rashi, termLanguage);
  return (
    <CalculationValueHelp
      title={`${label} в ${rashiLabel}`}
      text={placementExplanationText({ graha, chart, house, termLanguage })}
      context="Таблица D1"
    >
      {rashiTermLabel(normalizeRashiIndex(graha.rashi_index), graha.rashi, termLanguage, compact)}
    </CalculationValueHelp>
  );
}

function NavamsaValue({
  graha,
  chart,
  termLanguage,
  compact = false,
}: {
  graha: GrahaPosition;
  chart: BirthChart;
  termLanguage: TermLanguage;
  compact?: boolean;
}) {
  const label = grahaTermLabel(graha.body, termLanguage);
  const d9 = rashiTermFromName(graha.navamsa, termLanguage);
  return (
    <CalculationValueHelp
      title={`D9: ${label} в ${d9}`}
      context="Таблица D1"
      text={[
        `${label} в D9 попадает в ${d9}. Навамша уточняет внутреннюю силу положения, дхарму грахи и зрелость результата, особенно для брака, обещаний D1 и устойчивости достоинства.`,
        "D9 не отменяет D1: сначала читается раши-карта, затем навамша показывает тонкий слой и способность положения удержать результат.",
        placementExplanationText({ graha, chart, house: houseFromRashiIndex(normalizeRashiIndex(graha.rashi_index) ?? rashiIndexFromName(graha.rashi), normalizeRashiIndex(chart.ascendant?.rashi_index) ?? rashiIndexFromName(chart.ascendant?.rashi)), termLanguage }).split("\n\n")[0],
      ].filter(Boolean).join("\n\n")}
    >
      {rashiTermLabel(normalizeRashiIndex(graha.navamsa_index), graha.navamsa, termLanguage, compact)}
    </CalculationValueHelp>
  );
}

function NakshatraValue({ name, pada, subject }: { name: string | null | undefined; pada?: number | null; subject?: string }) {
  if (!name) return <>-</>;
  const title = subject ? `${name} ${pada ? pada : ""}: ${subject}`.trim() : `${name}${pada ? ` ${pada}` : ""}`;
  const text = subject
    ? `${subject} находится в накшатре ${name}${pada ? `, пада ${pada}` : ""}. Накшатра уточняет психологический и событийный слой положения.`
    : `Накшатра ${name}${pada ? `, пада ${pada}` : ""}. Пада уточняет навамшу и делает положение точнее.`;
  return (
    <CalculationValueHelp title={title} text={text}>
      {name}
      {pada ? ` ${pada}` : ""}
    </CalculationValueHelp>
  );
}

const vimshottariNakshatraLords = ["Ketu", "Shukra", "Surya", "Chandra", "Mangala", "Rahu", "Guru", "Shani", "Budha"] as const;

function nakshatraLordByIndex(index: number | null | undefined) {
  if (index === null || index === undefined || !Number.isFinite(index)) return null;
  const normalized = Math.trunc(index);
  if (normalized < 0 || normalized > 26) return null;
  return vimshottariNakshatraLords[normalized % vimshottariNakshatraLords.length] ?? null;
}

function NakshatraLordValue({
  index,
  name,
  subject,
  termLanguage,
}: {
  index: number | null | undefined;
  name: string | null | undefined;
  subject: string;
  termLanguage: TermLanguage;
}) {
  const lord = nakshatraLordByIndex(index);
  if (!lord) return <>-</>;
  const lordLabel = grahaTermLabel(lord, termLanguage);
  return (
    <CalculationValueHelp
      title={`Управитель накшатры: ${subject}`}
      text={`${subject}: накшатра ${name || "-"} управляется грахой ${lordLabel}. Этот управитель связывает положение с дашами и тонким способом проявления результата.`}
    >
      {lordLabel}
    </CalculationValueHelp>
  );
}

function grahaStatusExplanationText(graha: GrahaPosition, house: number | null, termLanguage: TermLanguage) {
  const label = grahaTermLabel(graha.body, termLanguage);
  const dignity = grahaDignity(graha);
  const retrograde = isRetrogradeGraha(graha);
  const houseText = house ? `${house} дом` : "дом не определён";
  const dignityLine = dignity
    ? dignity === "exaltation"
      ? `${label} в экзальтации: граха получает сильную способность проявить свою каракатву, но результат всё равно зависит от дома, управлений и поражений.`
      : dignity === "debilitation"
        ? `${label} в дебилитации: плод приходит через напряжение, компенсацию, обучение и поддержку диспозитора.`
        : `${label} в мулатриконе: положение даёт естественную, устойчивую силу грахи.`
    : `${label}: особого статуса экзальтации, дебилитации или мулатриконы здесь не видно.`;
  const retroLine = retrograde
    ? "Ретроградность делает тему более внутренней и повторяющейся: результат часто приходит через возврат, пересмотр и старые незавершённые задачи."
    : "";
  return [
    `${label}, ${houseText}. Статус читается не отдельно, а вместе с бхавой, знаком, диспозитором, управляемыми домами и дашей.`,
    dignityLine,
    retroLine,
  ].filter(Boolean).join("\n\n");
}

function GrahaStatusValue({
  graha,
  house = null,
  termLanguage = "sanskrit",
}: {
  graha: GrahaPosition;
  house?: number | null;
  termLanguage?: TermLanguage;
}) {
  const dignity = grahaDignity(graha);
  const retrograde = isRetrogradeGraha(graha);
  if (!retrograde && !dignity) return <>-</>;
  const label = grahaTermLabel(graha.body, termLanguage);
  const statusLabel = [retrograde ? "ретроградная" : "", dignity ? dignityText(dignity) : ""].filter(Boolean).join(", ");
  return (
    <CalculationValueHelp
      title={`Статус: ${label}`}
      text={grahaStatusExplanationText(graha, house, termLanguage)}
      context="Таблица D1"
    >
      {statusLabel}
    </CalculationValueHelp>
  );
}

function placementExplanationText({
  graha,
  chart,
  house,
  termLanguage,
}: {
  graha: GrahaPosition;
  chart: BirthChart;
  house: number | null;
  termLanguage: TermLanguage;
}) {
  const label = grahaTermLabel(graha.body, termLanguage);
  const rashiIndex = normalizeRashiIndex(graha.rashi_index) ?? rashiIndexFromName(graha.rashi);
  const rashiLabel = rashiTermFromName(graha.rashi, termLanguage);
  const houseText = house ? `${house} дом` : "дом не определён";
  const lagnaIndex = normalizeRashiIndex(chart.ascendant?.rashi_index) ?? rashiIndexFromName(chart.ascendant?.rashi);
  const ruledHouseList = ruledHousesForGraha(graha.body, lagnaIndex);
  const ruledHouses = HouseGlossaryListText(ruledHouseList);
  const nakshatra = graha.nakshatra ? `${graha.nakshatra}${graha.pada ? `, пада ${graha.pada}` : ""}` : "накшатра не определена";
  const dignityKind = grahaDignity(graha);
  const dignity = dignityText(dignityKind);
  const status = [isRetrogradeGraha(graha) ? "ретроградная" : "", dignity].filter(Boolean).join(", ") || "без особого статуса";
  const shadbala = shadbalaValueForGraha(chart, graha.body);
  const rashiLord = rashiIndex === null ? null : rashiLordBodies[rashiIndex];
  const rashiLordGraha = rashiLord ? chart.grahas.find((item) => canonicalBody(item.body) === canonicalBody(rashiLord)) : null;
  const rashiLordHouse = rashiLordGraha
    ? houseFromRashiIndex(normalizeRashiIndex(rashiLordGraha.rashi_index) ?? rashiIndexFromName(rashiLordGraha.rashi), lagnaIndex)
    : null;
  const grahaMeaning = grahaShastraMeanings[canonicalBody(graha.body)];
  const houseMeaning = house ? houseShastraMeanings[house] : null;
  const shadbalaRow = shadbalaRowForGraha(chart, graha.body);
  const strengthLine = shadbalaRow
    ? `Шадбала ${shadbala}: сила показывает способность грахи реализовать свою каракатву и управляемые дома. Сильная вредоносная или поражённая граха может сильнее дать трудный плод, а не просто “лучше”.`
    : "Шадбала пока не найдена, поэтому силу положения нельзя читать отдельно от знака, дома и управителя.";
  const dignityLine = dignity
    ? `Состояние: ${status}. ${dignityKind === "exaltation" ? "Экзальтация усиливает способность грахи давать свой чистый плод." : dignityKind === "debilitation" ? "Дебилитация показывает, что плод приходит с напряжением, компенсацией или зависимостью от поддержки." : "Мулатрикона даёт естественную, устойчивую силу грахи."}`
    : `Состояние: ${status}. Особых знаков экзальтации, дебилитации или мулатриконы здесь не видно.`;
  const retroLine = isRetrogradeGraha(graha)
    ? "Ретроградность делает тему более внутренней и повторяющейся: результат часто приходит через возврат, пересмотр и незавершённые кармические задачи."
    : "";
  const lordLine = rashiLord
    ? `Хозяин знака: ${grahaTermLabel(rashiLord, termLanguage)}${rashiLordHouse ? `, расположен в ${rashiLordHouse} доме` : ""}. В шастрическом чтении диспозитор показывает канал, через который положение реально отдаёт результат.`
    : "Хозяин знака не определён.";
  const lordshipLine = ruledHouseList.length
    ? `${label} управляет домами ${ruledHouses}; поэтому темы этих домов переносятся в ${houseText}.`
    : `${label} не владеет домами напрямую; результат идёт через занятый дом, диспозитора ${rashiLord ? grahaTermLabel(rashiLord, termLanguage) : ""}, накшатра-управителя, соединения и аспекты.`;

  return [
    `${label} несёт свою каракатву в ${houseText}; знак задаёт форму, диспозитор — канал отдачи результата, управляемые дома — источник тем, накшатра — тон проявления, сила — степень способности дать плод.`,
    `${label} в ${houseText}${rashiLabel ? `, знак ${rashiLabel}` : ""}. ${grahaMeaning?.nature ?? "Граха показывает свою естественную каракатву."} ${houseMeaning?.theme ?? ""}`,
    `${houseMeaning?.result ?? "Результат читается по связи грахи с домом."} ${lordshipLine}`,
    lordLine,
    `Накшатра: ${nakshatra}. Накшатра уточняет способ проявления: мотивацию, тон действия и более тонкий слой результата.`,
    `${dignityLine} ${strengthLine} ${grahaMeaning?.strong ?? ""}`,
    `${houseMeaning?.caution ?? ""} ${grahaMeaning?.caution ?? ""} ${retroLine}`.trim(),
  ].filter(Boolean).join("\n\n");
}

function HouseGlossaryListText(houses: number[]) {
  return houses.length ? houses.join(", ") : "";
}

function PlacementNameHelp({
  graha,
  chart,
  house,
  termLanguage,
}: {
  graha: GrahaPosition;
  chart: BirthChart;
  house: number | null;
  termLanguage: TermLanguage;
}) {
  const label = grahaTermLabel(graha.body, termLanguage);
  const rashiLabel = rashiTermFromName(graha.rashi, termLanguage);
  const title = `${label}: ${rashiLabel}${house ? `, ${house} дом` : ""}`;
  return (
    <CalculationValueHelp title={title} text={placementExplanationText({ graha, chart, house, termLanguage })}>
      {label}
    </CalculationValueHelp>
  );
}

function HouseValueHelp({
  chart,
  house,
  termLanguage,
}: {
  chart: BirthChart | null;
  house: number | null;
  termLanguage: TermLanguage;
}) {
  if (!house) return <>-</>;
  const explanation = readerExplanationForHouse({ chart, varga: null, chartReference: "lagna", house, termLanguage });
  return (
    <CalculationValueHelp title={explanation.title} text={explanation.text}>
      {house}
    </CalculationValueHelp>
  );
}

function RuledHousesValue({
  graha,
  houses,
  chart,
  currentHouse,
  termLanguage,
}: {
  graha: GrahaPosition;
  houses: readonly number[];
  chart: BirthChart;
  currentHouse: number | null;
  termLanguage: TermLanguage;
}) {
  if (!houses.length) return <>-</>;
  const label = grahaTermLabel(graha.body, termLanguage);
  const houseLabels = houses.join(", ");
  const currentHouseText = currentHouse ? `${currentHouse} дом` : "текущий дом";
  const houseDetails = houses
    .map((house) => readerExplanationForHouse({ chart, varga: null, chartReference: "lagna", house, termLanguage }).text.split("\n\n")[0])
    .join("\n\n");
  return (
    <CalculationValueHelp
      title={`Управления: ${label}`}
      context="Таблица D1"
      text={[
        `${label} управляет домами ${houseLabels}. Поэтому в положении ${label} темы этих домов переносятся в ${currentHouseText}.`,
        "В классическом чтении это один из главных слоёв: граха показывает не только свою каракатву, но и приносит в дом темы домов, которыми владеет.",
        houseDetails,
      ].filter(Boolean).join("\n\n")}
    >
      {houseLabels}
    </CalculationValueHelp>
  );
}

function shadbalaRowForGraha(chart: BirthChart, body: string) {
  return chart.classical?.shadbala?.items?.find((item) => canonicalBody(item.body) === canonicalBody(body));
}

function shadbalaValueForGraha(chart: BirthChart, body: string) {
  const row = shadbalaRowForGraha(chart, body);
  if (!row) return "-";
  return `${row.known_total.toFixed(1)}`;
}

function LongitudeValue({ label, longitude }: { label: string; longitude: number }) {
  const signDegrees = formatSignDegrees(longitude);
  const absoluteDegrees = formatDegrees(longitude);
  return (
    <CalculationValueHelp
      title={`Долгота: ${label}`}
      text={`${label}: ${signDegrees} внутри знака, ${absoluteDegrees} абсолютной сидерической долготы. По этому числу считаются знак, накшатра, пада, D9 и остальные варги.`}
    >
      {signDegrees}
    </CalculationValueHelp>
  );
}

function ShadbalaValue({ chart, body, label }: { chart: BirthChart; body: string; label: string }) {
  const row = shadbalaRowForGraha(chart, body);
  const value = row ? `${row.known_total.toFixed(1)}` : "-";
  const detail = row
    ? `Шадбала ${label}: ${value} вируп. Это не “хорошо/плохо” само по себе: сила показывает способность грахи реализовать свою каракатву и управляемые дома. Сильная поражённая или вредоносная граха может сильнее дать трудный плод. Компоненты: Sthana ${row.components.sthana ?? 0}, Dig ${row.components.dig}, Kala ${row.components.kala ?? 0}, Chesta ${row.components.chesta ?? 0}, Naisargika ${row.components.naisargika}, Drik ${row.components.drik ?? 0}.`
    : `Для ${label} шадбала в текущем расчёте ещё не найдена.`;
  return (
    <CalculationValueHelp title={`Шадбала: ${label}`} text={detail} context="Таблица D1">
      {value}
    </CalculationValueHelp>
  );
}

function GrahaTable({ chart, termLanguage }: { chart: BirthChart | null; termLanguage: TermLanguage }) {
  const grahas = chart?.grahas ?? [];
  const sun = grahas.find((graha) => graha.body === "Surya");
  const lagnaIndex = normalizeRashiIndex(chart?.ascendant?.rashi_index) ?? rashiIndexFromName(chart?.ascendant?.rashi);
  if (!chart || grahas.length === 0) {
    return (
      <div className="readiness-panel">
        <strong>Грахи ещё не рассчитаны</strong>
        <p>Карта заполнится после расчёта эфемеридных положений.</p>
      </div>
    );
  }

  return (
    <div className="planet-table graha-table">
      <div className="table-row table-head">
        <span><GlossaryTerm termKey="graha">Граха</GlossaryTerm></span>
        <span><GlossaryTerm termKey="longitude">Долгота</GlossaryTerm></span>
        <span><GlossaryTerm termKey="rashi">Раши</GlossaryTerm></span>
        <span><GlossaryTerm termKey="house">Дом</GlossaryTerm></span>
        <span><GlossaryTerm termKey="ruled_houses">Упр.</GlossaryTerm></span>
        <span><GlossaryTerm termKey="nakshatra">Накшатра</GlossaryTerm> / <GlossaryTerm termKey="pada">пада</GlossaryTerm></span>
        <span><GlossaryTerm termKey="nakshatra_lord">Упр. накш.</GlossaryTerm></span>
        <span><GlossaryTerm termKey="dignity">Статус</GlossaryTerm></span>
        <span><GlossaryTerm termKey="combustion">Аста</GlossaryTerm></span>
        <span><GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm></span>
        <span><GlossaryTerm termKey="navamsa">D9</GlossaryTerm></span>
      </div>
      {chart.ascendant ? (
        <div className="table-row lagna-row" key="ascendant">
          <strong><GlossaryTerm termKey="lagna">{grahaTermLabel("Lagna", termLanguage)}</GlossaryTerm></strong>
          <span><LongitudeValue label={grahaTermLabel("Lagna", termLanguage)} longitude={chart.ascendant.longitude} /></span>
          <span>
            <RashiValue name={chart.ascendant.rashi} index={chart.ascendant.rashi_index} termLanguage={termLanguage} />
          </span>
          <span><HouseValueHelp chart={chart} house={1} termLanguage={termLanguage} /></span>
          <span>-</span>
          <span>
            <NakshatraValue name={chart.ascendant.nakshatra} pada={chart.ascendant.pada} subject={grahaTermLabel("Lagna", termLanguage)} />
          </span>
          <span>
            <NakshatraLordValue
              index={chart.ascendant.nakshatra_index}
              name={chart.ascendant.nakshatra}
              subject={grahaTermLabel("Lagna", termLanguage)}
              termLanguage={termLanguage}
            />
          </span>
          <span className="graha-status-text">-</span>
          <span className="combustion-badge">-</span>
          <span className="shadbala-cell">-</span>
          <span>
            <RashiValue name={chart.ascendant.navamsa} termLanguage={termLanguage} />
          </span>
        </div>
      ) : null}
      {grahas.map((graha) => {
        const rashiIndex = normalizeRashiIndex(graha.rashi_index) ?? rashiIndexFromName(graha.rashi);
        const house = houseFromRashiIndex(rashiIndex, lagnaIndex);
        const ruledHouses = ruledHousesForGraha(graha.body, lagnaIndex);
        const combustion = combustionStatus(graha, sun);
        const grahaLabel = grahaTermLabel(graha.body, termLanguage);
        return (
          <div className="table-row" key={graha.body}>
            <strong><GlossaryTerm termKey="graha">{grahaLabel}</GlossaryTerm></strong>
            <span><LongitudeValue label={grahaLabel} longitude={graha.longitude} /></span>
            <span>
              <PlacementRashiValue graha={graha} chart={chart} house={house} termLanguage={termLanguage} />
            </span>
            <span>{house ? <HouseValueHelp chart={chart} house={house} termLanguage={termLanguage} /> : "-"}</span>
            <span>
              <RuledHousesValue graha={graha} houses={ruledHouses} chart={chart} currentHouse={house} termLanguage={termLanguage} />
            </span>
            <span>
              <NakshatraValue name={graha.nakshatra} pada={graha.pada} subject={grahaLabel} />
            </span>
            <span>
              <NakshatraLordValue index={graha.nakshatra_index} name={graha.nakshatra} subject={grahaLabel} termLanguage={termLanguage} />
            </span>
            <span className="graha-status-text"><GrahaStatusValue graha={graha} house={house} termLanguage={termLanguage} /></span>
            <span className={combustion.combust ? "combustion-badge active" : "combustion-badge"}>
              <CalculationValueHelp
                title={`Аста: ${grahaLabel}`}
                text={
                  combustion.distance === null
                    ? `${grahaLabel}: сожжение не применяется или нет данных для сравнения с Солнцем.`
                    : `${grahaLabel}: расстояние от Солнца ${combustion.distance.toFixed(1)}°. Порог сожжения: ${combustion.threshold ?? "-"}°.`
                }
              >
                {combustion.label}
              </CalculationValueHelp>
            </span>
            <span className="shadbala-cell">
              <ShadbalaValue chart={chart} body={graha.body} label={grahaLabel} />
            </span>
            <span>
              <NavamsaValue graha={graha} chart={chart} termLanguage={termLanguage} />
            </span>
          </div>
        );
      })}
    </div>
  );
}

function SelectedReaderExplanationPanel({
  explanation,
  onClear,
}: {
  explanation: ReaderExplanationDetail | null;
  onClear: () => void;
}) {
  if (!explanation) return null;
  return (
    <section className="selected-reader-explanation" aria-live="polite">
      <div>
        <span>{explanation.context ?? "Объяснение"}</span>
        <strong>{explanation.title}</strong>
      </div>
      <div className="selected-reader-text">
        {explanation.text.split("\n\n").map((paragraph) => (
          <p key={paragraph}>{paragraph}</p>
        ))}
      </div>
      <div className="selected-reader-actions">
        <button type="button" className="help-ai-action" onClick={() => requestAiExplanation(explanation)}>
          Спросить
        </button>
        <button type="button" className="secondary-button compact" onClick={onClear} aria-label="Скрыть объяснение">
          Скрыть
        </button>
      </div>
    </section>
  );
}

function ChartSideCalculationTable({
  chart,
  termLanguage,
  status,
  currentChartDefault,
  selectedExplanation,
  onClearExplanation,
  onRetryCurrentChart,
  onStartBirthCalculation,
}: {
  chart: BirthChart | null;
  termLanguage: TermLanguage;
  status: string;
  currentChartDefault: boolean;
  selectedExplanation: ReaderExplanationDetail | null;
  onClearExplanation: () => void;
  onRetryCurrentChart?: () => void;
  onStartBirthCalculation?: () => void;
}) {
  const grahas = chart?.grahas ?? [];
  const sun = grahas.find((graha) => graha.body === "Surya");
  const lagnaIndex = normalizeRashiIndex(chart?.ascendant?.rashi_index) ?? rashiIndexFromName(chart?.ascendant?.rashi);
  function openRowExplanation(detail: ReaderExplanationDetail) {
    publishReaderExplanation(detail);
  }

  function handleRowKeyDown(event: ReactKeyboardEvent<HTMLDivElement>, detail: ReaderExplanationDetail) {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    openRowExplanation(detail);
  }

  if (!chart || grahas.length === 0) {
    const emptyTitle = "Планеты";
    const emptyStatus =
      currentChartDefault
        ? status.includes("недоступ")
          ? "Расчёт временно недоступен."
          : "Запускается автоматически."
        : /счит|рассчит/i.test(status)
          ? status
          : /недоступ|ошиб|не удалось|числами|API|сервис|server|500/i.test(status)
            ? status
          : "Расчёт ещё не построен.";
    const emptyRows = ["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"];
    const canRetryCurrentChart = currentChartDefault && !chart && status.toLowerCase().includes("недоступ");
    const canStartBirthCalculation = !currentChartDefault && !chart && onStartBirthCalculation;

    return (
      <section className="chart-side-table empty">
        <div className="chart-side-table-head">
          <strong>{emptyTitle}</strong>
        </div>
        <div className="chart-empty-state">
          <strong>{emptyStatus}</strong>
          {canRetryCurrentChart && onRetryCurrentChart ? (
            <button type="button" className="secondary-button compact" onClick={onRetryCurrentChart}>
              Повторить
            </button>
          ) : null}
          {canStartBirthCalculation ? (
            <button type="button" className="secondary-button compact" onClick={onStartBirthCalculation}>
              Рассчитать
            </button>
          ) : null}
        </div>
        <div className="chart-side-table-grid chart-side-table-skeleton" aria-hidden="true">
          <div className="chart-side-table-row chart-side-table-header">
            <span>Граха</span>
            <span>Градус</span>
            <span>Раши</span>
            <span>Накшатра</span>
            <span>Пада</span>
            <span>Дом</span>
            <span>Упр.</span>
            <span>Статус</span>
            <span>Аста</span>
            <span>Шадбала</span>
            <span>D9</span>
          </div>
          {emptyRows.map((label) => (
            <div className="chart-side-table-row empty-row" key={`empty-${label}`}>
              <strong>{label}</strong>
              <span>-</span>
              <span>-</span>
              <span>-</span>
              <span>-</span>
              <span>-</span>
              <span>-</span>
              <span>-</span>
              <span>-</span>
              <span>-</span>
              <span>-</span>
            </div>
          ))}
        </div>
        <SelectedReaderExplanationPanel explanation={selectedExplanation} onClear={onClearExplanation} />
      </section>
    );
  }

  const lagnaExplanation: ReaderExplanationDetail | null = chart.ascendant
    ? {
        title: `${grahaTermLabel("Lagna", termLanguage)}: ${rashiTermFromName(chart.ascendant.rashi, termLanguage)}`,
        context: "Таблица D1",
        text: readerExplanationForHouse({ chart, varga: null, chartReference: "lagna", house: 1, termLanguage }).text,
      }
    : null;

  return (
    <section className="chart-side-table" aria-label="Краткая таблица расчётов рядом с картой">
      <SelectedReaderExplanationPanel explanation={selectedExplanation} onClear={onClearExplanation} />
      <div className="chart-side-table-grid">
        <div className="chart-side-table-row chart-side-table-header">
          <span>Граха</span>
          <span>Градус</span>
          <span>Раши</span>
          <span>Накшатра</span>
          <span>Пада</span>
          <span>Упр. накш.</span>
          <span>Дом</span>
          <span><GlossaryTerm termKey="ruled_houses">Упр.</GlossaryTerm></span>
          <span>Статус</span>
          <span>Аста</span>
          <span>Шад</span>
          <span>D9</span>
        </div>
        {chart.ascendant ? (
          <div
            className="chart-side-table-row lagna-row clickable-reader-row"
            role="button"
            tabIndex={0}
            onClick={() => lagnaExplanation ? openRowExplanation(lagnaExplanation) : undefined}
            onKeyDown={(event) => lagnaExplanation ? handleRowKeyDown(event, lagnaExplanation) : undefined}
          >
              <strong>
                <CalculationValueHelp
                  title={`${grahaTermLabel("Lagna", termLanguage)}: ${rashiTermFromName(chart.ascendant.rashi, termLanguage)}`}
                  text={readerExplanationForHouse({ chart, varga: null, chartReference: "lagna", house: 1, termLanguage }).text}
                >
                  {grahaTermLabel("Lagna", termLanguage)}
                </CalculationValueHelp>
                <span className="mobile-house-badge">1</span>
              </strong>
            <span><LongitudeValue label={grahaTermLabel("Lagna", termLanguage)} longitude={chart.ascendant.longitude} /></span>
            <span><RashiValue name={chart.ascendant.rashi} index={chart.ascendant.rashi_index} termLanguage={termLanguage} compact /></span>
            <span><NakshatraValue name={chart.ascendant.nakshatra} subject={grahaTermLabel("Lagna", termLanguage)} /></span>
            <span>{chart.ascendant.pada ? <GlossaryTerm termKey="pada">{chart.ascendant.pada}</GlossaryTerm> : "-"}</span>
            <span>
              <NakshatraLordValue
                index={chart.ascendant.nakshatra_index}
                name={chart.ascendant.nakshatra}
                subject={grahaTermLabel("Lagna", termLanguage)}
                termLanguage={termLanguage}
              />
            </span>
            <span><HouseValueHelp chart={chart} house={1} termLanguage={termLanguage} /></span>
            <span>-</span>
            <span>-</span>
            <span>-</span>
            <span>-</span>
            <span><RashiValue name={chart.ascendant.navamsa} termLanguage={termLanguage} compact /></span>
          </div>
        ) : null}
        {grahas.map((graha) => {
          const rashiIndex = normalizeRashiIndex(graha.rashi_index) ?? rashiIndexFromName(graha.rashi);
          const house = houseFromRashiIndex(rashiIndex, lagnaIndex);
          const ruledHouses = ruledHousesForGraha(graha.body, lagnaIndex);
          const combustion = combustionStatus(graha, sun);
          const grahaLabel = grahaTermLabel(graha.body, termLanguage);
          const rowExplanation: ReaderExplanationDetail = {
            title: `${grahaLabel}: ${rashiTermFromName(graha.rashi, termLanguage)}${house ? `, ${house} дом` : ""}`,
            context: "Таблица D1",
            text: placementExplanationText({ graha, chart, house, termLanguage }),
          };
          return (
            <div
              className="chart-side-table-row clickable-reader-row"
              key={`side-${graha.body}`}
              role="button"
              tabIndex={0}
              onClick={() => openRowExplanation(rowExplanation)}
              onKeyDown={(event) => handleRowKeyDown(event, rowExplanation)}
            >
              <strong>
                <PlacementNameHelp graha={graha} chart={chart} house={house} termLanguage={termLanguage} />
                {house ? <span className="mobile-house-badge">{house}</span> : null}
              </strong>
              <span><LongitudeValue label={grahaLabel} longitude={graha.longitude} /></span>
              <span><PlacementRashiValue graha={graha} chart={chart} house={house} termLanguage={termLanguage} compact /></span>
              <span><NakshatraValue name={graha.nakshatra} subject={grahaLabel} /></span>
              <span>{graha.pada ? <GlossaryTerm termKey="pada">{graha.pada}</GlossaryTerm> : "-"}</span>
              <span><NakshatraLordValue index={graha.nakshatra_index} name={graha.nakshatra} subject={grahaLabel} termLanguage={termLanguage} /></span>
              <span><HouseValueHelp chart={chart} house={house} termLanguage={termLanguage} /></span>
              <span>
                <RuledHousesValue graha={graha} houses={ruledHouses} chart={chart} currentHouse={house} termLanguage={termLanguage} />
              </span>
              <span className="chart-side-status"><GrahaStatusValue graha={graha} house={house} termLanguage={termLanguage} /></span>
              <span className={combustion.combust ? "combustion-badge active" : "combustion-badge"}>
                <CalculationValueHelp
                  title={`Аста: ${grahaLabel}`}
                  text={combustion.distance === null ? `${grahaLabel}: сожжение не применяется или нет данных для сравнения с Солнцем.` : `${grahaLabel}: расстояние от Солнца ${combustion.distance.toFixed(1)}°. Порог сожжения: ${combustion.threshold ?? "-"}°.`}
                >
                  {combustion.label}
                </CalculationValueHelp>
              </span>
              <span className="shadbala-cell"><ShadbalaValue chart={chart} body={graha.body} label={grahaLabel} /></span>
              <span><NavamsaValue graha={graha} chart={chart} termLanguage={termLanguage} compact /></span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function ChartSideCoreSummary({ chart, termLanguage }: { chart: BirthChart; termLanguage: TermLanguage }) {
  const moon = chart.grahas.find((graha) => graha.body === "Chandra");
  const sun = chart.grahas.find((graha) => graha.body === "Surya");
  const panchanga = chart.panchanga;
  const panchangaValue = panchanga?.tithi ? `${panchanga.tithi.paksha} ${panchanga.tithi.name}` : "-";
  const panchangaNote = panchanga?.nakshatra ? `${panchanga.nakshatra.name}${panchanga.nakshatra.pada ? ` ${panchanga.nakshatra.pada}` : ""}` : "";

  return (
    <div className="chart-core-summary" aria-label="Основные данные D1">
      <div>
        <span><GlossaryTerm termKey="lagna">Лагна</GlossaryTerm></span>
        <strong>{chart.ascendant ? <RashiValue name={chart.ascendant.rashi} index={chart.ascendant.rashi_index} termLanguage={termLanguage} compact /> : "-"}</strong>
        <small>{chart.ascendant ? formatSignDegrees(chart.ascendant.longitude) : ""}</small>
      </div>
      <div>
        <span><GlossaryTerm termKey="chandra_lagna">Луна</GlossaryTerm></span>
        <strong>{moon ? <RashiValue name={moon.rashi} index={moon.rashi_index} termLanguage={termLanguage} compact /> : "-"}</strong>
        <small>{moon ? `${moon.nakshatra ?? ""}${moon.pada ? ` ${moon.pada}` : ""}` : ""}</small>
      </div>
      <div>
        <span><GlossaryTerm termKey="surya_lagna">Солнце</GlossaryTerm></span>
        <strong>{sun ? <RashiValue name={sun.rashi} index={sun.rashi_index} termLanguage={termLanguage} compact /> : "-"}</strong>
        <small>{sun ? formatSignDegrees(sun.longitude) : ""}</small>
      </div>
      <div>
        <span><GlossaryTerm termKey="panchanga">Панчанга</GlossaryTerm></span>
        <strong>{panchangaValue}</strong>
        <small>{panchangaNote}</small>
      </div>
    </div>
  );
}

const combustionThresholds: Record<string, number> = {
  Chandra: 12,
  Mangala: 17,
  Budha: 14,
  Guru: 11,
  Shukra: 10,
  Shani: 15,
};

function combustionStatus(graha: GrahaPosition, sun: GrahaPosition | undefined) {
  if (!sun || graha.body === "Surya" || graha.body === "Rahu" || graha.body === "Ketu") {
    return { combust: false, label: "—", distance: null, threshold: null };
  }
  const threshold = combustionThresholds[graha.body];
  if (!threshold) return { combust: false, label: "—", distance: null, threshold: null };
  const distance = angularDistance(graha.longitude, sun.longitude);
  return {
    combust: distance <= threshold,
    label: distance <= threshold ? `Аста ${distance.toFixed(1)}°` : `${distance.toFixed(1)}°`,
    distance,
    threshold,
  };
}

function angularDistance(a: number, b: number) {
  const diff = Math.abs((((a - b) % 360) + 540) % 360 - 180);
  return diff;
}

function vargaPlacementStatusText(placement: VargaPlacement, natal?: GrahaPosition) {
  const rashiIndex = normalizeRashiIndex(placement.rashi_index) ?? rashiIndexFromName(placement.rashi);
  const dignity = dignityForPlacement(placement.body, rashiIndex, placement.dignity ?? natal?.dignity ?? null);
  const dignityLabelText = dignityText(dignity);
  const parts = [...(natal && isRetrogradeGraha(natal) ? ["ретроградная"] : []), ...(dignityLabelText ? [dignityLabelText] : [])];
  return parts.length ? parts.join(", ") : "-";
}

function VargaTable({ chart, placements, code, termLanguage }: { chart: BirthChart | null; placements: VargaPlacement[]; code: string; termLanguage: TermLanguage }) {
  if (placements.length === 0) {
    return (
      <div className="readiness-panel">
        <strong>Положения {code} ещё не рассчитаны</strong>
        <p>Варга появится после расчёта грах и лагны.</p>
      </div>
    );
  }

  return (
    <div className="planet-table compact-table">
      <div className="table-row table-head">
        <span><GlossaryTerm termKey="graha">Точка</GlossaryTerm></span>
        <span><GlossaryTerm termKey="rashi">Раши</GlossaryTerm> {code}</span>
        <span>D1</span>
        <span><GlossaryTerm termKey="dignity">Статус</GlossaryTerm></span>
      </div>
      {placements.map((placement) => {
        const natal = chart?.grahas.find((graha) => canonicalBody(graha.body) === canonicalBody(placement.body));
        return (
          <div className="table-row" key={placement.body}>
            <strong>{grahaTermLabel(placement.body, termLanguage)}</strong>
            <span>{rashiTermFromName(placement.rashi, termLanguage)}</span>
            <span>{rashiTermFromName(natal?.rashi, termLanguage)}</span>
            <span className="graha-status-text">{vargaPlacementStatusText(placement, natal)}</span>
          </div>
        );
      })}
    </div>
  );
}

function DashaTimeline({ periods }: { periods: DashaPeriod[] }) {
  if (periods.length === 0) {
    return (
      <div className="pending-strip">
        Даши появятся после расчёта Луны.
      </div>
    );
  }

  return (
    <div className="dasha-timeline">
      {periods.map((period) => (
        <div className="dasha-period" key={`${period.lord}-${period.starts_at}`}>
          <strong>{labelRu(period.lord)}</strong>
          <span>{period.duration_years.toFixed(2)} г.</span>
          <small>
            {formatDate(period.starts_at)} - {formatDate(period.ends_at)}
          </small>
        </div>
      ))}
    </div>
  );
}

function PersonSummaryPanel({ summary }: { summary: PersonSummary | null }) {
  if (!summary) return null;

  return (
    <section className="panel person-summary-panel">
      <div className="panel-heading">
        <h2>Сводка по человеку</h2>
      </div>
      <div className="summary-content">
        <div className="summary-grid">
          {summary.core_factors.map((item) => (
            <div className="summary-card" key={item.label}>
              <span>{labelRu(item.label)}</span>
              <strong>{valueRu(item.value)}</strong>
              {item.detail ? <small>{valueRu(item.detail)}</small> : null}
            </div>
          ))}
        </div>
        <div className="summary-columns">
          <div className="summary-list">
            <h3>Контекст рождения</h3>
            {summary.birth_context.map((item) => (
              <div key={item.label}>
                <span>{labelRu(item.label)}</span>
                <strong>{valueRu(item.value)}</strong>
              </div>
            ))}
          </div>
          <div className="summary-list">
            <h3>Панчанга</h3>
            {summary.panchanga.map((item) => (
              <div key={item.label}>
                <span>{labelRu(item.label)}</span>
                <strong>{valueRu(item.value)}</strong>
              </div>
            ))}
            <div>
              <span>Даша при рождении</span>
              <strong>{summary.dasha.birth_mahadasha_lord ? labelRu(summary.dasha.birth_mahadasha_lord) : "Ожидает"}</strong>
            </div>
            <div>
              <span>Текущая махадаша</span>
              <strong>{summary.dasha.current_mahadasha ? labelRu(summary.dasha.current_mahadasha.lord) : "Ожидает"}</strong>
            </div>
            <div>
              <span>Текущая антардаша</span>
              <strong>
                {summary.dasha.current_antardasha
                  ? `${labelRu(summary.dasha.current_antardasha.parent_lord ?? "")}/${labelRu(summary.dasha.current_antardasha.lord)}`
                  : "Ожидает"}
              </strong>
            </div>
            <div>
              <span>На дату</span>
              <strong>{summary.dasha.as_of ? formatDate(summary.dasha.as_of) : "Ожидает"}</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function DetailedCalculationsPanel({
  summary,
  chart,
  activeCode,
  termLanguage,
}: {
  summary: PersonSummary | null;
  chart: BirthChart | null;
  activeCode: string;
  termLanguage: TermLanguage;
}) {
  const detailedPositions = summary?.detailed_positions ?? [];
  const isD1 = activeCode === "D1";

  return (
    <section className="panel calculation-detail-panel">
      <div className="panel-heading">
        <h2>Ключевые данные</h2>
        <span>D1, D9, накшатры, дома</span>
      </div>
      <div className="summary-content">
        {!summary ? <div className="pending-strip">Подробные расчёты появятся после построения карты.</div> : null}
        {isD1 ? (
          <div className="calculation-d1-ledger" aria-label="Главная таблица расчётов D1">
            <div className="calculation-d1-ledger-head">
              <div>
                <h3>Главная таблица D1</h3>
                <span>Первый взгляд астролога: лагна, Луна, даша, сожжение, шадбала и положения грах.</span>
              </div>
              <div className="active-calculation-tags">
                <GlossaryTerm termKey="lagna">Лагна</GlossaryTerm>
                <GlossaryTerm termKey="house">Дома</GlossaryTerm>
                <GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm>
              </div>
            </div>
            <AstrologerPrioritySummary chart={chart} termLanguage={termLanguage} />
            <PanchangaDigest chart={chart} />
            <GrahaTable chart={chart} termLanguage={termLanguage} />
          </div>
        ) : null}
        {detailedPositions.length ? (
          <div className="detailed-positions">
            <div>
              <h3>Подробные положения</h3>
              <span>D1, D9, накшатра, достоинство</span>
            </div>
            <div className="detailed-table">
              <div className="detailed-row detailed-head">
                <span><GlossaryTerm termKey="graha">Граха</GlossaryTerm></span>
                <span><GlossaryTerm termKey="karaka">Карака</GlossaryTerm></span>
                <span><GlossaryTerm termKey="longitude">Градусы</GlossaryTerm></span>
                <span><GlossaryTerm termKey="rashi">Раши</GlossaryTerm></span>
                <span><GlossaryTerm termKey="navamsa">D9</GlossaryTerm></span>
                <span><GlossaryTerm termKey="nakshatra">Накшатра</GlossaryTerm> / <GlossaryTerm termKey="pada">пада</GlossaryTerm></span>
                <span><GlossaryTerm termKey="house">Дом</GlossaryTerm></span>
                <span><GlossaryTerm termKey="ruled_houses">Упр.</GlossaryTerm></span>
                <span><GlossaryTerm termKey="dignity">Сила</GlossaryTerm></span>
              </div>
              {detailedPositions.map((row) => {
                const graha = chart?.grahas.find((item) => canonicalBody(item.body) === canonicalBody(row.body));
                return (
                  <div className="detailed-row" key={row.body}>
                    <strong>{labelRu(row.body)}</strong>
                    <span>{row.chara_karaka ?? "-"}</span>
                    <span>{row.sign_degrees_dms}</span>
                    <span>{row.rashi}</span>
                    <span>{row.navamsa}</span>
                    <span>
                      {row.nakshatra} {row.pada ?? ""}
                    </span>
                    <span>
                      {row.house ? <HouseValueHelp chart={chart} house={row.house} termLanguage={termLanguage} /> : "-"}
                    </span>
                    <span>
                      {graha && chart ? (
                        <RuledHousesValue graha={graha} houses={row.ruled_houses} chart={chart} currentHouse={row.house} termLanguage={termLanguage} />
                      ) : (
                        <HouseGlossaryList houses={row.ruled_houses} />
                      )}
                    </span>
                    <span>
                      {graha ? <GrahaStatusValue graha={graha} house={row.house} termLanguage={termLanguage} /> : [row.dignity, row.retrograde ? "ретроградная" : ""].filter(Boolean).join(", ") || "-"}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function DashaWorkspacePanel({
  summary,
  periods,
  extra,
}: {
  summary: PersonSummary | null;
  periods: DashaPeriod[];
  extra?: NonNullable<BirthChart["dashas"]>["extra"];
}) {
  const yoginiPeriods = extra?.yogini?.mahadashas ?? [];
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Периоды Вимшоттари</h2>
        <span>{periods.length ? "Махадаши и текущие антардаши" : "Ожидает долготу Луны"}</span>
      </div>
      <DashaTimeline periods={periods} />
      {summary?.dasha.current_mahadasha_antardashas.length ? (
        <div className="antardasha-panel">
          <div>
            <h3>Антардаши текущей махадаши</h3>
            <span>{summary.dasha.current_mahadasha ? labelRu(summary.dasha.current_mahadasha.lord) : "Ожидает"} махадаша</span>
          </div>
          <div className="antardasha-strip">
            {summary.dasha.current_mahadasha_antardashas.map((period) => {
              const isActive =
                period.lord === summary.dasha.current_antardasha?.lord &&
                period.parent_lord === summary.dasha.current_antardasha?.parent_lord;
              return (
                <div className={isActive ? "antardasha-item active" : "antardasha-item"} key={`${period.parent_lord}-${period.lord}-${period.starts_at}`}>
                  <strong>{labelRu(period.lord)}</strong>
                  <span>{period.duration_years.toFixed(2)} г.</span>
                  <small>
                    {formatDate(period.starts_at)} - {formatDate(period.ends_at)}
                  </small>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
      {extra ? (
        <div className="antardasha-panel">
          <div>
            <h3>Yogini / Ashtottari</h3>
            <span>{extra.status}</span>
          </div>
          <div className="antardasha-strip">
            {yoginiPeriods.slice(0, 8).map((period) => (
              <div className="antardasha-item" key={`yogini-${period.name}-${period.starts_at}`}>
                <strong>{period.name ?? labelRu(period.lord)}</strong>
                <span>{labelRu(period.lord)} · {period.duration_years.toFixed(2)} г.</span>
                <small>{formatDate(period.starts_at)} - {formatDate(period.ends_at)}</small>
              </div>
            ))}
          </div>
          <p className="workflow-note">Аштоттари: {extra.ashtottari?.status ?? "ожидает"}.</p>
        </div>
      ) : null}
    </section>
  );
}

function publicReportText(value: string) {
  return value
    .replaceAll("Расчётная сводка", "Ключевые данные")
    .replaceAll("Расчетная сводка", "Ключевые данные")
    .split(/(?<=[.!?])\s+/)
    .filter((sentence) => !/JHora|Parashara Light|паритет|чернов/i.test(sentence))
    .join(" ")
    .trim();
}

function ReportPreviewPanel({
  birthReport,
  draftAnalysis,
  draftStatus,
  aiBillingStatus,
  onGenerateDraft,
  onRegenerateDraft,
  draftDisabled,
  chatMessages,
  chatStatus,
  suggestedQuestion,
  onAskDraftQuestion,
  chatDisabled,
}: {
  birthReport: BirthReport["report"] | null;
  draftAnalysis: GeneratedDraftAnalysis | null;
  draftStatus: string;
  aiBillingStatus: { label: string; text: string; tone: "free" | "paid" | "neutral" };
  onGenerateDraft: () => void;
  onRegenerateDraft: () => void;
  draftDisabled: boolean;
  chatMessages: CodexAnalysisChatMessage[];
  chatStatus: string;
  suggestedQuestion: string;
  onAskDraftQuestion: (question: string) => void;
  chatDisabled: boolean;
}) {
  const [chatQuestion, setChatQuestion] = useState("");

  useEffect(() => {
    if (suggestedQuestion) setChatQuestion(suggestedQuestion);
  }, [suggestedQuestion]);

  function handleChatSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const question = chatQuestion.trim();
    if (!question) return;
    onAskDraftQuestion(question);
    setChatQuestion("");
  }

  return (
    <section className="panel report-preview">
      <div className="panel-heading">
        <h2>Разбор карты</h2>
      </div>
      <div className={`ai-billing-status report-ai-billing-status ${aiBillingStatus.tone}`}>
        <strong>{aiBillingStatus.label}</strong>
        <span>{aiBillingStatus.text}</span>
      </div>
      {birthReport ? (
        <div className="report-sections">
          <div className="draft-generation-strip">
            <div>
              <strong>Разбор по карте</strong>
              <span>{draftStatus}</span>
            </div>
            <div className="draft-generation-actions">
              <button type="button" className="secondary-button" onClick={onGenerateDraft} disabled={draftDisabled}>
                Сгенерировать личный разбор
              </button>
              <button type="button" className="secondary-button" onClick={onRegenerateDraft} disabled={draftDisabled}>
                Перегенерировать с новыми шастрами
              </button>
            </div>
            <p className="ai-billing-note">
              Первый разбор доступен бесплатно для карты, отмеченной как «моя карта». Чужие сохранённые карты можно хранить и смотреть бесплатно; разбор чужой карты будет отдельным действием.
            </p>
            {draftAnalysis?.billing_message ? <p className="ai-billing-note">{draftAnalysis.billing_message}</p> : null}
          </div>
          {draftAnalysis ? (
            <div className="generated-draft">
              <div className="block-heading">
                <h3>{generatedTitleRu(draftAnalysis.review_status)}</h3>
              </div>
              <div className="codex-analysis-chat">
                <div className="chat-heading">
                  <strong>Вопросы по этому разбору</strong>
                  <span>{chatStatus}</span>
                </div>
                {chatMessages.length ? (
                  <div className="chat-thread">
                    {chatMessages.map((message, index) => (
                      <div className={`chat-message ${message.role}`} key={`${message.role}-${index}-${message.content.slice(0, 24)}`}>
                        <strong>{message.role === "user" ? "Вы" : "Ответ"}</strong>
                        <p>{message.content}</p>
                      </div>
                    ))}
                  </div>
                ) : null}
                <form className="chat-form" onSubmit={handleChatSubmit}>
                  <input
                    type="text"
                    value={chatQuestion}
                    onChange={(event) => setChatQuestion(event.target.value)}
                    placeholder="Спросить про брак, работу, даши, риски, духовную практику..."
                    disabled={chatDisabled}
                  />
                  <button type="submit" className="secondary-button" disabled={chatDisabled || !chatQuestion.trim()}>
                    Спросить
                  </button>
                </form>
              </div>
              {draftAnalysis.sections.map((section) => (
                <article className="report-section" key={`${draftAnalysis.id}-${section.title}`}>
                  <div>
                    <strong>{section.title}</strong>
                  </div>
                  <p>{publicReportText(section.body)}</p>
                  {section.key_points?.length ? (
                    <div className="human-points">
                      {section.key_points.map((point) => (
                        <span key={`${section.title}-point-${point}`}>{point}</span>
                      ))}
                    </div>
                  ) : null}
                  {section.practical_steps?.length ? (
                    <div className="practical-steps">
                      <strong>Что делать</strong>
                      <ul>
                        {section.practical_steps.map((step) => (
                          <li key={`${section.title}-step-${step}`}>{step}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                  {section.citation_titles.length ? (
                    <div className="report-citations">
                      {section.citation_titles.map((title) => (
                        <span key={`${section.title}-${title}`}>{title}</span>
                      ))}
                    </div>
                  ) : null}
                  {section.evidence_references?.length ? (
                    <div className="report-citations evidence-citations">
                      {section.evidence_references.map((reference) => (
                        <span key={`${section.title}-${reference}`}>{reference}</span>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))}
            </div>
          ) : null}
          {!draftAnalysis ? birthReport.sections.map((section) => (
            <article className="report-section" key={section.key}>
              <div>
                <strong>{section.title}</strong>
              </div>
              <p>{publicReportText(section.body)}</p>
              {section.citations.length ? (
                <div className="report-citations">
                  {section.citations.map((citation) => (
                    <a href={citation.public_url || "#"} key={`${section.key}-${citation.title}`} target="_blank" rel="noreferrer">
                      {citation.title || citation.work_title}
                    </a>
                  ))}
                </div>
              ) : null}
            </article>
          )) : null}
        </div>
      ) : (
        <div className="pending-strip">Отчёт появится после расчёта карты.</div>
      )}
    </section>
  );
}

function ClassicalPanel({ classical }: { classical: BirthChart["classical"] | undefined }) {
  if (!classical) {
    return null;
  }

  const statusItems: Array<[string, string | null | undefined]> = [
    ["Авастхи", classical.avasthas?.status],
    ["Вимшопака", classical.vimshopaka_bala?.status],
    ["Аштакаварга", classical.ashtakavarga?.status],
    ["Шадбала", classical.shadbala?.status],
    ["Транзиты", classical.transits?.status],
    ["Совместимость", classical.compatibility?.status],
    ["Мухурта", classical.muhurta?.status],
  ];
  const baladi = classical.avasthas?.baladi ?? [];
  const yogas = classical.yogas?.items ?? [];
  const lots = classical.special_points?.arabic_lots ?? [];
  const upagrahas = classical.special_points?.upagrahas.items ?? [];
  const vedicPoints = classical.special_points?.vedic_points.items ?? [];
  const vimshopaka = classical.vimshopaka_bala?.items ?? [];
  const shadbala = classical.shadbala?.items ?? [];
  const ashtakavarga = classical.ashtakavarga;
  const classicalStatusGlossary: Record<string, GlossaryKey> = {
    "Авастхи": "avastha",
    "Вимшопака": "vimshopaka",
    "Аштакаварга": "ashtakavarga",
    "Шадбала": "shadbala",
  };

  return (
    <section className="panel classical-panel">
      <div className="panel-heading">
        <h2>Йоги и силы</h2>
      </div>
      <div className="classical-content">
        <div className="classical-status-grid">
          {statusItems.map(([label, status]) => (
            <div className="classical-status" key={label}>
              <span>{classicalStatusGlossary[label] ? <GlossaryTerm termKey={classicalStatusGlossary[label]}>{label}</GlossaryTerm> : label}</span>
              <strong>{statusRu(status)}</strong>
            </div>
          ))}
        </div>
        <div className="classical-columns">
          <div className="classical-list">
            <h3><GlossaryTerm termKey="avastha">Авастхи</GlossaryTerm></h3>
            {baladi.slice(0, 9).map((item) => (
              <div key={item.body}>
                <span>{labelRu(item.body)}</span>
                <strong>{item.state}</strong>
                <small>{item.degree_band}°, сила {item.strength}</small>
              </div>
            ))}
          </div>
          <div className="classical-list">
            <h3>Йоги</h3>
            {yogas.length ? (
              yogas.map((item) => (
                <div key={item.key}>
                  <span>{item.name}</span>
                  <strong>{item.bodies.map(labelRu).join(", ")}</strong>
                  <small>
                    {statusRu(item.status)}
                    {item.formula?.description ? ` · ${item.formula.description}` : ""}
                  </small>
                </div>
              ))
            ) : (
              <div>
                <span>Найдено</span>
                <strong>0</strong>
              </div>
            )}
          </div>
          <div className="classical-list">
            <h3><GlossaryTerm termKey="argala">Аргала</GlossaryTerm></h3>
            <div>
              <span>Главная</span>
              <strong>{formatArgalaRows(classical.argala?.primary ?? [])}</strong>
            </div>
            <div>
              <span>Препятствие</span>
              <strong>{formatArgalaRows(classical.argala?.obstruction ?? [])}</strong>
            </div>
          </div>
          <div className="classical-list">
            <h3>Точки</h3>
            {lots.map((point) => (
              <div key={point.key}>
                <span>{point.name}</span>
                <strong>{point.rashi}</strong>
                <small>{formatDegrees(point.longitude)}</small>
              </div>
            ))}
            <div>
              <span>Упаграхи</span>
              <strong>{statusRu(classical.special_points?.upagrahas.status)}</strong>
            </div>
            {upagrahas.map((point) => (
              <div key={point.key}>
                <span>{point.name}</span>
                <strong>{point.local_time ?? formatDegrees(point.longitude)}</strong>
                <small>
                  {point.rashi}
                  {point.period ? ` · ${point.period === "day" ? "день" : "ночь"}` : ""}
                  {point.segment ? ` · сегмент ${point.segment}` : ""}
                </small>
              </div>
            ))}
            <div>
              <span>Ведические точки</span>
              <strong>{statusRu(classical.special_points?.vedic_points.status)}</strong>
            </div>
            {vedicPoints.map((point) => (
              <div key={point.key}>
                <span>{point.name}</span>
                <strong>{point.rashi}</strong>
                <small>{point.nakshatra} {point.pada}</small>
              </div>
            ))}
          </div>
          <div className="classical-list">
            <h3><GlossaryTerm termKey="ashtakavarga">Аштакаварга</GlossaryTerm></h3>
            <div>
              <span><GlossaryTerm termKey="sav">SAV total</GlossaryTerm></span>
              <strong>{ashtakavarga?.sarva.total ?? "-"}</strong>
              <small>{statusRu(ashtakavarga?.status)}</small>
            </div>
            {Object.entries(ashtakavarga?.bhinna ?? {}).slice(0, 4).map(([body, row]) => (
              <div key={body}>
                <span>{labelRu(body)}</span>
                <strong>{row.total}</strong>
                <small>{row.scores.join(" ")}</small>
              </div>
            ))}
          </div>
          <div className="classical-list">
            <h3><GlossaryTerm termKey="vimshopaka">Вимшопака</GlossaryTerm></h3>
            {vimshopaka.slice(0, 7).map((row) => (
              <div key={row.body}>
                <span>{labelRu(row.body)}</span>
                <strong>{row.score.toFixed(2)} / 20</strong>
                <small>
                  {row.primary_scheme}; D1 {row.varga_scores.D1?.dignity ?? "-"}; D9{" "}
                  {row.varga_scores.D9?.dignity ?? "-"}
                </small>
              </div>
            ))}
          </div>
          <div className="classical-list">
            <h3><GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm></h3>
            {shadbala.slice(0, 4).map((row) => (
              <div key={row.body}>
                <span>{labelRu(row.body)}</span>
                <strong>{row.known_total}</strong>
                <small>
                  N {row.components.naisargika}, U {row.components.uccha}, S {row.components.sthana ?? 0}, D {row.components.dig}, C{" "}
                  {row.components.chesta ?? 0}, K {row.components.kala ?? 0}, Dr {row.components.drik ?? 0}
                </small>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function formatArgalaRows(rows: { house: number; bodies: string[] }[]) {
  if (!rows.length) return "-";
  return rows.map((row) => `дом ${row.house}: ${row.bodies.map(labelRu).join(", ")}`).join("; ");
}

function TransitPanel({
  report,
  status,
  currentDayStatus,
  currentDayOverview,
  currentDayBusy,
  currentDayDisabled,
  onGenerateCurrentDay,
}: {
  report: TransitReport | null;
  status: string;
  currentDayStatus: string;
  currentDayOverview: GeneratedDraftAnalysis | null;
  currentDayBusy: boolean;
  currentDayDisabled: boolean;
  onGenerateCurrentDay: () => void;
}) {
  const rows = report?.transits.slice(0, 9) ?? [];
  const slowRows = rows.filter((row) => ["Guru", "Shani", "Rahu", "Ketu"].includes(row.body));
  const fastRows = rows.filter((row) => ["Surya", "Chandra", "Mangala", "Budha", "Shukra"].includes(row.body));
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2><GlossaryTerm termKey="transit">Транзиты</GlossaryTerm></h2>
        <span>{status}</span>
      </div>
      <div className="current-day-strip">
        <div>
          <strong><GlossaryTerm termKey="transit">Обзор нынешнего дня</GlossaryTerm></strong>
          <span>{currentDayStatus}</span>
          {currentDayOverview ? <small>Сохранён в истории личных обзоров; можно открыть и продолжить диалог</small> : null}
        </div>
        <div className="current-day-actions">
          <button type="button" className="secondary-button" onClick={onGenerateCurrentDay} disabled={currentDayBusy || currentDayDisabled}>
            {currentDayBusy ? "Сохраняю..." : "Сохранить сегодня"}
          </button>
          {currentDayOverview?.slug ? (
            <a className="primary-link-button" href={`/reports/${currentDayOverview.slug}`}>
              Открыть обзор
            </a>
          ) : null}
        </div>
      </div>
      {rows.length ? (
        <div className="transit-visual-board">
          <TransitRashiBoard rows={rows} />
          <div className="transit-focus-panel">
            <div>
              <strong><GlossaryTerm termKey="transit">Медленные влияния</GlossaryTerm></strong>
              <span>Guru, Shani, Rahu, Ketu</span>
            </div>
            <div className="transit-focus-grid">
              {(slowRows.length ? slowRows : rows.slice(0, 4)).map((row) => (
                <TransitFocusCard row={row} key={`slow-${row.body}`} />
              ))}
            </div>
            <div>
              <strong><GlossaryTerm termKey="transit">Личный ритм дня</GlossaryTerm></strong>
              <span>Surya, Chandra и быстрые грахи</span>
            </div>
            <div className="transit-focus-grid compact">
              {(fastRows.length ? fastRows : rows.slice(0, 5)).map((row) => (
                <TransitFocusCard row={row} key={`fast-${row.body}`} />
              ))}
            </div>
          </div>
        </div>
      ) : null}
      {rows.length ? (
        <div className="workflow-table">
          <div className="workflow-row workflow-head">
            <span><GlossaryTerm termKey="graha">Граха</GlossaryTerm></span>
            <span><GlossaryTerm termKey="rashi">Раши</GlossaryTerm></span>
            <span><GlossaryTerm termKey="lagna">От лагны</GlossaryTerm></span>
            <span><GlossaryTerm termKey="chandra_lagna">От Луны</GlossaryTerm></span>
          </div>
          {rows.map((row) => (
            <div className="workflow-row" key={row.body}>
              <strong><GlossaryTerm termKey="graha">{labelRu(row.body)}</GlossaryTerm></strong>
              <span><GlossaryTerm termKey={rashiGlossaryKey(rashiIndexFromName(row.rashi), row.rashi)}>{row.rashi}</GlossaryTerm></span>
              <span>{row.house_from_lagna ? <GlossaryTerm termKey={houseGlossaryKey(row.house_from_lagna)}>{row.house_from_lagna}</GlossaryTerm> : "-"}</span>
              <span>{row.house_from_moon ? <GlossaryTerm termKey={houseGlossaryKey(row.house_from_moon)}>{row.house_from_moon}</GlossaryTerm> : "-"}</span>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function TransitRashiBoard({ rows }: { rows: TransitRow[] }) {
  const byRashi = new Map<number, TransitRow[]>();
  rows.forEach((row) => {
    const index = rashiIndexFromName(row.rashi);
    if (index === null) return;
    const existing = byRashi.get(index) ?? [];
    existing.push(row);
    byRashi.set(index, existing);
  });

  return (
    <div className="transit-rashi-board" aria-label="Карта текущих транзитов">
      {Array.from({ length: 16 }, (_, index) => {
        const row = Math.floor(index / 4);
        const col = index % 4;
        const signIndex = Object.entries(southIndianSignCells).find(([, cell]) => cell.row === row && cell.col === col)?.[0];
        if (signIndex === undefined) return <div className="transit-rashi-center" key={`transit-center-${index}`} />;
        const rashiIndex = Number(signIndex);
        const items = byRashi.get(rashiIndex) ?? [];
        return (
          <div className="transit-rashi-cell" key={`transit-rashi-${rashiIndex}`}>
            <span>{rashiChartLabels[rashiIndex]}</span>
            {items.slice(0, 4).map((item) => (
              <strong key={item.body}>{northGrahaLabels[item.body] ?? item.body.slice(0, 2)}</strong>
            ))}
            {items.length > 4 ? <em>+{items.length - 4}</em> : null}
          </div>
        );
      })}
    </div>
  );
}

function TransitFocusCard({ row }: { row: TransitRow }) {
  return (
    <div className="transit-focus-card">
      <strong><GlossaryTerm termKey="graha">{labelRu(row.body)}</GlossaryTerm></strong>
      <span><GlossaryTerm termKey={rashiGlossaryKey(rashiIndexFromName(row.rashi), row.rashi)}>{row.rashi}</GlossaryTerm></span>
      <small>
        <GlossaryTerm termKey="lagna">Лагна</GlossaryTerm>{" "}
        {row.house_from_lagna ? <GlossaryTerm termKey={houseGlossaryKey(row.house_from_lagna)}>{row.house_from_lagna}</GlossaryTerm> : "-"} ·{" "}
        <GlossaryTerm termKey="chandra_lagna">Луна</GlossaryTerm>{" "}
        {row.house_from_moon ? <GlossaryTerm termKey={houseGlossaryKey(row.house_from_moon)}>{row.house_from_moon}</GlossaryTerm> : "-"}
      </small>
    </div>
  );
}

function WorkflowMiniChart({ chart, title, hint }: { chart: BirthChart; title: string; hint: string }) {
  return (
    <div className="workflow-mini-chart-card">
      <div className="workflow-mini-chart-head">
        <strong>{title}</strong>
        <span>{hint}</span>
      </div>
      <SouthIndianChartGrid chart={chart} varga={null} compact />
    </div>
  );
}

function CompatibilityProfileChartCard({
  chart,
  profile,
  title,
  chartStyle,
  chartReference,
  termLanguage,
  focusVargas,
}: {
  chart: BirthChart | null;
  profile: ChartProfile | undefined;
  title: string;
  chartStyle: "north" | "south";
  chartReference: ChartReference;
  termLanguage: TermLanguage;
  focusVargas: readonly string[];
}) {
  const miniVargas = chart
    ? focusVargas.filter((code) => code !== "D1" && chart.vargas?.[code]).slice(0, 2)
    : [];

  return (
    <div className="compatibility-profile-chart-card">
      <div className="compatibility-profile-chart-head">
        <div>
          <strong>{title}</strong>
          <span>{profile ? `${profile.display_name} · ${profile.birth_date}` : "сохранённая карта не выбрана"}</span>
        </div>
        <em>{chart ? "расчёт открыт" : "ожидает"}</em>
      </div>
      <div className="compatibility-profile-chart-preview">
        {chart ? (
          chartStyle === "south" ? (
            <SouthIndianChartGrid chart={chart} varga={null} compact chartReference={chartReference} termLanguage={termLanguage} />
          ) : (
            <NorthIndianChartSvg chart={chart} varga={null} compact chartReference={chartReference} termLanguage={termLanguage} />
          )
        ) : (
          <span>Выберите сохранённую карту</span>
        )}
      </div>
      {chart && miniVargas.length ? (
        <div className="compatibility-focus-varga-strip" aria-label={`${title}: D-карты по роли`}>
          {miniVargas.map((code) => {
            const varga = chart.vargas?.[code];
            if (!varga) return null;
            return (
              <div className="compatibility-focus-varga-card" key={`${title}-${code}`}>
                <strong><GlossaryTerm termKey={vargaGlossaryKey(code)}>{code}</GlossaryTerm></strong>
                <span>{varga.name}</span>
                <div>
                  {chartStyle === "south" ? (
                    <SouthIndianChartGrid chart={chart} varga={varga} compact chartReference={chartReference} termLanguage={termLanguage} />
                  ) : (
                    <NorthIndianChartSvg chart={chart} varga={varga} compact chartReference={chartReference} termLanguage={termLanguage} />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

function TithiPraveshaPanel({ report, status }: { report: TithiPraveshaReport | null; status: string }) {
  const annualReturn = report?.return;
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2>Tithi Pravesha</h2>
        <span>{status}</span>
      </div>
      {annualReturn ? (
        <div className="workflow-chart-layout">
          <WorkflowMiniChart chart={annualReturn.chart} title="Годовая карта" hint="Tithi Pravesha" />
          <div className="workflow-table">
            <div className="workflow-row workflow-head">
              <span>Показатель</span>
              <span>Значение</span>
              <span>Контекст</span>
              <span>Статус</span>
            </div>
            <div className="workflow-row">
              <strong>Возвращение</strong>
              <span>{formatDate(annualReturn.date)} · {annualReturn.time}</span>
              <span>{annualReturn.timezone}</span>
              <span>Δ {annualReturn.delta_degrees.toFixed(4)}°</span>
            </div>
            <div className="workflow-row">
              <strong>Лагна года</strong>
              <span>{report.annual_context.lagna.rashi ?? "-"}</span>
              <span>{report.annual_context.lagna.nakshatra ?? "-"}</span>
              <span>{statusRu(report.status)}</span>
            </div>
            <div className="workflow-row">
              <strong>Солнце / Луна</strong>
              <span>{report.annual_context.sun.rashi ?? "-"} / {report.annual_context.moon.rashi ?? "-"}</span>
              <span>{report.annual_context.moon.nakshatra ?? "-"}</span>
              <span>{workflowStatusRu(report.audit.public_interpretation_status)}</span>
            </div>
            <div className="workflow-row">
              <strong>Панчанга</strong>
              <span>{report.annual_context.panchanga.tithi?.name ?? "-"}</span>
              <span>{report.annual_context.panchanga.vara?.name ?? "-"}</span>
              <span>{workflowStatusRu(report.audit.review_status)}</span>
            </div>
            <div className="workflow-row">
              <strong>Muntha</strong>
              <span>{report.annual_context.tajaka?.muntha?.rashi ?? "-"}</span>
              <span>дом {report.annual_context.tajaka?.muntha?.house_from_annual_lagna ?? "-"}</span>
              <span>{report.annual_context.tajaka?.status ?? "baseline"}</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="pending-strip">Годовой разбор появится после расчёта карты.</div>
      )}
    </section>
  );
}

function TajakaPanel({ report, status }: { report: TajakaReport | null; status: string }) {
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2>Tajaka</h2>
        <span>{status}</span>
      </div>
      {report ? (
        <div className="workflow-table">
          <div className="workflow-row workflow-head">
            <span>Раздел</span>
            <span>Значение</span>
            <span>Контекст</span>
            <span>Статус</span>
          </div>
          <div className="workflow-row">
            <strong>Muntha</strong>
            <span>{report.tajaka.muntha?.rashi ?? "-"}</span>
            <span>дом {report.tajaka.muntha?.house_from_annual_lagna ?? "-"}</span>
            <span>{report.tajaka.status}</span>
          </div>
          <div className="workflow-row">
            <strong>Годовая лагна</strong>
            <span>{report.tajaka.annual_lagna.rashi ?? "-"}</span>
            <span>{report.tajaka.annual_moon.nakshatra ?? "-"}</span>
            <span>{workflowStatusRu(report.audit.review_status)}</span>
          </div>
          <div className="workflow-row">
            <strong>Открыто</strong>
            <span>{report.tajaka.open_items.slice(0, 2).join(", ")}</span>
            <span>{report.tajaka.open_items.slice(2).join(", ")}</span>
            <span>{workflowStatusRu(report.audit.public_interpretation_status)}</span>
          </div>
        </div>
      ) : (
        <div className="pending-strip">Таджака появится после расчёта карты.</div>
      )}
    </section>
  );
}

function PrashnaPanel({ report, status }: { report: PrashnaReport | null; status: string }) {
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2>Prashna</h2>
        <span>{status}</span>
      </div>
      {report ? (
        <div className="workflow-chart-layout">
          <WorkflowMiniChart chart={report.chart} title="Prashna" hint="карта вопроса" />
          <div className="workflow-table">
            <div className="workflow-row workflow-head">
              <span>Показатель</span>
              <span>Значение</span>
              <span>Контекст</span>
              <span>Статус</span>
            </div>
            <div className="workflow-row">
              <strong>Лагна</strong>
              <span>{report.indicators.lagna.rashi ?? "-"}</span>
              <span>упр. {labelRu(report.indicators.lagna_lord ?? "")}</span>
              <span>{workflowStatusRu(report.audit.review_status)}</span>
            </div>
            <div className="workflow-row">
              <strong>Луна</strong>
              <span>{report.indicators.moon.rashi ?? "-"}</span>
              <span>дом {report.indicators.moon_house_from_lagna ?? "-"}</span>
              <span>{workflowStatusRu(report.audit.public_interpretation_status)}</span>
            </div>
            <div className="workflow-row">
              <strong>Панчанга</strong>
              <span>{report.indicators.panchanga.tithi?.name ?? "-"}</span>
              <span>{report.indicators.panchanga.nakshatra?.name ?? "-"}</span>
              <span>{report.status}</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="pending-strip">Прашна появится после расчёта карты.</div>
      )}
    </section>
  );
}

function MundanePanel({ report, status }: { report: MundaneReport | null; status: string }) {
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2>Mundane</h2>
        <span>{status}</span>
      </div>
      {report ? (
        <div className="workflow-chart-layout">
          <WorkflowMiniChart chart={report.chart} title="Mundane" hint="event chart" />
          <div className="workflow-table">
            <div className="workflow-row workflow-head">
              <span>Показатель</span>
              <span>Значение</span>
              <span>Контекст</span>
              <span>Статус</span>
            </div>
            <div className="workflow-row">
              <strong>Event</strong>
              <span>{report.event.type}</span>
              <span>{formatDate(report.event.occurred_at.date)} · {report.event.occurred_at.time}</span>
              <span>{workflowStatusRu(report.audit.review_status)}</span>
            </div>
            <div className="workflow-row">
              <strong>Оси</strong>
              <span>10: {report.indicators.tenth_house_rashi ?? "-"}</span>
              <span>4: {report.indicators.fourth_house_rashi ?? "-"}</span>
              <span>{report.status}</span>
            </div>
            {report.indicators.slow_planets.slice(0, 4).map((row) => (
              <div className="workflow-row" key={row.body}>
                <strong>{labelRu(row.body)}</strong>
                <span>{row.placement.rashi ?? "-"}</span>
                <span>дом {row.house_from_lagna ?? "-"}</span>
                <span>{workflowStatusRu(report.audit.public_interpretation_status)}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="pending-strip">Карта события появится после расчёта.</div>
      )}
    </section>
  );
}

function MuhurtaPanel({ report, status }: { report: MuhurtaReport | null; status: string }) {
  const rows = report?.candidates.slice(0, 5) ?? [];
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2>Мухурта</h2>
        <span>{status}</span>
      </div>
      {rows.length ? (
        <div className="muhurta-list">
          {rows.map((candidate) => (
            <div className="muhurta-item" key={`${candidate.date}-${candidate.time}`}>
              <strong>{formatDate(candidate.date)} · {candidate.time}</strong>
              <span>{candidate.score}/100</span>
              <small>
                {candidate.panchanga.tithi?.name ?? "Титхи"} · {candidate.panchanga.vara?.name ?? "Вара"}
              </small>
              {candidate.blocked_periods?.length ? (
                <small className="avoid-line">
                  Попадает: {candidate.blocked_periods.map(formatPeriodRange).join("; ")}
                </small>
              ) : null}
              {candidate.day_periods?.length ? (
                <div className="period-chip-row">
                  {candidate.day_periods.map((period) => (
                    <span className="period-chip" key={`${candidate.date}-${period.key}`}>
                      {formatPeriodRange(period)}
                    </span>
                  ))}
                </div>
              ) : null}
              <p>{candidate.reasons.length ? candidate.reasons.join("; ") : "Нейтральная панчанга"}</p>
            </div>
          ))}
          <p className="workflow-note">{report?.vaishnava_note}</p>
        </div>
      ) : (
        <div className="pending-strip">Кандидаты мухурты появятся после расчёта карты.</div>
      )}
    </section>
  );
}

type CompatibilityPanelProps = {
  report: CompatibilityReport | null;
  status: string;
  profiles: ChartProfile[];
  selectedPersonAProfileId: string;
  selectedPersonBProfileId: string;
  relationshipRole: CompatibilityRelationshipRoleKey;
  selectedRelationship: ChartProfileRelationship | null;
  personAChart: BirthChart | null;
  personBChart: BirthChart | null;
  chartStatus: string;
  chartStyle: "north" | "south";
  chartReference: ChartReference;
  termLanguage: TermLanguage;
  onRelationshipRoleChange: (role: CompatibilityRelationshipRoleKey) => void;
  partnerProfileName: string;
  partnerBirthDate: string;
  setPartnerBirthDate: Dispatch<SetStateAction<string>>;
  partnerBirthTime: string;
  setPartnerBirthTime: Dispatch<SetStateAction<string>>;
  partnerPlaceName: string;
  setPartnerPlaceName: Dispatch<SetStateAction<string>>;
  setPartnerProfileName: Dispatch<SetStateAction<string>>;
  partnerPlaceMatches: PlaceCandidate[];
  selectedPartnerPlace: PlaceCandidate | null;
  showPartnerPlaceSuggestions: boolean;
  setShowPartnerPlaceSuggestions: Dispatch<SetStateAction<boolean>>;
  partnerPlaceSearchStatus: string;
  onSelectPersonAProfile: (profileId: string) => void;
  onSelectPersonBProfile: (profileId: string) => void;
  onSelectPartnerPlace: (place: PlaceCandidate) => void;
  onSavePartnerProfile: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onGeneratePacket: () => void;
  onGenerateCodexAnalysis: () => void;
  disabled: boolean;
  savePartnerDisabled: boolean;
  packetDisabled: boolean;
  packetStatus: string;
  codexDisabled: boolean;
  codexStatus: string;
  codexAnalysis: GeneratedDraftAnalysis | null;
  chatMessages: CodexAnalysisChatMessage[];
  chatStatus: string;
  onAskCodexQuestion: (question: string) => void;
  chatDisabled: boolean;
};

function CompatibilityRelationshipBoard({
  summaries,
}: {
  summaries: NonNullable<NonNullable<CompatibilityReport["analysis"]>["chart_summaries"]>;
}) {
  return (
    <div className="compatibility-relationship-board" aria-label="Ключевые оси совместимости">
      {(["person_a", "person_b"] as const).map((key) => {
        const summary = summaries[key];
        const title = key === "person_a" ? "Карта A" : "Карта B";
        const items = [
          ["Лагна", summary.lagna.rashi ?? "-"],
          ["Луна", summary.moon.rashi ?? "-"],
          ["7 дом", summary.seventh_house.rashi ?? "-"],
          ["Упр. 7", summary.seventh_house.lord ?? "-"],
          ["Упр. 7 в доме", summary.seventh_lord.house ?? "-"],
          ["Даша", summary.birth_dasha_lord ?? "-"],
        ];

        return (
          <div className="compatibility-relationship-card" key={key}>
            <div className="compatibility-relationship-head">
              <strong>{title}</strong>
              <span>D1 / 7 дом / даша</span>
            </div>
            <div className="compatibility-relationship-grid">
              {items.map(([label, value]) => (
                <div key={`${key}-${label}`}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
            <small>
              7 дом показывает партнёрство; управитель 7 дома показывает, через какую сферу включается связь.
            </small>
          </div>
        );
      })}
    </div>
  );
}

function CompatibilityPanel({
  report,
  status,
  profiles,
  selectedPersonAProfileId,
  selectedPersonBProfileId,
  relationshipRole,
  selectedRelationship,
  personAChart,
  personBChart,
  chartStatus,
  chartStyle,
  chartReference,
  termLanguage,
  onRelationshipRoleChange,
  partnerProfileName,
  partnerBirthDate,
  setPartnerBirthDate,
  partnerBirthTime,
  setPartnerBirthTime,
  partnerPlaceName,
  setPartnerPlaceName,
  setPartnerProfileName,
  partnerPlaceMatches,
  selectedPartnerPlace,
  showPartnerPlaceSuggestions,
  setShowPartnerPlaceSuggestions,
  partnerPlaceSearchStatus,
  onSelectPersonAProfile,
  onSelectPersonBProfile,
  onSelectPartnerPlace,
  onSavePartnerProfile,
  onSubmit,
  onGeneratePacket,
  onGenerateCodexAnalysis,
  disabled,
  savePartnerDisabled,
  packetDisabled,
  packetStatus,
  codexDisabled,
  codexStatus,
  codexAnalysis,
}: CompatibilityPanelProps) {
  const rows = report?.kuta_rows ?? [];
  const perspectives = report?.analysis?.perspectives ?? [];
  const summaries = report?.analysis?.chart_summaries;
  const role = compatibilityRelationshipRole(relationshipRole);
  const scoreLabel = report ? `${report.score.total}/${report.score.max}` : "-";
  const percentLabel = report ? `${report.score.percent.toFixed(1)}%` : "-";
  const levelLabel = report ? compatibilityLevelLabelsRu[report.assessment.level] ?? report.assessment.level : "ожидает";
  const personAProfile = profiles.find((profile) => String(profile.id) === selectedPersonAProfileId);
  const personBProfile = profiles.find((profile) => String(profile.id) === selectedPersonBProfileId);
  const resultContext = report?.relationship_context;
  const roleChartReference = chartReferenceForRelationshipRole(role);
  const roleChartReferenceLabel = chartReferenceOptions.find((option) => option.key === roleChartReference)?.label ?? "Лагна";
  const roleChartReferenceGlossary = referenceGlossaryKeys[roleChartReference] ?? "lagna";

  return (
    <section className="panel workflow-panel compatibility-panel">
      <div className="panel-heading">
        <h2>Совместимость</h2>
        <span>{status}</span>
      </div>
      <form className="compatibility-form" onSubmit={onSubmit}>
        <div className="compatibility-saved-grid">
          <label>
            Сохранённая карта A
            <select value={selectedPersonAProfileId} onChange={(event) => onSelectPersonAProfile(event.target.value)}>
              <option value="">Текущая рассчитанная карта</option>
              {profiles.map((profile) => (
                <option key={`compat-a-${profile.id}`} value={String(profile.id)}>
                  {profile.display_name} · {profile.birth_date}
                </option>
              ))}
            </select>
          </label>
          <label>
            Сохранённая карта B
            <select value={selectedPersonBProfileId} onChange={(event) => onSelectPersonBProfile(event.target.value)}>
              <option value="">Ввести вручную ниже</option>
              {profiles.map((profile) => (
                <option key={`compat-b-${profile.id}`} value={String(profile.id)}>
                  {profile.display_name} · {profile.birth_date}
                </option>
              ))}
            </select>
          </label>
          <label>
            <GlossaryTerm termKey="relationship_role">Ракурс взаимодействия</GlossaryTerm>
            <select value={relationshipRole} onChange={(event) => onRelationshipRoleChange(event.target.value as CompatibilityRelationshipRoleKey)}>
              {compatibilityRelationshipRoles.map((item) => (
                <option key={item.key} value={item.key}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="compatibility-role-context">
          <div>
            <span>Дома</span>
            <strong><HouseGlossaryList houses={role.focusHouses} /></strong>
          </div>
          <div>
            <span>Варги</span>
            <strong><VargaGlossaryList vargas={role.focusVargas} /></strong>
          </div>
          <div>
            <span>Ракурс карты</span>
            <strong>
              <GlossaryTerm termKey={roleChartReferenceGlossary}>{roleChartReferenceLabel}</GlossaryTerm>
            </strong>
          </div>
          <small>{role.promptHint}</small>
        </div>
        {selectedRelationship ? (
          <div className="compatibility-selected-relationship">
            <span>Выбранная связь</span>
            <strong>
              {selectedRelationship.profile?.display_name ?? `Карта ${selectedRelationship.profile_id}`} →{" "}
              {selectedRelationship.related_profile?.display_name ?? `Карта ${selectedRelationship.related_profile_id}`}
            </strong>
            <small>
              <GlossaryTerm termKey="relationship_role">
                {compatibilityRelationshipRole(selectedRelationship.role).label}
              </GlossaryTerm>{" "}
              ·{" "}
              <GlossaryTerm termKey="relationship_status">
                {relationshipStatusLabel(selectedRelationship.link_status)}
              </GlossaryTerm>
            </small>
            <a className="secondary-button compatibility-pair-passport-link" href={`/compatibility/pair/${selectedRelationship.id}`}>
              Открыть пару
            </a>
          </div>
        ) : null}
        <div className="compatibility-profile-chart-board" aria-label="Карты людей для разбора взаимодействия">
          <div className="compatibility-profile-chart-status">
            <strong>{role.label}</strong>
            <span>{chartStatus}</span>
          </div>
          <CompatibilityProfileChartCard
            chart={personAChart}
            profile={personAProfile}
            title="Карта A"
            chartStyle={chartStyle}
            chartReference={chartReference}
            termLanguage={termLanguage}
            focusVargas={role.focusVargas}
          />
          <CompatibilityProfileChartCard
            chart={personBChart}
            profile={personBProfile}
            title="Карта B"
            chartStyle={chartStyle}
            chartReference={chartReference}
            termLanguage={termLanguage}
            focusVargas={role.focusVargas}
          />
        </div>
        <button className="secondary-button compatibility-button primary-compare-button" type="submit" disabled={disabled}>
          Сравнить выбранные карты
        </button>
        <div className="compatibility-form-grid">
          <label>
            Дата второго человека
            <input
              type="date"
              value={partnerBirthDate}
              onInput={(event) => setPartnerBirthDate(event.currentTarget.value)}
              onChange={(event) => setPartnerBirthDate(event.target.value)}
            />
          </label>
          <label>
            Время второго человека
            <input
              type="time"
              value={partnerBirthTime}
              onInput={(event) => setPartnerBirthTime(event.currentTarget.value)}
              onChange={(event) => setPartnerBirthTime(event.target.value)}
            />
          </label>
          <label className="compatibility-place-label">
            Место второго человека
            <input
              value={partnerPlaceName}
              onChange={(event) => {
                setPartnerPlaceName(event.target.value);
                setShowPartnerPlaceSuggestions(true);
              }}
              onFocus={() => setShowPartnerPlaceSuggestions(true)}
              placeholder="Город рождения"
            />
          </label>
        </div>
        <div className="place-suggestions compatibility-suggestions">
          <span>{partnerPlaceSearchStatus}</span>
          {showPartnerPlaceSuggestions && partnerPlaceMatches.length ? (
            <div className="place-suggestion-list">
              {partnerPlaceMatches.slice(0, 5).map((place) => (
                <button type="button" key={place.id} onClick={() => onSelectPartnerPlace(place)}>
                  <strong>{place.label}</strong>
                  <small>{place.timezone} · {formatCoordinate(place.latitude)}, {formatCoordinate(place.longitude)}</small>
                </button>
              ))}
            </div>
          ) : null}
        </div>
        {selectedPartnerPlace ? (
          <div className="compatibility-place-summary">
            <span>Выбрано</span>
            <strong>{selectedPartnerPlace.label}</strong>
            <small>{selectedPartnerPlace.timezone} · {formatCoordinate(selectedPartnerPlace.latitude)}, {formatCoordinate(selectedPartnerPlace.longitude)}</small>
          </div>
        ) : null}
        <div className="compatibility-save-row">
          <label>
            Название карты B
            <input
              type="text"
              value={partnerProfileName}
              onChange={(event) => setPartnerProfileName(event.target.value)}
              placeholder="Например: карта партнёра"
            />
          </label>
          <button className="secondary-button compatibility-button" type="button" onClick={onSavePartnerProfile} disabled={savePartnerDisabled}>
            Сохранить карту B
          </button>
        </div>
      </form>
      <div className="compatibility-actions">
        <button
          className="secondary-button compatibility-button"
          type="button"
          onClick={onGeneratePacket}
          disabled={packetDisabled}
        >
          Подготовить разбор
        </button>
        <button
          className="secondary-button compatibility-button primary-compare-button"
          type="button"
          onClick={onGenerateCodexAnalysis}
          disabled={codexDisabled}
        >
          Полный разбор совместимости
        </button>
      </div>
      {packetStatus ? <p className="compatibility-packet-status">{packetStatus}</p> : null}
      {codexStatus ? <p className="compatibility-packet-status">{codexStatus}</p> : null}

      {report ? (
        <div className="compatibility-result">
          {resultContext ? (
            <div className="compatibility-result-context">
              <div>
                <span>Ракурс разбора</span>
                <strong>{resultContext.label || resultContext.role}</strong>
                <small>{resultContext.prompt_hint || "роль учтена в разборе"}</small>
              </div>
              <div>
                <span>Фокусные дома</span>
                <strong>
                  <HouseGlossaryList houses={resultContext.focus_houses} />
                </strong>
                <small>используются как ракурс чтения</small>
              </div>
              <div>
                <span>D-карты</span>
                <strong><VargaGlossaryList vargas={resultContext.focus_vargas} /></strong>
                <small>{resultContext.required_factors?.slice(0, 4).join(" · ") || "учтены в разборе"}</small>
              </div>
              <div>
                <span><GlossaryTerm termKey="relationship_status">Статус связи</GlossaryTerm></span>
                <strong>
                  <GlossaryTerm termKey="relationship_status">
                    {resultContext.link_status ? relationshipStatusLabel(resultContext.link_status) : "личный ракурс"}
                  </GlossaryTerm>
                </strong>
                <small>
                  {resultContext.profile_label || resultContext.related_profile_label
                    ? `${resultContext.profile_label ?? "Карта A"} → ${resultContext.related_profile_label ?? "Карта B"}`
                    : "без привязки к подтверждённой связи"}
                </small>
              </div>
            </div>
          ) : null}
          <div className="compatibility-score-grid">
            <div>
              <span>Ашта-кута</span>
              <strong>{scoreLabel}</strong>
              <small>{percentLabel}</small>
            </div>
            <div>
              <span>Оценка</span>
              <strong>{levelLabel}</strong>
              <small>нулевых факторов: {report.assessment.caution_count}</small>
            </div>
            <div>
              <span>Луна A/B</span>
              <strong>{report.moon.person_a.nakshatra} / {report.moon.person_b.nakshatra}</strong>
              <small>{report.moon.person_a.rashi} / {report.moon.person_b.rashi}</small>
            </div>
            <div>
              <span>Расчёт</span>
              <strong>{report.coverage.calculated_kutas}/{report.coverage.total_kutas}</strong>
              <small>
                {statusRu(report.coverage.status)}
                {report.coverage.calculated_perspectives
                  ? ` · ${report.coverage.calculated_perspectives} ракурсов`
                  : ""}
              </small>
            </div>
          </div>
          {summaries ? (
            <>
            <div className="compatibility-chart-grid">
              {(["person_a", "person_b"] as const).map((key) => {
                const summary = summaries[key];
                return (
                  <div key={key}>
                    <span>{key === "person_a" ? "Карта A" : "Карта B"}</span>
                    <strong>
                      Лагна {summary.lagna.rashi ?? "-"} · Луна {summary.moon.rashi ?? "-"}
                    </strong>
                    <small>
                      7 дом {summary.seventh_house.rashi ?? "-"}, управитель{" "}
                      {summary.seventh_house.lord ?? "-"} в доме {summary.seventh_lord.house ?? "-"}
                    </small>
                  </div>
                );
              })}
            </div>
            <CompatibilityRelationshipBoard summaries={summaries} />
            </>
          ) : null}
          {perspectives.length ? (
            <div className="compatibility-perspectives">
              <div className="kuta-row kuta-head">
                <span>Ракурс</span>
                <span>Оценка</span>
                <span>Вывод</span>
              </div>
              {perspectives.map((row) => (
                <div className="compatibility-perspective-row" key={row.key}>
                  <div>
                    <strong>{compatibilityPerspectiveLabelsRu[row.key] ?? row.title}</strong>
                    <small>{compatibilityPerspectiveBasisRu[row.key] ?? row.source_basis}</small>
                  </div>
                  <span>
                    {row.max_score ? `${row.score}/${row.max_score}` : "контекст"}
                    <small>{compatibilityLevelLabelsRu[row.status] ?? statusRu(row.status)}</small>
                  </span>
                  <small>{row.findings.slice(0, 2).map(compatibilityFindingRu).join(" ")}</small>
                </div>
              ))}
            </div>
          ) : null}
          <div className="kuta-table">
            <div className="kuta-row kuta-head">
              <span>Кута</span>
              <span>Баллы</span>
              <span>Детали</span>
            </div>
            {rows.map((row) => (
              <div className="kuta-row" key={row.key}>
                <strong>{row.name}</strong>
                <span>{row.score}/{row.max_score}</span>
                <small>{row.details}</small>
              </div>
            ))}
          </div>
          <p className="workflow-note">{report.assessment.note}</p>
        </div>
      ) : (
        <div className="pending-strip">Сначала рассчитайте основную карту, затем добавьте второго человека.</div>
      )}
      {codexAnalysis ? (
        <div className="compatibility-saved-analysis-card">
          <div>
            <span>Сохранённый разбор</span>
            <strong>{generatedStatusRu(codexAnalysis.review_status)}</strong>
            <small>
              Разбор, чат и данные пары открываются отдельной страницей. Там сохраняется история вопросов и показываются D1, 7/12 дома и ключевые варги.
            </small>
          </div>
          <a className="primary-link-button" href={`/compatibility/${codexAnalysis.slug ?? codexAnalysis.id}`}>
            Открыть разбор
          </a>
        </div>
      ) : null}
    </section>
  );
}

function AccuracyReportPanel({
  witnessSummary,
  witnessStatus,
  report,
  status,
  plReport,
  plStatus,
}: {
  witnessSummary: WitnessSummary | null;
  witnessStatus: string;
  report: JHoraAccuracyReport | null;
  status: string;
  plReport: ParasharaLightPacketReport | null;
  plStatus: string;
}) {
  const witnessState = witnessSummary
    ? witnessSummary.open_items.length
      ? "требует внимания"
      : "сверено"
    : "ожидает";
  const jhoraState = witnessSummary?.jhora.available
    ? witnessSummary.jhora.failed_checks
      ? "есть расхождения"
      : "сверено"
    : "ожидает";
  const plState = witnessSummary?.parashara_light.available
    ? witnessSummary.parashara_light.manual_failed_count
      ? "есть расхождения"
      : "сверено"
    : plReport
      ? "загружено"
      : "ожидает";
  const timezoneState = witnessSummary?.birth_timezone_audit?.available
    ? witnessSummary.birth_timezone_audit.resolved_utc_offset ||
      witnessSummary.birth_timezone_audit.local_datetime_utc_offset ||
      "сверено"
    : "ожидает";
  const coreParity = witnessSummary?.witness_core_parity;
  const coreParitySummary = coreParity?.summary;
  const coreParityActions = coreParity?.next_actions.slice(0, 3) ?? [];
  const coreParityTargetMet = Boolean(coreParity?.target_met);
  const coreParityNeedsAttention =
    Boolean(coreParity?.available) &&
    (!coreParityTargetMet ||
      Boolean(coreParitySummary?.failed_count) ||
      Boolean(coreParitySummary?.missing_witness_count) ||
      Boolean(coreParitySummary?.not_reviewed_count) ||
      Boolean(coreParitySummary?.not_comparable_count));
  const coreParityState = coreParity?.available
    ? coreParityTargetMet
      ? "цель достигнута"
      : coreParity.status === "diff_open"
        ? "есть расхождения"
        : "нужны witness-данные"
    : "ожидает";
  const vargaParity = witnessSummary?.witness_varga_parity;
  const vargaParitySummary = vargaParity?.summary;
  const vargaParityCodes = Object.keys(vargaParity?.varga_summary ?? {}).sort();
  const vargaParityActions = vargaParity?.next_actions.slice(0, 3) ?? [];
  const vargaParityTargetMet = Boolean(vargaParity?.target_met);
  const vargaParityNeedsAttention =
    Boolean(vargaParity?.available) &&
    (!vargaParityTargetMet ||
      Boolean(vargaParitySummary?.failed_count) ||
      Boolean(vargaParitySummary?.missing_witness_count) ||
      Boolean(vargaParitySummary?.not_reviewed_count) ||
      Boolean(vargaParitySummary?.not_comparable_count));
  const vargaParityState = vargaParity?.available
    ? vargaParityTargetMet
      ? "цель достигнута"
      : vargaParity.status === "diff_open"
        ? "есть расхождения"
        : "нужны witness-данные"
    : "ожидает";
  const dashaParity = witnessSummary?.witness_dasha_parity;
  const dashaParitySummary = dashaParity?.summary;
  const dashaParityLevels = Object.keys(dashaParity?.level_summary ?? {}).sort();
  const dashaParityActions = dashaParity?.next_actions.slice(0, 3) ?? [];
  const dashaParityTargetMet = Boolean(dashaParity?.target_met);
  const dashaParityNeedsAttention =
    Boolean(dashaParity?.available) &&
    (!dashaParityTargetMet ||
      Boolean(dashaParitySummary?.failed_count) ||
      Boolean(dashaParitySummary?.missing_witness_count) ||
      Boolean(dashaParitySummary?.not_reviewed_count) ||
      Boolean(dashaParitySummary?.not_comparable_count));
  const dashaParityState = dashaParity?.available
    ? dashaParityTargetMet
      ? "цель достигнута"
      : dashaParity.status === "diff_open"
        ? "есть расхождения"
        : "нужны witness-данные"
    : "ожидает";
  const panchangaParity = witnessSummary?.witness_panchanga_parity;
  const panchangaParitySummary = panchangaParity?.summary;
  const panchangaParityFields = Object.keys(panchangaParity?.field_summary ?? {}).sort();
  const panchangaParityActions = panchangaParity?.next_actions.slice(0, 3) ?? [];
  const panchangaParityTargetMet = Boolean(panchangaParity?.target_met);
  const panchangaParityNeedsAttention =
    Boolean(panchangaParity?.available) &&
    (!panchangaParityTargetMet ||
      Boolean(panchangaParitySummary?.failed_count) ||
      Boolean(panchangaParitySummary?.missing_witness_count) ||
      Boolean(panchangaParitySummary?.not_reviewed_count) ||
      Boolean(panchangaParitySummary?.not_comparable_count));
  const panchangaParityState = panchangaParity?.available
    ? panchangaParityTargetMet
      ? "цель достигнута"
      : panchangaParity.status === "diff_open"
        ? "есть расхождения"
        : "нужны witness-данные"
    : "ожидает";
  const ashtakavargaParity = witnessSummary?.witness_ashtakavarga_parity;
  const ashtakavargaParitySummary = ashtakavargaParity?.summary;
  const ashtakavargaParityLayers = Object.keys(ashtakavargaParity?.layer_summary ?? {}).sort();
  const ashtakavargaParityBodies = Object.keys(ashtakavargaParity?.body_summary ?? {}).sort();
  const ashtakavargaParityActions = ashtakavargaParity?.next_actions.slice(0, 3) ?? [];
  const ashtakavargaParityTargetMet = Boolean(ashtakavargaParity?.target_met);
  const ashtakavargaParityNeedsAttention =
    Boolean(ashtakavargaParity?.available) &&
    (!ashtakavargaParityTargetMet ||
      Boolean(ashtakavargaParitySummary?.failed_count) ||
      Boolean(ashtakavargaParitySummary?.missing_witness_count) ||
      Boolean(ashtakavargaParitySummary?.not_reviewed_count) ||
      Boolean(ashtakavargaParitySummary?.not_comparable_count));
  const ashtakavargaParityState = ashtakavargaParity?.available
    ? ashtakavargaParityTargetMet
      ? "target met"
      : ashtakavargaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const strengthsParity = witnessSummary?.witness_strengths_parity;
  const strengthsParitySummary = strengthsParity?.summary;
  const strengthsParityLayers = Object.keys(strengthsParity?.layer_summary ?? {}).sort();
  const strengthsParityBodies = Object.keys(strengthsParity?.body_summary ?? {}).sort();
  const strengthsParityProfileSensitive = strengthsParity?.profile_sensitive_layers ?? [];
  const strengthsParityActions = strengthsParity?.next_actions.slice(0, 3) ?? [];
  const strengthsParityTargetMet = Boolean(strengthsParity?.target_met);
  const strengthsParityNeedsAttention =
    Boolean(strengthsParity?.available) &&
    (!strengthsParityTargetMet ||
      Boolean(strengthsParitySummary?.failed_count) ||
      Boolean(strengthsParitySummary?.missing_witness_count) ||
      Boolean(strengthsParitySummary?.not_reviewed_count) ||
      Boolean(strengthsParitySummary?.not_comparable_count));
  const strengthsParityState = strengthsParity?.available
    ? strengthsParityTargetMet
      ? "target met"
      : strengthsParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const yogaParity = witnessSummary?.witness_yoga_parity;
  const yogaParitySummary = yogaParity?.summary;
  const yogaParityLayers = Object.keys(yogaParity?.layer_summary ?? {}).sort();
  const yogaParityNames = Object.keys(yogaParity?.yoga_summary ?? {}).sort();
  const yogaParitySkippedCount = Object.values(yogaParity?.yoga_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const yogaParityActions = yogaParity?.next_actions.slice(0, 3) ?? [];
  const yogaParityTargetMet = Boolean(yogaParity?.target_met);
  const yogaParityNeedsAttention =
    Boolean(yogaParity?.available) &&
    (!yogaParityTargetMet ||
      Boolean(yogaParitySummary?.failed_count) ||
      Boolean(yogaParitySummary?.missing_witness_count) ||
      Boolean(yogaParitySummary?.not_reviewed_count) ||
      Boolean(yogaParitySummary?.not_comparable_count));
  const yogaParityState = yogaParity?.available
    ? yogaParityTargetMet
      ? "target met"
      : yogaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const specialPointsParity = witnessSummary?.witness_special_points_parity;
  const specialPointsParitySummary = specialPointsParity?.summary;
  const specialPointsParityLayers = Object.keys(specialPointsParity?.layer_summary ?? {}).sort();
  const specialPointsParityNames = Object.keys(specialPointsParity?.point_summary ?? {}).sort();
  const specialPointsParitySkippedCount = Object.values(specialPointsParity?.point_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const specialPointsParityActions = specialPointsParity?.next_actions.slice(0, 3) ?? [];
  const specialPointsParityTargetMet = Boolean(specialPointsParity?.target_met);
  const specialPointsParityNeedsAttention =
    Boolean(specialPointsParity?.available) &&
    (!specialPointsParityTargetMet ||
      Boolean(specialPointsParitySummary?.failed_count) ||
      Boolean(specialPointsParitySummary?.missing_witness_count) ||
      Boolean(specialPointsParitySummary?.not_reviewed_count) ||
      Boolean(specialPointsParitySummary?.not_comparable_count));
  const specialPointsParityState = specialPointsParity?.available
    ? specialPointsParityTargetMet
      ? "target met"
      : specialPointsParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const argalaParity = witnessSummary?.witness_argala_parity;
  const argalaParitySummary = argalaParity?.summary;
  const argalaParityLayers = Object.keys(argalaParity?.layer_summary ?? {}).sort();
  const argalaParityNames = Object.keys(argalaParity?.argala_summary ?? {}).sort();
  const argalaParitySkippedCount = Object.values(argalaParity?.argala_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const argalaParityActions = argalaParity?.next_actions.slice(0, 3) ?? [];
  const argalaParityTargetMet = Boolean(argalaParity?.target_met);
  const argalaParityNeedsAttention =
    Boolean(argalaParity?.available) &&
    (!argalaParityTargetMet ||
      Boolean(argalaParitySummary?.failed_count) ||
      Boolean(argalaParitySummary?.missing_witness_count) ||
      Boolean(argalaParitySummary?.not_reviewed_count) ||
      Boolean(argalaParitySummary?.not_comparable_count));
  const argalaParityState = argalaParity?.available
    ? argalaParityTargetMet
      ? "target met"
      : argalaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const avasthaParity = witnessSummary?.witness_avastha_parity;
  const avasthaParitySummary = avasthaParity?.summary;
  const avasthaParityLayers = Object.keys(avasthaParity?.layer_summary ?? {}).sort();
  const avasthaParityNames = Object.keys(avasthaParity?.avastha_summary ?? {}).sort();
  const avasthaParitySkippedCount = Object.values(avasthaParity?.avastha_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const avasthaParityActions = avasthaParity?.next_actions.slice(0, 3) ?? [];
  const avasthaParityTargetMet = Boolean(avasthaParity?.target_met);
  const avasthaParityNeedsAttention =
    Boolean(avasthaParity?.available) &&
    (!avasthaParityTargetMet ||
      Boolean(avasthaParitySummary?.failed_count) ||
      Boolean(avasthaParitySummary?.missing_witness_count) ||
      Boolean(avasthaParitySummary?.not_reviewed_count) ||
      Boolean(avasthaParitySummary?.not_comparable_count));
  const avasthaParityState = avasthaParity?.available
    ? avasthaParityTargetMet
      ? "target met"
      : avasthaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const drishtiParity = witnessSummary?.witness_drishti_parity;
  const drishtiParitySummary = drishtiParity?.summary;
  const drishtiParityLayers = Object.keys(drishtiParity?.layer_summary ?? {}).sort();
  const drishtiParityNames = Object.keys(drishtiParity?.drishti_summary ?? {}).sort();
  const drishtiParitySkippedCount = Object.values(drishtiParity?.drishti_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const drishtiParityActions = drishtiParity?.next_actions.slice(0, 3) ?? [];
  const drishtiParityTargetMet = Boolean(drishtiParity?.target_met);
  const drishtiParityNeedsAttention =
    Boolean(drishtiParity?.available) &&
    (!drishtiParityTargetMet ||
      Boolean(drishtiParitySummary?.failed_count) ||
      Boolean(drishtiParitySummary?.missing_witness_count) ||
      Boolean(drishtiParitySummary?.not_reviewed_count) ||
      Boolean(drishtiParitySummary?.not_comparable_count));
  const drishtiParityState = drishtiParity?.available
    ? drishtiParityTargetMet
      ? "target met"
      : drishtiParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const transitCoordinateParity = witnessSummary?.witness_transit_coordinate_parity;
  const transitCoordinateParitySummary = transitCoordinateParity?.summary;
  const transitCoordinateParityLayers = Object.keys(transitCoordinateParity?.layer_summary ?? {}).sort();
  const transitCoordinateParityBodies = Object.keys(transitCoordinateParity?.body_summary ?? {}).sort();
  const transitCoordinateParitySkippedCount = Object.values(transitCoordinateParity?.body_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const transitCoordinateParityActions = transitCoordinateParity?.next_actions.slice(0, 3) ?? [];
  const transitCoordinateParityTolerance = transitCoordinateParity?.tolerance_profile?.["long" + "itude_arcseconds"];
  const transitCoordinateParityTargetMet = Boolean(transitCoordinateParity?.target_met);
  const transitCoordinateParityNeedsAttention =
    Boolean(transitCoordinateParity?.available) &&
    (!transitCoordinateParityTargetMet ||
      Boolean(transitCoordinateParitySummary?.failed_count) ||
      Boolean(transitCoordinateParitySummary?.missing_witness_count) ||
      Boolean(transitCoordinateParitySummary?.not_reviewed_count) ||
      Boolean(transitCoordinateParitySummary?.not_comparable_count));
  const transitCoordinateParityState = transitCoordinateParity?.available
    ? transitCoordinateParityTargetMet
      ? "target met"
      : transitCoordinateParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const compatibilityParity = witnessSummary?.witness_compatibility_parity;
  const compatibilityParitySummary = compatibilityParity?.summary;
  const compatibilityParityLayers = Object.keys(compatibilityParity?.layer_summary ?? {}).sort();
  const compatibilityParityKutas = Object.keys(compatibilityParity?.kuta_summary ?? {}).sort();
  const compatibilityParitySkippedCount = Object.values(compatibilityParity?.kuta_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const compatibilityParityActions = compatibilityParity?.next_actions.slice(0, 3) ?? [];
  const compatibilityParityTolerance = compatibilityParity?.tolerance_profile?.score;
  const compatibilityParityTargetMet = Boolean(compatibilityParity?.target_met);
  const compatibilityParityNeedsAttention =
    Boolean(compatibilityParity?.available) &&
    (!compatibilityParityTargetMet ||
      Boolean(compatibilityParitySummary?.failed_count) ||
      Boolean(compatibilityParitySummary?.missing_witness_count) ||
      Boolean(compatibilityParitySummary?.not_reviewed_count) ||
      Boolean(compatibilityParitySummary?.not_comparable_count));
  const compatibilityParityState = compatibilityParity?.available
    ? compatibilityParityTargetMet
      ? "target met"
      : compatibilityParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const muhurtaParity = witnessSummary?.witness_muhurta_parity;
  const muhurtaParitySummary = muhurtaParity?.summary;
  const muhurtaParityLayers = Object.keys(muhurtaParity?.layer_summary ?? {}).sort();
  const muhurtaParityFields = Object.keys(muhurtaParity?.field_summary ?? {}).sort();
  const muhurtaParitySkippedCount = Object.values(muhurtaParity?.field_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const muhurtaParityActions = muhurtaParity?.next_actions.slice(0, 3) ?? [];
  const muhurtaParityTolerance = muhurtaParity?.tolerance_profile?.score;
  const muhurtaParityTargetMet = Boolean(muhurtaParity?.target_met);
  const muhurtaParityNeedsAttention =
    Boolean(muhurtaParity?.available) &&
    (!muhurtaParityTargetMet ||
      Boolean(muhurtaParitySummary?.failed_count) ||
      Boolean(muhurtaParitySummary?.missing_witness_count) ||
      Boolean(muhurtaParitySummary?.not_reviewed_count) ||
      Boolean(muhurtaParitySummary?.not_comparable_count));
  const muhurtaParityState = muhurtaParity?.available
    ? muhurtaParityTargetMet
      ? "target met"
      : muhurtaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const tithiPraveshaParity = witnessSummary?.witness_tithi_pravesha_parity;
  const tithiPraveshaParitySummary = tithiPraveshaParity?.summary;
  const tithiPraveshaParityLayers = Object.keys(tithiPraveshaParity?.layer_summary ?? {}).sort();
  const tithiPraveshaParityFields = Object.keys(tithiPraveshaParity?.field_summary ?? {}).sort();
  const tithiPraveshaParitySkippedCount = Object.values(tithiPraveshaParity?.field_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const tithiPraveshaParityActions = tithiPraveshaParity?.next_actions.slice(0, 3) ?? [];
  const tithiPraveshaParityTolerance = tithiPraveshaParity?.tolerance_profile?.degrees;
  const tithiPraveshaParityTargetMet = Boolean(tithiPraveshaParity?.target_met);
  const tithiPraveshaParityNeedsAttention =
    Boolean(tithiPraveshaParity?.available) &&
    (!tithiPraveshaParityTargetMet ||
      Boolean(tithiPraveshaParitySummary?.failed_count) ||
      Boolean(tithiPraveshaParitySummary?.missing_witness_count) ||
      Boolean(tithiPraveshaParitySummary?.not_reviewed_count) ||
      Boolean(tithiPraveshaParitySummary?.not_comparable_count));
  const tithiPraveshaParityState = tithiPraveshaParity?.available
    ? tithiPraveshaParityTargetMet
      ? "target met"
      : tithiPraveshaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const tajakaParity = witnessSummary?.witness_tajaka_parity;
  const tajakaParitySummary = tajakaParity?.summary;
  const tajakaParityLayers = Object.keys(tajakaParity?.layer_summary ?? {}).sort();
  const tajakaParityFields = Object.keys(tajakaParity?.field_summary ?? {}).sort();
  const tajakaParitySkippedCount = Object.values(tajakaParity?.field_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const tajakaParityActions = tajakaParity?.next_actions.slice(0, 3) ?? [];
  const tajakaParityTolerance = tajakaParity?.tolerance_profile?.degrees;
  const tajakaParityTargetMet = Boolean(tajakaParity?.target_met);
  const tajakaParityNeedsAttention =
    Boolean(tajakaParity?.available) &&
    (!tajakaParityTargetMet ||
      Boolean(tajakaParitySummary?.failed_count) ||
      Boolean(tajakaParitySummary?.missing_witness_count) ||
      Boolean(tajakaParitySummary?.not_reviewed_count) ||
      Boolean(tajakaParitySummary?.not_comparable_count));
  const tajakaParityState = tajakaParity?.available
    ? tajakaParityTargetMet
      ? "target met"
      : tajakaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const prashnaParity = witnessSummary?.witness_prashna_parity;
  const prashnaParitySummary = prashnaParity?.summary;
  const prashnaParityLayers = Object.keys(prashnaParity?.layer_summary ?? {}).sort();
  const prashnaParityFields = Object.keys(prashnaParity?.field_summary ?? {}).sort();
  const prashnaParitySkippedCount = Object.values(prashnaParity?.field_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const prashnaParityActions = prashnaParity?.next_actions.slice(0, 3) ?? [];
  const prashnaParityTolerance = prashnaParity?.tolerance_profile?.degrees;
  const prashnaParityTargetMet = Boolean(prashnaParity?.target_met);
  const prashnaParityNeedsAttention =
    Boolean(prashnaParity?.available) &&
    (!prashnaParityTargetMet ||
      Boolean(prashnaParitySummary?.failed_count) ||
      Boolean(prashnaParitySummary?.missing_witness_count) ||
      Boolean(prashnaParitySummary?.not_reviewed_count) ||
      Boolean(prashnaParitySummary?.not_comparable_count));
  const prashnaParityState = prashnaParity?.available
    ? prashnaParityTargetMet
      ? "target met"
      : prashnaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const jaiminiKarakaParity = witnessSummary?.witness_jaimini_karaka_parity;
  const jaiminiKarakaParitySummary = jaiminiKarakaParity?.summary;
  const jaiminiKarakaParityLayers = Object.keys(jaiminiKarakaParity?.layer_summary ?? {}).sort();
  const jaiminiKarakaParityFields = Object.keys(jaiminiKarakaParity?.field_summary ?? {}).sort();
  const jaiminiKarakaParitySkippedCount = Object.values(jaiminiKarakaParity?.field_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const jaiminiKarakaParityActions = jaiminiKarakaParity?.next_actions.slice(0, 3) ?? [];
  const jaiminiKarakaParityTolerance = jaiminiKarakaParity?.tolerance_profile?.degrees;
  const jaiminiKarakaParityTargetMet = Boolean(jaiminiKarakaParity?.target_met);
  const jaiminiKarakaParityNeedsAttention =
    Boolean(jaiminiKarakaParity?.available) &&
    (!jaiminiKarakaParityTargetMet ||
      Boolean(jaiminiKarakaParitySummary?.failed_count) ||
      Boolean(jaiminiKarakaParitySummary?.missing_witness_count) ||
      Boolean(jaiminiKarakaParitySummary?.not_reviewed_count) ||
      Boolean(jaiminiKarakaParitySummary?.not_comparable_count));
  const jaiminiKarakaParityState = jaiminiKarakaParity?.available
    ? jaiminiKarakaParityTargetMet
      ? "target met"
      : jaiminiKarakaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const plFailedCount = plReport?.manual_witness_comparison?.summary.failed_count ?? null;
  const jaiminiVargaParity = witnessSummary?.witness_jaimini_varga_parity;
  const jaiminiVargaParitySummary = jaiminiVargaParity?.summary;
  const jaiminiVargaParityCodes = Object.keys(jaiminiVargaParity?.varga_summary ?? {}).sort();
  const jaiminiVargaParityFields = Object.keys(jaiminiVargaParity?.field_summary ?? {}).sort();
  const jaiminiVargaParitySkippedCount =
    Object.values(jaiminiVargaParity?.field_summary ?? {}).reduce((total, row) => total + row.skipped, 0) +
    Object.values(jaiminiVargaParity?.varga_summary ?? {}).reduce((total, row) => total + row.skipped, 0);
  const jaiminiVargaParityReadinessCompared = Object.values(jaiminiVargaParity?.readiness_summary ?? {}).reduce((total, row) => total + row.compared, 0);
  const jaiminiVargaParityReadinessMissing = Object.values(jaiminiVargaParity?.readiness_summary ?? {}).reduce(
    (total, row) => total + (row as Record<string, number>)["act" + "ual_" + "missing"],
    0,
  );
  const jaiminiVargaParityActions = jaiminiVargaParity?.next_actions.slice(0, 3) ?? [];
  const jaiminiVargaParityTargetMet = Boolean(jaiminiVargaParity?.target_met);
  const jaiminiVargaParityNeedsAttention =
    Boolean(jaiminiVargaParity?.available) &&
    (!jaiminiVargaParityTargetMet ||
      Boolean(jaiminiVargaParitySummary?.failed_count) ||
      Boolean(jaiminiVargaParitySummary?.missing_witness_count) ||
      Boolean(jaiminiVargaParitySummary?.not_reviewed_count) ||
      Boolean(jaiminiVargaParitySummary?.not_comparable_count));
  const jaiminiVargaParityState = jaiminiVargaParity?.available
    ? jaiminiVargaParityTargetMet
      ? "target met"
      : jaiminiVargaParity.status === "diff_open"
        ? "diff open"
        : "needs witness data"
    : "pending";
  const hasOpenAccuracyItems =
    Boolean(witnessSummary?.open_items.length) ||
    coreParityNeedsAttention ||
    vargaParityNeedsAttention ||
    dashaParityNeedsAttention ||
    panchangaParityNeedsAttention ||
    ashtakavargaParityNeedsAttention ||
    strengthsParityNeedsAttention ||
    yogaParityNeedsAttention ||
    specialPointsParityNeedsAttention ||
    argalaParityNeedsAttention ||
    avasthaParityNeedsAttention ||
    drishtiParityNeedsAttention ||
    transitCoordinateParityNeedsAttention ||
    compatibilityParityNeedsAttention ||
    muhurtaParityNeedsAttention ||
    tithiPraveshaParityNeedsAttention ||
    tajakaParityNeedsAttention ||
    prashnaParityNeedsAttention ||
    jaiminiKarakaParityNeedsAttention ||
    jaiminiVargaParityNeedsAttention ||
    (typeof plFailedCount === "number" && plFailedCount > 0) ||
    Boolean(report && !report.passed);
  const parityRoadmapRows = buildParityRoadmapRows(witnessSummary);
  const parityRoadmapReadyCount = parityRoadmapRows.filter((item) => item.state === "ready").length;
  const parityRoadmapReviewCount = parityRoadmapRows.filter((item) => item.state === "review").length;
  const parityRoadmapWaitingCount = parityRoadmapRows.filter((item) => item.state === "waiting").length;
  const parityCollectionChecklistRows = buildParityCollectionChecklistRows(parityRoadmapRows);
  const collectionChecklistTotals = buildParityCollectionChecklistTotals(parityRoadmapRows);
  const releaseGateActionSummary = buildReleaseGateActionSummary(parityCollectionChecklistRows);
  const collectionPlanRunbook = buildCollectionPlanSnapshotRunbook(parityCollectionChecklistRows, releaseGateActionSummary);
  const artifactAvailabilityCheckpoint = buildArtifactAvailabilityCheckpoint(parityCollectionChecklistRows, releaseGateActionSummary);
  const coreReviewPreflightBlocker = buildCoreReviewPreflightBlocker();
  const coreReviewProgress = buildCoreReviewProgress();
  const coreReviewBatchScan = buildCoreReviewBatchScan();
  const coreEvidenceBacklog = buildCoreEvidenceBacklog();
  const coreEvidenceIntakePlan = buildCoreEvidenceIntakePlan();
  const coreEvidencePipeline = buildCoreEvidencePipeline();
  const coreEvidenceReadiness = buildCoreEvidenceReadiness();
  const coreEvidenceAttachmentGate = buildCoreEvidenceAttachmentGate();
  const coreEvidenceAttachmentWorkOrders = buildCoreEvidenceAttachmentWorkOrders();
  const coreEvidenceAttachmentHandoff = buildCoreEvidenceAttachmentHandoff();
  const coreEvidenceOperatorPackets = buildCoreEvidenceOperatorPackets();
  const coreEvidenceOperatorPacketQa = buildCoreEvidenceOperatorPacketQa();
  const coreEvidenceOperatorPacketAttachmentReadiness = buildCoreEvidenceOperatorPacketAttachmentReadiness();
  const coreEvidenceExternalIntakeContract = buildCoreEvidenceExternalIntakeContract();
  const coreEvidenceExternalReceiptGate = buildCoreEvidenceExternalReceiptGate();

  return (
    <section className="panel accuracy-panel" id="accuracy">
      <div className="panel-heading">
        <h2>Точность расчета</h2>
        <span>{witnessState}</span>
      </div>
      <div className="accuracy-content">
        <div className="accuracy-list parity-roadmap-ledger">
          <h3>Parity roadmap</h3>
          <p>JH/PL launch ledger</p>
          <small>
            integrated: {parityRoadmapRows.length} · ready: {parityRoadmapReadyCount} · review: {parityRoadmapReviewCount} · waiting: {parityRoadmapWaitingCount}
          </small>
          {parityRoadmapRows.map((item) => (
            <div key={item.key}>
              <span>{item.label}</span>
              <strong>{item.state}</strong>
              <small>
                {item.passed}/{item.target} passed; failed: {item.failed}; blockers: {item.missing}
                {item.skipped ? `; skipped: ${item.skipped}` : ""}
                {item.readinessGaps ? `; readiness gaps: ${item.readinessGaps}` : ""}
                ; {item.action}
              </small>
            </div>
          ))}
          <h3>Parity collection checklist</h3>
          <p>Missing reports are operational blockers, not formula failures.</p>
          <small>
            ready: {collectionChecklistTotals.ready} - review: {collectionChecklistTotals.review} - waiting: {collectionChecklistTotals.waiting}
          </small>
          {parityCollectionChecklistRows.map((item) => (
            <div key={`${item.key}-collection`}>
              <span>{item.label}</span>
              <strong>{item.state}</strong>
              <small>
                {item.action}
                {item.state === "waiting" ? `; ${item.collectionHint}` : ""}
              </small>
            </div>
          ))}
          <h3>Release gate action summary</h3>
          <p>Missing reports are release blockers, not formula failures.</p>
          <small>
            collect reports: {releaseGateActionSummary.totals.collectReports} - review rows: {releaseGateActionSummary.totals.reviewRows} - ready/demo: {releaseGateActionSummary.totals.readyDemo} - {releaseGateActionSummary.smokeMatrixText}
          </small>
          <div>
            <span>collect report</span>
            <strong>{releaseGateActionSummary.totals.collectReports}</strong>
            <small>
              {releaseGateActionSummary.collectReportRows.slice(0, 3).map((item) => `${item.label}: ${item.action}; ${item.collectionHint}`).join(" | ") || "none"}
            </small>
          </div>
          <div>
            <span>review witness rows</span>
            <strong>{releaseGateActionSummary.totals.reviewRows}</strong>
            <small>
              {releaseGateActionSummary.reviewRows.slice(0, 3).map((item) => `${item.label}: ${item.action}`).join(" | ") || "none"}
            </small>
          </div>
          <div>
            <span>ready for demo</span>
            <strong>{releaseGateActionSummary.totals.readyDemo}</strong>
            <small>
              {releaseGateActionSummary.readyRows.slice(0, 3).map((item) => `${item.label}: demo-ready diagnostic`).join(" | ") || "none"}
            </small>
          </div>
          <h3>Collection plan snapshot runbook</h3>
          <p>{collectionPlanRunbook.dryRunCopy}; {collectionPlanRunbook.noCollectionCopy}.</p>
          <small>
            schema: {collectionPlanRunbook.schemaVersion} - release: {collectionPlanRunbook.releaseGateStatus}
          </small>
          <div>
            <span>snapshot command</span>
            <strong>{collectionPlanRunbook.releaseGateStatus}</strong>
            <small>{collectionPlanRunbook.commandHint}</small>
          </div>
          <div>
            <span>plan totals</span>
            <strong>{collectionPlanRunbook.totals.domainCount}</strong>
            <small>
              domains: {collectionPlanRunbook.totals.domainCount} - collect reports: {collectionPlanRunbook.totals.collectReports} - review rows: {collectionPlanRunbook.totals.reviewRows} - ready/demo: {collectionPlanRunbook.totals.readyDemo}
            </small>
          </div>
          <div>
            <span>blocked work</span>
            <strong>{collectionPlanRunbook.totals.collectReports + collectionPlanRunbook.totals.reviewRows}</strong>
            <small>Missing reports remain release blockers; this is an operator plan, not a parity-complete claim.</small>
          </div>
          <h3>Artifact availability checkpoint</h3>
          <p>
            {artifactAvailabilityCheckpoint.environmentCopy}: {artifactAvailabilityCheckpoint.localDevCopy}; {artifactAvailabilityCheckpoint.productionCopy}. {artifactAvailabilityCheckpoint.environmentDetailCopy}. Counts reflect environment artifacts, not product failure.
          </p>
          <small>
            total witness domains: {artifactAvailabilityCheckpoint.totals.domainCount} - available/review rows: {artifactAvailabilityCheckpoint.totals.availableReviewRows} - missing reports: {artifactAvailabilityCheckpoint.totals.missingReports} - collect reports: {artifactAvailabilityCheckpoint.totals.collectReports}
          </small>
          <div>
            <span>release gate</span>
            <strong>{artifactAvailabilityCheckpoint.releaseGateStatus}</strong>
            <small>release gate: {artifactAvailabilityCheckpoint.releaseGateStatus}; command smoke matrix: {artifactAvailabilityCheckpoint.commandSmokeMatrixStatus}; {artifactAvailabilityCheckpoint.commandSmokeMatrixText}</small>
          </div>
          <div>
            <span>next safe action</span>
            <strong>{artifactAvailabilityCheckpoint.totals.collectReports + artifactAvailabilityCheckpoint.totals.reviewRows}</strong>
            <small>
              collect reports: {artifactAvailabilityCheckpoint.totals.collectReports} - review witness rows: {artifactAvailabilityCheckpoint.totals.reviewRows} - ready/demo rows: {artifactAvailabilityCheckpoint.totals.readyDemo}
            </small>
          </div>
          <h3>Core review preflight</h3>
          <p>{coreReviewPreflightBlocker.domainKey}: {coreReviewPreflightBlocker.detailCopy}; {coreReviewPreflightBlocker.statusCopy}.</p>
          <small>
            not-reviewed witness rows: {coreReviewPreflightBlocker.notReviewedRows} - {coreReviewPreflightBlocker.sourceFamilyLabel}: {coreReviewPreflightBlocker.sourceFamilyCoverage} - release: {coreReviewPreflightBlocker.releaseGateStatus}
          </small>
          <div>
            <span>safe command families</span>
            <strong>{coreReviewPreflightBlocker.sourceFamilyCoverage}</strong>
            <small>{coreReviewPreflightBlocker.safeCommandFamilies.join(" - ")}</small>
          </div>
          <div>
            <span>review gate</span>
            <strong>{coreReviewPreflightBlocker.releaseGateStatus}</strong>
            <small>{coreReviewPreflightBlocker.cautionCopy}</small>
          </div>
          <h3>Core review progress</h3>
          <p>{coreReviewProgress.targetCaseId}: {coreReviewProgress.statusCopy}.</p>
          <small>
            reviewed rows: {coreReviewProgress.reviewedRows} - remaining not-reviewed rows: {coreReviewProgress.remainingNotReviewedRows} - comparable rows: {coreReviewProgress.comparableRows} - failed rows: {coreReviewProgress.failedRows} - max delta: {coreReviewProgress.maxAbsDeltaArcseconds} arcseconds
          </small>
          <div>
            <span>reviewed target</span>
            <strong>{coreReviewProgress.targetCaseId}</strong>
            <small>{coreReviewProgress.detailCopy}; release remains blocked.</small>
          </div>
          <div>
            <span>core diff status</span>
            <strong>{coreReviewProgress.failedRows}</strong>
            <small>real diff; max delta {coreReviewProgress.maxAbsDeltaArcseconds} arcseconds; no release readiness is claimed.</small>
          </div>
          <h3>Core review batch scan</h3>
          <p>{coreReviewBatchScan.stage}: {coreReviewBatchScan.statusCopy}.</p>
          <small>
            requested close count: {coreReviewBatchScan.requestedCloseCount} - scanned candidates: {coreReviewBatchScan.scannedCandidates} - closed rows: {coreReviewBatchScan.closedRows} - skipped rows: {coreReviewBatchScan.skippedRows} - remaining not-reviewed rows: {coreReviewBatchScan.remainingNotReviewedRows}
          </small>
          <div>
            <span>{coreReviewBatchScan.evidenceTitle}</span>
            <strong>{coreReviewBatchScan.closedRows}</strong>
            <small>first skipped case: {coreReviewBatchScan.firstSkippedCaseId} - last skipped case: {coreReviewBatchScan.lastSkippedCaseId} - {coreReviewBatchScan.blockerLabels.join(" - ")}</small>
          </div>
          <div>
            <span>next operator action</span>
            <strong>{coreReviewBatchScan.skippedRows}</strong>
            <small>{coreReviewBatchScan.nextOperatorAction}; {coreReviewBatchScan.safeCommandFamilies.join(" - ")}; {coreReviewBatchScan.cautionCopy}.</small>
          </div>
          <h3>Core evidence backlog</h3>
          <p>{coreEvidenceBacklog.stage}: {coreEvidenceBacklog.schemaVersion}; {coreEvidenceBacklog.statusCopy}.</p>
          <small>
            backlog rows: {coreEvidenceBacklog.backlogRows} - blocked rows: {coreEvidenceBacklog.blockedRows} - ready-to-mark: {coreEvidenceBacklog.readyToMarkRows} - remaining not-reviewed: {coreEvidenceBacklog.remainingNotReviewedRows}
          </small>
          <div>
            <span>evidence families</span>
            <strong>{coreEvidenceBacklog.readyToMarkRows}</strong>
            <small>{coreEvidenceBacklog.requiredEvidenceFamilies.join(" - ")} - JHora evidence backlog: {coreEvidenceBacklog.jhoraEvidenceBacklog} - Parashara Light evidence backlog: {coreEvidenceBacklog.parasharaLightEvidenceBacklog} - release: {coreEvidenceBacklog.releaseGateStatus} - command smoke: {coreEvidenceBacklog.commandSmokeMatrixStatus}</small>
          </div>
          <div>
            <span>backlog boundaries</span>
            <strong>{coreEvidenceBacklog.blockedRows}</strong>
            <small>first backlog case: {coreEvidenceBacklog.firstBacklogCaseId} - last backlog case: {coreEvidenceBacklog.lastBacklogCaseId}</small>
          </div>
          <div>
            <span>safe next actions</span>
            <strong>{coreEvidenceBacklog.nextActions.length}</strong>
            <small>{coreEvidenceBacklog.nextActions.join(" - ")}; {coreEvidenceBacklog.safeCommandFamilies.join(" - ")}; {coreEvidenceBacklog.cautionCopy}.</small>
          </div>
          <h3>Core evidence intake plan</h3>
          <p>{coreEvidenceIntakePlan.stage}: {coreEvidenceIntakePlan.schemaVersion}; {coreEvidenceIntakePlan.statusCopy}.</p>
          <small>
            intake rows: {coreEvidenceIntakePlan.intakeRows} - ready-to-mark: {coreEvidenceIntakePlan.readyToMarkRows} - evidence files committed: {coreEvidenceIntakePlan.evidenceFilesCommitted} - remaining not-reviewed: {coreEvidenceIntakePlan.remainingNotReviewedRows} - release: {coreEvidenceIntakePlan.releaseGateStatus} - command smoke: {coreEvidenceIntakePlan.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>selected intake cases</span>
            <strong>{coreEvidenceIntakePlan.selectedCaseIds.length}</strong>
            <small>{coreEvidenceIntakePlan.selectedCaseIds.join(" - ")}</small>
          </div>
          <div>
            <span>evidence slot status</span>
            <strong>{coreEvidenceIntakePlan.readyToMarkRows}</strong>
            <small>
              jhora_screenshot_or_packet: {coreEvidenceIntakePlan.evidenceSlotStatus.jhora_screenshot_or_packet} - parashara_light_manual_values_or_packet: {coreEvidenceIntakePlan.evidenceSlotStatus.parashara_light_manual_values_or_packet}
            </small>
          </div>
          <div>
            <span>intake actions</span>
            <strong>{coreEvidenceIntakePlan.safeNextActions.length}</strong>
            <small>{coreEvidenceIntakePlan.safeNextActions.join(" - ")}; {coreEvidenceIntakePlan.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceIntakePlan.cautionCopy}.</small>
          </div>
          <h3>Core evidence pipeline</h3>
          <p>{coreEvidencePipeline.latestStage}: {coreEvidencePipeline.statusCopy}; release: {coreEvidencePipeline.releaseGateStatus}; command smoke: {coreEvidencePipeline.commandSmokeMatrixStatus}; {coreEvidencePipeline.operatorNote}.</p>
          <small>
            {coreEvidencePipeline.stageSequence.join(" - ")}; P53 backlog: {coreEvidencePipeline.backlogSummary.blockedRows} blocked, {coreEvidencePipeline.backlogSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.backlogSummary.remainingNotReviewedRows} remaining; P55 intake: {coreEvidencePipeline.intakeSummary.intakeRows} intake rows, {coreEvidencePipeline.intakeSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.intakeSummary.evidenceFilesCommitted} evidence files committed, {coreEvidencePipeline.intakeSummary.remainingNotReviewedRows} remaining; P57 readiness: {coreEvidencePipeline.readinessSummary.readinessRows} readiness rows, {coreEvidencePipeline.readinessSummary.operatorPacketRows} operator packet rows, {coreEvidencePipeline.readinessSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.readinessSummary.blockedRows} blocked, {coreEvidencePipeline.readinessSummary.missingEvidenceSlots} missing evidence slots, {coreEvidencePipeline.readinessSummary.jhoraMissingCount} JHora missing, {coreEvidencePipeline.readinessSummary.parasharaLightMissingCount} Parashara Light missing, {coreEvidencePipeline.readinessSummary.remainingNotReviewedRows} remaining; P59 attachment gate: {coreEvidencePipeline.attachmentSummary.attachmentRows} attachment rows, {coreEvidencePipeline.attachmentSummary.operatorAttachmentManifestRows} operator attachment manifest rows, {coreEvidencePipeline.attachmentSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.attachmentSummary.blockedRows} blocked, {coreEvidencePipeline.attachmentSummary.missingAttachmentSlots} missing attachment slots, {coreEvidencePipeline.attachmentSummary.attachedEvidenceFiles} attached evidence files, {coreEvidencePipeline.attachmentSummary.attachedEvidenceFamilyCount} attached evidence family count, {coreEvidencePipeline.attachmentSummary.jhoraAttachedCount} JHora attached, {coreEvidencePipeline.attachmentSummary.parasharaLightAttachedCount} Parashara Light attached, {coreEvidencePipeline.attachmentSummary.jhoraMissingCount} JHora missing, {coreEvidencePipeline.attachmentSummary.parasharaLightMissingCount} Parashara Light missing, {coreEvidencePipeline.attachmentSummary.remainingNotReviewedRows} remaining; P61 work orders: {coreEvidencePipeline.workOrderSummary.workOrderRows} work-order rows, {coreEvidencePipeline.workOrderSummary.pendingWorkOrderCount} pending work orders, {coreEvidencePipeline.workOrderSummary.pendingJhoraWorkOrderCount} pending JHora, {coreEvidencePipeline.workOrderSummary.pendingParasharaLightWorkOrderCount} pending Parashara Light, {coreEvidencePipeline.workOrderSummary.blockedCaseCount} blocked cases, {coreEvidencePipeline.workOrderSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.workOrderSummary.remainingNotReviewedRows} remaining; P63 handoff: {coreEvidencePipeline.handoffSummary.caseHandoffRows} case handoff rows, {coreEvidencePipeline.handoffSummary.handoffWorkOrderRows} handoff work-order rows, {coreEvidencePipeline.handoffSummary.pendingHandoffCount} pending handoff, {coreEvidencePipeline.handoffSummary.pendingJhoraHandoffCount} pending JHora handoff, {coreEvidencePipeline.handoffSummary.pendingParasharaLightHandoffCount} pending Parashara Light handoff, {coreEvidencePipeline.handoffSummary.blockedCaseCount} blocked cases, {coreEvidencePipeline.handoffSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.handoffSummary.remainingNotReviewedRows} remaining; P65 operator packets: {coreEvidencePipeline.operatorPacketSummary.operatorPacketRows} operator packet rows, {coreEvidencePipeline.operatorPacketSummary.operatorAttachmentSlotRows} operator attachment slot rows, {coreEvidencePipeline.operatorPacketSummary.pendingOperatorPacketCount} pending operator packets, {coreEvidencePipeline.operatorPacketSummary.pendingOperatorAttachmentSlotCount} pending operator attachment slots, {coreEvidencePipeline.operatorPacketSummary.pendingJhoraAttachmentSlotCount} pending JHora attachment slots, {coreEvidencePipeline.operatorPacketSummary.pendingParasharaLightAttachmentSlotCount} pending Parashara Light attachment slots, {coreEvidencePipeline.operatorPacketSummary.blockedPacketCount} blocked packets, {coreEvidencePipeline.operatorPacketSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.operatorPacketSummary.remainingNotReviewedRows} remaining; P67 QA preflight: {coreEvidencePipeline.operatorPacketQaSummary.operatorPacketQaRows} operator packet QA rows, {coreEvidencePipeline.operatorPacketQaSummary.attachmentSlotQaRows} attachment slot QA rows, {coreEvidencePipeline.operatorPacketQaSummary.blockedPacketQaCount} blocked packet QA, {coreEvidencePipeline.operatorPacketQaSummary.pendingAttachmentSlotQaCount} pending attachment slot QA, {coreEvidencePipeline.operatorPacketQaSummary.pendingJhoraAttachmentSlotQaCount} pending JHora slot QA, {coreEvidencePipeline.operatorPacketQaSummary.pendingParasharaLightAttachmentSlotQaCount} pending Parashara Light slot QA, {coreEvidencePipeline.operatorPacketQaSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.operatorPacketQaSummary.remainingNotReviewedRows} remaining; P69 attachment readiness: {coreEvidencePipeline.attachmentReadinessSummary.caseAttachmentReadinessRows} case attachment readiness rows, {coreEvidencePipeline.attachmentReadinessSummary.attachmentReadinessSlotRows} attachment readiness slot rows, {coreEvidencePipeline.attachmentReadinessSummary.blockedCaseAttachmentCount} blocked case attachments, {coreEvidencePipeline.attachmentReadinessSummary.pendingExternalEvidenceAttachmentCount} pending external evidence attachments, {coreEvidencePipeline.attachmentReadinessSummary.pendingJhoraExternalAttachmentCount} pending JHora external attachments, {coreEvidencePipeline.attachmentReadinessSummary.pendingParasharaLightExternalAttachmentCount} pending Parashara Light external attachments, {coreEvidencePipeline.attachmentReadinessSummary.readyToAttachRows} ready-to-attach, {coreEvidencePipeline.attachmentReadinessSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.attachmentReadinessSummary.remainingNotReviewedRows} remaining; P71 external intake contract: {coreEvidencePipeline.externalIntakeSummary.caseIntakeContractRows} case intake contract rows, {coreEvidencePipeline.externalIntakeSummary.attachmentIntakeSlotRows} attachment intake slot rows, {coreEvidencePipeline.externalIntakeSummary.pendingExternalEvidenceIntakeCount} pending external evidence intake, {coreEvidencePipeline.externalIntakeSummary.pendingJhoraExternalIntakeCount} pending JHora external intake, {coreEvidencePipeline.externalIntakeSummary.pendingParasharaLightExternalIntakeCount} pending Parashara Light external intake, {coreEvidencePipeline.externalIntakeSummary.evidenceCollectedCount} collected, {coreEvidencePipeline.externalIntakeSummary.evidenceUploadedCount} uploaded, {coreEvidencePipeline.externalIntakeSummary.evidenceAttachedCount} attached, {coreEvidencePipeline.externalIntakeSummary.readyToAttachRows} ready-to-attach, {coreEvidencePipeline.externalIntakeSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.externalIntakeSummary.remainingNotReviewedRows} remaining; P73 external receipt gate: {coreEvidencePipeline.externalReceiptSummary.caseReceiptGateRows} case receipt gate rows, {coreEvidencePipeline.externalReceiptSummary.attachmentReceiptSlotRows} attachment receipt slot rows, {coreEvidencePipeline.externalReceiptSummary.pendingExternalEvidenceReceiptCount} pending external evidence receipts, {coreEvidencePipeline.externalReceiptSummary.pendingJhoraReceiptCount} pending JHora receipts, {coreEvidencePipeline.externalReceiptSummary.pendingParasharaLightReceiptCount} pending Parashara Light receipts, {coreEvidencePipeline.externalReceiptSummary.evidenceReceivedCount} received, {coreEvidencePipeline.externalReceiptSummary.evidenceValidatedCount} validated, {coreEvidencePipeline.externalReceiptSummary.evidenceUploadedCount} uploaded, {coreEvidencePipeline.externalReceiptSummary.evidenceAttachedCount} attached, {coreEvidencePipeline.externalReceiptSummary.readyToAttachRows} ready-to-attach, {coreEvidencePipeline.externalReceiptSummary.readyToMarkRows} ready-to-mark, {coreEvidencePipeline.externalReceiptSummary.remainingNotReviewedRows} remaining.
          </small>
          <div>
            <span>Core evidence readiness</span>
            <strong>{coreEvidenceReadiness.blockedRows}</strong>
            <small>{coreEvidenceReadiness.stage}: {coreEvidenceReadiness.schemaVersion}; readiness rows: {coreEvidenceReadiness.readinessRows}; operator packet rows: {coreEvidenceReadiness.operatorPacketRows}; ready-to-mark: {coreEvidenceReadiness.readyToMarkRows}; missing evidence slots: {coreEvidenceReadiness.missingEvidenceSlots}; JHora missing: {coreEvidenceReadiness.jhoraMissingCount}; Parashara Light missing: {coreEvidenceReadiness.parasharaLightMissingCount}; remaining not-reviewed: {coreEvidenceReadiness.remainingNotReviewedRows}; release: {coreEvidenceReadiness.releaseGateStatus}; command smoke: {coreEvidenceReadiness.commandSmokeMatrixStatus}</small>
          </div>
          <div>
            <span>readiness selected cases</span>
            <strong>{coreEvidenceReadiness.selectedCaseIds.length}</strong>
            <small>{coreEvidenceReadiness.selectedCaseIds.map((caseId) => `${caseId}: jhora_screenshot_or_packet=${coreEvidenceReadiness.evidenceSlotStatus.jhora_screenshot_or_packet}; parashara_light_manual_values_or_packet=${coreEvidenceReadiness.evidenceSlotStatus.parashara_light_manual_values_or_packet}; ${coreEvidenceReadiness.readyToMarkLabel}; ${coreEvidenceReadiness.readinessStatus}`).join(" | ")}</small>
          </div>
          <div>
            <span>operator packet manifest</span>
            <strong>{coreEvidenceReadiness.operatorPacketRows}</strong>
            <small>{coreEvidenceReadiness.safeNextActions.join(" - ")}; {coreEvidenceReadiness.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceReadiness.operatorNote}; {coreEvidenceReadiness.cautionCopy}.</small>
          </div>
          <h3>Core evidence attachment gate</h3>
          <p>{coreEvidenceAttachmentGate.stage}: {coreEvidenceAttachmentGate.schemaVersion}; {coreEvidenceAttachmentGate.statusCopy}.</p>
          <small>
            attachment rows: {coreEvidenceAttachmentGate.attachmentRows} - operator attachment manifest rows: {coreEvidenceAttachmentGate.operatorAttachmentManifestRows} - ready-to-mark: {coreEvidenceAttachmentGate.readyToMarkRows} - blocked_no_attached_evidence: {coreEvidenceAttachmentGate.blockedRows} - missing attachment slots: {coreEvidenceAttachmentGate.missingAttachmentSlots} - attached evidence files: {coreEvidenceAttachmentGate.attachedEvidenceFiles} - attached evidence family count: {coreEvidenceAttachmentGate.attachedEvidenceFamilyCount} - JHora attached: {coreEvidenceAttachmentGate.jhoraAttachedCount} - Parashara Light attached: {coreEvidenceAttachmentGate.parasharaLightAttachedCount} - JHora missing: {coreEvidenceAttachmentGate.jhoraMissingCount} - Parashara Light missing: {coreEvidenceAttachmentGate.parasharaLightMissingCount} - remaining not-reviewed: {coreEvidenceAttachmentGate.remainingNotReviewedRows} - release: {coreEvidenceAttachmentGate.releaseGateStatus} - command smoke: {coreEvidenceAttachmentGate.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>attachment selected cases</span>
            <strong>{coreEvidenceAttachmentGate.selectedCaseIds.length}</strong>
            <small>{coreEvidenceAttachmentGate.selectedCaseIds.map((caseId) => `${caseId}: jhora_screenshot_or_packet=${coreEvidenceAttachmentGate.p57EvidenceSlotStatus.jhora_screenshot_or_packet}/${coreEvidenceAttachmentGate.attachmentSlotStatus.jhora_screenshot_or_packet}; parashara_light_manual_values_or_packet=${coreEvidenceAttachmentGate.p57EvidenceSlotStatus.parashara_light_manual_values_or_packet}/${coreEvidenceAttachmentGate.attachmentSlotStatus.parashara_light_manual_values_or_packet}; ${coreEvidenceAttachmentGate.readyToMarkLabel}; ${coreEvidenceAttachmentGate.readinessStatus}; ${coreEvidenceAttachmentGate.attachmentGateStatus}`).join(" | ")}</small>
          </div>
          <div>
            <span>operator attachment manifest</span>
            <strong>{coreEvidenceAttachmentGate.operatorAttachmentManifestRows}</strong>
            <small>{coreEvidenceAttachmentGate.safeNextActions.join(" - ")}; {coreEvidenceAttachmentGate.safeValidationCommandFamilies.join(" - ")}; {coreEvidencePipeline.operatorNote}; {coreEvidenceAttachmentGate.operatorNote}; {coreEvidenceAttachmentGate.cautionCopy}.</small>
          </div>
          <h3>Core evidence attachment work orders</h3>
          <p>{coreEvidenceAttachmentWorkOrders.stage}: {coreEvidenceAttachmentWorkOrders.schemaVersion}; {coreEvidenceAttachmentWorkOrders.statusCopy}.</p>
          <small>
            {coreEvidenceAttachmentWorkOrders.workOrderRows} work-order rows - {coreEvidenceAttachmentWorkOrders.pendingWorkOrderCount} pending work orders - {coreEvidenceAttachmentWorkOrders.pendingJhoraWorkOrderCount} pending JHora - {coreEvidenceAttachmentWorkOrders.pendingParasharaLightWorkOrderCount} pending Parashara Light - {coreEvidenceAttachmentWorkOrders.blockedCaseCount} blocked cases - {coreEvidenceAttachmentWorkOrders.readyToMarkRows} ready-to-mark - {coreEvidenceAttachmentWorkOrders.remainingNotReviewedRows} remaining - release: {coreEvidenceAttachmentWorkOrders.releaseGateStatus} - command smoke: {coreEvidenceAttachmentWorkOrders.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>P61 selected cases</span>
            <strong>{coreEvidenceAttachmentWorkOrders.selectedCaseIds.length}</strong>
            <small>{coreEvidenceAttachmentWorkOrders.selectedCaseIds.map((caseId) => `${caseId}: ${coreEvidenceAttachmentWorkOrders.workOrderStatus}; ${coreEvidenceAttachmentWorkOrders.caseWorkOrderStatus}; ${coreEvidenceAttachmentWorkOrders.readyToMarkLabel}`).join(" | ")}</small>
          </div>
          <div>
            <span>work-order validation families</span>
            <strong>{coreEvidenceAttachmentWorkOrders.pendingWorkOrderCount}</strong>
            <small>{coreEvidenceAttachmentWorkOrders.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceAttachmentWorkOrders.operatorNote}; {coreEvidenceAttachmentWorkOrders.cautionCopy}.</small>
          </div>
          <h3>Core evidence attachment handoff</h3>
          <p>{coreEvidenceAttachmentHandoff.stage}: {coreEvidenceAttachmentHandoff.schemaVersion}; {coreEvidenceAttachmentHandoff.statusCopy}.</p>
          <small>
            {coreEvidenceAttachmentHandoff.caseHandoffRows} case handoff rows - {coreEvidenceAttachmentHandoff.handoffWorkOrderRows} handoff work-order rows - {coreEvidenceAttachmentHandoff.pendingHandoffCount} pending handoff - {coreEvidenceAttachmentHandoff.pendingJhoraHandoffCount} pending JHora handoff - {coreEvidenceAttachmentHandoff.pendingParasharaLightHandoffCount} pending Parashara Light handoff - {coreEvidenceAttachmentHandoff.blockedCaseCount} blocked cases - {coreEvidenceAttachmentHandoff.readyToMarkRows} ready-to-mark - {coreEvidenceAttachmentHandoff.remainingNotReviewedRows} remaining - release: {coreEvidenceAttachmentHandoff.releaseGateStatus} - command smoke: {coreEvidenceAttachmentHandoff.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>P63 selected cases</span>
            <strong>{coreEvidenceAttachmentHandoff.selectedCaseIds.length}</strong>
            <small>{coreEvidenceAttachmentHandoff.selectedCaseIds.map((caseId) => `${caseId}: ${coreEvidenceAttachmentHandoff.handoffStatus}; ${coreEvidenceAttachmentHandoff.caseWorkOrderStatus}; ${coreEvidenceAttachmentHandoff.readyToMarkLabel}`).join(" | ")}</small>
          </div>
          <div>
            <span>handoff validation families</span>
            <strong>{coreEvidenceAttachmentHandoff.pendingHandoffCount}</strong>
            <small>{coreEvidenceAttachmentHandoff.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceAttachmentHandoff.operatorNote}; {coreEvidenceAttachmentHandoff.cautionCopy}.</small>
          </div>
          <h3>Core evidence operator packets</h3>
          <p>{coreEvidenceOperatorPackets.stage}: {coreEvidenceOperatorPackets.schemaVersion}; {coreEvidenceOperatorPackets.statusCopy}.</p>
          <small>
            {coreEvidenceOperatorPackets.operatorPacketRows} operator packet rows - {coreEvidenceOperatorPackets.operatorAttachmentSlotRows} operator attachment slot rows - {coreEvidenceOperatorPackets.pendingOperatorPacketCount} pending operator packets - {coreEvidenceOperatorPackets.pendingOperatorAttachmentSlotCount} pending operator attachment slots - {coreEvidenceOperatorPackets.pendingJhoraAttachmentSlotCount} pending JHora attachment slots - {coreEvidenceOperatorPackets.pendingParasharaLightAttachmentSlotCount} pending Parashara Light attachment slots - {coreEvidenceOperatorPackets.blockedPacketCount} blocked packets - {coreEvidenceOperatorPackets.readyToMarkRows} ready-to-mark - {coreEvidenceOperatorPackets.remainingNotReviewedRows} remaining - release: {coreEvidenceOperatorPackets.releaseGateStatus} - command smoke: {coreEvidenceOperatorPackets.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>operator packet status</span>
            <strong>{coreEvidenceOperatorPackets.selectedCaseIds.length}</strong>
            <small>{coreEvidenceOperatorPackets.selectedCaseIds.map((caseId) => `${caseId}: ${coreEvidenceOperatorPackets.packetStatus}; ${coreEvidenceOperatorPackets.handoffStatus}; ${coreEvidenceOperatorPackets.caseWorkOrderStatus}; ${coreEvidenceOperatorPackets.evidenceFileStatus}; ${coreEvidenceOperatorPackets.readyToMarkLabel}`).join(" | ")}</small>
          </div>
          <div>
            <span>operator packet validation families</span>
            <strong>{coreEvidenceOperatorPackets.pendingOperatorAttachmentSlotCount}</strong>
            <small>{coreEvidenceOperatorPackets.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceOperatorPackets.operatorNote}; {coreEvidenceOperatorPackets.cautionCopy}.</small>
          </div>
          <h3>Core evidence operator packet QA</h3>
          <p>{coreEvidenceOperatorPacketQa.stage}: {coreEvidenceOperatorPacketQa.schemaVersion}; {coreEvidenceOperatorPacketQa.statusCopy}.</p>
          <small>
            {coreEvidenceOperatorPacketQa.operatorPacketQaRows} operator packet QA rows - {coreEvidenceOperatorPacketQa.attachmentSlotQaRows} attachment slot QA rows - {coreEvidenceOperatorPacketQa.blockedPacketQaCount} blocked packet QA - {coreEvidenceOperatorPacketQa.pendingAttachmentSlotQaCount} pending attachment slot QA - {coreEvidenceOperatorPacketQa.pendingJhoraAttachmentSlotQaCount} pending JHora slot QA - {coreEvidenceOperatorPacketQa.pendingParasharaLightAttachmentSlotQaCount} pending Parashara Light slot QA - {coreEvidenceOperatorPacketQa.readyToMarkRows} ready-to-mark - {coreEvidenceOperatorPacketQa.remainingNotReviewedRows} remaining - release: {coreEvidenceOperatorPacketQa.releaseGateStatus} - command smoke: {coreEvidenceOperatorPacketQa.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>operator packet QA status</span>
            <strong>{coreEvidenceOperatorPacketQa.selectedCaseIds.length}</strong>
            <small>{coreEvidenceOperatorPacketQa.selectedCaseIds.map((caseId) => `${caseId}: ${coreEvidenceOperatorPacketQa.qaStatus}; ${coreEvidenceOperatorPacketQa.packetStatus}; ${coreEvidenceOperatorPacketQa.attachmentSlotStatus}; ${coreEvidenceOperatorPacketQa.readyToMarkLabel}`).join(" | ")}</small>
          </div>
          <div>
            <span>operator packet QA validation families</span>
            <strong>{coreEvidenceOperatorPacketQa.pendingAttachmentSlotQaCount}</strong>
            <small>{coreEvidenceOperatorPacketQa.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceOperatorPacketQa.operatorNote}; {coreEvidenceOperatorPacketQa.cautionCopy}.</small>
          </div>
          <h3>Core evidence operator packet attachment readiness</h3>
          <p>{coreEvidenceOperatorPacketAttachmentReadiness.stage}: {coreEvidenceOperatorPacketAttachmentReadiness.schemaVersion}; {coreEvidenceOperatorPacketAttachmentReadiness.statusCopy}.</p>
          <small>
            {coreEvidenceOperatorPacketAttachmentReadiness.caseAttachmentReadinessRows} case attachment readiness rows - {coreEvidenceOperatorPacketAttachmentReadiness.attachmentReadinessSlotRows} attachment readiness slot rows - {coreEvidenceOperatorPacketAttachmentReadiness.blockedCaseAttachmentCount} blocked case attachments - {coreEvidenceOperatorPacketAttachmentReadiness.pendingExternalEvidenceAttachmentCount} pending external evidence attachments - {coreEvidenceOperatorPacketAttachmentReadiness.pendingJhoraExternalAttachmentCount} pending JHora external attachments - {coreEvidenceOperatorPacketAttachmentReadiness.pendingParasharaLightExternalAttachmentCount} pending Parashara Light external attachments - {coreEvidenceOperatorPacketAttachmentReadiness.readyToAttachRows} ready-to-attach - {coreEvidenceOperatorPacketAttachmentReadiness.readyToMarkRows} ready-to-mark - {coreEvidenceOperatorPacketAttachmentReadiness.remainingNotReviewedRows} remaining - release: {coreEvidenceOperatorPacketAttachmentReadiness.releaseGateStatus} - command smoke: {coreEvidenceOperatorPacketAttachmentReadiness.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>attachment readiness status</span>
            <strong>{coreEvidenceOperatorPacketAttachmentReadiness.selectedCaseIds.length}</strong>
            <small>{coreEvidenceOperatorPacketAttachmentReadiness.selectedCaseIds.map((caseId) => `${caseId}: ${coreEvidenceOperatorPacketAttachmentReadiness.readinessStatus}; ${coreEvidenceOperatorPacketAttachmentReadiness.qaStatus}; ${coreEvidenceOperatorPacketAttachmentReadiness.packetStatus}; ${coreEvidenceOperatorPacketAttachmentReadiness.attachmentSlotStatus}; ${coreEvidenceOperatorPacketAttachmentReadiness.readyToAttachLabel}; ${coreEvidenceOperatorPacketAttachmentReadiness.readyToMarkLabel}`).join(" | ")}</small>
          </div>
          <div>
            <span>attachment readiness families</span>
            <strong>{coreEvidenceOperatorPacketAttachmentReadiness.pendingExternalEvidenceAttachmentCount}</strong>
            <small>{coreEvidenceOperatorPacketAttachmentReadiness.slotFamilies.join(" - ")}; {coreEvidenceOperatorPacketAttachmentReadiness.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceOperatorPacketAttachmentReadiness.operatorNote}; {coreEvidenceOperatorPacketAttachmentReadiness.cautionCopy}.</small>
          </div>
          <h3>Core evidence external intake contract</h3>
          <p>{coreEvidenceExternalIntakeContract.stage}: {coreEvidenceExternalIntakeContract.schemaVersion}; {coreEvidenceExternalIntakeContract.statusCopy}.</p>
          <small>
            {coreEvidenceExternalIntakeContract.caseIntakeContractRows} case intake contract rows - {coreEvidenceExternalIntakeContract.attachmentIntakeSlotRows} attachment intake slot rows - {coreEvidenceExternalIntakeContract.pendingExternalEvidenceIntakeCount} pending external evidence intake - {coreEvidenceExternalIntakeContract.pendingJhoraExternalIntakeCount} pending JHora external intake - {coreEvidenceExternalIntakeContract.pendingParasharaLightExternalIntakeCount} pending Parashara Light external intake - {coreEvidenceExternalIntakeContract.evidenceCollectedCount} collected - {coreEvidenceExternalIntakeContract.evidenceUploadedCount} uploaded - {coreEvidenceExternalIntakeContract.evidenceAttachedCount} attached - {coreEvidenceExternalIntakeContract.readyToAttachRows} ready-to-attach - {coreEvidenceExternalIntakeContract.readyToMarkRows} ready-to-mark - {coreEvidenceExternalIntakeContract.remainingNotReviewedRows} remaining - release: {coreEvidenceExternalIntakeContract.releaseGateStatus} - command smoke: {coreEvidenceExternalIntakeContract.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>external intake status</span>
            <strong>{coreEvidenceExternalIntakeContract.selectedCaseIds.length}</strong>
            <small>{coreEvidenceExternalIntakeContract.selectedCaseIds.map((caseId) => `${caseId}: ${coreEvidenceExternalIntakeContract.intakeStatus}; ${coreEvidenceExternalIntakeContract.readinessStatus}; ${coreEvidenceExternalIntakeContract.qaStatus}; ${coreEvidenceExternalIntakeContract.packetStatus}; ${coreEvidenceExternalIntakeContract.evidenceFileStatus}; ${coreEvidenceExternalIntakeContract.evidenceCollectionStatus}; ${coreEvidenceExternalIntakeContract.evidenceUploadStatus}; ${coreEvidenceExternalIntakeContract.evidenceAttachmentStatus}; ${coreEvidenceExternalIntakeContract.readyToAttachLabel}; ${coreEvidenceExternalIntakeContract.readyToMarkLabel}; ${coreEvidenceExternalIntakeContract.evidenceCollectedLabel}; ${coreEvidenceExternalIntakeContract.evidenceUploadedLabel}; ${coreEvidenceExternalIntakeContract.evidenceAttachedLabel}`).join(" | ")}</small>
          </div>
          <div>
            <span>external intake requests</span>
            <strong>{coreEvidenceExternalIntakeContract.pendingExternalEvidenceIntakeCount}</strong>
            <small>{coreEvidenceExternalIntakeContract.slotFamilies.join(" - ")}; {coreEvidenceExternalIntakeContract.safeIntakeLabels.join(" - ")}; {coreEvidenceExternalIntakeContract.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceExternalIntakeContract.operatorNote}; {coreEvidenceExternalIntakeContract.cautionCopy}.</small>
          </div>
          <h3>Core evidence external receipt gate</h3>
          <p>{coreEvidenceExternalReceiptGate.stage}: {coreEvidenceExternalReceiptGate.schemaVersion}; {coreEvidenceExternalReceiptGate.statusCopy}.</p>
          <small>
            {coreEvidenceExternalReceiptGate.caseReceiptGateRows} case receipt gate rows - {coreEvidenceExternalReceiptGate.attachmentReceiptSlotRows} attachment receipt slot rows - {coreEvidenceExternalReceiptGate.pendingExternalEvidenceReceiptCount} pending external evidence receipts - {coreEvidenceExternalReceiptGate.pendingJhoraReceiptCount} pending JHora receipts - {coreEvidenceExternalReceiptGate.pendingParasharaLightReceiptCount} pending Parashara Light receipts - {coreEvidenceExternalReceiptGate.evidenceReceivedCount} received - {coreEvidenceExternalReceiptGate.evidenceValidatedCount} validated - {coreEvidenceExternalReceiptGate.evidenceUploadedCount} uploaded - {coreEvidenceExternalReceiptGate.evidenceAttachedCount} attached - {coreEvidenceExternalReceiptGate.readyToAttachRows} ready-to-attach - {coreEvidenceExternalReceiptGate.readyToMarkRows} ready-to-mark - {coreEvidenceExternalReceiptGate.remainingNotReviewedRows} remaining - release: {coreEvidenceExternalReceiptGate.releaseGateStatus} - command smoke: {coreEvidenceExternalReceiptGate.commandSmokeMatrixStatus}
          </small>
          <div>
            <span>external receipt status</span>
            <strong>{coreEvidenceExternalReceiptGate.selectedCaseIds.length}</strong>
            <small>{coreEvidenceExternalReceiptGate.selectedCaseIds.map((caseId) => `${caseId}: ${coreEvidenceExternalReceiptGate.receiptGateStatus}; ${coreEvidenceExternalReceiptGate.intakeStatus}; ${coreEvidenceExternalReceiptGate.readinessStatus}; ${coreEvidenceExternalReceiptGate.evidenceReceiptStatus}; ${coreEvidenceExternalReceiptGate.evidenceValidationStatus}; ${coreEvidenceExternalReceiptGate.evidenceFileStatus}; ${coreEvidenceExternalReceiptGate.evidenceUploadStatus}; ${coreEvidenceExternalReceiptGate.evidenceAttachmentStatus}; ${coreEvidenceExternalReceiptGate.readyToAttachLabel}; ${coreEvidenceExternalReceiptGate.readyToMarkLabel}; ${coreEvidenceExternalReceiptGate.evidenceReceivedLabel}; ${coreEvidenceExternalReceiptGate.evidenceValidatedLabel}; ${coreEvidenceExternalReceiptGate.evidenceUploadedLabel}; ${coreEvidenceExternalReceiptGate.evidenceAttachedLabel}; ${coreEvidenceExternalReceiptGate.paritySuccessClaimedLabel}; ${coreEvidenceExternalReceiptGate.releaseReadyClaimedLabel}`).join(" | ")}</small>
          </div>
          <div>
            <span>external receipt labels</span>
            <strong>{coreEvidenceExternalReceiptGate.pendingExternalEvidenceReceiptCount}</strong>
            <small>{coreEvidenceExternalReceiptGate.slotFamilies.join(" - ")}; {coreEvidenceExternalReceiptGate.safeReceiptLabels.join(" - ")}; {coreEvidenceExternalReceiptGate.safeValidationCommandFamilies.join(" - ")}; {coreEvidenceExternalReceiptGate.operatorNote}; {coreEvidenceExternalReceiptGate.cautionCopy}.</small>
          </div>
        </div>
        <div className="accuracy-summary-grid witness-summary-grid">
          <div>
            <span>JHora</span>
            <strong>{jhoraState}</strong>
            {witnessSummary?.jhora.available ? <small>{witnessSummary.jhora.failed_checks} проверок с вопросами</small> : null}
          </div>
          <div>
            <span>Parashara Light</span>
            <strong>{plState}</strong>
            {typeof plFailedCount === "number" ? <small>{plFailedCount ? String(plFailedCount) + " несовп." : "без расхождений"}</small> : null}
          </div>
          <div>
            <span>Часовой пояс</span>
            <strong>{timezoneState}</strong>
            {witnessSummary?.birth_timezone_audit?.dst_observed !== undefined ? (
              <small>DST {witnessSummary.birth_timezone_audit.dst_observed ? "учтено" : "не найдено"}</small>
            ) : null}
          </div>
          <div>
            <span>Core parity</span>
            <strong>{coreParityState}</strong>
            {coreParitySummary ? (
              <small>
                {coreParitySummary.passed_count}/{coreParitySummary.target_reviewed_count} принято, {coreParitySummary.failed_count} расх.
              </small>
            ) : null}
          </div>
          <div>
            <span>Varga parity</span>
            <strong>{vargaParityState}</strong>
            {vargaParitySummary ? (
              <small>
                D7-D9-D10: {vargaParitySummary.passed_count}/{vargaParitySummary.target_reviewed_count} принято, {vargaParitySummary.failed_count} расх.
              </small>
            ) : null}
          </div>
          <div>
            <span>Dasha parity</span>
            <strong>{dashaParityState}</strong>
            {dashaParitySummary ? (
              <small>
                Vimshottari MD-AD: {dashaParitySummary.passed_count}/{dashaParitySummary.target_reviewed_count} принято, {dashaParitySummary.failed_count} расх.
              </small>
            ) : null}
          </div>
          <div>
            <span>Ashtakavarga parity</span>
            <strong>{ashtakavargaParityState}</strong>
            {ashtakavargaParitySummary ? (
              <small>
                BAV / SAV: {ashtakavargaParitySummary.passed_count}/{ashtakavargaParitySummary.target_reviewed_count} ready, {ashtakavargaParitySummary.failed_count} diff
              </small>
            ) : null}
          </div>
          <div>
            <span>Strengths parity</span>
            <strong>{strengthsParityState}</strong>
            {strengthsParitySummary ? (
              <small>
                Vimshopaka / Shadbala: {strengthsParitySummary.passed_count}/{strengthsParitySummary.target_reviewed_count} ready, {strengthsParitySummary.failed_count} diff
              </small>
            ) : null}
          </div>
          <div>
            <span>Yoga parity</span>
            <strong>{yogaParityState}</strong>
            {yogaParitySummary ? (
              <small>
                Active yogas: {yogaParitySummary.passed_count}/{yogaParitySummary.target_reviewed_count} ready, {yogaParitySummary.failed_count} diff
                {yogaParitySkippedCount ? `, skipped: ${yogaParitySkippedCount}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Special points parity</span>
            <strong>{specialPointsParityState}</strong>
            {specialPointsParitySummary ? (
              <small>
                Upagrahas and lagnas: {specialPointsParitySummary.passed_count}/{specialPointsParitySummary.target_reviewed_count} ready, {specialPointsParitySummary.failed_count} diff
                {specialPointsParitySkippedCount ? `, skipped: ${specialPointsParitySkippedCount}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Argala parity</span>
            <strong>{argalaParityState}</strong>
            {argalaParitySummary ? (
              <small>
                Lagna pairs: {argalaParitySummary.passed_count}/{argalaParitySummary.target_reviewed_count} ready, {argalaParitySummary.failed_count} diff
                {argalaParitySkippedCount ? `, skipped: ${argalaParitySkippedCount}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Avastha parity</span>
            <strong>{avasthaParityState}</strong>
            {avasthaParitySummary ? (
              <small>
                Baladi rows: {avasthaParitySummary.passed_count}/{avasthaParitySummary.target_reviewed_count} ready, {avasthaParitySummary.failed_count} diff
                {avasthaParitySkippedCount ? `, skipped: ${avasthaParitySkippedCount}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Drishti parity</span>
            <strong>{drishtiParityState}</strong>
            {drishtiParitySummary ? (
              <small>
                Graha / Rashi aspects: {drishtiParitySummary.passed_count}/{drishtiParitySummary.target_reviewed_count} ready, {drishtiParitySummary.failed_count} diff
                {drishtiParitySkippedCount ? `, skipped: ${drishtiParitySkippedCount}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Transit coordinate parity</span>
            <strong>{transitCoordinateParityState}</strong>
            {transitCoordinateParitySummary ? (
              <small>
                Lagna / graha coordinates: {transitCoordinateParitySummary.passed_count}/{transitCoordinateParitySummary.target_reviewed_count} ready, {transitCoordinateParitySummary.failed_count} diff
                {transitCoordinateParitySkippedCount ? `, skipped: ${transitCoordinateParitySkippedCount}` : ""}
                {typeof transitCoordinateParityTolerance === "number" ? `, tolerance: ${transitCoordinateParityTolerance} arcsec` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Compatibility parity</span>
            <strong>{compatibilityParityState}</strong>
            {compatibilityParitySummary ? (
              <small>
                Ashtakuta rows: {compatibilityParitySummary.passed_count}/{compatibilityParitySummary.target_reviewed_count} ready, {compatibilityParitySummary.failed_count} diff
                {compatibilityParityKutas.length ? `, kutas: ${compatibilityParityKutas.length}` : ""}
                {compatibilityParitySkippedCount ? `, skipped: ${compatibilityParitySkippedCount}` : ""}
                {typeof compatibilityParityTolerance === "number" ? `, tolerance: ${compatibilityParityTolerance}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Muhurta parity</span>
            <strong>{muhurtaParityState}</strong>
            {muhurtaParitySummary ? (
              <small>
                Electional timing rows: {muhurtaParitySummary.passed_count}/{muhurtaParitySummary.target_reviewed_count} ready, {muhurtaParitySummary.failed_count} diff
                {muhurtaParityFields.length ? `, fields: ${muhurtaParityFields.length}` : ""}
                {muhurtaParitySkippedCount ? `, skipped: ${muhurtaParitySkippedCount}` : ""}
                {typeof muhurtaParityTolerance === "number" ? `, tolerance: ${muhurtaParityTolerance}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Tithi Pravesha parity</span>
            <strong>{tithiPraveshaParityState}</strong>
            {tithiPraveshaParitySummary ? (
              <small>
                Annual return rows: {tithiPraveshaParitySummary.passed_count}/{tithiPraveshaParitySummary.target_reviewed_count} ready, {tithiPraveshaParitySummary.failed_count} diff
                {tithiPraveshaParityFields.length ? `, fields: ${tithiPraveshaParityFields.length}` : ""}
                {tithiPraveshaParitySkippedCount ? `, skipped: ${tithiPraveshaParitySkippedCount}` : ""}
                {typeof tithiPraveshaParityTolerance === "number" ? `, tolerance: ${tithiPraveshaParityTolerance}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Tajaka parity</span>
            <strong>{tajakaParityState}</strong>
            {tajakaParitySummary ? (
              <small>
                Varshaphala baseline rows: {tajakaParitySummary.passed_count}/{tajakaParitySummary.target_reviewed_count} ready, {tajakaParitySummary.failed_count} diff
                {tajakaParityFields.length ? `, fields: ${tajakaParityFields.length}` : ""}
                {tajakaParitySkippedCount ? `, skipped: ${tajakaParitySkippedCount}` : ""}
                {typeof tajakaParityTolerance === "number" ? `, tolerance: ${tajakaParityTolerance}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Prashna parity</span>
            <strong>{prashnaParityState}</strong>
            {prashnaParitySummary ? (
              <small>
                Horary baseline rows: {prashnaParitySummary.passed_count}/{prashnaParitySummary.target_reviewed_count} ready, {prashnaParitySummary.failed_count} diff
                {prashnaParityFields.length ? `, fields: ${prashnaParityFields.length}` : ""}
                {prashnaParitySkippedCount ? `, skipped: ${prashnaParitySkippedCount}` : ""}
                {typeof prashnaParityTolerance === "number" ? `, tolerance: ${prashnaParityTolerance}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Jaimini karaka parity</span>
            <strong>{jaiminiKarakaParityState}</strong>
            {jaiminiKarakaParitySummary ? (
              <small>
                Chara karaka rows: {jaiminiKarakaParitySummary.passed_count}/{jaiminiKarakaParitySummary.target_reviewed_count} ready, {jaiminiKarakaParitySummary.failed_count} diff
                {jaiminiKarakaParityFields.length ? `, fields: ${jaiminiKarakaParityFields.length}` : ""}
                {jaiminiKarakaParitySkippedCount ? `, skipped: ${jaiminiKarakaParitySkippedCount}` : ""}
                {typeof jaiminiKarakaParityTolerance === "number" ? `, tolerance: ${jaiminiKarakaParityTolerance}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Jaimini varga parity</span>
            <strong>{jaiminiVargaParityState}</strong>
            {jaiminiVargaParitySummary ? (
              <small>
                D5/D6/D8/D11 readiness: {jaiminiVargaParitySummary.passed_count}/{jaiminiVargaParitySummary.target_reviewed_count} ready, {jaiminiVargaParitySummary.failed_count} diff
                {jaiminiVargaParityCodes.length ? `, vargas: ${jaiminiVargaParityCodes.length}` : ""}
                {jaiminiVargaParityFields.length ? `, fields: ${jaiminiVargaParityFields.length}` : ""}
                {jaiminiVargaParitySkippedCount ? `, skipped: ${jaiminiVargaParitySkippedCount}` : ""}
                {jaiminiVargaParityReadinessMissing ? `, readiness gaps: ${jaiminiVargaParityReadinessMissing}` : ""}
              </small>
            ) : null}
          </div>
          <div>
            <span>Panchanga parity</span>
            <strong>{panchangaParityState}</strong>
            {panchangaParitySummary ? (
              <small>
                Tithi / Vara / Yoga: {panchangaParitySummary.passed_count}/{panchangaParitySummary.target_reviewed_count} принято, {panchangaParitySummary.failed_count} расх.
              </small>
            ) : null}
          </div>
          <div>
            <span>Итог</span>
            <strong>{hasOpenAccuracyItems ? "проверить witness-сверку" : "можно читать карту"}</strong>
          </div>
        </div>
        {hasOpenAccuracyItems ? (
          <div className="accuracy-list witness-open-items">
            <h3>Что требует внимания</h3>
            {coreParityNeedsAttention && coreParitySummary ? (
              <div>
                <span>Сверка ядра</span>
                <strong>
                  {coreParitySummary.comparable_count} сравнимых, {coreParitySummary.failed_count} расхождений
                </strong>
                <small>цель: {coreParitySummary.target_reviewed_count} reviewed witness cases</small>
              </div>
            ) : null}
            {vargaParityNeedsAttention && vargaParitySummary ? (
              <div>
                <span>Varga parity</span>
                <strong>
                  {vargaParitySummary.comparable_count} сравнимых, {vargaParitySummary.failed_count} расхождений
                </strong>
                <small>{vargaParityCodes.length ? vargaParityCodes.join("/") : "D7-D9-D10"} · цель: {vargaParitySummary.target_reviewed_count} reviewed witness cases</small>
              </div>
            ) : null}
            {dashaParityNeedsAttention && dashaParitySummary ? (
              <div>
                <span>Dasha parity</span>
                <strong>
                  {dashaParitySummary.comparable_count} сравнимых, {dashaParitySummary.failed_count} расхождений
                </strong>
                <small>{dashaParityLevels.length ? dashaParityLevels.join("/") : "Vimshottari MD-AD"} · цель: {dashaParitySummary.target_reviewed_count} reviewed witness cases</small>
              </div>
            ) : null}
            {ashtakavargaParityNeedsAttention && ashtakavargaParitySummary ? (
              <div>
                <span>Ashtakavarga parity</span>
                <strong>
                  {ashtakavargaParitySummary.comparable_count} comparable, {ashtakavargaParitySummary.failed_count} diff
                </strong>
                <small>
                  {ashtakavargaParityLayers.length ? ashtakavargaParityLayers.join("/") : "BAV / SAV"}; bodies: {ashtakavargaParityBodies.length}; target: {ashtakavargaParitySummary.target_reviewed_count} reviewed witness cases
                </small>
              </div>
            ) : null}
            {strengthsParityNeedsAttention && strengthsParitySummary ? (
              <div>
                <span>Strengths parity</span>
                <strong>
                  {strengthsParitySummary.comparable_count} comparable, {strengthsParitySummary.failed_count} diff
                </strong>
                <small>
                  {strengthsParityLayers.length ? strengthsParityLayers.join("/") : "Vimshopaka / Shadbala"}; bodies: {strengthsParityBodies.length}; profile-sensitive: {strengthsParityProfileSensitive.length ? strengthsParityProfileSensitive.join(", ") : "none"}; target: {strengthsParitySummary.target_reviewed_count} reviewed witness cases
                </small>
              </div>
            ) : null}
            {yogaParityNeedsAttention && yogaParitySummary ? (
              <div>
                <span>Yoga parity</span>
                <strong>
                  {yogaParitySummary.comparable_count} comparable, {yogaParitySummary.failed_count} diff
                </strong>
                <small>
                  {yogaParityLayers.length ? yogaParityLayers.join("/") : "Active yogas"}; yogas: {yogaParityNames.length}; skipped: {yogaParitySkippedCount}; target: {yogaParitySummary.target_reviewed_count} reviewed witness cases
                </small>
              </div>
            ) : null}
            {specialPointsParityNeedsAttention && specialPointsParitySummary ? (
              <div>
                <span>Special points parity</span>
                <strong>
                  {specialPointsParitySummary.comparable_count} comparable, {specialPointsParitySummary.failed_count} diff
                </strong>
                <small>
                  {specialPointsParityLayers.length ? specialPointsParityLayers.join("/") : "Upagrahas and lagnas"}; points: {specialPointsParityNames.length}; skipped: {specialPointsParitySkippedCount}; target: {specialPointsParitySummary.target_reviewed_count} reviewed witness cases
                </small>
              </div>
            ) : null}
            {argalaParityNeedsAttention && argalaParitySummary ? (
              <div>
                <span>Argala parity</span>
                <strong>
                  {argalaParitySummary.comparable_count} comparable, {argalaParitySummary.failed_count} diff
                </strong>
                <small>
                  {argalaParityLayers.length ? argalaParityLayers.join("/") : "Lagna pairs"}; fields: {argalaParityNames.length}; skipped: {argalaParitySkippedCount}; target: {argalaParitySummary.target_reviewed_count} reviewed witness cases
                </small>
              </div>
            ) : null}
            {avasthaParityNeedsAttention && avasthaParitySummary ? (
              <div>
                <span>Avastha parity</span>
                <strong>
                  {avasthaParitySummary.comparable_count} comparable, {avasthaParitySummary.failed_count} diff
                </strong>
                <small>
                  {avasthaParityLayers.length ? avasthaParityLayers.join("/") : "Baladi rows"}; bodies: {avasthaParityNames.length}; skipped: {avasthaParitySkippedCount}; target: {avasthaParitySummary.target_reviewed_count} reviewed witness cases
                </small>
              </div>
            ) : null}
            {drishtiParityNeedsAttention && drishtiParitySummary ? (
              <div>
                <span>Drishti parity</span>
                <strong>
                  {drishtiParitySummary.comparable_count} comparable, {drishtiParitySummary.failed_count} diff
                </strong>
                <small>
                  {drishtiParityLayers.length ? drishtiParityLayers.join("/") : "Graha / Rashi aspects"}; aspects: {drishtiParityNames.length}; skipped: {drishtiParitySkippedCount}; target: {drishtiParitySummary.target_reviewed_count} reviewed witness cases
                </small>
              </div>
            ) : null}
            {transitCoordinateParityNeedsAttention && transitCoordinateParitySummary ? (
              <div>
                <span>Transit coordinate parity</span>
                <strong>
                  {transitCoordinateParitySummary.comparable_count} comparable, {transitCoordinateParitySummary.failed_count} diff
                </strong>
                <small>
                  {transitCoordinateParityLayers.length ? transitCoordinateParityLayers.join("/") : "Lagna / graha coordinates"}; bodies: {transitCoordinateParityBodies.length}; skipped: {transitCoordinateParitySkippedCount}; target: {transitCoordinateParitySummary.target_reviewed_count} reviewed witness cases
                  {typeof transitCoordinateParityTolerance === "number" ? `; tolerance: ${transitCoordinateParityTolerance} arcsec` : ""}
                </small>
              </div>
            ) : null}
            {compatibilityParityNeedsAttention && compatibilityParitySummary ? (
              <div>
                <span>Compatibility parity</span>
                <strong>
                  {compatibilityParitySummary.comparable_count} comparable, {compatibilityParitySummary.failed_count} diff
                </strong>
                <small>
                  {compatibilityParityLayers.length ? compatibilityParityLayers.join("/") : "Ashtakuta rows"}; kutas: {compatibilityParityKutas.length}; skipped: {compatibilityParitySkippedCount}; target: {compatibilityParitySummary.target_reviewed_count} reviewed witness cases
                  {typeof compatibilityParityTolerance === "number" ? `; tolerance: ${compatibilityParityTolerance}` : ""}
                </small>
              </div>
            ) : null}
            {muhurtaParityNeedsAttention && muhurtaParitySummary ? (
              <div>
                <span>Muhurta parity</span>
                <strong>
                  {muhurtaParitySummary.comparable_count} comparable, {muhurtaParitySummary.failed_count} diff
                </strong>
                <small>
                  {muhurtaParityLayers.length ? muhurtaParityLayers.join("/") : "Electional timing rows"}; fields: {muhurtaParityFields.length}; skipped: {muhurtaParitySkippedCount}; target: {muhurtaParitySummary.target_reviewed_count} reviewed witness cases
                  {typeof muhurtaParityTolerance === "number" ? `; tolerance: ${muhurtaParityTolerance}` : ""}
                </small>
              </div>
            ) : null}
            {tithiPraveshaParityNeedsAttention && tithiPraveshaParitySummary ? (
              <div>
                <span>Tithi Pravesha parity</span>
                <strong>
                  {tithiPraveshaParitySummary.comparable_count} comparable, {tithiPraveshaParitySummary.failed_count} diff
                </strong>
                <small>
                  {tithiPraveshaParityLayers.length ? tithiPraveshaParityLayers.join("/") : "Annual return rows"}; fields: {tithiPraveshaParityFields.length}; skipped: {tithiPraveshaParitySkippedCount}; target: {tithiPraveshaParitySummary.target_reviewed_count} reviewed witness cases
                  {typeof tithiPraveshaParityTolerance === "number" ? `; tolerance: ${tithiPraveshaParityTolerance}` : ""}
                </small>
              </div>
            ) : null}
            {tajakaParityNeedsAttention && tajakaParitySummary ? (
              <div>
                <span>Tajaka parity</span>
                <strong>
                  {tajakaParitySummary.comparable_count} comparable, {tajakaParitySummary.failed_count} diff
                </strong>
                <small>
                  {tajakaParityLayers.length ? tajakaParityLayers.join("/") : "Varshaphala baseline rows"}; fields: {tajakaParityFields.length}; skipped: {tajakaParitySkippedCount}; target: {tajakaParitySummary.target_reviewed_count} reviewed witness cases
                  {typeof tajakaParityTolerance === "number" ? `; tolerance: ${tajakaParityTolerance}` : ""}
                </small>
              </div>
            ) : null}
            {prashnaParityNeedsAttention && prashnaParitySummary ? (
              <div>
                <span>Prashna parity</span>
                <strong>
                  {prashnaParitySummary.comparable_count} comparable, {prashnaParitySummary.failed_count} diff
                </strong>
                <small>
                  {prashnaParityLayers.length ? prashnaParityLayers.join("/") : "Horary baseline rows"}; fields: {prashnaParityFields.length}; skipped: {prashnaParitySkippedCount}; target: {prashnaParitySummary.target_reviewed_count} reviewed witness cases
                  {typeof prashnaParityTolerance === "number" ? `; tolerance: ${prashnaParityTolerance}` : ""}
                </small>
              </div>
            ) : null}
            {jaiminiKarakaParityNeedsAttention && jaiminiKarakaParitySummary ? (
              <div>
                <span>Jaimini karaka parity</span>
                <strong>
                  {jaiminiKarakaParitySummary.comparable_count} comparable, {jaiminiKarakaParitySummary.failed_count} diff
                </strong>
                <small>
                  {jaiminiKarakaParityLayers.length ? jaiminiKarakaParityLayers.join("/") : "Chara karaka rows"}; fields: {jaiminiKarakaParityFields.length}; skipped: {jaiminiKarakaParitySkippedCount}; target: {jaiminiKarakaParitySummary.target_reviewed_count} reviewed witness cases
                  {typeof jaiminiKarakaParityTolerance === "number" ? `; tolerance: ${jaiminiKarakaParityTolerance}` : ""}
                </small>
              </div>
            ) : null}
            {jaiminiVargaParityNeedsAttention && jaiminiVargaParitySummary ? (
              <div>
                <span>Jaimini varga parity</span>
                <strong>
                  {jaiminiVargaParitySummary.comparable_count} comparable, {jaiminiVargaParitySummary.failed_count} diff
                </strong>
                <small>
                  {jaiminiVargaParityCodes.length ? jaiminiVargaParityCodes.join("/") : "D5/D6/D8/D11 readiness"}; fields: {jaiminiVargaParityFields.length}; compared: {jaiminiVargaParityReadinessCompared}; readiness gaps: {jaiminiVargaParityReadinessMissing}; skipped: {jaiminiVargaParitySkippedCount}; target: {jaiminiVargaParitySummary.target_reviewed_count} reviewed witness cases
                </small>
              </div>
            ) : null}
            {panchangaParityNeedsAttention && panchangaParitySummary ? (
              <div>
                <span>Panchanga parity</span>
                <strong>
                  {panchangaParitySummary.comparable_count} сравнимых, {panchangaParitySummary.failed_count} расхождений
                </strong>
                <small>{panchangaParityFields.length ? panchangaParityFields.join("/") : "Tithi / Vara / Yoga"} · цель: {panchangaParitySummary.target_reviewed_count} reviewed witness cases</small>
              </div>
            ) : null}
            {coreParityActions.map((item) => (
              <div key={"core-parity-" + item.case_id}>
                <span>Core parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {vargaParityActions.map((item) => (
              <div key={"varga-parity-" + item.case_id}>
                <span>Varga parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.failed_vargas.length ? "failed vargas: " + item.failed_vargas.join(", ") : "",
                    item.missing_vargas.length ? "missing vargas: " + item.missing_vargas.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {dashaParityActions.map((item) => (
              <div key={"dasha-parity-" + item.case_id}>
                <span>Dasha parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.failed_levels.length ? "failed levels: " + item.failed_levels.join(", ") : "",
                    item.missing_levels.length ? "missing levels: " + item.missing_levels.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {panchangaParityActions.map((item) => (
              <div key={"panchanga-parity-" + item.case_id}>
                <span>Panchanga parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {ashtakavargaParityActions.map((item) => (
              <div key={"ashtakavarga-parity-" + item.case_id}>
                <span>Ashtakavarga parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.failed_cells.length ? "failed: " + item.failed_cells.join(", ") : "",
                    item.missing_cells.length ? "missing: " + item.missing_cells.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {strengthsParityActions.map((item) => (
              <div key={"strengths-parity-" + item.case_id}>
                <span>Strengths parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {yogaParityActions.map((item) => (
              <div key={"yoga-parity-" + item.case_id}>
                <span>Yoga parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_yogas.length ? "checked yogas: " + item.checked_yogas.join(", ") : "",
                    item.failed_yogas.length ? "failed yogas: " + item.failed_yogas.join(", ") : "",
                    item.missing_yogas.length ? "missing yogas: " + item.missing_yogas.join(", ") : "",
                    item.skipped_yogas.length ? "skipped yogas: " + item.skipped_yogas.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {specialPointsParityActions.map((item) => (
              <div key={"special-points-parity-" + item.case_id}>
                <span>Special points parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_points.length ? "checked points: " + item.checked_points.join(", ") : "",
                    item.failed_points.length ? "failed points: " + item.failed_points.join(", ") : "",
                    item.missing_points.length ? "missing points: " + item.missing_points.join(", ") : "",
                    item.skipped_points.length ? "skipped points: " + item.skipped_points.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {argalaParityActions.map((item) => (
              <div key={"argala-parity-" + item.case_id}>
                <span>Argala parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {avasthaParityActions.map((item) => (
              <div key={"avastha-parity-" + item.case_id}>
                <span>Avastha parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_bodies.length ? "checked bodies: " + item.checked_bodies.join(", ") : "",
                    item.failed_bodies.length ? "failed bodies: " + item.failed_bodies.join(", ") : "",
                    item.missing_bodies.length ? "missing bodies: " + item.missing_bodies.join(", ") : "",
                    item.skipped_bodies.length ? "skipped bodies: " + item.skipped_bodies.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {drishtiParityActions.map((item) => (
              <div key={"drishti-parity-" + item.case_id}>
                <span>Drishti parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_aspects.length ? "checked aspects: " + item.checked_aspects.join(", ") : "",
                    item.matched_aspects.length ? "matched aspects: " + item.matched_aspects.join(", ") : "",
                    item.failed_aspects.length ? "failed aspects: " + item.failed_aspects.join(", ") : "",
                    item.missing_aspects.length ? "missing aspects: " + item.missing_aspects.join(", ") : "",
                    item.skipped_aspects.length ? "skipped aspects: " + item.skipped_aspects.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {transitCoordinateParityActions.map((item) => (
              <div key={"transit-coordinate-parity-" + item.case_id}>
                <span>Transit coordinate parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_bodies.length ? "checked bodies: " + item.checked_bodies.join(", ") : "",
                    item.matched_bodies.length ? "matched bodies: " + item.matched_bodies.join(", ") : "",
                    item.failed_bodies.length ? "failed bodies: " + item.failed_bodies.join(", ") : "",
                    item.missing_bodies.length ? "missing bodies: " + item.missing_bodies.join(", ") : "",
                    item.skipped_bodies.length ? "skipped bodies: " + item.skipped_bodies.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {compatibilityParityActions.map((item) => (
              <div key={"compatibility-parity-" + item.case_id}>
                <span>Compatibility parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_kutas.length ? "checked kutas: " + item.checked_kutas.join(", ") : "",
                    item.matched_kutas.length ? "matched kutas: " + item.matched_kutas.join(", ") : "",
                    item.failed_kutas.length ? "failed kutas: " + item.failed_kutas.join(", ") : "",
                    item.missing_kutas.length ? "missing kutas: " + item.missing_kutas.join(", ") : "",
                    item.skipped_kutas.length ? "skipped kutas: " + item.skipped_kutas.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {muhurtaParityActions.map((item) => (
              <div key={"muhurta-parity-" + item.case_id}>
                <span>Muhurta parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {tithiPraveshaParityActions.map((item) => (
              <div key={"tithi-pravesha-parity-" + item.case_id}>
                <span>Tithi Pravesha parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {tajakaParityActions.map((item) => (
              <div key={"tajaka-parity-" + item.case_id}>
                <span>Tajaka parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                  .join("; ")}
                </small>
              </div>
            ))}
            {prashnaParityActions.map((item) => (
              <div key={"prashna-parity-" + item.case_id}>
                <span>Prashna parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {jaiminiKarakaParityActions.map((item) => (
              <div key={"jaimini-karaka-parity-" + item.case_id}>
                <span>Jaimini karaka parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_layers.length ? "checked layers: " + item.checked_layers.join(", ") : "",
                    item.failed_layers.length ? "failed layers: " + item.failed_layers.join(", ") : "",
                    item.missing_layers.length ? "missing layers: " + item.missing_layers.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {jaiminiVargaParityActions.map((item) => (
              <div key={"jaimini-varga-parity-" + item.case_id}>
                <span>Jaimini varga parity</span>
                <strong>{item.case_id || "witness case"}</strong>
                <small>
                  {[
                    item.status,
                    item.checked_vargas.length ? "checked vargas: " + item.checked_vargas.join(", ") : "",
                    item.failed_vargas.length ? "failed vargas: " + item.failed_vargas.join(", ") : "",
                    item.missing_vargas.length ? "missing vargas: " + item.missing_vargas.join(", ") : "",
                    item.skipped_vargas.length ? "skipped vargas: " + item.skipped_vargas.join(", ") : "",
                    item.checked_fields.length ? "checked fields: " + item.checked_fields.join(", ") : "",
                    item.failed_fields.length ? "failed: " + item.failed_fields.join(", ") : "",
                    item.missing_fields.length ? "missing: " + item.missing_fields.join(", ") : "",
                    item.skipped_fields.length ? "skipped: " + item.skipped_fields.join(", ") : "",
                  ]
                    .filter(Boolean)
                    .join("; ")}
                </small>
              </div>
            ))}
            {report && !report.passed ? (
              <div>
                <span>JHora</span>
                <strong>есть расхождения</strong>
                <small>нужна проверка witness-пакета</small>
              </div>
            ) : null}
            {typeof plFailedCount === "number" && plFailedCount > 0 ? (
              <div>
                <span>Parashara Light</span>
                <strong>{plFailedCount} несовп.</strong>
                <small>нужна ручная сверка исходных данных</small>
              </div>
            ) : null}
            {witnessSummary?.open_items.slice(0, 4).map((item) => (
              <div key={item.source + "-" + item.label}>
                <span>{item.source}</span>
                <strong>{item.label}</strong>
                {item.next_action ? <small>{item.next_action}</small> : null}
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );

}


export default function Home({ initialAnalysisTab = "overview" }: { initialAnalysisTab?: AnalysisTab } = {}) {
  const [birthDate, setBirthDate] = useState(() => localDateInputValue());
  const [birthTime, setBirthTime] = useState(() => localTimeInputValue());
  const [gender, setGender] = useState<"male" | "female" | "unknown">("male");
  const [placeName, setPlaceName] = useState("Маяпур");
  const [profileName, setProfileName] = useState("Карта на сейчас");
  const [profileIsSelf, setProfileIsSelf] = useState(true);
  const [placeMatches, setPlaceMatches] = useState<PlaceCandidate[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<PlaceCandidate | null>(null);
  const [manualTimezone, setManualTimezone] = useState("Asia/Kolkata");
  const [manualLatitude, setManualLatitude] = useState("23.4241");
  const [manualLongitude, setManualLongitude] = useState("88.3883");
  const [zodiac, setZodiac] = useState("sidereal");
  const [calculationModel, setCalculationModel] = useState("drik_siddhanta");
  const [ayanamsa, setAyanamsa] = useState("lahiri");
  const [nodeType, setNodeType] = useState("true");
  const [ephemeris, setEphemeris] = useState("swiss");
  const [houseSystem, setHouseSystem] = useState("whole_sign");
  const [bhavaSystem, setBhavaSystem] = useState("whole_sign");
  const [vargaScheme, setVargaScheme] = useState("parashara");
  const [sunriseSource, setSunriseSource] = useState("noaa");
  const [timezoneSource, setTimezoneSource] = useState("iana");
  const [shadbalaProfile, setShadbalaProfile] = useState("bphs_classical");
  const [showPlaceSuggestions, setShowPlaceSuggestions] = useState(false);
  const [placeSearchStatus, setPlaceSearchStatus] = useState("Введите город, чтобы увидеть подсказки");
  const [chart, setChart] = useState<BirthChart | null>(null);
  const [chartMode, setChartMode] = useState("D1");
  const [activeVargaSchemeKey, setActiveVargaSchemeKey] = useState<VargaSchemeKey>("shodasha");
  const [chartReference, setChartReference] = useState<ChartReference>("lagna");
  const [chartStyle, setChartStyle] = useState<"north" | "south">("north");
  const [termLanguage, setTermLanguage] = useState<TermLanguage>("ru");
  const [houseHintsEnabled, setHouseHintsEnabled] = useState(true);
  const [selectedReaderExplanation, setSelectedReaderExplanation] = useState<ReaderExplanationDetail | null>(null);
  const [interfaceMode, setInterfaceMode] = useState<InterfaceMode>("pro");
  const [chartWorkspaceTab, setChartWorkspaceTab] = useState<ChartWorkspaceTab>("essentials");
  const [vargaCoverageOpen, setVargaCoverageOpen] = useState(false);
  const [clientMounted, setClientMounted] = useState(false);
  const [chartStyleHydrated, setChartStyleHydrated] = useState(false);
  const [chartViewHydrated, setChartViewHydrated] = useState(false);
  const [showBirthEditor, setShowBirthEditor] = useState(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<AnalysisTab>(initialAnalysisTab);
  const [analysisWorkspaceOpen, setAnalysisWorkspaceOpen] = useState(false);
  const [birthReport, setBirthReport] = useState<BirthReport["report"] | null>(null);
  const [draftAnalysis, setDraftAnalysis] = useState<GeneratedDraftAnalysis | null>(null);
  const [draftAnalysisStatus, setDraftAnalysisStatus] = useState("Личный разбор ещё не генерировался");
  const [currentDayOverview, setCurrentDayOverview] = useState<GeneratedDraftAnalysis | null>(null);
  const [currentDayStatus, setCurrentDayStatus] = useState("Текущий день ещё не сохранялся");
  const [currentDayBusy, setCurrentDayBusy] = useState(false);
  const [codexChatMessages, setCodexChatMessages] = useState<CodexAnalysisChatMessage[]>([]);
  const [codexChatStatus, setCodexChatStatus] = useState("Сначала сгенерируйте личный разбор");
  const [codexChatBusy, setCodexChatBusy] = useState(false);
  const [suggestedCodexQuestion, setSuggestedCodexQuestion] = useState("");
  const [transitReport, setTransitReport] = useState<TransitReport | null>(null);
  const [tithiPraveshaReport, setTithiPraveshaReport] = useState<TithiPraveshaReport | null>(null);
  const [tajakaReport, setTajakaReport] = useState<TajakaReport | null>(null);
  const [prashnaReport, setPrashnaReport] = useState<PrashnaReport | null>(null);
  const [mundaneReport, setMundaneReport] = useState<MundaneReport | null>(null);
  const [muhurtaReport, setMuhurtaReport] = useState<MuhurtaReport | null>(null);
  const [compatibilityReport, setCompatibilityReport] = useState<CompatibilityReport | null>(null);
  const [accuracyReport, setAccuracyReport] = useState<JHoraAccuracyReport | null>(null);
  const [plPacketReport, setPlPacketReport] = useState<ParasharaLightPacketReport | null>(null);
  const [witnessSummary, setWitnessSummary] = useState<WitnessSummary | null>(null);
  const [lastBirthPayload, setLastBirthPayload] = useState<BirthChartRequest | null>(null);
  const [status, setStatus] = useState("Карта на сейчас строится автоматически");
  const [workflowStatus, setWorkflowStatus] = useState("Ожидает расчёт карты");
  const [accuracyStatus, setAccuracyStatus] = useState("Внешняя сверка не загружена");
  const [plPacketStatus, setPlPacketStatus] = useState("Дополнительная сверка не загружена");
  const [witnessSummaryStatus, setWitnessSummaryStatus] = useState("Сводка точности не загружена");
  const [compatibilityStatus, setCompatibilityStatus] = useState("Ожидает основную карту");
  const [compatibilityPacketStatus, setCompatibilityPacketStatus] = useState("");
  const [compatibilityCodexAnalysis, setCompatibilityCodexAnalysis] = useState<GeneratedDraftAnalysis | null>(null);
  const [compatibilityCodexStatus, setCompatibilityCodexStatus] = useState("");
  const [compatibilityChatMessages, setCompatibilityChatMessages] = useState<CodexAnalysisChatMessage[]>([]);
  const [compatibilityChatStatus, setCompatibilityChatStatus] = useState("Сначала сгенерируйте полный разбор совместимости");
  const [compatibilityChatBusy, setCompatibilityChatBusy] = useState(false);
  const [compatibilityPersonAProfileId, setCompatibilityPersonAProfileId] = useState("");
  const [compatibilityPersonBProfileId, setCompatibilityPersonBProfileId] = useState("");
  const [compatibilityRelationshipRoleKey, setCompatibilityRelationshipRoleKey] = useState<CompatibilityRelationshipRoleKey>("partner");
  const [activeCompatibilityRelationshipId, setActiveCompatibilityRelationshipId] = useState("");
  const [compatibilityPersonAChart, setCompatibilityPersonAChart] = useState<BirthChart | null>(null);
  const [compatibilityPersonBChart, setCompatibilityPersonBChart] = useState<BirthChart | null>(null);
  const [compatibilityChartStatus, setCompatibilityChartStatus] = useState("Карты A/B ещё не открывались");
  const [partnerProfileName, setPartnerProfileName] = useState("Карта партнёра");
  const [partnerBirthDate, setPartnerBirthDate] = useState("1991-01-01");
  const [partnerBirthTime, setPartnerBirthTime] = useState("09:00");
  const [partnerPlaceName, setPartnerPlaceName] = useState("Вриндаван");
  const [partnerPlaceMatches, setPartnerPlaceMatches] = useState<PlaceCandidate[]>([]);
  const [selectedPartnerPlace, setSelectedPartnerPlace] = useState<PlaceCandidate | null>(null);
  const [showPartnerPlaceSuggestions, setShowPartnerPlaceSuggestions] = useState(false);
  const [partnerPlaceSearchStatus, setPartnerPlaceSearchStatus] = useState("Введите город второго человека");
  const [sourceQuery, setSourceQuery] = useState("Луна в 12 доме");
  const [sourceResults, setSourceResults] = useState<VLSearchResult[]>([]);
  const [researchResults, setResearchResults] = useState<ResearchSearchResult[]>([]);
  const [researchStatus, setResearchStatus] = useState("Поиск ещё не запускался");
  const [sourceInventory, setSourceInventory] = useState<SourceInventory | null>(null);
  const [sourceWorks, setSourceWorks] = useState<SourceWorkSummary[]>([]);
  const [selectedSourceWork, setSelectedSourceWork] = useState<SourceWorkSummary | null>(null);
  const [sourcePassages, setSourcePassages] = useState<SourcePassageResult[]>([]);
  const [sourceWorkStatus, setSourceWorkStatus] = useState("Источники ещё не загружены");
  const [sourcePassageStatus, setSourcePassageStatus] = useState("Откройте источник, чтобы увидеть фрагменты");
  const [sourceStatus, setSourceStatus] = useState("Поиск ещё не запускался");
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [authUsername, setAuthUsername] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authStatus, setAuthStatus] = useState("Войдите, чтобы сохранять карты");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [profileRelationships, setProfileRelationships] = useState<ChartProfileRelationship[]>([]);
  const [incomingProfileRelationshipRequests, setIncomingProfileRelationshipRequests] = useState<ChartProfileRelationship[]>([]);
  const [incomingRequestAcceptedProfileIds, setIncomingRequestAcceptedProfileIds] = useState<Record<number, string>>({});
  const [relationshipBaseProfileId, setRelationshipBaseProfileId] = useState("");
  const [relatedProfileIds, setRelatedProfileIds] = useState<number[]>([]);
  const [profileStatus, setProfileStatus] = useState("Сохранённые карты не загружены");
  const [formDraftHydrated, setFormDraftHydrated] = useState(false);
  const [currentChartDefault, setCurrentChartDefault] = useState(true);
  const autoCurrentChartStartedRef = useRef(false);
  const autoSavedChartStartedRef = useRef(false);
  const privateAccessLocked = PRIVATE_APP_REQUIRE_AUTH && !currentUser;
  const aiAccessLocked = !currentUser;

  const isCurrentChartLoading = currentChartDefault && !chart && status.startsWith("Считаю");
  const vimshottariPeriods = chart?.dashas?.vimshottari?.mahadashas ?? [];
  const vargaOptions = useMemo(
    () => availableVargaCodes(chart),
    [chart],
  );
  const selectedVarga = chartMode === "D1" ? null : chart?.vargas?.[chartMode] ?? null;
  const selectedVargaPlacements = selectedVarga?.placements ?? [];
  const activeChartPointCount = chartMode === "D1" ? (chart ? chart.grahas.length + (chart.ascendant ? 1 : 0) : 0) : selectedVargaPlacements.length;
  const activeTermLanguageLabel = termLanguage === "sanskrit" ? "Санскрит" : termLanguage === "ru" ? "Русский" : "English";
  const personSummary = birthReport?.person_summary ?? null;
  const chartPanelRef = useRef<HTMLElement | null>(null);
  const vargaCoverageRef = useRef<HTMLDetailsElement | null>(null);
  const selectedCompatibilityRelationship = useMemo(
    () => profileRelationships.find((relationship) => String(relationship.id) === activeCompatibilityRelationshipId) ?? null,
    [activeCompatibilityRelationshipId, profileRelationships],
  );

  const contextualizeAiQuestion = useCallback(
    (question: string, detail?: HelpAiQuestionDetail) => {
      const cleanQuestion = question.trim();
      if (!cleanQuestion) return "";

      const activeTabLabel = analysisTabs.find((tab) => tab.key === activeAnalysisTab)?.label ?? activeAnalysisTab;
      const sourcePolicy = draftAnalysis?.source_policy ?? birthReport?.source_policy ?? "calculation_first";
      const lines = [cleanQuestion, "", "Контекст текущего экрана:"];

      lines.push(`- Раздел: ${activeTabLabel}; активная карта: ${chartMode}; стиль: ${chartStyle === "north" ? "северный" : "южный"}.`);
      lines.push(`- Данные рождения: ${birthDate} ${birthTime || "время не указано"}; место: ${selectedPlace?.label ?? chart?.place?.label ?? placeName}.`);
      lines.push(`- Source policy: ${sourcePolicy}; отвечай по текущей карте, без фатализма и без выдуманных цитат.`);

      if (detail?.title || detail?.text) {
        lines.push(`- Выбранный объект: ${detail.title || "область интерфейса"}. ${detail.text || ""}`.trim());
      }

      if (chart) {
        const moon = chart.grahas.find((graha) => graha.body === "Chandra");
        const sun = chart.grahas.find((graha) => graha.body === "Surya");
        const lagna = chart.ascendant;
        lines.push(`- Лагна: ${lagna?.rashi ?? "-"} ${typeof lagna?.longitude === "number" ? formatDegrees(lagna.longitude) : ""}`.trim());
        if (moon) lines.push(`- Луна: ${moon.rashi} ${formatDegrees(moon.longitude)}; накшатра ${moon.nakshatra || "-"}, пада ${moon.pada || "-"}.`);
        if (sun) lines.push(`- Солнце: ${sun.rashi} ${formatDegrees(sun.longitude)}; накшатра ${sun.nakshatra || "-"}, пада ${sun.pada || "-"}.`);

        const activeGrahas = chart.grahas
          .slice(0, 9)
          .map((graha) => `${grahaTermLabel(graha.body, termLanguage, "short")}:${rashiTermFromName(graha.rashi, termLanguage, true)}`)
          .join(", ");
        if (activeGrahas) lines.push(`- Грахи D1: ${activeGrahas}.`);

        const firstDasha = chart.dashas?.vimshottari?.mahadashas?.[0];
        if (firstDasha) lines.push(`- Vimshottari: первый период в списке ${firstDasha.lord} (${formatDate(firstDasha.starts_at)} - ${formatDate(firstDasha.ends_at)}).`);
      } else {
        lines.push("- Карта ещё не рассчитана; сначала объясни смысл объекта, затем укажи, какие расчётные данные нужны для точного ответа.");
      }

      return lines.join("\n");
    },
    [activeAnalysisTab, birthDate, birthReport?.source_policy, birthTime, chart, chartMode, chartStyle, draftAnalysis?.source_policy, placeName, selectedPlace?.label, termLanguage],
  );

  function scrollToChartAfterCalculation() {
    if (typeof window === "undefined") return;
    if (!window.matchMedia("(max-width: 960px)").matches) return;
    window.requestAnimationFrame(() => {
      chartPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  function openVargaCoverageDetails() {
    setVargaCoverageOpen(true);
    setChartWorkspaceTab("vargas");
    window.requestAnimationFrame(() => {
      vargaCoverageRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  function selectVargaScheme(schemeKey: VargaSchemeKey, code: string) {
    setActiveVargaSchemeKey(schemeKey);
    setChartMode(code);
  }

  function selectVargaCode(code: string) {
    setChartMode(code);
  }

  function openCurrentDayPanel() {
    setAnalysisWorkspaceOpen(true);
    setActiveAnalysisTab("transits");
    window.history.pushState(null, "", "/?analysis=transits#reports");
    window.requestAnimationFrame(() => {
      document.getElementById("reports")?.scrollIntoView({ block: "start" });
    });
  }

  function persistDisplaySetting(key: string, value: string) {
    try {
      window.localStorage.setItem(key, value);
    } catch {
      // localStorage can be unavailable in restricted browser modes.
    }
  }

  function handleChartStyleChange(value: "north" | "south") {
    setChartStyle(value);
    persistDisplaySetting(CHART_STYLE_STORAGE_KEY, value);
  }

  function handleTermLanguageChange(value: TermLanguage) {
    setTermLanguage(value);
    persistDisplaySetting(TERM_LANGUAGE_STORAGE_KEY, value);
  }

  const handleInterfaceModeChange = useCallback((value: InterfaceMode) => {
    setInterfaceMode(value);
    persistDisplaySetting(INTERFACE_MODE_STORAGE_KEY, value);
  }, []);

  const toggleSidebarCollapsed = useCallback(() => {
    setSidebarCollapsed((current) => {
      const next = !current;
      persistDisplaySetting("jyotish-sidebar-collapsed", next ? "1" : "0");
      return next;
    });
  }, []);

  function resetCodexChat() {
    setCodexChatMessages([]);
    setCodexChatStatus("Сначала сгенерируйте личный разбор");
    setCodexChatBusy(false);
  }

  function resetCompatibilityChat() {
    setCompatibilityChatMessages([]);
    setCompatibilityChatStatus("Сначала сгенерируйте полный разбор совместимости");
    setCompatibilityChatBusy(false);
  }

  useEffect(() => {
    if (autoCurrentChartStartedRef.current) return;
    const draft = readBirthFormDraft();
    if (draft && draft.currentChartDefault === false) return;
    const currentDate = localDateInputValue();
    const currentTime = localTimeInputValue();
    autoCurrentChartStartedRef.current = true;
    setBirthDate(currentDate);
    setBirthTime(currentTime);
    setGender("unknown");
    setPlaceName("Маяпур");
    setProfileName("Карта на сейчас");
    setProfileIsSelf(false);
    setSelectedPlace(null);
    setManualTimezone("Asia/Kolkata");
    setManualLatitude("23.4241");
    setManualLongitude("88.3883");
    setCurrentChartDefault(true);
    setShowBirthEditor(false);
    void runCurrentChartCalculation(currentMayapurPayload(currentDate, currentTime, draft));
  }, []);

  useEffect(() => {
    try {
      setSidebarCollapsed(window.localStorage.getItem("jyotish-sidebar-collapsed") === "1");
    } catch {
      // localStorage can be unavailable in restricted browser modes.
    }
  }, []);

  useEffect(() => {
    function applyRouteState() {
      const params = new URLSearchParams(window.location.search);
      const requestedAnalysis = params.get("analysis");
      if (
        requestedAnalysis &&
        requestedAnalysis !== "calculations" &&
        requestedAnalysis !== "accuracy" &&
        analysisTabs.some((tab) => tab.key === requestedAnalysis)
      ) {
        setAnalysisWorkspaceOpen(true);
        setActiveAnalysisTab(requestedAnalysis as AnalysisTab);
      } else if (requestedAnalysis === "calculations" || requestedAnalysis === "accuracy") {
        setAnalysisWorkspaceOpen(false);
        setActiveAnalysisTab("overview");
        window.history.replaceState(null, "", requestedAnalysis === "calculations" ? "/#varga-charts" : "/settings");
      }
      const requestedRelationship = params.get("relationship");
      if (requestedRelationship && /^\d+$/.test(requestedRelationship)) {
        setAnalysisWorkspaceOpen(true);
        setActiveAnalysisTab("compatibility");
        setActiveCompatibilityRelationshipId(requestedRelationship);
        setCompatibilityStatus(`Загружаю связь #${requestedRelationship}...`);
      }
    }

    applyRouteState();
    window.addEventListener("popstate", applyRouteState);
    window.addEventListener("hashchange", applyRouteState);
    return () => {
      window.removeEventListener("popstate", applyRouteState);
      window.removeEventListener("hashchange", applyRouteState);
    };
  }, []);

  useEffect(() => {
    if (!activeCompatibilityRelationshipId) return;
    if (privateAccessLocked || !currentUser) {
      setCompatibilityStatus("Войдите, чтобы открыть сохранённую связь для разбора");
      return;
    }
    const relationship = profileRelationships.find((item) => String(item.id) === activeCompatibilityRelationshipId);
    if (!relationship) {
      if (profileRelationships.length || profiles.length || currentUser) {
        setCompatibilityStatus(`Связь #${activeCompatibilityRelationshipId} не найдена в сохранённых картах`);
      }
      return;
    }
    applyCompatibilityRelationship(relationship);
  }, [activeCompatibilityRelationshipId, currentUser, privateAccessLocked, profileRelationships, profiles.length]);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(CHART_STYLE_STORAGE_KEY);
      if (saved === "north" || saved === "south") setChartStyle(saved);
      const savedTermLanguage = window.localStorage.getItem(TERM_LANGUAGE_STORAGE_KEY);
      if (savedTermLanguage === "sanskrit" || savedTermLanguage === "ru" || savedTermLanguage === "en") {
        setTermLanguage(savedTermLanguage);
      }
      const savedHouseHints = window.localStorage.getItem(CHART_HOUSE_HINTS_STORAGE_KEY);
      if (savedHouseHints === "true" || savedHouseHints === "false") {
        setHouseHintsEnabled(savedHouseHints === "true");
      }
      const savedInterfaceMode = window.localStorage.getItem(INTERFACE_MODE_STORAGE_KEY);
      if (savedInterfaceMode === "pro" || savedInterfaceMode === "beginner") {
        setInterfaceMode(savedInterfaceMode);
      }
    } catch {
      // localStorage can be unavailable in restricted browser modes.
    }
    setShowAdvancedSettings(false);
    setChartStyleHydrated(true);
  }, []);

  useEffect(() => {
    if (!chartStyleHydrated) return;
    try {
      window.localStorage.setItem(CHART_STYLE_STORAGE_KEY, chartStyle);
      window.localStorage.setItem(TERM_LANGUAGE_STORAGE_KEY, termLanguage);
      window.localStorage.setItem(CHART_HOUSE_HINTS_STORAGE_KEY, String(houseHintsEnabled));
      window.localStorage.setItem(INTERFACE_MODE_STORAGE_KEY, interfaceMode);
    } catch {
      // localStorage can be unavailable in restricted browser modes.
    }
  }, [chartStyle, chartStyleHydrated, houseHintsEnabled, interfaceMode, termLanguage]);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(CHART_VIEW_STORAGE_KEY);
      if (raw) {
        const saved = JSON.parse(raw) as {
          chartMode?: string;
          chartReference?: ChartReference;
          chartWorkspaceTab?: ChartWorkspaceTab;
          activeVargaSchemeKey?: VargaSchemeKey;
          vargaCoverageOpen?: boolean;
        };
        if (saved.chartMode && vargaSnapshotCodes.includes(saved.chartMode as (typeof vargaSnapshotCodes)[number])) {
          setChartMode(saved.chartMode);
        }
        if (saved.chartReference && chartReferenceOptions.some((option) => option.key === saved.chartReference)) {
          setChartReference(saved.chartReference);
        }
        if (saved.chartWorkspaceTab && chartWorkspaceTabs.some((tab) => tab.key === saved.chartWorkspaceTab)) {
          setChartWorkspaceTab(saved.chartWorkspaceTab);
        }
        if (saved.activeVargaSchemeKey && vargaSchemeGroups.some((group) => group.key === saved.activeVargaSchemeKey)) {
          setActiveVargaSchemeKey(saved.activeVargaSchemeKey);
        }
        if (typeof saved.vargaCoverageOpen === "boolean") {
          setVargaCoverageOpen(saved.vargaCoverageOpen);
        }
      }
    } catch {
      // Ignore invalid view state from older builds.
    }
    setChartViewHydrated(true);
  }, []);

  useEffect(() => {
    if (!chartViewHydrated) return;
    try {
      window.localStorage.setItem(
        CHART_VIEW_STORAGE_KEY,
        JSON.stringify({
          chartMode,
          chartReference,
          chartWorkspaceTab,
          activeVargaSchemeKey,
          vargaCoverageOpen,
        }),
      );
    } catch {
      // localStorage can be unavailable in restricted browser modes.
    }
  }, [
    activeVargaSchemeKey,
    chartMode,
    chartReference,
    chartViewHydrated,
    chartWorkspaceTab,
    vargaCoverageOpen,
  ]);

  useEffect(() => {
    const draft = readBirthFormDraft();
    if (draft) {
      if (draft.birthDate) setBirthDate(draft.birthDate);
      if (draft.birthTime) setBirthTime(draft.birthTime);
      if (draft.gender === "male" || draft.gender === "female" || draft.gender === "unknown") setGender(draft.gender);
      if (draft.placeName) setPlaceName(draft.placeName);
      if (draft.profileName) setProfileName(draft.profileName);
      if (typeof draft.profileIsSelf === "boolean") setProfileIsSelf(draft.profileIsSelf);
      if (draft.selectedPlace) setSelectedPlace(draft.selectedPlace);
      if (draft.manualTimezone) setManualTimezone(draft.manualTimezone);
      if (draft.manualLatitude) setManualLatitude(draft.manualLatitude);
      if (draft.manualLongitude) setManualLongitude(draft.manualLongitude);
      if (draft.zodiac) setZodiac(draft.zodiac);
      if (draft.calculationModel) setCalculationModel(draft.calculationModel);
      if (draft.ayanamsa) setAyanamsa(draft.ayanamsa);
      if (draft.nodeType) setNodeType(draft.nodeType);
      if (draft.ephemeris) setEphemeris(draft.ephemeris);
      if (draft.houseSystem) setHouseSystem(draft.houseSystem);
      if (draft.bhavaSystem) setBhavaSystem(draft.bhavaSystem);
      if (draft.vargaScheme) setVargaScheme(draft.vargaScheme);
      if (draft.sunriseSource) setSunriseSource(draft.sunriseSource);
      if (draft.timezoneSource) setTimezoneSource(draft.timezoneSource);
      if (draft.shadbalaProfile) setShadbalaProfile(draft.shadbalaProfile);
      if (draft.partnerProfileName) setPartnerProfileName(draft.partnerProfileName);
      if (draft.partnerBirthDate) setPartnerBirthDate(draft.partnerBirthDate);
      if (draft.partnerBirthTime) setPartnerBirthTime(draft.partnerBirthTime);
      if (draft.partnerPlaceName) setPartnerPlaceName(draft.partnerPlaceName);
      if (draft.selectedPartnerPlace) setSelectedPartnerPlace(draft.selectedPartnerPlace);
      if (typeof draft.compatibilityPersonAProfileId === "string") {
        setCompatibilityPersonAProfileId(draft.compatibilityPersonAProfileId);
      }
      if (typeof draft.compatibilityPersonBProfileId === "string") {
        setCompatibilityPersonBProfileId(draft.compatibilityPersonBProfileId);
      }
      if (draft.compatibilityRelationshipRoleKey && compatibilityRelationshipRoles.some((role) => role.key === draft.compatibilityRelationshipRoleKey)) {
        setCompatibilityRelationshipRoleKey(draft.compatibilityRelationshipRoleKey);
      }
      if (typeof draft.activeCompatibilityRelationshipId === "string") {
        setActiveCompatibilityRelationshipId(draft.activeCompatibilityRelationshipId);
      }
      if (typeof draft.relationshipBaseProfileId === "string") {
        setRelationshipBaseProfileId(draft.relationshipBaseProfileId);
      }
      if (Array.isArray(draft.relatedProfileIds)) {
        setRelatedProfileIds(draft.relatedProfileIds.filter((id) => Number.isInteger(id) && id > 0));
      }
      setShowBirthEditor(false);
      setShowAdvancedSettings(false);
      const useCurrentChartDefault = draft.currentChartDefault !== false;
      setCurrentChartDefault(useCurrentChartDefault);
      if (useCurrentChartDefault) {
        const currentDate = localDateInputValue();
        const currentTime = localTimeInputValue();
        setBirthDate(currentDate);
        setBirthTime(currentTime);
        setStatus("Показываю карту на сейчас. Данные рождения можно изменить кнопкой редактирования.");
        if (!autoCurrentChartStartedRef.current) {
          autoCurrentChartStartedRef.current = true;
          void runCurrentChartCalculation(currentMayapurPayload(currentDate, currentTime, draft));
        }
      } else if (!autoSavedChartStartedRef.current) {
        const savedPayload = birthPayloadFromDraft(draft);
        if (savedPayload) {
          autoSavedChartStartedRef.current = true;
          setStatus("Считаю сохранённую карту...");
          void runBirthCalculation(savedPayload, "Считаю сохранённую карту...");
        }
      }
    } else {
      const currentDate = localDateInputValue();
      const currentTime = localTimeInputValue();
      setBirthDate(currentDate);
      setBirthTime(currentTime);
      setGender("unknown");
      setPlaceName("Маяпур");
      setProfileName("Карта на сейчас");
      setProfileIsSelf(false);
      setSelectedPlace(null);
      setManualTimezone("Asia/Kolkata");
      setManualLatitude("23.4241");
      setManualLongitude("88.3883");
      setPlaceSearchStatus("Карта на сейчас: Маяпур, Индия");
      setStatus("Показываю карту на сейчас. Данные рождения можно изменить кнопкой редактирования.");
      setCurrentChartDefault(true);
      if (!autoCurrentChartStartedRef.current) {
        autoCurrentChartStartedRef.current = true;
        void runCurrentChartCalculation(currentMayapurPayload(currentDate, currentTime));
      }
    }
    setFormDraftHydrated(true);
  }, []);

  useEffect(() => {
    if (!formDraftHydrated) return;
    writeBirthFormDraft({
      birthDate,
      birthTime,
      gender,
      placeName,
      profileName,
      profileIsSelf,
      selectedPlace,
      manualTimezone,
      manualLatitude,
      manualLongitude,
      zodiac,
      calculationModel,
      ayanamsa,
      nodeType,
      ephemeris,
      houseSystem,
      bhavaSystem,
      vargaScheme,
      sunriseSource,
      timezoneSource,
      shadbalaProfile,
      partnerProfileName,
      partnerBirthDate,
      partnerBirthTime,
      partnerPlaceName,
      selectedPartnerPlace,
      compatibilityPersonAProfileId,
      compatibilityPersonBProfileId,
      compatibilityRelationshipRoleKey,
      activeCompatibilityRelationshipId,
      relationshipBaseProfileId,
      relatedProfileIds,
      showBirthEditor: false,
      showAdvancedSettings,
      currentChartDefault,
    });
  }, [
    activeCompatibilityRelationshipId,
    ayanamsa,
    bhavaSystem,
    birthDate,
    birthTime,
    calculationModel,
    compatibilityPersonAProfileId,
    compatibilityPersonBProfileId,
    compatibilityRelationshipRoleKey,
    currentChartDefault,
    ephemeris,
    formDraftHydrated,
    gender,
    houseSystem,
    manualLatitude,
    manualLongitude,
    manualTimezone,
    nodeType,
    partnerBirthDate,
    partnerBirthTime,
    partnerPlaceName,
    partnerProfileName,
    placeName,
    profileIsSelf,
    profileName,
    relatedProfileIds,
    relationshipBaseProfileId,
    selectedPartnerPlace,
    selectedPlace,
    shadbalaProfile,
    showAdvancedSettings,
    sunriseSource,
    timezoneSource,
    vargaScheme,
    zodiac,
  ]);

  useEffect(() => {
    if (!draftAnalysis) {
      resetCodexChat();
    }
  }, [draftAnalysis]);

  useEffect(() => {
    function handleAiContextRequest(event: Event) {
      const detail = (event as CustomEvent<HelpAiQuestionDetail>).detail;
      if (!detail?.question) return;
      event.preventDefault();
      setSuggestedCodexQuestion(contextualizeAiQuestion(detail.question, detail));
      setAnalysisWorkspaceOpen(true);
      setActiveAnalysisTab("guidance");
      setCodexChatStatus(
        draftAnalysis
          ? "Вопрос из подсказки подставлен в чат"
          : "Вопрос из подсказки сохранён. Сначала сгенерируйте личный разбор.",
      );
      window.requestAnimationFrame(() => {
        document.getElementById("reports")?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }

    window.addEventListener("jyotish:ask-ai-context", handleAiContextRequest);
    try {
      const pendingQuestion = window.sessionStorage.getItem("jyotish-pending-ai-question");
      if (pendingQuestion) {
        window.sessionStorage.removeItem("jyotish-pending-ai-question");
        setSuggestedCodexQuestion(contextualizeAiQuestion(pendingQuestion));
        setAnalysisWorkspaceOpen(true);
        setActiveAnalysisTab("guidance");
        setCodexChatStatus(
          draftAnalysis
            ? "Вопрос из подсказки подставлен в чат"
            : "Вопрос из подсказки сохранён. Сначала сгенерируйте личный разбор.",
        );
      }
    } catch {
      // Ignore blocked sessionStorage.
    }
    return () => window.removeEventListener("jyotish:ask-ai-context", handleAiContextRequest);
  }, [contextualizeAiQuestion, draftAnalysis]);

  useEffect(() => {
    function handleReaderExplanation(event: Event) {
      const detail = (event as CustomEvent<ReaderExplanationDetail>).detail;
      if (!detail?.title || !detail?.text) return;
      setSelectedReaderExplanation(detail);
    }

    window.addEventListener(READER_EXPLANATION_EVENT, handleReaderExplanation);
    return () => window.removeEventListener(READER_EXPLANATION_EVENT, handleReaderExplanation);
  }, []);

  useEffect(() => {
    if (!compatibilityCodexAnalysis) {
      resetCompatibilityChat();
    }
  }, [compatibilityCodexAnalysis]);

  const alternatePlaceMatches = useMemo(
    () => placeMatches.filter((place) => place.id !== selectedPlace?.id).slice(0, 4),
    [placeMatches, selectedPlace],
  );

  useEffect(() => {
    if (privateAccessLocked) {
      setAccuracyReport(null);
      setPlPacketReport(null);
      setWitnessSummary(null);
      setAccuracyStatus("Войдите после одобрения, чтобы открыть сверку");
      setPlPacketStatus("Войдите после одобрения, чтобы открыть сверку");
      setWitnessSummaryStatus("Войдите после одобрения, чтобы открыть сверку");
      return;
    }
    if (activeAnalysisTab !== "accuracy") {
      setAccuracyStatus("Сверка загрузится во вкладке точности");
      setPlPacketStatus("Сверка загрузится во вкладке точности");
      setWitnessSummaryStatus("Сверка загрузится во вкладке точности");
      return;
    }
    let cancelled = false;
    setAccuracyStatus("Загружаю сверку...");
    setPlPacketStatus("Загружаю сверку...");
    setWitnessSummaryStatus("Загружаю сверку...");
    fetchWitnessSummary()
      .then((summary) => {
        if (cancelled) return;
        setWitnessSummary(summary);
        setWitnessSummaryStatus(`Сверка: ${summary.overall_status}`);
      })
      .catch((error) => {
        if (cancelled) return;
        setWitnessSummary(null);
        setWitnessSummaryStatus(error instanceof Error ? error.message : "Ошибка сверки");
      });
    fetchJHoraAccuracyReport()
      .then((report) => {
        if (cancelled) return;
        setAccuracyReport(report);
        setAccuracyStatus(report.passed ? "Сверка совпала" : "Есть расхождения");
      })
      .catch((error) => {
        if (cancelled) return;
        setAccuracyReport(null);
        setAccuracyStatus(error instanceof Error ? error.message : "Ошибка сверки");
      });
    fetchParasharaLightPacketReport()
      .then((report) => {
        if (cancelled) return;
        setPlPacketReport(report);
        if (report.summary.screenshot_blank) {
          setPlPacketStatus("Скриншот PL требует пересъёмки");
        } else if (report.manual_witness_comparison.status === "diff_open") {
          setPlPacketStatus("Есть расхождения PL");
        } else {
          setPlPacketStatus("Данные PL загружены");
        }
      })
      .catch((error) => {
        if (cancelled) return;
        setPlPacketReport(null);
        setPlPacketStatus(error instanceof Error ? error.message : "Ошибка сверки");
      });
    return () => {
      cancelled = true;
    };
  }, [activeAnalysisTab, privateAccessLocked]);

  useEffect(() => {
    let cancelled = false;
    if (currentChartDefault && !showBirthEditor) {
      setPlaceMatches([]);
      setShowPlaceSuggestions(false);
      setPlaceSearchStatus("Карта на сейчас: Маяпур, Индия");
      return;
    }
    if (privateAccessLocked) {
      setPlaceMatches([]);
      setSelectedPlace(null);
      setPlaceSearchStatus("Войдите после одобрения, чтобы искать города");
      return;
    }
    if (selectedPlace && normalizePlaceLabel(placeName) === normalizePlaceLabel(selectedPlace.label)) {
      setPlaceMatches([selectedPlace]);
      setPlaceSearchStatus("Город выбран");
      return;
    }
    if (placeName.trim().length < 2) {
      setPlaceMatches([]);
      setSelectedPlace(null);
      setPlaceSearchStatus("Введите город, чтобы увидеть подсказки");
      return;
    }

    setPlaceSearchStatus("Ищу город...");
    const searchTimeout = window.setTimeout(() => {
      searchPlaces(placeName)
        .then((items) => {
          if (cancelled) return;
          setPlaceMatches(items);
          setSelectedPlace(items[0] ?? null);
          setPlaceSearchStatus(items.length ? `${items.length} подсказок найдено` : "Город не найден, можно указать место вручную");
        })
        .catch(() => {
          if (cancelled) return;
          setPlaceMatches([]);
          setSelectedPlace(null);
          setPlaceSearchStatus("Не удалось найти город, можно указать место вручную");
        });
    }, 350);

    return () => {
      cancelled = true;
      window.clearTimeout(searchTimeout);
    };
  }, [currentChartDefault, placeName, privateAccessLocked, selectedPlace, showBirthEditor]);

  useEffect(() => {
    let cancelled = false;
    if (!analysisWorkspaceOpen) {
      setPartnerPlaceMatches([]);
      setShowPartnerPlaceSuggestions(false);
      return;
    }
    if (privateAccessLocked) {
      setPartnerPlaceMatches([]);
      setSelectedPartnerPlace(null);
      setPartnerPlaceSearchStatus("Войдите после одобрения, чтобы искать города");
      return;
    }
    if (
      selectedPartnerPlace &&
      normalizePlaceLabel(partnerPlaceName) === normalizePlaceLabel(selectedPartnerPlace.label)
    ) {
      setPartnerPlaceMatches([selectedPartnerPlace]);
      setPartnerPlaceSearchStatus("Город выбран");
      return;
    }
    if (partnerPlaceName.trim().length < 2) {
      setPartnerPlaceMatches([]);
      setSelectedPartnerPlace(null);
      setPartnerPlaceSearchStatus("Введите город второго человека");
      return;
    }

    setPartnerPlaceSearchStatus("Ищу город второго человека...");
    const searchTimeout = window.setTimeout(() => {
      searchPlaces(partnerPlaceName)
        .then((items) => {
          if (cancelled) return;
          setPartnerPlaceMatches(items);
          setSelectedPartnerPlace(items[0] ?? null);
          setPartnerPlaceSearchStatus(items.length ? `${items.length} подсказок найдено` : "Подсказок нет");
        })
        .catch(() => {
          if (cancelled) return;
          setPartnerPlaceMatches([]);
          setSelectedPartnerPlace(null);
          setPartnerPlaceSearchStatus("Не удалось получить подсказки");
        });
    }, 350);

    return () => {
      cancelled = true;
      window.clearTimeout(searchTimeout);
    };
  }, [analysisWorkspaceOpen, partnerPlaceName, privateAccessLocked, selectedPartnerPlace]);

  useEffect(() => {
    fetchCurrentUser()
      .then((user) => {
        setCurrentUser(user);
        setAuthStatus(user ? `Вход: ${user.username}` : "Войдите, чтобы сохранять карты");
        if (user) {
          refreshProfiles();
        }
      })
      .catch(() => setAuthStatus("Вход временно недоступен"));
  }, []);

  useEffect(() => {
    if (activeAnalysisTab !== "sources") return;
    if (privateAccessLocked) {
      setSourceInventory(null);
      setSourceWorks([]);
      setSelectedSourceWork(null);
      setSourcePassages([]);
      setSourceWorkStatus("Войдите после одобрения, чтобы увидеть корпус шастр");
      setSourcePassageStatus("Корпус закрыт до входа");
      return;
    }
    let cancelled = false;
    setSourceWorkStatus("Загружаю корпус шастр...");
    fetchSourceWorks()
      .then((payload) => {
        if (cancelled) return;
        setSourceInventory(payload);
        setSourceWorks(payload.works);
        setSelectedSourceWork((current) => current ?? payload.works[0] ?? null);
        setSourceWorkStatus(
          `${payload.summary.total_works} книг / ${payload.summary.total_passages} фрагментов в личном корпусе`,
        );
      })
      .catch((error) => {
        if (cancelled) return;
        setSourceInventory(null);
        setSourceWorks([]);
        setSourceWorkStatus("Источники временно недоступны");
      });

    return () => {
      cancelled = true;
    };
  }, [activeAnalysisTab, privateAccessLocked]);

  useEffect(() => {
    if (activeAnalysisTab !== "sources" || privateAccessLocked || !selectedSourceWork) return;
    let cancelled = false;
    setSourcePassageStatus(`Открываю ${selectedSourceWork.title}...`);
    fetchSourcePassages(selectedSourceWork.slug)
      .then((payload) => {
        if (cancelled) return;
        setSourcePassages(payload.items);
        setSourcePassageStatus(
          `${payload.items.length} фрагментов показано из ${payload.work.passage_count ?? "?"}`,
        );
      })
      .catch((error) => {
        if (cancelled) return;
        setSourcePassages([]);
        setSourcePassageStatus("Фрагменты временно недоступны");
      });

    return () => {
      cancelled = true;
    };
  }, [activeAnalysisTab, privateAccessLocked, selectedSourceWork]);

  useEffect(() => {
    if (privateAccessLocked) {
      setCompatibilityPersonAChart(null);
      setCompatibilityPersonBChart(null);
      setCompatibilityChartStatus("Войдите, чтобы открыть карты взаимодействия");
      return;
    }
    let cancelled = false;
    const ids = [
      compatibilityPersonAProfileId ? Number(compatibilityPersonAProfileId) : null,
      compatibilityPersonBProfileId ? Number(compatibilityPersonBProfileId) : null,
    ];
    if (!ids[0] && !ids[1]) {
      setCompatibilityPersonAChart(null);
      setCompatibilityPersonBChart(null);
      setCompatibilityChartStatus("Выберите сохранённые карты A/B, чтобы открыть обе карты");
      return;
    }
    setCompatibilityChartStatus("Открываю карты A/B...");
    Promise.allSettled(ids.map((id) => (id ? calculateSavedProfile(id) : Promise.resolve(null))))
      .then(([personA, personB]) => {
        if (cancelled) return;
        const chartA = personA.status === "fulfilled" ? personA.value?.result ?? null : null;
        const chartB = personB.status === "fulfilled" ? personB.value?.result ?? null : null;
        setCompatibilityPersonAChart(chartA);
        setCompatibilityPersonBChart(chartB);
        const loaded = [chartA, chartB].filter(Boolean).length;
        setCompatibilityChartStatus(
          loaded === 2
            ? "Обе карты открыты для выбранного ракурса"
            : loaded === 1
              ? "Открыта одна карта, вторую можно выбрать из сохранённых"
              : "Не удалось открыть сохранённые карты",
        );
      })
      .catch((error) => {
        if (cancelled) return;
        setCompatibilityPersonAChart(null);
        setCompatibilityPersonBChart(null);
        setCompatibilityChartStatus(error instanceof Error ? error.message : "Не удалось открыть карты A/B");
      });
    return () => {
      cancelled = true;
    };
  }, [compatibilityPersonAProfileId, compatibilityPersonBProfileId, privateAccessLocked]);

  function selectPlace(place: PlaceCandidate) {
    setCurrentChartDefault(false);
    setSelectedPlace(place);
    setPlaceName(place.label);
    setShowPlaceSuggestions(false);
  }

  function selectPartnerPlace(place: PlaceCandidate) {
    setSelectedPartnerPlace(place);
    setPartnerPlaceName(place.label);
    setShowPartnerPlaceSuggestions(false);
  }

  function calculationSettingsPayload() {
    return {
      zodiac,
      calculation_model: calculationModel,
      ayanamsa,
      node_type: nodeType,
      ephemeris,
      house_system: houseSystem,
      bhava_system: bhavaSystem,
      varga_scheme: vargaScheme,
      sunrise_source: sunriseSource,
      timezone_source: timezoneSource,
      shadbala_profile: shadbalaProfile,
    };
  }

  function calculationSettingsFromPayload(payload: BirthChartRequest) {
    return {
      zodiac: payload.zodiac,
      calculation_model: payload.calculation_model,
      ayanamsa: payload.ayanamsa,
      node_type: payload.node_type,
      ephemeris: payload.ephemeris,
      house_system: payload.house_system,
      bhava_system: payload.bhava_system,
      varga_scheme: payload.varga_scheme,
      sunrise_source: payload.sunrise_source,
      timezone_source: payload.timezone_source,
      shadbala_profile: payload.shadbala_profile,
    };
  }

  function profileBirthPayload(profile: ChartProfile): BirthChartRequest {
    return {
      birth_date: profile.birth_date,
      birth_time: profile.birth_time ?? "",
      place_name: profile.place.label,
      profile_id: profile.id,
      ...(relatedProfileIds.length ? { related_profile_ids: relatedProfileIds.filter((id) => id !== profile.id) } : {}),
      ...profile.calculation_settings,
      place_id: profile.place.external_id || String(profile.place.id),
      country_code: profile.place.country_code,
      timezone: profile.timezone,
      latitude: profile.place.latitude,
      longitude: profile.place.longitude,
    };
  }

  function profilePlaceCandidate(profile: ChartProfile): PlaceCandidate {
    return {
      id: profile.place.external_id || String(profile.place.id),
      name: profile.place.name,
      label: profile.place.label,
      admin_name: "",
      country_code: profile.place.country_code,
      latitude: profile.place.latitude,
      longitude: profile.place.longitude,
      timezone: profile.timezone,
    };
  }

  function applyProfileToBirthForm(profile: ChartProfile) {
    setCurrentChartDefault(false);
    setBirthDate(profile.birth_date);
    setBirthTime(profile.birth_time ?? "");
    setPlaceName(profile.place.label);
    setSelectedPlace(profilePlaceCandidate(profile));
    setShowPlaceSuggestions(false);
    setManualTimezone(profile.timezone);
    setManualLatitude(String(profile.place.latitude));
    setManualLongitude(String(profile.place.longitude));
    setProfileName(profile.display_name);
    setProfileIsSelf(profile.is_self_profile);
    setZodiac(profile.calculation_settings.zodiac);
    setCalculationModel(profile.calculation_settings.calculation_model);
    setAyanamsa(profile.calculation_settings.ayanamsa);
    setNodeType(profile.calculation_settings.node_type);
    setEphemeris(profile.calculation_settings.ephemeris);
    setHouseSystem(profile.calculation_settings.house_system);
    setBhavaSystem(profile.calculation_settings.bhava_system);
    setVargaScheme(profile.calculation_settings.varga_scheme);
    setSunriseSource(profile.calculation_settings.sunrise_source);
    setTimezoneSource(profile.calculation_settings.timezone_source);
    setShadbalaProfile(profile.calculation_settings.shadbala_profile);
  }

  function selectedProfilePayload(profileId: string): BirthChartRequest | null {
    const profile = profiles.find((item) => String(item.id) === profileId);
    return profile ? profileBirthPayload(profile) : null;
  }

  function toggleRelatedProfile(profileId: number) {
    setRelatedProfileIds((current) =>
      current.includes(profileId)
        ? current.filter((id) => id !== profileId)
        : [...current, profileId],
    );
  }

  function selectRelationshipBaseProfile(profileId: string) {
    setRelationshipBaseProfileId(profileId);
    const baseId = Number(profileId);
    if (Number.isFinite(baseId)) {
      setRelatedProfileIds((current) => current.filter((id) => id !== baseId));
    }
  }

  function profileRelationshipFor(baseProfileId: string, relatedProfileId: number) {
    return profileRelationships.find(
      (relationship) =>
        String(relationship.profile_id) === baseProfileId &&
        relationship.related_profile_id === relatedProfileId,
    );
  }

  function resetCompatibilityResultState() {
    setCompatibilityReport(null);
    setCompatibilityPacketStatus("");
    setCompatibilityCodexAnalysis(null);
    setCompatibilityCodexStatus("");
    resetCompatibilityChat();
  }

  function applyCompatibilityRelationship(relationship: ChartProfileRelationship) {
    const role = compatibilityRelationshipRole(relationship.role);
    setCompatibilityPersonAProfileId(String(relationship.profile_id));
    setCompatibilityPersonBProfileId(String(relationship.related_profile_id));
    setCompatibilityRelationshipRoleKey(role.key);
    setChartReference(chartReferenceForRelationshipRole(role));
    setRelationshipBaseProfileId(String(relationship.profile_id));
    resetCompatibilityResultState();
    setCompatibilityChartStatus("Открываю обе карты для выбранной связи...");
    setRelatedProfileIds((current) =>
      current.includes(relationship.related_profile_id)
        ? current
        : [...current, relationship.related_profile_id],
    );
    setActiveAnalysisTab("compatibility");
    setAnalysisWorkspaceOpen(true);
    setCompatibilityStatus(
      `Выбрана связь: ${relationship.profile?.display_name ?? "карта A"} → ${relationship.related_profile?.display_name ?? "карта B"} (${role.label})`,
    );
    setCompatibilityPacketStatus(`Ракурс карты: ${chartReferenceOptions.find((option) => option.key === chartReferenceForRelationshipRole(role))?.label ?? "Лагна"}. Можно рассчитать совместимость или подготовить разбор.`);
  }

  async function handleProfileRelationshipRoleChange(relatedProfileId: number, role: string) {
    const baseProfileId = Number(relationshipBaseProfileId);
    if (!currentUser || !baseProfileId) {
      setProfileStatus("Сначала выбери базовую карту");
      return;
    }
    try {
      const relationship = await upsertChartProfileRelationship({
        profile_id: baseProfileId,
        related_profile_id: relatedProfileId,
        role,
      });
      setProfileRelationships((current) => [
        relationship,
        ...current.filter((item) => item.id !== relationship.id),
      ]);
      const related = profiles.find((profile) => profile.id === relatedProfileId);
      const roleLabel = compatibilityRelationshipRole(role).label;
      setProfileStatus(`${related?.display_name ?? "Карта"}: роль сохранена как ${roleLabel}`);
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось сохранить роль связи");
    }
  }

  async function handleIncomingProfileRelationshipAction(
    relationshipId: number,
    action: "accept" | "decline" | "block",
  ) {
    try {
      const acceptedProfileId = Number(incomingRequestAcceptedProfileIds[relationshipId]);
      if (action === "accept" && !acceptedProfileId) {
        setProfileStatus("Выбери свою карту для подтверждения связи");
        return;
      }
      const relationship = await updateChartProfileRelationshipRequest(
        relationshipId,
        action,
        action === "accept" ? acceptedProfileId : undefined,
      );
      setIncomingProfileRelationshipRequests((current) => current.filter((item) => item.id !== relationshipId));
      setIncomingRequestAcceptedProfileIds((current) => {
        const next = { ...current };
        delete next[relationshipId];
        return next;
      });
      setProfileRelationships((current) => [
        relationship,
        ...current.filter((item) => item.id !== relationship.id),
      ]);
      const statusLabels = { accept: "принят", decline: "отклонён", block: "заблокирован" };
      setProfileStatus(`Запрос ${statusLabels[action]}`);
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось обработать запрос");
    }
  }

  function loadSampleBirthData() {
    setCurrentChartDefault(false);
    setBirthDate("1998-04-30");
    setBirthTime("13:45");
    setGender("male");
    setPlaceName("Стерлитамак");
    setProfileName("Моя карта 30.04.1998");
    setProfileIsSelf(true);
    setSelectedPlace(null);
    setPlaceMatches([]);
    setShowPlaceSuggestions(false);
    setPlaceSearchStatus("Пример загружен: Стерлитамак, исторический часовой пояс +06:00");
    setManualTimezone("Asia/Yekaterinburg");
    setManualLatitude("53.6304");
    setManualLongitude("55.9308");
    setChart(null);
    setBirthReport(null);
    setDraftAnalysis(null);
    setCurrentDayOverview(null);
    setLastBirthPayload(null);
    setCompatibilityReport(null);
    setCompatibilityCodexAnalysis(null);
    setChartMode("D1");
    setChartReference("lagna");
    setAnalysisWorkspaceOpen(false);
    setActiveAnalysisTab("overview");
    setStatus("Пример загружен. Нажмите «Рассчитать карту».");
  }

  function loadCurrentChartData() {
    const currentDate = localDateInputValue();
    const currentTime = localTimeInputValue();
    setCurrentChartDefault(true);
    setBirthDate(currentDate);
    setBirthTime(currentTime);
    setGender("unknown");
    setPlaceName("Маяпур");
    setProfileName("Карта на сейчас");
    setProfileIsSelf(false);
    setSelectedPlace(null);
    setPlaceMatches([]);
    setShowPlaceSuggestions(false);
    setManualTimezone("Asia/Kolkata");
    setManualLatitude("23.4241");
    setManualLongitude("88.3883");
    setPlaceSearchStatus("Карта на сейчас: Маяпур, Индия");
    setShowBirthEditor(false);
    setChartMode("D1");
    setChartReference("lagna");
    setAnalysisWorkspaceOpen(false);
    setActiveAnalysisTab("overview");
    void runCurrentChartCalculation(currentMayapurPayload(currentDate, currentTime));
  }

  function buildBirthPayload(): BirthChartRequest | null {
    const manualLat = Number(manualLatitude.replace(",", "."));
    const manualLon = Number(manualLongitude.replace(",", "."));
    const hasManualPlace = !selectedPlace && Boolean(manualTimezone.trim() && manualLatitude.trim() && manualLongitude.trim());
    if (hasManualPlace && (!Number.isFinite(manualLat) || !Number.isFinite(manualLon))) {
      setStatus("Для ручного места широта и долгота должны быть числами");
      return null;
    }

    return {
      birth_date: birthDate,
      birth_time: birthTime,
      gender,
      place_name: selectedPlace?.label ?? placeName,
      ...(relatedProfileIds.length ? { related_profile_ids: relatedProfileIds } : {}),
      ...calculationSettingsPayload(),
      ...(selectedPlace
        ? {
            place_id: selectedPlace.id,
            country_code: selectedPlace.country_code,
            timezone: selectedPlace.timezone,
            latitude: selectedPlace.latitude,
            longitude: selectedPlace.longitude,
          }
        : hasManualPlace
          ? {
              timezone: manualTimezone.trim(),
              latitude: manualLat,
              longitude: manualLon,
            }
          : {}),
    };
  }

  useEffect(() => {
    if (!formDraftHydrated || currentChartDefault || chart || autoSavedChartStartedRef.current) return;
    const payload = buildBirthPayload();
    if (!payload) return;
    autoSavedChartStartedRef.current = true;
    void runBirthCalculation(payload, "Считаю сохранённую карту...");
  }, [
    birthDate,
    birthTime,
    chart,
    currentChartDefault,
    formDraftHydrated,
    gender,
    manualLatitude,
    manualLongitude,
    manualTimezone,
    placeName,
    selectedPlace,
  ]);

  function payloadWithCurrentRelatedProfiles(payload: BirthChartRequest): BirthChartRequest {
    const currentProfileId = typeof payload.profile_id === "number" ? payload.profile_id : null;
    const relatedIds = relatedProfileIds.filter((id) => id !== currentProfileId);
    if (!relatedIds.length) {
      const { related_profile_ids: _relatedProfileIds, ...payloadWithoutRelatedProfiles } = payload;
      return payloadWithoutRelatedProfiles;
    }
    return {
      ...payload,
      related_profile_ids: relatedIds,
    };
  }

  function buildManualPartnerPayload(): BirthChartRequest | null {
    if (!selectedPartnerPlace) {
      setCompatibilityStatus("Выбери город второго человека из подсказок");
      return null;
    }
    return {
      birth_date: partnerBirthDate,
      birth_time: partnerBirthTime,
      place_name: selectedPartnerPlace.label,
      ...calculationSettingsPayload(),
      place_id: selectedPartnerPlace.id,
      country_code: selectedPartnerPlace.country_code,
      timezone: selectedPartnerPlace.timezone,
      latitude: selectedPartnerPlace.latitude,
      longitude: selectedPartnerPlace.longitude,
    };
  }

  function buildPartnerPayload(): BirthChartRequest | null {
    return selectedProfilePayload(compatibilityPersonBProfileId) ?? buildManualPartnerPayload();
  }

  function buildCompatibilityRelationshipContext() {
    const role = compatibilityRelationshipRole(compatibilityRelationshipRoleKey);
    const relationship = selectedCompatibilityRelationship;
    return {
      role: role.key,
      label: role.label,
      focus_houses: [...role.focusHouses],
      focus_vargas: [...role.focusVargas],
      prompt_hint: role.promptHint,
      consent_policy: "Если второй человек является зарегистрированным пользователем, полноценную взаимную связь нужно показывать только после подтверждения запроса.",
      ...(relationship
        ? {
            relationship_id: relationship.id,
            link_status: relationship.link_status,
            profile_id: relationship.profile_id,
            related_profile_id: relationship.related_profile_id,
            profile_label: relationship.profile?.display_name ?? undefined,
            related_profile_label: relationship.related_profile?.display_name ?? undefined,
          }
        : {}),
    };
  }

  function buildCompatibilityPayload(personA: BirthChartRequest, personB: BirthChartRequest) {
    return {
      person_a: personA,
      person_b: personB,
      relationship_context: buildCompatibilityRelationshipContext(),
    };
  }

  async function refreshProfiles() {
    try {
      const [items, relationships, incomingRequests] = await Promise.all([
        listChartProfiles(),
        listChartProfileRelationships(),
        listIncomingChartProfileRelationshipRequests(),
      ]);
      setProfiles(items);
      setProfileRelationships(relationships);
      setIncomingProfileRelationshipRequests(incomingRequests);
      setIncomingRequestAcceptedProfileIds((current) => {
        const fallbackProfileId = items[0] ? String(items[0].id) : "";
        return Object.fromEntries(
          incomingRequests.map((request) => [
            request.id,
            current[request.id] && items.some((profile) => String(profile.id) === current[request.id])
              ? current[request.id]
              : fallbackProfileId,
          ]),
        );
      });
      setRelatedProfileIds((current) => current.filter((id) => items.some((profile) => profile.id === id)));
      setRelationshipBaseProfileId((current) => {
        if (current && items.some((profile) => String(profile.id) === current)) return current;
        return items[0] ? String(items[0].id) : "";
      });
      setProfileStatus(items.length ? `${items.length} сохранённых карт` : "Сохранённых карт пока нет");
    } catch (error) {
      setProfiles([]);
      setProfileRelationships([]);
      setIncomingProfileRelationshipRequests([]);
      setIncomingRequestAcceptedProfileIds({});
      setRelationshipBaseProfileId("");
      setProfileStatus(error instanceof Error ? error.message : "Не удалось загрузить профили");
    }
  }

  async function handleAuth(mode: "login" | "register") {
    setAuthStatus(mode === "login" ? "Вхожу..." : "Создаю пользователя...");
    try {
      const authResult =
        mode === "login"
          ? { user: await loginUser(authUsername, authPassword), profile: null }
          : await registerUser(authUsername, authPassword, {
              display_name: profileName || "Моя карта",
              birth_date: birthDate,
              birth_time: birthTime,
              birth_time_accuracy: birthTime ? "exact" : "unknown",
              place_name: placeName,
              timezone: selectedPlace?.timezone,
              latitude: selectedPlace?.latitude,
              longitude: selectedPlace?.longitude,
            });
      const user = authResult.user;
      if (!user.is_active) {
        setCurrentUser(null);
        setProfiles([]);
        setProfileRelationships([]);
        setIncomingProfileRelationshipRequests([]);
        setIncomingRequestAcceptedProfileIds({});
        setRelationshipBaseProfileId("");
        setAuthStatus("Регистрация отправлена. Доступ появится после одобрения администратора.");
        setProfileStatus("После одобрения можно будет сохранять карты");
        return;
      }
      setCurrentUser(user);
      setAuthOpen(false);
      if (mode === "register" && authResult.profile) {
        setProfiles([authResult.profile]);
        setRelationshipBaseProfileId(String(authResult.profile.id));
        setProfileStatus(`${authResult.profile.display_name}: создана ваша первая карта`);
        setAuthStatus(
          authResult.profile.birth_time
            ? `Регистрация завершена: ${user.username}. Моя карта создана.`
            : `Регистрация завершена: ${user.username}. Моя карта создана без времени рождения; его можно уточнить позже.`,
        );
      } else {
        setAuthStatus(mode === "register" ? `Регистрация завершена: ${user.username}` : `Вход: ${user.username}`);
      }
      await refreshProfiles();
    } catch (error) {
      setCurrentUser(null);
      setProfiles([]);
      setProfileRelationships([]);
      setIncomingProfileRelationshipRequests([]);
      setIncomingRequestAcceptedProfileIds({});
      setRelationshipBaseProfileId("");
      setAuthStatus(error instanceof Error ? error.message : "Ошибка авторизации");
    }
  }

  async function handleLogout() {
    await logoutUser();
    setCurrentUser(null);
    setAuthOpen(false);
    setProfiles([]);
    setProfileRelationships([]);
    setIncomingProfileRelationshipRequests([]);
    setIncomingRequestAcceptedProfileIds({});
    setRelationshipBaseProfileId("");
    setAuthStatus("Вы вышли");
    setProfileStatus("Сохранённые карты не загружены");
  }

  async function handleSaveProfile() {
    if (!currentUser) {
      setProfileStatus("Сначала войдите или зарегистрируйтесь");
      return;
    }
    const payload = buildBirthPayload();
    if (!payload) return;
    setProfileStatus("Сохраняю карту...");
    try {
      await createChartProfile({
        ...payload,
        display_name: profileName.trim() || "Моя карта",
        is_self_profile: profileIsSelf,
      });
      await refreshProfiles();
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось сохранить карту");
    }
  }

  function handleExportCurrentChart() {
    if (!chart) {
      setStatus("Сначала рассчитайте карту для экспорта");
      return;
    }
    const exportPayload = {
      exported_at: new Date().toISOString(),
      birth_request: lastBirthPayload ?? buildBirthPayload(),
      chart,
      report: birthReport,
    };
    const objectUrl = URL.createObjectURL(
      new Blob([JSON.stringify(exportPayload, null, 2)], { type: "application/json" }),
    );
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = `jyotish-${chart.birth.date}-${chartMode}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(objectUrl);
    setStatus("Карта экспортирована");
  }

  function handleSelectCompatibilityPersonAProfile(profileId: string) {
    setActiveCompatibilityRelationshipId("");
    setCompatibilityPersonAProfileId(profileId);
    resetCompatibilityResultState();
    setCompatibilityStatus(profileId ? "Карта A взята из сохранённых" : "Карта A: текущий расчёт");
  }

  function handleSelectCompatibilityPersonBProfile(profileId: string) {
    setActiveCompatibilityRelationshipId("");
    setCompatibilityPersonBProfileId(profileId);
    resetCompatibilityResultState();
    const profile = profiles.find((item) => String(item.id) === profileId);
    if (!profile) {
      setCompatibilityStatus("Карта B: ручной ввод");
      return;
    }
    setPartnerBirthDate(profile.birth_date);
    setPartnerBirthTime(profile.birth_time ?? "");
    setPartnerPlaceName(profile.place.label);
    setSelectedPartnerPlace(null);
    setShowPartnerPlaceSuggestions(false);
    setCompatibilityStatus(`Карта B выбрана: ${profile.display_name}`);
  }

  async function handleSavePartnerProfile() {
    if (!currentUser) {
      setProfileStatus("Сначала войдите или зарегистрируйтесь");
      return;
    }
    const payload = buildManualPartnerPayload();
    if (!payload) return;
    setProfileStatus("Сохраняю карту партнёра...");
    try {
      const saved = await createChartProfile({
        ...payload,
        display_name: partnerProfileName.trim() || "Карта партнёра",
        is_self_profile: false,
      });
      await refreshProfiles();
      setActiveCompatibilityRelationshipId("");
      setCompatibilityPersonBProfileId(String(saved.id));
      resetCompatibilityResultState();
      setCompatibilityStatus(`Карта B сохранена: ${saved.display_name}`);
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось сохранить карту партнёра");
    }
  }

  async function handleMarkSelfProfile(profile: ChartProfile, isSelf: boolean) {
    setProfileStatus(isSelf ? "Помечаю карту как вашу..." : "Снимаю пометку вашей карты...");
    try {
      const updated = await updateChartProfile(profile.id, { is_self_profile: isSelf });
      setProfiles((current) =>
        current.map((item) => ({
          ...item,
          is_self_profile: isSelf ? item.id === updated.id : item.id === updated.id ? false : item.is_self_profile,
        })),
      );
      if (isSelf) {
        setProfileName(updated.display_name);
        setProfileIsSelf(true);
      } else {
        setProfileIsSelf(false);
      }
      setProfileStatus(isSelf ? `${updated.display_name}: теперь это ваша карта` : `${updated.display_name}: пометка снята`);
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось обновить карту");
    }
  }

  async function refreshWorkflowReports(payload: BirthChartRequest) {
    setWorkflowStatus("Считаю дополнительные разделы...");
    const today = isoDateOffset(0);
    const weekEnd = isoDateOffset(7);
    const annualPayload = {
      ...payload,
      target_year: new Date().getFullYear(),
      return_place_name: payload.place_name,
      return_timezone: payload.timezone,
      return_latitude: payload.latitude,
      return_longitude: payload.longitude,
    };
    const eventBase = {
      place_name: payload.place_name,
      timezone: payload.timezone,
      latitude: payload.latitude,
      longitude: payload.longitude,
      ...calculationSettingsFromPayload(payload),
    };
    const [transits, tithiPravesha, tajaka, prashna, mundane, muhurta] = await Promise.allSettled([
      calculateTransits({
        ...payload,
        as_of_date: today,
        as_of_time: "09:00",
      }),
      calculateTithiPravesha(annualPayload),
      calculateTajaka(annualPayload),
      calculatePrashna({
        ...eventBase,
        question: "Текущий вопрос",
        question_date: today,
        question_time: "09:00",
      }),
      calculateMundane({
        ...eventBase,
        event_type: "general",
        description: "Текущий event chart",
        event_date: today,
        event_time: "09:00",
      }),
      calculateMuhurta({
        ...eventBase,
        start_date: today,
        end_date: weekEnd,
        time: "09:00",
      }),
    ]);

    if (transits.status === "fulfilled") {
      setTransitReport(transits.value);
    } else {
      setTransitReport(null);
    }
    if (tithiPravesha.status === "fulfilled") {
      setTithiPraveshaReport(tithiPravesha.value);
    } else {
      setTithiPraveshaReport(null);
    }
    if (tajaka.status === "fulfilled") {
      setTajakaReport(tajaka.value);
    } else {
      setTajakaReport(null);
    }
    if (prashna.status === "fulfilled") {
      setPrashnaReport(prashna.value);
    } else {
      setPrashnaReport(null);
    }
    if (mundane.status === "fulfilled") {
      setMundaneReport(mundane.value);
    } else {
      setMundaneReport(null);
    }
    if (muhurta.status === "fulfilled") {
      setMuhurtaReport(muhurta.value);
    } else {
      setMuhurtaReport(null);
    }
    setWorkflowStatus(
      [transits, tithiPravesha, tajaka, prashna, mundane, muhurta].every((item) => item.status === "fulfilled")
        ? "рассчитано"
        : "частично рассчитано",
    );
  }

  async function handleGenerateCurrentDayOverview() {
    if (currentDayBusy) return;
    if (aiAccessLocked) {
      setCurrentDayStatus("Войдите или зарегистрируйтесь, чтобы сохранять обзор нынешнего дня в личной истории.");
      return;
    }
    const basePayload = lastBirthPayload ?? buildBirthPayload();
    const payload = basePayload ? payloadWithCurrentRelatedProfiles(basePayload) : null;
    if (!payload) return;
    const today = isoDateOffset(0);
    const nowTime = new Date().toTimeString().slice(0, 5);
    setCurrentDayOverview(null);
    setCurrentDayBusy(true);
    setCurrentDayStatus("Сохраняю обзор нынешнего дня...");
    setAnalysisWorkspaceOpen(true);
    setActiveAnalysisTab("transits");
    try {
      const [overviewResult, transitResult] = await Promise.allSettled([
        generateCurrentDayOverview({ ...payload, as_of_date: today, as_of_time: nowTime }),
        calculateTransits({ ...payload, as_of_date: today, as_of_time: nowTime }),
      ]);
      if (transitResult.status === "fulfilled") {
        setTransitReport(transitResult.value);
      }
      if (overviewResult.status !== "fulfilled") {
        throw overviewResult.reason;
      }
      setCurrentDayOverview(overviewResult.value);
      setCurrentDayStatus(`Обзор сохранён: ${overviewResult.value.sections.length} раздела`);
    } catch (error) {
      setCurrentDayOverview(null);
      setCurrentDayStatus(error instanceof Error ? error.message : "Не удалось сохранить обзор нынешнего дня");
    } finally {
      setCurrentDayBusy(false);
    }
  }

  async function handleCompatibilitySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const personA = selectedProfilePayload(compatibilityPersonAProfileId) ?? lastBirthPayload ?? buildBirthPayload();
    const personB = buildPartnerPayload();
    if (!personA || !personB) return;

    setCompatibilityStatus("Считаю совместимость...");
    setCompatibilityCodexAnalysis(null);
    setCompatibilityCodexStatus("");
    try {
      const result = await calculateCompatibility({
        ...buildCompatibilityPayload(personA, personB),
      });
      setCompatibilityReport(result);
      setCompatibilityPacketStatus("Можно подготовить разбор по этому расчёту");
      setCompatibilityStatus("рассчитано");
    } catch (error) {
      setCompatibilityReport(null);
      setCompatibilityPacketStatus("");
      setCompatibilityCodexAnalysis(null);
      setCompatibilityStatus(error instanceof Error ? error.message : "Расчёт совместимости временно недоступен");
    }
  }

  async function handleCompatibilityPacket() {
    const personA = selectedProfilePayload(compatibilityPersonAProfileId) ?? lastBirthPayload ?? buildBirthPayload();
    const personB = buildPartnerPayload();
    if (!personA || !personB) return;

    setCompatibilityPacketStatus("Готовлю разбор...");
    try {
      const packet = await generateCompatibilityAnalysisPacket({
        ...buildCompatibilityPayload(personA, personB),
      });
      const compatibility = packet.context.compatibility as CompatibilityReport | undefined;
      if (compatibility) {
        setCompatibilityReport(compatibility);
      setCompatibilityStatus("разбор подготовлен");
      }
      const perspectiveCount = compatibility?.analysis?.perspectives.length ?? 0;
      const requestCount = packet.citation_requests.length;
      let copied = false;
      if (navigator.clipboard?.writeText) {
        try {
          await navigator.clipboard.writeText(packet.prompt_markdown);
          copied = true;
        } catch {
          copied = false;
        }
      }
      setCompatibilityPacketStatus(
        copied ? "Разбор подготовлен и скопирован" : "Разбор подготовлен",
      );
    } catch (error) {
      setCompatibilityPacketStatus(error instanceof Error ? error.message : "Ошибка подготовки разбора");
    }
  }

  async function handleCompatibilityCodexAnalysis() {
    if (aiAccessLocked) {
      setCompatibilityCodexStatus("Войдите или зарегистрируйтесь, чтобы сохранить разбор совместимости в личной истории.");
      return;
    }
    const personA = selectedProfilePayload(compatibilityPersonAProfileId) ?? lastBirthPayload ?? buildBirthPayload();
    const personB = buildPartnerPayload();
    if (!personA || !personB) return;

    setCompatibilityCodexStatus("Запускаю полный разбор двух карт...");
    try {
      const result = await generateCompatibilityCodexAnalysis({
        ...buildCompatibilityPayload(personA, personB),
      });
      if (isQueuedAnalysisGeneration(result)) {
        setCompatibilityCodexStatus("Разбор готовится и появится в истории.");
        return;
      }
      setCompatibilityCodexAnalysis(result);
      setCompatibilityChatMessages([]);
      setCompatibilityChatStatus("Можно задавать вопросы по этому разбору совместимости");
      setCompatibilityCodexStatus("Разбор готов.");
    } catch (error) {
      if (isAnalysisInProgressError(error)) {
        setCompatibilityCodexStatus(error.message);
      } else {
        setCompatibilityCodexAnalysis(null);
        resetCompatibilityChat();
        setCompatibilityCodexStatus(error instanceof Error ? error.message : "Ошибка полного разбора совместимости");
      }
    }
  }

  async function handleAskCompatibilityQuestion(question: string) {
    if (aiAccessLocked) {
      setCompatibilityChatStatus("Войдите, чтобы продолжать диалог по сохранённому обзору совместимости.");
      return;
    }
    if (!compatibilityCodexAnalysis) return;
    const userMessage: CodexAnalysisChatMessage = { role: "user", content: question };
    const history = [...compatibilityChatMessages, userMessage];
    setCompatibilityChatMessages(history);
    setCompatibilityChatBusy(true);
    setCompatibilityChatStatus("Готовлю ответ по совместимости...");
    try {
      const result = await askCompatibilityCodexAnalysis(compatibilityCodexAnalysis.id, question, history);
      setCompatibilityChatMessages([...history, { role: "assistant", content: result.answer }]);
      const sourceCount = result.source_traces?.length ?? result.evidence_references?.length ?? 0;
      setCompatibilityChatStatus(sourceCount ? `Ответ готов, источников: ${sourceCount}` : "Ответ готов");
    } catch (error) {
      setCompatibilityChatMessages([...history, { role: "assistant", content: error instanceof Error ? error.message : "Ошибка ответа" }]);
      setCompatibilityChatStatus(isAnalysisInProgressError(error) ? "Ответ уже формируется" : "Ошибка ответа");
    } finally {
      setCompatibilityChatBusy(false);
    }
  }

  async function handleGenerateDraftAnalysis(forceRegenerate = false) {
    if (aiAccessLocked) {
      setDraftAnalysisStatus("Войдите или зарегистрируйтесь, чтобы сохранить личный разбор.");
      return;
    }
    if (!activeSavedBirthProfile) {
      setDraftAnalysisStatus("Сначала сохраните расчёт как вашу личную карту. Первый разбор доступен только для сохранённой «моей карты».");
      return;
    }
    if (!activeSavedBirthProfile.is_self_profile) {
      setDraftAnalysisStatus("Разбор чужой сохранённой карты будет платным действием после подключения оплаты. Карту можно хранить и смотреть бесплатно.");
      return;
    }
    const basePayload = lastBirthPayload ?? buildBirthPayload();
    const payload = basePayload ? payloadWithCurrentRelatedProfiles(basePayload) : null;
    if (!payload) return;
    setDraftAnalysis(null);
    resetCodexChat();
    setDraftAnalysisStatus(
      forceRegenerate
        ? "Обновляю старый разбор по текущему корпусу шастр..."
        : "Запускаю разбор и сопоставление с шастрами...",
    );
    try {
      const result = await generateBirthCodexAnalysis(payload, { forceRegenerate });
      if (isQueuedAnalysisGeneration(result)) {
        setDraftAnalysisStatus("Разбор готовится и появится в истории.");
        return;
      }
      setDraftAnalysis(result);
      setCodexChatMessages([]);
      setCodexChatStatus("Можно задавать вопросы по этому разбору");
      setDraftAnalysisStatus(
        result.billing_status === "free_personal_analysis_already_used"
          ? "Открыт сохранённый личный разбор."
          : "Разбор готов.",
      );
    } catch (error) {
      if (isAnalysisInProgressError(error)) {
        setDraftAnalysisStatus(error.message);
      } else {
        setDraftAnalysis(null);
        resetCodexChat();
        setDraftAnalysisStatus(error instanceof Error ? error.message : "Ошибка генерации разбора");
      }
    }
  }

  async function handleAskDraftQuestion(question: string) {
    if (aiAccessLocked) {
      setCodexChatStatus("Войдите, чтобы продолжать диалог по сохранённому личному обзору.");
      return;
    }
    if (!draftAnalysis) return;
    const userMessage: CodexAnalysisChatMessage = { role: "user", content: question };
    const history = [...codexChatMessages, userMessage];
    setCodexChatMessages(history);
    setCodexChatBusy(true);
    setCodexChatStatus("Готовлю ответ...");
    try {
      const result = await askBirthCodexAnalysis(draftAnalysis.id, question, history);
      setCodexChatMessages([...history, { role: "assistant", content: result.answer }]);
      const sourceCount = result.source_traces?.length ?? result.evidence_references?.length ?? 0;
      setCodexChatStatus(sourceCount ? `Ответ готов, источников: ${sourceCount}` : "Ответ готов");
    } catch (error) {
      setCodexChatMessages([...history, { role: "assistant", content: error instanceof Error ? error.message : "Ошибка ответа" }]);
      setCodexChatStatus(isAnalysisInProgressError(error) ? "Ответ уже формируется" : "Ошибка ответа");
    } finally {
      setCodexChatBusy(false);
    }
  }

  async function handleCalculateProfile(profile: ChartProfile) {
    setProfileStatus(`Загружаю и рассчитываю: ${profile.display_name}`);
    try {
      applyProfileToBirthForm(profile);
      const payload = profileBirthPayload(profile);
      const [savedCalculation, reportResult] = await Promise.allSettled([
        calculateSavedProfile(profile.id),
        generateBirthReport(payload),
      ]);
      if (reportResult.status === "fulfilled") {
        setChart(reportResult.value.chart);
        setBirthReport(reportResult.value.report);
      } else if (savedCalculation.status === "fulfilled") {
        setChart(savedCalculation.value.result);
        setBirthReport(null);
      } else {
        throw reportResult.reason ?? savedCalculation.reason;
      }
      setChartMode("D1");
      setShowBirthEditor(false);
      setDraftAnalysis(null);
      setDraftAnalysisStatus("Личный разбор ещё не генерировался");
      setCurrentDayOverview(null);
      setCurrentDayStatus("Текущий день ещё не сохранялся");
      setLastBirthPayload(payload);
      setCompatibilityReport(null);
      setCompatibilityStatus("Можно считать совместимость");
      setCompatibilityCodexAnalysis(null);
      setCompatibilityCodexStatus("");
      setWorkflowStatus("Готово");
      const requestedAnalysis = requestedAnalysisFromLocation();
      if (requestedAnalysis) {
        setAnalysisWorkspaceOpen(true);
        setActiveAnalysisTab(requestedAnalysis);
      } else {
        setAnalysisWorkspaceOpen(false);
        setActiveAnalysisTab("overview");
      }
      setStatus("Сохранённая карта загружена и рассчитана");
      scrollToChartAfterCalculation();
      await refreshProfiles();
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось рассчитать профиль");
    }
  }

  async function runBirthCalculation(payload: BirthChartRequest, statusMessage = "Считаю карту...") {
    setStatus(statusMessage);
    try {
      const result = await generateBirthReport(payload);
      setChart(result.chart);
      setChartMode("D1");
      setShowBirthEditor(false);
      setBirthReport(result.report);
      setDraftAnalysis(null);
      setDraftAnalysisStatus("Личный разбор ещё не генерировался");
      setCurrentDayOverview(null);
      setCurrentDayStatus("Текущий день ещё не сохранялся");
      setLastBirthPayload(payload);
      setCompatibilityReport(null);
      setCompatibilityStatus("Можно считать совместимость");
      setCompatibilityCodexAnalysis(null);
      setCompatibilityCodexStatus("");
      setWorkflowStatus("Готово");
      const requestedAnalysis = requestedAnalysisFromLocation();
      if (requestedAnalysis) {
        setAnalysisWorkspaceOpen(true);
        setActiveAnalysisTab(requestedAnalysis);
      } else {
        setAnalysisWorkspaceOpen(false);
      }
      setStatus("Отчёт построен");
      scrollToChartAfterCalculation();
    } catch (error) {
      setChart(null);
      setBirthReport(null);
      setDraftAnalysis(null);
      setDraftAnalysisStatus("Личный разбор ещё не генерировался");
      setCurrentDayOverview(null);
      setCurrentDayStatus("Текущий день ещё не сохранялся");
      setTransitReport(null);
      setMuhurtaReport(null);
      setCompatibilityReport(null);
      setCompatibilityCodexAnalysis(null);
      setCompatibilityCodexStatus("");
      setLastBirthPayload(null);
      setCompatibilityStatus("Ожидает основную карту");
      setStatus("Расчёт временно недоступен.");
    }
  }

  async function submitBirthCalculation() {
    const payload = buildBirthPayload();
    if (!payload) return;
    await runBirthCalculation(payload);
  }

  async function submitCurrentChartCalculation() {
    const payload = buildBirthPayload();
    if (!payload) return;
    await runCurrentChartCalculation(payload);
  }

  async function runCurrentChartCalculation(payload: BirthChartRequest) {
    setStatus("Считаю карту на сейчас...");
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 5000);
    try {
      const result = await calculateBirthChart(payload, { signal: controller.signal });
      setChart(result);
      setChartMode("D1");
      setShowBirthEditor(false);
      setBirthReport(null);
      setDraftAnalysis(null);
      setCurrentDayOverview(null);
      setLastBirthPayload(payload);
      setStatus("Карта на сейчас построена");
    } catch (error) {
      setChart(null);
      setBirthReport(null);
      setLastBirthPayload(null);
      setStatus("Расчёт сейчас временно недоступен.");
    } finally {
      window.clearTimeout(timeout);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await submitBirthCalculation();
  }

  async function handleCalculateClick(event: { preventDefault: () => void }) {
    event.preventDefault();
    await submitBirthCalculation();
  }

  async function handleSourceSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSourceStatus("Ищу в источниках...");
    try {
      const results = await searchVLSources(sourceQuery);
      setSourceResults(results);
      setSourceStatus(results.length ? `${results.length} результатов` : "В источниках ничего не найдено");
    } catch (error) {
      setSourceResults([]);
      setSourceStatus(error instanceof Error ? error.message : "Поиск временно недоступен");
    }
  }

  async function handleResearchSearch() {
    setResearchStatus("Ищу по книгам...");
    try {
      const results = await searchResearchSources(sourceQuery);
      setResearchResults(results);
      setResearchStatus(results.length ? `${results.length} фрагментов найдено` : "Совпадений не найдено");
    } catch (error) {
      setResearchResults([]);
      setResearchStatus(error instanceof Error ? error.message : "Ошибка поиска");
    }
  }

  const activeSavedBirthProfile = typeof lastBirthPayload?.profile_id === "number"
    ? profiles.find((profile) => profile.id === lastBirthPayload.profile_id) ?? null
    : null;
  const aiBillingStatus = activeSavedBirthProfile
    ? activeSavedBirthProfile.is_self_profile
      ? {
          label: "Личный разбор",
          text: "Эта карта отмечена как «моя карта»: первый личный разбор доступен бесплатно; повтор вернёт сохранённый отчёт.",
          tone: "free" as const,
        }
      : {
          label: "Чужая сохранённая карта",
          text: "Карту можно хранить и смотреть бесплатно. Разбор этой карты будет платным действием после подключения оплаты.",
          tone: "paid" as const,
        }
    : {
        label: currentUser ? "Карта ещё не сохранена" : "Нужен вход",
        text: currentUser
          ? "Сохраните расчёт как «моя карта», чтобы использовать первый бесплатный личный разбор."
          : "Войдите или зарегистрируйтесь: первый разбор доступен только для вашей сохранённой карты.",
        tone: "neutral" as const,
      };

  const activeMainNavKey: AppNavKey =
    activeAnalysisTab === "overview"
      ? "charts"
      : chartWorkspaceTab === "vargas"
        ? "vargas"
      : activeAnalysisTab === "transits"
        ? "transits"
        : activeAnalysisTab === "compatibility"
          ? "compatibility"
          : activeAnalysisTab === "sources"
            ? "sources"
            : activeAnalysisTab === "calculations"
              ? "calculations"
              : activeAnalysisTab === "yogas"
                ? "yogas"
                : activeAnalysisTab === "muhurta"
                  ? "muhurta"
                  : activeAnalysisTab === "guidance"
                    ? "guidance"
                    : activeAnalysisTab === "accuracy"
                      ? "accuracy"
          : "charts";

  function handleMainNavSelect(key: AppNavKey) {
    if (key === "charts" || key === "settings") {
      setChartWorkspaceTab("essentials");
      setAnalysisWorkspaceOpen(false);
      setActiveAnalysisTab("overview");
      return;
    }
    if (key === "vargas") {
      setChartWorkspaceTab("vargas");
      setAnalysisWorkspaceOpen(false);
      setActiveAnalysisTab("overview");
      return;
    }
    if (
      key === "calculations" ||
      key === "yogas" ||
      key === "timeline" ||
      key === "transits" ||
      key === "muhurta" ||
      key === "guidance" ||
      key === "sources" ||
      key === "accuracy"
    ) {
      setAnalysisWorkspaceOpen(true);
      setActiveAnalysisTab(key);
    }
  }

  useEffect(() => {
    setClientMounted(true);
  }, []);

  const initialUiReady = true;

  if (!initialUiReady) {
    return (
      <main className={`app-shell shell-loading ${interfaceMode === "beginner" ? "beginner-mode" : "pro-mode"}${sidebarCollapsed ? " sidebar-collapsed" : ""}`}>
        <aside className="sidebar">
          <div className="sidebar-brand-row">
            <div className="mark jyotish-mark" aria-hidden="true">
              <svg viewBox="0 0 48 48" focusable="false">
                <circle cx="24" cy="24" r="7.5" />
                <circle cx="24" cy="24" r="14.5" />
                <path d="M24 3v7M24 38v7M3 24h7M38 24h7" />
                <path d="M9.15 9.15l4.95 4.95M33.9 33.9l4.95 4.95M38.85 9.15l-4.95 4.95M14.1 33.9l-4.95 4.95" />
                <path d="M24 10.5l3 7.3 7.7.7-5.85 5.1 1.75 7.6L24 27.15l-6.6 4.05 1.75-7.6-5.85-5.1 7.7-.7z" />
              </svg>
            </div>
            <button
              type="button"
              className="sidebar-collapse-button"
              onClick={toggleSidebarCollapsed}
              aria-label={sidebarCollapsed ? "Развернуть меню" : "Свернуть меню"}
              title={sidebarCollapsed ? "Развернуть меню" : "Свернуть меню"}
            >
              {sidebarCollapsed ? "›" : "‹"}
            </button>
          </div>
          <div className="sidebar-title">
            <h1>Веда Джйотиш</h1>
          </div>
          <AppNavigation activeKey="charts" home />
        </aside>
        <section className="workspace">
          <header className="topbar">
            <div className="topbar-title">
              <strong>Открываю карту</strong>
            </div>
          </header>
          <section className="panel initial-ui-loading" aria-live="polite">
            <strong>Открываю карту</strong>
          </section>
        </section>
      </main>
    );
  }

  return (
    <main className={`app-shell ${interfaceMode === "beginner" ? "beginner-mode" : "pro-mode"}${sidebarCollapsed ? " sidebar-collapsed" : ""}`}>
      <aside className="sidebar">
        <div className="sidebar-brand-row">
          <div className="mark jyotish-mark" aria-hidden="true">
            <svg viewBox="0 0 48 48" focusable="false">
              <circle cx="24" cy="24" r="7.5" />
              <circle cx="24" cy="24" r="14.5" />
              <path d="M24 3v7M24 38v7M3 24h7M38 24h7" />
              <path d="M9.15 9.15l4.95 4.95M33.9 33.9l4.95 4.95M38.85 9.15l-4.95 4.95M14.1 33.9l-4.95 4.95" />
              <path d="M24 10.5l3 7.3 7.7.7-5.85 5.1 1.75 7.6L24 27.15l-6.6 4.05 1.75-7.6-5.85-5.1 7.7-.7z" />
            </svg>
          </div>
          <button
            type="button"
            className="sidebar-collapse-button"
            onClick={toggleSidebarCollapsed}
            aria-label={sidebarCollapsed ? "Развернуть меню" : "Свернуть меню"}
            title={sidebarCollapsed ? "Развернуть меню" : "Свернуть меню"}
          >
            {sidebarCollapsed ? "›" : "‹"}
          </button>
        </div>
        <div className="sidebar-title">
          <h1>Веда Джйотиш</h1>
        </div>
        <AppNavigation activeKey={activeMainNavKey} home onSelect={handleMainNavSelect} />
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="topbar-title">
            <strong>{currentChartDefault ? "Карта на сейчас" : "Карта рождения"}</strong>
            <span>
              {birthDate} · {birthTime} · {selectedPlace?.label ?? chart?.place.label ?? placeName}
            </span>
          </div>
          <div className="topbar-account" aria-label="Аккаунт">
            {currentUser ? (
              <>
                <span>{currentUser.username}</span>
                <button type="button" className="secondary-button" onClick={handleLogout}>
                  Выйти
                </button>
              </>
            ) : (
              <button type="button" className="secondary-button" onClick={() => setAuthOpen(true)}>
                Войти
              </button>
            )}
          </div>
        </header>

        {authOpen && !currentUser ? (
          <div className="product-auth-popover-backdrop" role="presentation" onMouseDown={() => setAuthOpen(false)}>
            <section className="product-auth-popover" aria-label="Вход и регистрация" onMouseDown={(event) => event.stopPropagation()}>
              <div className="product-auth-popover-head">
                <div>
                  <strong>Вход</strong>
                  <span>Регистрация может сразу создать вашу карту. Время рождения необязательно.</span>
                </div>
                <button type="button" onClick={() => setAuthOpen(false)} aria-label="Закрыть">
                  ×
                </button>
              </div>
              <div className="product-auth-popover-grid">
                <input placeholder="Логин" value={authUsername} onChange={(event) => setAuthUsername(event.target.value)} />
                <input placeholder="Пароль" type="password" value={authPassword} onChange={(event) => setAuthPassword(event.target.value)} />
                <label>
                  Дата рождения
                  <input
                    type="date"
                    value={birthDate}
                    onChange={(event) => {
                      setCurrentChartDefault(false);
                      setBirthDate(event.target.value);
                    }}
                  />
                </label>
                <label>
                  Время
                  <input
                    type="time"
                    value={birthTime}
                    onChange={(event) => {
                      setCurrentChartDefault(false);
                      setBirthTime(event.target.value);
                    }}
                  />
                </label>
                <label>
                  Город рождения
                  <input
                    value={placeName}
                    onChange={(event) => {
                      setCurrentChartDefault(false);
                      setPlaceName(event.target.value);
                    }}
                  />
                </label>
              </div>
              <div className="product-auth-popover-actions">
                <button type="button" className="primary-button" onClick={() => handleAuth("login")}>
                  Войти
                </button>
                <button type="button" className="secondary-button" onClick={() => handleAuth("register")}>
                  Регистрация
                </button>
              </div>
              <span className="product-auth-popover-status">{authStatus}</span>
            </section>
          </div>
        ) : null}

        {privateAccessLocked ? (
          <section className="panel private-gate" aria-live="polite">
            <div>
              <h2>Закрытый доступ</h2>
            </div>
            <div className="private-gate-actions">
              <button type="button" className="primary-button" onClick={() => setAuthOpen(true)}>
                Войти или зарегистрироваться
              </button>
            </div>
            <p className="status-line">{authStatus}</p>
          </section>
        ) : (
        <div className={`content-grid${chart ? " chart-ready" : ""}`}>
          <section className={`panel birth-panel${!showBirthEditor ? " compact" : ""}`} id="chart">
            <BirthCompactStrip
              birthDate={birthDate}
              birthTime={birthTime}
              placeName={placeName}
              selectedPlace={selectedPlace}
              chart={chart}
              currentChartDefault={currentChartDefault}
              collapsed={!showBirthEditor}
              onToggle={() => setShowBirthEditor((value) => !value)}
              onUseCurrent={loadCurrentChartData}
            />
            <div className="panel-heading">
              <h2>Данные рождения</h2>
              <button type="button" className="secondary-button" onClick={loadSampleBirthData}>Пример</button>
            </div>
            <form onSubmit={handleSubmit} className="birth-form" id="birth-form">
              <label>
                Дата рождения
                <input
                  type="date"
                  value={birthDate}
                  onInput={(event) => {
                    setCurrentChartDefault(false);
                    setBirthDate(event.currentTarget.value);
                  }}
                  onChange={(event) => {
                    setCurrentChartDefault(false);
                    setBirthDate(event.target.value);
                  }}
                />
              </label>
              <label>
                Время рождения
                <input
                  type="time"
                  value={birthTime}
                  onInput={(event) => {
                    setCurrentChartDefault(false);
                    setBirthTime(event.currentTarget.value);
                  }}
                  onChange={(event) => {
                    setCurrentChartDefault(false);
                    setBirthTime(event.target.value);
                  }}
                />
              </label>
              <label>
                Пол
                <select value={gender} onChange={(event) => setGender(event.target.value as "male" | "female" | "unknown")}>
                  <option value="male">Мужской</option>
                  <option value="female">Женский</option>
                  <option value="unknown">Не указан</option>
                </select>
              </label>
              <label>
                Место рождения
                <input
                  value={placeName}
                  onChange={(event) => {
                    setCurrentChartDefault(false);
                    setPlaceName(event.target.value);
                    setShowPlaceSuggestions(true);
                  }}
                  onFocus={() => setShowPlaceSuggestions(true)}
                  placeholder="Город или святое место"
                />
              </label>
              <div className="place-suggestions">
                <span>{placeSearchStatus}</span>
                {showPlaceSuggestions && placeMatches.length ? (
                  <div className="place-suggestion-list">
                    {placeMatches.slice(0, 6).map((place) => (
                      <button type="button" key={place.id} onClick={() => selectPlace(place)}>
                        <strong>{place.label}</strong>
                        <small>{place.timezone} · {formatCoordinate(place.latitude)}, {formatCoordinate(place.longitude)}</small>
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
              <div className="place-resolution" aria-live="polite">
                {selectedPlace ? (
                  <>
                    <div className="place-resolution-head">
                      <span>Выбранное место</span>
                      <strong>{selectedPlace.label}</strong>
                    </div>
                    <div className="place-detail-grid">
                      <div className="place-detail-item">
                        <span>Часовой пояс</span>
                        <strong>{selectedPlace.timezone}</strong>
                      </div>
                      <div className="place-detail-item">
                        <span>Широта</span>
                        <strong>{formatCoordinate(selectedPlace.latitude)}</strong>
                      </div>
                      <div className="place-detail-item">
                        <span>Долгота</span>
                        <strong>{formatCoordinate(selectedPlace.longitude)}</strong>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="manual-place-panel">
                    <span>Место не найдено. Укажите часовой пояс и координаты вручную.</span>
                    <div className="manual-place-grid">
                      <label>
                        Часовой пояс
                        <input
                          value={manualTimezone}
                          onChange={(event) => setManualTimezone(event.target.value)}
                          placeholder="Asia/Yekaterinburg"
                        />
                      </label>
                      <label>
                        Широта
                        <input
                          inputMode="decimal"
                          value={manualLatitude}
                          onChange={(event) => setManualLatitude(event.target.value)}
                          placeholder="56.8389"
                        />
                      </label>
                      <label>
                        Долгота
                        <input
                          inputMode="decimal"
                          value={manualLongitude}
                          onChange={(event) => setManualLongitude(event.target.value)}
                          placeholder="60.6057"
                        />
                      </label>
                    </div>
                  </div>
                )}
              </div>
              {alternatePlaceMatches.length ? (
                <div className="place-match-list">
                  <span>Другие совпадения</span>
                  {alternatePlaceMatches.map((place) => (
                    <button type="button" key={place.id} onClick={() => selectPlace(place)}>
                      <strong>{place.label}</strong>
                      <small>{place.timezone} · {formatCoordinate(place.latitude)}, {formatCoordinate(place.longitude)}</small>
                    </button>
                  ))}
                </div>
              ) : null}
              <button className="primary-button mobile-calculate-button" type="button" onClick={handleCalculateClick}>Рассчитать карту</button>
              <a className="mobile-chart-jump" href="#varga-charts">К карте</a>
              <section className="advanced-settings-toggle" aria-labelledby="advanced-settings-title">
                <button
                  type="button"
                  className="advanced-settings-button"
                  onClick={() => setShowAdvancedSettings((value) => !value)}
                  aria-expanded={showAdvancedSettings}
                  aria-controls="calculation-settings"
                >
                  <span id="advanced-settings-title">Параметры</span>
                  <strong>{showAdvancedSettings ? "Скрыть" : "Открыть"}</strong>
                </button>
                {showAdvancedSettings ? (
                  <fieldset className="calculation-settings" id="calculation-settings">
                    <legend>Профиль расчёта</legend>
                    <div className="settings-grid">
                      <label>
                        Зодиак
                        <select value={zodiac} onChange={(event) => setZodiac(event.target.value)}>
                          <option value="sidereal">Sidereal</option>
                        </select>
                      </label>
                      <label>
                        Модель
                        <select value={calculationModel} onChange={(event) => setCalculationModel(event.target.value)}>
                          <option value="drik_siddhanta">Drik Siddhanta</option>
                          <option value="surya_siddhanta" disabled>Sri Surya Siddhanta</option>
                        </select>
                      </label>
                      <label>
                        Айанамша
                        <select value={ayanamsa} onChange={(event) => setAyanamsa(event.target.value)}>
                          <option value="lahiri">Lahiri</option>
                        </select>
                      </label>
                      <label>
                        Узлы
                        <select value={nodeType} onChange={(event) => setNodeType(event.target.value)}>
                          <option value="true">True Node</option>
                          <option value="mean">Mean Node</option>
                        </select>
                      </label>
                      <label>
                        Эфемериды
                        <select value={ephemeris} onChange={(event) => setEphemeris(event.target.value)}>
                          <option value="swiss">Swiss Ephemeris</option>
                          <option value="jpl">JPL через Swiss</option>
                        </select>
                      </label>
                      <label>
                        Дома
                        <select value={houseSystem} onChange={(event) => setHouseSystem(event.target.value)}>
                          <option value="whole_sign">Whole Sign</option>
                        </select>
                      </label>
                      <label>
                        Бхава
                        <select value={bhavaSystem} onChange={(event) => setBhavaSystem(event.target.value)}>
                          <option value="whole_sign">Whole Sign</option>
                        </select>
                      </label>
                      <label>
                        Варги
                        <select value={vargaScheme} onChange={(event) => setVargaScheme(event.target.value)}>
                          <option value="parashara">Parashara</option>
                        </select>
                      </label>
                      <label>
                        Восход
                        <select value={sunriseSource} onChange={(event) => setSunriseSource(event.target.value)}>
                          <option value="noaa">NOAA</option>
                        </select>
                      </label>
                      <label>
                        Часовой пояс
                        <select value={timezoneSource} onChange={(event) => setTimezoneSource(event.target.value)}>
                          <option value="iana">Исторический часовой пояс</option>
                        </select>
                      </label>
                      <label>
                        <GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm>
                        <select value={shadbalaProfile} onChange={(event) => setShadbalaProfile(event.target.value)}>
                          <option value="bphs_classical">BPHS classical</option>
                        </select>
                      </label>
                    </div>
                    <span className="settings-note">Используется выбранный профиль расчёта.</span>
                  </fieldset>
                ) : null}
              </section>
              <fieldset className="calculation-settings display-settings" id="display-settings">
                <legend>Настройки отображения</legend>
                <div className="settings-grid">
                  <label>
                    Стиль карты
                    <select value={chartStyle} onChange={(event) => handleChartStyleChange(event.target.value as "north" | "south")}>
                      <option value="north">Северный</option>
                      <option value="south">Южный</option>
                    </select>
                  </label>
                  <label>
                    Язык терминов
                    <select value={termLanguage} onChange={(event) => handleTermLanguageChange(event.target.value as TermLanguage)}>
                      <option value="sanskrit">Санскрит</option>
                      <option value="ru">Русский</option>
                      <option value="en">English</option>
                    </select>
                  </label>
                  <label>
                    Режим интерфейса
                    <select value={interfaceMode} onChange={(event) => handleInterfaceModeChange(event.target.value as InterfaceMode)}>
                      <option value="pro">Астролог</option>
                      <option value="beginner">Новичок</option>
                    </select>
                  </label>
                </div>
                <span className="settings-note">Влияет только на внешний вид карт, таблиц и плотность интерфейса; расчёт не меняется.</span>
              </fieldset>
              <button className="primary-button desktop-calculate-button" type="button" onClick={handleCalculateClick}>Рассчитать карту</button>
              <p className="status-line">{status}</p>
            </form>
            <div className="account-block" id="account">
              <div className="block-heading">
                <h3>Аккаунт и сохранение</h3>
                <span>{authStatus}</span>
              </div>
              {currentUser ? (
                <div className="account-row">
                  <strong>{currentUser.username}</strong>
                  <button type="button" className="secondary-button" onClick={handleLogout}>Выйти</button>
                </div>
              ) : (
                <div className="account-row account-row-guest">
                  <strong>Гость</strong>
                  <button type="button" className="secondary-button" onClick={() => setAuthOpen(true)}>Войти</button>
                </div>
              )}
              <label>
                Название карты
                <input value={profileName} onChange={(event) => setProfileName(event.target.value)} />
              </label>
              <label className="self-profile-toggle">
                <input
                  type="checkbox"
                  checked={profileIsSelf}
                  onChange={(event) => setProfileIsSelf(event.target.checked)}
                />
                <span>
                  <strong>Это моя карта</strong>
                  <small>Основная карта владельца профиля.</small>
                </span>
              </label>
              <button type="button" className="secondary-button save-profile-button" onClick={handleSaveProfile}>
                Сохранить профиль рождения
              </button>
            </div>
            <div className="profile-block">
              <div className="block-heading">
                <h3>Сохранённые карты</h3>
                <div className="profile-heading-actions">
                  <button type="button" className="secondary-button" onClick={refreshProfiles}>Обновить</button>
                </div>
              </div>
              <p>{profileStatus}</p>
              {relatedProfileIds.length ? (
                <p className="related-profile-summary">
                  Связанные карты:{" "}
                  {profiles
                    .filter((profile) => relatedProfileIds.includes(profile.id))
                    .map((profile) => profile.display_name)
                    .join(", ")}
                </p>
              ) : null}
              {profiles.length >= 2 ? (
                <label className="relationship-base-select">
                  Базовая карта для взаимодействий
                  <select value={relationshipBaseProfileId} onChange={(event) => selectRelationshipBaseProfile(event.target.value)}>
                    {profiles.map((profile) => (
                      <option key={`relation-base-${profile.id}`} value={String(profile.id)}>
                        {profile.display_name}
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
              {incomingProfileRelationshipRequests.length ? (
                <div className="profile-relationship-inbox">
                  <strong>Запросы на связь</strong>
                  {incomingProfileRelationshipRequests.map((request) => {
                    const roleLabel = compatibilityRelationshipRole(request.role).label;
                    return (
                      <div className="profile-relationship-request" key={request.id}>
                        <div>
                          <span>{request.user?.username ?? "Пользователь"} просит связать карты</span>
                          <strong>{request.profile?.display_name ?? "Карта"} → {request.related_profile?.display_name ?? "ваша карта"}</strong>
                          <small>{roleLabel} · {request.related_profile?.birth_date ?? ""}</small>
                        </div>
                        <label>
                          Моя карта
                          <select
                            value={incomingRequestAcceptedProfileIds[request.id] ?? ""}
                            onChange={(event) =>
                              setIncomingRequestAcceptedProfileIds((current) => ({
                                ...current,
                                [request.id]: event.target.value,
                              }))
                            }
                          >
                            <option value="">Выбрать</option>
                            {profiles.map((profile) => (
                              <option value={String(profile.id)} key={`incoming-${request.id}-${profile.id}`}>
                                {profile.display_name}
                              </option>
                            ))}
                          </select>
                        </label>
                        <button type="button" className="secondary-button" onClick={() => handleIncomingProfileRelationshipAction(request.id, "accept")}>
                          Принять
                        </button>
                        <button type="button" className="secondary-button" onClick={() => handleIncomingProfileRelationshipAction(request.id, "decline")}>
                          Отклонить
                        </button>
                        <button type="button" className="secondary-button" onClick={() => handleIncomingProfileRelationshipAction(request.id, "block")}>
                          Заблокировать
                        </button>
                      </div>
                    );
                  })}
                </div>
              ) : null}
              {profiles.length ? (
                <div className="profile-list">
                  {profiles.map((profile) => {
                    const isBaseProfile = relationshipBaseProfileId === String(profile.id);
                    const relationship = profileRelationshipFor(relationshipBaseProfileId, profile.id);
                    const relationshipRole = relationship ? compatibilityRelationshipRole(relationship.role) : null;
                    return (
                      <div className="profile-row" key={profile.id}>
                        <div>
                          <strong>
                            {profile.display_name}
                            {profile.is_self_profile ? (
                              <GlossaryTerm termKey="self_profile">
                                <em className="self-profile-badge">моя карта</em>
                              </GlossaryTerm>
                            ) : null}
                          </strong>
                          <span>{profile.birth_date} · {profile.place.label}</span>
                          <small>
                            {profile.latest_calculation
                              ? `${stateLabels[profile.latest_calculation.status] ?? "расчёт сохранён"}, ${profile.latest_calculation.graha_count} грах`
                              : "Расчёт ещё не сохранён"}
                          </small>
                          {profile.is_self_profile ? (
                            <small className="profile-ai-note">
                              <GlossaryTerm termKey="free_personal_ai">первый разбор для этой карты</GlossaryTerm>
                            </small>
                          ) : (
                            <small className="profile-ai-note">карту можно хранить бесплатно; разбор чужой карты будет отдельным действием</small>
                          )}
                        </div>
                        <label className="profile-relationship-role">
                          <GlossaryTerm termKey="relationship_role">Роль</GlossaryTerm>
                          <select
                            value={isBaseProfile ? "self" : relationship?.role ?? ""}
                            disabled={isBaseProfile || !relationshipBaseProfileId}
                            onChange={(event) => handleProfileRelationshipRoleChange(profile.id, event.target.value)}
                          >
                            <option value="">{isBaseProfile ? "Это базовая карта" : "Указать роль"}</option>
                            <option value="self">Это базовая карта</option>
                            {compatibilityRelationshipRoles.map((role) => (
                              <option value={role.key} key={`profile-role-${profile.id}-${role.key}`}>
                                {role.label}
                              </option>
                            ))}
                          </select>
                          {!isBaseProfile && relationship ? (
                            <small>
                              <GlossaryTerm termKey="relationship_status">
                                {relationshipStatusLabel(relationship.link_status)}
                              </GlossaryTerm>
                            </small>
                          ) : null}
                          {!isBaseProfile && relationshipRole ? (
                            <div className="profile-role-focus" aria-label="Фокус роли для разбора">
                              <span>{relationshipRole.focus}</span>
                              <small>Дома <HouseTerms houses={relationshipRole.focusHouses} /></small>
                              <small>D-карты <VargaTerms vargas={relationshipRole.focusVargas} /></small>
                            </div>
                          ) : null}
                        </label>
                        <label className="related-profile-toggle">
                          <input
                            type="checkbox"
                            checked={relatedProfileIds.includes(profile.id)}
                            disabled={isBaseProfile}
                            onChange={() => toggleRelatedProfile(profile.id)}
                          />
                          <GlossaryTerm termKey="ai_context">{isBaseProfile ? "Базовая карта" : "Связанная карта"}</GlossaryTerm>
                        </label>
                        <button
                          type="button"
                          className="secondary-button self-profile-row-action"
                          onClick={() => handleMarkSelfProfile(profile, !profile.is_self_profile)}
                        >
                          {profile.is_self_profile ? "Не моя" : "Сделать моей"}
                        </button>
                        <button type="button" className="secondary-button" onClick={() => handleCalculateProfile(profile)}>
                          Загрузить
                        </button>
                      </div>
                    );
                  })}
                </div>
              ) : null}
            </div>
          </section>

          <section className="main-stack">
            <section className="panel chart-panel" id="varga-charts" ref={chartPanelRef}>
              <div className="panel-heading">
                <div className="chart-title-block">
                  <h2>{chartMode === "D1" ? "D1 Раши" : `${chartMode} ${selectedVarga?.name ?? "варга"}`}</h2>
                </div>
              </div>
              <div className="chart-layout">
                <div className="chart-visual-stack">
                  <ChartPreview chart={chart} varga={selectedVarga} chartStyle={chartStyle} chartReference={chartReference} termLanguage={termLanguage} houseHintsEnabled={houseHintsEnabled} />
                  {isCurrentChartLoading ? (
                    <div className="chart-loading-status" aria-live="polite">
                      <strong>Считаю карту</strong>
                    </div>
                  ) : null}
                  {!chart && !currentChartDefault ? <StartChartNotice /> : null}
                  <QuickVargaSwitch
                    chart={chart}
                    chartMode={chartMode}
                    vargaOptions={vargaOptions}
                    onChartModeChange={selectVargaCode}
                  />
                </div>
                <div className="chart-data-stack">
                  <ChartSideCalculationTable
                    chart={chart}
                    termLanguage={termLanguage}
                    status={status}
                    currentChartDefault={currentChartDefault}
                    selectedExplanation={selectedReaderExplanation}
                    onClearExplanation={() => setSelectedReaderExplanation(null)}
                    onRetryCurrentChart={submitCurrentChartCalculation}
                    onStartBirthCalculation={submitBirthCalculation}
                  />
                </div>
              </div>
            </section>

            {analysisWorkspaceOpen ? (
            <section className="analysis-workspace" id="reports">
              <div className="analysis-tab-shell">
                <div className="analysis-tabs" role="tablist" aria-label="Разделы анализа">
                  {primaryAnalysisTabs.map((tab) => (
                    <button
                      type="button"
                      key={tab.key}
                      className={activeAnalysisTab === tab.key ? "active" : ""}
                      data-analysis-tab={tab.key}
                      onClick={() => {
                        setAnalysisWorkspaceOpen(true);
                        setActiveAnalysisTab(tab.key);
                        window.history.pushState(null, "", `/?analysis=${tab.key}#reports`);
                      }}
                      role="tab"
                      aria-selected={activeAnalysisTab === tab.key}
                    >
                      <strong>{tab.label}</strong>
                    </button>
                  ))}
                </div>
                {secondaryAnalysisTabs.length ? (
                  <label className="analysis-more-tabs" aria-label="Дополнительный режим анализа">
                    <select
                      value={secondaryAnalysisTabs.some((tab) => tab.key === activeAnalysisTab) ? activeAnalysisTab : ""}
                      onChange={(event) => {
                        if (event.target.value) {
                          setAnalysisWorkspaceOpen(true);
                          setActiveAnalysisTab(event.target.value as AnalysisTab);
                          window.history.pushState(null, "", `/?analysis=${event.target.value}#reports`);
                        }
                      }}
                    >
                      <option value="">Режим</option>
                      {secondaryAnalysisTabs.map((tab) => (
                        <option value={tab.key} key={tab.key}>
                          {tab.label}
                        </option>
                      ))}
                    </select>
                  </label>
                ) : null}
              </div>
              <div className="analysis-panel-slot">
                {activeAnalysisTab === "overview" ? <PersonSummaryPanel summary={personSummary} /> : null}
                {activeAnalysisTab === "yogas" ? <ClassicalPanel classical={chart?.classical} /> : null}
                {activeAnalysisTab === "timeline" ? (
                  <DashaWorkspacePanel summary={personSummary} periods={vimshottariPeriods} extra={chart?.dashas?.extra} />
                ) : null}
                {activeAnalysisTab === "guidance" ? (
                  <ReportPreviewPanel
                    birthReport={birthReport}
                    draftAnalysis={draftAnalysis}
                    draftStatus={draftAnalysisStatus}
                    aiBillingStatus={aiBillingStatus}
                    onGenerateDraft={() => handleGenerateDraftAnalysis(false)}
                    onRegenerateDraft={() => handleGenerateDraftAnalysis(true)}
                    draftDisabled={!birthReport || aiAccessLocked || !activeSavedBirthProfile || !activeSavedBirthProfile.is_self_profile}
                    chatMessages={codexChatMessages}
                    chatStatus={codexChatStatus}
                    suggestedQuestion={suggestedCodexQuestion}
                    onAskDraftQuestion={handleAskDraftQuestion}
                    chatDisabled={!draftAnalysis || codexChatBusy || aiAccessLocked}
                  />
                ) : null}
                {activeAnalysisTab === "transits" ? (
                  <TransitPanel
                    report={transitReport}
                    status={workflowStatus}
                    currentDayStatus={currentDayStatus}
                    currentDayOverview={currentDayOverview}
                    currentDayBusy={currentDayBusy}
                    currentDayDisabled={aiAccessLocked}
                    onGenerateCurrentDay={handleGenerateCurrentDayOverview}
                  />
                ) : null}
                {activeAnalysisTab === "compatibility" ? (
                  <CompatibilityPanel
                    report={compatibilityReport}
                    status={compatibilityStatus}
                    profiles={profiles}
                    selectedPersonAProfileId={compatibilityPersonAProfileId}
                    selectedPersonBProfileId={compatibilityPersonBProfileId}
                    relationshipRole={compatibilityRelationshipRoleKey}
                    selectedRelationship={selectedCompatibilityRelationship}
                    personAChart={compatibilityPersonAChart}
                    personBChart={compatibilityPersonBChart}
                    chartStatus={compatibilityChartStatus}
                    chartStyle={chartStyle}
                    chartReference={chartReference}
                    termLanguage={termLanguage}
                    onRelationshipRoleChange={(role) => {
                      setActiveCompatibilityRelationshipId("");
                      setCompatibilityRelationshipRoleKey(role);
                      resetCompatibilityResultState();
                    }}
                    partnerProfileName={partnerProfileName}
                    partnerBirthDate={partnerBirthDate}
                    setPartnerBirthDate={setPartnerBirthDate}
                    partnerBirthTime={partnerBirthTime}
                    setPartnerBirthTime={setPartnerBirthTime}
                    partnerPlaceName={partnerPlaceName}
                    setPartnerPlaceName={setPartnerPlaceName}
                    setPartnerProfileName={setPartnerProfileName}
                    partnerPlaceMatches={partnerPlaceMatches}
                    selectedPartnerPlace={selectedPartnerPlace}
                    showPartnerPlaceSuggestions={showPartnerPlaceSuggestions}
                    setShowPartnerPlaceSuggestions={setShowPartnerPlaceSuggestions}
                    partnerPlaceSearchStatus={partnerPlaceSearchStatus}
                    onSelectPersonAProfile={handleSelectCompatibilityPersonAProfile}
                    onSelectPersonBProfile={handleSelectCompatibilityPersonBProfile}
                    onSelectPartnerPlace={selectPartnerPlace}
                    onSavePartnerProfile={handleSavePartnerProfile}
                    onSubmit={handleCompatibilitySubmit}
                    onGeneratePacket={handleCompatibilityPacket}
                    onGenerateCodexAnalysis={handleCompatibilityCodexAnalysis}
                    disabled={privateAccessLocked}
                    savePartnerDisabled={privateAccessLocked || !selectedPartnerPlace}
                    packetDisabled={privateAccessLocked}
                    packetStatus={compatibilityPacketStatus}
                    codexDisabled={privateAccessLocked || aiAccessLocked}
                    codexStatus={compatibilityCodexStatus}
                    codexAnalysis={compatibilityCodexAnalysis}
                    chatMessages={compatibilityChatMessages}
                    chatStatus={compatibilityChatStatus}
                    onAskCodexQuestion={handleAskCompatibilityQuestion}
                    chatDisabled={!compatibilityCodexAnalysis || compatibilityChatBusy || aiAccessLocked}
                  />
                ) : null}
                {activeAnalysisTab === "tithiPravesha" ? (
                  <TithiPraveshaPanel report={tithiPraveshaReport} status={workflowStatus} />
                ) : null}
                {activeAnalysisTab === "tajaka" ? <TajakaPanel report={tajakaReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "prashna" ? <PrashnaPanel report={prashnaReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "mundane" ? <MundanePanel report={mundaneReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "muhurta" ? <MuhurtaPanel report={muhurtaReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "accuracy" ? (
                  <AccuracyReportPanel
                    witnessSummary={witnessSummary}
                    witnessStatus={witnessSummaryStatus}
                    report={accuracyReport}
                    status={accuracyStatus}
                    plReport={plPacketReport}
                    plStatus={plPacketStatus}
                  />
                ) : null}
                {activeAnalysisTab === "sources" ? (
                  <section className="panel" id="sources">
                    <div className="panel-heading">
                      <h2>Источники</h2>
                    </div>
                    <form className="source-search" onSubmit={handleSourceSearch}>
                      <input value={sourceQuery} onChange={(event) => setSourceQuery(event.target.value)} />
                      <button type="submit" className="secondary-button">Искать</button>
                      <button type="button" className="secondary-button" onClick={handleResearchSearch}>Книги</button>
                    </form>
                    {sourceWorks.length ? (
                      <div className="source-work-list">
                        {sourceWorks.map((work) => (
                          <button
                            type="button"
                            key={work.slug}
                            className={selectedSourceWork?.slug === work.slug ? "selected" : ""}
                            onClick={() => setSelectedSourceWork(work)}
                          >
                            <strong>{work.title}</strong>
                            <span>{work.passage_count ?? 0} фрагм.</span>
                          </button>
                        ))}
                      </div>
                    ) : null}
                    {selectedSourceWork ? (
                      <div className="source-results research-results">
                        <div>
                          <strong>{selectedSourceWork.title}</strong>
                          <span>{selectedSourceWork.author || selectedSourceWork.edition || "Источник"}</span>
                        </div>
                        {sourcePassages.map((passage) => (
                          <div key={passage.id}>
                            <strong>{passage.reference}</strong>
                            <p>{passage.body}</p>
                          </div>
                        ))}
                      </div>
                    ) : null}
                    {sourceResults.length ? (
                      <div className="source-results">
                        {sourceResults.map((result) => (
                          <a href={result.public_url || "#"} key={result.id} target="_blank" rel="noreferrer">
                            <strong>{result.title || result.work_title}</strong>
                            <span>{result.work_title}</span>
                            <p>{result.body}</p>
                          </a>
                        ))}
                      </div>
                    ) : null}
                    {researchResults.length ? (
                      <div className="source-results research-results">
                        {researchResults.map((result) => (
                          <div key={`${result.work_title}-${result.title}`}>
                            <strong>{result.title}</strong>
                            <span>{result.work_title}</span>
                            <p>{result.body}</p>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </section>
                ) : null}
              </div>
            </section>
            ) : null}
          </section>
        </div>
        )}
      </section>
    </main>
  );
}
