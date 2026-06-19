"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { ProductShell } from "@/app/product-shell";
import { buildD1WorkbenchModel } from "@/astrology/d1-workbench";
import {
  fetchChartProfile,
  fetchD1ChartWorkbench,
  fetchJyotishSettings,
  type ChartProfile,
  type ChartWorkbenchScope,
  type D1WorkbenchApiResponse,
  type JyotishUserSettings,
} from "@/lib/api";
import { D1ChartWorkbench, D1ChartWorkbenchShell } from "@/ui";

function profileIdFromParams(value: string | string[] | undefined) {
  const raw = Array.isArray(value) ? value[0] : value;
  const parsed = Number(raw);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

export default function ChartDetailPage() {
  const params = useParams<{ id: string }>();
  const profileId = profileIdFromParams(params.id);
  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [settings, setSettings] = useState<JyotishUserSettings | null>(null);
  const [workbench, setWorkbench] = useState<D1WorkbenchApiResponse | null>(null);
  const [scope, setScope] = useState<ChartWorkbenchScope>("d1");
  const [status, setStatus] = useState("Открываю карту D1...");

  useEffect(() => {
    let mounted = true;
    async function load() {
      if (!profileId) {
        setStatus("Карта не найдена.");
        return;
      }
      try {
        const [profileRow, settingsRow, workbenchRow] = await Promise.all([
          fetchChartProfile(profileId),
          fetchJyotishSettings(),
          fetchD1ChartWorkbench(profileId, scope),
        ]);
        if (!mounted) return;
        setProfile(profileRow);
        setSettings(settingsRow);
        setWorkbench(workbenchRow);
        setStatus(workbenchRow.calculation ? "" : "Расчёт ещё не сохранён.");
      } catch (error) {
        if (!mounted) return;
        setStatus(error instanceof Error ? error.message : "Не удалось открыть карту D1.");
      }
    }
    void load();
    return () => {
      mounted = false;
    };
  }, [profileId, scope]);

  const model = useMemo(() => {
    if (!profile || !workbench) return null;
    const scopeId = workbench.scope === "d9" ? "D9" : "D1";
    return buildD1WorkbenchModel(profile, settings, workbench.calculation, scopeId);
  }, [profile, settings, workbench]);

  return (
    <ProductShell active="charts">
      <div className="chart-detail-static-shell" aria-hidden={Boolean(model)}>
        <span>Карта D1</span>
        <span>Стиль карты</span>
        <span>Режим</span>
        <span>Объяснение</span>
      </div>
      {model ? (
        <D1ChartWorkbench key={model.scopeId} model={model} status={status} onScopeChange={(nextScope) => setScope(nextScope === "D9" ? "d9" : "d1")} />
      ) : (
        <D1ChartWorkbenchShell status={status} />
      )}
    </ProductShell>
  );
}