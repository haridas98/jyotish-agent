"use client";

import { useMemo, useState, type CSSProperties } from "react";
import type { EntityId } from "@/astrology";
import type { D1ChartStyle, D1GrahaRow, D1HouseCell, D1ReaderMode, D1WorkbenchModel } from "@/astrology/d1-workbench";
import { EntityInspector } from "@/ui/components/EntityInspector";

type D1ChartWorkbenchProps = {
  model: D1WorkbenchModel;
  onRecalculate?: () => void;
  status?: string;
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
        <aside className="v2-inspector"><h2>Объяснение</h2><p>Нажмите на дом, знак или граху.</p></aside>
      </div>
    </section>
  );
}

export function D1ChartWorkbench({ model, onRecalculate, status }: D1ChartWorkbenchProps) {
  const [chartStyle, setChartStyle] = useState<D1ChartStyle>(model.defaults.chartStyle);
  const [mode, setMode] = useState<D1ReaderMode>(model.defaults.readerMode);
  const [activeEntityId, setActiveEntityId] = useState<EntityId | null>(null);
  const selected = useMemo(() => selectedFacts(model, activeEntityId), [model, activeEntityId]);

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
          <a href="/charts">Кабинет карт</a>
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
        <strong>Стиль карты</strong>
        <button type="button" className={chartStyle === "north" ? "active" : ""} onClick={() => setChartStyle("north")}>Северный</button>
        <button type="button" className={chartStyle === "south" ? "active" : ""} onClick={() => setChartStyle("south")}>Южный</button>
        <strong>Режим</strong>
        <button type="button" className={mode === "novice" ? "active" : ""} onClick={() => setMode("novice")}>Новичок</button>
        <button type="button" className={mode === "astrologer" ? "active" : ""} onClick={() => setMode("astrologer")}>Астролог</button>
      </div>

      {status ? <div className="product-status">{status}</div> : null}
      {model.warnings.length ? (
        <div className="d1-warning-list">
          {model.warnings.map((warning) => <span key={warning.code}>{warning.message}</span>)}
        </div>
      ) : null}

      <div className="d1-main-grid">
        <div>
          {chartStyle === "north" ? (
            <NorthChart model={model} mode={mode} onSelect={setActiveEntityId} />
          ) : (
            <SouthChart model={model} mode={mode} onSelect={setActiveEntityId} />
          )}
          <GrahaTable model={model} mode={mode} onSelect={setActiveEntityId} />
        </div>
        <aside className="d1-inspector-panel">
          <EntityInspector entityId={activeEntityId} onClose={() => setActiveEntityId(null)} />
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

function NorthChart({ model, mode, onSelect }: { model: D1WorkbenchModel; mode: D1ReaderMode; onSelect: (id: EntityId) => void }) {
  return (
    <section className="d1-chart-card">
      <div className="d1-chart-title"><h2>D1 Раши</h2><span>Нажмите на дом, знак или граху</span></div>
      <div className="d1-north-chart">
        <svg viewBox="0 0 100 100" aria-hidden="true">
          <path d="M0 0 L100 100 M100 0 L0 100" />
          <path d="M50 0 L100 50 L50 100 L0 50 Z" />
          <path d="M0 0 L50 50 L100 0 M0 100 L50 50 L100 100" />
        </svg>
        {model.houses.map((house) => {
          const position = NORTH_POSITIONS[house.house];
          return <ChartCell key={house.house} house={house} grahas={grahasForHouse(model, house.house)} mode={mode} onSelect={onSelect} style={{ left: `${position.x}%`, top: `${position.y}%` }} />;
        })}
      </div>
    </section>
  );
}

function SouthChart({ model, mode, onSelect }: { model: D1WorkbenchModel; mode: D1ReaderMode; onSelect: (id: EntityId) => void }) {
  return (
    <section className="d1-chart-card">
      <div className="d1-chart-title"><h2>D1 Раши</h2><span>Южноиндийская сетка знаков</span></div>
      <div className="d1-south-chart">
        {model.houses.map((house) => {
          const position = SOUTH_GRID[house.house];
          return <ChartCell key={house.house} house={house} grahas={grahasForHouse(model, house.house)} mode={mode} onSelect={onSelect} style={{ gridColumn: position.col, gridRow: position.row }} />;
        })}
        <div className="d1-south-center">D1</div>
      </div>
    </section>
  );
}

function ChartCell({ house, grahas, mode, onSelect, style }: { house: D1HouseCell; grahas: D1GrahaRow[]; mode: D1ReaderMode; onSelect: (id: EntityId) => void; style: CSSProperties }) {
  return (
    <div className="d1-chart-cell" style={style}>
      <button type="button" className="d1-house-button" onClick={() => onSelect(house.houseEntityId)}>{house.house}</button>
      {house.rashiEntityId ? <button type="button" className="d1-rashi-button" onClick={() => onSelect(house.rashiEntityId!)}>{house.rashiName}</button> : null}
      <div className="d1-graha-stack">
        {grahas.map((graha) => (
          <button key={graha.code} type="button" onClick={() => onSelect(graha.placementEntityId ?? graha.entityId)}>
            {mode === "novice" ? graha.label : graha.code}{graha.retrograde ? " (R)" : ""}
          </button>
        ))}
      </div>
    </div>
  );
}

function GrahaTable({ model, mode, onSelect }: { model: D1WorkbenchModel; mode: D1ReaderMode; onSelect: (id: EntityId) => void }) {
  return (
    <section className="d1-table-card">
      <div className="d1-chart-title"><h2>Таблица D1</h2><span>Основные расчётные значения рядом с картой</span></div>
      <div className="d1-table-scroll">
        <table>
          <thead>
            <tr>
              <th>Граха</th>
              <th>Знак</th>
              <th>Градус</th>
              <th>Дом</th>
              <th>Накшатра</th>
              <th>Пада</th>
              {mode === "astrologer" ? <th>Статус</th> : null}
              {mode === "astrologer" ? <th>Навамша</th> : null}
            </tr>
          </thead>
          <tbody>
            {model.grahas.map((graha) => (
              <tr key={graha.code}>
                <td><button type="button" onClick={() => onSelect(graha.placementEntityId ?? graha.entityId)}>{mode === "novice" ? graha.label : graha.code}</button></td>
                <td>{graha.rashiEntityId ? <button type="button" onClick={() => onSelect(graha.rashiEntityId!)}>{graha.rashiName}</button> : graha.rashiName}</td>
                <td>{graha.degreeInSign}</td>
                <td>{graha.houseEntityId ? <button type="button" onClick={() => onSelect(graha.houseEntityId!)}>{graha.house}</button> : "-"}</td>
                <td>{graha.nakshatraEntityId ? <button type="button" onClick={() => onSelect(graha.nakshatraEntityId!)}>{graha.nakshatra}</button> : "-"}</td>
                <td>{graha.pada ?? "-"}</td>
                {mode === "astrologer" ? <td>{statusText(graha)}</td> : null}
                {mode === "astrologer" ? <td>{graha.navamsa ?? "-"}</td> : null}
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

function selectedFacts(model: D1WorkbenchModel, entityId: EntityId | null): string[] {
  if (!entityId) return [];
  const graha = model.grahas.find((item) => item.entityId === entityId || item.placementEntityId === entityId);
  if (graha) return [`${graha.label}: ${graha.rashiName}, дом ${graha.house ?? "-"}`, `Накшатра: ${graha.nakshatra ?? "-"}`, `Статус: ${statusText(graha)}`];
  const house = model.houses.find((item) => item.houseEntityId === entityId || item.rashiEntityId === entityId);
  if (house) return [`Дом ${house.house}: ${house.rashiName}`, `Грахи: ${house.grahaCodes.join(", ") || "нет"}`];
  return [];
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