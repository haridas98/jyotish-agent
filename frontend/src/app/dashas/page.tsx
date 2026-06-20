"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { calculateSavedProfile, listChartProfiles, type ChartCalculationRecord, type ChartProfile, type DashaPeriod } from "@/lib/api";

type DashaViewMode = "tree" | "table" | "timeline";
type DashaLevel = "mahadasha" | "antardasha" | "pratyantardasha";

type SelectedEntity = {
  title: string;
  kind: DashaLevel | "system";
  period?: DashaPeriod;
  parentLord?: string;
  mahadashaLord?: string;
};

function todayInputValue() {
  return new Date().toISOString().slice(0, 10);
}

function controlDateValue(value: string) {
  const date = new Date(`${value || todayInputValue()}T12:00:00`);
  return Number.isNaN(date.getTime()) ? new Date() : date;
}

function formatProfileMeta(profile: ChartProfile) {
  const time = profile.birth_time ? profile.birth_time.slice(0, 5) : "время неизвестно";
  return `${profile.birth_date} · ${time} · ${profile.place.label}`;
}

function formatDate(value: string) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("ru-RU", { year: "numeric", month: "2-digit", day: "2-digit" });
}

function periodLabel(period: DashaPeriod) {
  return period.name || period.lord;
}

function containsDate(period: DashaPeriod, at: Date) {
  const start = new Date(period.starts_at).getTime();
  const end = new Date(period.ends_at).getTime();
  const value = at.getTime();
  return Number.isFinite(start) && Number.isFinite(end) && value >= start && value < end;
}

function selectCurrentPeriod(periods: DashaPeriod[], at: Date) {
  return periods.find((period) => containsDate(period, at)) ?? periods[0] ?? null;
}

function getMahadashas(calculation: ChartCalculationRecord | null) {
  return calculation?.result.dashas?.vimshottari?.mahadashas ?? [];
}

function periodBoundary(period: DashaPeriod) {
  return `${formatDate(period.starts_at)} — ${formatDate(period.ends_at)}`;
}

function flattenPeriods(mahadashas: DashaPeriod[]) {
  return mahadashas.flatMap((mahadasha) => [
    { level: "Махадаша", period: mahadasha, parent: "" },
    ...(mahadasha.antardashas ?? []).flatMap((antardasha) => [
      { level: "Антардаша", period: antardasha, parent: mahadasha.lord },
      ...(antardasha.pratyantardashas ?? []).map((pratyantardasha) => ({
        level: "Пратьянтардаша",
        period: pratyantardasha,
        parent: `${mahadasha.lord} / ${antardasha.lord}`,
      })),
    ]),
  ]);
}

function timelineWidth(period: DashaPeriod, root: DashaPeriod | null) {
  if (!root) return "0%";
  const rootStart = new Date(root.starts_at).getTime();
  const rootEnd = new Date(root.ends_at).getTime();
  const start = new Date(period.starts_at).getTime();
  const end = new Date(period.ends_at).getTime();
  const total = Math.max(rootEnd - rootStart, 1);
  const width = Math.max(((end - start) / total) * 100, 1.5);
  return `${Math.min(width, 100).toFixed(2)}%`;
}

