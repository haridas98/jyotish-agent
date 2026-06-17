"use client";

import { useEffect, useMemo, useState } from "react";
import { normalizeExistingChart, registerCoreEntities, registerExistingChartCalculationModules } from "@/astrology";
import { calculateBirthChart, type BirthChart, type BirthChartRequest } from "@/lib/api";
import { chartLayoutForMode, LayoutRenderer, type UiMode } from "@/ui";
import { registerChartWorkbenchBlocks } from "@/ui/blocks/chart-workbench-blocks";
import "./workbench-v2.css";

const defaultPayload: BirthChartRequest = {
  birth_date: "1998-04-30",
  birth_time: "13:45",
  gender: "male",
  place_name: "Sterlitamak, Bashkortostan, RU",
  latitude: 53.6304,
  longitude: 55.9308,
  timezone: "Asia/Yekaterinburg",
  ayanamsa: "Lahiri",
  node_type: "true",
  calculation_model: "drik_siddhanta",
  house_system: "whole_sign",
  bhava_system: "whole_sign",
  varga_scheme: "parashara",
  timezone_source: "iana",
};

export default function WorkbenchV2Page() {
  const [mode, setMode] = useState<UiMode>("expert");
  const [chart, setChart] = useState<BirthChart | null>(null);
  const [activeEntityId, setActiveEntityId] = useState<string | null>("house.1");
  const [status, setStatus] = useState("Считаю карту...");

  useMemo(() => {
    registerExistingChartCalculationModules();
    registerCoreEntities();
    registerChartWorkbenchBlocks();
  }, []);

  useEffect(() => {
    let alive = true;
    setStatus("Считаю карту...");
    calculateBirthChart(defaultPayload)
      .then((result) => {
        if (!alive) return;
        setChart(result);
        setStatus("Карта рассчитана");
      })
      .catch((error) => {
        if (!alive) return;
        setStatus(error instanceof Error ? error.message : "Не удалось рассчитать карту");
      });
    return () => {
      alive = false;
    };
  }, []);

  const normalized = useMemo(
    () =>
      chart
        ? normalizeExistingChart(chart, [
            "calc.birthData",
            "calc.geo",
            "calc.planetPositions",
            "calc.houses",
            "calc.dignities",
            "calc.nakshatras",
            "calc.panchanga",
            "calc.varga.D1",
            "calc.varga.D9",
            "calc.varga.D10",
            "calc.varga.D12",
            "calc.varga.D60",
            "calc.vimshottari",
            "calc.yogas",
            "calc.shadBala",
            "calc.ashtakavarga",
          ])
        : null,
    [chart],
  );
  const layout = chartLayoutForMode(mode);

  return (
    <main className="workbench-v2-page">
      <div className="v2-topbar">
        <div>
          <strong>Jyotish Workbench v2</strong>
          <span>{status}</span>
        </div>
        <div className="v2-mode-switch">
          <button type="button" className={mode === "simple" ? "active" : ""} onClick={() => setMode("simple")}>
            Простой
          </button>
          <button type="button" className={mode === "expert" ? "active" : ""} onClick={() => setMode("expert")}>
            Астролог
          </button>
        </div>
      </div>

      <LayoutRenderer layout={layout} chart={normalized} mode={mode} activeEntityId={activeEntityId} setActiveEntityId={setActiveEntityId} />
    </main>
  );
}
