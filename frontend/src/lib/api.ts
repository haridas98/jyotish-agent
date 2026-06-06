export type ZodiacPlacement = {
  longitude: number;
  rashi: {
    index: number;
    name: string;
  };
  nakshatra: {
    index: number;
    name: string;
    pada: number;
  };
  navamsa: {
    index: number;
    name: string;
  };
};

export type EphemerisStatus = {
  provider: string;
  available: boolean;
  detail: string;
};

export type CalculationSettingsRequest = {
  zodiac?: string;
  calculation_model?: string;
  ayanamsa?: string;
  node_type?: string;
  ephemeris?: string;
  house_system?: string;
  bhava_system?: string;
  varga_scheme?: string;
  sunrise_source?: string;
  timezone_source?: string;
  shadbala_profile?: string;
};

export type BirthChartRequest = CalculationSettingsRequest & {
  birth_date: string;
  birth_time: string;
  gender?: "male" | "female" | "unknown";
  place_name: string;
  place_id?: string;
  country_code?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
};

export type TransitRequest = BirthChartRequest & {
  as_of_date: string;
  as_of_time?: string;
};

export type MuhurtaRequest = CalculationSettingsRequest & {
  place_name: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
  start_date: string;
  end_date: string;
  time?: string;
  purpose?: string;
  task_type?: string;
};

export type CompatibilityRequest = {
  person_a: BirthChartRequest;
  person_b: BirthChartRequest;
};

export type TithiPraveshaRequest = BirthChartRequest & {
  target_year: number;
  search_days?: number;
  return_place_name?: string;
  return_timezone?: string;
  return_latitude?: number;
  return_longitude?: number;
};

export type PrashnaRequest = CalculationSettingsRequest & {
  question?: string;
  question_date: string;
  question_time: string;
  place_name: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
};

export type MundaneRequest = CalculationSettingsRequest & {
  event_type?: string;
  description?: string;
  event_date: string;
  event_time: string;
  place_name: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
};

export type CompactPlacement = {
  rashi: string | null;
  rashi_index?: number | null;
  nakshatra: string | null;
  nakshatra_index?: number | null;
  pada: number | null;
};

export type GrahaPosition = {
  body: string;
  longitude: number;
  latitude: number | null;
  speed_longitude: number | null;
  ephemeris_engine?: string | null;
  ephemeris_flags?: number | null;
  rashi: string;
  rashi_index?: number;
  nakshatra: string;
  nakshatra_index?: number;
  pada: number;
  navamsa: string;
  navamsa_index?: number;
};

export type HousePlacement = {
  house: number;
  rashi_index: number;
  rashi: string;
};

export type VargaPlacement = {
  body: string;
  rashi_index: number;
  rashi: string;
};

export type VargaChart = {
  code: string;
  name: string;
  method: string;
  placements: VargaPlacement[];
};

export type Panchanga = {
  tithi?: {
    number: number;
    name: string;
    paksha: string;
  };
  vara?: {
    name: string;
  };
  nakshatra?: {
    name: string;
    pada?: number;
  };
  yoga?: {
    number: number;
    name: string;
  };
  karana?: {
    name: string;
  };
};

export type DashaPeriod = {
  name?: string;
  lord: string;
  level: number;
  starts_at: string;
  ends_at: string;
  duration_years: number;
  sequence_index: number;
  parent_lord?: string;
};

export type ClassicalStatus = {
  status: string;
  method?: string;
};

export type BaladiAvastha = {
  body: string;
  state: string;
  strength: number;
  degree_band: string;
};

export type YogaSignature = {
  key: string;
  name: string;
  bodies: string[];
  status: string;
  category?: string;
  rarity?: string;
  present?: boolean;
  detection_status?: string;
  source_priority?: string[];
  reference?: string;
  formula?: {
    description: string;
    status: string;
    source_basis: string;
  };
};

export type YogaSummary = {
  catalog_total: number;
  detected_count: number;
  signature_checked_count: number;
  checked_not_present_count: number;
  formula_pending_count: number;
  calculation_pending_count?: number;
  citation_required_count: number;
};

export type ArgalaRow = {
  house: number;
  bodies: string[];
};

export type SpecialPoint = {
  key: string;
  name: string;
  longitude: number;
  rashi: string;
  rashi_index: number;
  nakshatra: string;
  pada: number;
  local_time?: string;
  period?: string;
  segment?: number;
  starts_at?: string;
  ends_at?: string;
  midpoint?: string;
  calculation_note?: string;
  metadata?: Record<string, unknown>;
};

export type VimshopakaRow = {
  body: string;
  primary_scheme: string;
  score: number;
  percentage: number;
  scheme_scores: Record<string, number>;
  scheme_percentages: Record<string, number>;
  varga_scores: Record<
    string,
    {
      rashi: string;
      weight: number;
      dignity: string;
      factor: number;
      score: number;
    }
  >;
  supportive_vargas: string[];
  support_count: number;
  missing_vargas: string[];
};

export type AshtakavargaBody = {
  scores: number[];
  total: number;
};

