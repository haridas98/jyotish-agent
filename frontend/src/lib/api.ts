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
  profile_id?: number;
  related_profile_ids?: number[];
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
  relationship_context?: {
    role: string;
    label: string;
    focus_houses: number[];
    focus_vargas: string[];
    prompt_hint: string;
    consent_policy: string;
    relationship_id?: number;
    link_status?: string;
    profile_id?: number;
    related_profile_id?: number;
    profile_label?: string;
    related_profile_label?: string;
  };
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
  retrograde?: boolean;
  dignity?: string | null;
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

export type HouseCusp = {
  house: number;
  longitude: number;
  rashi: string;
  rashi_index: number;
};

export type VargaPlacement = {
  body: string;
  rashi_index: number;
  rashi: string;
  dignity?: string | null;
};

export type VargaChart = {
  code: string;
  name: string;
  method: string;
  methodId?: string;
  methodVersion?: string;
  calculationPreset?: string;
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
  mahadasha_lord?: string;
  antardashas?: DashaPeriod[];
  pratyantardashas?: DashaPeriod[];
  boundary_policy?: string;
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
  house_cusps?: HouseCusp[];
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

export type WitnessCaptureQueueItem = {
  priority: number;
  id: string;
  group: string;
  label: string;
  status: string;
  capture_targets: {
    jhora: string[];
    parashara_light: string[];
  };
  suggested_actions: string[];
  suggested_action_labels: string[];
  next_action_key: string;
  next_action_label: string;
  next_command_kind: string;
  next_step_label: string;
  next_command: string;
  manual_review_command: string;
  blocker_count: number;
};

export type WitnessOpenDiffRow = {
  field: string;
  witness: string | number | null;
  calculated: string | number | null;
  delta_arcseconds?: number;
};

export type WitnessOpenDiffSummary = {
  status: string;
  failed_count: number;
  sample: WitnessOpenDiffRow[];
};

export type WitnessReviewChecklistItem = {
  key: string;
  label: string;
  status: string;
  required: boolean;
  detail: string;
  next_step: string;
};

export type WitnessSummary = {
  overall_status: string;
  birth_timezone_audit: {
    available: boolean;
    status: string;
    source_packet: string;
    birth_date: string;
    birth_time: string;
    timezone: string;
    timezone_source: string;
    expected_utc_offset: string;
    resolved_utc_offset: string;
    local_datetime_utc_offset: string;
    local_datetime: string;
    utc_datetime: string;
    dst_observed: boolean;
    error?: string;
  };
  witness_review: {
    available: boolean;
    status: string;
    overall: {
      reviewable: boolean;
      ack_required: boolean;
      blocked: boolean;
    };
    seal_command: string;
    safe_next_step: string;
    jhora: {
      available?: boolean;
      source?: string;
      id?: string;
      status?: string;
      missing_evidence?: string[];
      ack_required?: boolean;
      review_command?: string;
      packet_path?: string;
      fixture_path?: string;
    };
    parashara_light: {
      available?: boolean;
      source?: string;
      id?: string;
      status?: string;
      missing_evidence?: string[];
      ack_required?: boolean;
      review_command?: string;
      packet_path?: string;
      fixture_path?: string;
    };
    open_diffs: {
      status: string;
      jhora: WitnessOpenDiffSummary;
      parashara_light: WitnessOpenDiffSummary;
      error?: string;
    };
    review_checklist: WitnessReviewChecklistItem[];
    error?: string;
  };
  witness_review_batch: {
    available: boolean;
    status: string;
    source_index: string;
    schema_version: string;
    metadata: {
      generated_at: string;
      reviewer: string;
      reviewed_at: string;
      jhora_root: string;
      pl_root: string;
    };
    summary: {
      written_count: number;
      skipped_count: number;
      error_count: number;
      output_root: string;
      index_path: string;
      index_json_path: string;
      target_reviewed_count: number;
      batch_review_ready_count: number;
      remaining_to_target_count: number;
      reviewable_count: number;
      blocked_count: number;
      ack_required_count: number;
      next_case_ids: string[];
      next_review_case_id: string;
      next_review_step: string;
    };
    written: Array<{
      id: string;
      output_path: string;
      reviewable: boolean;
      ack_required: boolean;
      blocked: boolean;
      safe_next_step: string;
      review_checklist: WitnessReviewChecklistItem[];
      review_checklist_summary: string;
      review_checklist_next_steps_summary: string;
    }>;
    next_actions: Array<{
      id: string;
      group: string;
      label: string;
      status: string;
      missing_for_authoritative_review: string[];
      missing_secondary_witness: string[];
      suggested_actions: string[];
      suggested_action_labels: string[];
    }>;
    skipped_reason_counts: Record<string, number>;
    errors: Array<{
      id?: string;
      error?: string;
    }>;
    audit_summary: Record<string, number | string | boolean | string[] | null>;
    error?: string;
  };
  witness_capture_queue: {
    available: boolean;
    status: string;
    source_queue: string;
    schema_version: string;
    metadata: {
      generated_at: string;
      jhora_root: string;
      pl_root: string;
      target_reviewed_count: number;
      limit: number;
    };
    summary: {
      queue_count: number;
      remaining_to_target_count: number;
      batch_review_ready_count: number;
      capture_started_count: number;
      pl_witness_count: number;
      output: string;
      markdown_output: string;
    };
    items: WitnessCaptureQueueItem[];
    next_item: WitnessCaptureQueueItem | null;
    next_action_key: string;
    next_action_label: string;
    next_command_kind: string;
    next_step_label: string;
    next_command: string;
    manual_review_command: string;
    error?: string;
  };
  jhora: {
    available: boolean;
    status: string;
    fixture_id: string;
    source_report: string;
    source_export: string;
    birth_export: {
      available: boolean;
      status: string;
      source_export: string;
      date: string;
      time: string;
      timezone_line: string;
      parsed_utc_offset: string;
      place: string;
      error?: string;
    };
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
      raw_birth_info: Record<string, number | string | null>;
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
    settings_aware_forensic: {
      available: boolean;
      status: string;
      source_report: string;
      ayanamsha_status: string;
      offset_status: string;
      engine_swiss_status: string;
      uniform_offset_status: string;
      time_shift_status: string;
      next_action: string;
      error?: string;
    };
    preferences_inventory: {
      available: boolean;
      status: string;
      source_report: string;
      tabs_count: number;
      visible_ayanamsha_controls: boolean;
      visible_graph_ephemeris_display_option: boolean;
      visible_system_paths: boolean;
      internal_ephemeris_mode_visible: boolean;
      next_action: string;
      error?: string;
    };
    hidden_option_store: {
      available: boolean;
      status: string;
      source_report: string;
      proprietary_binary_policy: string;
      primary_candidate: string;
      option_store_candidates_count: number;
      session_token_candidates_count: number;
      next_action: string;
      error?: string;
    };
    option_store_diff: {
      available: boolean;
      status: string;
      source_report: string;
      proprietary_binary_policy: string;
      visible_setting: string;
      primary_candidate: string;
      changed_candidates_count: number;
      restore_verified: boolean;
      next_action: string;
      error?: string;
    };
    internal_settings_audit: {
      available: boolean;
      status: string;
      source_report: string;
      visible_settings_status: string;
      internal_ephemeris_mode_visible: boolean;
      option_store_diff_status: string;
      hidden_option_store_primary_candidate: string;
      ruled_out_count: number;
      next_action: string;
      error?: string;
    };
  };
  open_items: Array<{
    source: string;
    status: string;
    label: string;
    failed_checks?: number;
    completion_percent?: number;
    next_action?: string;
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
  slug?: string;
  kind: string;
  review_status: string;
  coverage_status?: string;
  source_policy: string;
  provider?: string;
  model?: string;
  engine_label?: string;
  language?: string;
  billing_status?: string;
  billing_message?: string;
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

export type AnalysisHistoryItem = {
  id: number;
  slug: string;
  kind: string;
  provider: string;
  model: string;
  review_status: string;
  source_policy: string;
  engine_label: string;
  section_count: number;
  created_at: string;
  input_summary?: Record<string, unknown>;
  input_snapshot: Record<string, unknown>;
  chat_count: number;
  first_section_title?: string;
  excerpt?: string;
};

export type AnalysisHistoryDetail = {
  analysis: AnalysisHistoryItem & {
    output_json?: GeneratedDraftAnalysis & Record<string, unknown>;
    packet_snapshot?: Record<string, unknown>;
    prompt_markdown?: string;
  };
  chat_record_limit?: number;
  chat_record_total?: number;
  chat_messages: (CodexAnalysisChatMessage & {
    analysis_message_id?: number;
    created_at?: string;
  })[];
  chat_truncated?: boolean;
};

export type AnalysisHistoryQuery = {
  kind?: string;
  profileId?: number;
  limit?: number;
};

export type AnalysisGenerationJob = {
  id: number;
  kind: string;
  status: "queued" | "running" | "complete" | "failed";
  input_summary: Record<string, unknown>;
  analysis_id: number | null;
  analysis_slug: string;
  error: string;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
};

export type QueuedAnalysisGeneration = {
  queued: true;
  job: AnalysisGenerationJob;
  message?: string;
};

export type AnalysisGenerationJobQuery = {
  kind?: string;
  status?: AnalysisGenerationJob["status"];
  limit?: number;
};

export function isQueuedAnalysisGeneration(value: unknown): value is QueuedAnalysisGeneration {
  return Boolean(
    value &&
      typeof value === "object" &&
      (value as { queued?: unknown }).queued === true &&
      typeof (value as { job?: { id?: unknown } }).job?.id === "number",
  );
}

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
  relationship_context?: {
    role: string;
    label: string;
    focus_houses: number[];
    focus_vargas: string[];
    prompt_hint: string;
    relationship_id?: number | null;
    link_status?: string | null;
    profile_id?: number | null;
    related_profile_id?: number | null;
    profile_label?: string | null;
    related_profile_label?: string | null;
    consent_policy?: string;
    required_factors?: string[];
  };
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
  gender: "male" | "female" | "unknown";
  timezone: string;
  is_self_profile: boolean;
  notes: string;
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

export type JyotishCalculationSettings = {
  ayanamsa: "lahiri" | "raman" | "krishnamurti" | "yukteshwar";
  zodiacType: "sidereal";
  houseSystem: "whole_sign" | "sripati" | "equal";
  nodeType: "mean" | "true";
  calculationProfile: "default" | "bphs_research" | "gaudiya_default";
  divisionalChartsEnabled: string[];
  defaultDivisionalChart: "D1" | "D2" | "D3" | "D4" | "D7" | "D9" | "D10" | "D12" | "D16" | "D20" | "D24" | "D30" | "D60";
  timezoneMode: "birth_place_timezone";
};

export type JyotishDisplaySettings = {
  chartStyle: "north_indian" | "south_indian";
  language: "ru" | "en";
  terminologyMode: "russian" | "sanskrit" | "mixed";
  degreeFormat: "dms" | "decimal";
  showSanskritNames: boolean;
  showTransliteration: boolean;
  themeMode: "system" | "light" | "dark";
};

export type JyotishUserSettings = {
  id: number;
  userId: number;
  calculation: JyotishCalculationSettings;
  display: JyotishDisplaySettings;
  createdAt: string;
  updatedAt: string;
};

export type ChartProfileRelationship = {
  id: number;
  user: null | {
    id: number;
    username: string;
  };
  profile_id: number;
  related_profile_id: number;
  profile: null | {
    id: number;
    display_name: string;
    birth_date: string;
    place_label: string;
  };
  related_profile: null | {
    id: number;
    display_name: string;
    birth_date: string;
    place_label: string;
  };
  role: string;
  link_status: string;
  requested_user: null | {
    id: number;
    username: string;
  };
  notes: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ChartRelationship = {
  id: number;
  chart_a_id: number;
  chart_b_id: number;
  chart_a: null | {
    id: number;
    display_name: string;
    birth_date: string;
    place_label: string;
  };
  chart_b: null | {
    id: number;
    display_name: string;
    birth_date: string;
    place_label: string;
  };
  relationship_type_id: string;
  role_a_id: string;
  role_b_id: string;
  pair_key: string;
  notes: string;
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

export type ChartWorkbenchScope = "d1" | "d2" | "d3" | "d4" | "d7" | "d9" | "d10" | "d12" | "d16" | "d20" | "d24" | "d30" | "d60";

export type VargaScopeCategory = "main" | "family" | "professional" | "spiritual" | "expert";

export type VargaScopeMetadata = {
  code: string;
  name: string;
  category: VargaScopeCategory;
  methodId: string;
  methodVersion: string;
  calculationPreset: string;
  expertOnly: boolean;
  timeAccuracyRequired: string;
};

export type VargaAccuracyGate = {
  scopeId: string;
  status: "usable" | "blocked" | string;
  requiredBirthTimeAccuracy: string;
  actualBirthTimeAccuracy: string;
  reason: string;
};

export type D1WorkbenchApiResponse = {
  scope: ChartWorkbenchScope;
  profile: ChartProfile;
  calculation: ChartCalculationRecord | null;
  result: BirthChart | null;
  method?: {
    methodId: string;
    methodVersion: string;
    calculationPreset: string;
  };
  warnings?: Array<{ code: string; severity: string; message: string }>;
  accuracyGates?: Record<string, VargaAccuracyGate>;
  supportedScopes?: string[];
  expertOnlyScopes?: string[];
  vargaScopes?: VargaScopeMetadata[];
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

type ApiErrorPayload = {
  error?: unknown;
  message?: unknown;
  retry_after_seconds?: unknown;
  [key: string]: unknown;
};

export class ApiError extends Error {
  code: string;
  payload: ApiErrorPayload;
  retryAfterSeconds?: number;
  status: number;

  constructor(message: string, options: { status: number; code: string; payload?: ApiErrorPayload }) {
    super(message);
    this.name = "ApiError";
    this.status = options.status;
    this.code = options.code;
    this.payload = options.payload ?? {};
    const retryAfter = Number(this.payload.retry_after_seconds);
    if (Number.isFinite(retryAfter) && retryAfter > 0) {
      this.retryAfterSeconds = retryAfter;
    }
  }
}

function apiErrorFromResponse(status: number, data: ApiErrorPayload, fallbackMessage: string) {
  const code = typeof data.error === "string" ? data.error : `api_status_${status}`;
  const message = typeof data.message === "string" && data.message.trim()
    ? data.message
    : fallbackMessage === "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ"
      ? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ. РћР±РЅРѕРІРёС‚Рµ СЃС‚СЂР°РЅРёС†Сѓ РёР»Рё РїРѕРїСЂРѕР±СѓР№С‚Рµ РїРѕР·Р¶Рµ."
      : fallbackMessage;
  return new ApiError(message, { status, code, payload: data });
}

export function isAnalysisInProgressError(error: unknown): error is ApiError {
  return (
    error instanceof ApiError &&
    [409, 429].includes(error.status) &&
    ["analysis_generation_in_progress", "analysis_chat_in_progress", "analysis_user_generation_limit"].includes(error.code)
  );
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const FALLBACK_RESPONSE_STATUSES = new Set([404, 500, 502, 503, 504]);

function apiBaseUrls() {
  if (API_BASE_URL) return [API_BASE_URL];
  return [""];
}

function apiNetworkError(path: string, baseUrls: string[], lastError: unknown) {
  const rawDetail = lastError instanceof Error ? lastError.message : String(lastError ?? "network error");
  const detail = rawDetail === "Failed to fetch" ? "сетевой запрос не выполнен" : rawDetail;
  return new Error(`Backend API недоступен для ${path}. Проверены адреса: ${baseUrls.join(", ")}. Деталь: ${detail}`);
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
  const baseUrls = apiBaseUrls();
  for (const baseUrl of baseUrls) {
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
  throw apiNetworkError("/api/auth/csrf", baseUrls, lastError);
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
  throw apiNetworkError(path, baseUrls, lastError);
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
    throw new Error("Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return response.json();
}

export async function fetchEphemerisStatus(): Promise<EphemerisStatus> {
  const response = await apiFetch("/api/calculations/ephemeris/status", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return response.json();
}

export async function calculateBirthChart(payload: BirthChartRequest, options: { signal?: AbortSignal } = {}): Promise<BirthChart> {
  const response = await apiFetch("/api/calculations/birth-chart", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: options.signal,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function fetchJHoraAccuracyReport(): Promise<JHoraAccuracyReport> {
  const response = await apiFetch("/api/calculations/jhora-accuracy", {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function fetchParasharaLightPacketReport(): Promise<ParasharaLightPacketReport> {
  const response = await apiFetch("/api/calculations/parashara-light-packet", {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function fetchWitnessSummary(): Promise<WitnessSummary> {
  const response = await apiFetch("/api/calculations/witness-summary", {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function generateCompatibilityCodexAnalysis(payload: CompatibilityRequest): Promise<GeneratedDraftAnalysis | QueuedAnalysisGeneration> {
  return retryNetworkFetch(async () => {
    const response = await apiFetch("/api/reports/compatibility/codex-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      if (data.payment_required) {
        throw apiErrorFromResponse(response.status, data, "Р Р°Р·Р±РѕСЂ СЌС‚РѕР№ РєР°СЂС‚С‹ С‚СЂРµР±СѓРµС‚ РѕРїР»Р°С‚С‹.");
      }
      throw apiErrorFromResponse(response.status, data, "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function generateBirthCodexAnalysis(
  payload: BirthChartRequest,
  options: { forceRegenerate?: boolean } = {},
): Promise<GeneratedDraftAnalysis | QueuedAnalysisGeneration> {
  return retryNetworkFetch(async () => {
    const response = await apiFetch("/api/reports/birth-chart/codex-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options.forceRegenerate ? { ...payload, force_regenerate: true } : payload),
    });

    const data = await response.json();
    if (!response.ok) {
      if (data.payment_required) {
        throw apiErrorFromResponse(
          response.status,
          data,
          "Р Р°Р·Р±РѕСЂ С‡СѓР¶РѕР№ СЃРѕС…СЂР°РЅС‘РЅРЅРѕР№ РєР°СЂС‚С‹ С‚СЂРµР±СѓРµС‚ РѕРїР»Р°С‚С‹. РљР°СЂС‚Сѓ РјРѕР¶РЅРѕ С…СЂР°РЅРёС‚СЊ Рё СЃРјРѕС‚СЂРµС‚СЊ Р±РµСЃРїР»Р°С‚РЅРѕ.",
        );
      }
      throw apiErrorFromResponse(response.status, data, "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
    }

    return data;
  });
}

export async function generateCurrentDayOverview(payload: TransitRequest): Promise<GeneratedDraftAnalysis> {
  const response = await apiFetch("/api/reports/birth-chart/current-day", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw apiErrorFromResponse(response.status, data, "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function askAnalysis(
  analysisId: number,
  question: string,
  history: CodexAnalysisChatMessage[],
): Promise<CodexAnalysisChatResponse> {
  const response = await apiFetch("/api/reports/analysis/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ analysis_id: analysisId, question, history }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw apiErrorFromResponse(response.status, data, "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
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
    throw apiErrorFromResponse(response.status, data, "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw apiErrorFromResponse(response.status, data, "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function fetchAnalysisHistory(query: AnalysisHistoryQuery = {}): Promise<AnalysisHistoryItem[]> {
  const params = new URLSearchParams();
  if (query.kind) params.set("kind", query.kind);
  if (query.profileId) params.set("profile_id", String(query.profileId));
  if (query.limit) params.set("limit", String(query.limit));
  const suffix = params.toString() ? `?${params.toString()}` : "";
  const response = await apiFetch(`/api/reports/history${suffix}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data.items ?? [];
}

export async function fetchAnalysisHistoryDetail(id: number): Promise<AnalysisHistoryDetail> {
  const response = await apiFetch(`/api/reports/history/${encodeURIComponent(id)}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function fetchAnalysisHistoryBySlug(slug: string): Promise<AnalysisHistoryDetail> {
  const response = await apiFetch(`/api/reports/history/slug/${encodeURIComponent(slug)}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function fetchAnalysisChatHistory(analysisId: number): Promise<CodexAnalysisChatMessage[]> {
  const response = await apiFetch(`/api/reports/history/${encodeURIComponent(analysisId)}/chat`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data.messages ?? [];
}

export async function fetchAnalysisGenerationJobs(query: AnalysisGenerationJobQuery = {}): Promise<AnalysisGenerationJob[]> {
  const params = new URLSearchParams();
  if (query.kind) params.set("kind", query.kind);
  if (query.status) params.set("status", query.status);
  if (query.limit) params.set("limit", String(query.limit));
  const suffix = params.toString() ? `?${params.toString()}` : "";
  const response = await apiFetch(`/api/reports/generation-jobs${suffix}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw apiErrorFromResponse(response.status, data, "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data.jobs ?? [];
}

export async function fetchAnalysisGenerationJob(jobId: number): Promise<AnalysisGenerationJob> {
  const response = await apiFetch(`/api/reports/generation-jobs/${encodeURIComponent(jobId)}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw apiErrorFromResponse(response.status, data, "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data.job;
}

export async function calculateTransits(payload: TransitRequest): Promise<TransitReport> {
  const response = await apiFetch("/api/calculations/transits", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function searchPlaces(query: string): Promise<PlaceCandidate[]> {
  if (!query.trim()) return [];
  const response = await apiFetch(`/api/places/search?q=${encodeURIComponent(query)}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data.items ?? [];
}

export async function fetchSourceWorks(): Promise<SourceInventory> {
  const response = await apiFetch("/api/sources/works?limit=1000", {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
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
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }

  return data;
}

export async function fetchCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/auth/me", { cache: "no-store" });
  const data = await response.json();
  if (response.status === 401) return null;
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.user ?? null;
}

export async function fetchJyotishSettings(): Promise<JyotishUserSettings> {
  const response = await apiFetch("/api/settings", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? data.detail ?? "Запрос не выполнен");
  }
  return data;
}

export async function updateJyotishSettings(payload: {
  calculation?: Partial<JyotishCalculationSettings>;
  display?: Partial<JyotishDisplaySettings>;
}): Promise<JyotishUserSettings> {
  const response = await apiFetch("/api/settings", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? data.detail ?? "Запрос не выполнен");
  }
  return data;
}

export async function loginUser(username: string, password: string): Promise<User> {
  const response = await apiFetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  await ensureCsrf(true);
  return data.user;
}

export type RegisterOptions = {
  display_name?: string;
  birth_date?: string;
  birth_time?: string;
  birth_time_accuracy?: string;
  place_name?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
};

export type RegisterResult = {
  user: User;
  status: string;
  profile?: ChartProfile;
};

export async function registerUser(username: string, password: string, options: RegisterOptions = {}): Promise<RegisterResult> {
  const response = await apiFetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, ...options }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  await ensureCsrf(true);
  return data;
}

export async function logoutUser(): Promise<void> {
  const response = await apiFetch("/api/auth/logout", { method: "POST" });
  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  await ensureCsrf(true);
}

export async function listChartProfiles(): Promise<ChartProfile[]> {
  const response = await apiFetch("/api/charts", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.profiles ?? [];
}

export async function fetchChartProfile(profileId: number): Promise<ChartProfile> {
  const response = await apiFetch(`/api/charts/${profileId}`, { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Request failed");
  }
  return data.profile;
}
export async function fetchD1ChartWorkbench(profileId: number, scope: ChartWorkbenchScope = "d1"): Promise<D1WorkbenchApiResponse> {
  const response = await apiFetch("/api/charts/" + profileId + "/workbench?scope=" + scope, { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Request failed");
  }
  return data;
}


export type TransitWorkbenchQuery = {
  at?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
  scope?: "d1";
};

export async function fetchTransitWorkbench(profileId: number, query: TransitWorkbenchQuery = {}): Promise<Record<string, unknown>> {
  const params = new URLSearchParams();
  if (query.at) params.set("at", query.at);
  if (query.timezone) params.set("timezone", query.timezone);
  if (typeof query.latitude === "number") params.set("latitude", String(query.latitude));
  if (typeof query.longitude === "number") params.set("longitude", String(query.longitude));
  if (query.scope) params.set("scope", query.scope);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  const response = await apiFetch(`/api/charts/${profileId}/transit-workbench${suffix}`, { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Request failed");
  }
  return data;
}
export async function createChartProfile(payload: BirthChartRequest & { display_name: string; is_self_profile?: boolean; birth_time_accuracy?: string; gender?: "male" | "female" | "unknown"; notes?: string }): Promise<ChartProfile> {
  const birthTimeAccuracy = payload.birth_time_accuracy ?? (payload.birth_time?.trim() ? "exact" : "unknown");
  const response = await apiFetch("/api/charts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...payload,
      birth_time_accuracy: birthTimeAccuracy,
    }),
  });
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 403) {
      throw new Error("РќРµС‚ РґРѕСЃС‚СѓРїР° Рє СЃРѕС…СЂР°РЅРµРЅРёСЋ: РІРѕР№РґРёС‚Рµ Р·Р°РЅРѕРІРѕ РёР»Рё РѕР±РЅРѕРІРёС‚Рµ СЃС‚СЂР°РЅРёС†Сѓ РґР»СЏ CSRF-СЃРµСЃСЃРёРё");
    }
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.profile;
}

export async function updateChartProfile(
  profileId: number,
  payload: Partial<BirthChartRequest & { display_name: string; is_self_profile?: boolean; birth_time_accuracy?: string; gender?: "male" | "female" | "unknown"; notes?: string }>,
): Promise<ChartProfile> {
  const response = await apiFetch(`/api/charts/${profileId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.profile;
}

export async function deleteChartProfile(profileId: number): Promise<void> {
  const response = await apiFetch(`/api/charts/${profileId}`, { method: "DELETE" });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error ?? "Request failed");
  }
}
export async function calculateSavedProfile(profileId: number): Promise<ChartCalculationRecord> {
  const response = await apiFetch(`/api/charts/profiles/${profileId}/calculate`, {
    method: "POST",
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? data.calculation?.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.calculation;
}

export async function listChartProfileRelationships(): Promise<ChartProfileRelationship[]> {
  const response = await apiFetch("/api/charts/profile-relationships", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.relationships ?? [];
}

export async function listChartRelationships(filters?: { chartId?: number; relationshipTypeId?: string }): Promise<ChartRelationship[]> {
  const params = new URLSearchParams();
  if (filters?.chartId) params.set("chart_id", String(filters.chartId));
  if (filters?.relationshipTypeId) params.set("relationship_type_id", filters.relationshipTypeId);
  const query = params.toString();
  const response = await apiFetch(`/api/relationships${query ? `?${query}` : ""}`, { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Request failed");
  }
  return data.relationships ?? [];
}

export async function fetchChartRelationship(relationshipId: number): Promise<ChartRelationship> {
  const response = await apiFetch(`/api/relationships/${relationshipId}`, { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Request failed");
  }
  return data.relationship;
}

export async function createChartRelationship(payload: {
  chart_a_id: number;
  chart_b_id: number;
  relationship_type_id: string;
  role_a_id: string;
  role_b_id: string;
  notes?: string;
}): Promise<ChartRelationship> {
  const response = await apiFetch("/api/relationships", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Request failed");
  }
  return data.relationship;
}

export async function updateChartRelationship(
  relationshipId: number,
  payload: {
    chart_a_id: number;
    chart_b_id: number;
    relationship_type_id: string;
    role_a_id: string;
    role_b_id: string;
    notes?: string;
  },
): Promise<ChartRelationship> {
  const response = await apiFetch(`/api/relationships/${relationshipId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Request failed");
  }
  return data.relationship;
}

export async function deleteChartRelationship(relationshipId: number): Promise<void> {
  const response = await apiFetch(`/api/relationships/${relationshipId}`, { method: "DELETE" });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error ?? "Request failed");
  }
}

export async function fetchChartProfileRelationship(relationshipId: number): Promise<ChartProfileRelationship> {
  const response = await apiFetch(`/api/charts/profile-relationships/${relationshipId}`, { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.relationship;
}

export async function listIncomingChartProfileRelationshipRequests(): Promise<ChartProfileRelationship[]> {
  const response = await apiFetch("/api/charts/profile-relationships/inbox", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.relationships ?? [];
}

export async function upsertChartProfileRelationship(payload: {
  profile_id: number;
  related_profile_id: number;
  role: string;
  link_status?: string;
  requested_user_id?: number;
  requested_username?: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}): Promise<ChartProfileRelationship> {
  const response = await apiFetch("/api/charts/profile-relationships", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.relationship;
}

export async function updateChartProfileRelationshipRequest(
  relationshipId: number,
  action: "accept" | "decline" | "block",
  acceptedProfileId?: number,
): Promise<ChartProfileRelationship> {
  const response = await apiFetch(`/api/charts/profile-relationships/${relationshipId}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action,
      ...(acceptedProfileId ? { accepted_profile_id: acceptedProfileId } : {}),
    }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? "Р—Р°РїСЂРѕСЃ РЅРµ РІС‹РїРѕР»РЅРµРЅ");
  }
  return data.relationship;
}
