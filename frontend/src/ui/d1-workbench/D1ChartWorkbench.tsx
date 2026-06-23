"use client";

import { useMemo, useState, type CSSProperties } from "react";
import type { EntityId } from "@/astrology";
import {
  type ChartWorkbenchScopeId,
  type D1ChartStyle,
  type D1DataTab,
  type D1TechnicalSummaryRow,
  type D1GrahaRow,
  type D1HouseCell,
  type D1ReaderMode,
  type D1SpecialPointRow,
  type D1TerminologyMode,
  type D1WorkbenchModel,
} from "@/astrology/d1-workbench";
import { EntityInspector } from "@/ui/components/EntityInspector";

type D1ChartWorkbenchProps = {
  model: D1WorkbenchModel;
  onRecalculate?: () => void | Promise<void>;
  onScopeChange?: (scopeId: ChartWorkbenchScopeId) => void;
  readOnlyFixture?: boolean;
  recalculating?: boolean;
  status?: string;
};

type ChartWorkbenchState = {
  scopeId: ChartWorkbenchScopeId;
  mode: D1ReaderMode;
  chartStyle: D1ChartStyle;
  density: D1DensityMode;
  activeEntityId: EntityId | null;
  activeTab: D1DataTab;
  terminologyMode: D1TerminologyMode;
  displayLayers: {
    houseNumbers: boolean;
    rashiLabels: boolean;
    grahas: boolean;
    specialPoints: boolean;
    degrees: boolean;
    nakshatras: boolean;
    padas: boolean;
    retrograde: boolean;
    dignity: boolean;
  };
};

type D1DensityMode = "comfortable" | "compact";

const NORTH_POSITIONS: Record<number, { x: number; y: number }> = {
  1: { x: 49, y: 47 },
  2: { x: 49, y: 18 },
  3: { x: 28, y: 28 },
  4: { x: 17, y: 50 },
  5: { x: 28, y: 72 },
  6: { x: 49, y: 84 },
  7: { x: 49, y: 67 },
  8: { x: 71, y: 72 },
  9: { x: 82, y: 50 },
  10: { x: 71, y: 28 },
  11: { x: 88, y: 18 },
  12: { x: 12, y: 18 },
};

const SOUTH_SIGN_GRID: Record<number, { col: number; row: number }> = {
  12: { col: 1, row: 1 },
  1: { col: 2, row: 1 },
  2: { col: 3, row: 1 },
  3: { col: 4, row: 1 },
  11: { col: 1, row: 2 },
  4: { col: 4, row: 2 },
  10: { col: 1, row: 3 },
  5: { col: 4, row: 3 },
  9: { col: 1, row: 4 },
  8: { col: 2, row: 4 },
  7: { col: 3, row: 4 },
  6: { col: 4, row: 4 },
};

const SOUTH_GRID = SOUTH_SIGN_GRID;
const SOUTH_SIGN_ORDER = [12, 1, 2, 3, 11, 4, 10, 5, 9, 8, 7, 6] as const;
const SOUTH_SIGN_LABELS: Record<number, { name: string; short: string; entityId: EntityId }> = {
  1: { name: "Mesha / Aries", short: "Ar", entityId: "rashi.Aries" as EntityId },
  2: { name: "Vrishabha / Taurus", short: "Ta", entityId: "rashi.Taurus" as EntityId },
  3: { name: "Mithuna / Gemini", short: "Ge", entityId: "rashi.Gemini" as EntityId },
  4: { name: "Karka / Cancer", short: "Ca", entityId: "rashi.Cancer" as EntityId },
  5: { name: "Simha / Leo", short: "Le", entityId: "rashi.Leo" as EntityId },
  6: { name: "Kanya / Virgo", short: "Vi", entityId: "rashi.Virgo" as EntityId },
  7: { name: "Tula / Libra", short: "Li", entityId: "rashi.Libra" as EntityId },
  8: { name: "Vrischika / Scorpio", short: "Sc", entityId: "rashi.Scorpio" as EntityId },
  9: { name: "Dhanu / Sagittarius", short: "Sg", entityId: "rashi.Sagittarius" as EntityId },
  10: { name: "Makara / Capricorn", short: "Cp", entityId: "rashi.Capricorn" as EntityId },
  11: { name: "Kumbha / Aquarius", short: "Aq", entityId: "rashi.Aquarius" as EntityId },
  12: { name: "Meena / Pisces", short: "Pi", entityId: "rashi.Pisces" as EntityId },
};

export function D1ChartWorkbenchShell({ status = "Открываю карту D1..." }: { status?: string }) {
  return (
    <section className="d1-workbench d1-workbench-shell" aria-label="Карта D1">
      <div className="d1-header">
        <div>
          <span className="d1-kicker">Карта D1</span>
          <h1>Карта D1</h1>
        </div>
        <div className="d1-toolbar" aria-label="Стиль карты и режим">
          <span>Стиль карты</span>
          <span>Режим</span>
        </div>
      </div>
      <div className="d1-shell-grid">
        <div className="d1-chart-placeholder">{status}</div>
        <aside className="v2-inspector"><h2>Объяснение</h2><p>Нажмите на дом, знак, граху или Лагну.</p></aside>
      </div>
    </section>
  );
}

