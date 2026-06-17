import type { ComponentType, ReactNode } from "react";
import type { CalculationId, NormalizedChartResult } from "@/astrology";

export type UiMode = "simple" | "expert";
export type LayoutRegion = "header" | "sidebar" | "main" | "bottom" | "inspector";

export type ViewBlockProps = {
  chart: NormalizedChartResult | null;
  mode: UiMode;
  activeEntityId: string | null;
  setActiveEntityId: (entityId: string) => void;
};

export type ViewBlock = {
  id: string;
  title: string;
  requires: CalculationId[];
  supportedModes: UiMode[];
  allowedRegions: LayoutRegion[];
  component: ComponentType<ViewBlockProps>;
};

export type MissingBlockProps = {
  title: string;
  missing: CalculationId[];
};

export type BlockChildrenProps = {
  children: ReactNode;
};
