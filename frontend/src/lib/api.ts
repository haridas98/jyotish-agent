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

export type BirthChartRequest = {
  birth_date: string;
  birth_time: string;
  place_name: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
};

export type GrahaPosition = {
  body: string;
  longitude: number;
  latitude: number | null;
  speed_longitude: number | null;
  rashi: string;
  nakshatra: string;
  pada: number;
  navamsa: string;
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
  yoga?: {
    number: number;
    name: string;
  };
  karana?: {
    name: string;
  };
};

export type DashaPeriod = {
  lord: string;
  level: number;
  starts_at: string;
  ends_at: string;
  duration_years: number;
  sequence_index: number;
};

export type BirthChart = {
  calculation_version: string;
  birth: {
    date: string;
    time: string;
    timezone: string;
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
  grahas: GrahaPosition[];
  ascendant: GrahaPosition | null;
  houses: HousePlacement[];
  vargas?: {
    D9?: VargaChart;
  };
  panchanga: Panchanga;
  dashas?: {
    vimshottari?: {
      system: string;
      level: string;
      year_length_days: number;
      mahadashas: DashaPeriod[];
    };
  };
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

export type PersonSummary = {
  birth_context: SummaryItem[];
  core_factors: SummaryItem[];
  graha_houses: GrahaHouseSummary[];
  panchanga: SummaryItem[];
  dasha: {
    birth_mahadasha_lord: string | null;
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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8100";

export async function fetchZodiacPlacement(longitude: number): Promise<ZodiacPlacement> {
  const response = await fetch(
    `${API_BASE_URL}/api/calculations/zodiac-placement?longitude=${encodeURIComponent(longitude)}`,
    { cache: "no-store" },
  );

  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  return response.json();
}

export async function fetchEphemerisStatus(): Promise<EphemerisStatus> {
  const response = await fetch(`${API_BASE_URL}/api/calculations/ephemeris/status`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  return response.json();
}

export async function calculateBirthChart(payload: BirthChartRequest): Promise<BirthChart> {
  const response = await fetch(`${API_BASE_URL}/api/calculations/birth-chart`, {
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

export async function generateBirthReport(payload: BirthChartRequest): Promise<BirthReport> {
  const response = await fetch(`${API_BASE_URL}/api/reports/birth-chart`, {
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
  const response = await fetch(`${API_BASE_URL}/api/places/search?q=${encodeURIComponent(query)}`, {
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
  const response = await fetch(`${API_BASE_URL}/api/sources/vl/search?q=${encodeURIComponent(query)}`, {
    cache: "no-store",
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? `API returned ${response.status}`);
  }

  return data.items ?? [];
}
