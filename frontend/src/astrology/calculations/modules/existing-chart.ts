import { registerCalculation } from "../registry";

export function registerExistingChartCalculationModules() {
  registerCalculation({
    id: "calc.birthData",
    label: "Birth data",
    dependsOn: [],
    compute: (ctx) => ctx.chart?.birth ?? null,
  });

  registerCalculation({
    id: "calc.geo",
    label: "Geography and timezone",
    dependsOn: ["calc.birthData"],
    compute: (ctx) => ctx.chart?.place ?? null,
  });

  registerCalculation({
    id: "calc.planetPositions",
    label: "Planet positions",
    dependsOn: ["calc.birthData", "calc.geo"],
    compute: (ctx) => ctx.chart?.grahas ?? [],
  });

  registerCalculation({
    id: "calc.houses",
    label: "Houses",
    dependsOn: ["calc.planetPositions"],
    compute: (ctx) => ctx.chart?.houses ?? [],
  });

  registerCalculation({
    id: "calc.nakshatras",
    label: "Nakshatras",
    dependsOn: ["calc.planetPositions"],
    compute: (ctx) => ctx.chart?.grahas ?? [],
  });

  registerCalculation({
    id: "calc.panchanga",
    label: "Panchanga",
    dependsOn: ["calc.planetPositions", "calc.nakshatras"],
    compute: (ctx) => ctx.chart?.panchanga ?? null,
  });

  registerCalculation({
    id: "calc.vimshottari",
    label: "Vimshottari Dasha",
    dependsOn: ["calc.nakshatras"],
    compute: (ctx) => ctx.chart?.dashas?.vimshottari ?? null,
  });

  registerCalculation({
    id: "calc.yogas",
    label: "Yogas",
    dependsOn: ["calc.planetPositions", "calc.houses"],
    compute: (ctx) => ctx.chart?.classical?.yogas ?? null,
  });

  registerCalculation({
    id: "calc.dignities",
    label: "Dignities",
    dependsOn: ["calc.planetPositions"],
    compute: (ctx) => ctx.chart?.grahas.map((graha) => ({ body: graha.body, dignity: graha.dignity ?? null })) ?? [],
  });

  registerCalculation({
    id: "calc.shadBala",
    label: "Shad Bala",
    dependsOn: ["calc.planetPositions"],
    compute: (ctx) => ctx.chart?.classical?.shadbala ?? null,
  });

  registerCalculation({
    id: "calc.ashtakavarga",
    label: "Ashtakavarga",
    dependsOn: ["calc.planetPositions"],
    compute: (ctx) => ctx.chart?.classical?.ashtakavarga ?? null,
  });

  for (const code of ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D20", "D60"] as const) {
    registerCalculation({
      id: `calc.varga.${code}`,
      label: `${code} varga`,
      dependsOn: ["calc.planetPositions"],
      compute: (ctx) => ctx.chart?.vargas?.[code] ?? null,
    });
  }
}