export type ShadbalaRow = {
  body: string;
  components: {
    naisargika: number;
    uccha: number;
    sthana?: number;
    dig: number;
    chesta?: number;
    kala?: number;
    drik?: number;
  };
  subcomponents?: {
    sthana?: Record<string, unknown>;
    dig?: Record<string, unknown>;
    chesta?: Record<string, unknown>;
    kala?: Record<string, unknown>;
    drik?: Record<string, unknown>;
  };
  known_total: number;
};

export type DayPeriod = {
  key: string;
  name: string;
  period: string;
  segment: number;
  starts_at: string;
  ends_at: string;
  midpoint: string;
  local_time: string;
  status: string;
};

export type WorkflowInterpretationPlan = {
  kind: string;
  source_anchors: string[];
  required_factors: string[];
  client_text_sequence: string[];
  gaudiya_guard: string;
  citation_rule: string;
};

export type SolarDay = {
  date: string;
  timezone: string;
  sunrise: string;
  sunset: string;
  next_sunrise: string;
  daylight_minutes: number;
  night_minutes: number;
  status: string;
  method: string;
  day_periods: DayPeriod[];
};

export type ClassicalCalculations = {
  avasthas?: ClassicalStatus & {
    baladi: BaladiAvastha[];
  };
  vimshopaka_bala?: ClassicalStatus & {
    items: VimshopakaRow[];
  };
  ashtakavarga?: ClassicalStatus & {
    missing_sources: string[];
    bhinna: Record<string, AshtakavargaBody>;
    sarva: AshtakavargaBody;
  };
  shadbala?: ClassicalStatus & {
    items: ShadbalaRow[];
  };
  yogas?: ClassicalStatus & {
    items: YogaSignature[];
    coverage?: YogaSignature[];
    summary?: YogaSummary;
  };
  argala?: ClassicalStatus & {
    reference: string;
    primary: ArgalaRow[];
    obstruction: ArgalaRow[];
  };
  special_points?: ClassicalStatus & {
    arabic_lots: SpecialPoint[];
    upagrahas: ClassicalStatus & {
      items: SpecialPoint[];
    };
    vedic_points: ClassicalStatus & {
      items: SpecialPoint[];
    };
  };
  transits?: ClassicalStatus;
  compatibility?: ClassicalStatus;
  muhurta?: ClassicalStatus;
};

export type ShastraAuditItem = {
  key: string;
  label: string;
  source_priority: string[];
  source_basis: string;
  authority_status: string;
  implementation_status: string;
  review_status: string;
  public_claim: string;
  can_generate_client_interpretation: boolean;
  blocker?: string;
};

export type ShastraAudit = {
  policy: string;
  authority_order: string[];
  bphs_policy: string;
  summary: {
    total: number;
    source_backed: number;
    client_interpretation_allowed: number;
    partial_or_audit: number;
    needs_text_rule_review: number;
  };
  items: ShastraAuditItem[];
  items_by_key: Record<string, ShastraAuditItem>;
};

export type BirthChart = {
  calculation_version: string;
  settings?: {
    zodiac: string;
    calculation_model: string;
    ayanamsa: string;
    node_type: string;
    ephemeris: string;
    house_system: string;
    bhava_system: string;
    varga_scheme: string;
    sunrise_source: string;
    timezone_source: string;
    shadbala_profile: string;
  };
  birth: {
    date: string;
    time: string;
    timezone: string;
    utc_offset?: string;
    local_datetime: string;
    utc_datetime: string;
  };
  place: {
    id?: string;
    name: string;
    label?: string;
    country_code?: string;
    latitude: number;
    longitude: number;
  };
  solar_day?: SolarDay;
  grahas: GrahaPosition[];
  ascendant: GrahaPosition | null;
  houses: HousePlacement[];
  vargas?: Record<string, VargaChart>;
  panchanga: Panchanga;
  classical?: ClassicalCalculations;
  shastra_audit?: ShastraAudit;
  dashas?: {
    vimshottari?: {
      system: string;
      level: string;
      year_length_days: number;
      mahadashas: DashaPeriod[];
    };
    extra?: {
      status: string;
      yogini?: {
        system: string;
        status: string;
        level: string;
        cycle_years: number;
        year_length_days: number;
        start_rule: string;
        mahadashas: DashaPeriod[];
      };
      ashtottari?: {
        system: string;
        status: string;
        cycle_years: number;
        sequence: { lord: string; years: number }[];
        audit: Record<string, unknown>;
      };
    };
  };
};

