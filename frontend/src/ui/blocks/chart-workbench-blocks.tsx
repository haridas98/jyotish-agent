"use client";

import type { BirthChart, GrahaPosition, HousePlacement, VargaChart, VargaPlacement } from "@/lib/api";
import type { EntityId, NormalizedChartResult } from "@/astrology";
import { registerBlock } from "@/ui/blocks/registry";
import { EntityInspector } from "@/ui/components/EntityInspector";
import type { ViewBlockProps } from "./types";

const rashiNames = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"];
const shortBody: Record<string, string> = {
  Ascendant: "As",
  Lagna: "As",
  Sun: "Su",
  Surya: "Su",
  Moon: "Mo",
  Chandra: "Mo",
  Mars: "Ma",
  Mangala: "Ma",
  Mercury: "Me",
  Budha: "Me",
  Jupiter: "Ju",
  Guru: "Ju",
  Venus: "Ve",
  Shukra: "Ve",
  Saturn: "Sa",
  Shani: "Sa",
  Rahu: "Ra",
  Ketu: "Ke",
};

let registered = false;

export function registerChartWorkbenchBlocks() {
  if (registered) return;
  registered = true;

  registerBlock({ id: "block.profileHeader", title: "Profile header", requires: ["calc.birthData", "calc.geo"], supportedModes: ["simple", "expert"], allowedRegions: ["header"], component: ProfileHeaderBlock });
  registerBlock({ id: "block.modeSwitcher", title: "Mode switcher", requires: [], supportedModes: ["simple", "expert"], allowedRegions: ["header"], component: ModeBadgeBlock });
  registerBlock({ id: "block.calculationPresetBadge", title: "Calculation preset", requires: [], supportedModes: ["expert"], allowedRegions: ["header"], component: PresetBadgeBlock });
  registerBlock({ id: "block.chartToolbar", title: "Chart toolbar", requires: [], supportedModes: ["expert"], allowedRegions: ["header", "main"], component: ChartToolbarBlock });
  registerBlock({ id: "block.chart.main", title: "Main chart", requires: ["calc.varga.D1"], supportedModes: ["simple", "expert"], allowedRegions: ["main"], component: MainChartBlock });
  registerBlock({ id: "block.chart.vargaSelector", title: "Varga selector", requires: ["calc.varga.D1"], supportedModes: ["expert"], allowedRegions: ["main"], component: VargaSelectorBlock });
  registerBlock({ id: "block.chart.displayLayerToggles", title: "Display layers", requires: [], supportedModes: ["expert"], allowedRegions: ["main"], component: DisplayLayersBlock });
  registerBlock({ id: "block.panel.simpleSummary", title: "Simple summary", requires: ["calc.planetPositions", "calc.houses", "calc.panchanga"], supportedModes: ["simple"], allowedRegions: ["main", "bottom"], component: PanchangaStripBlock });
  registerBlock({ id: "block.panel.currentDasha", title: "Current dasha", requires: ["calc.vimshottari"], supportedModes: ["simple", "expert"], allowedRegions: ["main", "bottom"], component: CurrentDashaBlock });
  registerBlock({ id: "block.table.grahas.simple", title: "Grahas table", requires: ["calc.planetPositions", "calc.houses", "calc.nakshatras"], supportedModes: ["simple"], allowedRegions: ["bottom"], component: GrahaTableBlock });
  registerBlock({ id: "block.table.grahas", title: "Grahas table", requires: ["calc.planetPositions", "calc.houses", "calc.nakshatras", "calc.dignities"], supportedModes: ["expert"], allowedRegions: ["bottom"], component: GrahaTableBlock });
  registerBlock({ id: "block.table.bhavas.simple", title: "Bhavas table", requires: ["calc.houses"], supportedModes: ["simple"], allowedRegions: ["bottom"], component: BhavaTableBlock });
  registerBlock({ id: "block.table.bhavas", title: "Bhavas table", requires: ["calc.houses"], supportedModes: ["expert"], allowedRegions: ["bottom"], component: BhavaTableBlock });
  registerBlock({ id: "block.table.dashas", title: "Dashas table", requires: ["calc.vimshottari"], supportedModes: ["expert"], allowedRegions: ["bottom"], component: DashaTableBlock });
  registerBlock({ id: "block.panel.entityInspector", title: "Entity inspector", requires: [], supportedModes: ["simple", "expert"], allowedRegions: ["inspector"], component: InspectorBlock });
}