export function D1ChartWorkbench({ model, onRecalculate, onScopeChange, readOnlyFixture = false, recalculating = false, status }: D1ChartWorkbenchProps) {
  const [workbenchState, setWorkbenchState] = useState<ChartWorkbenchState>({
    scopeId: model.scopeId,
    mode: model.defaults.readerMode,
    chartStyle: model.defaults.chartStyle,
    density: "comfortable",
    activeEntityId: null,
    activeTab: "grahas",
    terminologyMode: model.defaults.terminologyMode,
    displayLayers: {
      houseNumbers: true,
      rashiLabels: true,
      grahas: true,
      specialPoints: true,
      degrees: true,
      nakshatras: model.capabilities.nakshatrasAvailable,
      padas: model.capabilities.padasAvailable,
      retrograde: model.capabilities.retrogradeAvailable,
      dignity: model.capabilities.dignityAvailable,
    },
  });
  const selected = useMemo(() => selectedFacts(model, workbenchState.activeEntityId), [model, workbenchState.activeEntityId]);
  const tabIds = availableTabs(model);
  const activeScopeMeta = model.vargaScopes.find((scope) => scope.code === model.scopeId);
  const activeAccuracyGate = model.accuracyGates[model.scopeId];
  const orientationLagna = model.specialPoints.find((item) => item.code === "LAGNA")?.rashiName ?? "-";
  const activeOrientationCopy = workbenchState.chartStyle === "south" ? "South Indian: sign-fixed layout" : "North Indian: house-fixed layout";
  const activeOrientationMode = workbenchState.chartStyle === "south" ? "sign-fixed" : "house-fixed";

  const setActiveEntityId = (activeEntityId: EntityId | null) => setWorkbenchState((state) => ({ ...state, activeEntityId }));
  const setChartStyle = (chartStyle: D1ChartStyle) => setWorkbenchState((state) => ({ ...state, chartStyle }));
  const setDensity = (density: D1DensityMode) => setWorkbenchState((state) => ({ ...state, density }));
  const setMode = (mode: D1ReaderMode) => {
    if (mode === "novice" && model.expertOnlyScopes.includes(model.scopeId)) {
      onScopeChange?.("D1");
    }
    setWorkbenchState((state) => ({ ...state, mode }));
  };
  const setTerminologyMode = (terminologyMode: D1TerminologyMode) => setWorkbenchState((state) => ({ ...state, terminologyMode }));
  const setActiveTab = (activeTab: D1DataTab) => setWorkbenchState((state) => ({ ...state, activeTab }));

  return (
    <section
      className={workbenchState.density === "compact" ? "d1-workbench d1-workbench-compact" : "d1-workbench"}
      data-density={workbenchState.density}
      data-chart-detail-smoke-fixture={readOnlyFixture ? "P107-A" : undefined}
      data-chart-detail-polish-stage={readOnlyFixture ? "E108-A" : undefined}
      data-chart-demo-kind={readOnlyFixture ? "read-only-example" : undefined}
      aria-label="Карта D1"
    >
      <div className="d1-header">
        <div>
          <span className="d1-kicker">Карта D1</span>
          <h1>{model.profile.title}</h1>
          <p>{model.profile.birthDate} · {model.profile.birthTime} · {model.profile.place}</p>
        </div>
        {readOnlyFixture ? (
          <div className="d1-actions">
            <span className="d1-readonly-fixture-badge">
              Пример D1 · только просмотр
              <span className="d1-readonly-fixture-note">это не сохранённая карта пользователя</span>
              <span hidden>P107-A E108-A read-only chart detail smoke path</span>
            </span>
          </div>
        ) : null}
        {!readOnlyFixture ? <div className="d1-actions">
          <a href={`/charts/${model.profile.id}/edit`}>Редактировать</a>
          <a href="/compatibility">Сравнить</a>
          <a href="/settings">Настройки</a>
          {onRecalculate ? <button type="button" data-chart-recalculate="chart-detail-recalculate-action" disabled={recalculating} onClick={() => void onRecalculate()}>{recalculating ? "Считаю..." : "Обновить расчёт"}</button> : null}
        </div> : null}
      </div>

      <div className="d1-meta-row">
        <span>Точность: {accuracyLabel(model.profile.birthTimeAccuracy)}</span>
        <span>Место: {model.profile.place}</span>
        <span>Часовой пояс: {model.profile.timezone}</span>
        <span>Расчёт: {model.calculation.version}</span>
        <span>Пресет: {model.profile.calculationPreset}</span>
      </div>

      <div className="d1-toolbar" aria-label="Стиль карты">
        <strong>Карта</strong>
        {availableScopeGroupsForMode(model, workbenchState.mode).map((group) => (
          <div key={group.category} className="d1-scope-group" data-category={group.category}>
            <span>{scopeCategoryLabel(group.category)}</span>
            {group.scopes.map((scope) => (
              <button key={scope.code} type="button" className={model.scopeId === scope.code ? "active" : ""} title={`${scope.name} - ${scope.methodId} v${scope.methodVersion}`} onClick={() => onScopeChange?.(scope.code)}>
                {scope.code}
              </button>
            ))}
          </div>
        ))}
        <strong>Стиль</strong>
        <button type="button" className={workbenchState.chartStyle === "north" ? "active" : ""} aria-pressed={workbenchState.chartStyle === "north"} aria-label="North chart style, house-fixed" onClick={() => setChartStyle("north")}>Северный</button>
        <button type="button" className={workbenchState.chartStyle === "south" ? "active" : ""} aria-pressed={workbenchState.chartStyle === "south"} aria-label="South chart style, sign-fixed" onClick={() => setChartStyle("south")}>Южный</button>
        <strong>Режим</strong>
        <button type="button" className={workbenchState.mode === "novice" ? "active" : ""} onClick={() => setMode("novice")}>Новичок</button>
        <button type="button" className={workbenchState.mode === "astrologer" ? "active" : ""} onClick={() => setMode("astrologer")}>Астролог</button>
        <strong>Термины</strong>
        {(["ru", "en", "sa", "short"] as const).map((termMode) => (
          <button key={termMode} type="button" className={workbenchState.terminologyMode === termMode ? "active" : ""} onClick={() => setTerminologyMode(termMode)}>
            {terminologyLabel(termMode)}
          </button>
        ))}
        <strong>Плотность</strong>
        <button type="button" className={workbenchState.density === "comfortable" ? "active" : ""} onClick={() => setDensity("comfortable")}>Обычный</button>
        <button type="button" className={workbenchState.density === "compact" ? "active" : ""} onClick={() => setDensity("compact")}>Компактный</button>
      </div>
      <p className="d1-style-explainer">North = house-fixed. South = sign-fixed.</p>
      <div
        className="d1-orientation-legend"
        data-chart-orientation-stage="E110-A"
        data-chart-orientation-mode={activeOrientationMode}
        data-chart-orientation-readonly={readOnlyFixture ? "read-only-demo" : "standard-chart"}
        aria-label="D1 chart orientation"
      >
        <span>
          <strong>Active style</strong>
          {activeOrientationCopy}
        </span>
        <span>
          <strong>Lagna</strong>
          {orientationLagna}
        </span>
        {readOnlyFixture ? (
          <span>
            <strong>Demo</strong>
            read-only example
          </span>
        ) : null}
        <span hidden>E110-A orientation legend</span>
      </div>

      {status ? <div className="product-status">{status}</div> : null}
      {workbenchState.mode === "astrologer" && activeScopeMeta ? (
        <div className="d1-method-strip">
          <span>{activeScopeMeta.methodId} v{activeScopeMeta.methodVersion}</span>
          <span>{activeScopeMeta.calculationPreset}</span>
          {activeAccuracyGate ? <span>accuracy: {activeAccuracyGate.status}</span> : null}
        </div>
      ) : null}
      {model.warnings.length ? (
        <div className="d1-warning-list">
          {model.warnings.map((warning) => <span key={warning.code}>{warning.message}</span>)}
        </div>
      ) : null}
      <D1TechnicalContextStrip model={model} activeScopeMeta={activeScopeMeta} activeAccuracyGate={activeAccuracyGate} />
      <D1MobileWorkflowNav activeTab={workbenchState.activeTab} onGrahaJump={() => setActiveTab("grahas")} />

      <div className="d1-main-grid">
        <div>
          <div id="d1-chart-panel" className="d1-chart-panel-anchor">
            {workbenchState.chartStyle === "north" ? (
              <NorthChart model={model} state={workbenchState} onSelect={setActiveEntityId} />
            ) : (
              <SouthChart model={model} state={workbenchState} onSelect={setActiveEntityId} />
            )}
          </div>
          <div className="d1-toolbar" aria-label="Вкладки D1">
            {tabIds.map((tabId) => (
              <button key={tabId} type="button" className={workbenchState.activeTab === tabId ? "active" : ""} onClick={() => setActiveTab(tabId)}>{tabLabel(tabId)}</button>
            ))}
          </div>
          <div id="d1-data-panel" className="d1-data-panel-anchor">
            <ChartDataTabs model={model} state={workbenchState} onSelect={setActiveEntityId} />
          </div>
        </div>
        <aside id="d1-inspector-panel" className="d1-inspector-panel">
          <EntityInspector entityId={workbenchState.activeEntityId} onClose={() => setActiveEntityId(null)} />
          {selected.length ? (
            <div className="d1-selected-facts">
              {selected.map((fact) => <span key={fact}>{fact}</span>)}
            </div>
          ) : null}
        </aside>
      </div>
    </section>
  );
}