export type DualCalculationReport = {
  status: string;
  profile_status: string;
  primary_calculation: {
    key: string;
    calculation_version: string;
    settings: NonNullable<BirthChart["settings"]>;
    birth: BirthChart["birth"];
    place: BirthChart["place"];
    chart: BirthChart;
  };
  jhora_profile_calculation: {
    key: string;
    calculation_version: string;
    settings: NonNullable<BirthChart["settings"]>;
    birth: BirthChart["birth"];
    place: BirthChart["place"];
    chart: BirthChart;
  };
  settings_diff: Array<{
    key: string;
    primary: string | null;
    jhora_profile: string | null;
    matches: boolean;
  }>;
  delta: {
    exact_match: boolean;
    summary: {
      graha_count: number;
      max_graha_delta_arcseconds: number;
      varga_mismatches: number;
      dasha_mismatches: number;
      shadbala_mismatches: number;
      panchanga_mismatches: number;
    };
    lagna: null | {
      body: string;
      primary_longitude: number;
      jhora_profile_longitude: number;
      signed_delta_arcseconds: number;
      delta_arcseconds: number;
      primary_rashi: string;
      jhora_profile_rashi: string;
      rashi_matches: boolean;
      primary_nakshatra: string;
      jhora_profile_nakshatra: string;
      nakshatra_matches: boolean;
      primary_pada: number;
      jhora_profile_pada: number;
      pada_matches: boolean;
    };
    grahas: Array<{
      body: string;
      primary_longitude: number;
      jhora_profile_longitude: number;
      signed_delta_arcseconds: number;
      delta_arcseconds: number;
      primary_rashi: string;
      jhora_profile_rashi: string;
      rashi_matches: boolean;
      primary_nakshatra: string;
      jhora_profile_nakshatra: string;
      nakshatra_matches: boolean;
      primary_pada: number;
      jhora_profile_pada: number;
      pada_matches: boolean;
    }>;
    vargas: {
      mismatch_count: number;
      rows: Array<{
        code: string;
        checked: number;
        mismatches: number;
        missing: number;
        samples: Array<{
          body: string;
          primary: string | null;
          jhora_profile: string | null;
        }>;
      }>;
    };
    dashas: {
      mismatch_count: number;
      rows: Array<{
        index: number;
        status?: string;
        primary_lord?: string | null;
        jhora_profile_lord?: string | null;
        primary_starts_at?: string | null;
        jhora_profile_starts_at?: string | null;
        primary_ends_at?: string | null;
        jhora_profile_ends_at?: string | null;
        matches?: boolean;
      }>;
    };
    shadbala: {
      mismatch_count: number;
      rows: Array<{
        body: string;
        primary?: number;
        jhora_profile?: number;
        delta?: number;
        status?: string;
      }>;
    };
    panchanga: {
      mismatch_count: number;
      rows: Array<{
        key: string;
        primary: string | null;
        jhora_profile: string | null;
        matches: boolean;
      }>;
    };
  };
  authority_decision: {
    accepted_track: string;
    status: string;
    needs_review: boolean;
    reason: string;
    differing_settings: string[];
  };
};

export type JHoraAccuracyReport = {
  fixture_id: string;
  passed: boolean;
  generated_at: string;
  source_report: string;
  source_export: string;
  summary: {
    longitude: {
      checked: number;
      failed: number;
      max_delta_arcseconds: number;
      median_delta_arcseconds: number;
      ayanamsa_delta_arcseconds: number;
      corrected_max_delta_arcseconds: number;
      failed_samples: Array<{
        body: string;
        delta_arcseconds: number;
        signed_delta_arcseconds: number;
      }>;
    };
    exact_groups: Array<{
      key: string;
      total: number;
      passed: number;
      failed: number;
      failed_samples: string[];
    }>;
    jhora_layers: Record<string, Record<string, number | string | null>>;
    missing_fields: string[];
  };
  diagnostics: Record<string, unknown>;
};

export type ParasharaLightPacketReport = {
  schema_version: string;
  id: string;
  status: string;
  source_packet: string;
  checklist_count: number;
  manual_witness_source: string;
  manual_witness_comparison: {
    status: string;
    summary: {
      manual_values_count: number;
      checked_count: number;
      passed_count: number;
      failed_count: number;
      missing_count: number;
    };
    completion: {
      fillable_fields_count: number;
      filled_fields_count: number;
      empty_fields_count: number;
      completion_percent: number;
      completed_rows_count: number;
      empty_field_sample: string[];
    };
    diffs: Array<{
      source: string;
      body: string;
      field: string;
      witness: string | number | boolean | null;
      calculated: string | number | boolean | null;
      delta_arcseconds?: number;
      tolerance_arcseconds?: number;
      passed: boolean;
      missing?: boolean;
    }>;
  };
  summary: {
    review_status: string;
    capture_status: string;
    version_required: string;
    window_title: string;
    control_count: number | null;
    screenshot_blank: boolean | null;
    screenshot_error: string | null;
    screenshots_count: number;
    fingerprints: {
      ui_state?: {
        path?: string;
        bytes?: number;
        sha256?: string;
        missing?: boolean;
      };
      screenshots?: Array<{
        path?: string;
        bytes?: number;
        sha256?: string;
        missing?: boolean;
      }>;
    };
    jyotish_agent_lagna: string;
    manual_values_count: number;
    manual_failed_count: number;
    manual_filled_fields_count: number;
    manual_empty_fields_count: number;
    manual_completion_percent: number;
  };
};

