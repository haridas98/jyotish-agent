"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { ProductShell } from "@/app/product-shell";
import { buildD1WorkbenchModel, type ChartWorkbenchScopeId } from "@/astrology/d1-workbench";
import { buildD1WorkbenchSmokeModel, D1_WORKBENCH_POLISH_STAGE, D1_WORKBENCH_SMOKE_CHART_ID, D1_WORKBENCH_SMOKE_ROUTE, D1_WORKBENCH_SMOKE_USER_STATUS } from "@/astrology/d1-workbench-smoke-fixture";
import {
  calculateSavedProfile,
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

function chartIdFromParams(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

type LoadedWorkbenchRows = {
  profileRow: ChartProfile;
  settingsRow: JyotishUserSettings | null;
  workbenchRow: D1WorkbenchApiResponse;
};

async function fetchWorkbenchRows(profileId: number, scope: ChartWorkbenchScope): Promise<LoadedWorkbenchRows> {
  const [profileRow, settingsRow, workbenchRow] = await Promise.all([
    fetchChartProfile(profileId),
    fetchJyotishSettings(),
    fetchD1ChartWorkbench(profileId, scope),
  ]);
  return { profileRow, settingsRow, workbenchRow };
}

export default function ChartDetailPage() {
  const params = useParams<{ id: string }>();
  const chartId = chartIdFromParams(params.id);
  const isSmokeDemoChart = chartId === D1_WORKBENCH_SMOKE_CHART_ID;
  const profileId = isSmokeDemoChart ? null : profileIdFromParams(params.id);
  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [settings, setSettings] = useState<JyotishUserSettings | null>(null);
  const [workbench, setWorkbench] = useState<D1WorkbenchApiResponse | null>(null);
  const [scope, setScope] = useState<ChartWorkbenchScope>("d1");
  const [status, setStatus] = useState("Открываю карту D1...");
  const [calculating, setCalculating] = useState(false);

  const applyWorkbenchRows = useCallback((rows: LoadedWorkbenchRows) => {
    setProfile(rows.profileRow);
    setSettings(rows.settingsRow);
    setWorkbench(rows.workbenchRow);
    setStatus(rows.workbenchRow.calculation ? "" : "Расчёт ещё не сохранён.");
  }, []);

  const refreshWorkbench = useCallback(async () => {
    if (!profileId) return null;
    const rows = await fetchWorkbenchRows(profileId, scope);
    applyWorkbenchRows(rows);
    return rows.workbenchRow;
  }, [applyWorkbenchRows, profileId, scope]);

  const handleRecalculate = useCallback(async () => {
    if (!profileId || calculating) return;
    setCalculating(true);
    setStatus("Пересчитываю карту...");
    try {
      await calculateSavedProfile(profileId);
      await refreshWorkbench();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось пересчитать карту.");
    } finally {
      setCalculating(false);
    }
  }, [calculating, profileId, refreshWorkbench]);

  useEffect(() => {
    let mounted = true;
    async function load() {
      if (isSmokeDemoChart) {
        setProfile(null);
        setSettings(null);
        setWorkbench(null);
        setStatus(D1_WORKBENCH_SMOKE_USER_STATUS);
        return;
      }
      if (!profileId) {
        setStatus("Карта не найдена.");
        return;
      }
      try {
        const rows = await fetchWorkbenchRows(profileId, scope);
        if (!mounted) return;
        applyWorkbenchRows(rows);
        if (!rows.workbenchRow.calculation) {
          setCalculating(true);
          setStatus("Считаю карту...");
          await calculateSavedProfile(profileId);
          const refreshedRows = await fetchWorkbenchRows(profileId, scope);
          if (!mounted) return;
          applyWorkbenchRows(refreshedRows);
        }
      } catch (error) {
        if (!mounted) return;
        setStatus(error instanceof Error ? error.message : "Не удалось открыть карту D1.");
      } finally {
        if (mounted) setCalculating(false);
      }
    }
    void load();
    return () => {
      mounted = false;
    };
  }, [applyWorkbenchRows, isSmokeDemoChart, profileId, scope]);

  const model = useMemo(() => {
    if (isSmokeDemoChart) return buildD1WorkbenchSmokeModel();
    if (!profile || !workbench) return null;
    const scopeId = workbench.scope.toUpperCase() as ChartWorkbenchScopeId;
    return buildD1WorkbenchModel(profile, settings, workbench.calculation, scopeId, workbench);
  }, [isSmokeDemoChart, profile, settings, workbench]);

  const renderedStatus = isSmokeDemoChart ? D1_WORKBENCH_SMOKE_USER_STATUS : status;

  return (
    <ProductShell active="charts">
      <div className="chart-detail-static-shell" aria-hidden={Boolean(model)}>
        <span>{D1_WORKBENCH_POLISH_STAGE}</span>
        <span>{D1_WORKBENCH_SMOKE_ROUTE}</span>
        <span>Карта D1</span>
        <span>Стиль карты</span>
        <span>Режим</span>
        <span>Объяснение</span>
        <span hidden>chart-detail-autocalculate</span>
      </div>
      {model ? (
        <D1ChartWorkbench model={model} readOnlyFixture={isSmokeDemoChart} status={renderedStatus} recalculating={calculating} onRecalculate={isSmokeDemoChart ? undefined : handleRecalculate} onScopeChange={(nextScope) => setScope(nextScope.toLowerCase() as ChartWorkbenchScope)} />
      ) : (
        <D1ChartWorkbenchShell status={renderedStatus} />
      )}
    </ProductShell>
  );
}