function D1MobileWorkflowNav({ activeTab, onGrahaJump }: { activeTab: D1DataTab; onGrahaJump: () => void }) {
  return (
    <nav className="d1-mobile-workflow-nav" data-d1-mobile-workflow-stage="E139-A" aria-label="Mobile chart workflow">
      <a href="#d1-chart-panel"><strong>Chart</strong><span>D1</span></a>
      <a href="#d1-data-panel" className={activeTab === "grahas" ? "active" : ""} onClick={onGrahaJump}><strong>Grahas</strong><span>All rows</span></a>
      <a href="#d1-inspector-panel"><strong>Inspect</strong><span>Entity</span></a>
      <span hidden>E139-A; chart_viewer_mobile_workflow_nav=true; chart_viewer_mobile_chart_table_inspector_anchors=true; chart_viewer_mobile_graha_rows_compact=true; chart_viewer_mobile_no_wide_table_primary=true; backend_calculation_changed=false; production_deploy_skipped_per_user_batching_policy=true; last_verified_deploy_commit=40120c8</span>
    </nav>
  );
}

function D1TechnicalContextStrip({
  model,
  activeScopeMeta,
  activeAccuracyGate,
}: {
  model: D1WorkbenchModel;
  activeScopeMeta: D1WorkbenchModel["vargaScopes"][number] | undefined;
  activeAccuracyGate: D1WorkbenchModel["accuracyGates"][string] | undefined;
}) {
  const availableVargas = model.technical.vargas.filter((row) => row.status === "available").length;
  return (
    <div className="chart-context-strip d1-technical-context-strip" data-d1-technical-context-stage="E137-A" aria-label="Technical chart context">
      <span><strong>Scope</strong>{model.scopeId} / {activeScopeMeta?.category ?? "main"} / {activeScopeMeta?.methodId ?? "saved calculation"}</span>
      <span><strong>Objects</strong>{model.stats.chartObjectCount} total / {model.stats.grahaCount} grahas / {model.stats.specialPointCount} points</span>
      <span><strong>Coverage</strong>{availableVargas}/{model.technical.vargas.length} vargas / {model.technical.dashas.length} dashas</span>
      <span><strong>Calculation</strong>{model.calculation.status} / {model.calculation.version}</span>
      <span><strong>Gate</strong>{activeAccuracyGate?.status ?? "standard"}</span>
      <span hidden>E137-A; d1_technical_context_strip_present=true; chart_viewer_scope_coverage_visible=true; chart_viewer_calculation_status_visible=true; chart_viewer_accuracy_gate_visible=true; backend_calculation_changed=false; production_deploy_skipped_per_user_batching_policy=true; last_verified_deploy_commit=40120c8</span>
      <span hidden>E138-A; chart_viewer_default_tab=grahas; chart_viewer_all_planets_visible_first_view=true; backend_calculation_changed=false; production_deploy_skipped_per_user_batching_policy=true; last_verified_deploy_commit=40120c8</span>
    </div>
  );
}

