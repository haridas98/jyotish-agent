"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { buildD1WorkbenchModel } from "@/astrology/d1-workbench";
import { D1ChartWorkbench, D1ChartWorkbenchShell } from "@/ui/d1-workbench";
import { fetchTransitWorkbench, listChartProfiles, type ChartCalculationRecord, type ChartProfile } from "@/lib/api";

function nowParts() {
  const now = new Date();
  return {
    date: now.toISOString().slice(0, 10),
    time: now.toTimeString().slice(0, 5),
  };
}

function profileMeta(profile: ChartProfile) {
  return `${profile.birth_date} · ${profile.birth_time?.slice(0, 5) ?? "время неизвестно"} · ${profile.place.label}`;
}

function transitMomentIso(date: string, time: string) {
  return `${date}T${time || "12:00"}:00`;
}

function compactNumber(value: unknown) {
  return typeof value === "number" ? Number(value.toFixed(6)) : value;
}

function displayAspectRef(ref: string | undefined) {
  if (!ref) return "-";
  const [, entity = ref] = ref.split(":");
  const [kind = "", value = entity] = entity.split(".");
  if (kind === "house") return `дом ${value}`;
  if (kind === "rashi") return `знак ${value}`;
  if (kind === "graha") return `граха ${value}`;
  if (kind === "point") return value;
  return value;
}

function displayAspectKind(kind: string | undefined) {
  if (kind === "movable_to_fixed") return "подвижный → неподвижный";
  if (kind === "fixed_to_movable") return "неподвижный → подвижный";
  if (kind === "dual_to_dual") return "двойственный → двойственный";
  return "знаковый аспект";
}

type TransitViewMode = "transit_only" | "overlay" | "side_by_side";

type GrahaDrishtiRef = {
  sourceEntityRef?: string;
  targetEntityRef?: string;
  aspectKind?: string;
  signDistance?: number;
  sourceRashiIndex?: number;
  targetRashiIndex?: number;
};

type GrahaDrishtiLayer = {
  methodId?: string;
  sourceStatus?: string;
  enabledByDefault?: boolean;
  availableInModes?: string[];
  aspectCount?: number;
  sampleRefs?: GrahaDrishtiRef[];
  items?: GrahaDrishtiRef[];
};

const RASHI_DRISHTI_METHOD_ID = "aspect.rashi_drishti.parashara.v1";

const TRANSIT_VIEW_MODES: Array<{ id: TransitViewMode; label: string }> = [
  { id: "transit_only", label: "Только транзиты" },
  { id: "overlay", label: "Натал + транзиты" },
  { id: "side_by_side", label: "Две карты рядом" },
];

