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
  timezone: string;
  place_name: string;
  latitude: number;
  longitude: number;
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
    name: string;
    latitude: number;
    longitude: number;
  };
  grahas: GrahaPosition[];
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