function NorthChart({ model, state, onSelect }: { model: D1WorkbenchModel; state: ChartWorkbenchState; onSelect: (id: EntityId) => void }) {
  return (
    <section className="d1-chart-card">
      <div className="d1-chart-title"><h2>{model.scopeId} Раши</h2><span>North = house-fixed; houses stay in position</span></div>
      <div className="d1-north-chart">
        <svg viewBox="0 0 100 100" aria-hidden="true">
          <path d="M0 0 L100 100 M100 0 L0 100" />
          <path d="M50 0 L100 50 L50 100 L0 50 Z" />
          <path d="M0 0 L50 50 L100 0 M0 100 L50 50 L100 100" />
        </svg>
        {model.houses.map((house) => {
          const position = NORTH_POSITIONS[house.house];
          return <ChartCell key={house.house} house={house} grahas={grahasForHouse(model, house.house)} specialPoints={specialPointsForHouse(model, house.house)} state={state} onSelect={onSelect} style={{ left: `${position.x}%`, top: `${position.y}%` }} />;
        })}
      </div>
    </section>
  );
}

function SouthChart({ model, state, onSelect }: { model: D1WorkbenchModel; state: ChartWorkbenchState; onSelect: (id: EntityId) => void }) {
  return (
    <section className="d1-chart-card">
      <div className="d1-chart-title"><h2>{model.scopeId} Раши</h2><span>South = sign-fixed; grahas and houses move through fixed rashi cells</span></div>
      <div className="d1-south-chart" aria-label="South Indian sign-fixed chart">
        {SOUTH_SIGN_ORDER.map((rashiIndex) => {
          const position = SOUTH_SIGN_GRID[rashiIndex];
          const house = houseForRashi(model, rashiIndex);
          return (
            <SouthSignCell
              key={rashiIndex}
              rashiIndex={rashiIndex}
              house={house}
              grahas={grahasForRashi(model, rashiIndex)}
              specialPoints={specialPointsForRashi(model, rashiIndex)}
              state={state}
              onSelect={onSelect}
              style={{ gridColumn: position.col, gridRow: position.row }}
            />
          );
        })}
        <div className="d1-south-center"><strong>{model.scopeId}</strong><span>sign-fixed</span></div>
      </div>
    </section>
  );
}

