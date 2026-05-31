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