export default function TransitsPage() {
  const initialNow = useMemo(() => nowParts(), []);
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [selectedChartId, setSelectedChartId] = useState<number | null>(null);
  const [date, setDate] = useState(initialNow.date);
  const [time, setTime] = useState(initialNow.time);
  const [timezone, setTimezone] = useState("Asia/Yekaterinburg");
  const [latitude, setLatitude] = useState("53.6304");
  const [longitude, setLongitude] = useState("55.9308");
  const [model, setModel] = useState<Record<string, unknown> | null>(null);
  const [viewMode, setViewMode] = useState<TransitViewMode>("transit_only");
  const [showGrahaDrishti, setShowGrahaDrishti] = useState(false);
  const [showRashiDrishti, setShowRashiDrishti] = useState(false);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listChartProfiles()
      .then((rows) => {
        setProfiles(rows);
        const first = rows[0] ?? null;
        setSelectedChartId((current) => current ?? first?.id ?? null);
        if (first) {
          setTimezone(first.timezone);
          setLatitude(String(compactNumber(first.place.latitude)));
          setLongitude(String(compactNumber(first.place.longitude)));
          setStatus("");
        } else {
          setStatus("Для работы с транзитами сначала создайте натальную карту.");
        }
      })
      .catch((error) => setStatus(error instanceof Error ? error.message : "Не удалось загрузить карты."));
  }, []);

  const selectedProfile = profiles.find((profile) => profile.id === selectedChartId) ?? null;

  const loadTransit = useCallback(async () => {
    if (!selectedChartId) return;
    setLoading(true);
    setStatus("Загружаю транзитную модель...");
    try {
      const payload = await fetchTransitWorkbench(selectedChartId, {
        at: transitMomentIso(date, time),
        timezone,
        latitude: Number(latitude),
        longitude: Number(longitude),
        scope: "d1",
      });
      setModel(payload);
      const aspectLayer = payload.aspectLayer as GrahaDrishtiLayer | undefined;
      const rashiAspectLayer = payload.rashiAspectLayer as GrahaDrishtiLayer | undefined;
      setShowGrahaDrishti(Boolean(aspectLayer?.enabledByDefault));
      setShowRashiDrishti(Boolean(rashiAspectLayer?.enabledByDefault));
      setStatus("");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Проверьте координаты и часовой пояс.");
    } finally {
      setLoading(false);
    }
  }, [date, latitude, longitude, selectedChartId, time, timezone]);

  useEffect(() => {
    if (selectedChartId) void loadTransit();
  }, [selectedChartId]);

  const setNow = () => {
    const parts = nowParts();
    setDate(parts.date);
    setTime(parts.time);
  };

  const overlay = (model?.overlay as { natalObjectCount?: number; transitObjectCount?: number; housesRelativeTo?: string } | undefined) ?? null;
  const natalModel = (model?.natal as { hasCalculation?: boolean; grahas?: unknown[]; specialPoints?: unknown[] } | undefined) ?? null;
  const aspectLayer = (model?.aspectLayer as GrahaDrishtiLayer | undefined) ?? null;
  const aspectRefs = (aspectLayer?.items?.length ? aspectLayer.items : aspectLayer?.sampleRefs) ?? [];
  const rashiAspectLayer = (model?.rashiAspectLayer as GrahaDrishtiLayer | undefined) ?? null;
  const rashiAspectRefs = (rashiAspectLayer?.items?.length ? rashiAspectLayer.items : rashiAspectLayer?.sampleRefs) ?? [];

  const d1Model = useMemo(() => {
    if (!model || !selectedProfile) return null;
    const calculation = {
      id: 0,
      status: "complete",
      calculation_version: "transit-workbench.v1",
      updated_at: String((model.transitMoment as { isoDateTime?: string } | undefined)?.isoDateTime ?? ""),
      result: {
        ascendant: (model.specialPoints as unknown[])?.[0] ?? null,
        grahas: (model.grahas as unknown[]) ?? [],
        houses: (model.houses as unknown[]) ?? [],
        settings: (model.method as Record<string, unknown>) ?? {},
        birth: {},
        place: model.location ?? {},
      },
    } as ChartCalculationRecord;
    return buildD1WorkbenchModel(selectedProfile, null, calculation, "D1");
  }, [model, selectedProfile]);

  return (
    <ProductShell active="transits">
      <section className="product-main">
        <header className="product-page-head">
          <div>
            <h1>Транзиты</h1>
            <p>Выберите карту и контрольный момент.</p>
          </div>
        </header>

        <section className="product-page-card dasha-workbench-shell" aria-label="Transit Workbench">
          <div className="dasha-toolbar">
            <label>Натальная карта
              <select value={selectedChartId ?? ""} onChange={(event) => setSelectedChartId(Number(event.target.value) || null)}>
                {profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.display_name}</option>)}
              </select>
            </label>
            <label>Дата<input type="date" value={date} onChange={(event) => setDate(event.target.value)} /></label>
            <label>Время<input type="time" value={time} onChange={(event) => setTime(event.target.value)} /></label>
            <label>Часовой пояс<input value={timezone} onChange={(event) => setTimezone(event.target.value)} /></label>
            <label>Место<input value={selectedProfile?.place.label ?? ""} readOnly /></label>
            <label>Широта<input value={latitude} onChange={(event) => setLatitude(event.target.value)} /></label>
            <label>Долгота<input value={longitude} onChange={(event) => setLongitude(event.target.value)} /></label>
          </div>
          <div className="dasha-control-bar" aria-label="Управление транзитами">
            <button type="button" onClick={setNow}>Сейчас</button>
            <button type="button" onClick={() => void loadTransit()}>Применить</button>
            <button type="button" onClick={setNow}>Вернуться к текущему моменту</button>
            <span>Стиль: Северный / Южный</span>
            <span>Режим: Новичок / Астролог</span>
            <span>Термины: RU / EN / SA / Кратко</span>
            <span>Слои: дома, знаки, грахи, Лагна, градусы, накшатры, пады</span>
          </div>
          <div className="dasha-control-bar transit-view-switch" aria-label="Режим наложения транзитов">
            {TRANSIT_VIEW_MODES.map((item) => (
              <button key={item.id} type="button" className={viewMode === item.id ? "active" : ""} onClick={() => setViewMode(item.id)}>
                {item.label}
              </button>
            ))}
          </div>
          <div className="product-status transit-overlay-contract">
            <strong>Легенда:</strong> Натал = сохранённая D1, Транзит = контрольный момент. Дома в overlay читаются от натальной карты; орбисы, прогнозы и AI не строятся.
            {overlay ? <span> Контракт: {overlay.natalObjectCount ?? 0} натальных объектов, {overlay.transitObjectCount ?? 0} транзитных объектов, один EntityInspector.</span> : null}
            {natalModel?.hasCalculation === false ? <span> Для overlay нужен сохранённый D1-расчёт.</span> : null}
          </div>
          {aspectLayer ? (
            <section className="product-status transit-aspect-layer" aria-label="Graha Drishti aspect layer">
              <div className="transit-aspect-head">
                <strong>Граха-дришти</strong>
                <span>{aspectLayer.methodId} · источник: {aspectLayer.sourceStatus === "needs_source" ? "нужен" : aspectLayer.sourceStatus ?? "нужен"} · {aspectLayer.aspectCount ?? aspectRefs.length} связей</span>
                <button type="button" onClick={() => setShowGrahaDrishti((value) => !value)}>
                  {showGrahaDrishti ? "Скрыть аспекты" : "Показать аспекты"}
                </button>
              </div>
              <p>Слой доступен в режиме астролога и выключен по умолчанию: транзит → натал, без орбисов, соединений, Раху/Кету и трактовок.</p>
              <span className="transit-aspect-meta">По умолчанию: {aspectLayer.enabledByDefault ? "включено" : "выключено"} · режим: {(aspectLayer.availableInModes ?? []).includes("astrologer") ? "астролог" : "-"}</span>
              {showGrahaDrishti ? (
                <div className="transit-aspect-lines" aria-label="Линии аспектов Graha Drishti">
                  {aspectRefs.slice(0, 24).map((item, index) => (
                    <span key={`${item.sourceEntityRef}-${item.targetEntityRef}-${item.aspectKind}-${index}`}>
                      {item.sourceEntityRef} → {item.targetEntityRef} · {item.aspectKind} · {item.signDistance}
                    </span>
                  ))}
                </div>
              ) : null}
            </section>
          ) : null}
          {rashiAspectLayer ? (
            <section className="product-status transit-aspect-layer" aria-label="Rashi Drishti aspect layer">
              <div className="transit-aspect-head">
                <strong>Раши-дришти</strong>
                <span>Проверенный источник · {rashiAspectLayer.aspectCount ?? rashiAspectRefs.length} связей · только режим астролога</span>
                <button type="button" onClick={() => setShowRashiDrishti((value) => !value)}>
                  {showRashiDrishti ? "Скрыть Раши-дришти" : "Показать Раши-дришти"}
                </button>
              </div>
              <p>Экспертный слой выключен по умолчанию: транзитный знак → натальная карта, без орбисов, соединений, прогнозов и AI. Граха-дришти считается отдельно.</p>
              <span className="transit-aspect-meta">По умолчанию: {rashiAspectLayer.enabledByDefault ? "включено" : "выключено"} · режим: {(rashiAspectLayer.availableInModes ?? []).includes("astrologer") ? "астролог" : "-"}</span>
              {showRashiDrishti ? (
                <div className="transit-aspect-lines" aria-label="Линии аспектов Rashi Drishti">
                  {rashiAspectRefs.slice(0, 24).map((item, index) => (
                    <span key={`${item.sourceEntityRef}-${item.targetEntityRef}-${item.aspectKind}-${index}`}>
                      {displayAspectRef(item.sourceEntityRef)} → {displayAspectRef(item.targetEntityRef)} · {displayAspectKind(item.aspectKind)}
                    </span>
                  ))}
                </div>
              ) : null}
            </section>
          ) : null}
          {selectedProfile ? <p className="dasha-empty-note">{profileMeta(selectedProfile)}</p> : <a href="/charts/new">Создать карту</a>}
          {status ? <div className="product-status">{status}</div> : null}
          {loading && !d1Model ? <D1ChartWorkbenchShell status="Открываю транзитную D1..." /> : null}
          {d1Model ? <D1ChartWorkbench model={d1Model} status={viewMode === "transit_only" ? "Транзитная карта D1: факты без прогнозов и AI; аспекты выключены по умолчанию." : "Режим overlay: натальные и транзитные refs разделены; открываются в одном EntityInspector."} /> : null}
        </section>
      </section>
    </ProductShell>
  );
}