function SouthSignCell({ rashiIndex, house, grahas, specialPoints, state, onSelect, style }: { rashiIndex: number; house: D1HouseCell | null; grahas: D1GrahaRow[]; specialPoints: D1SpecialPointRow[]; state: ChartWorkbenchState; onSelect: (id: EntityId) => void; style: CSSProperties }) {
  const sign = SOUTH_SIGN_LABELS[rashiIndex];
  const rashiEntityId = house?.rashiEntityId ?? sign.entityId;
  return (
    <div
      className="d1-chart-cell d1-south-sign-cell"
      data-south-sign-fixed="true"
      data-rashi-index={rashiIndex}
      style={style}
      aria-label={`${sign.name}; ${house ? `house ${house.house}` : "house not mapped"}`}
    >
      {state.displayLayers.rashiLabels ? <button type="button" className="d1-rashi-button" onClick={() => onSelect(rashiEntityId)}>{sign.short} {sign.name}</button> : null}
      {state.displayLayers.houseNumbers && house ? <button type="button" className="d1-house-button" onClick={() => onSelect(house.houseEntityId)}>House {house.house}</button> : null}
      <div className="d1-graha-stack">
        {state.displayLayers.specialPoints ? specialPoints.map((point) => (
          <button key={point.code} type="button" className={point.code === "LAGNA" ? "d1-lagna-marker" : undefined} onClick={() => onSelect(point.entityId)}>
            {point.code === "LAGNA" ? "Lagna" : placementLabel(point, state.terminologyMode)}{state.displayLayers.degrees && state.mode === "astrologer" ? ` ${point.degreeInSign}` : ""}
          </button>
        )) : null}
        {state.displayLayers.grahas ? grahas.map((graha) => (
          <button key={graha.code} type="button" onClick={() => onSelect(graha.placementEntityId ?? graha.entityId)}>
            {placementLabel(graha, state.terminologyMode)}{graha.retrograde && state.displayLayers.retrograde ? " (R)" : ""}{state.displayLayers.degrees && state.mode === "astrologer" ? ` ${graha.degreeInSign}` : ""}
          </button>
        )) : null}
      </div>
    </div>
  );
}

function ChartCell({ house, grahas, specialPoints, state, onSelect, style }: { house: D1HouseCell; grahas: D1GrahaRow[]; specialPoints: D1SpecialPointRow[]; state: ChartWorkbenchState; onSelect: (id: EntityId) => void; style: CSSProperties }) {
  return (
    <div className="d1-chart-cell" style={style}>
      {state.displayLayers.houseNumbers ? <button type="button" className="d1-house-button" onClick={() => onSelect(house.houseEntityId)}>{house.house}</button> : null}
      {state.displayLayers.rashiLabels && house.rashiEntityId ? <button type="button" className="d1-rashi-button" onClick={() => onSelect(house.rashiEntityId!)}>{house.rashiName}</button> : null}
      <div className="d1-graha-stack">
        {state.displayLayers.specialPoints ? specialPoints.map((point) => (
          <button key={point.code} type="button" onClick={() => onSelect(point.entityId)}>
            {placementLabel(point, state.terminologyMode)}{state.displayLayers.degrees && state.mode === "astrologer" ? ` ${point.degreeInSign}` : ""}
          </button>
        )) : null}
        {state.displayLayers.grahas ? grahas.map((graha) => (
          <button key={graha.code} type="button" onClick={() => onSelect(graha.placementEntityId ?? graha.entityId)}>
            {placementLabel(graha, state.terminologyMode)}{graha.retrograde && state.displayLayers.retrograde ? " (R)" : ""}{state.displayLayers.degrees && state.mode === "astrologer" ? ` ${graha.degreeInSign}` : ""}
          </button>
        )) : null}
      </div>
    </div>
  );
}

function ChartDataTabs({ model, state, onSelect }: { model: D1WorkbenchModel; state: ChartWorkbenchState; onSelect: (id: EntityId) => void }) {
  if (state.activeTab === "grahas") return <GrahaTable model={model} state={state} onSelect={onSelect} />;
  if (state.activeTab === "houses") return <HouseTable model={model} onSelect={onSelect} />;
  if (state.activeTab === "nakshatras" && model.capabilities.nakshatrasAvailable) return <NakshatraTable model={model} state={state} onSelect={onSelect} />;
  if (state.activeTab === "technical") return <TechnicalPayloadPanel model={model} />;
  return <OverviewPanel model={model} state={state} onSelect={onSelect} />;
}