export default function DashasPage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<number | null>(null);
  const [calculation, setCalculation] = useState<ChartCalculationRecord | null>(null);
  const [activeMahadasha, setActiveMahadasha] = useState<DashaPeriod | null>(null);
  const [activeAntardasha, setActiveAntardasha] = useState<DashaPeriod | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<SelectedEntity>({ title: "Вимшоттари", kind: "system" });
  const [viewMode, setViewMode] = useState<DashaViewMode>("tree");
  const [controlDate, setControlDate] = useState(todayInputValue());
  const [collapsedLevels, setCollapsedLevels] = useState<Record<DashaLevel, boolean>>({ mahadasha: false, antardasha: false, pratyantardasha: false });
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [loadingCalculation, setLoadingCalculation] = useState(false);

  const loadProfiles = useCallback(async () => {
    try {
      const rows = await listChartProfiles();
      setProfiles(rows);
      setStatus(rows.length ? "" : "Сохранённых карт пока нет.");
      setActiveProfileId((current) => current ?? rows[0]?.id ?? null);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось загрузить карты.");
    }
  }, []);

  useEffect(() => {
    void loadProfiles();
  }, [loadProfiles]);

  const jumpToCurrentPeriod = useCallback((record: ChartCalculationRecord | null = calculation, dateValue = controlDate) => {
    const mahadashas = getMahadashas(record);
    const at = controlDateValue(dateValue);
    const currentMd = selectCurrentPeriod(mahadashas, at);
    const currentAd = selectCurrentPeriod(currentMd?.antardashas ?? [], at);
    const currentPd = selectCurrentPeriod(currentAd?.pratyantardashas ?? [], at);
    setActiveMahadasha(currentMd);
    setActiveAntardasha(currentAd);
    setSelectedEntity(
      currentPd
        ? { title: `${periodLabel(currentPd)} пратьянтардаша`, kind: "pratyantardasha", period: currentPd, parentLord: currentAd?.lord, mahadashaLord: currentMd?.lord }
        : currentAd
          ? { title: `${periodLabel(currentAd)} антардаша`, kind: "antardasha", period: currentAd, parentLord: currentMd?.lord }
          : currentMd
            ? { title: `${periodLabel(currentMd)} махадаша`, kind: "mahadasha", period: currentMd }
            : { title: "Вимшоттари", kind: "system" },
    );
  }, [calculation, controlDate]);

  useEffect(() => {
    if (!activeProfileId) return;
    let cancelled = false;
    setLoadingCalculation(true);
    setStatus("Загружаю периоды Вимшоттари...");
    calculateSavedProfile(activeProfileId)
      .then((record) => {
        if (cancelled) return;
        const mahadashas = getMahadashas(record);
        setCalculation(record);
        jumpToCurrentPeriod(record, controlDate);
        setStatus(mahadashas.length ? "" : "Для карты пока нет расчёта Вимшоттари.");
      })
      .catch((error) => {
        if (cancelled) return;
        setCalculation(null);
        setActiveMahadasha(null);
        setActiveAntardasha(null);
        setStatus(error instanceof Error ? error.message : "Не удалось загрузить расчёт даш.");
      })
      .finally(() => {
        if (!cancelled) setLoadingCalculation(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeProfileId, controlDate, jumpToCurrentPeriod]);

  const activeProfile = profiles.find((profile) => profile.id === activeProfileId) ?? null;
  const vimshottari = calculation?.result.dashas?.vimshottari ?? null;
  const mahadashas = useMemo(() => getMahadashas(calculation), [calculation]);
  const selectedAntardashas = activeMahadasha?.antardashas ?? [];
  const selectedPratyantardashas = activeAntardasha?.pratyantardashas ?? [];
  const allPeriods = useMemo(() => flattenPeriods(mahadashas), [mahadashas]);

  function toggleLevel(level: DashaLevel) {
    setCollapsedLevels((current) => ({ ...current, [level]: !current[level] }));
  }

  function selectMahadasha(period: DashaPeriod) {
    const at = controlDateValue(controlDate);
    const nextAntardasha = selectCurrentPeriod(period.antardashas ?? [], at);
    setActiveMahadasha(period);
    setActiveAntardasha(nextAntardasha);
    setSelectedEntity({ title: `${periodLabel(period)} махадаша`, kind: "mahadasha", period });
  }

  function selectAntardasha(period: DashaPeriod) {
    setActiveAntardasha(period);
    setSelectedEntity({ title: `${periodLabel(period)} антардаша`, kind: "antardasha", period, parentLord: activeMahadasha?.lord });
  }

  function selectPratyantardasha(period: DashaPeriod) {
    setSelectedEntity({
      title: `${periodLabel(period)} пратьянтардаша`,
      kind: "pratyantardasha",
      period,
      parentLord: activeAntardasha?.lord,
      mahadashaLord: activeMahadasha?.lord,
    });
  }

  return (
    <ProductShell active="timeline">
      <header className="product-page-head">
        <div>
          <h1>Даши</h1>
          <p>Вимшоттари по сохранённой карте: дерево, таблица, таймлайн и контрольная дата.</p>
        </div>
      </header>

      <section className="product-page-card dasha-workbench-shell" aria-label="Рабочее место даш">
        <div className="dasha-toolbar">
          <label>
            Карта
            <select value={activeProfileId ?? ""} onChange={(event) => setActiveProfileId(Number(event.target.value) || null)}>
              {profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.display_name}</option>)}
            </select>
          </label>
          <label>
            Контрольная дата
            <input type="date" value={controlDate} onChange={(event) => setControlDate(event.target.value)} />
          </label>
          <div>
            <strong>Вимшоттари</strong>
            <span>{activeProfile ? formatProfileMeta(activeProfile) : "Выберите сохранённую карту"}</span>
          </div>
          <div>
            <strong>{vimshottari?.year_length_days ?? 365.25} дней</strong>
            <span>год даши · границы start-inclusive / end-exclusive</span>
          </div>
        </div>

        <div className="dasha-control-bar" aria-label="Управление дашами">
          {(["tree", "table", "timeline"] as const).map((mode) => (
            <button key={mode} type="button" className={viewMode === mode ? "active" : ""} aria-pressed={viewMode === mode} onClick={() => setViewMode(mode)}>
              {mode === "tree" ? "Дерево" : mode === "table" ? "Таблица" : "Таймлайн"}
            </button>
          ))}
          <button type="button" onClick={() => jumpToCurrentPeriod()}>К текущему периоду</button>
          {(["mahadasha", "antardasha", "pratyantardasha"] as const).map((level) => (
            <button key={level} type="button" aria-pressed={collapsedLevels[level]} onClick={() => toggleLevel(level)}>
              {collapsedLevels[level] ? "Показать" : "Свернуть"} {level === "mahadasha" ? "MD" : level === "antardasha" ? "AD" : "PD"}
            </button>
          ))}
        </div>

        {status ? <div className="product-status">{status}</div> : null}

        {viewMode === "tree" ? (
          <div className="dasha-period-tree" aria-busy={loadingCalculation}>
            {!collapsedLevels.mahadasha ? (
              <section className="dasha-period-panel" aria-label="Махадаши">
                <div className="source-explorer-card-head"><span>Уровень 1</span><strong>Махадаша</strong></div>
                <div className="dasha-period-list">
                  {mahadashas.map((period) => {
                    const active = activeMahadasha?.starts_at === period.starts_at && activeMahadasha?.lord === period.lord;
                    return <PeriodButton key={`${period.lord}-${period.starts_at}`} period={period} active={active} onClick={() => selectMahadasha(period)} />;
                  })}
                </div>
              </section>
            ) : null}

            {!collapsedLevels.antardasha ? (
              <section className="dasha-period-panel" aria-label="Антардаши">
                <div className="source-explorer-card-head"><span>Уровень 2</span><strong>Антардаша</strong></div>
                <div className="dasha-period-list">
                  {selectedAntardashas.map((period) => {
                    const active = activeAntardasha?.starts_at === period.starts_at && activeAntardasha?.lord === period.lord;
                    return <PeriodButton key={`${period.parent_lord ?? activeMahadasha?.lord}-${period.lord}-${period.starts_at}`} period={period} active={active} onClick={() => selectAntardasha(period)} />;
                  })}
                  {!selectedAntardashas.length ? <p className="dasha-empty-note">Выберите махадашу с рассчитанными антардашами.</p> : null}
                </div>
              </section>
            ) : null}

            {!collapsedLevels.pratyantardasha ? (
              <section className="dasha-period-panel" aria-label="Пратьянтардаши">
                <div className="source-explorer-card-head"><span>Уровень 3</span><strong>Пратьянтардаша</strong></div>
                <div className="dasha-period-list">
                  {selectedPratyantardashas.map((period) => {
                    const active = selectedEntity.kind === "pratyantardasha" && selectedEntity.period?.starts_at === period.starts_at && selectedEntity.period?.lord === period.lord;
                    return <PeriodButton key={`${period.parent_lord ?? activeAntardasha?.lord}-${period.lord}-${period.starts_at}`} period={period} active={active} onClick={() => selectPratyantardasha(period)} />;
                  })}
                  {!selectedPratyantardashas.length ? <p className="dasha-empty-note">Выберите антардашу с рассчитанными пратьянтардашами.</p> : null}
                </div>
              </section>
            ) : null}

            <DashaInspector selectedEntity={selectedEntity} />
          </div>
        ) : null}

        {viewMode === "table" ? (
          <div className="dasha-table-wrap">
            <table className="dasha-period-table">
              <thead><tr><th>Уровень</th><th>Граха</th><th>Контекст</th><th>Границы</th><th>Лет</th></tr></thead>
              <tbody>
                {allPeriods.map((row) => (
                  <tr key={`${row.level}-${row.period.lord}-${row.period.starts_at}`}>
                    <td>{row.level}</td><td>{periodLabel(row.period)}</td><td>{row.parent || "—"}</td><td className="dasha-boundary">{periodBoundary(row.period)}</td><td>{row.period.duration_years.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}

        {viewMode === "timeline" ? (
          <div className="dasha-timeline" aria-label="Таймлайн периодов">
            {mahadashas.map((period) => (
              <button type="button" key={`${period.lord}-${period.starts_at}`} style={{ width: timelineWidth(period, mahadashas[0] ?? null) }} onClick={() => selectMahadasha(period)}>
                <strong>{periodLabel(period)}</strong><span className="dasha-boundary">{periodBoundary(period)}</span>
              </button>
            ))}
          </div>
        ) : null}
      </section>
    </ProductShell>
  );
}

function PeriodButton({ period, active, onClick }: { period: DashaPeriod; active: boolean; onClick: () => void }) {
  return (
    <button type="button" className={`dasha-period-row${active ? " active" : ""}`} aria-pressed={active} onClick={onClick}>
      <strong>{periodLabel(period)}</strong>
      <span className="dasha-boundary">{periodBoundary(period)}</span>
      <em>{period.duration_years.toFixed(2)} лет</em>
    </button>
  );
}

function DashaInspector({ selectedEntity }: { selectedEntity: SelectedEntity }) {
  return (
    <aside className="dasha-inspector" aria-label="Объяснение">
      <div className="source-explorer-card-head"><span>Объяснение</span><strong>EntityInspector</strong></div>
      <h2>{selectedEntity.title}</h2>
      {selectedEntity.period ? (
        <dl>
          <div><dt>Граха</dt><dd>{periodLabel(selectedEntity.period)}</dd></div>
          {selectedEntity.mahadashaLord ? <div><dt>Махадаша</dt><dd>{selectedEntity.mahadashaLord}</dd></div> : null}
          {selectedEntity.parentLord ? <div><dt>Внутри</dt><dd>{selectedEntity.parentLord}</dd></div> : null}
          <div><dt>Границы</dt><dd className="dasha-boundary">{periodBoundary(selectedEntity.period)}</dd></div>
          <div><dt>Длительность</dt><dd>{selectedEntity.period.duration_years.toFixed(2)} лет</dd></div>
        </dl>
      ) : <p>Нажмите период, чтобы увидеть параметры в одном общем инспекторе.</p>}
    </aside>
  );
}