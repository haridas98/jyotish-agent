import type { BirthChart } from "@/lib/api";
import { getCalculationModule } from "./registry";
import type { CalculationId, CalculationPreset, CalculationStore, NormalizedChartResult } from "./types";

export function normalizeExistingChart(
  chart: BirthChart,
  requested: CalculationId[],
  preset: CalculationPreset = {},
): NormalizedChartResult {
  const store: CalculationStore = {};
  const visited = new Set<CalculationId>();

  function run(id: CalculationId) {
    if (visited.has(id)) return;
    const module = getCalculationModule(id);
    module.dependsOn.forEach(run);
    store[id] = module.compute({ chart, preset }, store);
    visited.add(id);
  }

  requested.forEach(run);

  return {
    chartId: chart.birth?.utc_datetime ?? "active-chart",
    sourceChart: chart,
    preset,
    store,
    warnings: [],
  };
}
