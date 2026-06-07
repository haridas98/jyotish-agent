"use client";

import { FormEvent, useEffect, useMemo, useRef, useState, type Dispatch, type ReactNode, type SetStateAction } from "react";
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
  generateBirthDeepseekAnalysis,
  generateBirthNemotronAnalysis,
  generateBirthQwenAnalysis,
  generateBirthReport,
  generateCompatibilityAnalysisPacket,
  generateCompatibilityCodexAnalysis,
  listChartProfiles,
  loginUser,
  logoutUser,
  registerUser,
  searchPlaces,
  searchResearchSources,
  searchVLSources,
  type BirthReport,
  type BirthChart,
  type BirthChartRequest,
  type ChartProfile,
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
  type User,
  type VargaPlacement,
  type WitnessSummary,
  type WorkflowInterpretationPlan,
  type VLSearchResult,
} from "@/lib/api";
import {
  firstSymbolLineY,
  northIndianHouseCells,
  safeSymbolCenterY,
} from "@/lib/northIndianChartGeometry";

const PRIVATE_APP_REQUIRE_AUTH = process.env.NEXT_PUBLIC_PRIVATE_APP_REQUIRE_AUTH === "true";

const sourceRows = [
  ["Айанамша", "Lahiri", "Рабочий профиль; JHora diff подключён", "ready"],
  ["Система карты", "Drik Siddhanta / Swiss-JPL", "Профиль JHora-сравнения подключён", "ready"],
  ["Корпус VL", "База Шрилы Прабхупады", "Поиск подключён", "ready"],
];