export type WitnessSummary = {
  overall_status: string;
  jhora: {
    available: boolean;
    status: string;
    fixture_id: string;
    source_report: string;
    failed_checks: number;
    missing_fields_count: number;
    max_delta_arcseconds?: number;
    corrected_max_delta_arcseconds?: number;
    layers?: Record<string, Record<string, number | string | null>>;
  };
  parashara_light: {
    available: boolean;
    status: string;
    id: string;
    source_packet: string;
    manual_witness_source?: string;
    manual_values_count: number;
    manual_failed_count: number;
    manual_completion_percent: number;
    capture_status?: string;
    review_status?: string;
    profile: {
      available: boolean;
      status: string;
      source_report: string;
      source_xml?: string;
      authoritative: boolean;
      data_quality_flags: string[];
      packet_comparison: Record<string, number | string | null>;
      candidate_normalization: Record<string, number | string | null>;
      error?: string;
    };
    forensic: {
      available: boolean;
      status: string;
      source_report: string;
      conclusion: string;
      next_action: string;
      engine_swiss_diff_count: number;
      pl_diff_count: number;
      pl_swiss_max_abs_arcsec: number;
      uniform_offset_status: string;
      time_shift_status: string;
      row_health: {
        total: number;
        matched: number;
        diff_open: number;
      };
      error?: string;
    };
    settings_evidence: {
      available: boolean;
      status: string;
      source_report: string;
      proprietary_binary_policy: string;
      artifact_policy: string;
      options_files_count: number;
      text_artifacts_count: number;
      session_tokens_count: number;
      runtime_build: string;
      next_action: string;
      error?: string;
    };
    visible_settings_capture: {
      available: boolean;
      status: string;
      source_report: string;
      settings_dialog_captured: boolean;
      options_menu_captured: boolean;
      surfaces_count: number;
      screenshots_count: number;
      next_action: string;
      error?: string;
    };
    calculation_options: {
      available: boolean;
      status: string;
      source_report: string;
      selected_ayanamsha_key: string;
      selected_ayanamsha_label: string;
      selected_calculation_method_key: string;
      selected_calculation_method_label: string;
      offset_value: string;
      selected_miscellaneous_item_key: string;
      selected_miscellaneous_item_label: string;
      offset_control_visible: boolean;
      miscellaneous_list_visible: boolean;
      error?: string;
    };
  };
  open_items: Array<{
    source: string;
    status: string;
    label: string;
    failed_checks?: number;
    completion_percent?: number;
  }>;
};

export type ReportCitation = {
  title: string;
  work_title: string;
  snippet: string;
  public_url: string;
};

export type ReportSection = {
  key: string;
  title: string;
  body: string;
  review_status: string;
  calculation_only: boolean;
  citations: ReportCitation[];
};

export type SummaryItem = {
  label: string;
  value: string;
  detail?: string;
};

export type GrahaHouseSummary = {
  body: string;
  rashi: string;
  house: number | null;
  nakshatra: string;
  pada: number | null;
  navamsa: string;
};

export type DetailedPositionSummary = {
  body: string;
  chara_karaka: string | null;
  longitude: number | null;
  sign_degrees_dms: string;
  rashi: string;
  rashi_lord: string | null;
  navamsa: string;
  nakshatra: string;
  pada: number | null;
  house: number | null;
  ruled_houses: number[];
  dignity: string;
  retrograde: boolean;
};

export type HouseSummary = {
  house: number;
  rashi: string;
  grahas: string[];
};

export type PersonSummary = {
  birth_context: SummaryItem[];
  core_factors: SummaryItem[];
  graha_houses: GrahaHouseSummary[];
  detailed_positions: DetailedPositionSummary[];
  houses: HouseSummary[];
  panchanga: SummaryItem[];
  dasha: {
    birth_mahadasha_lord: string | null;
    current_mahadasha: DashaPeriod | null;
    current_antardasha: DashaPeriod | null;
    current_mahadasha_antardashas: DashaPeriod[];
    as_of: string | null;
    starts_at: string | null;
    ends_at: string | null;
  };
};

export type BirthReport = {
  chart: BirthChart;
  report: {
    review_status: string;
    calculation_version: string;
    source_policy: string;
    chart_facts?: Record<string, unknown>;
    person_summary?: PersonSummary;
    sections: ReportSection[];
  };
};

export type AnalysisPacket = {
  schema_version: string;
  status: string;
  prompt_markdown: string;
  generator_policy: Record<string, unknown>;
  citation_requests: {
    kind: string;
    key: string;
    title?: string;
    required_for_public_text?: boolean;
    citation_coverage_status?: string;
  }[];
  citations: ReportCitation[];
  context: Record<string, unknown>;
  report: Record<string, unknown>;
};

export type ShastraEvidenceCitation = {
  condition_key: string;
  condition_title: string;
  work_slug: string;
  work_title: string;
  source_url: string;
  passage_id: number;
  evidence_id: number;
  reference: string;
  excerpt: string;
  reviewer: string;
  review_status: string;
  public_quote_policy: string;
};

export type ShastraEvidenceItem = {
  id: number;
  condition_key: string;
  score: number;
  work_slug: string;
  work_title: string;
  passage_id: number;
  passage_reference: string;
  inferred_reference: string;
  reference_status: string;
  review_status: string;
  public_quote_policy: string;
  snippet: string;
};

export type ShastraEvidenceCondition = {
  condition_key: string;
  condition_kind: string;
  condition_title: string;
  condition_summary: string;
  evidence_status: string;
  public_release_policy: string;
  approved_citations: ShastraEvidenceCitation[];
  evidence: ShastraEvidenceItem[];
};