function sourceChart(chart: NormalizedChartResult | null): BirthChart | null {
  return chart?.sourceChart ?? null;
}

function ProfileHeaderBlock({ chart }: ViewBlockProps) {
  const birthChart = sourceChart(chart);
  return (
    <div className="v2-header-card">
      <div>
        <h1>{birthChart ? "Карта рождения" : "Карта загружается"}</h1>
        <p>{birthChart ? `${birthChart.birth.date} · ${birthChart.birth.time} · ${birthChart.place.label ?? birthChart.place.name}` : "Ожидаем расчёт"}</p>
      </div>
      <div className="v2-header-facts">
        <span>UTC {birthChart?.birth.utc_offset ?? birthChart?.birth.timezone ?? "—"}</span>
        <span>{birthChart?.settings?.ayanamsa ?? "Lahiri"}</span>
      </div>
    </div>
  );
}

function ModeBadgeBlock({ mode }: ViewBlockProps) {
  return <div className="v2-chip">{mode === "expert" ? "Астролог" : "Новичок"}</div>;
}

function PresetBadgeBlock({ chart }: ViewBlockProps) {
  const settings = sourceChart(chart)?.settings;
  return <div className="v2-chip">{settings?.calculation_model ?? "default"}</div>;
}

function ChartToolbarBlock() {
  return (
    <div className="v2-toolbar">
      <button type="button">Северный</button>
      <button type="button">Южный</button>
      <button type="button">D1</button>
      <button type="button">D9</button>
      <button type="button">D10</button>
      <button type="button">D60</button>
    </div>
  );
}