const analysisTabs = [
  { key: "overview", label: "Обзор", hint: "контекст" },
  { key: "compatibility", label: "Совместимость", hint: "две карты" },
  { key: "calculations", label: "Расчёт", hint: "D1, D9" },
  { key: "yogas", label: "Силы", hint: "бала, йоги" },
  { key: "timeline", label: "Даши", hint: "периоды" },
  { key: "transits", label: "Транзиты", hint: "гочара" },
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

type ChartPlacement = {
  body: string;
  rashi: string;
  rashiIndex: number | null;
  isLagna: boolean;
  longitude: number | null;
  nakshatra: string | null;
  pada: number | null;
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

function isLagnaBody(body: string) {
  return body === "Lagna" || body === "Ascendant";
}

function activeChartPlacements(chart: BirthChart | null, varga: ActiveVargaChart | null): ChartPlacement[] {
  if (!chart) return [];

  if (varga) {
    return varga.placements.map((placement) => ({
      body: placement.body,
      rashi: placement.rashi,
      rashiIndex: normalizeRashiIndex(placement.rashi_index) ?? rashiIndexFromName(placement.rashi),
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
    });
  }
  placements.push(
    ...chart.grahas.map((graha) => ({
      body: graha.body,
      rashi: graha.rashi,
      rashiIndex: normalizeRashiIndex(graha.rashi_index) ?? rashiIndexFromName(graha.rashi),
      isLagna: false,
      longitude: graha.longitude,
      nakshatra: graha.nakshatra,
      pada: graha.pada,
    })),
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

function northIndianHouseItems(chart: BirthChart | null, varga: ActiveVargaChart | null): NorthIndianHouseItem[] {
  if (!chart) return [];
  const placements = activeChartPlacements(chart, varga);
  const bySign = placementsBySign(placements);
  const lagnaIndex = lagnaRashiIndex(chart, placements) ?? 0;
  const rows = !varga && chart.houses.length
    ? chart.houses
    : Array.from({ length: 12 }, (_, index) => ({
        house: index + 1,
        rashi_index: (lagnaIndex + index) % 12,
        rashi: rashiNames[(lagnaIndex + index) % 12],
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
}: {
  chart: BirthChart | null;
  varga: ActiveVargaChart | null;
}) {
  return <NorthIndianChartPreview chart={chart} varga={varga} />;
}

function NorthIndianChartPreview({ chart, varga }: { chart: BirthChart | null; varga: ActiveVargaChart | null }) {
  const houses = northIndianHouseItems(chart, varga);
  return (
    <div className="chart-box" aria-label="Предпросмотр карты раши">
      <svg viewBox="0 0 400 400" role="img" aria-label="Североиндийская сетка карты">
        <rect x="1.5" y="1.5" width="397" height="397" fill="white" stroke="#b88a2f" strokeWidth="1.5" />
        <path d="M2 2 L398 398 M398 2 L2 398" stroke="#c99a43" strokeWidth="1" />
        <path d="M200 2 L398 200 L200 398 L2 200 Z" fill="none" stroke="#c99a43" strokeWidth="1" />
        {houses.map((house) => {
          const cell = northIndianHouseCells[house.house];
          const signLabel = rashiChartLabel(house.rashiIndex, house.rashi);
          const textLines = northIndianCellLines(house);
          const lineGap = textLines.length > 5 ? 11 : 13;
          const centerY = safeSymbolCenterY(cell.centerY, textLines.length, lineGap);
          const firstLineY = firstSymbolLineY(centerY, textLines.length, lineGap);
          return (
            <g className="chart-house-group" key={house.house}>
              <title>{`Знак ${signLabel}: ${house.placements.map(fullPlacementTitle).join("; ") || "пусто"}`}</title>
              <text
                className={`chart-cell-text${textLines.length > 5 ? " dense" : ""}`}
                x={cell.centerX}
                y={firstLineY}
                textAnchor="middle"
              >
                {textLines.map((line, index) => (
                  <tspan
                    className={index === 0 ? "chart-rashi-label" : "chart-graha-detail"}
                    key={`${house.house}-${line}-${index}`}
                    x={cell.centerX}
                    dy={index === 0 ? 0 : lineGap}
                  >
                    {line}
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
    </div>
  );
}

function northIndianCellLines(house: NorthIndianHouseItem) {
  return [
    `${house.house} ${rashiChartLabel(house.rashiIndex, house.rashi)}`,
    ...house.placements.map(compactPlacementLine),
  ];
}

function compactPlacementLine(placement: ChartPlacement) {
  const label = placement.isLagna ? "As" : northGrahaLabel(placement.body);
  if (placement.longitude === null) return label;
  return `${label} ${formatSignDegrees(placement.longitude)}`;
}

function fullPlacementTitle(placement: ChartPlacement) {
  const label = placement.isLagna ? "Lagna" : labelRu(placement.body);
  if (placement.longitude === null) return label;
  const nakshatra = placement.nakshatra ? `, ${placement.nakshatra} ${placement.pada ?? ""}` : "";
  return `${label}: ${formatSignDegrees(placement.longitude)}${nakshatra}`;
}

function rashiChartLabel(index: number | null, fallback: string) {
  return index === null ? fallback || "-" : rashiChartLabels[index] ?? fallback;
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

const vargaSnapshotCodes = ["D1", "D9", "D10", "D30", "D3", "D60"];

function VargaSnapshotGrid({ chart }: { chart: BirthChart | null }) {
  const items = vargaSnapshotCodes.map((code) => {
    if (code === "D1") {
      return {
        code,
        name: "Раши",
        placements: chart?.grahas.map((graha) => ({ body: graha.body, rashi: graha.rashi })) ?? [],
      };
    }
    const varga = chart?.vargas?.[code];
    return {
      code,
      name: varga?.name ?? "Варга",
      placements: varga?.placements ?? [],
    };
  });

  return (
    <div className="varga-snapshot-grid" aria-label="Быстрый обзор варг">
      {items.map((item) => (
        <div className="varga-snapshot-card" key={item.code}>
          <div className="varga-snapshot-head">
            <strong>{item.code}</strong>
            <span>{item.name}</span>
          </div>
          <div className="varga-snapshot-body">
            {item.placements.slice(0, 7).map((placement) => (
              <span key={`${item.code}-${placement.body}`}>
                {shortGraha(placement.body)} {placement.rashi}
              </span>
            ))}
            {!item.placements.length ? <em>ожидает</em> : null}
          </div>
        </div>
      ))}
    </div>
  );
}

function shortGraha(body: string) {
  return grahaSymbol(body);
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

function isoDateOffset(days: number) {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function GrahaTable({ grahas }: { grahas: GrahaPosition[] }) {
  if (grahas.length === 0) {
    return (
      <div className="readiness-panel">
        <strong>Грахи ещё не рассчитаны</strong>
        <p>Карта заполнится после ответа бэкенда с эфемеридными позициями.</p>
      </div>
    );
  }

  return (
    <div className="planet-table">
      <div className="table-row table-head">
        <span>Граха</span>
        <span>Долгота</span>
        <span>Раши</span>
        <span>Накшатра</span>
        <span>D9</span>
      </div>
      {grahas.map((graha) => (
        <div className="table-row" key={graha.body}>
          <strong>{labelRu(graha.body)}</strong>
          <span>{formatDegrees(graha.longitude)}</span>
          <span>{graha.rashi}</span>
          <span>
            {graha.nakshatra} {graha.pada}
          </span>
          <span>{graha.navamsa}</span>
        </div>
      ))}
    </div>
  );
}

function VargaTable({ placements, code }: { placements: VargaPlacement[]; code: string }) {
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
        <span>Точка</span>
        <span>Раши {code}</span>
      </div>
      {placements.map((placement) => (
        <div className="table-row" key={placement.body}>
          <strong>{labelRu(placement.body)}</strong>
          <span>{placement.rashi}</span>
        </div>
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

function DetailedCalculationsPanel({ summary }: { summary: PersonSummary | null }) {
  const detailedPositions = summary?.detailed_positions ?? [];
  const houses = summary?.houses ?? [];

  return (
    <section className="panel calculation-detail-panel">
      <div className="panel-heading">
        <h2>Расчёты карты</h2>
        <span>D1, D9, накшатры, дома</span>
      </div>
      <div className="summary-content">
        {!summary ? <div className="pending-strip">Подробные расчёты появятся после построения карты.</div> : null}
        {detailedPositions.length ? (
          <div className="detailed-positions">
            <div>
              <h3>Подробные положения</h3>
              <span>D1, D9, накшатра, достоинство</span>
            </div>
            <div className="detailed-table">
              <div className="detailed-row detailed-head">
                <span>Граха</span>
                <span>Карака</span>
                <span>Градусы</span>
                <span>Раши</span>
                <span>D9</span>
                <span>Накшатра</span>
                <span>Дом</span>
                <span>Упр.</span>
                <span>Сила</span>
              </div>
              {detailedPositions.map((row) => (
                <div className="detailed-row" key={row.body}>
                  <strong>
                    {labelRu(row.body)}
                    {row.retrograde ? " R" : ""}
                  </strong>
                  <span>{row.chara_karaka ?? "-"}</span>
                  <span>{row.sign_degrees_dms}</span>
                  <span>{row.rashi}</span>
                  <span>{row.navamsa}</span>
                  <span>
                    {row.nakshatra} {row.pada ?? ""}
                  </span>
                  <span>{row.house ?? "-"}</span>
                  <span>{row.ruled_houses.length ? row.ruled_houses.join(", ") : "-"}</span>
                  <span>{row.dignity}</span>
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
                  <span>Дом {house.house}</span>
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
  qwenAnalysis,
  deepseekAnalysis,
  nemotronAnalysis,
  draftStatus,
  qwenStatus,
  deepseekStatus,
  nemotronStatus,
  onGenerateDraft,
  onRegenerateDraft,
  onGenerateQwen,
  onGenerateDeepseek,
  onGenerateNemotron,
  draftDisabled,
  qwenDisabled,
  deepseekDisabled,
  nemotronDisabled,
  chatMessages,
  chatStatus,
  onAskDraftQuestion,
  chatDisabled,
}: {
  birthReport: BirthReport["report"] | null;
  draftAnalysis: GeneratedDraftAnalysis | null;
  qwenAnalysis: GeneratedDraftAnalysis | null;
  deepseekAnalysis: GeneratedDraftAnalysis | null;
  nemotronAnalysis: GeneratedDraftAnalysis | null;
  draftStatus: string;
  qwenStatus: string;
  deepseekStatus: string;
  nemotronStatus: string;
  onGenerateDraft: () => void;
  onRegenerateDraft: () => void;
  onGenerateQwen: () => void;
  onGenerateDeepseek: () => void;
  onGenerateNemotron: () => void;
  draftDisabled: boolean;
  qwenDisabled: boolean;
  deepseekDisabled: boolean;
  nemotronDisabled: boolean;
  chatMessages: CodexAnalysisChatMessage[];
  chatStatus: string;
  onAskDraftQuestion: (question: string) => void;
  chatDisabled: boolean;
}) {
  const traceCount = draftAnalysis?.sections.reduce((total, section) => total + (section.source_traces?.length ?? 0), 0) ?? 0;
  const [chatQuestion, setChatQuestion] = useState("");

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
          </div>
          <div className="draft-generation-strip qwen-generation-strip">
            <div>
              <strong>Альтернативный разбор QWEN</strong>
              <span>{qwenStatus}</span>
            </div>
            <div className="draft-generation-actions">
              <button type="button" className="secondary-button" onClick={onGenerateQwen} disabled={qwenDisabled}>
                Сгенерировать с помощью QWEN
              </button>
            </div>
          </div>
          <div className="draft-generation-strip deepseek-generation-strip">
            <div>
              <strong>Альтернативный обзор DeepSeek</strong>
              <span>{deepseekStatus}</span>
            </div>
            <div className="draft-generation-actions">
              <button type="button" className="secondary-button" onClick={onGenerateDeepseek} disabled={deepseekDisabled}>
                Сгенерировать с помощью DeepSeek
              </button>
            </div>
          </div>
          <div className="draft-generation-strip nemotron-generation-strip">
            <div>
              <strong>Альтернативный обзор Nemotron</strong>
              <span>{nemotronStatus}</span>
            </div>
            <div className="draft-generation-actions">
              <button type="button" className="secondary-button" onClick={onGenerateNemotron} disabled={nemotronDisabled}>
                Сгенерировать с помощью Nemotron
              </button>
            </div>
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
          {qwenAnalysis ? (
            <GeneratedAnalysisDetails analysis={qwenAnalysis} assistantLabel="QWEN" />
          ) : null}
          {deepseekAnalysis ? (
            <GeneratedAnalysisDetails analysis={deepseekAnalysis} assistantLabel="DeepSeek" />
          ) : null}
          {nemotronAnalysis ? (
            <GeneratedAnalysisDetails analysis={nemotronAnalysis} assistantLabel="Nemotron" />
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

  const statusItems = [
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
              <span>{label}</span>
              <strong>{statusRu(status)}</strong>
            </div>
          ))}
        </div>
        <div className="classical-columns">
          <div className="classical-list">
            <h3>Авастхи</h3>
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
            <h3>Аргала</h3>
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
            <h3>Аштакаварга</h3>
            <div>
              <span>SAV total</span>
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
            <h3>Вимшопака</h3>
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
            <h3>Шадбала</h3>
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

function TransitPanel({ report, status }: { report: TransitReport | null; status: string }) {
  const rows = report?.transits.slice(0, 9) ?? [];
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2>Транзиты</h2>
        <span>{status}</span>
      </div>
      <WorkflowPlanStrip plan={report?.interpretation_plan} />
      {rows.length ? (
        <div className="workflow-table">
          <div className="workflow-row workflow-head">
            <span>Граха</span>
            <span>Раши</span>
            <span>От лагны</span>
            <span>От Луны</span>
          </div>
          {rows.map((row) => (
            <div className="workflow-row" key={row.body}>
              <strong>{labelRu(row.body)}</strong>
              <span>{row.rashi}</span>
              <span>{row.house_from_lagna ?? "-"}</span>
              <span>{row.house_from_moon ?? "-"}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="pending-strip">Транзиты появятся после расчёта карты.</div>
      )}
    </section>
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

function CompatibilityPanel({
  report,
  status,
  profiles,
  selectedPersonAProfileId,
  selectedPersonBProfileId,
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
  chatMessages,
  chatStatus,
  onAskCodexQuestion,
  chatDisabled,
}: CompatibilityPanelProps) {
  const rows = report?.kuta_rows ?? [];
  const perspectives = report?.analysis?.perspectives ?? [];
  const summaries = report?.analysis?.chart_summaries;
  const scoreLabel = report ? `${report.score.total}/${report.score.max}` : "-";
  const percentLabel = report ? `${report.score.percent.toFixed(1)}%` : "-";
  const levelLabel = report ? compatibilityLevelLabelsRu[report.assessment.level] ?? report.assessment.level : "ожидает";
  const [chatQuestion, setChatQuestion] = useState("");

  function handleChatSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const question = chatQuestion.trim();
    if (!question) return;
    onAskCodexQuestion(question);
    setChatQuestion("");
  }

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
        </div>
        <button className="secondary-button compatibility-button primary-compare-button" type="submit" disabled={disabled}>
          Сравнить выбранные карты
        </button>
        <div className="compatibility-form-grid">
          <label>
            Дата второго человека
            <input type="date" value={partnerBirthDate} onChange={(event) => setPartnerBirthDate(event.target.value)} />
          </label>
          <label>
            Время второго человека
            <input type="time" value={partnerBirthTime} onChange={(event) => setPartnerBirthTime(event.target.value)} />
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
        <div className="compatibility-full-analysis">
          <div className="panel-heading">
            <h3>Полный разбор двух карт</h3>
            <span>#{codexAnalysis.id} · {generatedStatusRu(codexAnalysis.review_status)}</span>
          </div>
          <div className="codex-analysis-chat">
            <div className="chat-heading">
              <strong>Вопросы к Codex CLI по совместимости</strong>
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
                placeholder="Спросить про перспективы брака, риски, даши, духовную совместимость..."
                disabled={chatDisabled}
              />
              <button type="submit" className="secondary-button" disabled={chatDisabled || !chatQuestion.trim()}>
                Спросить
              </button>
            </form>
          </div>
          {codexAnalysis.sections.map((section, index) => (
            <article key={`${section.title}-${index}`} className="generated-section">
              <h3>{section.title}</h3>
              <p>{section.body}</p>
              {section.key_points?.length ? (
                <ul>
                  {section.key_points.slice(0, 4).map((point) => (
                    <li key={point}>{point}</li>
                  ))}
                </ul>
              ) : null}
              {section.practical_steps?.length ? (
                <div className="generated-actions">
                  <strong>Что делать</strong>
                  {section.practical_steps.slice(0, 4).map((step) => (
                    <span key={step}>{step}</span>
                  ))}
                </div>
              ) : null}
              {section.source_traces?.length ? (
                <div className="source-trace-list">
                  {section.source_traces.slice(0, 3).map((trace, traceIndex) => (
                    <small key={`${trace.condition_key}-${traceIndex}`}>
                      {trace.condition_key} · {trace.work_title} · {trace.reference} · {trace.source_status}
                    </small>
                  ))}
                </div>
              ) : null}
            </article>
          ))}
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
              <span>Шадбала</span>
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
              <h3>Шадбала</h3>
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
  const [sealCommandCopyStatus, setSealCommandCopyStatus] = useState("");

  async function copySealCommand() {
    if (!witnessReview?.seal_command) return;
    if (!navigator.clipboard?.writeText) {
      setSealCommandCopyStatus("clipboard unavailable");
      return;
    }
    try {
      await navigator.clipboard.writeText(witnessReview.seal_command);
      setSealCommandCopyStatus("copied");
    } catch {
      setSealCommandCopyStatus("copy failed");
    }
  }

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
                <span>JHora / PL</span>
                <strong>
                  {witnessReview.jhora.status ?? "missing"} / {witnessReview.parashara_light.status ?? "missing"}
                </strong>
                <small>
                  {witnessReview.jhora.id ?? "JHora missing"} · {witnessReview.parashara_light.id ?? "PL missing"}
                </small>
              </div>
              {witnessReview.seal_command ? (
                <div className="seal-command-row">
                  <span>
                    Seal command
                    <button type="button" className="seal-copy-button" onClick={copySealCommand}>
                      Copy
                    </button>
                  </span>
                  <strong>{witnessReview.seal_command}</strong>
                  {sealCommandCopyStatus ? <small>{sealCommandCopyStatus}</small> : null}
                </div>
              ) : null}
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
              {witnessReviewBatchWritten.slice(0, 3).map((row) => (
                <div key={row.id}>
                  <span>{row.id}</span>
                  <strong>
                    {row.reviewable ? "reviewable" : "not reviewable"} / ACK {row.ack_required ? "yes" : "no"}
                  </strong>
                  <small>{row.output_path}</small>
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
                  <strong>{row.suggested_actions.slice(0, 3).join(", ") || row.status || "review"}</strong>
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
              {witnessCaptureQueueNext ? (
                <div>
                  <span>{witnessCaptureQueueNext.next_step_label || "Next step"}</span>
                  <strong>
                    {witnessCaptureQueueNext.next_action_key || witnessCaptureQueueNext.status || "review"}
                  </strong>
                  <small>
                    {witnessCaptureQueueNext.next_command ||
                      witnessCaptureQueueNext.manual_review_command ||
                      "manual capture/review"}
                  </small>
                </div>
              ) : null}
              {witnessCaptureQueueItems.slice(0, 3).map((row) => (
                <div key={`capture-${row.id}`}>
                  <span>
                    {row.priority}. {row.label || row.id}
                  </span>
                  <strong>{row.suggested_actions.slice(0, 3).join(", ") || row.status || "review"}</strong>
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
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<AnalysisTab>("overview");
  const [birthReport, setBirthReport] = useState<BirthReport["report"] | null>(null);
  const [draftAnalysis, setDraftAnalysis] = useState<GeneratedDraftAnalysis | null>(null);
  const [draftAnalysisStatus, setDraftAnalysisStatus] = useState("Личный разбор ещё не генерировался");
  const [qwenAnalysis, setQwenAnalysis] = useState<GeneratedDraftAnalysis | null>(null);
  const [qwenAnalysisStatus, setQwenAnalysisStatus] = useState("QWEN разбор ещё не генерировался");
  const [deepseekAnalysis, setDeepseekAnalysis] = useState<GeneratedDraftAnalysis | null>(null);
  const [deepseekAnalysisStatus, setDeepseekAnalysisStatus] = useState("DeepSeek обзор ещё не генерировался");
  const [nemotronAnalysis, setNemotronAnalysis] = useState<GeneratedDraftAnalysis | null>(null);
  const [nemotronAnalysisStatus, setNemotronAnalysisStatus] = useState("Nemotron обзор ещё не генерировался");
  const [codexChatMessages, setCodexChatMessages] = useState<CodexAnalysisChatMessage[]>([]);
  const [codexChatStatus, setCodexChatStatus] = useState("Сначала сгенерируйте личный разбор");
  const [codexChatBusy, setCodexChatBusy] = useState(false);
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
  const [authUsername, setAuthUsername] = useState("haridas");
  const [authPassword, setAuthPassword] = useState("");
  const [authStatus, setAuthStatus] = useState("Войдите, чтобы сохранять карты");
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [profileStatus, setProfileStatus] = useState("Сохранённые карты не загружены");
  const autoCalculationStartedRef = useRef(false);
  const privateAccessLocked = PRIVATE_APP_REQUIRE_AUTH && !currentUser;

  const calculatedLabel = useMemo(() => {
    if (!chart) return "Карта останется пустой до расчёта эфемеридных позиций.";
    return `${chart.grahas.length} грах рассчитано для ${chart.place.label ?? chart.place.name}.`;
  }, [chart]);
  const vimshottariPeriods = chart?.dashas?.vimshottari?.mahadashas ?? [];
  const vargaOptions = useMemo(
    () => ["D1", ...Object.keys(chart?.vargas ?? {}).filter((code) => code !== "D1")],
    [chart],
  );
  const selectedVarga = chartMode === "D1" ? null : chart?.vargas?.[chartMode] ?? null;
  const selectedVargaPlacements = selectedVarga?.placements ?? [];
  const personSummary = birthReport?.person_summary ?? null;

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
    if (!draftAnalysis) {
      resetCodexChat();
    }
  }, [draftAnalysis]);

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
  }, [privateAccessLocked]);

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
    if (privateAccessLocked || autoCalculationStartedRef.current || chart || lastBirthPayload || !selectedPlace) {
      return;
    }
    const payload = buildBirthPayload();
    if (!payload) return;
    autoCalculationStartedRef.current = true;
    void runBirthCalculation(payload, "Формирую стартовую карту...");
  }, [privateAccessLocked, selectedPlace, chart, lastBirthPayload]);

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

  async function refreshProfiles() {
    try {
      const items = await listChartProfiles();
      setProfiles(items);
      setProfileStatus(items.length ? `${items.length} сохранённых карт` : "Сохранённых карт пока нет");
    } catch (error) {
      setProfiles([]);
      setProfileStatus(error instanceof Error ? error.message : "Не удалось загрузить профили");
    }
  }

  async function handleAuth(mode: "login" | "register") {
    setAuthStatus(mode === "login" ? "Вхожу..." : "Создаю пользователя...");
    try {
      const user =
        mode === "login"
          ? await loginUser(authUsername, authPassword)
          : await registerUser(authUsername, authPassword);
      if (!user.is_active) {
        setCurrentUser(null);
        setProfiles([]);
        setAuthStatus("Регистрация отправлена. Доступ появится после одобрения администратора.");
        setProfileStatus("После одобрения можно будет сохранять карты");
        return;
      }
      setCurrentUser(user);
      setAuthStatus(`Вход: ${user.username}`);
      await refreshProfiles();
    } catch (error) {
      setCurrentUser(null);
      setProfiles([]);
      setAuthStatus(error instanceof Error ? error.message : "Ошибка авторизации");
    }
  }

  async function handleLogout() {
    await logoutUser();
    setCurrentUser(null);
    setProfiles([]);
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
      });
      await refreshProfiles();
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось сохранить карту");
    }
  }

  function handleSelectCompatibilityPersonAProfile(profileId: string) {
    setCompatibilityPersonAProfileId(profileId);
    setCompatibilityReport(null);
    setCompatibilityPacketStatus("Codex-пакет ещё не сформирован");
    setCompatibilityCodexAnalysis(null);
    setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
    setCompatibilityStatus(profileId ? "Карта A взята из сохранённых" : "Карта A: текущий расчёт");
  }

  function handleSelectCompatibilityPersonBProfile(profileId: string) {
    setCompatibilityPersonBProfileId(profileId);
    setCompatibilityReport(null);
    setCompatibilityPacketStatus("Codex-пакет ещё не сформирован");
    setCompatibilityCodexAnalysis(null);
    setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
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
      });
      await refreshProfiles();
      setCompatibilityPersonBProfileId(String(saved.id));
      setCompatibilityStatus(`Карта B сохранена: ${saved.display_name}`);
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось сохранить карту партнёра");
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
        person_a: personA,
        person_b: personB,
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
        person_a: personA,
        person_b: personB,
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
    const personA = selectedProfilePayload(compatibilityPersonAProfileId) ?? lastBirthPayload ?? buildBirthPayload();
    const personB = buildPartnerPayload();
    if (!personA || !personB) return;

    setCompatibilityCodexStatus("Запускаю Codex CLI для полного разбора двух карт...");
    try {
      const result = await generateCompatibilityCodexAnalysis({
        person_a: personA,
        person_b: personB,
      });
      setCompatibilityCodexAnalysis(result);
      setCompatibilityChatMessages([]);
      setCompatibilityChatStatus("Можно задавать вопросы по этому разбору совместимости");
      setCompatibilityCodexStatus(
        `Codex CLI #${result.id}: ${result.sections.length} разделов, ${generatedStatusRu(result.review_status)}`,
      );
    } catch (error) {
      setCompatibilityCodexAnalysis(null);
      resetCompatibilityChat();
      setCompatibilityCodexStatus(error instanceof Error ? error.message : "Ошибка полного разбора совместимости");
    }
  }

  async function handleAskCompatibilityQuestion(question: string) {
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
      setCompatibilityChatStatus("Ошибка ответа");
    } finally {
      setCompatibilityChatBusy(false);
    }
  }

  async function handleGenerateDraftAnalysis(forceRegenerate = false) {
    const payload = lastBirthPayload ?? buildBirthPayload();
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
      setDraftAnalysis(result);
      setCodexChatMessages([]);
      setCodexChatStatus("Можно задавать вопросы по этому разбору");
      setDraftAnalysisStatus(
        `Codex CLI #${result.id}: ${result.sections.length} разделов, ${generatedStatusRu(result.review_status)}`,
      );
    } catch (error) {
      setDraftAnalysis(null);
      resetCodexChat();
      setDraftAnalysisStatus(error instanceof Error ? error.message : "Ошибка генерации разбора");
    }
  }

  async function handleGenerateQwenAnalysis() {
    const payload = lastBirthPayload ?? buildBirthPayload();
    if (!payload) return;
    setQwenAnalysis(null);
    setQwenAnalysisStatus("Запускаю QWEN через локальный FreeQwenApi...");
    try {
      const result = await generateBirthQwenAnalysis(payload);
      setQwenAnalysis(result);
      setQwenAnalysisStatus(
        `QWEN #${result.id}: ${result.sections.length} разделов, ${generatedStatusRu(result.review_status)}`,
      );
    } catch (error) {
      setQwenAnalysis(null);
      setQwenAnalysisStatus(error instanceof Error ? error.message : "Ошибка генерации QWEN-разбора");
    }
  }

  async function handleGenerateDeepseekAnalysis() {
    const payload = lastBirthPayload ?? buildBirthPayload();
    if (!payload) return;
    setDeepseekAnalysis(null);
    setDeepseekAnalysisStatus("Запускаю DeepSeek через локальный FreeDeepseekAPI...");
    try {
      const result = await generateBirthDeepseekAnalysis(payload);
      setDeepseekAnalysis(result);
      setDeepseekAnalysisStatus(
        `DeepSeek #${result.id}: ${result.sections.length} разделов, ${generatedStatusRu(result.review_status)}`,
      );
    } catch (error) {
      setDeepseekAnalysis(null);
      setDeepseekAnalysisStatus(error instanceof Error ? error.message : "Ошибка генерации DeepSeek-обзора");
    }
  }

  async function handleGenerateNemotronAnalysis() {
    const payload = lastBirthPayload ?? buildBirthPayload();
    if (!payload) return;
    setNemotronAnalysis(null);
    setNemotronAnalysisStatus("Запускаю Nemotron через OpenRouter...");
    try {
      const result = await generateBirthNemotronAnalysis(payload);
      setNemotronAnalysis(result);
      setNemotronAnalysisStatus(
        `Nemotron #${result.id}: ${result.sections.length} разделов, ${generatedStatusRu(result.review_status)}`,
      );
    } catch (error) {
      setNemotronAnalysis(null);
      setNemotronAnalysisStatus(error instanceof Error ? error.message : "Ошибка генерации Nemotron-обзора");
    }
  }

  async function handleAskDraftQuestion(question: string) {
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
      setCodexChatStatus("Ошибка ответа");
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
      setDraftAnalysis(null);
      setDraftAnalysisStatus("Личный разбор ещё не генерировался");
      setQwenAnalysis(null);
      setQwenAnalysisStatus("QWEN разбор ещё не генерировался");
      setDeepseekAnalysis(null);
      setDeepseekAnalysisStatus("DeepSeek обзор ещё не генерировался");
      setNemotronAnalysis(null);
      setNemotronAnalysisStatus("Nemotron обзор ещё не генерировался");
      setLastBirthPayload(payload);
      setCompatibilityReport(null);
      setCompatibilityStatus("Можно считать совместимость");
      setCompatibilityCodexAnalysis(null);
      setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
      await Promise.all([refreshWorkflowReports(payload), refreshDualCalculation(payload)]);
      setActiveAnalysisTab("overview");
      setStatus("Сохранённая карта загружена и рассчитана");
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
      setBirthReport(result.report);
      setDraftAnalysis(null);
      setDraftAnalysisStatus("Личный разбор ещё не генерировался");
      setQwenAnalysis(null);
      setQwenAnalysisStatus("QWEN разбор ещё не генерировался");
      setDeepseekAnalysis(null);
      setDeepseekAnalysisStatus("DeepSeek обзор ещё не генерировался");
      setNemotronAnalysis(null);
      setNemotronAnalysisStatus("Nemotron обзор ещё не генерировался");
      setLastBirthPayload(payload);
      setCompatibilityReport(null);
      setCompatibilityStatus("Можно считать совместимость");
      setCompatibilityCodexAnalysis(null);
      setCompatibilityCodexStatus("Полный разбор совместимости ещё не запускался");
      await Promise.all([refreshWorkflowReports(payload), refreshDualCalculation(payload)]);
      setStatus("Отчёт построен");
    } catch (error) {
      setChart(null);
      setBirthReport(null);
      setDraftAnalysis(null);
      setDraftAnalysisStatus("Личный разбор ещё не генерировался");
      setQwenAnalysis(null);
      setQwenAnalysisStatus("QWEN разбор ещё не генерировался");
      setDeepseekAnalysis(null);
      setDeepseekAnalysisStatus("DeepSeek обзор ещё не генерировался");
      setNemotronAnalysis(null);
      setNemotronAnalysisStatus("Nemotron обзор ещё не генерировался");
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

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = buildBirthPayload();
    if (!payload) return;
    await runBirthCalculation(payload);
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

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="mark">Ом</div>
        <div>
          <h1>Jyotish Agent</h1>
          <p>Гаудия-сиддханта джйотиш</p>
        </div>
        <nav aria-label="Основная навигация">
          <a className="active" href="#chart">Карты</a>
          <a
            href="#reports"
            onClick={(event) => {
              event.preventDefault();
              setActiveAnalysisTab("compatibility");
              document.getElementById("reports")?.scrollIntoView({ block: "start" });
            }}
          >
            Совместимость
          </a>
          <a href="#reports" onClick={() => setActiveAnalysisTab("guidance")}>Отчёт</a>
          <a href="#reports" onClick={() => setActiveAnalysisTab("sources")}>Источники</a>
          <a href="#reports" onClick={() => setActiveAnalysisTab("accuracy")}>Точность</a>
        </nav>
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
          <div className="mantra">Hare Krishna Hare Krishna Krishna Krishna Hare Hare</div>
          <div className="top-actions">
            <button type="button">Источники</button>
            <button
              type="button"
              onClick={() => document.getElementById("calculation-settings")?.scrollIntoView({ behavior: "smooth" })}
            >
              Настройки
            </button>
          </div>
        </header>

        {privateAccessLocked ? (
          <section className="panel private-gate" aria-live="polite">
            <div>
              <h2>Закрытый доступ</h2>
              <p>Зарегистрируйтесь или войдите. Новые аккаунты начинают работать только после одобрения администратора.</p>
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
              <div className="auth-actions">
                <button type="button" className="secondary-button" onClick={() => handleAuth("login")}>Войти</button>
                <button type="button" className="secondary-button" onClick={() => handleAuth("register")}>Регистрация</button>
              </div>
            </div>
            <p className="status-line">{authStatus}</p>
          </section>
        ) : (
        <div className="content-grid">
          <section className="panel birth-panel" id="chart">
            <div className="panel-heading">
              <h2>Данные рождения</h2>
              <button type="button" className="secondary-button">Пример</button>
            </div>
            <form onSubmit={handleSubmit} className="birth-form">
              <label>
                Дата рождения
                <input type="date" value={birthDate} onChange={(event) => setBirthDate(event.target.value)} />
              </label>
              <label>
                Время рождения
                <input type="time" value={birthTime} onChange={(event) => setBirthTime(event.target.value)} />
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
              <fieldset className="calculation-settings" id="calculation-settings">
                <legend>Настройки расчёта</legend>
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
                    Шадбала
                    <select value={shadbalaProfile} onChange={(event) => setShadbalaProfile(event.target.value)}>
                      <option value="bphs_classical">BPHS classical</option>
                    </select>
                  </label>
                </div>
                <span className="settings-note">SSS ведётся как отдельный профиль; сейчас расчёт Drik.</span>
              </fieldset>
              <div className="notice">
                Политика MVP: айанамша Lahiri, рамка Парашары, обязательные ссылки на источники.
              </div>
              <button className="primary-button" type="submit">Рассчитать карту</button>
              <p className="status-line">{status}</p>
            </form>
            <div className="account-block">
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
                <div className="auth-grid">
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
                  <div className="auth-actions">
                    <button type="button" className="secondary-button" onClick={() => handleAuth("login")}>Войти</button>
                    <button type="button" className="secondary-button" onClick={() => handleAuth("register")}>Регистрация</button>
                  </div>
                </div>
              )}
              <label>
                Название карты
                <input value={profileName} onChange={(event) => setProfileName(event.target.value)} />
              </label>
              <button type="button" className="secondary-button save-profile-button" onClick={handleSaveProfile}>
                Сохранить профиль рождения
              </button>
            </div>
            <div className="profile-block">
              <div className="block-heading">
                <h3>Сохранённые карты</h3>
                <div className="profile-heading-actions">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => setActiveAnalysisTab("compatibility")}
                  >
                    Совместимость
                  </button>
                  <button type="button" className="secondary-button" onClick={refreshProfiles}>Обновить</button>
                </div>
              </div>
              <p>{profileStatus}</p>
              {profiles.length ? (
                <div className="profile-list">
                  {profiles.map((profile) => (
                    <div className="profile-row" key={profile.id}>
                      <div>
                        <strong>{profile.display_name}</strong>
                        <span>{profile.birth_date} · {profile.place.label}</span>
                        <small>
                          {profile.latest_calculation
                            ? `${profile.latest_calculation.status}, ${profile.latest_calculation.graha_count} грах`
                            : "Расчёт ещё не сохранён"}
                        </small>
                      </div>
                      <button type="button" className="secondary-button" onClick={() => handleCalculateProfile(profile)}>
                        Загрузить
                      </button>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          </section>

          <section className="main-stack">
            <section className="panel chart-panel">
              <div className="panel-heading">
                <h2>{chartMode === "D1" ? "Карта раши" : `${chartMode} ${selectedVarga?.name ?? "варга"}`}</h2>
                <div className="chart-controls">
                  <label className="compact-control">
                    <span>Карта</span>
                    <select
                      value={chartMode}
                      onChange={(event) => setChartMode(event.target.value)}
                    >
                      {vargaOptions.map((code) => (
                        <option value={code} key={code}>
                          {code === "D1" ? "D1 Раши" : `${code} ${chart?.vargas?.[code]?.name ?? ""}`}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              </div>
              <div className="chart-layout">
                <ChartPreview chart={chart} varga={selectedVarga} />
                <div className="chart-data-stack">
                  {chartMode === "D1" ? (
                    <GrahaTable grahas={chart?.grahas ?? []} />
                  ) : (
                    <VargaTable placements={selectedVargaPlacements} code={chartMode} />
                  )}
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
              <p className="calculation-result">{calculatedLabel}</p>
              <VargaSnapshotGrid chart={chart} />
            </section>

            <section className="analysis-workspace" id="reports">
              <div className="analysis-tabs" role="tablist" aria-label="Разделы анализа">
                {analysisTabs.map((tab) => (
                  <button
                    type="button"
                    key={tab.key}
                    className={activeAnalysisTab === tab.key ? "active" : ""}
                    onClick={() => setActiveAnalysisTab(tab.key)}
                    role="tab"
                    aria-selected={activeAnalysisTab === tab.key}
                  >
                    <strong>{tab.label}</strong>
                    <span>{tab.hint}</span>
                  </button>
                ))}
              </div>
              <div className="analysis-panel-slot">
                {activeAnalysisTab === "overview" ? <PersonSummaryPanel summary={personSummary} /> : null}
                {activeAnalysisTab === "calculations" ? (
                  <div className="analysis-tab-stack">
                    <DualCalculationPanel report={dualCalculationReport} status={dualCalculationStatus} />
                    <DetailedCalculationsPanel summary={personSummary} />
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
                    qwenAnalysis={qwenAnalysis}
                    deepseekAnalysis={deepseekAnalysis}
                    nemotronAnalysis={nemotronAnalysis}
                    draftStatus={draftAnalysisStatus}
                    qwenStatus={qwenAnalysisStatus}
                    deepseekStatus={deepseekAnalysisStatus}
                    nemotronStatus={nemotronAnalysisStatus}
                    onGenerateDraft={() => handleGenerateDraftAnalysis(false)}
                    onRegenerateDraft={() => handleGenerateDraftAnalysis(true)}
                    onGenerateQwen={handleGenerateQwenAnalysis}
                    onGenerateDeepseek={handleGenerateDeepseekAnalysis}
                    onGenerateNemotron={handleGenerateNemotronAnalysis}
                    draftDisabled={!birthReport}
                    qwenDisabled={!birthReport}
                    deepseekDisabled={!birthReport}
                    nemotronDisabled={!birthReport}
                    chatMessages={codexChatMessages}
                    chatStatus={codexChatStatus}
                    onAskDraftQuestion={handleAskDraftQuestion}
                    chatDisabled={!draftAnalysis || codexChatBusy}
                  />
                ) : null}
                {activeAnalysisTab === "transits" ? <TransitPanel report={transitReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "tithiPravesha" ? (
                  <TithiPraveshaPanel report={tithiPraveshaReport} status={workflowStatus} />
                ) : null}
                {activeAnalysisTab === "tajaka" ? <TajakaPanel report={tajakaReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "prashna" ? <PrashnaPanel report={prashnaReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "mundane" ? <MundanePanel report={mundaneReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "muhurta" ? <MuhurtaPanel report={muhurtaReport} status={workflowStatus} /> : null}
                {activeAnalysisTab === "compatibility" ? (
                  <CompatibilityPanel
                    report={compatibilityReport}
                    status={compatibilityStatus}
                    partnerBirthDate={partnerBirthDate}
                    setPartnerBirthDate={setPartnerBirthDate}
                    partnerBirthTime={partnerBirthTime}
                    setPartnerBirthTime={setPartnerBirthTime}
                    partnerPlaceName={partnerPlaceName}
                    setPartnerPlaceName={setPartnerPlaceName}
                    partnerPlaceMatches={partnerPlaceMatches}
                    selectedPartnerPlace={selectedPartnerPlace}
                    showPartnerPlaceSuggestions={showPartnerPlaceSuggestions}
                    setShowPartnerPlaceSuggestions={setShowPartnerPlaceSuggestions}
                    partnerPlaceSearchStatus={partnerPlaceSearchStatus}
                    onSelectPartnerPlace={selectPartnerPlace}
                    onSelectPersonAProfile={handleSelectCompatibilityPersonAProfile}
                    onSelectPersonBProfile={handleSelectCompatibilityPersonBProfile}
                    onSavePartnerProfile={handleSavePartnerProfile}
                    onSubmit={handleCompatibilitySubmit}
                    onGeneratePacket={handleCompatibilityPacket}
                    onGenerateCodexAnalysis={handleCompatibilityCodexAnalysis}
                    disabled={!chart && !compatibilityPersonAProfileId}
                    savePartnerDisabled={!currentUser || !selectedPartnerPlace}
                    packetDisabled={!chart && !compatibilityPersonAProfileId}
                    packetStatus={compatibilityPacketStatus}
                    codexDisabled={!chart && !compatibilityPersonAProfileId}
                    codexStatus={compatibilityCodexStatus}
                    codexAnalysis={compatibilityCodexAnalysis}
                    chatMessages={compatibilityChatMessages}
                    chatStatus={compatibilityChatStatus}
                    onAskCodexQuestion={handleAskCompatibilityQuestion}
                    chatDisabled={!compatibilityCodexAnalysis || compatibilityChatBusy}
                    profiles={profiles}
                    selectedPersonAProfileId={compatibilityPersonAProfileId}
                    selectedPersonBProfileId={compatibilityPersonBProfileId}
                    partnerProfileName={partnerProfileName}
                    setPartnerProfileName={setPartnerProfileName}
                  />
                ) : null}
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