export type ShastraEvidencePayload = {
  schema_version: string;
  summary: {
    conditions: number;
    conditions_with_evidence: number;
    evidence_items: number;
    approved_conditions: number;
    approved_evidence_items: number;
    review_queue_items: number;
  };
  conditions: ShastraEvidenceCondition[];
};

export type GeneratedDraftAnalysis = {
  id: number;
  kind: string;
  review_status: string;
  coverage_status?: string;
  source_policy: string;
  provider?: string;
  model?: string;
  engine_label?: string;
  language?: string;
  sections: {
    title: string;
    body: string;
    key_points?: string[];
    practical_steps?: string[];
    condition_keys?: string[];
    evidence_references?: string[];
    citation_titles: string[];
    source_traces?: {
      condition_key: string;
      work_title: string;
      reference: string;
      source_status: string;
      short_excerpt: string;
      interpretation: string;
    }[];
    review_notes?: string[];
  }[];
};

export type CodexAnalysisChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type CodexAnalysisChatResponse = {
  id?: number;
  kind: string;
  analysis_id: number;
  question: string;
  answer: string;
  history_used?: number;
  evidence_references?: string[];
  source_traces?: {
    condition_key?: string;
    work_title?: string;
    reference?: string;
    source_status?: string;
    short_excerpt?: string;
    interpretation?: string;
  }[];
};

export type TransitRow = {
  body: string;
  longitude: number;
  rashi: string;
  nakshatra: string;
  pada: number;
  house_from_lagna: number | null;
  house_from_moon: number | null;
};

export type TransitReport = {
  status: string;
  method: string;
  interpretation_plan?: WorkflowInterpretationPlan;
  as_of: {
    date: string;
    time: string;
    timezone: string;
    local_datetime: string;
  };
  natal: {
    lagna: Record<string, unknown>;
    moon: Record<string, unknown>;
  };
  transits: TransitRow[];
};

export type MuhurtaCandidate = {
  date: string;
  time: string;
  score: number;
  purpose: string;
  purpose_profile: string;
  purpose_adjustments: {
    field: string;
    name: string | null;
    delta: number;
    status: string;
  }[];
  panchanga: Panchanga;
  day_periods: DayPeriod[];
  blocked_periods: DayPeriod[];
  reasons: string[];
};

export type MuhurtaReport = {
  status: string;
  method: string;
  purpose: string;
  purpose_profile: string;
  interpretation_plan?: WorkflowInterpretationPlan;
  candidates: MuhurtaCandidate[];
  vaishnava_note: string;
};

export type TithiPraveshaReport = {
  status: string;
  method: string;
  target_year: number;
  interpretation_plan?: WorkflowInterpretationPlan;
  search: {
    center_date: string;
    search_days: number;
    step_hours: number;
    tolerance_degrees: number;
  };
  natal: {
    birth: BirthChart["birth"];
    tithi?: Panchanga["tithi"];
    solar_lunar_angle: number;
    sun: CompactPlacement;
    moon: CompactPlacement;
  };
  return: {
    date: string;
    time: string;
    timezone: string;
    local_datetime: string;
    solar_lunar_angle: number;
    delta_degrees: number;
    iterations: number;
    chart: BirthChart;
  };
  annual_context: {
    lagna: CompactPlacement;
    sun: CompactPlacement;
    moon: CompactPlacement;
    panchanga: Panchanga;
    tajaka?: {
      status: string;
      method: string;
      completed_years?: number;
      muntha?: {
        rashi_index: number;
        rashi: string;
        house_from_annual_lagna: number;
      };
    };
  };
  audit: {
    review_status: string;
    source_anchors: string[];
    public_interpretation_status: string;
  };
};

export type TajakaReport = {
  status: string;
  method: string;
  tithi_pravesha: TithiPraveshaReport;
  interpretation_plan?: WorkflowInterpretationPlan;
  tajaka: {
    status: string;
    muntha?: {
      rashi_index: number;
      rashi: string;
      house_from_annual_lagna: number;
    };
    annual_lagna: CompactPlacement;
    annual_moon: CompactPlacement;
    annual_sun: CompactPlacement;
    panchanga: Panchanga;
    open_items: string[];
  };
  audit: {
    review_status: string;
    public_interpretation_status: string;
    chart_id: string | null;
  };
};

export type PrashnaReport = {
  status: string;
  method: string;
  interpretation_plan?: WorkflowInterpretationPlan;
  question: {
    text: string;
    asked_at: BirthChart["birth"];
    place: BirthChart["place"];
  };
  chart: BirthChart;
  indicators: {
    lagna: CompactPlacement;
    lagna_lord: string | null;
    lagna_lord_placement: CompactPlacement;
    moon: CompactPlacement;
    moon_house_from_lagna: number | null;
    seventh_house_rashi: string | null;
    panchanga: Panchanga;
  };
  audit: {
    review_status: string;
    source_anchors: string[];
    public_interpretation_status: string;
  };
};

