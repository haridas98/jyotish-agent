"use client";

import { FormEvent, useCallback, useEffect, useId, useMemo, useRef, useState, type Dispatch, type ReactNode, type RefObject, type SetStateAction } from "react";
import {
  askBirthCodexAnalysis,
  askCompatibilityCodexAnalysis,
  calculateCompatibility,
  calculateDualCalculation,
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
  fetchShastraEvidence,
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
  type DualCalculationReport,
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
  type ShastraEvidencePayload,
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
  type WorkflowInterpretationPlan,
  type VLSearchResult,
} from "@/lib/api";
import {
  firstSymbolLineY,
  northIndianHouseCells,
  northIndianHousePolygons,
  safeSymbolCenterY,
} from "@/lib/northIndianChartGeometry";
import { InterfaceModeSwitch, INTERFACE_MODE_STORAGE_KEY, type InterfaceMode } from "@/app/interface-mode-switch";
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

const sourceRows = [
  ["Айанамша", "Lahiri", "Рабочий профиль; JHora diff подключён", "ready"],
  ["Система карты", "Drik Siddhanta / Swiss-JPL", "Профиль JHora-сравнения подключён", "ready"],
  ["Корпус VL", "База Шрилы Прабхупады", "Поиск подключён", "ready"],
];

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
  { key: "accuracy", label: "Точность", hint: "JHora diff" },
  { key: "guidance", label: "Разбор", hint: "цитаты" },
  { key: "sources", label: "Источники", hint: "VL" },
] as const;

type AnalysisTab = (typeof analysisTabs)[number]["key"];
type ChartWorkspaceTab = "essentials" | "references" | "vargas";

function analysisTabFromLocation(): AnalysisTab {
  if (typeof window === "undefined") return "overview";
  const requestedAnalysis = new URLSearchParams(window.location.search).get("analysis");
  return requestedAnalysis && analysisTabs.some((tab) => tab.key === requestedAnalysis)
    ? (requestedAnalysis as AnalysisTab)
    : "overview";
}

const primaryAnalysisTabKeys = new Set<AnalysisTab>([
  "overview",
  "calculations",
  "yogas",
  "timeline",
  "transits",
  "guidance",
  "sources",
]);
const primaryAnalysisTabs = analysisTabs.filter((tab) => primaryAnalysisTabKeys.has(tab.key));
const secondaryAnalysisTabs = analysisTabs.filter((tab) => !primaryAnalysisTabKeys.has(tab.key));
const chartWorkspaceTabs: Array<{ key: ChartWorkspaceTab; label: string; hint: string }> = [
  { key: "essentials", label: "Главные карты", hint: "D1, D9, D10" },
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
  draft_needs_citation: "рабочий текст",
  draft_needs_jhora_audit: "рабочий расчёт",
  calculated_needs_citation: "расчёт готов",
  calculated_needs_jhora_audit: "расчёт готов",
  calculated_needs_jhora_component_audit: "расчёт готов",
  calculated_source_backed_needs_jhora_profile_audit: "рассчитано по шастре, открыт JHora profile diff",
  calculated_with_tradition_profile_needs_jhora_audit: "расчёт готов",
  calculated_bphs_varga_viswa_single_jhora_profile_audited: "BPHS Varga Viswa, сверено на JHora profile",
  calculated_bphs_varga_viswa_weights_fixed_profile_diff_open: "BPHS веса исправлены, открыт JHora profile diff",
  calculated_bphs_varga_viswa_jhora_fixture_matched: "BPHS Varga Viswa, сверено с JHora fixture",
  calculated_jhora_fixture_matched: "сверено с JHora fixture",
  calculated_single_jhora_fixture_matched_partial_catalog: "проверенные точки сверены с JHora",
  calculated_single_jhora_fixture_matched_core_catalog: "core-точки сверены с JHora",
  calculated_needs_jhora_split_profile: "рассчитано, нужен JHora split-профиль",
  baseline_calculated_needs_jhora_tajaka_audit: "базово рассчитано, нужен Tajaka/JHora audit",
  baseline_calculated_needs_full_tajaka_audit: "базово рассчитано, нужен полный Tajaka audit",
  baseline_calculated_needs_prashna_tradition_review: "рабочий расчёт",
  baseline_event_chart_needs_mundane_rules_review: "рабочий расчёт",
  partial_extra_dasha_catalog: "частичный каталог даш",
  calculated_needs_tradition_review: "расчёт готов",
  calculated_needs_task_review: "расчёт готов",
  partial_calculated_needs_citation: "рабочий слой",
  partial_calculated_needs_jhora_audit: "рабочий слой",
  partial_calculated_needs_jhora_profile_audit: "частично рассчитано, открыт JHora profile diff",
  calculated_needs_source_audit: "рассчитано, нужен аудит источника",
  pending_source_mapping: "источники подключаются",
  pending_jhora_audit: "ждёт сверку JHora",
  pending_endpoint: "ждёт API",
  api_available: "API готов",
  complete_baseline_needs_jhora_audit: "рабочий расчёт",
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
  calculated_jhora_profile_diff_open: "открыт JHora diff",
  calculated_single_jhora_fixture_matched_partial_catalog: "частичный каталог сверен с JHora",
  calculated_single_jhora_fixture_matched_core_catalog: "core-каталог сверен с JHora",
  calculated_bphs_varga_viswa_weights_fixed_profile_diff_open: "BPHS веса исправлены, открыт JHora diff",
  calculated_bphs_varga_viswa_jhora_fixture_matched: "BPHS Varga Viswa сверена с JHora",
  calculated_needs_jhora_split_profile: "нужен JHora split-профиль",
  partial: "частично",
  temporary_proxy: "временная формула",
  partial_detection_needs_citations: "рабочий слой",
  partial_gulika_only: "только Гулика",
  baseline_api_ready: "API готов, правила не финальны",
  baseline_ashtakuta: "базовая аштакута",
  baseline_scoring: "базовая оценка",
  multi_factor_calculated_needs_shastra_review: "многофакторный расчёт",
  source_backed: "есть шастра",
  source_backed_with_bphs_caution: "есть шастра, BPHS осторожно",
  source_backed_but_tradition_sensitive: "по шастрам",
  source_backed_but_pastoral_review_required: "по шастрам",
  needs_tradition_decision: "рабочий слой",
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
  vargas_d2_d60: "Правила варг требуют сверки вариантов, особенно если правило взято из modern BPHS.",
  panchanga: "Угловые деления Солнце-Луна и правила панчанги/мухурты.",
  vimshottari: "Уду-даша от накшатры Луны, 120-летний цикл и классическая последовательность грах.",
  avasthas: "Авастхи по градусным диапазонам с учётом нечётных/чётных знаков.",
  ashtakavarga: "Brhat Jataka IX и стандартная сумма SAV 337 бинду.",
  shadbala: "Шесть групп шадбалы рассчитаны по компонентам и готовы для личного разбора.",
  vimshopaka: "BPHS веса shadvarga/sapta/dasha/shodasha рассчитаны; Sterlitamak JHora fixture 36/36.",
  yogas: "Показываются условия йог, но не окончательное предсказание.",
  argala: "Структурная аргала рассчитана как рабочий слой анализа.",
  upagrahas: "Гулика, Маанди и солнечные упаграхи сверены на Sterlitamak JHora fixture.",
  special_points: "Indu/Bhava/Hora/Ghati и upagraha core-точки сверены на Sterlitamak JHora fixture.",
  transits: "API готов, правила интерпретации транзитов ещё не финальны.",
  compatibility: "Аштакута плюс многофакторный анализ двух карт.",
  muhurta: "Базовая оценка окна, не финальная элекция.",
};

auditSourceBasisRu.shadbala =
  "Шадбала рассчитана по компонентам: Sthana, Dig, Kala, Chesta, Drik и Naisargika.";

const authorityOrderRu: Record<string, string> = {
  "older shastra and reviewed parampara instruction": "старшие шастры и проверенное наставление парампары",
  "astronomical ephemeris and timezone audit": "астрономическая точность, эфемериды и часовой пояс",
  "JHora and external services as black-box witnesses": "JHora и сервисы только как свидетели",
  "internal regression fixtures": "внутренние regression fixtures",
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

const settingsLabelsRu: Record<string, string> = {
  zodiac: "Зодиак",
  calculation_model: "Модель",
  ayanamsa: "Айанамша",
  node_type: "Узлы",
  ephemeris: "Эфемериды",
  house_system: "Дома",
  bhava_system: "Бхава",
  varga_scheme: "Варги",
  sunrise_source: "Восход",
  timezone_source: "Часовой пояс",
  shadbala_profile: "Шадбала",
};

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
  if (!value) return "рабочий слой";
  if (value.startsWith("source_backed")) return "по шастрам";
  if (value.startsWith("needs")) return "рабочий слой";
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
  if (status.startsWith("partial")) return "рабочий слой";
  if (status.startsWith("baseline") || status === "api_available") return "рабочий расчёт";
  if (status === "api_ready") return "API готов";
  return auditStatusRu(status);
}

function auditInterpretationReadyRu(ready: boolean) {
  return ready ? "готово" : "в работе";
}

function generatedStatusRu(status: string | null | undefined) {
  if (status === "private_final") return "готовый личный разбор";
  if (status === "private_partial") return "неполный личный разбор";
  if (status === "draft") return "личный рабочий разбор";
  if (status === "approved") return "утверждено";
  return status || "ожидает";
}

function generatedTitleRu(status: string | null | undefined) {
  if (status === "private_final" || status === "approved") return "Готовый личный разбор";
  if (status === "private_partial") return "Неполный личный разбор";
  return "Рабочий личный разбор";
}

function workflowStatusRu(status: string | null | undefined) {
  if (!status) return "готово";
  if (status.includes("pending") || status.includes("missing")) return "ожидает данных";
  if (status.includes("calculated") || status.includes("ready") || status.includes("approved")) return "готово";
  return "рабочий слой";
}

function reportSectionStatusRu(status: string | null | undefined) {
  if (!status) return "готово";
  if (status === "calculation_only") return "расчёт";
  if (status === "private_final" || status === "approved") return "готово";
  return "рабочий текст";
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
    text: "Рабочий слой для болезней, долгов, врагов, споров и конфликтного напряжения.",
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
    text: "Основная карта владельца аккаунта. Первый личный AI-разбор даётся именно для этой карты; чужие карты можно хранить отдельно.",
  },
  free_personal_ai: {
    label: "Первый AI-разбор",
    text: "Бесплатный личный разбор относится к вашей собственной карте. Если разбор уже создан, повторное открытие показывает сохранённую историю.",
  },
  relationship_role: {
    label: "Роль человека",
    text: "Ракурс чтения второй карты: партнёр, отец, мать, брат, руководитель, оппонент и т.д. От роли зависят дома и D-карты, которые AI должен учитывать.",
  },
  relationship_status: {
    label: "Статус связи",
    text: "Показывает приватность связи: личная пометка видна только вам, запрос ждёт согласия, подтверждённая связь видна обоим зарегистрированным пользователям.",
  },
  saved_other_chart: {
    label: "Чужая сохранённая карта",
    text: "Карту другого человека можно сохранить и просматривать. Ограничение относится к AI-разбору, а не к самому хранению карты.",
  },
  paid_other_ai: {
    label: "AI-разбор чужой карты",
    text: "После запуска оплаты AI-разбор чужой карты будет платным. Сейчас бесплатный личный разбор предназначен только для собственной карты аккаунта.",
  },
  mvp_readiness: {
    label: "Готовность MVP",
    text: "Показывает, какие функции уже можно проверять астрологам, а какие остаются следующим этапом разработки.",
  },
  ai_context: {
    label: "Контекст AI",
    text: "Отмеченные карты и их сохранённые обзоры можно передавать AI как дополнительный контекст при личном разборе.",
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

function ChartHouseExplanation({
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
}) {
  const item = jyotishGlossary[houseGlossaryKey(house)];
  const houseItem = northIndianHouseItems(chart, varga, chartReference).find((row) => row.house === house);
  const rashiIndex = houseItem?.rashiIndex ?? null;
  const rashiLabel = rashiIndex === null
    ? "-"
    : rashiTermFromName(houseItem?.rashi ?? rashiNames[rashiIndex], termLanguage);
  const lordBody = rashiIndex === null ? null : rashiLordBodies[rashiIndex];
  const placements = houseItem?.placements ?? [];
  const placementText = placements.length
    ? placements.map((placement) => chartPlacementLabel(placement, termLanguage)).join(", ")
    : "нет грах";
  const referenceLabel = chartReferenceOptions.find((option) => option.key === chartReference)?.label ?? "Лагна";
  return (
    <div className="chart-cell-explanation" aria-live="polite">
      <strong>{item.label}</strong>
      <span>{item.text}</span>
      <dl>
        <div>
          <dt>
            <GlossaryTerm termKey="rashi">Знак</GlossaryTerm>
          </dt>
          <dd>{rashiLabel}</dd>
        </div>
        <div>
          <dt>
            <GlossaryTerm termKey="ruled_houses">Хозяин</GlossaryTerm>
          </dt>
          <dd>{lordBody ? grahaTermLabel(lordBody, termLanguage) : "-"}</dd>
        </div>
        <div>
          <dt>
            <GlossaryTerm termKey="graha">Грахи</GlossaryTerm>
          </dt>
          <dd>{placementText}</dd>
        </div>
      </dl>
      <em>Ракурс домов: {referenceLabel}. Чтение: сфера дома, знак, хозяин, грахи внутри, D9 и даша.</em>
      <button
        type="button"
        className="help-ai-action chart-cell-ai-action"
        onClick={() =>
          requestAiExplanation({
            title: `${item.label} в карте`,
            text: `Ракурс: ${referenceLabel}. Знак: ${rashiLabel}. Хозяин: ${lordBody ? grahaTermLabel(lordBody, termLanguage) : "-"}. Грахи: ${placementText}.`,
          })
        }
      >
        Спросить AI об этом доме
      </button>
      <small>Нажмите другой дом на карте, чтобы сменить пояснение.</small>
    </div>
  );
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
  return (
    <div
      className="chart-house-popover"
      style={{ left: `${position.x}%`, top: `${position.y}%` }}
      role="tooltip"
      onPointerDown={(event) => event.stopPropagation()}
    >
      <div className="chart-house-popover-head">
        <strong>{item.label}</strong>
        <button type="button" onClick={onClose} aria-label="Закрыть подсказку">×</button>
      </div>
      <span>{item.text}</span>
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
            text: `Ракурс: ${referenceLabel}. Знак: ${rashiLabel}. Хозяин: ${lordBody ? grahaTermLabel(lordBody, termLanguage) : "-"}. Грахи: ${placementText}.`,
          })
        }
      >
        Спросить AI
      </button>
    </div>
  );
}

function StartChartNotice() {
  return (
    <div className="start-chart-notice" aria-label="Карта ещё не рассчитана">
      <strong>Карта не запускается автоматически</strong>
      <span>Это снижает нагрузку на сервер. Проверьте данные рождения и нажмите «Рассчитать карту».</span>
      <a href="#birth-form">Перейти к данным рождения</a>
    </div>
  );
}

