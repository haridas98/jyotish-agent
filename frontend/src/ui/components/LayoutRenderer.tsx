"use client";

import type { NormalizedChartResult } from "@/astrology";
import type { UiMode } from "@/ui/blocks/types";
import { getBlock } from "@/ui/blocks/registry";
import type { LayoutManifest } from "@/ui/layouts/types";

export function LayoutRenderer({
  layout,
  chart,
  mode,
  activeEntityId,
  setActiveEntityId,
}: {
  layout: LayoutManifest;
  chart: NormalizedChartResult | null;
  mode: UiMode;
  activeEntityId: string | null;
  setActiveEntityId: (entityId: string) => void;
}) {
  return (
    <div className="v2-layout" data-mode={mode}>
      {(["header", "sidebar", "main", "bottom", "inspector"] as const).map((region) => {
        const blockIds = layout.regions[region] ?? [];
        if (!blockIds.length) return null;
        return (
          <section key={region} className={`v2-region v2-region-${region}`}>
            {blockIds.map((blockId) => {
              const block = getBlock(blockId);
              if (!block) {
                return <MissingBlock key={blockId} title={blockId} missing={[]} />;
              }
              const missing = chart ? block.requires.filter((calcId) => !(calcId in chart.store)) : block.requires;
              if (missing.length) {
                return <MissingBlock key={blockId} title={block.title} missing={missing} />;
              }
              const Component = block.component;
              return (
                <Component
                  key={block.id}
                  chart={chart}
                  mode={mode}
                  activeEntityId={activeEntityId}
                  setActiveEntityId={setActiveEntityId}
                />
              );
            })}
          </section>
        );
      })}
    </div>
  );
}

function MissingBlock({ title, missing }: { title: string; missing: string[] }) {
  return (
    <div className="v2-block v2-missing">
      <strong>{title}</strong>
      {missing.length ? <small>Расчётные данные ещё не готовы.</small> : <small>Раздел временно недоступен.</small>}
    </div>
  );
}