export type MundaneReport = {
  status: string;
  method: string;
  interpretation_plan?: WorkflowInterpretationPlan;
  event: {
    type: string;
    description: string;
    occurred_at: BirthChart["birth"];
    place: BirthChart["place"];
  };
  chart: BirthChart;
  indicators: {
    lagna: CompactPlacement;
    sun: CompactPlacement;
    moon: CompactPlacement;
    tenth_house_rashi: string | null;
    fourth_house_rashi: string | null;
    slow_planets: { body: string; placement: CompactPlacement; house_from_lagna: number | null }[];
    panchanga: Panchanga;
  };
  audit: {
    review_status: string;
    source_anchors: string[];
    public_interpretation_status: string;
  };
};

export type CompatibilityReport = {
  status: string;
  method: string;
  interpretation_plan?: WorkflowInterpretationPlan;
  coverage: {
    system: string;
    calculated_kutas: number;
    total_kutas: number;
    calculated_perspectives?: number;
    status: string;
  };
  score: {
    total: number;
    max: number;
    percent: number;
  };
  moon: {
    person_a: CompactPlacement;
    person_b: CompactPlacement;
    rashi_distance_a_to_b: number | null;
    rashi_distance_b_to_a: number | null;
  };
  kuta: Record<string, unknown>;
  kuta_rows: {
    key: string;
    name: string;
    score: number;
    max_score: number;
    status: string;
    details: string;
  }[];
  analysis?: {
    status: string;
    review_status: string;
    source_policy: string;
    source_anchors: string[];
    vaishnava_guard: string;
    chart_summaries: Record<
      "person_a" | "person_b",
      {
        lagna: CompactPlacement;
        moon: CompactPlacement;
        seventh_house: {
          rashi: string | null;
          rashi_index: number | null;
          lord: string | null;
          planets: string[];
        };
        seventh_lord: {
          body: string | null;
          rashi: string | null;
          house: number | null;
          dignity: string;
        };
        relationship_grahas: Record<string, Record<string, unknown>>;
        birth_dasha_lord: string | null;
      }
    >;
    perspectives: {
      key: string;
      title: string;
      score: number;
      max_score: number;
      status: string;
      findings: string[];
      source_basis: string;
      review_status: string;
    }[];
    support_factors: string[];
    caution_factors: string[];
  };
  assessment: {
    level: string;
    caution_count: number;
    note: string;
  };
  vaishnava_note: string;
};

export type PlaceCandidate = {
  id: string;
  name: string;
  label: string;
  admin_name: string;
  country_code: string;
  latitude: number;
  longitude: number;
  timezone: string;
};

export type User = {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_staff: boolean;
};

export type ChartProfile = {
  id: number;
  display_name: string;
  birth_date: string;
  birth_time: string | null;
  birth_time_accuracy: string;
  timezone: string;
  calculation_settings: NonNullable<BirthChart["settings"]>;
  place: {
    id: number;
    external_id: string;
    name: string;
    label: string;
    country_code: string;
    latitude: number;
    longitude: number;
    timezone: string;
  };
  latest_calculation: null | {
    id: number;
    status: string;
    calculation_version: string;
    graha_count: number;
    created_at: string;
    updated_at: string;
  };
  created_at: string;
  updated_at: string;
};

export type ChartCalculationRecord = {
  id: number;
  profile_id: number;
  calculation_version: string;
  ayanamsa: string;
  house_system: string;
  status: string;
  error: string;
  result: BirthChart;
  created_at: string;
  updated_at: string;
};

export type VLSearchResult = {
  id: number;
  unit_id: number | null;
  work_id: number | null;
  work_title: string;
  document_type: string;
  language_code: string;
  title: string;
  body: string;
  date_text: string;
  metadata: Record<string, unknown>;
  public_url: string;
};

export type ResearchSearchResult = {
  title: string;
  work_title: string;
  body: string;
  source_url: string;
  review_status: string;
  work_review_status: string;
  rights_status: string;
  public_quote_policy: string;
  is_public_citation: boolean;
};

export type SourceWorkSummary = {
  id: number;
  slug: string;
  title: string;
  source_class: string;
  author: string;
  edition: string;
  language_code: string;
  source_url: string;
  review_status: string;
  passage_count: number | null;
  rights_status: string;
  public_quote_policy: string;
};

export type SourceInventory = {
  schema_version: string;
  summary: {
    total_works: number;
    total_passages: number;
    research_only_works: number;
    research_only_passages: number;
    returned_works: number;
    search_scope: string;
  };
  works: SourceWorkSummary[];
};

export type SourcePassageResult = {
  id: number;
  reference: string;
  body: string;
  language_code: string;
  review_status: string;
  rights_status: string;
  public_quote_policy: string;
  metadata: Record<string, unknown>;
};