function CoreVargaMiniRail({
  chart,
  activeCode,
  chartStyle,
  chartReference,
  termLanguage,
  onSelect,
}: {
  chart: BirthChart | null;
  activeCode: string;
  chartStyle: "north" | "south";
  chartReference: ChartReference;
  termLanguage: TermLanguage;
  onSelect: (code: string) => void;
}) {
  const comparisonCode = activeCode === "D1" || activeCode === "D9" ? "D10" : activeCode;
  const items = Array.from(new Set(["D1", "D9", comparisonCode])).slice(0, 3).map((code) => {
    const varga = code === "D1" ? null : chart?.vargas?.[code] ?? null;
    return {
      code,
      available: code === "D1" ? Boolean(chart) : Boolean(varga),
      title: code === "D1" ? "Раши" : priorityVargaContexts[code]?.scope ?? "Варга",
      hint: priorityVargaContexts[code]?.detail ?? "ключевая карта",
      varga,
    };
  });

  return (
    <div className="core-varga-mini-rail" aria-label="Быстрый визуальный контекст D1 D9 D10">
      {items.map((item) => (
        <button
          type="button"
          className={`${activeCode === item.code ? "active" : ""}${item.available ? " ready" : ""}`}
          disabled={!item.available}
          key={item.code}
          onClick={() => onSelect(item.code)}
        >
          <div>
            <strong>{item.code}</strong>
            <span>{item.title}</span>
          </div>
          <div className="core-varga-mini-preview">
            {item.available ? (
              chartStyle === "south" ? (
                <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact termLanguage={termLanguage} />
              ) : (
                <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact termLanguage={termLanguage} />
              )
            ) : (
              <em>{item.hint}</em>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}

function PractitionerVargaRail({
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
  const items = practitionerVargaCodes.map((code) => {
    const varga = code === "D1" ? null : chart?.vargas?.[code] ?? null;
    return {
      code,
      available: code === "D1" ? Boolean(chart) : Boolean(varga),
      varga,
      scope: priorityVargaContexts[code]?.scope ?? vargaPurposeLabels[code] ?? "Варга",
      detail: priorityVargaContexts[code]?.detail ?? "ключевая D-карта",
    };
  });

  return (
    <div className="practitioner-varga-rail" aria-label="Ключевые D-карты для быстрого чтения">
      <div className="practitioner-varga-rail-head">
        <strong>D-карты рядом</strong>
        <span>D1, D9, D10, D12, D30 и D60 видны без перехода в отдельное окно</span>
      </div>
      <div className="practitioner-varga-rail-list">
        {items.map((item) => (
          <button
            type="button"
            className={activeCode === item.code ? "active" : ""}
            disabled={!item.available}
            key={item.code}
            onClick={() => onSelect(item.code)}
          >
            <div>
              <strong>{item.code}</strong>
              <span>{item.scope}</span>
              <small>{item.available ? item.detail : unavailableVargaLabel(item.code)}</small>
            </div>
            <div className="practitioner-varga-preview">
              {item.available ? (
                chartStyle === "south" ? (
                  <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact />
                ) : (
                  <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact />
                )
              ) : (
                <em>{unavailableVargaLabel(item.code)}</em>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function ShodashaMiniAtlas({
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
  const readyCount = shodashaVargaCodes.filter((code) => code === "D1" ? Boolean(chart) : Boolean(chart?.vargas?.[code])).length;
  const items = shodashaVargaCodes.map((code) => {
    const varga = code === "D1" ? null : chart?.vargas?.[code] ?? null;
    return {
      code,
      varga,
      available: code === "D1" ? Boolean(chart) : Boolean(varga),
      scope: priorityVargaContexts[code]?.scope ?? vargaPurposeLabels[code] ?? "Варга",
    };
  });

  return (
    <div className="shodasha-mini-atlas" aria-label="Shodasha Varga: 16 основных D-карт">
      <div className="shodasha-mini-head">
        <div>
          <strong>Shodasha Varga</strong>
          <span>16 основных карт: D1-D60</span>
        </div>
        <em>{readyCount}/16 готово</em>
      </div>
      <div className="shodasha-mini-grid">
        {items.map((item) => (
          <button
            type="button"
            className={`${activeCode === item.code ? "active" : ""}${item.available ? " ready" : ""}`}
            disabled={!item.available}
            key={item.code}
            onClick={() => onSelect(item.code)}
          >
            <div>
              <strong>{item.code}</strong>
              <span>{item.scope}</span>
            </div>
            <div className="shodasha-mini-preview">
              {item.available ? (
                chartStyle === "south" ? (
                  <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact />
                ) : (
                  <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact />
                )
              ) : (
                <em>нет расчёта</em>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function KeyVargaComparisonPanel({
  chart,
  activeCode,
  chartStyle,
  chartReference,
  termLanguage,
  onSelect,
}: {
  chart: BirthChart | null;
  activeCode: string;
  chartStyle: "north" | "south";
  chartReference: ChartReference;
  termLanguage: TermLanguage;
  onSelect: (code: string) => void;
}) {
  const fallbackCode = activeCode === "D1" || activeCode === "D9" ? "D10" : activeCode;
  const codes = Array.from(new Set(["D1", "D9", fallbackCode])).slice(0, 3);
  const items = codes.map((code) => {
    const varga = code === "D1" ? null : chart?.vargas?.[code] ?? null;
    const available = code === "D1" ? Boolean(chart) : Boolean(varga);
    return {
      code,
      varga,
      available,
      scope: priorityVargaContexts[code]?.scope ?? vargaPurposeLabels[code] ?? "Варга",
      detail: priorityVargaContexts[code]?.detail ?? "дополнительный слой чтения",
    };
  });

  return (
    <div className="key-varga-comparison" aria-label="Сравнение D1 D9 и рабочей варги">
      <div className="key-varga-comparison-head">
        <strong>Три опоры чтения</strong>
        <span>D1 показывает основу, D9 силу грах, третья карта раскрывает выбранную сферу</span>
      </div>
      <div className="key-varga-comparison-grid">
        {items.map((item) => (
          <button
            type="button"
            className={`${activeCode === item.code ? "active" : ""}${item.available ? " ready" : ""}`}
            disabled={!item.available}
            key={item.code}
            onClick={() => onSelect(item.code)}
          >
            <div className="key-varga-copy">
              <strong>{item.code}</strong>
              <span>{item.scope}</span>
              <small>{item.available ? item.detail : unavailableVargaLabel(item.code)}</small>
            </div>
            <div className="key-varga-preview">
              {item.available ? (
                chartStyle === "south" ? (
                  <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact termLanguage={termLanguage} />
                ) : (
                  <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact termLanguage={termLanguage} />
                )
              ) : (
                <em>нет расчёта</em>
              )}
            </div>
          </button>
        ))}
      </div>
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
            title={glossaryItem?.text}
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

function ChartDisplayControls({
  chart,
  chartMode,
  chartStyle,
  vargaOptions,
  onChartModeChange,
  onChartStyleChange,
}: {
  chart: BirthChart | null;
  chartMode: string;
  chartStyle: "north" | "south";
  vargaOptions: string[];
  onChartModeChange: (value: string) => void;
  onChartStyleChange: (value: "north" | "south") => void;
}) {
  const options = vargaOptions.length ? vargaOptions : ["D1"];

  return (
    <div className="chart-display-controls" aria-label="Быстрые настройки отображения карты">
      <label>
        <span>Карта</span>
        <select value={chartMode} disabled={!chart} onChange={(event) => onChartModeChange(event.target.value)}>
          {options.map((code) => (
            <option value={code} key={`chart-display-${code}`}>
              {code}{vargaPurposeLabels[code] ? ` · ${vargaPurposeLabels[code]}` : ""}
            </option>
          ))}
        </select>
      </label>
      <div className="chart-style-inline-toggle" role="group" aria-label="Стиль карты">
        <button type="button" className={chartStyle === "north" ? "active" : ""} onClick={() => onChartStyleChange("north")}>
          Северный
        </button>
        <button type="button" className={chartStyle === "south" ? "active" : ""} onClick={() => onChartStyleChange("south")}>
          Южный
        </button>
      </div>
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
  const [hoveredHouse, setHoveredHouse] = useState<number | null>(null);
  const [pinnedHouse, setPinnedHouse] = useState<number | null>(null);
  const activeHouse = houseHintsEnabled ? pinnedHouse ?? hoveredHouse : null;
  const activeCell = activeHouse ? northIndianHouseCells[activeHouse] : null;
  return (
    <>
      <div className="chart-box" aria-label="Предпросмотр североиндийской карты">
        <NorthIndianChartSvg
          chart={chart}
          varga={varga}
          chartReference={chartReference}
          termLanguage={termLanguage}
          onHouseSelect={houseHintsEnabled ? (house) => setPinnedHouse((current) => (current === house ? null : house)) : undefined}
          onHouseHover={houseHintsEnabled ? setHoveredHouse : undefined}
          onHouseLeave={houseHintsEnabled ? () => setHoveredHouse(null) : undefined}
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
              setHoveredHouse(null);
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
  onHouseHover,
  onHouseLeave,
  selectedHouse,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference?: ChartReference;
  compact?: boolean;
  termLanguage?: TermLanguage;
  onHouseSelect?: (house: number) => void;
  onHouseHover?: (house: number) => void;
  onHouseLeave?: () => void;
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
              onMouseEnter={onHouseHover ? () => onHouseHover(house.house) : undefined}
              onMouseLeave={onHouseLeave}
              onFocus={onHouseHover ? () => onHouseHover(house.house) : undefined}
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
              <title>{`${house.house} дом. Знак ${signLabel}: ${house.placements.map((placement) => fullPlacementTitle(placement, termLanguage)).join("; ") || "пусто"}`}</title>
              {onHouseSelect && hitPolygon ? (
                <polygon
                  className="chart-house-hit-zone"
                  points={hitPolygon.map((point) => `${point.x},${point.y}`).join(" ")}
                  onClick={() => onHouseSelect(house.house)}
                />
              ) : null}
              <text
                className={`chart-cell-text${textLines.length > 5 ? " dense" : ""}`}
                x={cell.centerX}
                y={firstLineY}
                textAnchor="middle"
              >
                {textLines.map((line, index) => (
                  <tspan
                    className={`${line.kind === "rashi" ? "chart-rashi-label" : "chart-graha-detail"}${line.dignity ? ` dignity-${line.dignity}` : ""}${line.retrograde ? " retrograde" : ""}`}
                    key={`${house.house}-${line.text}-${index}`}
                    x={cell.centerX}
                    dy={index === 0 ? 0 : lineGap}
                  >
                    {line.text}
                  </tspan>
                ))}
              </text>
            </g>
          );
        })}
        {!chart ? (
          <text className="chart-empty-label" x="200" y="206" textAnchor="middle">
            ожидает расчёта
          </text>
        ) : null}
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
  const [hoveredHouse, setHoveredHouse] = useState<number | null>(null);
  const [pinnedHouse, setPinnedHouse] = useState<number | null>(null);
  const activeHouse = houseHintsEnabled ? pinnedHouse ?? hoveredHouse : null;
  const activePosition = activeHouse ? southIndianHouseTooltipPosition(chart, varga, chartReference, activeHouse) : null;
  return (
    <>
      <div className="chart-box south-chart-box" aria-label="Предпросмотр южноиндийской карты">
        <SouthIndianChartGrid
          chart={chart}
          varga={varga}
          chartReference={chartReference}
          termLanguage={termLanguage}
          onHouseSelect={houseHintsEnabled ? (house) => setPinnedHouse((current) => (current === house ? null : house)) : undefined}
          onHouseHover={houseHintsEnabled ? setHoveredHouse : undefined}
          onHouseLeave={houseHintsEnabled ? () => setHoveredHouse(null) : undefined}
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
              setHoveredHouse(null);
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
  onHouseHover,
  onHouseLeave,
  selectedHouse,
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
  chartReference?: ChartReference;
  compact?: boolean;
  termLanguage?: TermLanguage;
  onHouseSelect?: (house: number) => void;
  onHouseHover?: (house: number) => void;
  onHouseLeave?: () => void;
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
            title={house ? `${house} дом` : undefined}
            onClick={interactive && house ? () => onHouseSelect?.(house) : undefined}
            onMouseEnter={interactive && house ? () => onHouseHover?.(house) : undefined}
            onMouseLeave={onHouseLeave}
            onFocus={interactive && house ? () => onHouseHover?.(house) : undefined}
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
              <span className={`${placement.dignity ? `dignity-${placement.dignity}` : ""}${placement.retrograde ? " retrograde" : ""}`} key={`${rashiIndex}-${placement.body}`}>
                {chartPlacementLabel(placement, termLanguage)}
              </span>
            ))}
            {cellPlacements.length > (compact ? 4 : 7) ? <em>+{cellPlacements.length - (compact ? 4 : 7)}</em> : null}
          </div>
        );
      })}
      {!chart ? <span className="south-chart-empty">ожидает расчёта</span> : null}
    </div>
  );
}

function northIndianCellLines(house: NorthIndianHouseItem, compact = false, termLanguage: TermLanguage = "sanskrit"): ChartTextLine[] {
  if (compact) {
    const placements = house.placements.map((placement) => ({
      text: chartPlacementLabel(placement, termLanguage),
      kind: "graha" as const,
      dignity: placement.dignity,
      retrograde: placement.retrograde,
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

const vargaPriorityLabels: Record<string, string> = {
  D1: "основа",
  D5: "джайм.",
  D6: "джайм.",
  D7: "семья",
  D8: "джайм.",
  D9: "must",
  D10: "дело",
  D11: "джайм.",
  D12: "род",
  D20: "дух",
  D24: "учёба",
  D30: "риск",
  D40: "мать",
  D45: "отец",
  D60: "тонко",
};

const vargaFocusGroups: Array<{
  key: string;
  label: string;
  hint: string;
  title: string;
  description: string;
  codes: readonly string[];
}> = [
  {
    key: "core",
    label: "База",
    hint: "D1, D9, D10, D12, D30, D60",
    title: "Главные карты для чтения",
    description: "D1 и D9 держат основу, D10 показывает дело, D12 род, D30 риски, D60 тонкий кармический слой.",
    codes: ["D1", "D9", "D10", "D12", "D30", "D60"],
  },
  {
    key: "marriage",
    label: "Брак",
    hint: "D9, D1, D7",
    title: "Отношения и брак",
    description: "Проверяются 7 дом D1, Навамша D9, дети/потомство через D7 и общая сила Шукра/Гуру.",
    codes: ["D9", "D1", "D7"],
  },
  {
    key: "career",
    label: "Дело",
    hint: "D10, D1, D24",
    title: "Работа и призвание",
    description: "D10 показывает карму профессии, D24 поддерживает обучение и квалификацию, D1 держит контекст.",
    codes: ["D10", "D1", "D24"],
  },
  {
    key: "wealth",
    label: "Деньги",
    hint: "D2, D11, D1",
    title: "Ресурсы и доход",
    description: "D2 показывает накопление и питание ресурсов, D11 — доходы и прибыли после сверки, D1 держит общий контекст.",
    codes: ["D2", "D11", "D1"],
  },
  {
    key: "health",
    label: "Здоровье",
    hint: "D6, D30, D1",
    title: "Здоровье, долги и препятствия",
    description: "D6 нужен для болезней, долгов и врагов после сверки правил; D30 показывает повреждения и риски.",
    codes: ["D6", "D30", "D1"],
  },
  {
    key: "parents",
    label: "Род",
    hint: "D12, D40, D45",
    title: "Родители и род",
    description: "D12 даёт родителей, D40 материнскую линию, D45 отцовскую линию.",
    codes: ["D12", "D40", "D45"],
  },
  {
    key: "sadhana",
    label: "Дух",
    hint: "D20, D9, D1",
    title: "Садхана и духовная опора",
    description: "D20 показывает духовную практику, D9 — дхармическую зрелость, D1 — общий носитель жизни.",
    codes: ["D20", "D9", "D1"],
  },
  {
    key: "jaimini",
    label: "Дж.",
    hint: "D5, D6, D8, D11",
    title: "Дополнительные карты Джаимини",
    description: "D5, D6, D8 и D11 выделены отдельным набором; откроются после добавления проверенных правил расчёта.",
    codes: ["D5", "D6", "D8", "D11"],
  },
  {
    key: "karma",
    label: "Карма",
    hint: "D30, D60",
    title: "Риски и карма",
    description: "D30 показывает трудности и повреждения, D60 — тонкий кармический слой при точном времени.",
    codes: ["D30", "D60"],
  },
];

function availableCodeForVargaGroup(chart: BirthChart | null, group: (typeof vargaFocusGroups)[number]) {
  return availableCodeForVargaCodes(chart, group.codes);
}

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
  return jaiminiVargaCodeSet.has(code) ? "нужна сверка" : "нет расчёта";
}

const chartQuickSwitchCodes = vargaSnapshotCodes;
const primaryVargaTabCodes = ["D1", "D9", "D10", "D12", "D30", "D60"] as const;
const secondaryVargaQuickCodes = ["D2", "D3", "D4", "D7", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"] as const;
const practitionerVargaCodes = ["D1", "D9", "D10", "D7", "D12", "D20", "D24", "D30", "D60"] as const;

const priorityVargaContexts: Record<string, { scope: string; detail: string }> = {
  D1: { scope: "Основа", detail: "тело, характер, дома" },
  D2: { scope: "Ресурс", detail: "деньги, питание, опора" },
  D3: { scope: "Смелость", detail: "братья, усилие, воля" },
  D4: { scope: "Дом", detail: "недвижимость, счастье" },
  D5: { scope: "Власть", detail: "слава, полномочия" },
  D6: { scope: "Здоровье", detail: "болезни, долги, враги" },
  D7: { scope: "Дети", detail: "потомство, творчество" },
  D8: { scope: "Внезапное", detail: "скрытые переломы и риски" },
  D9: { scope: "Дхарма", detail: "брак, сила грах" },
  D10: { scope: "Карьера", detail: "дело, статус, работа" },
  D11: { scope: "Рудра", detail: "разрушение, предельные события" },
  D12: { scope: "Род", detail: "отец, мать, наследие" },
  D16: { scope: "Комфорт", detail: "транспорт, удобства" },
  D20: { scope: "Дух", detail: "садхана, вера" },
  D24: { scope: "Учёба", detail: "знание, образование" },
  D27: { scope: "Сила", detail: "выносливость, слабости" },
  D30: { scope: "Риски", detail: "трудности, повреждения" },
  D40: { scope: "Мат. род", detail: "линия матери" },
  D45: { scope: "Отц. род", detail: "линия отца" },
  D60: { scope: "Карма", detail: "тонкий итог при точном времени" },
};

function VargaTaskMatrix({
  chart,
  activeGroupKey,
  onSelect,
}: {
  chart: BirthChart | null;
  activeGroupKey: string;
  onSelect: (groupKey: string, code: string) => void;
}) {
  return (
    <div className="varga-task-matrix" aria-label="D-карты по жизненным задачам">
      {vargaFocusGroups.map((group) => {
        const selectedCode = availableCodeForVargaGroup(chart, group);
        return (
          <button
            type="button"
            className={activeGroupKey === group.key ? "active" : ""}
            disabled={!selectedCode}
            key={group.key}
            onClick={() => {
              if (!selectedCode) return;
              onSelect(group.key, selectedCode);
            }}
          >
            <strong>{group.title}</strong>
            <span>{group.hint}</span>
          </button>
        );
      })}
    </div>
  );
}

function VargaSchemeMatrix({
  chart,
  activeSchemeKey,
  onSelect,
}: {
  chart: BirthChart | null;
  activeSchemeKey: VargaSchemeKey;
  onSelect: (schemeKey: VargaSchemeKey, code: string) => void;
}) {
  return (
    <div className="varga-scheme-matrix" aria-label="Classical varga schemes">
      {vargaSchemeGroups.map((scheme) => {
        const selectedCode = availableCodeForVargaCodes(chart, scheme.codes);
        return (
          <button
            type="button"
            className={activeSchemeKey === scheme.key ? "active" : ""}
            disabled={!selectedCode}
            key={scheme.key}
            onClick={() => {
              if (!selectedCode) return;
              onSelect(scheme.key, selectedCode);
            }}
          >
            <span>{scheme.label}</span>
            <strong>{scheme.title}</strong>
            <small>{scheme.hint}</small>
          </button>
        );
      })}
    </div>
  );
}

function VargaStudyBoard({
  chart,
  activeGroupKey,
  activeCode,
  chartStyle,
  chartReference,
  onSelect,
}: {
  chart: BirthChart | null;
  activeGroupKey: string;
  activeCode: string;
  chartStyle: "north" | "south";
  chartReference: ChartReference;
  onSelect: (code: string) => void;
}) {
  const group = vargaFocusGroups.find((item) => item.key === activeGroupKey) ?? vargaFocusGroups[0];
  const items = group.codes.map((code) => {
    if (code === "D1") {
      return { code, name: "Раши", available: Boolean(chart), varga: null };
    }
    const varga = chart?.vargas?.[code];
    return { code, name: varga?.name ?? "Варга", available: Boolean(varga), varga: varga ?? null };
  });

  return (
    <div className="varga-study-board" aria-label="Фокусный набор варга-карт">
      <div className="varga-study-head">
        <div>
          <strong>{group.title}</strong>
          <span>{group.description}</span>
        </div>
        <small>{group.hint}</small>
      </div>
      <div className="varga-study-grid">
        {items.map((item) => (
          <button
            type="button"
            className={`varga-study-card${activeCode === item.code ? " active" : ""}`}
            disabled={!item.available}
            key={item.code}
            onClick={() => onSelect(item.code)}
          >
            <div className="varga-study-card-head">
              <div>
                <strong>{item.code}</strong>
                {vargaPriorityLabels[item.code] ? <em>{vargaPriorityLabels[item.code]}</em> : null}
              </div>
              <span>{vargaPurposeLabels[item.code] ?? item.name}</span>
            </div>
            <div className="varga-study-preview">
              {item.available ? (
                chartStyle === "south" ? (
                  <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact />
                ) : (
                  <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact />
                )
              ) : (
                <em>{unavailableVargaLabel(item.code)}</em>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function EssentialChartPairBoard({
  chart,
  activeCode,
  chartStyle,
  chartReference,
  onSelect,
  onOpenAtlas,
}: {
  chart: BirthChart | null;
  activeCode: string;
  chartStyle: "north" | "south";
  chartReference: ChartReference;
  onSelect: (code: string) => void;
  onOpenAtlas: () => void;
}) {
  const items = primaryVargaTabCodes.map((code) => {
    if (code === "D1") return { code, title: "D1 Раши", hint: "основа карты", available: Boolean(chart), varga: null };
    const varga = chart?.vargas?.[code] ?? null;
    return {
      code,
      title: `${code} ${vargaPurposeLabels[code] ?? varga?.name ?? "варга"}`,
      hint: priorityVargaContexts[code]?.detail ?? "ключевая D-карта",
      available: Boolean(varga),
      varga,
    };
  });

  return (
    <div className="essential-chart-board" aria-label="Главные рабочие D-карты">
      <div className="essential-chart-head">
        <div>
          <strong>Главные D-карты</strong>
          <span>D1, D9, D10 и ключевые дополнительные слои</span>
        </div>
        <button type="button" onClick={onOpenAtlas}>
          Открыть атлас D1-D60
        </button>
      </div>
      <div className="essential-chart-pair">
        {items.map((item) => (
          <button
            type="button"
            className={`essential-chart-card${["D1", "D9", "D10"].includes(item.code) ? " primary" : ""}${activeCode === item.code ? " active" : ""}`}
            disabled={!item.available}
            key={item.code}
            onClick={() => onSelect(item.code)}
          >
            <div className="essential-chart-title">
              <strong>{item.title}</strong>
              <span>{item.hint}</span>
            </div>
            <div className="essential-chart-preview">
              {item.available ? (
                chartStyle === "south" ? (
                  <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact />
                ) : (
                  <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact />
                )
              ) : (
                <em>{unavailableVargaLabel(item.code)}</em>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function PrimaryVargaTabs({
  chart,
  activeCode,
  activeGroupKey,
  workspaceTab,
  onSelect,
  onFocusGroupSelect,
  onWorkspaceTabChange,
  onCoverageSelect,
}: {
  chart: BirthChart | null;
  activeCode: string;
  activeGroupKey: string;
  workspaceTab: ChartWorkspaceTab;
  onSelect: (code: string) => void;
  onFocusGroupSelect: (groupKey: string, code: string) => void;
  onWorkspaceTabChange: (tab: ChartWorkspaceTab) => void;
  onCoverageSelect: () => void;
}) {
  const coverage = vargaCoverage(chart);
  const focusGroups = vargaFocusGroups.filter((group) => ["core", "marriage", "career", "parents", "sadhana", "karma"].includes(group.key));
  const allItems = vargaSnapshotCodes.map((code) => ({
    code,
    available: code === "D1" ? Boolean(chart) : Boolean(chart?.vargas?.[code]),
    label: `${code} · ${priorityVargaContexts[code]?.scope ?? vargaPurposeLabels[code] ?? "Варга"}`,
  }));
  const activeAvailable = activeCode === "D1" ? Boolean(chart) : Boolean(chart?.vargas?.[activeCode]);
  const activeStatus = !chart
    ? "ожидает расчёт"
    : activeAvailable
      ? "рассчитана"
      : unavailableVargaLabel(activeCode);
  const activeContext = priorityVargaContexts[activeCode] ?? { scope: vargaPurposeLabels[activeCode] ?? "Варга", detail: "дополнительный слой чтения" };
  const activeFocusGroup = focusGroups.find((group) => group.key === activeGroupKey) ?? focusGroups.find((group) => group.codes.includes(activeCode)) ?? focusGroups[0];

  return (
    <div className="primary-varga-tabs" aria-label="Быстрый выбор главных D-карт">
      <label className="primary-varga-picker">
        <span>Все D-карты</span>
        <select value={activeCode} onChange={(event) => onSelect(event.target.value)} disabled={!chart}>
          {allItems.map((item) => (
            <option value={item.code} disabled={!item.available} key={item.code}>
              {item.label}{item.available ? "" : ` (${unavailableVargaLabel(item.code)})`}
            </option>
          ))}
        </select>
      </label>
      <button
        type="button"
        className="primary-varga-coverage"
        onClick={onCoverageSelect}
        aria-label="Открыть атлас всех D-карт"
      >
        <span>{coverage.ready.length}/{coverage.total}</span>
        <strong>{coverage.pendingJaimini.length ? "Jaimini ждёт сверки" : "D-карты"}</strong>
      </button>
      <div className={`primary-varga-status${activeAvailable ? " ready" : ""}`}>
        <span>{activeCode}</span>
        <strong>{activeStatus}</strong>
      </div>
      <div className="primary-varga-purpose">
        <strong>{activeContext.scope}</strong>
        <span>{activeContext.detail}</span>
      </div>
      <div className="primary-focus-tabs" aria-label="Рабочий ракурс чтения карты">
        {focusGroups.map((group) => {
          const selectedCode = availableCodeForVargaGroup(chart, group);
          return (
            <button
              type="button"
              className={activeFocusGroup.key === group.key ? "active" : ""}
              disabled={!selectedCode}
              key={group.key}
              onClick={() => {
                if (!selectedCode) return;
                onFocusGroupSelect(group.key, selectedCode);
              }}
            >
              <strong>{group.label}</strong>
              <span>{group.hint}</span>
            </button>
          );
        })}
      </div>
      <div className="primary-focus-summary">
        <strong>{activeFocusGroup.title}</strong>
        <span>{activeFocusGroup.description}</span>
        <em>{activeFocusGroup.codes.join(" · ")}</em>
      </div>
      <div className="primary-workspace-shortcuts" aria-label="Быстрый переход по рабочим блокам карты">
        {chartWorkspaceTabs.map((tab) => (
          <button
            type="button"
            className={workspaceTab === tab.key ? "active" : ""}
            key={tab.key}
            onClick={() => onWorkspaceTabChange(tab.key)}
          >
            <strong>{tab.label}</strong>
            <span>{tab.hint}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function VargaCoverageSummary({
  chart,
  open,
  onOpenChange,
  onOpenAtlas,
  detailsRef,
}: {
  chart: BirthChart | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onOpenAtlas: () => void;
  detailsRef?: RefObject<HTMLDetailsElement | null>;
}) {
  const coverage = vargaCoverage(chart);
  const readyText = coverage.ready.length ? coverage.ready.slice(0, 8).join(", ") : "после расчёта";
  const pendingText = coverage.pendingJaimini.length
    ? coverage.pendingJaimini.join(", ")
    : coverage.missing.length
      ? coverage.missing.slice(0, 5).join(", ")
      : "нет";
  const items = [
    {
      label: "Готово",
      value: `${coverage.ready.length}/${coverage.total}`,
      detail: readyText,
    },
    {
      label: "Ключевые",
      value: "D1 D9 D10",
      detail: "основа, дхарма, карьера",
    },
    {
      label: "Семья/род",
      value: "D7 D12",
      detail: "дети, родители, наследие",
    },
    {
      label: coverage.pendingJaimini.length ? "Ждёт сверки" : "Ожидает",
      value: pendingText,
      detail: coverage.pendingJaimini.length ? "Джаимини и редкие варги" : "нет полной сетки",
    },
  ];

  return (
    <details
      className="varga-coverage-summary"
      ref={detailsRef}
      open={open}
      onToggle={(event) => onOpenChange(event.currentTarget.open)}
      aria-label="Покрытие D-карт"
    >
      <summary className="varga-coverage-summary-head">
        <strong>Покрытие варг</strong>
        <span>{coverage.ready.length}/{coverage.total} готово · D1-D60</span>
      </summary>
      <div className="varga-coverage-summary-grid">
        {items.map((item) => (
          <div key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.detail}</small>
          </div>
        ))}
      </div>
      <button type="button" className="varga-coverage-atlas-button" onClick={onOpenAtlas}>Атлас D1-D60</button>
    </details>
  );
}

function JaiminiPendingStrip({ onOpenAtlas }: { onOpenAtlas: () => void }) {
  const items = jaiminiVargaCodes.map((code) => ({
    code,
    scope: priorityVargaContexts[code]?.scope ?? vargaPurposeLabels[code] ?? "Jaimini",
    detail: priorityVargaContexts[code]?.detail ?? "ждёт сверки правила",
  }));

  return (
    <details className="jaimini-pending-strip" aria-label="D-карты Джаимини ждут сверки">
      <summary>
        <strong>Джаимини ждёт сверки</strong>
        <span>D5, D6, D8 и D11 не выдаются как расчёт, пока правило не подтверждено.</span>
      </summary>
      <div className="jaimini-pending-list">
        {items.map((item) => (
          <button type="button" disabled key={item.code} title={item.detail}>
            <strong>{item.code}</strong>
            <span>{item.scope}</span>
          </button>
        ))}
      </div>
      <button type="button" onClick={onOpenAtlas}>Открыть атлас</button>
    </details>
  );
}

function PriorityVargaRibbon({
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
  const items = practitionerVargaCodes.map((code) => {
    if (code === "D1") return { code, name: "Rashi", available: Boolean(chart), varga: null };
    const varga = chart?.vargas?.[code];
    return { code, name: varga?.name ?? "Varga", available: Boolean(varga), varga: varga ?? null };
  });
  const coverage = vargaCoverage(chart);
  const activeContext = priorityVargaContexts[activeCode] ?? { scope: "Варга", detail: "дополнительная карта" };

  return (
    <div className="priority-varga-ribbon" aria-label="Главные D-карты">
      <div className="priority-varga-ribbon-head">
        <div>
          <strong>D-карты</strong>
          <span>Быстрый набор астролога: D1, D9, D10 и ключевые варги</span>
        </div>
        <div className="varga-coverage-pill">
          <span>{coverage.ready.length}/{coverage.total}</span>
          <strong>{activeCode} · {activeContext.scope}</strong>
          <small>
            {coverage.pendingJaimini.length
              ? `Jaimini ждёт сверки: ${coverage.pendingJaimini.join(", ")}`
              : coverage.missing.length
                ? `полный атлас: ${coverage.ready.length}/${coverage.total}`
                : "все основные варги рассчитаны"}
          </small>
        </div>
      </div>
      <div className="priority-varga-ribbon-grid">
        {items.map((item) => (
          <button
            type="button"
            className={`priority-varga-card${activeCode === item.code ? " active" : ""}`}
            disabled={!item.available}
            key={item.code}
            onClick={() => onSelect(item.code)}
          >
            <div className="priority-varga-title">
              <div>
                <strong>{item.code}</strong>
                <em>{priorityVargaContexts[item.code].scope}</em>
              </div>
              <span>{vargaPurposeLabels[item.code] ?? item.name}</span>
              <small>{priorityVargaContexts[item.code].detail}</small>
            </div>
            <div className="priority-varga-preview">
              {item.available ? (
                chartStyle === "south" ? (
                  <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact />
                ) : (
                  <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact />
                )
              ) : (
                <em>{unavailableVargaLabel(item.code)}</em>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function VargaReadingStrip({
  chart,
  activeCode,
  onSelect,
}: {
  chart: BirthChart | null;
  activeCode: string;
  onSelect: (code: string) => void;
}) {
  const context = priorityVargaContexts[activeCode] ?? { scope: "Варга", detail: "дополнительный слой чтения" };
  const relatedGroup = vargaFocusGroups.find((group) => group.codes.includes(activeCode)) ?? vargaFocusGroups[0];
  const relatedCodes = relatedGroup.codes.filter((code) => code !== activeCode).slice(0, 5);
  const available = (code: string) => code === "D1" ? Boolean(chart) : Boolean(chart?.vargas?.[code]);

  return (
    <div className="varga-reading-strip" aria-label="Контекст чтения выбранной D-карты">
      <div>
        <span><GlossaryTerm termKey="varga">{activeCode}</GlossaryTerm> · {context.scope}</span>
        <strong>{vargaPurposeLabels[activeCode] ?? "Дробная карта"}</strong>
        <small>{context.detail}</small>
      </div>
      <div className="varga-reading-links">
        <span>читать вместе</span>
        {relatedCodes.map((code) => (
          <button type="button" disabled={!available(code)} onClick={() => onSelect(code)} key={code}>
            {code}
          </button>
        ))}
      </div>
    </div>
  );
}

function VargaCompareStrip({
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
  const codes = Array.from(new Set(["D1", "D9", activeCode])).filter((code) => code === "D1" || Boolean(chart?.vargas?.[code]));
  if (!chart || codes.length < 2) return null;

  return (
    <div className="varga-compare-strip" aria-label="Быстрое сравнение D1, D9 и активной варги">
      <div className="varga-compare-head">
        <strong>Сравнить</strong>
        <span>D1 / D9 / активная</span>
      </div>
      <div className="varga-compare-list">
        {codes.map((code) => {
          const varga = code === "D1" ? null : chart.vargas?.[code] ?? null;
          const context = priorityVargaContexts[code] ?? { scope: "Варга", detail: "дробная карта" };
          return (
            <button
              type="button"
              className={`varga-compare-card${activeCode === code ? " active" : ""}`}
              onClick={() => onSelect(code)}
              key={code}
            >
              <div>
                <strong>{code}</strong>
                <span>{context.scope}</span>
              </div>
              <div className="varga-compare-preview">
                {chartStyle === "south" ? (
                  <SouthIndianChartGrid chart={chart} varga={varga} chartReference={chartReference} compact />
                ) : (
                  <NorthIndianChartSvg chart={chart} varga={varga} chartReference={chartReference} compact />
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

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
  const [atlasFilter, setAtlasFilter] = useState<"all" | "ready" | "pending" | "jaimini">("all");
  const items = vargaSnapshotCodes.map((code) => {
    if (code === "D1") {
      return { code, name: "Раши", available: Boolean(chart), varga: null, status: chart ? "рассчитана" : "нет расчёта", previewStatus: "после расчёта" };
    }
    const varga = chart?.vargas?.[code];
    const available = Boolean(varga);
    return {
      code,
      name: varga?.name ?? "Варга",
      available,
      varga: varga ?? null,
      status: available ? "рассчитана" : unavailableVargaLabel(code),
      previewStatus: jaiminiVargaCodeSet.has(code) ? "после сверки" : "после расчёта",
    };
  });
  const coverage = vargaCoverage(chart);
  const missingText = coverage.missing.length ? coverage.missing.slice(0, 6).join(", ") : "нет";
  const jaiminiText = coverage.pendingJaimini.length ? coverage.pendingJaimini.join(", ") : "нет";
  const filteredItems = items.filter((item) => {
    if (atlasFilter === "ready") return item.available;
    if (atlasFilter === "pending") return !item.available && !jaiminiVargaCodeSet.has(item.code);
    if (atlasFilter === "jaimini") return jaiminiVargaCodeSet.has(item.code);
    return true;
  });
  const atlasFilters = [
    { key: "all", label: "Все", count: items.length },
    { key: "ready", label: "Готовые", count: coverage.ready.length },
    { key: "pending", label: "Ожидают", count: coverage.missing.length - coverage.pendingJaimini.length },
    { key: "jaimini", label: "Джаимини", count: coverage.pendingJaimini.length },
  ] as const;

  return (
    <div className="varga-atlas-board" aria-label="Атлас D-карт">
      <div className="varga-atlas-head">
        <div>
          <strong>Атлас D-карт</strong>
          <span>20 слоёв одним взглядом</span>
        </div>
        <div className="varga-atlas-status" aria-label="Покрытие атласа D-карт">
          <span><b>{coverage.ready.length}/{coverage.total}</b> рассчитано</span>
          <span><b>{missingText}</b> ожидает</span>
          <span><b>{jaiminiText}</b> Джаимини</span>
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
            <strong>В этом фильтре пока нет D-карт</strong>
            <span>Откройте все карты или запустите расчёт, чтобы появились готовые варги.</span>
            <button type="button" onClick={() => setAtlasFilter("all")}>Показать все</button>
          </div>
        )}
      </div>
      <VargaSummaryTable chart={chart} activeCode={activeCode} onSelect={onSelect} />
    </div>
  );
}

function VargaSummaryTable({
  chart,
  activeCode,
  onSelect,
}: {
  chart: BirthChart | null;
  activeCode: string;
  onSelect: (code: string) => void;
}) {
  const rows = vargaSnapshotCodes.map((code) => {
    const placements = code === "D1"
      ? [
          ...(chart?.ascendant ? [{ body: "Lagna", rashi: chart.ascendant.rashi }] : []),
          ...(chart?.grahas ?? []).map((graha) => ({ body: graha.body, rashi: graha.rashi })),
        ]
      : chart?.vargas?.[code]?.placements ?? [];
    const findRashi = (body: string) => placements.find((placement) => canonicalBody(placement.body) === canonicalBody(body))?.rashi ?? "";
    const available = code === "D1" ? Boolean(chart) : Boolean(chart?.vargas?.[code]);
    return {
      code,
      available,
      purpose: vargaPurposeLabels[code] ?? "Варга",
      lagna: findRashi("Lagna"),
      moon: findRashi("Chandra"),
      sun: findRashi("Surya"),
    };
  });

  return (
    <div className="varga-summary-table" aria-label="Сводная таблица Shodashvarga">
      <div className="varga-summary-head">
        <strong>Shodashvarga таблица</strong>
        <span>Lagna, Chandra и Surya по D-картам</span>
      </div>
      <div className="varga-summary-row table-head">
        <span>D</span>
        <span>Сфера</span>
        <span>Lagna</span>
        <span>Chandra</span>
        <span>Surya</span>
      </div>
      {rows.map((row) => (
        <button
          type="button"
          className={`varga-summary-row${activeCode === row.code ? " active" : ""}${row.available ? " ready" : ""}`}
          disabled={!row.available}
          key={row.code}
          onClick={() => onSelect(row.code)}
        >
          <strong>{row.code}</strong>
          <span>{row.purpose}</span>
          <span>{row.lagna || "-"}</span>
          <span>{row.moon || "-"}</span>
          <span>{row.sun || "-"}</span>
        </button>
      ))}
    </div>
  );
}

function BirthCompactStrip({
  birthDate,
  birthTime,
  placeName,
  selectedPlace,
  chart,
  collapsed,
  onToggle,
}: {
  birthDate: string;
  birthTime: string;
  placeName: string;
  selectedPlace: PlaceCandidate | null;
  chart: BirthChart | null;
  collapsed: boolean;
  onToggle: () => void;
}) {
  const placeLabel = selectedPlace?.label ?? chart?.place.label ?? chart?.place.name ?? placeName;
  const utcLabel = chart?.birth.utc_offset ?? selectedPlace?.timezone ?? "timezone";

  return (
    <div className="birth-compact-strip">
      <div>
        <span>Карта рождения</span>
        <strong>
          {birthDate} · {birthTime} · {placeLabel}
        </strong>
      </div>
      <div>
        <span>UTC / TZ</span>
        <strong>{utcLabel}</strong>
      </div>
      <button type="button" className="secondary-button" onClick={onToggle}>
        {collapsed ? "Изменить данные" : "Свернуть"}
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

function supportsHoverTooltips() {
  return typeof window !== "undefined" && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
}

function GlossaryTerm({ termKey, children }: { termKey: GlossaryKey; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [pinned, setPinned] = useState(false);
  const wrapRef = useRef<HTMLSpanElement | null>(null);
  const popoverId = useId();
  const item = jyotishGlossary[termKey];

  useEffect(() => {
    if (!open) return;

    function handlePointerDown(event: PointerEvent) {
      if (wrapRef.current?.contains(event.target as Node)) return;
      setOpen(false);
      setPinned(false);
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
        setPinned(false);
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  return (
    <span
      className="glossary-wrap"
      data-open={open ? "true" : "false"}
      ref={wrapRef}
      onPointerEnter={() => {
        if (supportsHoverTooltips() && !pinned) setOpen(true);
      }}
      onPointerLeave={() => {
        if (supportsHoverTooltips() && !pinned) setOpen(false);
      }}
    >
      <button
        type="button"
        className="glossary-trigger"
        aria-controls={popoverId}
        aria-expanded={open}
        title={item.text}
        onFocus={() => {
          if (!pinned) setOpen(true);
        }}
        onClick={(event) => {
          event.stopPropagation();
          const nextOpen = !open || !pinned;
          setPinned(nextOpen);
          setOpen(nextOpen);
        }}
      >
        {children}
      </button>
      <span className="glossary-popover" id={popoverId} role="note">
          <span className="glossary-popover-head">
            <strong>{item.label}</strong>
            <button
              type="button"
              className="glossary-close"
              aria-label="Закрыть объяснение"
              onClick={(event) => {
                event.stopPropagation();
                setOpen(false);
                setPinned(false);
              }}
            >
              ×
            </button>
          </span>
          <span>{item.text}</span>
          <button
            type="button"
            className="help-ai-action"
            onClick={(event) => {
              event.stopPropagation();
              requestAiExplanation({ title: item.label, text: item.text });
              setOpen(false);
              setPinned(false);
            }}
          >
            Спросить AI
          </button>
      </span>
    </span>
  );
}

function CalculationValueHelp({
  title,
  text,
  children,
}: {
  title: string;
  text: string;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [pinned, setPinned] = useState(false);
  const wrapRef = useRef<HTMLSpanElement | null>(null);
  const popoverId = useId();

  useEffect(() => {
    if (!open) return;

    function handlePointerDown(event: PointerEvent) {
      if (wrapRef.current?.contains(event.target as Node)) return;
      setOpen(false);
      setPinned(false);
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key !== "Escape") return;
      setOpen(false);
      setPinned(false);
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  return (
    <span
      className="glossary-wrap calculation-value-help"
      data-open={open ? "true" : "false"}
      ref={wrapRef}
      onPointerEnter={() => {
        if (supportsHoverTooltips() && !pinned) setOpen(true);
      }}
      onPointerLeave={() => {
        if (supportsHoverTooltips() && !pinned) setOpen(false);
      }}
    >
      <button
        type="button"
        className="glossary-trigger"
        aria-controls={popoverId}
        aria-expanded={open}
        title={text}
        onFocus={() => {
          if (!pinned) setOpen(true);
        }}
        onClick={(event) => {
          event.stopPropagation();
          const nextOpen = !open || !pinned;
          setPinned(nextOpen);
          setOpen(nextOpen);
        }}
      >
        {children}
      </button>
      <span className="glossary-popover" id={popoverId} role="note">
        <span className="glossary-popover-head">
          <strong>{title}</strong>
          <button
            type="button"
            className="glossary-close"
            aria-label="Закрыть объяснение"
            onClick={(event) => {
              event.stopPropagation();
              setOpen(false);
              setPinned(false);
            }}
          >
            ×
          </button>
        </span>
        <span>{text}</span>
        <button
          type="button"
          className="help-ai-action"
          onClick={(event) => {
            event.stopPropagation();
            requestAiExplanation({ title, text });
            setOpen(false);
            setPinned(false);
          }}
        >
          Спросить AI
        </button>
      </span>
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

function BeginnerLearningPanel() {
  const items: Array<{ key: string; title: ReactNode; text: string }> = [
    {
      key: "self",
      title: <GlossaryTerm termKey="lagna">Лагна</GlossaryTerm>,
      text: "старт карты: тело, характер, общий способ действовать",
    },
    {
      key: "mind",
      title: <GlossaryTerm termKey="chandra_lagna">Луна</GlossaryTerm>,
      text: "ум, реакция, эмоциональный комфорт и даши",
    },
    {
      key: "relationship",
      title: <GlossaryTerm termKey="house_7">7 дом</GlossaryTerm>,
      text: "партнёрство, договорённости и открытое взаимодействие",
    },
    {
      key: "inner",
      title: <GlossaryTerm termKey="house_12">12 дом</GlossaryTerm>,
      text: "сон, расходы, уединение, близость и скрытая сторона связи",
    },
    {
      key: "strength",
      title: <GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm>,
      text: "расчётная сила грахи; полезна как слой проверки, а не приговор",
    },
    {
      key: "navamsa",
      title: <GlossaryTerm termKey="d9">D9</GlossaryTerm>,
      text: "зрелость положения, дхарма, брак и тонкая сила грах",
    },
  ];

  return (
    <div className="beginner-learning-panel" aria-label="Базовый порядок чтения карты">
      <div>
        <strong>Базовый порядок чтения</strong>
        <span>D1 сначала даёт основу, D9 и силы уточняют картину.</span>
      </div>
      <div className="beginner-learning-grid">
        {items.map((item) => (
          <div key={item.key}>
            <strong>{item.title}</strong>
            <span>{item.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function BeginnerGuidedCourse() {
  const steps: Array<{ key: string; title: ReactNode; text: ReactNode; href: string }> = [
    {
      key: "map",
      title: <>1. Найдите <GlossaryTerm termKey="lagna">лагну</GlossaryTerm></>,
      text: <>Это старт карты: тело, характер и базовый способ действовать.</>,
      href: "#varga-charts",
    },
    {
      key: "houses",
      title: <>2. Откройте <GlossaryTerm termKey="house">дома</GlossaryTerm></>,
      text: <>Номера 1-12 под картой объясняют сферы жизни простым языком.</>,
      href: "#varga-charts",
    },
    {
      key: "moon",
      title: <>3. Смотрите <GlossaryTerm termKey="chandra_lagna">Луну</GlossaryTerm></>,
      text: <>Луна показывает ум, реакцию, комфорт и основу даш.</>,
      href: "#varga-charts",
    },
    {
      key: "table",
      title: <>4. Проверьте <GlossaryTerm termKey="calculation_table">таблицу</GlossaryTerm></>,
      text: <>Там видны градусы, раши, дома, накшатры, D9, сожжение и шадбала.</>,
      href: "/?analysis=calculations#reports",
    },
    {
      key: "ai",
      title: <>5. Спросите <GlossaryTerm termKey="ai_context">AI</GlossaryTerm></>,
      text: <>После расчёта можно задавать вопросы по карте и связанным людям.</>,
      href: "/?analysis=guidance#reports",
    },
  ];

  return (
    <section className="beginner-guided-course" aria-label="Обучение основам карты">
      <div className="beginner-guided-head">
        <strong>Режим новичка</strong>
        <span>Пять шагов, чтобы человек без подготовки не потерялся в карте.</span>
      </div>
      <div className="beginner-guided-steps">
        {steps.map((step) => (
          <a href={step.href} key={step.key}>
            <strong>{step.title}</strong>
            <span>{step.text}</span>
          </a>
        ))}
      </div>
    </section>
  );
}

function BeginnerAskAiPanel() {
  const questions = [
    {
      key: "rashi",
      title: "Что такое раши?",
      text: "Объясни простыми словами, что такое знак/раши в этой карте и почему он важен.",
    },
    {
      key: "house12",
      title: "Что значит 12 дом?",
      text: "Объясни 12 дом в этой карте: расходы, сон, уединение, близость, скрытые темы и мокша.",
    },
    {
      key: "combustion",
      title: "Что такое сожжение?",
      text: "Объясни, как сожжение планеты рядом с Солнцем влияет на проявление грахи в этой карте.",
    },
    {
      key: "shadbala",
      title: "Как читать шадбалу?",
      text: "Объясни шадбалу простыми словами и покажи, как не делать вывод только по одному числу.",
    },
  ];

  return (
    <section className="beginner-ask-ai-panel" aria-label="Вопросы AI по базовым понятиям">
      <div>
        <strong><GlossaryTerm termKey="ai_context">Спросить AI по карте</GlossaryTerm></strong>
        <span>Эти вопросы открывают разбор и передают формулировку как контекст.</span>
      </div>
      <div>
        {questions.map((question) => (
          <button type="button" key={question.key} onClick={() => requestAiExplanation(question)}>
            {question.title}
          </button>
        ))}
      </div>
    </section>
  );
}

function BeginnerCalculationGuide() {
  const items: Array<{ key: string; title: ReactNode; text: string }> = [
    {
      key: "graha",
      title: <GlossaryTerm termKey="graha">Граха</GlossaryTerm>,
      text: "какая планета или лагна сейчас читается в строке",
    },
    {
      key: "rashi",
      title: <GlossaryTerm termKey="rashi">Раши</GlossaryTerm>,
      text: "в каком знаке стоит граха; это показывает стиль проявления",
    },
    {
      key: "house",
      title: <GlossaryTerm termKey="house">Дом</GlossaryTerm>,
      text: "в какой сфере жизни проявится положение грахи",
    },
    {
      key: "ruled",
      title: <GlossaryTerm termKey="ruled_houses">Упр.</GlossaryTerm>,
      text: "какие дома граха приносит с собой как хозяин знаков",
    },
    {
      key: "nakshatra",
      title: <GlossaryTerm termKey="nakshatra">Накшатра</GlossaryTerm>,
      text: "тонкая лунная стоянка; уточняет мотивацию и оттенок положения",
    },
    {
      key: "d9",
      title: <GlossaryTerm termKey="navamsa">D9</GlossaryTerm>,
      text: "навамша показывает зрелость и внутреннюю силу положения",
    },
  ];

  return (
    <div className="beginner-calculation-guide" aria-label="Как читать таблицу расчётов">
      <div>
        <strong>Как читать таблицу расчётов</strong>
        <span>Читайте строку слева направо: кто действует, где стоит, каким домом управляет и как это уточняется.</span>
      </div>
      <div>
        {items.map((item) => (
          <section key={item.key}>
            <strong>{item.title}</strong>
            <span>{item.text}</span>
          </section>
        ))}
      </div>
    </div>
  );
}

function BeginnerNextSteps() {
  return (
    <div className="beginner-next-steps" aria-label="Что делать новичку">
      <div>
        <strong>Что делать дальше</strong>
        <span>Для первого знакомства достаточно трёх действий: рассчитать карту, открыть объяснения и задать вопрос.</span>
      </div>
      <div>
        <a href="#birth-form">1. Данные рождения</a>
        <a href="#varga-charts">2. Карта и дома</a>
        <a href="#reports">3. AI-разбор</a>
        <a href="/interactions">4. Люди рядом</a>
      </div>
    </div>
  );
}

function AiAccessPolicyPanel() {
  return (
    <section className="ai-access-policy-panel" aria-label="Правила AI-разбора">
      <div>
        <strong><GlossaryTerm termKey="free_personal_ai">AI-разбор карты</GlossaryTerm></strong>
        <span>Правило MVP: первый бесплатный разбор относится к вашей собственной карте.</span>
      </div>
      <div className="ai-access-policy-grid">
        <section>
          <strong><GlossaryTerm termKey="self_profile">Моя карта</GlossaryTerm></strong>
          <span>можно сохранить как основную и открыть бесплатный личный AI-разбор</span>
        </section>
        <section>
          <strong><GlossaryTerm termKey="saved_other_chart">Карта другого</GlossaryTerm></strong>
          <span>можно сохранить, смотреть расчёты и использовать в совместимости/взаимодействиях</span>
        </section>
        <section>
          <strong><GlossaryTerm termKey="paid_other_ai">AI по чужой карте</GlossaryTerm></strong>
          <span>будет платным сценарием; без согласия это остаётся личной заметкой владельца аккаунта</span>
        </section>
      </div>
    </section>
  );
}

function AiRelatedContextPanel({ relationships }: { relationships: ChartProfileRelationship[] }) {
  const visible = relationships.filter((relationship) => !["declined", "blocked"].includes(relationship.link_status)).slice(0, 4);
  return (
    <section className="ai-related-context-panel" aria-label="Связанные карты для AI-контекста">
      <div className="ai-related-context-head">
        <div>
          <strong><GlossaryTerm termKey="ai_context">Контекст связанных карт</GlossaryTerm></strong>
          <span>AI может учитывать выбранные карты родителей, партнёра, руководителя или другого человека вместе с ролью и сохранёнными обзорами.</span>
        </div>
        <a href="/interactions">Настроить</a>
      </div>
      {visible.length ? (
        <div className="ai-related-context-list">
          {visible.map((relationship) => {
            const role = relationshipRoleDefinitions.find((item) => item.key === relationship.role);
            return (
              <section key={`ai-context-relationship-${relationship.id}`}>
                <span>{role?.label ?? relationship.role}</span>
                <strong>
                  {relationship.profile?.display_name ?? "Карта A"} → {relationship.related_profile?.display_name ?? "Карта B"}
                </strong>
                <small>
                  <GlossaryTerm termKey="relationship_status">{relationshipStatusLabel(relationship.link_status)}</GlossaryTerm>
                  {" · "}
                  <GlossaryTerm termKey="ai_context">карта + обзоры</GlossaryTerm>
                </small>
              </section>
            );
          })}
        </div>
      ) : (
        <p>
          Связанные карты ещё не выбраны. Добавьте человека в разделе “Взаимодействия”, укажите роль и, если он зарегистрирован, отправьте запрос на подтверждение. В будущем AI будет подтягивать и сохранённые обзоры этих карт.
        </p>
      )}
    </section>
  );
}

function MvpReadinessPanel() {
  const items = [
    { key: "ready-calc", state: "готово", title: "Расчёты и таблицы", text: "D1, первичная таблица астролога, варги, шадбала, аста, накшатры." },
    { key: "ready-help", state: "готово", title: "Объяснения", text: "Дома, раши, термины, шадбала, сожжение и beginner-вопросы к AI." },
    { key: "ready-links", state: "готово", title: "Люди и роли", text: "Личные связи, запрос зарегистрированному пользователю, согласие и статусы." },
    { key: "next-pay", state: "дальше", title: "Оплата", text: "Платный AI-разбор чужих карт оставлен как следующий этап." },
  ];
  return (
    <section className="mvp-readiness-panel" aria-label="Готовность MVP">
      <div className="mvp-readiness-head">
        <strong><GlossaryTerm termKey="mvp_readiness">Что можно проверять сейчас</GlossaryTerm></strong>
        <span>Короткая карта готовности, чтобы не смешивать рабочий MVP и будущую коммерческую логику.</span>
      </div>
      <div className="mvp-readiness-grid">
        {items.map((item) => (
          <section className={item.state === "готово" ? "ready" : "next"} key={item.key}>
            <span>{item.state}</span>
            <strong>{item.title}</strong>
            <small>{item.text}</small>
          </section>
        ))}
      </div>
    </section>
  );
}

function CalculationReadingOrder({ isD1, chartMode }: { isD1: boolean; chartMode: string }) {
  const items: Array<{ key: string; title: ReactNode; text: ReactNode }> = isD1
    ? [
        {
          key: "placement",
          title: <GlossaryTerm termKey="graha">1. Граха</GlossaryTerm>,
          text: (
            <>
              кто действует, в каком <GlossaryTerm termKey="rashi">раши</GlossaryTerm> и <GlossaryTerm termKey="house">доме</GlossaryTerm>
            </>
          ),
        },
        {
          key: "ownership",
          title: <GlossaryTerm termKey="ruled_houses">2. Управление</GlossaryTerm>,
          text: <>какие дома граха приносит в место своего положения</>,
        },
        {
          key: "subtle",
          title: <GlossaryTerm termKey="nakshatra">3. Накшатра</GlossaryTerm>,
          text: (
            <>
              уточнение через <GlossaryTerm termKey="pada">паду</GlossaryTerm> и <GlossaryTerm termKey="navamsa">D9</GlossaryTerm>
            </>
          ),
        },
        {
          key: "condition",
          title: <GlossaryTerm termKey="dignity">4. Состояние</GlossaryTerm>,
          text: (
            <>
              достоинство, <GlossaryTerm termKey="combustion">аста</GlossaryTerm> и <GlossaryTerm termKey="shadbala">шадбала</GlossaryTerm>
            </>
          ),
        },
      ]
    : [
        {
          key: "varga-point",
          title: <GlossaryTerm termKey="varga">1. Варга {chartMode}</GlossaryTerm>,
          text: <>сначала проверяется, в какой знак попала каждая точка</>,
        },
        {
          key: "d1-anchor",
          title: <GlossaryTerm termKey="d1">2. Сравнение с D1</GlossaryTerm>,
          text: <>дробная карта читается вместе с основной картой, а не отдельно</>,
        },
        {
          key: "condition",
          title: <GlossaryTerm termKey="dignity">3. Состояние</GlossaryTerm>,
          text: <>сила положения уточняется через достоинство и поддержку D1</>,
        },
      ];

  return (
    <div className="calculation-reading-order" aria-label="Порядок чтения таблицы расчётов">
      <strong>Что смотреть первым</strong>
      <div>
        {items.map((item) => (
          <section key={item.key}>
            <span>{item.title}</span>
            <small>{item.text}</small>
          </section>
        ))}
      </div>
    </div>
  );
}

function CalculationTableHelp({ isD1 }: { isD1: boolean }) {
  if (!isD1) {
    return (
      <div className="calculation-table-help" aria-label="Подсказка к таблице варги">
        <section>
          <strong><GlossaryTerm termKey="varga">Варга</GlossaryTerm></strong>
          <span>Сначала сравните знак точки в этой варге с её положением в D1.</span>
        </section>
        <section>
          <strong><GlossaryTerm termKey="dignity">Статус</GlossaryTerm></strong>
          <span>Достоинство в варге уточняет качество проявления темы, но не заменяет D1.</span>
        </section>
      </div>
    );
  }

  const items: Array<{ key: string; title: ReactNode; text: ReactNode }> = [
    {
      key: "where",
      title: <GlossaryTerm termKey="house">Дом</GlossaryTerm>,
      text: <>сфера жизни, где граха проявляет себя</>,
    },
    {
      key: "owner",
      title: <GlossaryTerm termKey="ruled_houses">Упр.</GlossaryTerm>,
      text: <>какие темы граха приносит в этот дом</>,
    },
    {
      key: "condition",
      title: <GlossaryTerm termKey="graha_condition">Статус</GlossaryTerm>,
      text: <>ретроградность, достоинство, аста и сила</>,
    },
    {
      key: "strength",
      title: <GlossaryTerm termKey="shadbala_score">Шадбала</GlossaryTerm>,
      text: <>вирупы: сравнивайте относительно других грах</>,
    },
  ];

  return (
    <div className="calculation-table-help" aria-label="Подсказка к таблице D1">
      <strong><GlossaryTerm termKey="calculation_table">Ключ к таблице</GlossaryTerm></strong>
      {items.map((item) => (
        <section key={item.key}>
          <strong>{item.title}</strong>
          <span>{item.text}</span>
        </section>
      ))}
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

function GrahaStatusValue({ graha }: { graha: GrahaPosition }) {
  const dignity = grahaDignity(graha);
  const retrograde = isRetrogradeGraha(graha);
  if (!retrograde && !dignity) return <>-</>;
  return (
    <>
      {retrograde ? <GlossaryTerm termKey="retrograde">ретроградная</GlossaryTerm> : null}
      {retrograde && dignity ? ", " : null}
      {dignity ? <GlossaryTerm termKey={dignity}>{dignityText(dignity)}</GlossaryTerm> : null}
    </>
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
  return (
    <CalculationValueHelp
      title={`Долгота: ${label}`}
      text={`${label}: ${formatDegrees(longitude)} абсолютной сидерической долготы. По этому числу считаются знак, накшатра, пада, D9 и остальные варги.`}
    >
      {formatDegrees(longitude)}
    </CalculationValueHelp>
  );
}

function ShadbalaValue({ chart, body, label }: { chart: BirthChart; body: string; label: string }) {
  const row = shadbalaRowForGraha(chart, body);
  const value = row ? `${row.known_total.toFixed(1)}` : "-";
  const detail = row
    ? `Шадбала ${label}: ${value} вируп. Компоненты: Sthana ${row.components.sthana ?? 0}, Dig ${row.components.dig}, Kala ${row.components.kala ?? 0}, Chesta ${row.components.chesta ?? 0}, Naisargika ${row.components.naisargika}, Drik ${row.components.drik ?? 0}.`
    : `Для ${label} шадбала в текущем расчёте ещё не найдена.`;
  return (
    <CalculationValueHelp title={`Шадбала: ${label}`} text={detail}>
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
        <p>Карта заполнится после ответа бэкенда с эфемеридными позициями.</p>
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
          <span><GlossaryTerm termKey="house_1">1</GlossaryTerm></span>
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
              <RashiValue name={graha.rashi} index={graha.rashi_index} termLanguage={termLanguage} />
            </span>
            <span>{house ? <GlossaryTerm termKey={houseGlossaryKey(house)}>{house}</GlossaryTerm> : "-"}</span>
            <span>{ruledHouses.length ? <HouseGlossaryList houses={ruledHouses} /> : "-"}</span>
            <span>
              <NakshatraValue name={graha.nakshatra} pada={graha.pada} subject={grahaLabel} />
            </span>
            <span>
              <NakshatraLordValue index={graha.nakshatra_index} name={graha.nakshatra} subject={grahaLabel} termLanguage={termLanguage} />
            </span>
            <span className="graha-status-text"><GrahaStatusValue graha={graha} /></span>
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
              <RashiValue name={graha.navamsa} index={graha.navamsa_index} termLanguage={termLanguage} />
            </span>
          </div>
        );
      })}
    </div>
  );
}

function ChartSideCalculationTable({ chart, termLanguage }: { chart: BirthChart | null; termLanguage: TermLanguage }) {
  const grahas = chart?.grahas ?? [];
  const sun = grahas.find((graha) => graha.body === "Surya");
  const lagnaIndex = normalizeRashiIndex(chart?.ascendant?.rashi_index) ?? rashiIndexFromName(chart?.ascendant?.rashi);
  if (!chart || grahas.length === 0) {
    return (
      <section className="chart-side-table empty">
        <div className="chart-side-table-head">
          <strong>Расчёты D1</strong>
          <span>появятся после расчёта карты</span>
        </div>
      </section>
    );
  }

  return (
    <section className="chart-side-table" aria-label="Краткая таблица расчётов рядом с картой">
      <div className="chart-side-table-head">
        <strong>Расчёты D1</strong>
        <span>граха, градус, раши, накшатра, дом, статус</span>
      </div>
      <div className="chart-side-table-grid">
        <div className="chart-side-table-row chart-side-table-header">
          <span>Граха</span>
          <span>Градус</span>
          <span>Раши</span>
          <span>Накшатра</span>
          <span>Дом</span>
          <span>Статус</span>
          <span>D9</span>
        </div>
        {chart.ascendant ? (
          <div className="chart-side-table-row lagna-row">
            <strong><GlossaryTerm termKey="lagna">{grahaTermLabel("Lagna", termLanguage)}</GlossaryTerm></strong>
            <span><LongitudeValue label={grahaTermLabel("Lagna", termLanguage)} longitude={chart.ascendant.longitude} /></span>
            <span><RashiValue name={chart.ascendant.rashi} index={chart.ascendant.rashi_index} termLanguage={termLanguage} compact /></span>
            <span><NakshatraValue name={chart.ascendant.nakshatra} pada={chart.ascendant.pada} subject={grahaTermLabel("Lagna", termLanguage)} /></span>
            <span><GlossaryTerm termKey="house_1">1</GlossaryTerm></span>
            <span>-</span>
            <span><RashiValue name={chart.ascendant.navamsa} termLanguage={termLanguage} compact /></span>
          </div>
        ) : null}
        {grahas.map((graha) => {
          const rashiIndex = normalizeRashiIndex(graha.rashi_index) ?? rashiIndexFromName(graha.rashi);
          const house = houseFromRashiIndex(rashiIndex, lagnaIndex);
          const combustion = combustionStatus(graha, sun);
          const grahaLabel = grahaTermLabel(graha.body, termLanguage);
          return (
            <div className="chart-side-table-row" key={`side-${graha.body}`}>
              <strong><GlossaryTerm termKey="graha">{grahaLabel}</GlossaryTerm></strong>
              <span><LongitudeValue label={grahaLabel} longitude={graha.longitude} /></span>
              <span><RashiValue name={graha.rashi} index={graha.rashi_index} termLanguage={termLanguage} compact /></span>
              <span><NakshatraValue name={graha.nakshatra} pada={graha.pada} subject={grahaLabel} /></span>
              <span>{house ? <GlossaryTerm termKey={houseGlossaryKey(house)}>{house}</GlossaryTerm> : "-"}</span>
              <span className="chart-side-status">
                <GrahaStatusValue graha={graha} />
                {combustion.combust ? (
                  <>
                    {" · "}
                    <CalculationValueHelp
                      title={`Аста: ${grahaLabel}`}
                      text={combustion.distance === null ? `${grahaLabel}: нет данных для проверки сожжения.` : `${grahaLabel}: расстояние от Солнца ${combustion.distance.toFixed(1)}°. Порог: ${combustion.threshold ?? "-"}°.`}
                    >
                      {combustion.label}
                    </CalculationValueHelp>
                  </>
                ) : null}
              </span>
              <span><RashiValue name={graha.navamsa} index={graha.navamsa_index} termLanguage={termLanguage} compact /></span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function FirstReadCalculationPanel({
  chart,
  termLanguage,
  onOpenCalculations,
}: {
  chart: BirthChart | null;
  termLanguage: TermLanguage;
  onOpenCalculations: () => void;
}) {
  const moon = chart?.grahas.find((graha) => graha.body === "Chandra");
  const sun = chart?.grahas.find((graha) => graha.body === "Surya");
  const lagnaIndex = normalizeRashiIndex(chart?.ascendant?.rashi_index) ?? rashiIndexFromName(chart?.ascendant?.rashi);
  const shadbalaRows = [...(chart?.classical?.shadbala?.items ?? [])].sort((left, right) => right.known_total - left.known_total);
  const combust = combustGrahaLabels(chart);
  const keyRows = [
    {
      key: "lagna",
      label: <GlossaryTerm termKey="lagna">Лагна</GlossaryTerm>,
      rashi: chart?.ascendant ? <RashiValue name={chart.ascendant.rashi} index={chart.ascendant.rashi_index} termLanguage={termLanguage} compact /> : "-",
      degree: chart?.ascendant ? formatSignDegrees(chart.ascendant.longitude) : "-",
      nakshatra: chart?.ascendant ? <NakshatraValue name={chart.ascendant.nakshatra} pada={chart.ascendant.pada} subject="Лагна" /> : "-",
      house: <GlossaryTerm termKey="house_1">1</GlossaryTerm>,
      note: "старт чтения",
    },
    {
      key: "moon",
      label: <GlossaryTerm termKey="chandra_lagna">{grahaTermLabel("Chandra", termLanguage)}</GlossaryTerm>,
      rashi: moon ? <RashiValue name={moon.rashi} index={moon.rashi_index} termLanguage={termLanguage} compact /> : "-",
      degree: moon ? formatSignDegrees(moon.longitude) : "-",
      nakshatra: moon ? <NakshatraValue name={moon.nakshatra} pada={moon.pada} subject={grahaTermLabel("Chandra", termLanguage)} /> : "-",
      house: moon ? <GlossaryTerm termKey={houseGlossaryKey(houseFromRashiIndex(normalizeRashiIndex(moon.rashi_index) ?? rashiIndexFromName(moon.rashi), lagnaIndex))}>{houseFromRashiIndex(normalizeRashiIndex(moon.rashi_index) ?? rashiIndexFromName(moon.rashi), lagnaIndex) ?? "-"}</GlossaryTerm> : "-",
      note: "ум и даши",
    },
    {
      key: "sun",
      label: <GlossaryTerm termKey="surya_lagna">{grahaTermLabel("Surya", termLanguage)}</GlossaryTerm>,
      rashi: sun ? <RashiValue name={sun.rashi} index={sun.rashi_index} termLanguage={termLanguage} compact /> : "-",
      degree: sun ? formatSignDegrees(sun.longitude) : "-",
      nakshatra: sun ? <NakshatraValue name={sun.nakshatra} pada={sun.pada} subject={grahaTermLabel("Surya", termLanguage)} /> : "-",
      house: sun ? <GlossaryTerm termKey={houseGlossaryKey(houseFromRashiIndex(normalizeRashiIndex(sun.rashi_index) ?? rashiIndexFromName(sun.rashi), lagnaIndex))}>{houseFromRashiIndex(normalizeRashiIndex(sun.rashi_index) ?? rashiIndexFromName(sun.rashi), lagnaIndex) ?? "-"}</GlossaryTerm> : "-",
      note: "атма и власть",
    },
  ];
  const summaryRows = [
    {
      key: "panchanga",
      label: <GlossaryTerm termKey="panchanga">Панчанга</GlossaryTerm>,
      value: chart?.panchanga.tithi ? `${chart.panchanga.tithi.paksha} ${chart.panchanga.tithi.name}` : "-",
      detail: chart?.panchanga.nakshatra ? `${chart.panchanga.nakshatra.name}${chart.panchanga.nakshatra.pada ? ` ${chart.panchanga.nakshatra.pada}` : ""}` : "накшатра ожидает",
    },
    {
      key: "dasha",
      label: <GlossaryTerm termKey="dasha">Даша сейчас</GlossaryTerm>,
      value: currentDashaLabel(chart),
      detail: "первый слой времени",
    },
    {
      key: "combustion",
      label: <GlossaryTerm termKey="combustion">Сожжение</GlossaryTerm>,
      value: combust.length ? combust.join(", ") : "нет",
      detail: "проверка аста",
    },
    {
      key: "shadbala",
      label: <GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm>,
      value: shadbalaRows[0] ? `${grahaTermLabel(shadbalaRows[0].body, termLanguage, "short")} ${shadbalaRows[0].known_total.toFixed(1)}` : "-",
      detail: shadbalaRows.at(-1)
        ? `min ${grahaTermLabel(shadbalaRows.at(-1)?.body ?? "", termLanguage, "short")} ${shadbalaRows.at(-1)?.known_total.toFixed(1)}`
        : "ожидает силу",
    },
  ];

  return (
    <section className="first-read-calculation-panel" aria-label="Первичная таблица расчётов">
      <div className="first-read-head">
        <div>
          <strong><GlossaryTerm termKey="calculation_table">Первый взгляд астролога</GlossaryTerm></strong>
          <span>Лагна, Луна, Солнце, панчанга, сила и состояния до длинного текста.</span>
        </div>
        <a
          href="/?analysis=calculations#reports"
          onClick={(event) => {
            event.preventDefault();
            window.history.pushState(null, "", "/?analysis=calculations#reports");
            onOpenCalculations();
            document.getElementById("reports")?.scrollIntoView({ block: "start" });
          }}
        >
          вся таблица
        </a>
      </div>
      <div className="first-read-grid">
        <div className="first-read-key-table">
          <div className="first-read-row table-head">
            <span>Точка</span>
            <span><GlossaryTerm termKey="rashi">Раши</GlossaryTerm></span>
            <span><GlossaryTerm termKey="longitude">Градус</GlossaryTerm></span>
            <span><GlossaryTerm termKey="nakshatra">Накшатра</GlossaryTerm></span>
            <span><GlossaryTerm termKey="house">Дом</GlossaryTerm></span>
            <span>Зачем</span>
          </div>
          {keyRows.map((row) => (
            <div className="first-read-row" key={row.key}>
              <strong>{row.label}</strong>
              <span>{row.rashi}</span>
              <span>{row.degree}</span>
              <span>{row.nakshatra}</span>
              <span>{row.house}</span>
              <small>{row.note}</small>
            </div>
          ))}
        </div>
        <div className="first-read-summary">
          {summaryRows.map((row) => (
            <div key={row.key}>
              <span>{row.label}</span>
              <strong>{row.value}</strong>
              <small>{row.detail}</small>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CoreInfoStrip({ chart, termLanguage }: { chart: BirthChart | null; termLanguage: TermLanguage }) {
  const moon = chart?.grahas.find((graha) => graha.body === "Chandra");
  const sun = chart?.grahas.find((graha) => graha.body === "Surya");
  const items = [
    ["Лагна", chart?.ascendant ? `${rashiTermFromName(chart.ascendant.rashi, termLanguage)}, ${chart.ascendant.nakshatra} ${chart.ascendant.pada}` : "ожидает"],
    [grahaTermLabel("Chandra", termLanguage), moon ? `${rashiTermFromName(moon.rashi, termLanguage)}, ${moon.nakshatra} ${moon.pada}` : "ожидает"],
    [grahaTermLabel("Surya", termLanguage), sun ? `${rashiTermFromName(sun.rashi, termLanguage)}, ${formatSignDegrees(sun.longitude)}` : "ожидает"],
    ["Панчанга", chart?.panchanga.tithi?.name ?? chart?.panchanga.nakshatra?.name ?? "ожидает"],
    ["Место", chart?.place.label ?? chart?.place.name ?? "ожидает"],
    ["UTC", chart?.birth.utc_offset ?? chart?.birth.timezone ?? "ожидает"],
  ];

  return (
    <div className="core-info-strip" aria-label="Основная информация карты">
      {items.map(([label, value]) => (
        <div key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  );
}

function PlanetStrengthDigest({ chart }: { chart: BirthChart | null }) {
  const sun = chart?.grahas.find((graha) => graha.body === "Surya");
  const combust = chart?.grahas
    .map((graha) => ({ graha, status: combustionStatus(graha, sun) }))
    .filter((item) => item.status.combust) ?? [];
  const shadbala = [...(chart?.classical?.shadbala?.items ?? [])].sort((left, right) => right.known_total - left.known_total);
  const vimshopaka = [...(chart?.classical?.vimshopaka_bala?.items ?? [])].sort((left, right) => right.score - left.score);
  const sav = chart?.classical?.ashtakavarga?.sarva.total;
  const rows = [
    {
      label: "Сожжение",
      value: combust.length ? combust.map((item) => labelRu(item.graha.body)).join(", ") : "нет",
      detail: combust[0]?.status.label ?? "астангата по дистанции от Солнца",
      warn: combust.length > 0,
    },
    {
      label: "Шадбала max",
      value: shadbala[0] ? `${labelRu(shadbala[0].body)} ${shadbala[0].known_total.toFixed(1)}` : "-",
      detail: shadbala[0] ? "вирупы, полный компонентный слой" : "ожидает расчёт",
    },
    {
      label: "Шадбала min",
      value: shadbala.at(-1) ? `${labelRu(shadbala.at(-1)?.body ?? "")} ${shadbala.at(-1)?.known_total.toFixed(1)}` : "-",
      detail: "быстрая проверка слабого места",
      warn: Boolean(shadbala.at(-1)),
    },
    {
      label: "Вимшопака",
      value: vimshopaka[0] ? `${labelRu(vimshopaka[0].body)} ${vimshopaka[0].score.toFixed(1)}/20` : "-",
      detail: vimshopaka[0]?.primary_scheme ?? "шодаша-варга",
    },
    {
      label: "SAV",
      value: sav ? String(sav) : "-",
      detail: "сарва-аштакаварга",
    },
  ];

  return (
    <div className="planet-strength-digest" aria-label="Сила и состояния планет">
      {rows.map((row, index) => {
        const glossaryKeys: Array<GlossaryKey> = ["combustion", "shadbala", "shadbala", "vimshopaka", "sav"];
        const glossaryKey = glossaryKeys[index];
        return (
          <div className={row.warn ? "warn" : ""} key={row.label}>
            <span>{glossaryKey ? <GlossaryTerm termKey={glossaryKey}>{row.label}</GlossaryTerm> : row.label}</span>
            <strong>{row.value}</strong>
            <small>{row.detail}</small>
          </div>
        );
      })}
    </div>
  );
}

function AstrologerWorkflowPanel({
  chart,
  activeTab,
  onSelect,
}: {
  chart: BirthChart | null;
  activeTab: AnalysisTab;
  onSelect: (tab: AnalysisTab) => void;
}) {
  const items: Array<{
    tab: AnalysisTab;
    label: string;
    value: string;
    hint: string;
    ready: boolean;
  }> = [
    {
      tab: "calculations",
      label: "Планеты",
      value: chart ? `${chart.grahas.length} грах` : "нет карты",
      hint: "градусы, раши, накшатры, D9",
      ready: Boolean(chart),
    },
    {
      tab: "yogas",
      label: "Силы",
      value: chart?.classical?.shadbala?.items?.length ? "шадбала" : "ожидает",
      hint: "шадбала, аштакаварга, йоги",
      ready: Boolean(chart?.classical),
    },
    {
      tab: "timeline",
      label: "Даши",
      value: chart?.dashas?.vimshottari?.mahadashas?.length ? "Vimshottari" : "ожидает",
      hint: "периоды и подпериоды",
      ready: Boolean(chart?.dashas?.vimshottari?.mahadashas?.length),
    },
    {
      tab: "transits",
      label: "Сейчас",
      value: chart ? "гочара" : "нет карты",
      hint: "транзиты текущих дней",
      ready: Boolean(chart),
    },
    {
      tab: "accuracy",
      label: "Точность",
      value: "JHora / PL",
      hint: "сверка расчётов",
      ready: Boolean(chart),
    },
    {
      tab: "guidance",
      label: "AI-разбор",
      value: "Codex CLI",
      hint: "история и вопросы",
      ready: Boolean(chart),
    },
  ];

  return (
    <div className="astrologer-workflow-panel" aria-label="Рабочие разделы астролога">
      <div className="astrologer-workflow-head">
        <strong>Рабочий порядок</strong>
        <span>как в Jyotish-сервисах: карта → силы → периоды → текущие дни → разбор</span>
      </div>
      <div className="astrologer-workflow-grid">
        {items.map((item) => (
          <button
            type="button"
            className={`${activeTab === item.tab ? "active" : ""}${item.ready ? " ready" : ""}`}
            disabled={!item.ready}
            key={item.tab}
            onClick={() => onSelect(item.tab)}
          >
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.hint}</small>
          </button>
        ))}
      </div>
    </div>
  );
}

function ReadingFlowStrip({
  chart,
  chartMode,
  workspaceTab,
  activeAnalysisTab,
  onOpenEssentials,
  onOpenVargas,
  onOpenCalculations,
  onOpenGuidance,
}: {
  chart: BirthChart | null;
  chartMode: string;
  workspaceTab: ChartWorkspaceTab;
  activeAnalysisTab: AnalysisTab;
  onOpenEssentials: () => void;
  onOpenVargas: () => void;
  onOpenCalculations: () => void;
  onOpenGuidance: () => void;
}) {
  const items = [
    {
      label: "Карта",
      value: chart ? `${chartMode} открыт` : "нужен расчёт",
      hint: "основная схема",
      active: workspaceTab === "essentials",
      ready: Boolean(chart),
      action: onOpenEssentials,
    },
    {
      label: "D-карты",
      value: chart ? `${vargaCoverage(chart).ready.length}/${vargaSnapshotCodes.length}` : "после расчёта",
      hint: "D1-D60 и фокусы",
      active: workspaceTab === "vargas",
      ready: Boolean(chart),
      action: onOpenVargas,
    },
    {
      label: "Расчёты",
      value: chart ? "таблицы готовы" : "ожидает",
      hint: "грахи, дома, накшатры",
      active: activeAnalysisTab === "calculations",
      ready: Boolean(chart),
      action: onOpenCalculations,
    },
    {
      label: "AI",
      value: chart ? "разбор и вопросы" : "после карты",
      hint: "Codex CLI",
      active: activeAnalysisTab === "guidance",
      ready: Boolean(chart),
      action: onOpenGuidance,
    },
  ];

  return (
    <div className="reading-flow-strip" aria-label="Порядок работы с картой">
      {items.map((item, index) => (
        <button
          type="button"
          className={`${item.active ? "active" : ""}${item.ready ? " ready" : ""}`}
          disabled={!item.ready && index > 0}
          key={item.label}
          onClick={item.action}
        >
          <span>{index + 1}</span>
          <div>
            <strong>{item.label}</strong>
            <em>{item.value}</em>
            <small>{item.hint}</small>
          </div>
        </button>
      ))}
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

function ActiveCalculationTable({
  chart,
  chartMode,
  selectedVarga,
  selectedVargaPlacements,
  termLanguage,
}: {
  chart: BirthChart | null;
  chartMode: string;
  selectedVarga: ActiveVargaChart | null;
  selectedVargaPlacements: VargaPlacement[];
  termLanguage: TermLanguage;
}) {
  const isD1 = chartMode === "D1";
  const title = isD1 ? "Расчеты D1 Rashi" : `Расчеты ${chartMode} ${selectedVarga?.name ?? ""}`.trim();
  const hint = isD1 ? "Граха, градус, раши, накшатра, статус, сожжение, D9" : "Положение каждой точки в выбранной варге";

  return (
    <div className="active-calculation-table">
      <div className="active-calculation-head">
        <div>
          <strong>{title}</strong>
          <span>{hint}</span>
        </div>
        <div className="active-calculation-tags">
          <GlossaryTerm termKey="shadbala">Shadbala</GlossaryTerm>
          <GlossaryTerm termKey="combustion">Asta</GlossaryTerm>
        </div>
      </div>
      {!isD1 && selectedVarga?.method ? (
        <div className="active-varga-method">
          <strong>
            <GlossaryTerm termKey="varga_method">Метод</GlossaryTerm>
          </strong>
          <span>{selectedVarga.method}</span>
        </div>
      ) : null}
      <CalculationReadingOrder isD1={isD1} chartMode={chartMode} />
      <CalculationTableHelp isD1={isD1} />
      {isD1 ? <AstrologerPrioritySummary chart={chart} termLanguage={termLanguage} /> : null}
      {isD1 ? <PanchangaDigest chart={chart} /> : null}
      {isD1 ? (
        <GrahaTable chart={chart} termLanguage={termLanguage} />
      ) : (
        <VargaTable chart={chart} placements={selectedVargaPlacements} code={chartMode} termLanguage={termLanguage} />
      )}
    </div>
  );
}

function VargaSnapshotGrid({
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
  const items = vargaSnapshotCodes.map((code) => {
    if (code === "D1") return { code, available: Boolean(chart), varga: null };
    const varga = chart?.vargas?.[code];
    return { code, available: Boolean(varga), varga: varga ?? null };
  });

  return (
    <div className="varga-snapshot-grid" aria-label="Сводка варга-карт D1-D60">
      {items.map((item) => (
        <button
          type="button"
          className={`varga-snapshot-card${activeCode === item.code ? " active" : ""}`}
          disabled={!item.available}
          key={item.code}
          onClick={() => onSelect(item.code)}
        >
          <div className="varga-snapshot-head">
            <strong>{item.code}</strong>
            <span>{vargaPurposeLabels[item.code] ?? "Варга"}</span>
          </div>
          <div className="varga-snapshot-body">
            {item.available ? (
              chartStyle === "south" ? (
                <SouthIndianChartGrid chart={chart} varga={item.varga} chartReference={chartReference} compact />
              ) : (
                <NorthIndianChartSvg chart={chart} varga={item.varga} chartReference={chartReference} compact />
              )
            ) : (
              <em>{unavailableVargaLabel(item.code)}</em>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}

function DashaTimeline({ periods }: { periods: DashaPeriod[] }) {
  if (periods.length === 0) {
    return (
      <div className="pending-strip">
        Периоды даш появятся здесь после расчёта долготы Луны и движка Вимшоттари.
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
  if (!summary) {
    return (
      <section className="panel person-summary-panel">
        <div className="panel-heading">
          <h2>Сводка по человеку</h2>
          <span>Ожидает расчёт</span>
        </div>
        <div className="pending-strip">Основные факты рождения появятся после расчёта.</div>
      </section>
    );
  }

  return (
    <section className="panel person-summary-panel">
      <div className="panel-heading">
        <h2>Сводка по человеку</h2>
        <span>Пока только расчётные факты</span>
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
  chartStyle,
  chartReference,
  termLanguage,
  onSelectVarga,
}: {
  summary: PersonSummary | null;
  chart: BirthChart | null;
  activeCode: string;
  chartStyle: "north" | "south";
  chartReference: ChartReference;
  termLanguage: TermLanguage;
  onSelectVarga: (code: string) => void;
}) {
  const detailedPositions = summary?.detailed_positions ?? [];
  const houses = summary?.houses ?? [];
  const isD1 = activeCode === "D1";

  return (
    <section className="panel calculation-detail-panel">
      <div className="panel-heading">
        <h2>Расчёты карты</h2>
        <span>D1, D9, накшатры, дома</span>
      </div>
      <div className="summary-content">
        {!summary ? <div className="pending-strip">Подробные расчёты появятся после построения карты.</div> : null}
        <VargaSnapshotGrid
          chart={chart}
          activeCode={activeCode}
          chartStyle={chartStyle}
          chartReference={chartReference}
          onSelect={onSelectVarga}
        />
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
            <CalculationReadingOrder isD1 chartMode="D1" />
            <CalculationTableHelp isD1 />
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
              {detailedPositions.map((row) => (
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
                    {row.house ? <GlossaryTerm termKey={houseGlossaryKey(row.house)}>{row.house}</GlossaryTerm> : "-"}
                  </span>
                  <span>
                    <HouseGlossaryList houses={row.ruled_houses} />
                  </span>
                  <span>{[row.dignity, row.retrograde ? "ретроградная" : ""].filter(Boolean).join(", ") || "-"}</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
        {houses.length ? (
          <div className="house-overview">
            <div>
              <h3>Обзор домов</h3>
              <span>Цельнознаковые дома</span>
            </div>
            <div className="house-grid">
              {houses.map((house) => (
                <div className="house-card" key={house.house}>
                  <span><GlossaryTerm termKey={houseGlossaryKey(house.house)}>Дом {house.house}</GlossaryTerm></span>
                  <strong>{house.rashi}</strong>
                  <small>{house.grahas.length ? house.grahas.map(labelRu).join(", ") : "Пусто"}</small>
                </div>
              ))}
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
          <p className="workflow-note">
            Ashtottari: {extra.ashtottari?.status ?? "ожидает"}; применимость и стартовое правило требуют JHora/шастра-сверки.
          </p>
        </div>
      ) : null}
    </section>
  );
}

function GeneratedAnalysisDetails({
  analysis,
  assistantLabel,
  chatSlot,
}: {
  analysis: GeneratedDraftAnalysis;
  assistantLabel: string;
  chatSlot?: ReactNode;
}) {
  const traceCount = analysis.sections.reduce((total, section) => total + (section.source_traces?.length ?? 0), 0);
  return (
    <div className="generated-draft">
      <div className="block-heading">
        <h3>{analysis.engine_label ?? generatedTitleRu(analysis.review_status)}</h3>
        <span>
          #{analysis.id} · {assistantLabel} · {generatedStatusRu(analysis.review_status)} · {traceCount} источников
        </span>
      </div>
      {chatSlot}
      {analysis.sections.map((section) => (
        <article className="report-section" key={`${analysis.id}-${section.title}`}>
          <div>
            <strong>{section.title}</strong>
            <em>{generatedStatusRu(analysis.review_status)}</em>
          </div>
          <p>{section.body}</p>
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
          {section.citation_titles?.length ? (
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
          {section.source_traces?.length ? (
            <details className="source-trace-list">
              <summary>Источники и логика</summary>
              <div>
                {section.source_traces.map((trace) => (
                  <div key={`${section.title}-${trace.condition_key}-${trace.reference}`}>
                    <strong>{trace.condition_key}</strong>
                    <span>
                      {trace.work_title}
                      {trace.reference ? `, ${trace.reference}` : ""}
                    </span>
                    {trace.short_excerpt ? <p>{trace.short_excerpt}</p> : null}
                    <small>{trace.source_status}: {trace.interpretation}</small>
                  </div>
                ))}
              </div>
            </details>
          ) : null}
          {section.review_notes?.length ? (
            <ul className="review-notes">
              {section.review_notes.map((note) => (
                <li key={`${section.title}-${note}`}>{note}</li>
              ))}
            </ul>
          ) : null}
        </article>
      ))}
    </div>
  );
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
  const traceCount = draftAnalysis?.sections.reduce((total, section) => total + (section.source_traces?.length ?? 0), 0) ?? 0;
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
        <span>{draftAnalysis ? generatedStatusRu(draftAnalysis.review_status) : birthReport ? "готов к личному разбору" : "Отчёт ожидает расчёт"}</span>
      </div>
      <div className={`ai-billing-status report-ai-billing-status ${aiBillingStatus.tone}`}>
        <strong>{aiBillingStatus.label}</strong>
        <span>{aiBillingStatus.text}</span>
      </div>
      {birthReport ? (
        <div className="report-sections">
          <div className="draft-generation-strip">
            <div>
              <strong>Codex CLI разбор по шастра-связям</strong>
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
              Первый AI-разбор доступен бесплатно для карты, отмеченной как «моя карта». Чужие сохранённые карты можно хранить и смотреть бесплатно; AI-разбор чужой карты будет отдельным платным действием.
            </p>
            {draftAnalysis?.billing_message ? <p className="ai-billing-note">{draftAnalysis.billing_message}</p> : null}
          </div>
          {draftAnalysis ? (
            <div className="generated-draft">
              <div className="block-heading">
                <h3>{generatedTitleRu(draftAnalysis.review_status)}</h3>
                <span>
                  #{draftAnalysis.id} · {generatedStatusRu(draftAnalysis.review_status)} · {traceCount} источников
                </span>
              </div>
              <div className="codex-analysis-chat">
                <div className="chat-heading">
                  <strong>Вопросы к Codex CLI по этому разбору</strong>
                  <span>{chatStatus}</span>
                </div>
                {chatMessages.length ? (
                  <div className="chat-thread">
                    {chatMessages.map((message, index) => (
                      <div className={`chat-message ${message.role}`} key={`${message.role}-${index}-${message.content.slice(0, 24)}`}>
                        <strong>{message.role === "user" ? "Вы" : "Codex CLI"}</strong>
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
                    <em>{generatedStatusRu(draftAnalysis.review_status)}</em>
                  </div>
                  <p>{section.body}</p>
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
                  {section.source_traces?.length ? (
                    <details className="source-trace-list">
                      <summary>Источники и логика</summary>
                      <div>
                        {section.source_traces.map((trace) => (
                          <div key={`${section.title}-${trace.condition_key}-${trace.reference}`}>
                            <strong>{trace.condition_key}</strong>
                            <span>
                              {trace.work_title}
                              {trace.reference ? `, ${trace.reference}` : ""}
                            </span>
                            {trace.short_excerpt ? <p>{trace.short_excerpt}</p> : null}
                            <small>{trace.source_status}: {trace.interpretation}</small>
                          </div>
                        ))}
                      </div>
                    </details>
                  ) : null}
                  {section.review_notes?.length ? (
                    <ul className="review-notes">
                      {section.review_notes.map((note) => (
                        <li key={`${section.title}-${note}`}>{note}</li>
                      ))}
                    </ul>
                  ) : null}
                </article>
              ))}
            </div>
          ) : null}
          {birthReport.sections.map((section) => (
            <article className="report-section" key={section.key}>
              <div>
                <strong>{section.title}</strong>
                    <em>{reportSectionStatusRu(section.review_status)}</em>
              </div>
              <p>{section.body}</p>
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
          ))}
        </div>
      ) : (
        <div className="pending-strip">Отчёт появится после расчёта карты.</div>
      )}
    </section>
  );
}

function ClassicalPanel({ classical }: { classical: BirthChart["classical"] | undefined }) {
  if (!classical) {
    return (
      <section className="panel classical-panel">
        <div className="panel-heading">
          <h2>Дополнительные расчёты</h2>
          <span>Ожидает карту</span>
        </div>
        <div className="pending-strip">Авастхи, варга-сила, йоги и статусы сложных модулей появятся после расчёта.</div>
      </section>
    );
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
  const yogaCoverage = classical.yogas?.coverage ?? [];
  const yogaSummary = classical.yogas?.summary;
  const yogaCatalogTotal = yogaSummary?.catalog_total ?? (yogaCoverage.length || yogas.length);
  const pendingYogaRows = yogaCoverage
    .filter((item) => item.status === "formula_pending" || item.status === "calculation_pending")
    .slice(0, 8);
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
        <h2>Дополнительные расчёты</h2>
        <span>Расчётные слои готовы</span>
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
            <div>
              <span>Каталог</span>
              <strong>{yogaCatalogTotal}</strong>
              <small>
                найдено {yogaSummary?.detected_count ?? yogas.length}
                {yogaSummary ? ` · проверено ${yogaSummary.signature_checked_count}` : ""}
                {yogaSummary ? ` · без формулы ${yogaSummary.formula_pending_count}` : ""}
                {yogaSummary?.calculation_pending_count ? ` · ждут кода ${yogaSummary.calculation_pending_count}` : ""}
              </small>
            </div>
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
            {pendingYogaRows.length ? (
              <div>
                <span>Ещё в каталоге</span>
                <strong>{pendingYogaRows.map((item) => item.name).join(", ")}</strong>
                <small>{pendingYogaRows[0]?.formula?.description ?? "условия видны, точные формулы ещё привязываются к шастрам"}</small>
              </div>
            ) : null}
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

function ShastraAuditPanel({ audit }: { audit: BirthChart["shastra_audit"] | undefined }) {
  const items = audit?.items ?? [];

  return (
    <section className="shastra-audit-panel">
      <div className="block-heading">
        <h3>Проверка расчётов по шастрам</h3>
        <span>{audit ? `${audit.summary.source_backed}/${audit.summary.total} с опорой на шастру` : "ожидает карту"}</span>
      </div>
      {!audit ? (
        <div className="pending-strip">Аудит появится после расчёта карты.</div>
      ) : (
        <>
          <div className="shastra-policy">
            <strong>Порядок авторитета</strong>
            <span>{auditOrderRu(audit.authority_order)}</span>
            <small>
              Modern BPHS используем осторожно: если старшие источники или замечания Шьямасундары Прабху
              показывают конфликт, правило остаётся на аудите.
            </small>
          </div>
          <div className="audit-summary-grid">
            <div>
              <span>Всего слоёв</span>
              <strong>{audit.summary.total}</strong>
            </div>
            <div>
              <span>Есть опора на шастру</span>
              <strong>{audit.summary.source_backed}</strong>
            </div>
            <div>
              <span>Готово лично</span>
              <strong>{audit.summary.client_interpretation_allowed}</strong>
            </div>
            <div>
              <span>Служебный контроль</span>
              <strong>{audit.summary.partial_or_audit}</strong>
            </div>
          </div>
          <div className="readiness-note">
            Расчёт и найденные фрагменты шастр используются вместе для личного разбора. Служебная сверка хранится отдельно и не блокирует работу с картой.
          </div>
          <div className="audit-table">
            {items.map((item) => (
              <div className="audit-row" key={item.key}>
                <div>
                  <strong>{auditLayerLabelsRu[item.key] ?? item.label}</strong>
                  <span>{item.source_priority.join(", ")}</span>
                </div>
                <span>{auditCalculationReadyRu(item.implementation_status)}</span>
                <span>{auditAuthorityRu(item.authority_status)}</span>
                <em className={item.can_generate_client_interpretation ? "ready" : "draft"}>
                  {auditInterpretationReadyRu(item.can_generate_client_interpretation)}
                </em>
                <small>
                  Основа: {auditNoteRu(item.key, item.source_basis)}
                </small>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}

function ShastraEvidenceReviewPanel({
  evidence,
  status,
}: {
  evidence: ShastraEvidencePayload | null;
  status: string;
}) {
  const approvedRows = evidence?.conditions.filter((row) => row.approved_citations.length).slice(0, 5) ?? [];
  const queueRows =
    evidence?.conditions
      .filter((row) => !row.approved_citations.length && row.evidence.length)
      .slice(0, 5) ?? [];

  return (
    <section className="shastra-evidence-panel">
      <div className="block-heading">
        <h3>Шастра-фрагменты</h3>
        <span>{status}</span>
      </div>
      {evidence ? (
        <>
          <div className="audit-summary-grid">
            <div>
              <span>Условий</span>
              <strong>{evidence.summary.conditions}</strong>
            </div>
            <div>
              <span>Есть фрагменты</span>
              <strong>{evidence.summary.conditions_with_evidence}</strong>
            </div>
            <div>
              <span>Публично утверждено</span>
              <strong>{evidence.summary.approved_evidence_items}</strong>
            </div>
            <div>
              <span>Рабочие фрагменты</span>
              <strong>{evidence.summary.review_queue_items}</strong>
            </div>
          </div>
          {approvedRows.length ? (
            <div className="evidence-review-list">
              <h4>Публично готовые цитаты</h4>
              {approvedRows.map((row) => (
                <div key={row.condition_key}>
                  <strong>{row.condition_title}</strong>
                  <span>
                    {row.approved_citations[0].work_title}, {row.approved_citations[0].reference}
                  </span>
                  <small>{row.approved_citations[0].public_quote_policy}</small>
                </div>
              ))}
            </div>
          ) : null}
          <div className="evidence-review-list">
            <h4>Рабочие фрагменты для личного разбора</h4>
            {queueRows.length ? (
              queueRows.map((row) => (
                <div key={row.condition_key}>
                  <strong>{row.condition_title}</strong>
                  <span>
                    {row.evidence[0].work_title}, {row.evidence[0].inferred_reference || row.evidence[0].passage_reference}
                  </span>
                  <small>{row.evidence[0].reference_status}</small>
                </div>
              ))
            ) : (
              <p>Рабочие фрагменты ещё не найдены.</p>
            )}
          </div>
        </>
      ) : (
        <div className="pending-strip">Статус evidence загрузится при открытии источников.</div>
      )}
    </section>
  );
}

function formatArgalaRows(rows: { house: number; bodies: string[] }[]) {
  if (!rows.length) return "-";
  return rows.map((row) => `дом ${row.house}: ${row.bodies.map(labelRu).join(", ")}`).join("; ");
}

function WorkflowPlanStrip({ plan }: { plan?: WorkflowInterpretationPlan }) {
  if (!plan) return null;
  return (
    <div className="workflow-plan-strip">
      <div>
        <span>Слой</span>
        <strong>{plan.kind}</strong>
      </div>
      <div>
        <span>Факторы</span>
        <strong>{plan.required_factors.slice(0, 4).join(", ")}</strong>
      </div>
      <div>
        <span>Источники</span>
        <strong>{plan.source_anchors.slice(0, 3).join(", ")}</strong>
      </div>
      <div>
        <span>Правило текста</span>
        <strong>{plan.citation_rule}</strong>
      </div>
    </div>
  );
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
      <WorkflowPlanStrip plan={report?.interpretation_plan} />
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
      ) : (
        <div className="pending-strip">Транзиты появятся после расчёта карты.</div>
      )}
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
      <WorkflowPlanStrip plan={report?.interpretation_plan} />
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
        <div className="pending-strip">Tithi Pravesha появится после расчёта карты.</div>
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
      <WorkflowPlanStrip plan={report?.interpretation_plan} />
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
        <div className="pending-strip">Tajaka появится после расчёта карты.</div>
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
      <WorkflowPlanStrip plan={report?.interpretation_plan} />
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
        <div className="pending-strip">Prashna chart появится после расчёта карты.</div>
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
      <WorkflowPlanStrip plan={report?.interpretation_plan} />
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
        <div className="pending-strip">Mundane/event chart появится после расчёта карты.</div>
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
      <WorkflowPlanStrip plan={report?.interpretation_plan} />
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
              Паспорт пары
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
        <button className="secondary-button compatibility-button" type="submit" disabled={disabled}>
          Рассчитать совместимость
        </button>
      </form>
      <div className="compatibility-actions">
        <button
          className="secondary-button compatibility-button"
          type="button"
          onClick={onGeneratePacket}
          disabled={packetDisabled}
        >
          Codex-пакет
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
      <p className="compatibility-packet-status">{packetStatus}</p>
      <p className="compatibility-packet-status">{codexStatus}</p>
      <WorkflowPlanStrip plan={report?.interpretation_plan} />

      {report ? (
        <div className="compatibility-result">
          {resultContext ? (
            <div className="compatibility-result-context">
              <div>
                <span>Ракурс разбора</span>
                <strong>{resultContext.label || resultContext.role}</strong>
                <small>{resultContext.prompt_hint || "роль передана в расчёт и AI-пакет"}</small>
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
                <small>{resultContext.required_factors?.slice(0, 4).join(" · ") || "добавлены в interpretation plan"}</small>
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
              <span>Покрытие</span>
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
        <div className="pending-strip">Сначала рассчитай основную карту, затем добавь данные второго человека.</div>
      )}
      {codexAnalysis ? (
        <div className="compatibility-saved-analysis-card">
          <div>
            <span>Сохранённый AI-разбор</span>
            <strong>#{codexAnalysis.id} · {generatedStatusRu(codexAnalysis.review_status)}</strong>
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

function DualCalculationPanel({
  report,
  status,
}: {
  report: DualCalculationReport | null;
  status: string;
}) {
  const settingDiffs = report?.settings_diff.filter((row) => !row.matches) ?? [];
  const grahaDiffs = report?.delta.grahas
    .filter((row) => row.delta_arcseconds > 0 || !row.rashi_matches || !row.nakshatra_matches || !row.pada_matches)
    .slice(0, 8) ?? [];
  const vargaDiffs = report?.delta.vargas.rows.filter((row) => row.mismatches || row.missing).slice(0, 6) ?? [];
  const dashaDiffs = report?.delta.dashas.rows.filter((row) => row.status === "missing" || row.matches === false).slice(0, 6) ?? [];
  const shadbalaDiffs = report?.delta.shadbala.rows
    .filter((row) => row.status === "missing" || (row.delta ?? 0) !== 0)
    .slice(0, 6) ?? [];

  return (
    <section className="panel dual-calculation-panel">
      <div className="panel-heading">
        <h2>Сверка с JHora-профилем</h2>
        <span>{status}</span>
      </div>
      {!report ? (
        <div className="pending-strip">После расчёта карты здесь появится witness-сверка: наш расчёт, JHora-профиль, delta и решение по авторитету.</div>
      ) : (
        <div className="dual-content">
          <div className="dual-summary-grid">
            <div>
              <span>Макс. дельта грах</span>
              <strong>{report.delta.summary.max_graha_delta_arcseconds.toFixed(2)}"</strong>
            </div>
            <div>
              <span>Варги</span>
              <strong>{report.delta.summary.varga_mismatches}</strong>
            </div>
            <div>
              <span><GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm></span>
              <strong>{report.delta.summary.shadbala_mismatches}</strong>
            </div>
            <div>
              <span>Даши</span>
              <strong>{report.delta.summary.dasha_mismatches}</strong>
            </div>
            <div>
              <span>Решение</span>
              <strong>{report.authority_decision.needs_review ? "контроль" : "совпало"}</strong>
            </div>
          </div>
          <div className="dual-note">
            <strong>{report.authority_decision.accepted_track === "primary_calculation" ? "Оставляем наш расчёт" : report.authority_decision.accepted_track}</strong>
            <span>{report.authority_decision.reason}</span>
          </div>
          <div className="dual-columns">
            <div className="dual-list">
              <h3>Настройки</h3>
              {settingDiffs.length ? (
                settingDiffs.map((row) => (
                  <div key={row.key}>
                    <span>{settingsLabelsRu[row.key] ?? row.key}</span>
                    <strong>{String(row.primary)} → {String(row.jhora_profile)}</strong>
                  </div>
                ))
              ) : (
                <div>
                  <span>Профиль</span>
                  <strong>настройки совпадают</strong>
                </div>
              )}
            </div>
            <div className="dual-list">
              <h3>Грахи</h3>
              {report.delta.lagna ? (
                <div>
                  <span>Лагна</span>
                  <strong>{report.delta.lagna.delta_arcseconds.toFixed(2)}"</strong>
                </div>
              ) : null}
              {grahaDiffs.length ? (
                grahaDiffs.map((row) => (
                  <div key={row.body}>
                    <span>{labelRu(row.body)}</span>
                    <strong>{row.signed_delta_arcseconds.toFixed(2)}"</strong>
                    <small>{row.primary_rashi} → {row.jhora_profile_rashi}</small>
                  </div>
                ))
              ) : (
                <div>
                  <span>Долготы</span>
                  <strong>без различий</strong>
                </div>
              )}
            </div>
            <div className="dual-list">
              <h3>Варги</h3>
              {vargaDiffs.length ? (
                vargaDiffs.map((row) => (
                  <div key={row.code}>
                    <span>{row.code}</span>
                    <strong>{row.mismatches} diff, {row.missing} missing</strong>
                    {row.samples.length ? <small>{row.samples.map((sample) => `${labelRu(sample.body)} ${sample.primary}→${sample.jhora_profile}`).join("; ")}</small> : null}
                  </div>
                ))
              ) : (
                <div>
                  <span>D1-D60</span>
                  <strong>без различий</strong>
                </div>
              )}
            </div>
            <div className="dual-list">
              <h3>Даши</h3>
              {dashaDiffs.length ? (
                dashaDiffs.map((row) => (
                  <div key={row.index}>
                    <span>MD {row.index + 1}</span>
                    <strong>{row.status === "missing" ? "missing" : `${labelRu(row.primary_lord ?? "")} → ${labelRu(row.jhora_profile_lord ?? "")}`}</strong>
                    {row.primary_starts_at || row.jhora_profile_starts_at ? <small>{formatIsoTime(row.primary_starts_at)} → {formatIsoTime(row.jhora_profile_starts_at)}</small> : null}
                  </div>
                ))
              ) : (
                <div>
                  <span>Вимшоттари</span>
                  <strong>без различий</strong>
                </div>
              )}
            </div>
            <div className="dual-list">
              <h3><GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm></h3>
              {shadbalaDiffs.length ? (
                shadbalaDiffs.map((row) => (
                  <div key={row.body}>
                    <span>{labelRu(row.body)}</span>
                    <strong>{row.status === "missing" ? "missing" : `${row.delta?.toFixed(2)} virupa`}</strong>
                  </div>
                ))
              ) : (
                <div>
                  <span>Итоги</span>
                  <strong>без различий</strong>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

function shortHash(value?: string) {
  return value ? value.slice(0, 12) : "missing";
}

function formatWitnessDiffValue(value: string | number | null | undefined) {
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(6);
  return value === null || value === undefined || value === "" ? "n/a" : String(value);
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
  const longitude = report?.summary.longitude;
  const groups = report?.summary.exact_groups ?? [];
  const layers = report ? Object.entries(report.summary.jhora_layers) : [];
  const plSummary = plReport?.summary ?? null;
  const manualComparison = plReport?.manual_witness_comparison ?? null;
  const screenshotFingerprint = plSummary?.fingerprints.screenshots?.[0];
  const birthTimezoneAudit = witnessSummary?.birth_timezone_audit ?? null;
  const jhoraBirthExport = witnessSummary?.jhora.birth_export ?? null;
  const plProfile = witnessSummary?.parashara_light.profile ?? null;
  const plProfileFlags = Array.isArray(plProfile?.data_quality_flags) ? plProfile.data_quality_flags : [];
  const plProfileComparison = plProfile?.packet_comparison ?? {};
  const plProfileNormalization = plProfile?.candidate_normalization ?? {};
  const plProfileRawBirth = plProfile?.raw_birth_info ?? {};
  const plForensic = witnessSummary?.parashara_light.forensic ?? null;
  const plForensicMaxDeviation =
    typeof plForensic?.pl_swiss_max_abs_arcsec === "number" ? plForensic.pl_swiss_max_abs_arcsec : null;
  const plForensicRowHealth = plForensic?.row_health ?? { total: 0, matched: 0, diff_open: 0 };
  const plSettingsEvidence = witnessSummary?.parashara_light.settings_evidence ?? null;
  const plVisibleSettingsCapture = witnessSummary?.parashara_light.visible_settings_capture ?? null;
  const plCalculationOptions = witnessSummary?.parashara_light.calculation_options ?? null;
  const plSettingsAwareForensic = witnessSummary?.parashara_light.settings_aware_forensic ?? null;
  const plPreferencesInventory = witnessSummary?.parashara_light.preferences_inventory ?? null;
  const plHiddenOptionStore = witnessSummary?.parashara_light.hidden_option_store ?? null;
  const plOptionStoreDiff = witnessSummary?.parashara_light.option_store_diff ?? null;
  const plInternalSettingsAudit = witnessSummary?.parashara_light.internal_settings_audit ?? null;
  const witnessReview = witnessSummary?.witness_review ?? null;
  const witnessReviewBatch = witnessSummary?.witness_review_batch ?? null;
  const witnessReviewBatchSummary = witnessReviewBatch?.summary ?? null;
  const witnessReviewBatchMetadata = witnessReviewBatch?.metadata ?? null;
  const witnessReviewBatchWritten = witnessReviewBatch?.written ?? [];
  const witnessReviewBatchNextActions = witnessReviewBatch?.next_actions ?? [];
  const witnessReviewBatchSkippedReasons = witnessReviewBatch?.skipped_reason_counts ?? {};
  const witnessCaptureQueue = witnessSummary?.witness_capture_queue ?? null;
  const witnessCaptureQueueSummary = witnessCaptureQueue?.summary ?? null;
  const witnessCaptureQueueMetadata = witnessCaptureQueue?.metadata ?? null;
  const witnessCaptureQueueItems = witnessCaptureQueue?.items ?? [];
  const witnessCaptureQueueNext = witnessCaptureQueue?.next_item ?? witnessCaptureQueueItems[0] ?? null;
  const witnessCaptureQueueNextStepLabel =
    witnessCaptureQueue?.next_step_label || witnessCaptureQueueNext?.next_step_label || "Next step";
  const witnessCaptureQueueNextCommand =
    witnessCaptureQueue?.next_command ||
    witnessCaptureQueue?.manual_review_command ||
    witnessCaptureQueueNext?.next_command ||
    witnessCaptureQueueNext?.manual_review_command ||
    "manual capture/review";
  const witnessCaptureQueueNextAction =
    witnessCaptureQueue?.next_action_label ||
    witnessCaptureQueueNext?.next_action_label ||
    witnessCaptureQueue?.next_action_key ||
    witnessCaptureQueueNext?.next_action_key ||
    witnessCaptureQueueNext?.status ||
    witnessCaptureQueue?.next_command_kind ||
    "review";
  const witnessOpenDiffs = witnessReview?.open_diffs ?? null;
  const witnessOpenDiffRows = [
    ...(witnessOpenDiffs?.jhora.sample ?? []).map((row) => ({ source: "JHora", row })),
    ...(witnessOpenDiffs?.parashara_light.sample ?? []).map((row) => ({ source: "PL", row })),
  ].slice(0, 6);
  const witnessReviewChecklist = witnessReview?.review_checklist ?? [];
  const hasWitnessCaptureQueueNext =
    Boolean(witnessCaptureQueueNext) ||
    Boolean(witnessCaptureQueue?.next_step_label) ||
    Boolean(witnessCaptureQueue?.next_command) ||
    Boolean(witnessCaptureQueue?.manual_review_command);

  return (
    <section className="panel accuracy-panel" id="accuracy">
      <div className="panel-heading">
        <h2>Witness summary</h2>
        <span>{witnessStatus}</span>
      </div>
      {witnessSummary ? (
        <div className="accuracy-content">
          <div className="accuracy-summary-grid witness-summary-grid">
            <div>
              <span>Overall</span>
              <strong>{witnessSummary.overall_status}</strong>
            </div>
            <div>
              <span>JHora</span>
              <strong>{witnessSummary.jhora.available ? witnessSummary.jhora.status : "missing"}</strong>
              {witnessSummary.jhora.available ? (
                <small>
                  {jhoraBirthExport?.parsed_utc_offset
                    ? `${jhoraBirthExport.parsed_utc_offset}, ${witnessSummary.jhora.failed_checks} failed`
                    : `${witnessSummary.jhora.failed_checks} failed`}
                </small>
              ) : null}
            </div>
            <div>
              <span>PL</span>
              <strong>{witnessSummary.parashara_light.available ? witnessSummary.parashara_light.status : "missing"}</strong>
              {witnessSummary.parashara_light.available ? (
                <small>{witnessSummary.parashara_light.manual_completion_percent}% filled</small>
              ) : null}
            </div>
            <div>
              <span>PL profile</span>
              <strong>{plProfile?.available ? plProfile.status : "missing"}</strong>
              {plProfile?.available ? (
                <small>
                  {plProfileFlags.length} flags, authoritative: {plProfile.authoritative ? "yes" : "no"}
                </small>
              ) : null}
            </div>
            <div>
              <span>Birth timezone</span>
              <strong>{birthTimezoneAudit?.available ? birthTimezoneAudit.resolved_utc_offset || "resolved" : "missing"}</strong>
              {birthTimezoneAudit?.available ? (
                <small>DST {birthTimezoneAudit.dst_observed ? "yes" : "no"}</small>
              ) : null}
            </div>
            <div>
              <span>Open items</span>
              <strong>{witnessSummary.open_items.length}</strong>
            </div>
          </div>
          {witnessReview ? (
            <div className="accuracy-list witness-open-items witness-seal-gate">
              <h3>Witness seal gate</h3>
              <div>
                <span>Status</span>
                <strong>{witnessReview.available ? (witnessReview.overall.reviewable ? "reviewable" : witnessReview.status) : "missing"}</strong>
                <small>
                  ACK {witnessReview.overall.ack_required ? "required" : "not required"}, blocked{" "}
                  {witnessReview.overall.blocked ? "yes" : "no"}
                </small>
              </div>
              <div>
                <span>Safe next step</span>
                <strong>{witnessReview.safe_next_step || "review preflight first"}</strong>
                <small>mutating review commands hidden from summary API</small>
              </div>
              <div>
                <span>JHora / PL</span>
                <strong>
                  {witnessReview.jhora.status ?? "missing"} / {witnessReview.parashara_light.status ?? "missing"}
                </strong>
                <small>
                  {witnessReview.jhora.id ?? "JHora missing"} · {witnessReview.parashara_light.id ?? "PL missing"}
                </small>
              </div>
              {witnessOpenDiffs ? (
                <div>
                  <span>Open diffs</span>
                  <strong>
                    JHora {witnessOpenDiffs.jhora.failed_count}, PL {witnessOpenDiffs.parashara_light.failed_count}
                  </strong>
                  <small>{witnessOpenDiffs.status}</small>
                </div>
              ) : null}
              {witnessReviewChecklist.slice(0, 4).map((item) => (
                <div key={item.key}>
                  <span>{item.label}</span>
                  <strong>{item.status}</strong>
                  <small>{item.next_step ? `${item.detail}; next: ${item.next_step}` : item.detail}</small>
                </div>
              ))}
              {witnessOpenDiffRows.map(({ source, row }, index) => (
                <div key={`${source}-${row.field}-${index}`}>
                  <span>
                    {source} {row.field}
                  </span>
                  <strong>
                    {formatWitnessDiffValue(row.witness)} / {formatWitnessDiffValue(row.calculated)}
                  </strong>
                  <small>
                    {typeof row.delta_arcseconds === "number"
                      ? `${row.delta_arcseconds.toFixed(2)} arcsec`
                      : "exact diff"}
                  </small>
                </div>
              ))}
            </div>
          ) : null}
          {witnessReviewBatch ? (
            <div className="accuracy-list witness-open-items">
              <h3>Witness batch review</h3>
              <div>
                <span>Packets</span>
                <strong>
                  {witnessReviewBatch.available
                    ? `${witnessReviewBatchSummary?.written_count ?? 0} written`
                    : witnessReviewBatch.status}
                </strong>
                <small>
                  skipped {witnessReviewBatchSummary?.skipped_count ?? 0}, errors{" "}
                  {witnessReviewBatchSummary?.error_count ?? 0}
                </small>
              </div>
              <div>
                <span>Progress</span>
                <strong>
                  {witnessReviewBatchSummary?.batch_review_ready_count ?? 0} /{" "}
                  {witnessReviewBatchSummary?.target_reviewed_count ?? 0} ready
                </strong>
                <small>
                  remaining {witnessReviewBatchSummary?.remaining_to_target_count ?? 0}, reviewable{" "}
                  {witnessReviewBatchSummary?.reviewable_count ?? 0}, blocked{" "}
                  {witnessReviewBatchSummary?.blocked_count ?? 0}, ACK{" "}
                  {witnessReviewBatchSummary?.ack_required_count ?? 0}
                </small>
              </div>
              <div>
                <span>Index</span>
                <strong>{witnessReviewBatchSummary?.index_path || witnessReviewBatch.source_index || "missing"}</strong>
                <small>{witnessReviewBatchSummary?.index_json_path || "JSON index missing"}</small>
              </div>
              <div>
                <span>Generated</span>
                <strong>{witnessReviewBatchMetadata?.generated_at || "unknown"}</strong>
                <small>
                  reviewer {witnessReviewBatchMetadata?.reviewer || "n/a"}, reviewed at{" "}
                  {witnessReviewBatchMetadata?.reviewed_at || "n/a"}
                </small>
              </div>
              <div>
                <span>Next review</span>
                <strong>{witnessReviewBatchSummary?.next_review_case_id || "none"}</strong>
                <small>{witnessReviewBatchSummary?.next_review_step || "none"}</small>
              </div>
              {witnessReviewBatchWritten.slice(0, 3).map((row) => (
                <div key={row.id}>
                  <span>{row.id}</span>
                  <strong>
                    {row.reviewable ? "reviewable" : "not reviewable"} / ACK {row.ack_required ? "yes" : "no"}
                  </strong>
                  <small>
                    {row.safe_next_step};{" "}
                    {row.review_checklist_next_steps_summary !== "none"
                      ? row.review_checklist_next_steps_summary
                      : row.review_checklist_summary !== "none"
                        ? row.review_checklist_summary
                        : row.output_path}
                  </small>
                </div>
              ))}
              {witnessReviewBatchSummary?.next_case_ids?.length ? (
                <div>
                  <span>Next cases</span>
                  <strong>{witnessReviewBatchSummary.next_case_ids.slice(0, 4).join(", ")}</strong>
                </div>
              ) : null}
              {witnessReviewBatchNextActions.slice(0, 3).map((row) => (
                <div key={`next-${row.id}`}>
                  <span>{row.label || row.id}</span>
                  <strong>{row.suggested_action_labels.slice(0, 3).join(", ") || row.status || "review"}</strong>
                  <small>
                    JHora {row.missing_for_authoritative_review.join(", ") || "ok"}; PL{" "}
                    {row.missing_secondary_witness.join(", ") || "ok"}
                  </small>
                </div>
              ))}
              {Object.keys(witnessReviewBatchSkippedReasons).length ? (
                <div>
                  <span>Skipped reasons</span>
                  <strong>
                    {Object.entries(witnessReviewBatchSkippedReasons)
                      .map(([reason, count]) => `${reason}: ${count}`)
                      .join(", ")}
                  </strong>
                </div>
              ) : null}
            </div>
          ) : null}
          {witnessCaptureQueue ? (
            <div className="accuracy-list witness-open-items">
              <h3>Witness capture queue</h3>
              <div>
                <span>Queue</span>
                <strong>
                  {witnessCaptureQueue.available
                    ? `${witnessCaptureQueueSummary?.queue_count ?? 0} cases`
                    : witnessCaptureQueue.status}
                </strong>
                <small>
                  remaining {witnessCaptureQueueSummary?.remaining_to_target_count ?? 0}, ready{" "}
                  {witnessCaptureQueueSummary?.batch_review_ready_count ?? 0}
                </small>
              </div>
              <div>
                <span>Coverage</span>
                <strong>{witnessCaptureQueueSummary?.capture_started_count ?? 0} capture-started</strong>
                <small>
                  PL witnesses {witnessCaptureQueueSummary?.pl_witness_count ?? 0}, target{" "}
                  {witnessCaptureQueueMetadata?.target_reviewed_count ?? 0}
                </small>
              </div>
              <div>
                <span>Markdown</span>
                <strong>{witnessCaptureQueueSummary?.markdown_output || "missing"}</strong>
                <small>{witnessCaptureQueue.source_queue || witnessCaptureQueueSummary?.output || "queue missing"}</small>
              </div>
              {hasWitnessCaptureQueueNext ? (
                <div>
                  <span>{witnessCaptureQueueNextStepLabel}</span>
                  <strong>{witnessCaptureQueueNextAction}</strong>
                  <small>{witnessCaptureQueueNextCommand}</small>
                </div>
              ) : null}
              {witnessCaptureQueueItems.slice(0, 3).map((row) => (
                <div key={`capture-${row.id}`}>
                  <span>
                    {row.priority}. {row.label || row.id}
                  </span>
                  <strong>{row.suggested_action_labels.slice(0, 3).join(", ") || row.status || "review"}</strong>
                  <small>
                    JHora {row.capture_targets.jhora.join(", ") || "ok"}; PL{" "}
                    {row.capture_targets.parashara_light.join(", ") || "ok"}
                  </small>
                </div>
              ))}
            </div>
          ) : null}
          {birthTimezoneAudit?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>Birth timezone audit</h3>
              <div>
                <span>Status</span>
                <strong>{birthTimezoneAudit.status}</strong>
                <small>{birthTimezoneAudit.timezone_source || "timezone source unknown"}</small>
              </div>
              <div>
                <span>Offset</span>
                <strong>
                  {birthTimezoneAudit.resolved_utc_offset || "n/a"}
                  {birthTimezoneAudit.expected_utc_offset
                    ? ` expected ${birthTimezoneAudit.expected_utc_offset}`
                    : ""}
                </strong>
                <small>
                  local {birthTimezoneAudit.local_datetime_utc_offset || "n/a"}, DST{" "}
                  {birthTimezoneAudit.dst_observed ? "observed" : "not observed"}
                </small>
              </div>
              <div>
                <span>UTC</span>
                <strong>{birthTimezoneAudit.utc_datetime || "not captured"}</strong>
                <small>{birthTimezoneAudit.local_datetime || "local time missing"}</small>
              </div>
            </div>
          ) : null}
          {jhoraBirthExport?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>JHora birth export</h3>
              <div>
                <span>Birth time</span>
                <strong>{jhoraBirthExport.time || "not captured"}</strong>
                <small>{jhoraBirthExport.date || "date missing"}</small>
              </div>
              <div>
                <span>Timezone</span>
                <strong>{jhoraBirthExport.parsed_utc_offset || "not parsed"}</strong>
                <small>{jhoraBirthExport.timezone_line || "Time Zone line missing"}</small>
              </div>
              <div>
                <span>Place</span>
                <strong>{jhoraBirthExport.place || "not captured"}</strong>
                <small>{jhoraBirthExport.source_export || "export missing"}</small>
              </div>
            </div>
          ) : null}
          {plForensic?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL forensic dump</h3>
              <div>
                <span>Conclusion</span>
                <strong>{plForensic.conclusion || "not set"}</strong>
                <small>{plForensic.pl_diff_count} PL diffs</small>
              </div>
              <div>
                <span>Hypotheses</span>
                <strong>
                  offset {plForensic.uniform_offset_status || "n/a"}, time {plForensic.time_shift_status || "n/a"}
                </strong>
                <small>max {plForensicMaxDeviation !== null ? plForensicMaxDeviation.toFixed(2) : "n/a"}"</small>
              </div>
              <div>
                <span>Next action</span>
                <strong>{plForensic.next_action || "none"}</strong>
                <small>
                  rows {plForensicRowHealth.matched}/{plForensicRowHealth.total} matched
                </small>
              </div>
            </div>
          ) : null}
          {plSettingsEvidence?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL settings evidence</h3>
              <div>
                <span>Runtime</span>
                <strong>{plSettingsEvidence.runtime_build || "captured"}</strong>
                <small>{plSettingsEvidence.proprietary_binary_policy || "hash-only"}</small>
              </div>
              <div>
                <span>Manifests</span>
                <strong>{plSettingsEvidence.options_files_count} option files</strong>
                <small>
                  {plSettingsEvidence.session_tokens_count} sessions, {plSettingsEvidence.text_artifacts_count} text artifacts
                </small>
              </div>
              <div>
                <span>Next action</span>
                <strong>{plSettingsEvidence.next_action || "capture_visible_pl_profile_settings"}</strong>
                <small>{plSettingsEvidence.artifact_policy || "private audit"}</small>
              </div>
            </div>
          ) : null}
          {plVisibleSettingsCapture?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL visible settings capture</h3>
              <div>
                <span>Status</span>
                <strong>{plVisibleSettingsCapture.status || "captured"}</strong>
                <small>
                  dialog {plVisibleSettingsCapture.settings_dialog_captured ? "yes" : "pending"}, menu{" "}
                  {plVisibleSettingsCapture.options_menu_captured ? "yes" : "no"}
                </small>
              </div>
              <div>
                <span>Artifacts</span>
                <strong>{plVisibleSettingsCapture.screenshots_count} screenshots</strong>
                <small>{plVisibleSettingsCapture.surfaces_count} UI states</small>
              </div>
              <div>
                <span>Next action</span>
                <strong>{plVisibleSettingsCapture.next_action || "capture_calculation_options_dialog_or_native_export"}</strong>
              </div>
            </div>
          ) : null}
          {plCalculationOptions?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL calculation options</h3>
              <div>
                <span>Ayanamsha</span>
                <strong>{plCalculationOptions.selected_ayanamsha_label || "not captured"}</strong>
                <small>{plCalculationOptions.status || "captured"}</small>
              </div>
              <div>
                <span>Method</span>
                <strong>{plCalculationOptions.selected_calculation_method_label || "not captured"}</strong>
                <small>pixel-probed from PL7 dialog</small>
              </div>
              <div>
                <span>Controls</span>
                <strong>{plCalculationOptions.offset_value || "offset missing"}</strong>
                <small>{plCalculationOptions.selected_miscellaneous_item_label || "misc selection missing"}</small>
              </div>
            </div>
          ) : null}
          {plSettingsAwareForensic?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL settings-aware forensic</h3>
              <div>
                <span>Status</span>
                <strong>{plSettingsAwareForensic.status || "captured"}</strong>
                <small>{plSettingsAwareForensic.next_action || "review"}</small>
              </div>
              <div>
                <span>Visible settings</span>
                <strong>{plSettingsAwareForensic.ayanamsha_status || "unknown"}</strong>
                <small>{plSettingsAwareForensic.offset_status || "offset unknown"}</small>
              </div>
              <div>
                <span>Forensic gates</span>
                <strong>{plSettingsAwareForensic.engine_swiss_status || "unknown"}</strong>
                <small>
                  offset {plSettingsAwareForensic.uniform_offset_status || "n/a"}, time{" "}
                  {plSettingsAwareForensic.time_shift_status || "n/a"}
                </small>
              </div>
            </div>
          ) : null}
          {plPreferencesInventory?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL preferences inventory</h3>
              <div>
                <span>Status</span>
                <strong>{plPreferencesInventory.status || "captured"}</strong>
                <small>{plPreferencesInventory.next_action || "review"}</small>
              </div>
              <div>
                <span>Visible controls</span>
                <strong>{plPreferencesInventory.visible_ayanamsha_controls ? "ayanamsha visible" : "ayanamsha missing"}</strong>
                <small>{plPreferencesInventory.visible_system_paths ? "system paths visible" : "system paths missing"}</small>
              </div>
              <div>
                <span>Ephemeris mode</span>
                <strong>{plPreferencesInventory.internal_ephemeris_mode_visible ? "visible" : "not visible"}</strong>
                <small>{plPreferencesInventory.tabs_count} tabs/states reviewed</small>
              </div>
            </div>
          ) : null}
          {plHiddenOptionStore?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL hidden option store</h3>
              <div>
                <span>Status</span>
                <strong>{plHiddenOptionStore.status || "captured"}</strong>
                <small>{plHiddenOptionStore.proprietary_binary_policy || "hash-only"}</small>
              </div>
              <div>
                <span>Primary</span>
                <strong>{plHiddenOptionStore.primary_candidate || "not identified"}</strong>
                <small>
                  {plHiddenOptionStore.option_store_candidates_count} option candidates,{" "}
                  {plHiddenOptionStore.session_token_candidates_count} sessions
                </small>
              </div>
              <div>
                <span>Next action</span>
                <strong>{plHiddenOptionStore.next_action || "review"}</strong>
              </div>
            </div>
          ) : null}
          {plOptionStoreDiff?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL option store diff</h3>
              <div>
                <span>Status</span>
                <strong>{plOptionStoreDiff.status || "captured"}</strong>
                <small>{plOptionStoreDiff.proprietary_binary_policy || "hash-only"}</small>
              </div>
              <div>
                <span>Changed</span>
                <strong>{plOptionStoreDiff.primary_candidate || "none"}</strong>
                <small>
                  {plOptionStoreDiff.changed_candidates_count} candidates, restore{" "}
                  {plOptionStoreDiff.restore_verified ? "verified" : "not verified"}
                </small>
              </div>
              <div>
                <span>Setting</span>
                <strong>{plOptionStoreDiff.visible_setting || "not captured"}</strong>
                <small>{plOptionStoreDiff.next_action || "review"}</small>
              </div>
            </div>
          ) : null}
          {plInternalSettingsAudit?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL internal settings audit</h3>
              <div>
                <span>Status</span>
                <strong>{plInternalSettingsAudit.status || "captured"}</strong>
                <small>{plInternalSettingsAudit.visible_settings_status || "visible settings reviewed"}</small>
              </div>
              <div>
                <span>Gates</span>
                <strong>{plInternalSettingsAudit.option_store_diff_status || "option store pending"}</strong>
                <small>
                  ephemeris mode {plInternalSettingsAudit.internal_ephemeris_mode_visible ? "visible" : "not visible"}
                </small>
              </div>
              <div>
                <span>Next action</span>
                <strong>{plInternalSettingsAudit.next_action || "review"}</strong>
                <small>{plInternalSettingsAudit.ruled_out_count} ruled out</small>
              </div>
            </div>
          ) : null}
          {plProfile?.available ? (
            <div className="accuracy-list witness-open-items">
              <h3>PL birth XML profile</h3>
              <div>
                <span>PL XML timezone</span>
                <strong>
                  TimeZone {String(plProfileRawBirth.timezone ?? "n/a")}, DST{" "}
                  {String(plProfileRawBirth.dst ?? "n/a")}
                </strong>
                <small>
                  {String(plProfileNormalization.timezone_formula ?? "formula missing")}
                  {typeof plProfileNormalization.timezone_offset_hours_candidate === "number"
                    ? ` => ${plProfileNormalization.timezone_offset_hours_candidate.toFixed(2)}h`
                    : ""}
                </small>
              </div>
              <div>
                <span>Coordinates</span>
                <strong>
                  {typeof plProfileComparison.longitude_delta_degrees === "number"
                    ? `${plProfileComparison.longitude_delta_degrees.toFixed(6)}°`
                    : "not compared"}
                </strong>
                <small>
                  lat{" "}
                  {typeof plProfileComparison.latitude_delta_degrees === "number"
                    ? plProfileComparison.latitude_delta_degrees.toFixed(6)
                    : "n/a"}
                </small>
              </div>
              <div>
                <span>Timezone</span>
                <strong>
                  {typeof plProfileComparison.timezone_delta_hours === "number"
                    ? `${plProfileComparison.timezone_delta_hours.toFixed(2)}h delta`
                    : "not compared"}
                </strong>
                <small>candidate, not authoritative</small>
              </div>
              {plProfileFlags.length ? (
                <div>
                  <span>Flags</span>
                  <strong>{plProfileFlags.slice(0, 2).join(", ")}</strong>
                  {plProfileFlags.length > 2 ? (
                    <small>+{plProfileFlags.length - 2} more</small>
                  ) : null}
                </div>
              ) : null}
            </div>
          ) : null}
          {witnessSummary.open_items.length ? (
            <div className="accuracy-list witness-open-items">
              <h3>Open witness work</h3>
              {witnessSummary.open_items.map((item) => (
                <div key={`${item.source}-${item.status}-${item.label}`}>
                  <span>{item.source}</span>
                  <strong>{item.label}</strong>
                  <small>
                    {item.next_action
                      ? `${item.next_action}${item.failed_checks !== undefined ? `, ${item.failed_checks} failed` : ""}`
                      : item.failed_checks !== undefined
                        ? `${item.failed_checks} failed`
                        : `${item.completion_percent ?? 0}% filled`}
                  </small>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      ) : (
        <div className="pending-strip">Witness summary ещё не загружен.</div>
      )}
      <div className="panel-heading">
        <h2>JHora export accuracy</h2>
        <span>{status}</span>
      </div>
      {!report || !longitude ? (
        <div className="pending-strip">JHora export report ещё не загружен.</div>
      ) : (
        <div className="accuracy-content">
          <div className="accuracy-summary-grid">
            <div>
              <span>Fixture</span>
              <strong>{report.fixture_id}</strong>
            </div>
            <div>
              <span>Статус</span>
              <strong>{report.passed ? "passed" : "diff open"}</strong>
            </div>
            <div>
              <span>Макс. долгота</span>
              <strong>{longitude.max_delta_arcseconds.toFixed(2)}"</strong>
            </div>
            <div>
              <span>После ayanamsa</span>
              <strong>{longitude.corrected_max_delta_arcseconds.toFixed(2)}"</strong>
            </div>
            <div>
              <span>Ayanamsa delta</span>
              <strong>{longitude.ayanamsa_delta_arcseconds.toFixed(2)}"</strong>
            </div>
          </div>
          <div className="accuracy-columns">
            <div className="accuracy-list">
              <h3>Longitudes</h3>
              {longitude.failed_samples.length ? (
                longitude.failed_samples.map((row) => (
                  <div key={row.body}>
                    <span>{labelRu(row.body)}</span>
                    <strong>{row.signed_delta_arcseconds.toFixed(2)}"</strong>
                  </div>
                ))
              ) : (
                <div>
                  <span>Grahas</span>
                  <strong>без расхождений</strong>
                </div>
              )}
            </div>
            <div className="accuracy-list">
              <h3>Groups</h3>
              {groups.map((group) => (
                <div key={group.key}>
                  <span>{group.key}</span>
                  <strong>{group.passed}/{group.total}</strong>
                  {group.failed ? <small>{group.failed_samples.slice(0, 3).join(", ")}</small> : null}
                </div>
              ))}
            </div>
            <div className="accuracy-list">
              <h3>JHora layers</h3>
              {layers.map(([key, layer]) => (
                <div key={key}>
                  <span>{key}</span>
                  <strong>{String(layer.matched ?? 0)}/{String(layer.checked ?? 0)}</strong>
                  {layer.max_abs_delta ? <small>max {String(layer.max_abs_delta)}</small> : null}
                </div>
              ))}
            </div>
          </div>
          <p className="accuracy-footnote">{report.source_export}</p>
        </div>
      )}
      <div className="panel-heading accuracy-subheading">
        <h2>Parashara Light witness packet</h2>
        <span>{plStatus}</span>
      </div>
      {!plReport || !plSummary ? (
        <div className="pending-strip">Parashara Light packet ещё не загружен.</div>
      ) : (
        <div className="accuracy-content">
          <div className="accuracy-summary-grid">
            <div>
              <span>Packet</span>
              <strong>{plReport.id}</strong>
            </div>
            <div>
              <span>Status</span>
              <strong>{plReport.status}</strong>
            </div>
            <div>
              <span>Review</span>
              <strong>{plSummary.review_status || "unknown"}</strong>
            </div>
            <div>
              <span>PL version</span>
              <strong>{plSummary.version_required || "unknown"}</strong>
            </div>
            <div>
              <span>Controls</span>
              <strong>{plSummary.control_count ?? "unknown"}</strong>
            </div>
            <div>
              <span>Screenshots</span>
              <strong>{plSummary.screenshots_count}</strong>
            </div>
            <div>
              <span>Blank shot</span>
              <strong>{plSummary.screenshot_blank ? "yes" : "no"}</strong>
            </div>
            <div>
              <span>Lagna</span>
              <strong>{plSummary.jyotish_agent_lagna || "unknown"}</strong>
            </div>
            <div>
              <span>Manual values</span>
              <strong>{manualComparison?.summary.manual_values_count ?? 0}</strong>
            </div>
            <div>
              <span>Manual diff</span>
              <strong>{manualComparison?.summary.failed_count ?? 0}</strong>
            </div>
            <div>
              <span>Manual filled</span>
              <strong>{manualComparison ? `${manualComparison.completion.completion_percent}%` : "0%"}</strong>
            </div>
          </div>
          <div className="accuracy-columns">
            <div className="accuracy-list">
              <h3>Capture</h3>
              <div>
                <span>Window</span>
                <strong>{plSummary.window_title || "unknown"}</strong>
              </div>
              <div>
                <span>Capture status</span>
                <strong>{plSummary.capture_status || "unknown"}</strong>
              </div>
              {plSummary.screenshot_error ? (
                <div>
                  <span>Screenshot error</span>
                  <strong>{plSummary.screenshot_error}</strong>
                </div>
              ) : null}
            </div>
            <div className="accuracy-list">
              <h3>Fingerprints</h3>
              <div>
                <span>UI state</span>
                <strong>{shortHash(plSummary.fingerprints.ui_state?.sha256)}</strong>
                {plSummary.fingerprints.ui_state?.bytes ? <small>{plSummary.fingerprints.ui_state.bytes} bytes</small> : null}
              </div>
              <div>
                <span>Screenshot</span>
                <strong>{shortHash(screenshotFingerprint?.sha256)}</strong>
                {screenshotFingerprint?.bytes ? <small>{screenshotFingerprint.bytes} bytes</small> : null}
              </div>
            </div>
            <div className="accuracy-list">
              <h3>Manual witness</h3>
              <div>
                <span>Status</span>
                <strong>{manualComparison?.status ?? "no_manual_values"}</strong>
              </div>
              <div>
                <span>Source</span>
                <strong>{plReport.manual_witness_source || "none"}</strong>
              </div>
              <div>
                <span>Filled / empty</span>
                <strong>
                  {manualComparison?.completion.filled_fields_count ?? 0} / {manualComparison?.completion.empty_fields_count ?? 0}
                </strong>
              </div>
              {manualComparison?.completion.empty_field_sample.length ? (
                <div>
                  <span>Missing sample</span>
                  <strong>{manualComparison.completion.empty_field_sample.slice(0, 4).join(", ")}</strong>
                </div>
              ) : null}
              {manualComparison?.diffs.slice(0, 4).map((diff) => (
                <div key={`${diff.source}-${diff.body}-${diff.field}`}>
                  <span>{diff.body}.{diff.field}</span>
                  <strong>{String(diff.witness)} / {String(diff.calculated)}</strong>
                  {diff.delta_arcseconds ? <small>{diff.delta_arcseconds.toFixed(2)}"</small> : null}
                </div>
              ))}
            </div>
            <div className="accuracy-list">
              <h3>Checklist</h3>
              <div>
                <span>Items</span>
                <strong>{plReport.checklist_count}</strong>
              </div>
              <div>
                <span>Schema</span>
                <strong>{plReport.schema_version}</strong>
              </div>
            </div>
          </div>
          <p className="accuracy-footnote">{plReport.source_packet}</p>
        </div>
      )}
    </section>
  );
}

export default function Home() {
  const [birthDate, setBirthDate] = useState("1998-04-30");
  const [birthTime, setBirthTime] = useState("13:45");
  const [gender, setGender] = useState<"male" | "female" | "unknown">("male");
  const [placeName, setPlaceName] = useState("Стерлитамак");
  const [profileName, setProfileName] = useState("Моя карта 30.04.1998");
  const [profileIsSelf, setProfileIsSelf] = useState(true);
  const [placeMatches, setPlaceMatches] = useState<PlaceCandidate[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<PlaceCandidate | null>(null);
  const [manualTimezone, setManualTimezone] = useState("Asia/Yekaterinburg");
  const [manualLatitude, setManualLatitude] = useState("53.6304");
  const [manualLongitude, setManualLongitude] = useState("55.9308");
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
  const [activeVargaFocusKey, setActiveVargaFocusKey] = useState("core");
  const [activeVargaSchemeKey, setActiveVargaSchemeKey] = useState<VargaSchemeKey>("shodasha");
  const [chartReference, setChartReference] = useState<ChartReference>("lagna");
  const [chartStyle, setChartStyle] = useState<"north" | "south">("north");
  const [termLanguage, setTermLanguage] = useState<TermLanguage>("sanskrit");
  const [houseHintsEnabled, setHouseHintsEnabled] = useState(true);
  const [interfaceMode, setInterfaceMode] = useState<InterfaceMode>("pro");
  const [chartWorkspaceTab, setChartWorkspaceTab] = useState<ChartWorkspaceTab>("essentials");
  const [vargaCoverageOpen, setVargaCoverageOpen] = useState(false);
  const [chartStyleHydrated, setChartStyleHydrated] = useState(false);
  const [chartViewHydrated, setChartViewHydrated] = useState(false);
  const [showBirthEditor, setShowBirthEditor] = useState(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(true);
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<AnalysisTab>(() => analysisTabFromLocation());
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
  const [dualCalculationReport, setDualCalculationReport] = useState<DualCalculationReport | null>(null);
  const [accuracyReport, setAccuracyReport] = useState<JHoraAccuracyReport | null>(null);
  const [plPacketReport, setPlPacketReport] = useState<ParasharaLightPacketReport | null>(null);
  const [witnessSummary, setWitnessSummary] = useState<WitnessSummary | null>(null);
  const [lastBirthPayload, setLastBirthPayload] = useState<BirthChartRequest | null>(null);
  const [status, setStatus] = useState("Расчёт не запускался");
  const [workflowStatus, setWorkflowStatus] = useState("Ожидает расчёт карты");
  const [dualCalculationStatus, setDualCalculationStatus] = useState("JHora witness ещё не считался");
  const [accuracyStatus, setAccuracyStatus] = useState("JHora export report не загружен");
  const [plPacketStatus, setPlPacketStatus] = useState("Parashara Light packet не загружен");
  const [witnessSummaryStatus, setWitnessSummaryStatus] = useState("Witness summary не загружен");
  const [compatibilityStatus, setCompatibilityStatus] = useState("Ожидает основную карту");
  const [compatibilityPacketStatus, setCompatibilityPacketStatus] = useState("Codex-пакет ещё не сформирован");
  const [compatibilityCodexAnalysis, setCompatibilityCodexAnalysis] = useState<GeneratedDraftAnalysis | null>(null);
  const [compatibilityCodexStatus, setCompatibilityCodexStatus] = useState("Полный разбор совместимости ещё не запускался");
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
  const [sourceQuery, setSourceQuery] = useState("Krishna protects devotee");
  const [sourceResults, setSourceResults] = useState<VLSearchResult[]>([]);
  const [researchResults, setResearchResults] = useState<ResearchSearchResult[]>([]);
  const [researchStatus, setResearchStatus] = useState("Private corpus not searched");
  const [sourceInventory, setSourceInventory] = useState<SourceInventory | null>(null);
  const [sourceWorks, setSourceWorks] = useState<SourceWorkSummary[]>([]);
  const [selectedSourceWork, setSelectedSourceWork] = useState<SourceWorkSummary | null>(null);
  const [sourcePassages, setSourcePassages] = useState<SourcePassageResult[]>([]);
  const [sourceWorkStatus, setSourceWorkStatus] = useState("Corpus not loaded");
  const [sourcePassageStatus, setSourcePassageStatus] = useState("Open a source to view fragments");
  const [sourceStatus, setSourceStatus] = useState("Поиск по VL не запускался");
  const [shastraEvidence, setShastraEvidence] = useState<ShastraEvidencePayload | null>(null);
  const [shastraEvidenceStatus, setShastraEvidenceStatus] = useState("Evidence ещё не загружен");
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [authUsername, setAuthUsername] = useState("haridas");
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
  const privateAccessLocked = PRIVATE_APP_REQUIRE_AUTH && !currentUser;
  const aiAccessLocked = !currentUser;

  const calculatedLabel = useMemo(() => {
    if (!chart) return "Карта останется пустой до расчёта эфемеридных позиций.";
    return `${chart.grahas.length} грах рассчитано для ${chart.place.label ?? chart.place.name}.`;
  }, [chart]);
  const vimshottariPeriods = chart?.dashas?.vimshottari?.mahadashas ?? [];
  const vargaOptions = useMemo(
    () => availableVargaCodes(chart),
    [chart],
  );
  const selectedVarga = chartMode === "D1" ? null : chart?.vargas?.[chartMode] ?? null;
  const selectedVargaPlacements = selectedVarga?.placements ?? [];
  const activeChartPointCount = chartMode === "D1" ? (chart ? chart.grahas.length + (chart.ascendant ? 1 : 0) : 0) : selectedVargaPlacements.length;
  const activeChartContext = priorityVargaContexts[chartMode] ?? { scope: "Варга", detail: "дополнительный слой чтения" };
  const activeChartReferenceLabel = chartReferenceOptions.find((option) => option.key === chartReference)?.label ?? "Лагна";
  const activeChartStyleLabel = chartStyle === "south" ? "Южный стиль" : "Северный стиль";
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

  function selectVargaFocusGroup(groupKey: string, code: string) {
    setActiveVargaFocusKey(groupKey);
    setChartMode(code);
  }

  function selectVargaScheme(schemeKey: VargaSchemeKey, code: string) {
    setActiveVargaSchemeKey(schemeKey);
    setChartMode(code);
  }

  function selectVargaCode(code: string) {
    const currentGroup = vargaFocusGroups.find((group) => group.key === activeVargaFocusKey);
    const matchingGroup = currentGroup?.codes.includes(code)
      ? currentGroup
      : vargaFocusGroups.find((group) => group.key !== "core" && group.codes.includes(code))
        ?? vargaFocusGroups.find((group) => group.codes.includes(code));
    if (matchingGroup) setActiveVargaFocusKey(matchingGroup.key);
    setChartMode(code);
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
      if (requestedAnalysis && analysisTabs.some((tab) => tab.key === requestedAnalysis)) {
        setActiveAnalysisTab(requestedAnalysis as AnalysisTab);
      }
      const requestedRelationship = params.get("relationship");
      if (requestedRelationship && /^\d+$/.test(requestedRelationship)) {
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
    setShowAdvancedSettings(!window.matchMedia("(max-width: 760px)").matches);
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
          activeVargaFocusKey?: string;
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
        if (saved.activeVargaFocusKey && vargaFocusGroups.some((group) => group.key === saved.activeVargaFocusKey)) {
          setActiveVargaFocusKey(saved.activeVargaFocusKey);
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
          activeVargaFocusKey,
          activeVargaSchemeKey,
          vargaCoverageOpen,
        }),
      );
    } catch {
      // localStorage can be unavailable in restricted browser modes.
    }
  }, [
    activeVargaFocusKey,
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
      setActiveAnalysisTab("guidance");
      setCodexChatStatus(
        draftAnalysis
          ? "Вопрос из подсказки подставлен в чат"
          : "Вопрос из подсказки сохранён. Сначала сгенерируйте личный Codex-разбор.",
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
        setActiveAnalysisTab("guidance");
        setCodexChatStatus(
          draftAnalysis
            ? "Вопрос из подсказки подставлен в чат"
            : "Вопрос из подсказки сохранён. Сначала сгенерируйте личный Codex-разбор.",
        );
      }
    } catch {
      // Ignore blocked sessionStorage.
    }
    return () => window.removeEventListener("jyotish:ask-ai-context", handleAiContextRequest);
  }, [contextualizeAiQuestion, draftAnalysis]);

  useEffect(() => {
    if (!compatibilityCodexAnalysis) {
      resetCompatibilityChat();
    }
  }, [compatibilityCodexAnalysis]);

  const alternatePlaceMatches = useMemo(
    () => placeMatches.filter((place) => place.id !== selectedPlace?.id).slice(0, 4),
    [placeMatches, selectedPlace],
  );
  const chartFacts = useMemo(() => {
    if (!chart) return [];
    return [
      ["Лагна", chart.ascendant?.rashi ?? "Ожидает"],
      ["Титхи", chart.panchanga.tithi ? `${chart.panchanga.tithi.paksha} ${chart.panchanga.tithi.name}` : "Ожидает"],
      ["Вара", chart.panchanga.vara?.name ?? "Ожидает"],
      ["Йога", chart.panchanga.yoga?.name ?? "Ожидает"],
      ["Карана", chart.panchanga.karana?.name ?? "Ожидает"],
      ["UTC-смещение", chart.birth.utc_offset ?? "Ожидает"],
    ];
  }, [chart]);

  useEffect(() => {
    if (privateAccessLocked) {
      setAccuracyReport(null);
      setPlPacketReport(null);
      setWitnessSummary(null);
      setAccuracyStatus("Войдите после одобрения, чтобы загрузить JHora export report");
      setPlPacketStatus("Войдите после одобрения, чтобы загрузить Parashara Light packet");
      setWitnessSummaryStatus("Войдите после одобрения, чтобы загрузить witness summary");
      return;
    }
    if (activeAnalysisTab !== "accuracy") {
      setAccuracyStatus("JHora export report загрузится во вкладке точности");
      setPlPacketStatus("Parashara Light packet загрузится во вкладке точности");
      setWitnessSummaryStatus("Witness summary загрузится во вкладке точности");
      return;
    }
    let cancelled = false;
    setAccuracyStatus("Загружаю JHora export report...");
    setPlPacketStatus("Загружаю Parashara Light packet...");
    setWitnessSummaryStatus("Загружаю witness summary...");
    fetchWitnessSummary()
      .then((summary) => {
        if (cancelled) return;
        setWitnessSummary(summary);
        setWitnessSummaryStatus(`Witness summary: ${summary.overall_status}`);
      })
      .catch((error) => {
        if (cancelled) return;
        setWitnessSummary(null);
        setWitnessSummaryStatus(error instanceof Error ? error.message : "Witness summary API error");
      });
    fetchJHoraAccuracyReport()
      .then((report) => {
        if (cancelled) return;
        setAccuracyReport(report);
        setAccuracyStatus(report.passed ? "JHora export совпал" : "JHora export diff открыт");
      })
      .catch((error) => {
        if (cancelled) return;
        setAccuracyReport(null);
        setAccuracyStatus(error instanceof Error ? error.message : "JHora accuracy API error");
      });
    fetchParasharaLightPacketReport()
      .then((report) => {
        if (cancelled) return;
        setPlPacketReport(report);
        if (report.summary.screenshot_blank) {
          setPlPacketStatus("PL screenshot требует пересъёмки");
        } else if (report.manual_witness_comparison.status === "diff_open") {
          setPlPacketStatus("PL manual diff открыт");
        } else {
          setPlPacketStatus("PL packet загружен");
        }
      })
      .catch((error) => {
        if (cancelled) return;
        setPlPacketReport(null);
        setPlPacketStatus(error instanceof Error ? error.message : "Parashara Light packet API error");
      });
    return () => {
      cancelled = true;
    };
  }, [activeAnalysisTab, privateAccessLocked]);

  useEffect(() => {
    let cancelled = false;
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

    setPlaceSearchStatus("Ищу город и часовой пояс...");
    const searchTimeout = window.setTimeout(() => {
      searchPlaces(placeName)
        .then((items) => {
          if (cancelled) return;
          setPlaceMatches(items);
          setSelectedPlace(items[0] ?? null);
          setPlaceSearchStatus(items.length ? `${items.length} подсказок найдено` : "Подсказок нет, можно ввести координаты вручную");
        })
        .catch(() => {
          if (cancelled) return;
          setPlaceMatches([]);
          setSelectedPlace(null);
          setPlaceSearchStatus("Не удалось получить подсказки, можно ввести координаты вручную");
        });
    }, 350);

    return () => {
      cancelled = true;
      window.clearTimeout(searchTimeout);
    };
  }, [placeName, privateAccessLocked, selectedPlace]);

  useEffect(() => {
    let cancelled = false;
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
  }, [partnerPlaceName, privateAccessLocked, selectedPartnerPlace]);

  useEffect(() => {
    fetchCurrentUser()
      .then((user) => {
        setCurrentUser(user);
        setAuthStatus(user ? `Вход: ${user.username}` : "Войдите, чтобы сохранять карты");
        if (user) {
          refreshProfiles();
        }
      })
      .catch(() => setAuthStatus("Auth API недоступен"));
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
        setSourceWorkStatus(error instanceof Error ? error.message : "Source corpus API недоступен");
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
        setSourcePassageStatus(error instanceof Error ? error.message : "Source passages API недоступен");
      });

    return () => {
      cancelled = true;
    };
  }, [activeAnalysisTab, privateAccessLocked, selectedSourceWork]);

  useEffect(() => {
    if (activeAnalysisTab !== "sources") return;
    if (privateAccessLocked) {
      setShastraEvidence(null);
      setShastraEvidenceStatus("Войдите после одобрения, чтобы загрузить evidence");
      return;
    }
    let cancelled = false;
    setShastraEvidenceStatus("Загружаю shastra evidence...");
    fetchShastraEvidence()
      .then((payload) => {
        if (cancelled) return;
        setShastraEvidence(payload);
        setShastraEvidenceStatus(
          `источники: ${payload.summary.evidence_items} фрагментов; проверенных цитат ${payload.summary.approved_evidence_items}`,
        );
      })
      .catch((error) => {
        if (cancelled) return;
        setShastraEvidence(null);
        setShastraEvidenceStatus(error instanceof Error ? error.message : "Evidence API недоступен");
      });

    return () => {
      cancelled = true;
    };
  }, [activeAnalysisTab, privateAccessLocked]);

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

  function profileRelationshipFor(baseProfileId: string, relatedProfileId: number) {
    return profileRelationships.find(
      (relationship) =>
        String(relationship.profile_id) === baseProfileId &&
        relationship.related_profile_id === relatedProfileId,
    );
  }

  function resetCompatibilityResultState() {
    setCompatibilityReport(null);
    setCompatibilityPacketStatus("Codex-пакет ещё не сформирован");
    setCompatibilityCodexAnalysis(null);
    setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
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
    setCompatibilityStatus(
      `Выбрана связь: ${relationship.profile?.display_name ?? "карта A"} → ${relationship.related_profile?.display_name ?? "карта B"} (${role.label})`,
    );
    setCompatibilityPacketStatus(`Ракурс карты: ${chartReferenceOptions.find((option) => option.key === chartReferenceForRelationshipRole(role))?.label ?? "Лагна"}. Можно рассчитать совместимость или сформировать Codex-пакет.`);
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
    setBirthDate("1998-04-30");
    setBirthTime("13:45");
    setGender("male");
    setPlaceName("Стерлитамак");
    setProfileName("Моя карта 30.04.1998");
    setProfileIsSelf(true);
    setSelectedPlace(null);
    setPlaceMatches([]);
    setShowPlaceSuggestions(false);
    setPlaceSearchStatus("Пример: Стерлитамак, IANA Asia/Yekaterinburg, исторический UTC +06:00");
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
    setActiveAnalysisTab("overview");
    setStatus("Пример загружен. Нажмите «Рассчитать карту».");
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
    setStatus("Карта экспортирована в JSON");
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
    setWorkflowStatus("Считаю JHora-like workflow...");
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
        : "частично, см. API",
    );
  }

  async function refreshDualCalculation(payload: BirthChartRequest) {
    setDualCalculationStatus("Сверяю с JHora-профилем...");
    try {
      const result = await calculateDualCalculation(payload);
      setDualCalculationReport(result);
      setDualCalculationStatus(
        result.delta.exact_match
          ? "профили совпали"
          : `diff: ${result.delta.summary.max_graha_delta_arcseconds.toFixed(2)}", ${result.authority_decision.differing_settings.length} настроек`,
      );
    } catch (error) {
      setDualCalculationReport(null);
      setDualCalculationStatus(error instanceof Error ? error.message : "JHora witness API недоступен");
    }
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
      setCurrentDayStatus(`Сохранён обзор #${overviewResult.value.id}: ${overviewResult.value.sections.length} раздела`);
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
    setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
    try {
      const result = await calculateCompatibility({
        ...buildCompatibilityPayload(personA, personB),
      });
      setCompatibilityReport(result);
      setCompatibilityPacketStatus("Можно сформировать Codex-пакет по этому расчёту");
      setCompatibilityStatus("рассчитано");
    } catch (error) {
      setCompatibilityReport(null);
      setCompatibilityPacketStatus("Codex-пакет ещё не сформирован");
      setCompatibilityCodexAnalysis(null);
      setCompatibilityStatus(error instanceof Error ? error.message : "Ошибка API совместимости");
    }
  }

  async function handleCompatibilityPacket() {
    const personA = selectedProfilePayload(compatibilityPersonAProfileId) ?? lastBirthPayload ?? buildBirthPayload();
    const personB = buildPartnerPayload();
    if (!personA || !personB) return;

    setCompatibilityPacketStatus("Формирую Codex-пакет...");
    try {
      const packet = await generateCompatibilityAnalysisPacket({
        ...buildCompatibilityPayload(personA, personB),
      });
      const compatibility = packet.context.compatibility as CompatibilityReport | undefined;
      if (compatibility) {
        setCompatibilityReport(compatibility);
        setCompatibilityStatus("пакет сформирован");
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
        `Пакет: ${perspectiveCount} ракурсов, ${requestCount} запросов цитат${copied ? ", prompt скопирован" : ""}`,
      );
    } catch (error) {
      setCompatibilityPacketStatus(error instanceof Error ? error.message : "Ошибка Codex-пакета");
    }
  }

  async function handleCompatibilityCodexAnalysis() {
    if (aiAccessLocked) {
      setCompatibilityCodexStatus("Войдите или зарегистрируйтесь, чтобы сохранить AI-разбор совместимости в личной истории.");
      return;
    }
    const personA = selectedProfilePayload(compatibilityPersonAProfileId) ?? lastBirthPayload ?? buildBirthPayload();
    const personB = buildPartnerPayload();
    if (!personA || !personB) return;

    setCompatibilityCodexStatus("Запускаю Codex CLI для полного разбора двух карт...");
    try {
      const result = await generateCompatibilityCodexAnalysis({
        ...buildCompatibilityPayload(personA, personB),
      });
      if (isQueuedAnalysisGeneration(result)) {
        setCompatibilityCodexStatus(
          result.message || `Codex CLI задача #${result.job.id} поставлена в очередь. Статус появится в блоке активных генераций.`,
        );
        return;
      }
      setCompatibilityCodexAnalysis(result);
      setCompatibilityChatMessages([]);
      setCompatibilityChatStatus("Можно задавать вопросы по этому разбору совместимости");
      setCompatibilityCodexStatus(
        `Codex CLI #${result.id}: ${result.sections.length} разделов, ${generatedStatusRu(result.review_status)}`,
      );
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
    setCompatibilityChatStatus("Codex CLI отвечает по совместимости...");
    try {
      const result = await askCompatibilityCodexAnalysis(compatibilityCodexAnalysis.id, question, history);
      setCompatibilityChatMessages([...history, { role: "assistant", content: result.answer }]);
      const sourceCount = result.source_traces?.length ?? result.evidence_references?.length ?? 0;
      setCompatibilityChatStatus(sourceCount ? `Ответ готов, источников: ${sourceCount}` : "Ответ готов");
    } catch (error) {
      setCompatibilityChatMessages([...history, { role: "assistant", content: error instanceof Error ? error.message : "Ошибка Codex CLI" }]);
      setCompatibilityChatStatus(isAnalysisInProgressError(error) ? "Ответ уже формируется" : "Ошибка ответа");
    } finally {
      setCompatibilityChatBusy(false);
    }
  }

  async function handleGenerateDraftAnalysis(forceRegenerate = false) {
    if (aiAccessLocked) {
      setDraftAnalysisStatus("Войдите или зарегистрируйтесь, чтобы сохранить личный AI-разбор.");
      return;
    }
    if (!activeSavedBirthProfile) {
      setDraftAnalysisStatus("Сначала сохраните расчёт как вашу личную карту. Первый AI-разбор доступен только для сохранённой «моей карты».");
      return;
    }
    if (!activeSavedBirthProfile.is_self_profile) {
      setDraftAnalysisStatus("AI-разбор чужой сохранённой карты будет платным действием после подключения оплаты. Карту можно хранить и смотреть бесплатно.");
      return;
    }
    const basePayload = lastBirthPayload ?? buildBirthPayload();
    const payload = basePayload ? payloadWithCurrentRelatedProfiles(basePayload) : null;
    if (!payload) return;
    setDraftAnalysis(null);
    resetCodexChat();
    setDraftAnalysisStatus(
      forceRegenerate
        ? "Сбрасываю старый Codex CLI разбор и запускаю перегенерацию с текущим корпусом шастр..."
        : "Запускаю Codex CLI и сопоставление с шастрами...",
    );
    try {
      const result = await generateBirthCodexAnalysis(payload, { forceRegenerate });
      if (isQueuedAnalysisGeneration(result)) {
        setDraftAnalysisStatus(
          result.message || `Codex CLI задача #${result.job.id} поставлена в очередь. Отчёт появится в истории после обработки.`,
        );
        return;
      }
      setDraftAnalysis(result);
      setCodexChatMessages([]);
      setCodexChatStatus("Можно задавать вопросы по этому разбору");
      setDraftAnalysisStatus(
        result.billing_status === "free_personal_analysis_already_used"
          ? `Codex CLI #${result.id}: сохранённый бесплатный личный разбор, ${result.sections.length} разделов`
          : `Codex CLI #${result.id}: ${result.sections.length} разделов, ${generatedStatusRu(result.review_status)}`,
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
    setCodexChatStatus("Codex CLI отвечает...");
    try {
      const result = await askBirthCodexAnalysis(draftAnalysis.id, question, history);
      setCodexChatMessages([...history, { role: "assistant", content: result.answer }]);
      const sourceCount = result.source_traces?.length ?? result.evidence_references?.length ?? 0;
      setCodexChatStatus(sourceCount ? `Ответ готов, источников: ${sourceCount}` : "Ответ готов");
    } catch (error) {
      setCodexChatMessages([...history, { role: "assistant", content: error instanceof Error ? error.message : "Ошибка Codex CLI" }]);
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
      setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
      setWorkflowStatus("Дополнительные отчёты не запускались автоматически, чтобы не перегружать сервер");
      setDualCalculationStatus("JHora witness запускается отдельно во вкладке точности");
      setActiveAnalysisTab("overview");
      setStatus("Сохранённая карта загружена и рассчитана");
      scrollToChartAfterCalculation();
      await refreshProfiles();
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось рассчитать профиль");
    }
  }

  async function runBirthCalculation(payload: BirthChartRequest, statusMessage = "Формирую отчёт с приоритетом цитат...") {
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
      setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
      setWorkflowStatus("Дополнительные отчёты не запускались автоматически, чтобы не перегружать сервер");
      setDualCalculationStatus("JHora witness запускается отдельно во вкладке точности");
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
      setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
      setDualCalculationReport(null);
      setDualCalculationStatus("JHora witness ещё не считался");
      setLastBirthPayload(null);
      setCompatibilityStatus("Ожидает основную карту");
      setStatus(error instanceof Error ? error.message : "Ошибка API");
    }
  }

  async function submitBirthCalculation() {
    const payload = buildBirthPayload();
    if (!payload) return;
    await runBirthCalculation(payload);
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
    setSourceStatus("Ищу в VL...");
    try {
      const results = await searchVLSources(sourceQuery);
      setSourceResults(results);
      setSourceStatus(results.length ? `${results.length} результатов` : "В VL ничего не найдено");
    } catch (error) {
      setSourceResults([]);
      setSourceStatus(error instanceof Error ? error.message : "Ошибка поиска VL");
    }
  }

  async function handleResearchSearch() {
    setResearchStatus("Searching private corpus...");
    try {
      const results = await searchResearchSources(sourceQuery);
      setResearchResults(results);
      setResearchStatus(results.length ? `${results.length} research-only fragments` : "No private corpus matches");
    } catch (error) {
      setResearchResults([]);
      setResearchStatus(error instanceof Error ? error.message : "Private corpus search error");
    }
  }

  const activeSavedBirthProfile = typeof lastBirthPayload?.profile_id === "number"
    ? profiles.find((profile) => profile.id === lastBirthPayload.profile_id) ?? null
    : null;
  const aiBillingStatus = activeSavedBirthProfile
    ? activeSavedBirthProfile.is_self_profile
      ? {
          label: "Личный AI-разбор",
          text: "Эта карта отмечена как «моя карта»: первый Codex-разбор доступен бесплатно; повтор вернёт сохранённый отчёт.",
          tone: "free" as const,
        }
      : {
          label: "Чужая сохранённая карта",
          text: "Карту можно хранить и смотреть бесплатно. AI-разбор этой карты будет платным действием после подключения оплаты.",
          tone: "paid" as const,
        }
    : {
        label: currentUser ? "Карта ещё не сохранена" : "Нужен вход",
        text: currentUser
          ? "Сохраните расчёт как «моя карта», чтобы использовать первый бесплатный личный AI-разбор."
          : "Войдите или зарегистрируйтесь: первый AI-разбор доступен только для вашей сохранённой карты.",
        tone: "neutral" as const,
      };

  const activeMainNavKey: AppNavKey =
    activeAnalysisTab === "overview"
      ? chartWorkspaceTab === "vargas"
        ? "vargas"
        : "charts"
      : activeAnalysisTab === "calculations" ||
          activeAnalysisTab === "yogas" ||
          activeAnalysisTab === "timeline" ||
          activeAnalysisTab === "transits" ||
          activeAnalysisTab === "compatibility" ||
          activeAnalysisTab === "accuracy" ||
          activeAnalysisTab === "guidance" ||
          activeAnalysisTab === "sources"
        ? activeAnalysisTab
        : "charts";

  function handleMainNavSelect(key: AppNavKey) {
    if (key === "charts" || key === "settings") {
      setChartWorkspaceTab("essentials");
      setActiveAnalysisTab("overview");
      return;
    }
    if (key === "vargas") {
      setChartWorkspaceTab("vargas");
      setActiveAnalysisTab("overview");
      return;
    }
    if (
      key === "calculations" ||
      key === "yogas" ||
      key === "timeline" ||
      key === "transits" ||
      key === "guidance" ||
      key === "sources" ||
      key === "accuracy"
    ) {
      setActiveAnalysisTab(key);
    }
  }

  const initialUiReady = !browserStorageAvailable() || (formDraftHydrated && chartStyleHydrated && chartViewHydrated);

  if (!initialUiReady) {
    return (
      <main className={`app-shell shell-loading ${interfaceMode === "beginner" ? "beginner-mode" : "pro-mode"}${sidebarCollapsed ? " sidebar-collapsed" : ""}`}>
        <aside className="sidebar">
          <div className="sidebar-brand-row">
            <div className="mark">Ом</div>
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
            <h1>Jyotish Agent</h1>
            <p>Гаудия-сиддханта джйотиш</p>
          </div>
          <AppNavigation activeKey="charts" home />
        </aside>
        <section className="workspace">
          <header className="topbar">
            <div className="topbar-title">
              <strong>Карта рождения</strong>
              <span>Загружаю сохранённый рабочий стол...</span>
            </div>
          </header>
          <section className="panel initial-ui-loading" aria-live="polite">
            <strong>Открываю сохранённые данные</strong>
            <span>Сейчас подтянутся карта, настройки вида, язык терминов и последний выбранный раздел.</span>
          </section>
        </section>
      </main>
    );
  }

  return (
    <main className={`app-shell ${interfaceMode === "beginner" ? "beginner-mode" : "pro-mode"}${sidebarCollapsed ? " sidebar-collapsed" : ""}`}>
      <aside className="sidebar">
        <div className="sidebar-brand-row">
          <div className="mark">Ом</div>
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
          <h1>Jyotish Agent</h1>
          <p>Гаудия-сиддханта джйотиш</p>
        </div>
        <AppNavigation activeKey={activeMainNavKey} home onSelect={handleMainNavSelect} />
        <InterfaceModeSwitch value={interfaceMode} onChange={handleInterfaceModeChange} />
        <blockquote>
          yatha shastram
          <br />
          yatha guru
          <br />
          tatha siddhantah
        </blockquote>
        <div className="operator">
          <strong>Режим проверки</strong>
          <span>Личный режим с research-источниками</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="topbar-title">
            <strong>Карта рождения</strong>
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
                  <input type="date" value={birthDate} onChange={(event) => setBirthDate(event.target.value)} />
                </label>
                <label>
                  Время
                  <input type="time" value={birthTime} onChange={(event) => setBirthTime(event.target.value)} />
                </label>
                <label>
                  Город рождения
                  <input value={placeName} onChange={(event) => setPlaceName(event.target.value)} />
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
              <p>Зарегистрируйтесь или войдите. Сейчас аккаунт активируется сразу, чтобы астрологи могли проверить ресурс.</p>
            </div>
            <div className="auth-grid private-gate-auth">
              <label>
                Логин
                <input value={authUsername} onChange={(event) => setAuthUsername(event.target.value)} />
              </label>
              <label>
                Пароль
                <input
                  type="password"
                  value={authPassword}
                  onChange={(event) => setAuthPassword(event.target.value)}
                />
              </label>
              <div className="registration-birth-fields">
                <span>Для регистрации: дата и город рождения. Время необязательно; первый AI-разбор будет доступен для вашей карты.</span>
                <label>
                  Дата рождения
                  <input type="date" value={birthDate} onChange={(event) => setBirthDate(event.target.value)} />
                </label>
                <label>
                  Время рождения (необязательно)
                  <input type="time" value={birthTime} onChange={(event) => setBirthTime(event.target.value)} />
                </label>
                <label>
                  Город рождения
                  <input value={placeName} onChange={(event) => setPlaceName(event.target.value)} />
                </label>
              </div>
              <div className="auth-actions">
                <button type="button" className="secondary-button" onClick={() => handleAuth("login")}>Войти</button>
                <button type="button" className="secondary-button" onClick={() => handleAuth("register")}>Регистрация</button>
              </div>
            </div>
            <p className="status-line">{authStatus}</p>
          </section>
        ) : (
        <div className={`content-grid${chart ? " chart-ready" : ""}`}>
          <section className={`panel birth-panel${chart && !showBirthEditor ? " compact" : ""}`} id="chart">
            <BirthCompactStrip
              birthDate={birthDate}
              birthTime={birthTime}
              placeName={placeName}
              selectedPlace={selectedPlace}
              chart={chart}
              collapsed={Boolean(chart && !showBirthEditor)}
              onToggle={() => setShowBirthEditor((value) => !value)}
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
                  onInput={(event) => setBirthDate(event.currentTarget.value)}
                  onChange={(event) => setBirthDate(event.target.value)}
                />
              </label>
              <label>
                Время рождения
                <input
                  type="time"
                  value={birthTime}
                  onInput={(event) => setBirthTime(event.currentTarget.value)}
                  onChange={(event) => setBirthTime(event.target.value)}
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
                    <span>Каталог не нашёл точное место. Можно рассчитать вручную по IANA timezone и координатам.</span>
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
              <a className="mobile-chart-jump" href="#varga-charts">К карте и D-картам</a>
              <section className="advanced-settings-toggle" aria-labelledby="advanced-settings-title">
                <button
                  type="button"
                  className="advanced-settings-button"
                  onClick={() => setShowAdvancedSettings((value) => !value)}
                  aria-expanded={showAdvancedSettings}
                  aria-controls="calculation-settings"
                >
                  <span id="advanced-settings-title">Настройки расчёта</span>
                  <strong>{showAdvancedSettings ? "Скрыть" : "Показать"}</strong>
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
                          <option value="iana">IANA historical</option>
                        </select>
                      </label>
                      <label>
                        <GlossaryTerm termKey="shadbala">Шадбала</GlossaryTerm>
                        <select value={shadbalaProfile} onChange={(event) => setShadbalaProfile(event.target.value)}>
                          <option value="bphs_classical">BPHS classical</option>
                        </select>
                      </label>
                    </div>
                    <span className="settings-note">SSS ведётся как отдельный профиль; сейчас расчёт Drik.</span>
                  </fieldset>
                ) : null}
              </section>
              <fieldset className="calculation-settings display-settings" id="display-settings">
                <legend>Настройки отображения</legend>
                <div className="settings-grid">
                  <label>
                    Стиль карты
                    <select value={chartStyle} onChange={(event) => handleChartStyleChange(event.target.value as "north" | "south")}>
                      <option value="north">Северный: дома фиксированы</option>
                      <option value="south">Южный: знаки фиксированы</option>
                    </select>
                  </label>
                  <label>
                    Язык терминов
                    <select value={termLanguage} onChange={(event) => handleTermLanguageChange(event.target.value as TermLanguage)}>
                      <option value="sanskrit">Санскрит: Surya, Mithuna</option>
                      <option value="ru">Русский: Солнце, Близнецы</option>
                      <option value="en">English: Sun, Gemini</option>
                    </select>
                  </label>
                  <label>
                    Режим интерфейса
                    <select value={interfaceMode} onChange={(event) => handleInterfaceModeChange(event.target.value as InterfaceMode)}>
                      <option value="pro">Астролог: все рабочие панели</option>
                      <option value="beginner">Новичок: главное и объяснения</option>
                    </select>
                  </label>
                </div>
                <span className="settings-note">Влияет только на внешний вид карт, таблиц и плотность интерфейса; расчёт не меняется.</span>
              </fieldset>
              <div className="notice">
                Политика MVP: айанамша Lahiri, рамка Парашары, обязательные ссылки на источники.
              </div>
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
                  <small>Первый личный AI-разбор бесплатно доступен только для карты, отмеченной как ваша.</small>
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
                  Контекст AI:{" "}
                  {profiles
                    .filter((profile) => relatedProfileIds.includes(profile.id))
                    .map((profile) => profile.display_name)
                    .join(", ")}
                </p>
              ) : null}
              {profiles.length >= 2 ? (
                <label className="relationship-base-select">
                  Базовая карта для взаимодействий
                  <select value={relationshipBaseProfileId} onChange={(event) => setRelationshipBaseProfileId(event.target.value)}>
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
                          Блок
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
                              ? `${profile.latest_calculation.status}, ${profile.latest_calculation.graha_count} грах`
                              : "Расчёт ещё не сохранён"}
                          </small>
                          {profile.is_self_profile ? (
                            <small className="profile-ai-note">
                              <GlossaryTerm termKey="free_personal_ai">первый AI-разбор для этой карты</GlossaryTerm>
                            </small>
                          ) : (
                            <small className="profile-ai-note">карту можно хранить бесплатно; AI-разбор чужой карты будет отдельным действием</small>
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
                            <div className="profile-role-focus" aria-label="Фокус роли для AI-разбора">
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
                            onChange={() => toggleRelatedProfile(profile.id)}
                          />
                          <GlossaryTerm termKey="ai_context">Контекст AI</GlossaryTerm>
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
                  <h2>{chartMode === "D1" ? "Карта раши" : `${chartMode} ${selectedVarga?.name ?? "варга"}`}</h2>
                  <span>Отсчёт {activeChartReferenceLabel} · {activeChartContext.scope}: {activeChartContext.detail}</span>
                  <div className="chart-mode-summary" aria-label="Текущий вид карты">
                    <span>{chartMode} · {activeChartPointCount || "нет"} точек</span>
                    <span>{activeChartStyleLabel}</span>
                    <span>{activeTermLanguageLabel}</span>
                    <a href="#display-settings">Изменить вид</a>
                  </div>
                </div>
                <div className="chart-heading-tools">
                  <div className="chart-action-strip" aria-label="Действия с текущей картой">
                    <div className="chart-action-group primary">
                      <a
                        href="/?analysis=calculations#reports"
                        onClick={(event) => {
                          event.preventDefault();
                          setActiveAnalysisTab("calculations");
                          window.history.pushState(null, "", "/?analysis=calculations#reports");
                          document.getElementById("reports")?.scrollIntoView({ block: "start" });
                        }}
                      >
                        Таблица расчётов
                      </a>
                      <a href="#varga-charts" onClick={() => setChartWorkspaceTab("vargas")}>Атлас D-карт</a>
                      <a
                        href="/?analysis=guidance#reports"
                        onClick={(event) => {
                          event.preventDefault();
                          setActiveAnalysisTab("guidance");
                          window.history.pushState(null, "", "/?analysis=guidance#reports");
                          document.getElementById("reports")?.scrollIntoView({ block: "start" });
                        }}
                      >
                        AI-разбор
                      </a>
                      <a href="/reports">История</a>
                    </div>
                    <div className="chart-action-group file">
                      <button type="button" onClick={handleSaveProfile} disabled={!chart}>Сохранить</button>
                      <button type="button" onClick={handleExportCurrentChart} disabled={!chart}>Экспорт</button>
                      <button type="button" onClick={() => window.print()} disabled={!chart}>Печать</button>
                    </div>
                  </div>
                </div>
              </div>
              <ReadingFlowStrip
                chart={chart}
                chartMode={chartMode}
                workspaceTab={chartWorkspaceTab}
                activeAnalysisTab={activeAnalysisTab}
                onOpenEssentials={() => setChartWorkspaceTab("essentials")}
                onOpenVargas={() => setChartWorkspaceTab("vargas")}
                onOpenCalculations={() => setActiveAnalysisTab("calculations")}
                onOpenGuidance={() => setActiveAnalysisTab("guidance")}
              />
              <div className="chart-reference-row">
                <strong>Отсчёт домов</strong>
                <ChartReferenceToggle chart={chart} value={chartReference} onChange={setChartReference} />
                <ChartDisplayControls
                  chart={chart}
                  chartMode={chartMode}
                  chartStyle={chartStyle}
                  vargaOptions={vargaOptions}
                  onChartModeChange={selectVargaCode}
                  onChartStyleChange={handleChartStyleChange}
                />
                <label className="chart-house-hints-toggle">
                  <input
                    type="checkbox"
                    checked={houseHintsEnabled}
                    onChange={(event) => setHouseHintsEnabled(event.target.checked)}
                  />
                  <span>Подсказки в карте</span>
                </label>
              </div>
              {interfaceMode === "beginner" ? (
                <div className="beginner-guide-strip">
                  <strong>Сначала смотри: лагна, Луна, Солнце, 7 дом, 12 дом и таблицу расчётов.</strong>
                  <span>Подчёркнутые термины раскрывают короткое объяснение на телефоне и на компьютере.</span>
                </div>
              ) : null}
              <div className="chart-layout">
                <div className="chart-visual-stack">
                  <ChartPreview chart={chart} varga={selectedVarga} chartStyle={chartStyle} chartReference={chartReference} termLanguage={termLanguage} houseHintsEnabled={houseHintsEnabled} />
                  {!chart ? <StartChartNotice /> : null}
                  <ChartNotationLegend termLanguage={termLanguage} />
                  <FirstReadCalculationPanel
                    chart={chart}
                    termLanguage={termLanguage}
                    onOpenCalculations={() => setActiveAnalysisTab("calculations")}
                  />
                </div>
                <div className="chart-data-stack">
                  <CoreInfoStrip chart={chart} termLanguage={termLanguage} />
                  <ChartSideCalculationTable chart={chart} termLanguage={termLanguage} />
                  <AiAccessPolicyPanel />
                  <AiRelatedContextPanel relationships={profileRelationships} />
                  <MvpReadinessPanel />
                  {interfaceMode === "beginner" ? <BeginnerGuidedCourse /> : null}
                  {interfaceMode === "beginner" ? <BeginnerAskAiPanel /> : null}
                  {interfaceMode === "beginner" ? <BeginnerNextSteps /> : null}
                  {interfaceMode === "beginner" ? <BeginnerLearningPanel /> : null}
                  {interfaceMode === "beginner" ? <BeginnerCalculationGuide /> : null}
                  <KeyVargaComparisonPanel
                    chart={chart}
                    activeCode={chartMode}
                    chartStyle={chartStyle}
                    chartReference={chartReference}
                    termLanguage={termLanguage}
                    onSelect={selectVargaCode}
                  />
                  <PlanetStrengthDigest chart={chart} />
                  {interfaceMode === "pro" ? (
                    <AstrologerWorkflowPanel
                      chart={chart}
                      activeTab={activeAnalysisTab}
                      onSelect={setActiveAnalysisTab}
                    />
                  ) : null}
                  {chartFacts.length ? (
                    <div className="fact-grid">
                      {chartFacts.map(([label, value]) => (
                        <div className="fact-item" key={label}>
                          <span>{label}</span>
                          <strong>{value}</strong>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
              <PractitionerVargaRail
                chart={chart}
                activeCode={chartMode}
                chartStyle={chartStyle}
                chartReference={chartReference}
                onSelect={selectVargaCode}
              />
              <ShodashaMiniAtlas
                chart={chart}
                activeCode={chartMode}
                chartStyle={chartStyle}
                chartReference={chartReference}
                onSelect={selectVargaCode}
              />
              <PrimaryVargaTabs
                chart={chart}
                activeCode={chartMode}
                activeGroupKey={activeVargaFocusKey}
                workspaceTab={chartWorkspaceTab}
                onSelect={selectVargaCode}
                onFocusGroupSelect={selectVargaFocusGroup}
                onWorkspaceTabChange={setChartWorkspaceTab}
                onCoverageSelect={openVargaCoverageDetails}
              />
              <VargaCoverageSummary
                chart={chart}
                open={vargaCoverageOpen}
                onOpenChange={setVargaCoverageOpen}
                detailsRef={vargaCoverageRef}
                onOpenAtlas={() => setChartWorkspaceTab("vargas")}
              />
              <JaiminiPendingStrip onOpenAtlas={() => setChartWorkspaceTab("vargas")} />
              <div className="chart-workspace-body">
                {chartWorkspaceTab === "essentials" ? (
                  <EssentialChartPairBoard
                    chart={chart}
                    activeCode={chartMode}
                    chartStyle={chartStyle}
                    chartReference={chartReference}
                    onSelect={selectVargaCode}
                    onOpenAtlas={() => setChartWorkspaceTab("vargas")}
                  />
                ) : null}
                {chartWorkspaceTab === "references" ? (
                  <>
                    <ReferenceChartBoard
                      chart={chart}
                      chartStyle={chartStyle}
                      activeReference={chartReference}
                      onSelect={setChartReference}
                    />
                    <BhavaOverviewBoard chart={chart} termLanguage={termLanguage} />
                  </>
                ) : null}
                {chartWorkspaceTab === "vargas" ? (
                  <>
                    <VargaTaskMatrix
                      chart={chart}
                      activeGroupKey={activeVargaFocusKey}
                      onSelect={selectVargaFocusGroup}
                    />
                    <VargaSchemeMatrix
                      chart={chart}
                      activeSchemeKey={activeVargaSchemeKey}
                      onSelect={selectVargaScheme}
                    />
                    <VargaStudyBoard
                      chart={chart}
                      activeGroupKey={activeVargaFocusKey}
                      activeCode={chartMode}
                      chartStyle={chartStyle}
                      chartReference={chartReference}
                      onSelect={selectVargaCode}
                    />
                    <VargaAtlasBoard
                      chart={chart}
                      activeCode={chartMode}
                      chartStyle={chartStyle}
                      chartReference={chartReference}
                      onSelect={selectVargaCode}
                    />
                  </>
                ) : null}
              </div>
              <p className="calculation-result">{calculatedLabel}</p>
            </section>

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
                        setActiveAnalysisTab(tab.key);
                        window.history.pushState(null, "", `/?analysis=${tab.key}#reports`);
                      }}
                      role="tab"
                      aria-selected={activeAnalysisTab === tab.key}
                    >
                      <strong>{tab.label}</strong>
                      <span>{tab.hint}</span>
                    </button>
                  ))}
                </div>
                <label className="analysis-more-tabs">
                  <span>Ещё</span>
                  <select
                    value={secondaryAnalysisTabs.some((tab) => tab.key === activeAnalysisTab) ? activeAnalysisTab : ""}
                    onChange={(event) => {
                      if (event.target.value) {
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
                <a className="analysis-page-link" href="/compatibility">
                  <strong>Совместимость</strong>
                  <span>отдельная страница</span>
                </a>
              </div>
              <div className="analysis-panel-slot">
                {activeAnalysisTab === "overview" ? <PersonSummaryPanel summary={personSummary} /> : null}
                {activeAnalysisTab === "calculations" ? (
                  <div className="analysis-tab-stack">
                    <DetailedCalculationsPanel
                      summary={personSummary}
                      chart={chart}
                      activeCode={chartMode}
                      chartStyle={chartStyle}
                      chartReference={chartReference}
                      termLanguage={termLanguage}
                      onSelectVarga={selectVargaCode}
                    />
                    <DualCalculationPanel report={dualCalculationReport} status={dualCalculationStatus} />
                  </div>
                ) : null}
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
                      <h2>Цитаты и статус источников</h2>
                      <button type="button" className="secondary-button">Все источники</button>
                    </div>
                    <form className="source-search" onSubmit={handleSourceSearch}>
                      <input value={sourceQuery} onChange={(event) => setSourceQuery(event.target.value)} />
                      <button type="submit" className="secondary-button">Искать в VL</button>
                      <button type="button" className="secondary-button" onClick={handleResearchSearch}>Private corpus</button>
                      <span>{sourceStatus}</span>
                      <span>{researchStatus}</span>
                    </form>
                    <div className="source-corpus-summary">
                      <strong>Личный корпус шастр</strong>
                      <span>{sourceWorkStatus}</span>
                      {sourceInventory ? (
                        <small>
                          research-only: {sourceInventory.summary.research_only_works} книг / {sourceInventory.summary.research_only_passages} фрагментов
                        </small>
                      ) : null}
                    </div>
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
                            <span>
                              {work.language_code} / {work.review_status} / {work.passage_count ?? 0} фрагм.
                            </span>
                          </button>
                        ))}
                      </div>
                    ) : null}
                    {selectedSourceWork ? (
                      <div className="source-results research-results">
                        <div>
                          <strong>{selectedSourceWork.title}</strong>
                          <span>{selectedSourceWork.author || selectedSourceWork.edition || selectedSourceWork.slug}</span>
                          <small>{sourcePassageStatus}</small>
                        </div>
                        {sourcePassages.map((passage) => (
                          <div key={passage.id}>
                            <strong>{passage.reference}</strong>
                            <span>{passage.language_code} / {passage.review_status}</span>
                            <p>{passage.body}</p>
                            <small>{passage.public_quote_policy || passage.rights_status}</small>
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
                            <span>{result.work_title} / {result.review_status}</span>
                            <p>{result.body}</p>
                            <small>{result.public_quote_policy}</small>
                          </div>
                        ))}
                      </div>
                    ) : null}
                    <ShastraEvidenceReviewPanel evidence={shastraEvidence} status={shastraEvidenceStatus} />
                    <ShastraAuditPanel audit={chart?.shastra_audit} />
                    <div className="source-table">
                      {sourceRows.map(([component, source, citation, state]) => (
                        <div className="source-row" key={component}>
                          <strong>{component}</strong>
                          <span>{source}</span>
                          <span>{citation}</span>
                          <em className={state}>{stateLabels[state] ?? state}</em>
                        </div>
                      ))}
                    </div>
                  </section>
                ) : null}
              </div>
            </section>
          </section>
        </div>
        )}
      </section>
    </main>
  );
}
