import type { LayoutRegion, UiMode } from "@/ui/blocks/types";

export type LayoutManifest = {
  id: string;
  page: string;
  mode: UiMode;
  regions: Partial<Record<LayoutRegion, string[]>>;
};