export type SourcePassagesResponse = {
  work: SourceWorkSummary;
  limit: number;
  offset: number;
  items: SourcePassageResult[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const FALLBACK_RESPONSE_STATUSES = new Set([404, 502, 503, 504]);

function apiBaseUrls() {
  if (API_BASE_URL) return [API_BASE_URL];
  const browserHost = typeof window === "undefined" ? "" : window.location.hostname;
  const browserProtocol = typeof window === "undefined" ? "http:" : window.location.protocol;
  const host = browserHost || "127.0.0.1";
  const protocol = browserProtocol === "https:" ? "https" : "http";
  return Array.from(
    new Set([
      `${protocol}://${host}:8000`,
      `${protocol}://${host}:8100`,
      "http://127.0.0.1:8000",
      "http://127.0.0.1:8100",
    ]),
  );
}

function csrfToken() {
  if (typeof document === "undefined") return "";
  return document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith("csrftoken="))
    ?.split("=")[1] ?? "";
}

async function ensureCsrf(force = false) {
  if (!force && csrfToken()) return;
  let lastError: unknown = null;
  for (const baseUrl of apiBaseUrls()) {
    try {
      const response = await fetch(`${baseUrl}/api/auth/csrf`, {
        credentials: "include",
        cache: "no-store",
      });
      if (response.ok) return;
      lastError = new Error(`CSRF API ${baseUrl} returned ${response.status}`);
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

async function apiFetch(path: string, init: RequestInit = {}) {
  const method = init.method?.toUpperCase() ?? "GET";
  const headers = new Headers(init.headers);
  if (method !== "GET" && method !== "HEAD") {
    await ensureCsrf();
    headers.set("X-CSRFToken", csrfToken());
  }
  let lastError: unknown = null;
  const baseUrls = apiBaseUrls();
  for (let index = 0; index < baseUrls.length; index += 1) {
    const baseUrl = baseUrls[index];
    try {
      const response = await fetch(`${baseUrl}${path}`, {
        ...init,
        credentials: "include",
        headers,
      });
      const canTryNextBaseUrl =
        !process.env.NEXT_PUBLIC_API_BASE_URL &&
        index < baseUrls.length - 1 &&
        FALLBACK_RESPONSE_STATUSES.has(response.status);
      if (canTryNextBaseUrl) {
        lastError = new Error(`API ${baseUrl} returned ${response.status}`);
        continue;
      }
      return response;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

async function retryNetworkFetch<T>(operation: () => Promise<T>, retries = 1): Promise<T> {
  let lastError: unknown = null;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      if (!isNetworkFetchError(error) || attempt >= retries) break;
      await delay(1500 * (attempt + 1));
    }
  }
  throw lastError;
}

function isNetworkFetchError(error: unknown) {
  return error instanceof TypeError && /fetch|network|load failed/i.test(error.message);
}

function delay(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

export async function fetchZodiacPlacement(longitude: number): Promise<ZodiacPlacement> {
  const response = await apiFetch(
    `/api/calculations/zodiac-placement?longitude=${encodeURIComponent(longitude)}`,
    { cache: "no-store" },
  );

  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  return response.json();
}

export async function fetchEphemerisStatus(): Promise<EphemerisStatus> {
  const response = await apiFetch("/api/calculations/ephemeris/status", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  return response.json();
}

export async function calculateBirthChart(payload: BirthChartRequest): Promise<BirthChart> {
  const response = await apiFetch("/api/calculations/birth-chart", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function calculateDualCalculation(payload: BirthChartRequest): Promise<DualCalculationReport> {
  const response = await apiFetch("/api/calculations/dual", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function fetchJHoraAccuracyReport(): Promise<JHoraAccuracyReport> {
  const response = await apiFetch("/api/calculations/jhora-accuracy", {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function fetchParasharaLightPacketReport(): Promise<ParasharaLightPacketReport> {
  const response = await apiFetch("/api/calculations/parashara-light-packet", {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function fetchWitnessSummary(): Promise<WitnessSummary> {
  const response = await apiFetch("/api/calculations/witness-summary", {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function generateBirthReport(payload: BirthChartRequest): Promise<BirthReport> {
  const response = await apiFetch("/api/reports/birth-chart", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function generateCompatibilityAnalysisPacket(payload: CompatibilityRequest): Promise<AnalysisPacket> {
  const response = await apiFetch("/api/reports/compatibility/analysis-packet", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function generateCompatibilityCodexAnalysis(payload: CompatibilityRequest): Promise<GeneratedDraftAnalysis> {
  return retryNetworkFetch(async () => {
    const response = await apiFetch("/api/reports/compatibility/codex-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error ?? `API returned ${response.status}`);
    }

    return data;
  });
}

export async function fetchShastraEvidence(keys: string[] = []): Promise<ShastraEvidencePayload> {
  const query = keys.length ? `?keys=${encodeURIComponent(keys.join(","))}` : "";
  const response = await apiFetch(`/api/reports/shastra-evidence${query}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function generateBirthDraftAnalysis(payload: BirthChartRequest): Promise<GeneratedDraftAnalysis> {
  const response = await apiFetch("/api/reports/birth-chart/draft-analysis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function generateBirthCodexAnalysis(
  payload: BirthChartRequest,
  options: { forceRegenerate?: boolean } = {},
): Promise<GeneratedDraftAnalysis> {
  return retryNetworkFetch(async () => {
    const response = await apiFetch("/api/reports/birth-chart/codex-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options.forceRegenerate ? { ...payload, force_regenerate: true } : payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error ?? `API returned ${response.status}`);
    }

    return data;
  });
}

export async function generateBirthQwenAnalysis(payload: BirthChartRequest): Promise<GeneratedDraftAnalysis> {
  return retryNetworkFetch(async () => {
    const response = await apiFetch("/api/reports/birth-chart/qwen-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error ?? `API returned ${response.status}`);
    }

    return data;
  });
}

export async function generateBirthNemotronAnalysis(payload: BirthChartRequest): Promise<GeneratedDraftAnalysis> {
  return retryNetworkFetch(async () => {
    const response = await apiFetch("/api/reports/birth-chart/nemotron-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error ?? `API returned ${response.status}`);
    }

    return data;
  });
}

export async function askBirthCodexAnalysis(
  analysisId: number,
  question: string,
  history: CodexAnalysisChatMessage[],
): Promise<CodexAnalysisChatResponse> {
  const response = await apiFetch("/api/reports/birth-chart/codex-analysis/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ analysis_id: analysisId, question, history }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function askCompatibilityCodexAnalysis(
  analysisId: number,
  question: string,
  history: CodexAnalysisChatMessage[],
): Promise<CodexAnalysisChatResponse> {
  const response = await apiFetch("/api/reports/compatibility/codex-analysis/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ analysis_id: analysisId, question, history }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function calculateTransits(payload: TransitRequest): Promise<TransitReport> {
  const response = await apiFetch("/api/calculations/transits", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function calculateMuhurta(payload: MuhurtaRequest): Promise<MuhurtaReport> {
  const response = await apiFetch("/api/calculations/muhurta", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function calculateCompatibility(payload: CompatibilityRequest): Promise<CompatibilityReport> {
  const response = await apiFetch("/api/calculations/compatibility", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function calculateTithiPravesha(payload: TithiPraveshaRequest): Promise<TithiPraveshaReport> {
  const response = await apiFetch("/api/calculations/tithi-pravesha", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function calculateTajaka(payload: TithiPraveshaRequest): Promise<TajakaReport> {
  const response = await apiFetch("/api/calculations/tajaka", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function calculatePrashna(payload: PrashnaRequest): Promise<PrashnaReport> {
  const response = await apiFetch("/api/calculations/prashna", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function calculateMundane(payload: MundaneRequest): Promise<MundaneReport> {
  const response = await apiFetch("/api/calculations/mundane", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function searchPlaces(query: string): Promise<PlaceCandidate[]> {
  if (!query.trim()) return [];
  const response = await apiFetch(`/api/places/search?q=${encodeURIComponent(query)}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  const data = await response.json();
  return data.items ?? [];
}

export async function searchVLSources(query: string): Promise<VLSearchResult[]> {
  if (!query.trim()) return [];
  const response = await apiFetch(`/api/sources/vl/search?q=${encodeURIComponent(query)}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data.items ?? [];
}

export async function searchResearchSources(query: string): Promise<ResearchSearchResult[]> {
  if (!query.trim()) return [];
  const response = await apiFetch(`/api/sources/research/search?q=${encodeURIComponent(query)}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data.items ?? [];
}

export async function fetchSourceWorks(): Promise<SourceInventory> {
  const response = await apiFetch("/api/sources/works?limit=1000", {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function fetchSourcePassages(slug: string, offset = 0): Promise<SourcePassagesResponse> {
  const response = await apiFetch(
    `/api/sources/works/${encodeURIComponent(slug)}/passages?limit=12&offset=${encodeURIComponent(offset)}`,
    { cache: "no-store" },
  );

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data;
}

export async function fetchCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/auth/me", { cache: "no-store" });
  const data = await response.json();
  if (response.status === 401) return null;
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }
  return data.user ?? null;
}

export async function loginUser(username: string, password: string): Promise<User> {
  const response = await apiFetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }
  await ensureCsrf(true);
  return data.user;
}

export async function registerUser(username: string, password: string): Promise<User> {
  const response = await apiFetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }
  await ensureCsrf(true);
  return data.user;
}

export async function logoutUser(): Promise<void> {
  const response = await apiFetch("/api/auth/logout", { method: "POST" });
  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error ?? `API returned ${response.status}`);
  }
  await ensureCsrf(true);
}

export async function listChartProfiles(): Promise<ChartProfile[]> {
  const response = await apiFetch("/api/charts/profiles", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }
  return data.profiles ?? [];
}

export async function createChartProfile(payload: BirthChartRequest & { display_name: string }): Promise<ChartProfile> {
  const response = await apiFetch("/api/charts/profiles", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...payload,
      birth_time_accuracy: "exact",
    }),
  });
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 403) {
      throw new Error("Нет доступа к сохранению: войдите заново или обновите страницу для CSRF-сессии");
    }
    throw new Error(data.error ?? `API returned ${response.status}`);
  }
  return data.profile;
}

export async function calculateSavedProfile(profileId: number): Promise<ChartCalculationRecord> {
  const response = await apiFetch(`/api/charts/profiles/${profileId}/calculate`, {
    method: "POST",
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? data.calculation?.error ?? `API returned ${response.status}`);
  }
  return data.calculation;
}
