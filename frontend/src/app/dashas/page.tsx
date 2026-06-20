"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { calculateSavedProfile, listChartProfiles, type ChartCalculationRecord, type ChartProfile, type DashaPeriod } from "@/lib/api";

type SelectedEntity = {
  title: string;
  kind: "mahadasha" | "antardasha" | "system";
  period?: DashaPeriod;
  parentLord?: string;
};

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

function selectCurrentPeriod(periods: DashaPeriod[]) {
  const now = new Date();
  return periods.find((period) => containsDate(period, now)) ?? periods[0] ?? null;
}

function getMahadashas(calculation: ChartCalculationRecord | null) {
  return calculation?.result.dashas?.vimshottari?.mahadashas ?? [];
}

export default function DashasPage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<number | null>(null);
  const [calculation, setCalculation] = useState<ChartCalculationRecord | null>(null);
  const [activeMahadasha, setActiveMahadasha] = useState<DashaPeriod | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<SelectedEntity>({ title: "Вимшоттари", kind: "system" });
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

  useEffect(() => {
    if (!activeProfileId) return;
    let cancelled = false;
    setLoadingCalculation(true);
    setStatus("Загружаю периоды Вимшоттари...");
    calculateSavedProfile(activeProfileId)
      .then((record) => {
        if (cancelled) return;
        const mahadashas = getMahadashas(record);
        const current = selectCurrentPeriod(mahadashas);
        setCalculation(record);
        setActiveMahadasha(current);
        setSelectedEntity(current ? { title: `${periodLabel(current)} махадаша`, kind: "mahadasha", period: current } : { title: "Вимшоттари", kind: "system" });
        setStatus(mahadashas.length ? "" : "Для карты пока нет расчёта Вимшоттари.");
      })
      .catch((error) => {
        if (cancelled) return;
        setCalculation(null);
        setActiveMahadasha(null);
        setStatus(error instanceof Error ? error.message : "Не удалось загрузить расчёт даш.");
      })
      .finally(() => {
        if (!cancelled) setLoadingCalculation(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeProfileId]);

  const activeProfile = profiles.find((profile) => profile.id === activeProfileId) ?? null;
  const vimshottari = calculation?.result.dashas?.vimshottari ?? null;
  const mahadashas = useMemo(() => getMahadashas(calculation), [calculation]);
  const selectedAntardashas = activeMahadasha?.antardashas ?? [];
  const currentAntardasha = selectCurrentPeriod(selectedAntardashas);

  function selectMahadasha(period: DashaPeriod) {
    setActiveMahadasha(period);
    setSelectedEntity({ title: `${periodLabel(period)} махадаша`, kind: "mahadasha", period });
  }

  function selectAntardasha(period: DashaPeriod) {
    setSelectedEntity({ title: `${periodLabel(period)} антардаша`, kind: "antardasha", period, parentLord: activeMahadasha?.lord });
  }

  return (
    <ProductShell active="timeline">
      <header className="product-page-head">
        <div>
          <h1>Даши</h1>
          <p>Вимшоттари по сохранённой карте: махадаши, антардаши и общий инспектор периода.</p>
        </div>
      </header>

      <section className="product-page-card dasha-workbench-shell" aria-label="Рабочее место даш">
        <div className="dasha-toolbar">
          <label>
            Карта
            <select value={activeProfileId ?? ""} onChange={(event) => setActiveProfileId(Number(event.target.value) || null)}>
              {profiles.map((profile) => (
                <option key={profile.id} value={profile.id}>{profile.display_name}</option>
              ))}
            </select>
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

        {status ? <div className="product-status">{status}</div> : null}

        <div className="dasha-period-tree" aria-busy={loadingCalculation}>
          <section className="dasha-period-panel" aria-label="Махадаши">
            <div className="source-explorer-card-head">
              <span>Уровень 1</span>
              <strong>Махадаша</strong>
            </div>
            <div className="dasha-period-list">
              {mahadashas.map((period) => {
                const active = activeMahadasha?.starts_at === period.starts_at && activeMahadasha?.lord === period.lord;
                return (
                  <button
                    type="button"
                    className={`dasha-period-row${active ? " active" : ""}`}
                    key={`${period.lord}-${period.starts_at}`}
                    aria-pressed={active}
                    onClick={() => selectMahadasha(period)}
                  >
                    <strong>{periodLabel(period)}</strong>
                    <span>{formatDate(period.starts_at)} — {formatDate(period.ends_at)}</span>
                    <em>{period.duration_years.toFixed(2)} лет</em>
                  </button>
                );
              })}
            </div>
          </section>

          <section className="dasha-period-panel" aria-label="Антардаши">
            <div className="source-explorer-card-head">
              <span>Уровень 2</span>
              <strong>Антардаша</strong>
            </div>
            <div className="dasha-period-list">
              {selectedAntardashas.map((period) => {
                const active = currentAntardasha?.starts_at === period.starts_at && currentAntardasha?.lord === period.lord;
                return (
                  <button
                    type="button"
                    className={`dasha-period-row${active ? " current" : ""}`}
                    key={`${period.parent_lord ?? activeMahadasha?.lord}-${period.lord}-${period.starts_at}`}
                    aria-pressed={selectedEntity.period?.starts_at === period.starts_at && selectedEntity.kind === "antardasha"}
                    onClick={() => selectAntardasha(period)}
                  >
                    <strong>{periodLabel(period)}</strong>
                    <span>{formatDate(period.starts_at)} — {formatDate(period.ends_at)}</span>
                    <em>{period.duration_years.toFixed(2)} лет</em>
                  </button>
                );
              })}
              {!selectedAntardashas.length ? <p className="dasha-empty-note">Выберите махадашу с рассчитанными антардашами.</p> : null}
            </div>
          </section>

          <aside className="dasha-inspector" aria-label="Объяснение">
            <div className="source-explorer-card-head">
              <span>Объяснение</span>
              <strong>EntityInspector</strong>
            </div>
            <h2>{selectedEntity.title}</h2>
            {selectedEntity.period ? (
              <dl>
                <div><dt>Граха</dt><dd>{periodLabel(selectedEntity.period)}</dd></div>
                {selectedEntity.parentLord ? <div><dt>Внутри</dt><dd>{selectedEntity.parentLord}</dd></div> : null}
                <div><dt>Начало</dt><dd>{formatDate(selectedEntity.period.starts_at)}</dd></div>
                <div><dt>Конец</dt><dd>{formatDate(selectedEntity.period.ends_at)}</dd></div>
                <div><dt>Длительность</dt><dd>{selectedEntity.period.duration_years.toFixed(2)} лет</dd></div>
              </dl>
            ) : (
              <p>Нажмите махадашу или антардашу, чтобы увидеть параметры периода в одном общем инспекторе.</p>
            )}
          </aside>
        </div>
      </section>
    </ProductShell>
  );
}