function MainChartBlock({ chart, setActiveEntityId }: ViewBlockProps) {
  const birthChart = sourceChart(chart);
  const d1 = (chart?.store["calc.varga.D1"] as VargaChart | null) ?? birthChart?.vargas?.D1 ?? null;
  const planetPlacements = d1?.placements?.length ? d1.placements : birthChart?.grahas ?? [];
  const byHouse = groupByHouse(birthChart, planetPlacements);

  if (birthChart?.ascendant) {
    byHouse.set(1, [{ ...birthChart.ascendant, body: "Ascendant" }, ...(byHouse.get(1) ?? [])]);
  }

  return (
    <section className="v2-card v2-chart-card">
      <div className="v2-card-head">
        <h2>D1 Раши</h2>
        <small>Нажмите на дом, знак или граху</small>
      </div>
      <div className="v2-north-chart">
        <svg viewBox="0 0 100 100" aria-hidden="true">
          <path d="M0 0 L100 100 M100 0 L0 100" />
          <path d="M50 0 L100 50 L50 100 L0 50 Z" />
          <path d="M0 0 L50 50 L100 0 M0 100 L50 50 L100 100" />
        </svg>
        {chartCells().map((cell) => {
          const house = birthChart?.houses.find((item) => item.house === cell.house);
          const rashiIndex = normalizeRashiIndex(house?.rashi_index) ?? cell.rashiIndex;
          return (
            <div key={cell.house} className="v2-chart-cell" style={{ left: `${cell.x}%`, top: `${cell.y}%` }}>
              <button type="button" onClick={() => setActiveEntityId(`house.${cell.house}`)}>
                {cell.house} {rashiNames[rashiIndex - 1] ?? house?.rashi ?? ""}
              </button>
              <div>
                {(byHouse.get(cell.house) ?? []).map((placement) => (
                  <button key={`${placement.body}-${cell.house}`} type="button" className="v2-planet" onClick={() => setActiveEntityId(placementEntityId(placement.body, cell.house))}>
                    {bodyShort(placement.body)} {degreeInSign(placement)}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function VargaSelectorBlock({ setActiveEntityId }: ViewBlockProps) {
  const codes = ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D20", "D24", "D30", "D60"];
  return (
    <div className="v2-varga-selector">
      {codes.map((code) => (
        <button key={code} type="button" onClick={() => setActiveEntityId(`varga.${code}`)}>
          {code}
        </button>
      ))}
    </div>
  );
}

function DisplayLayersBlock() {
  return (
    <div className="v2-layer-grid">
      {["Градусы", "Накшатры", "Пады", "Дома", "Статусы"].map((label) => (
        <label key={label}>
          <input type="checkbox" defaultChecked /> {label}
        </label>
      ))}
    </div>
  );
}

function PanchangaStripBlock({ chart, setActiveEntityId }: ViewBlockProps) {
  const birthChart = sourceChart(chart);
  return (
    <section className="v2-card">
      <div className="v2-summary-grid">
        <Fact label="Лагна" value={birthChart?.ascendant ? `${birthChart.ascendant.rashi} ${degreeInSign(birthChart.ascendant)}` : "—"} onClick={() => setActiveEntityId("house.1")} />
        <Fact label="Титхи" value={birthChart?.panchanga?.tithi?.name ?? "—"} />
        <Fact label="Вара" value={birthChart?.panchanga?.vara?.name ?? "—"} />
        <Fact label="Йога" value={birthChart?.panchanga?.yoga?.name ?? "—"} />
      </div>
    </section>
  );
}

function CurrentDashaBlock({ chart }: ViewBlockProps) {
  const dasha = sourceChart(chart)?.dashas?.vimshottari?.mahadashas?.[0];
  return (
    <section className="v2-card">
      <div className="v2-card-head">
        <h2>Даша</h2>
        <small>Vimshottari</small>
      </div>
      <p className="v2-big-value">{dasha ? `${bodyShort(dasha.lord)} · ${shortDate(dasha.starts_at)} - ${shortDate(dasha.ends_at)}` : "Нет данных"}</p>
    </section>
  );
}

function GrahaTableBlock({ chart, setActiveEntityId, mode }: ViewBlockProps) {
  const birthChart = sourceChart(chart);
  const rows = birthChart ? ([birthChart.ascendant, ...birthChart.grahas].filter(Boolean) as GrahaPosition[]) : [];
  return (
    <section className="v2-card v2-table-card">
      <div className="v2-card-head">
        <h2>Таблица D1</h2>
        <small>Кликабельные значения</small>
      </div>
      <div className="v2-table-scroll">
        <table>
          <thead>
            <tr>
              <th>Граха</th>
              <th>Градус</th>
              <th>Раши</th>
              <th>Накшатра</th>
              <th>Пада</th>
              <th>Дом</th>
              {mode === "expert" ? <th>Статус</th> : null}
              <th>D9</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const house = houseForGraha(birthChart, row);
              return (
                <tr key={`${row.body}-${row.longitude}`}>
                  <td><button type="button" onClick={() => setActiveEntityId(house ? placementEntityId(row.body, house) : grahaEntityId(row.body))}>{bodyShort(row.body)}</button></td>
                  <td>{degreeInSign(row)}</td>
                  <td><button type="button" onClick={() => setActiveEntityId(rashiEntityId(normalizeRashiIndex(row.rashi_index) ?? rashiIndexByName(row.rashi) ?? 1))}>{row.rashi}</button></td>
                  <td><button type="button" onClick={() => setActiveEntityId(`nakshatra.${row.nakshatra}`)}>{row.nakshatra}</button></td>
                  <td>{row.pada}</td>
                  <td><button type="button" onClick={() => setActiveEntityId(`house.${house ?? 1}`)}>{house ?? "—"}</button></td>
                  {mode === "expert" ? <td>{formatStatus(row)}</td> : null}
                  <td><button type="button" onClick={() => setActiveEntityId("varga.D9")}>{row.navamsa}</button></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function BhavaTableBlock({ chart, setActiveEntityId }: ViewBlockProps) {
  const houses = sourceChart(chart)?.houses ?? [];
  return (
    <section className="v2-card v2-table-card">
      <div className="v2-card-head">
        <h2>Дома</h2>
        <small>12 сфер карты</small>
      </div>
      <div className="v2-house-grid">
        {houses.map((house) => (
          <button key={house.house} type="button" onClick={() => setActiveEntityId(`house.${house.house}`)}>
            <b>{house.house}</b>
            <span>{house.rashi}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function DashaTableBlock({ chart }: ViewBlockProps) {
  const periods = sourceChart(chart)?.dashas?.vimshottari?.mahadashas?.slice(0, 9) ?? [];
  return (
    <section className="v2-card v2-table-card">
      <div className="v2-card-head">
        <h2>Даши</h2>
        <small>Mahadasha</small>
      </div>
      <div className="v2-dasha-list">
        {periods.map((period) => (
          <div key={`${period.lord}-${period.starts_at}`}>
            <b>{bodyShort(period.lord)}</b>
            <span>{shortDate(period.starts_at)} - {shortDate(period.ends_at)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function InspectorBlock({ activeEntityId }: ViewBlockProps) {
  return <EntityInspector entityId={(activeEntityId as EntityId | null) ?? null} />;
}

function Fact({ label, value, onClick }: { label: string; value: string; onClick?: () => void }) {
  return (
    <button type="button" className="v2-fact" onClick={onClick}>
      <span>{label}</span>
      <b>{value}</b>
    </button>
  );
}

function groupByHouse(chart: BirthChart | null, placements: Array<GrahaPosition | VargaPlacement>) {
  const result = new Map<number, Array<GrahaPosition | VargaPlacement>>();
  placements.forEach((placement) => {
    const house = "longitude" in placement ? houseForGraha(chart, placement) : houseForVargaPlacement(chart, placement);
    if (!house) return;
    result.set(house, [...(result.get(house) ?? []), placement]);
  });
  return result;
}

function chartCells() {
  return [
    { house: 1, rashiIndex: 1, x: 50, y: 47 },
    { house: 2, rashiIndex: 2, x: 50, y: 18 },
    { house: 3, rashiIndex: 3, x: 28, y: 28 },
    { house: 4, rashiIndex: 4, x: 18, y: 50 },
    { house: 5, rashiIndex: 5, x: 28, y: 72 },
    { house: 6, rashiIndex: 6, x: 50, y: 84 },
    { house: 7, rashiIndex: 7, x: 50, y: 68 },
    { house: 8, rashiIndex: 8, x: 72, y: 72 },
    { house: 9, rashiIndex: 9, x: 82, y: 50 },
    { house: 10, rashiIndex: 10, x: 72, y: 28 },
    { house: 11, rashiIndex: 11, x: 88, y: 18 },
    { house: 12, rashiIndex: 12, x: 12, y: 18 },
  ];
}

function bodyShort(body: string) {
  return shortBody[body] ?? body.slice(0, 2);
}

function degreeInSign(placement: Pick<GrahaPosition, "longitude"> | VargaPlacement) {
  if (!("longitude" in placement)) return "";
  const within = ((placement.longitude % 30) + 30) % 30;
  const degree = Math.floor(within);
  const minute = Math.round((within - degree) * 60);
  return `${degree.toString().padStart(2, "0")}°${minute.toString().padStart(2, "0")}'`;
}

function rashiIndexByName(name: string) {
  const normalized = name.toLowerCase();
  const names = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"];
  const index = names.findIndex((item) => item === normalized);
  return index >= 0 ? index + 1 : null;
}

function normalizeRashiIndex(index: number | null | undefined) {
  if (index === null || index === undefined) return null;
  if (index >= 0 && index <= 11) return index + 1;
  if (index >= 1 && index <= 12) return index;
  return null;
}

function rashiEntityId(index: number): EntityId {
  const names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
  return `rashi.${names[index - 1] ?? "Aries"}`;
}

function grahaEntityId(body: string): EntityId {
  const mapped: Record<string, EntityId> = { AS: "house.1", SU: "graha.SU", MO: "graha.MO", MA: "graha.MA", ME: "graha.ME", JU: "graha.JU", VE: "graha.VE", SA: "graha.SA", RA: "graha.RA", KE: "graha.KE" };
  return mapped[bodyShort(body).toUpperCase()] ?? "graha.SU";
}

function placementEntityId(body: string, house: number): EntityId {
  return `placement.${bodyShort(body).toUpperCase()}.house.${house}`;
}

function houseForGraha(chart: BirthChart | null, graha: GrahaPosition) {
  const rashiIndex = normalizeRashiIndex(graha.rashi_index) ?? rashiIndexByName(graha.rashi);
  if (!rashiIndex) return null;
  const house = chart?.houses.find((item: HousePlacement) => normalizeRashiIndex(item.rashi_index) === rashiIndex);
  return house?.house ?? null;
}

function houseForVargaPlacement(chart: BirthChart | null, placement: VargaPlacement) {
  const rashiIndex = normalizeRashiIndex(placement.rashi_index) ?? rashiIndexByName(placement.rashi);
  if (!rashiIndex) return null;
  const house = chart?.houses.find((item: HousePlacement) => normalizeRashiIndex(item.rashi_index) === rashiIndex);
  return house?.house ?? null;
}

function formatStatus(row: GrahaPosition) {
  const parts = [];
  if (row.dignity) parts.push(row.dignity);
  if (row.retrograde) parts.push("ретро");
  return parts.join(", ") || "—";
}

function shortDate(value: string) {
  return value.slice(0, 10);
}
