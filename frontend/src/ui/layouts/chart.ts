import type { LayoutManifest } from "./types";

export const chartSimpleLayout: LayoutManifest = {
  id: "layout.chart.simple",
  page: "chartWorkbench",
  mode: "simple",
  regions: {
    header: ["block.profileHeader", "block.modeSwitcher"],
    main: ["block.chart.main", "block.panel.simpleSummary", "block.panel.currentDasha"],
    bottom: ["block.table.grahas.simple", "block.table.bhavas.simple"],
    inspector: ["block.panel.entityInspector"],
  },
};

export const chartExpertLayout: LayoutManifest = {
  id: "layout.chart.expert",
  page: "chartWorkbench",
  mode: "expert",
  regions: {
    header: ["block.profileHeader", "block.chartToolbar", "block.modeSwitcher", "block.calculationPresetBadge"],
    sidebar: [
      "nav.overview",
      "nav.grahas",
      "nav.bhavas",
      "nav.vargas",
      "nav.dashas",
      "nav.yogas",
      "nav.strengths",
      "nav.transits",
      "nav.sources",
    ],
    main: ["block.chart.main", "block.chart.vargaSelector", "block.chart.displayLayerToggles"],
    bottom: ["block.table.grahas", "block.table.bhavas", "block.table.dashas"],
    inspector: ["block.panel.entityInspector"],
  },
};

export function chartLayoutForMode(mode: "simple" | "expert"): LayoutManifest {
  return mode === "expert" ? chartExpertLayout : chartSimpleLayout;
}