function OverviewPanel({ model, state, onSelect }: { model: D1WorkbenchModel; state: ChartWorkbenchState; onSelect: (id: EntityId) => void }) {
  const sun = model.grahas.find((item) => item.code === "SU");
  const moon = model.grahas.find((item) => item.code === "MO");
  const lagna = model.specialPoints.find((item) => item.code === "LAGNA");
  const rows = [lagna, sun, moon].filter(Boolean) as Array<D1GrahaRow | D1SpecialPointRow>;
  return (
    <section className="d1-table-card">
      <div className="d1-chart-title"><h2>Обзор</h2><span>{model.scopeId} · {model.stats.grahaCount} грах · {model.stats.specialPointCount} опорная точка</span></div>
      <div className="d1-table-scroll">
        <table>
          <tbody>
            {rows.map((row) => (
              <tr key={row.code}>
                <td><button type="button" onClick={() => onSelect(row.entityId)}>{placementLabel(row, state.terminologyMode)}</button></td>
                <td>{row.rashiEntityId ? <button type="button" onClick={() => onSelect(row.rashiEntityId!)}>{row.rashiName}</button> : row.rashiName}</td>
                <td>{row.houseEntityId ? <button type="button" onClick={() => onSelect(row.houseEntityId!)}>{row.house}</button> : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function GrahaTable({ model, state, onSelect }: { model: D1WorkbenchModel; state: ChartWorkbenchState; onSelect: (id: EntityId) => void }) {
  const isAstrologer = state.mode === "astrologer";
  return (
    <section className="d1-table-card d1-graha-table-card">
      <div className="d1-chart-title"><h2>Грахи</h2><span>Только планеты; Лагна вынесена в опорные точки</span></div>
      <div className="d1-table-scroll">
        <table>
          <thead>
            <tr>
              <th>Граха</th>
              {isAstrologer ? <th>Longitude</th> : null}
              {isAstrologer ? <th>Градус</th> : null}
              {isAstrologer ? <th>Speed</th> : null}
              <th>Знак</th>
              <th>Дом</th>
              {isAstrologer && model.capabilities.nakshatrasAvailable ? <th>Накшатра</th> : null}
              {isAstrologer && model.capabilities.padasAvailable ? <th>Пада</th> : null}
              {isAstrologer && model.capabilities.retrogradeAvailable ? <th>Ретр.</th> : null}
              {isAstrologer && model.capabilities.dignityAvailable ? <th>Достоинство</th> : null}
              {isAstrologer && model.capabilities.navamsaAvailable ? <th>Навамша</th> : null}
            </tr>
          </thead>
          <tbody>
            {model.grahas.map((graha) => (
              <tr key={graha.code}>
                <td data-label="Graha"><button type="button" onClick={() => onSelect(graha.placementEntityId ?? graha.entityId)}>{placementLabel(graha, state.terminologyMode)}</button></td>
                {isAstrologer ? <td data-label="Longitude">{graha.absoluteLongitude}</td> : null}
                {isAstrologer ? <td data-label="Degree">{graha.degreeInSign}</td> : null}
                {isAstrologer ? <td data-label="Speed">{graha.speedLongitude}</td> : null}
                <td data-label="Rashi">{graha.rashiEntityId ? <button type="button" onClick={() => onSelect(graha.rashiEntityId!)}>{graha.rashiName}</button> : graha.rashiName}</td>
                <td data-label="House">{graha.houseEntityId ? <button type="button" onClick={() => onSelect(graha.houseEntityId!)}>{graha.house}</button> : "-"}</td>
                {isAstrologer && model.capabilities.nakshatrasAvailable ? <td data-label="Nakshatra">{graha.nakshatraEntityId ? <button type="button" onClick={() => onSelect(graha.nakshatraEntityId!)}>{graha.nakshatra}</button> : "-"}</td> : null}
                {isAstrologer && model.capabilities.padasAvailable ? <td data-label="Pada">{graha.pada ?? "-"}</td> : null}
                {isAstrologer && model.capabilities.retrogradeAvailable ? <td data-label="Retrograde">{graha.retrograde ? "да" : "-"}</td> : null}
                {isAstrologer && model.capabilities.dignityAvailable ? <td data-label="Dignity">{graha.dignity ?? "-"}</td> : null}
                {isAstrologer && model.capabilities.navamsaAvailable ? <td data-label="Navamsa">{graha.navamsa ?? "-"}</td> : null}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function HouseTable({ model, onSelect }: { model: D1WorkbenchModel; onSelect: (id: EntityId) => void }) {
  return (
    <section className="d1-table-card">
      <div className="d1-chart-title"><h2>Дома</h2><span>Знаки и объекты в домах</span></div>
      <div className="d1-table-scroll">
        <table>
          <thead><tr><th>Дом</th><th>Знак</th><th>Планеты</th><th>Опорные точки</th></tr></thead>
          <tbody>
            {model.houses.map((house) => (
              <tr key={house.house}>
                <td><button type="button" onClick={() => onSelect(house.houseEntityId)}>{house.house}</button></td>
                <td>{house.rashiEntityId ? <button type="button" onClick={() => onSelect(house.rashiEntityId!)}>{house.rashiName}</button> : house.rashiName}</td>
                <td>{house.grahaCodes.join(", ") || "-"}</td>
                <td>{house.specialPointCodes.join(", ") || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function NakshatraTable({ model, state, onSelect }: { model: D1WorkbenchModel; state: ChartWorkbenchState; onSelect: (id: EntityId) => void }) {
  const rows = [...model.specialPoints, ...model.grahas].filter((row) => row.nakshatra);
  return (
    <section className="d1-table-card">
      <div className="d1-chart-title"><h2>Накшатры</h2><span>Только уже рассчитанные данные</span></div>
      <div className="d1-table-scroll">
        <table>
          <thead><tr><th>Объект</th><th>Накшатра</th><th>Пада</th></tr></thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.code}>
                <td><button type="button" onClick={() => onSelect(row.entityId)}>{placementLabel(row, state.terminologyMode)}</button></td>
                <td>{row.nakshatraEntityId ? <button type="button" onClick={() => onSelect(row.nakshatraEntityId!)}>{row.nakshatra}</button> : row.nakshatra}</td>
                <td>{row.pada ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function TechnicalPayloadPanel({ model }: { model: D1WorkbenchModel }) {
  return (
    <div className="d1-technical-grid">
      <section className="d1-table-card" data-technical-section="settings">
        <div className="d1-chart-title"><h2>Settings</h2><span>Core calculation configuration</span></div>
        <TechnicalSummaryRows rows={model.technical.settings} />
      </section>
      <section className="d1-table-card" data-technical-section="panchanga">
        <div className="d1-chart-title"><h2>Panchanga</h2><span>Tithi, vara, nakshatra, yoga, karana</span></div>
        <TechnicalSummaryRows rows={model.technical.panchanga} />
      </section>
      <section className="d1-table-card" data-technical-section="solar-day">
        <div className="d1-chart-title"><h2>Solar day</h2><span>Sunrise, sunset and day/night bounds</span></div>
        <TechnicalSummaryRows rows={model.technical.solarDay} />
      </section>
      <section className="d1-table-card" data-technical-section="dashas">
        <div className="d1-chart-title"><h2>Dashas</h2><span>Vimshottari mahadashas from saved calculation</span></div>
        <div className="d1-table-scroll">
          <table>
            <thead><tr><th>Lord</th><th>Start</th><th>End</th><th>Years</th></tr></thead>
            <tbody>
              {model.technical.dashas.length ? model.technical.dashas.map((row) => (
                <tr key={`${row.lord}-${row.startsAt}`}>
                  <td>{row.lord}</td>
                  <td>{row.startsAt}</td>
                  <td>{row.endsAt}</td>
                  <td>{row.durationYears}</td>
                </tr>
              )) : <EmptyTechnicalRow colSpan={4} />}
            </tbody>
          </table>
        </div>
      </section>
      <section className="d1-table-card" data-technical-section="vargas">
        <div className="d1-chart-title"><h2>Vargas</h2><span>All supported D-charts and placement coverage</span></div>
        <div className="d1-table-scroll">
          <table>
            <thead><tr><th>Code</th><th>Name</th><th>Method</th><th>Status</th><th>Placements</th></tr></thead>
            <tbody>
              {model.technical.vargas.length ? model.technical.vargas.map((row) => (
                <tr key={row.code}>
                  <td>{row.code}</td>
                  <td>{row.name}</td>
                  <td>{row.method}</td>
                  <td>{row.status}</td>
                  <td>{row.placementCount}</td>
                </tr>
              )) : <EmptyTechnicalRow colSpan={5} />}
            </tbody>
          </table>
        </div>
      </section>
      <section className="d1-table-card" data-technical-section="house-cusps">
        <div className="d1-chart-title"><h2>House cusps</h2><span>Bhava cusp longitudes</span></div>
        <div className="d1-table-scroll">
          <table>
            <thead><tr><th>House</th><th>Longitude</th><th>Rashi</th></tr></thead>
            <tbody>
              {model.technical.houseCusps.length ? model.technical.houseCusps.map((row) => (
                <tr key={row.house}>
                  <td>{row.house}</td>
                  <td>{row.longitude}</td>
                  <td>{row.rashi}</td>
                </tr>
              )) : <EmptyTechnicalRow colSpan={3} />}
            </tbody>
          </table>
        </div>
      </section>
      <section className="d1-table-card" data-technical-section="classical">
        <div className="d1-chart-title"><h2>Classical</h2><span>Avasthas, bala, yogas and auxiliary modules</span></div>
        <TechnicalSummaryRows rows={model.technical.classical} />
      </section>
      <InternalJsonSnapshot model={model} />
    </div>
  );
}

function InternalJsonSnapshot({ model }: { model: D1WorkbenchModel }) {
  const snapshot = {
    schemaVersion: model.schemaVersion,
    scopeId: model.scopeId,
    calculation: model.calculation,
    stats: model.stats,
    technical: model.technical,
  };
  return (
    <section className="d1-table-card" data-technical-section="internal-json">
      <div className="d1-chart-title"><h2>Internal JSON</h2><span>Reviewer snapshot, not client interpretation</span></div>
      <details>
        <summary>Show compact JSON snapshot</summary>
        <pre>{JSON.stringify(snapshot, null, 2)}</pre>
      </details>
    </section>
  );
}

function TechnicalSummaryRows({ rows }: { rows: D1TechnicalSummaryRow[] }) {
  return (
    <div className="d1-table-scroll">
      <table>
        <tbody>
          {rows.length ? rows.map((row) => (
            <tr key={row.key}>
              <th>{row.label}</th>
              <td>{row.value}</td>
            </tr>
          )) : <EmptyTechnicalRow colSpan={2} />}
        </tbody>
      </table>
    </div>
  );
}

function EmptyTechnicalRow({ colSpan }: { colSpan: number }) {
  return <tr><td colSpan={colSpan}>No saved data</td></tr>;
}

function grahasForHouse(model: D1WorkbenchModel, house: number) {
  return model.grahas.filter((graha) => graha.house === house);
}

function specialPointsForHouse(model: D1WorkbenchModel, house: number) {
  return model.specialPoints.filter((point) => point.house === house);
}

function houseForRashi(model: D1WorkbenchModel, rashiIndex: number) {
  return model.houses.find((house) => house.rashiIndex === rashiIndex) ?? null;
}

function grahasForRashi(model: D1WorkbenchModel, rashiIndex: number) {
  return model.grahas.filter((graha) => graha.rashiIndex === rashiIndex);
}

function specialPointsForRashi(model: D1WorkbenchModel, rashiIndex: number) {
  return model.specialPoints.filter((point) => point.rashiIndex === rashiIndex);
}

function selectedFacts(model: D1WorkbenchModel, entityId: EntityId | null): string[] {
  if (!entityId) return [];
  const point = model.specialPoints.find((item) => item.entityId === entityId);
  if (point) return [`${point.label}: ${point.rashiName}, дом ${point.house ?? "-"}`, `Накшатра: ${point.nakshatra ?? "-"}`, "Лагна является опорной точкой, а не грахой."];
  const graha = model.grahas.find((item) => item.entityId === entityId || item.placementEntityId === entityId);
  if (graha) return [`${graha.label}: ${graha.rashiName}, дом ${graha.house ?? "-"}`, `Накшатра: ${graha.nakshatra ?? "-"}`, `Статус: ${statusText(graha)}`];
  const house = model.houses.find((item) => item.houseEntityId === entityId || item.rashiEntityId === entityId);
  if (house) return [`Дом ${house.house}: ${house.rashiName}`, `Грахи: ${house.grahaCodes.join(", ") || "нет"}`, `Опорные точки: ${house.specialPointCodes.join(", ") || "нет"}`];
  return [];
}

function placementLabel(row: D1GrahaRow | D1SpecialPointRow, terminologyMode: D1TerminologyMode) {
  if (terminologyMode === "short") return row.shortLabel;
  if (terminologyMode === "en") return row.body === "Surya" ? "Sun" : row.body === "Chandra" ? "Moon" : row.body;
  if (terminologyMode === "sa") return row.body;
  return row.label;
}

function terminologyLabel(terminologyMode: D1TerminologyMode) {
  if (terminologyMode === "ru") return "RU";
  if (terminologyMode === "en") return "EN";
  if (terminologyMode === "sa") return "SA";
  return "Кратко";
}

function availableScopeGroupsForMode(model: D1WorkbenchModel, mode: D1ReaderMode) {
  const supported = new Set(model.supportedScopes);
  const expert = new Set(model.expertOnlyScopes);
  const scopes = model.vargaScopes
    .filter((scope) => supported.has(scope.code))
    .filter((scope) => mode === "astrologer" || !expert.has(scope.code));
  const categories = ["main", "family", "professional", "spiritual", "expert"] as const;
  return categories
    .map((category) => ({ category, scopes: scopes.filter((scope) => scope.category === category) }))
    .filter((group) => group.scopes.length > 0);
}

function scopeCategoryLabel(category: string) {
  if (category === "main") return "Base";
  if (category === "family") return "Family";
  if (category === "professional") return "Work";
  if (category === "spiritual") return "Dharma";
  return "Expert";
}

function availableTabs(model: D1WorkbenchModel): D1DataTab[] {
  const tabs: D1DataTab[] = ["overview", "grahas", "houses"];
  if (model.capabilities.nakshatrasAvailable) tabs.push("nakshatras");
  tabs.push("technical");
  return tabs;
}

function tabLabel(tab: D1DataTab) {
  if (tab === "overview") return "Обзор";
  if (tab === "grahas") return "Грахи";
  if (tab === "houses") return "Дома";
  if (tab === "technical") return "Technical";
  return "Накшатры";
}

function statusText(graha: D1GrahaRow) {
  const parts = [];
  if (graha.dignity) parts.push(graha.dignity);
  if (graha.retrograde) parts.push("ретроградность");
  return parts.join(", ") || "-";
}

function accuracyLabel(value: string) {
  if (value === "exact") return "точное";
  if (value === "approximate") return "примерное";
  if (value === "unknown") return "неизвестно";
  return value;
}
