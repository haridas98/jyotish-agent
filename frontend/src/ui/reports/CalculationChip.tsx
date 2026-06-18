import type { CalculationId } from "@/astrology";

const calculationLabels: Record<CalculationId, string> = {
  "calc.birthData": "Данные рождения",
  "calc.geo": "Место и часовой пояс",
  "calc.ayanamsha": "Аянамша",
  "calc.planetPositions": "Планеты",
  "calc.houses": "Дома",
  "calc.dignities": "Достоинства",
  "calc.nakshatras": "Накшатры",
  "calc.panchanga": "Панчанга",
  "calc.varga.D1": "D1",
  "calc.varga.D2": "D2",
  "calc.varga.D3": "D3",
  "calc.varga.D7": "D7",
  "calc.varga.D9": "D9",
  "calc.varga.D10": "D10",
  "calc.varga.D12": "D12",
  "calc.varga.D20": "D20",
  "calc.varga.D60": "D60",
  "calc.vimshottari": "Вимшоттари",
  "calc.yogas": "Йоги",
  "calc.shadBala": "Шадбала",
  "calc.ashtakavarga": "Аштакаварга",
  "calc.arudhas": "Арудхи",
  "calc.argala": "Аргала",
  "calc.grahaDrishti": "Граха-дришти",
  "calc.rashiDrishti": "Раши-дришти",
  "calc.transits": "Транзиты",
};

export function CalculationChip({ calculationId }: { calculationId: CalculationId }) {
  return <span className="calculation-chip">{calculationLabels[calculationId]}</span>;
}
