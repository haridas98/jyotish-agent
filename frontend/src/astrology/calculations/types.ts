import type { BirthChart, BirthChartRequest } from "@/lib/api";

export type CalculationId =
  | "calc.birthData"
  | "calc.geo"
  | "calc.ayanamsha"
  | "calc.planetPositions"
  | "calc.houses"
  | "calc.dignities"
  | "calc.nakshatras"
  | "calc.panchanga"
  | "calc.varga.D1"
  | "calc.varga.D2"
  | "calc.varga.D3"
  | "calc.varga.D7"
  | "calc.varga.D9"
  | "calc.varga.D10"
  | "calc.varga.D12"
  | "calc.varga.D20"
  | "calc.varga.D60"
  | "calc.vimshottari"
  | "calc.yogas"
  | "calc.shadBala"
  | "calc.ashtakavarga"
  | "calc.arudhas"
  | "calc.argala"
  | "calc.grahaDrishti"
  | "calc.rashiDrishti"
  | "calc.transits";

export type ValidationResult = {
  ok: boolean;
  warnings?: CalculationWarning[];
  errors?: string[];
};

export type CalculationWarning = {
  code: string;
  message: string;
  severity: "info" | "warning" | "critical";
  entityIds?: string[];
};

export type CalculationPreset = {
  ayanamsha?: string;
  nodeMode?: "true" | "mean";
  houseSystem?: string;
  vargaScheme?: string;
  dashaYear?: "solar" | "savana" | "custom";
  source?: "user" | "profile" | "default";
};

export type CalculationContext = {
  request?: BirthChartRequest;
  chart?: BirthChart;
  preset?: CalculationPreset;
};

export type CalculationStore = Partial<Record<CalculationId, unknown>>;

export interface CalculationModule<TOutput = unknown> {
  id: CalculationId;
  label: string;
  dependsOn: CalculationId[];
  compute: (ctx: CalculationContext, deps: CalculationStore) => TOutput;
  validate?: (output: TOutput) => ValidationResult;
}

export type NormalizedChartResult = {
  chartId: string;
  sourceChart: BirthChart;
  preset: CalculationPreset;
  store: CalculationStore;
  warnings: CalculationWarning[];
};
