"use client";

import { useMemo, useState, type CSSProperties } from "react";
import type { EntityId } from "@/astrology";
import {
  CHART_WORKBENCH_EXPERT_SCOPE_IDS,
  CHART_WORKBENCH_SCOPE_IDS,
  type ChartWorkbenchScopeId,
  type D1ChartStyle,
  type D1DataTab,
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
  onRecalculate?: () => void;
  onScopeChange?: (scopeId: ChartWorkbenchScopeId) => void;
  status?: string;
};

type ChartWorkbenchState = {
  scopeId: ChartWorkbenchScopeId;
  mode: D1ReaderMode;
  chartStyle: D1ChartStyle;
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

const SOUTH_GRID: Record<number, { col: number; row: number }> = {
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

export function D1ChartWorkbench({ model, onRecalculate, onScopeChange, status }: D1ChartWorkbenchProps) {
  const [workbenchState, setWorkbenchState] = useState<ChartWorkbenchState>({
    scopeId: model.scopeId,
    mode: model.defaults.readerMode,
    chartStyle: model.defaults.chartStyle,
    activeEntityId: null,
    activeTab: "overview",
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

  const setActiveEntityId = (activeEntityId: EntityId | null) => setWorkbenchState((state) => ({ ...state, activeEntityId }));
  const setChartStyle = (chartStyle: D1ChartStyle) => setWorkbenchState((state) => ({ ...state, chartStyle }));
  const setMode = (mode: D1ReaderMode) => {
    if (mode === "novice" && CHART_WORKBENCH_EXPERT_SCOPE_IDS.includes(model.scopeId as typeof CHART_WORKBENCH_EXPERT_SCOPE_IDS[number])) {
      onScopeChange?.("D1");
    }
    setWorkbenchState((state) => ({ ...state, mode }));
  };
  const setTerminologyMode = (terminologyMode: D1TerminologyMode) => setWorkbenchState((state) => ({ ...state, terminologyMode }));
  const setActiveTab = (activeTab: D1DataTab) => setWorkbenchState((state) => ({ ...state, activeTab }));

  return (
    <section className="d1-workbench" aria-label="Карта D1">
      <div className="d1-header">
        <div>
          <span className="d1-kicker">Карта D1</span>
          <h1>{model.profile.title}</h1>
          <p>{model.profile.birthDate} · {model.profile.birthTime} · {model.profile.place}</p>
        </div>
        <div className="d1-actions">
          <a href={`/charts/${model.profile.id}/edit`}>Редактировать</a>
          <a href="/compatibility">Сравнить</a>
          <a href="/settings">Настройки</a>
          {onRecalculate ? <button type="button" onClick={onRecalculate}>Обновить расчёт</button> : null}
        </div>
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
        {availableScopesForMode(workbenchState.mode).map((scopeId) => (
          <button key={scopeId} type="button" className={model.scopeId === scopeId ? "active" : ""} onClick={() => onScopeChange?.(scopeId)}>{scopeId}</button>
        ))}
        <strong>Стиль</strong>
        <button type="button" className={workbenchState.chartStyle === "north" ? "active" : ""} onClick={() => setChartStyle("north")}>Северный</button>
        <button type="button" className={workbenchState.chartStyle === "south" ? "active" : ""} onClick={() => setChartStyle("south")}>Южный</button>
        <strong>Режим</strong>
        <button type="button" className={workbenchState.mode === "novice" ? "active" : ""} onClick={() => setMode("novice")}>Новичок</button>
        <button type="button" className={workbenchState.mode === "astrologer" ? "active" : ""} onClick={() => setMode("astrologer")}>Астролог</button>
        <strong>Термины</strong>
        {(["ru", "en", "sa", "short"] as const).map((termMode) => (
          <button key={termMode} type="button" className={workbenchState.terminologyMode === termMode ? "active" : ""} onClick={() => setTerminologyMode(termMode)}>
            {termMode === "short" ? "Кратко" : termMode.toUpperCase()}
          </button>
        ))}
      </div>

      {status ? <div className="product-status">{status}</div> : null}
      {model.warnings.length ? (
        <div className="d1-warning-list">
          {model.warnings.map((warning) => <span key={warning.code}>{warning.message}</span>)}
        </div>
      ) : null}

      <div className="d1-main-grid">
        <div>
          {workbenchState.chartStyle === "north" ? (
            <NorthChart model={model} state={workbenchState} onSelect={setActiveEntityId} />
          ) : (
            <SouthChart model={model} state={workbenchState} onSelect={setActiveEntityId} />
          )}
          <div className="d1-toolbar" aria-label="Вкладки D1">
            {tabIds.map((tabId) => (
              <button key={tabId} type="button" className={workbenchState.activeTab === tabId ? "active" : ""} onClick={() => setActiveTab(tabId)}>{tabLabel(tabId)}</button>
            ))}
          </div>
          <ChartDataTabs model={model} state={workbenchState} onSelect={setActiveEntityId} />
        </div>
        <aside className="d1-inspector-panel">
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

function NorthChart({ model, state, onSelect }: { model: D1WorkbenchModel; state: ChartWorkbenchState; onSelect: (id: EntityId) => void }) {
  return (
    <section className="d1-chart-card">
      <div className="d1-chart-title"><h2>{model.scopeId} Раши</h2><span>Нажмите на дом, знак, граху или Лагну</span></div>
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
      <div className="d1-chart-title"><h2>{model.scopeId} Раши</h2><span>Южноиндийская сетка знаков</span></div>
      <div className="d1-south-chart">
        {model.houses.map((house) => {
          const position = SOUTH_GRID[house.house];
          return <ChartCell key={house.house} house={house} grahas={grahasForHouse(model, house.house)} specialPoints={specialPointsForHouse(model, house.house)} state={state} onSelect={onSelect} style={{ gridColumn: position.col, gridRow: position.row }} />;
        })}
        <div className="d1-south-center">{model.scopeId}</div>
      </div>
    </section>
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
    <section className="d1-table-card">
      <div className="d1-chart-title"><h2>Грахи</h2><span>Только планеты; Лагна вынесена в опорные точки</span></div>
      <div className="d1-table-scroll">
        <table>
          <thead>
            <tr>
              <th>Граха</th>
              {isAstrologer ? <th>Градус</th> : null}
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
                <td><button type="button" onClick={() => onSelect(graha.placementEntityId ?? graha.entityId)}>{placementLabel(graha, state.terminologyMode)}</button></td>
                {isAstrologer ? <td>{graha.degreeInSign}</td> : null}
                <td>{graha.rashiEntityId ? <button type="button" onClick={() => onSelect(graha.rashiEntityId!)}>{graha.rashiName}</button> : graha.rashiName}</td>
                <td>{graha.houseEntityId ? <button type="button" onClick={() => onSelect(graha.houseEntityId!)}>{graha.house}</button> : "-"}</td>
                {isAstrologer && model.capabilities.nakshatrasAvailable ? <td>{graha.nakshatraEntityId ? <button type="button" onClick={() => onSelect(graha.nakshatraEntityId!)}>{graha.nakshatra}</button> : "-"}</td> : null}
                {isAstrologer && model.capabilities.padasAvailable ? <td>{graha.pada ?? "-"}</td> : null}
                {isAstrologer && model.capabilities.retrogradeAvailable ? <td>{graha.retrograde ? "да" : "-"}</td> : null}
                {isAstrologer && model.capabilities.dignityAvailable ? <td>{graha.dignity ?? "-"}</td> : null}
                {isAstrologer && model.capabilities.navamsaAvailable ? <td>{graha.navamsa ?? "-"}</td> : null}
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

function grahasForHouse(model: D1WorkbenchModel, house: number) {
  return model.grahas.filter((graha) => graha.house === house);
}

function specialPointsForHouse(model: D1WorkbenchModel, house: number) {
  return model.specialPoints.filter((point) => point.house === house);
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

function availableScopesForMode(mode: D1ReaderMode): ChartWorkbenchScopeId[] {
  if (mode === "astrologer") return [...CHART_WORKBENCH_SCOPE_IDS];
  return CHART_WORKBENCH_SCOPE_IDS.filter((scopeId) => !CHART_WORKBENCH_EXPERT_SCOPE_IDS.includes(scopeId as typeof CHART_WORKBENCH_EXPERT_SCOPE_IDS[number]));
}
function availableTabs(model: D1WorkbenchModel): D1DataTab[] {
  const tabs: D1DataTab[] = ["overview", "grahas", "houses"];
  if (model.capabilities.nakshatrasAvailable) tabs.push("nakshatras");
  return tabs;
}

function tabLabel(tab: D1DataTab) {
  if (tab === "overview") return "Обзор";
  if (tab === "grahas") return "Грахи";
  if (tab === "houses") return "Дома";
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
