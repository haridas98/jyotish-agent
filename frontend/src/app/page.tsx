"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  generateBirthReport,
  searchPlaces,
  searchVLSources,
  type BirthReport,
  type BirthChart,
  type DashaPeriod,
  type GrahaPosition,
  type PersonSummary,
  type PlaceCandidate,
  type VargaPlacement,
  type VLSearchResult,
} from "@/lib/api";

const sourceRows = [
  ["Айанамша", "Lahiri", "Нужна проверка", "draft"],
  ["Система карты", "Парашара-сиддханта", "Сопоставление источников в работе", "draft"],
  ["Корпус VL", "База Шрилы Прабхупады", "Поиск подключён", "ready"],
];

const stateLabels: Record<string, string> = {
  draft: "черновик",
  ready: "готово",
};

const bodyLabelsRu: Record<string, string> = {
  Ascendant: "Асцендент",
  Lagna: "Лагна",
  Surya: "Сурья",
  Chandra: "Чандра",
  Mangala: "Мангала",
  Budha: "Будха",
  Guru: "Гуру",
  Shukra: "Шукра",
  Shani: "Шани",
  Rahu: "Раху",
  Ketu: "Кету",
  Moon: "Луна",
  Sun: "Солнце",
};

const summaryLabelsRu: Record<string, string> = {
  Ayanamsa: "Айанамша",
  Birth: "Рождение",
  Ephemeris: "Эфемериды",
  Karana: "Карана",
  Lagna: "Лагна",
  Moon: "Луна",
  Panchanga: "Панчанга",
  Place: "Место",
  Sun: "Солнце",
  Tithi: "Титхи",
  Vara: "Вара",
  Yoga: "Йога",
};

function labelRu(value: string) {
  return summaryLabelsRu[value] ?? bodyLabelsRu[value] ?? value;
}

function valueRu(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return "Ожидает";
  return String(value).replace(/house (\d+)/g, "дом $1");
}

function formatCoordinate(value: number) {
  return value.toFixed(4);
}

function ChartPreview() {
  return (
    <div className="chart-box" aria-label="Предпросмотр карты раши">
      <svg viewBox="0 0 600 600" role="img" aria-label="Североиндийская сетка карты">
        <rect x="2" y="2" width="596" height="596" fill="white" stroke="#b88a2f" strokeWidth="2" />
        <path d="M2 2 L598 598 M598 2 L2 598" stroke="#c99a43" strokeWidth="1.35" />
        <path d="M300 2 L598 300 L300 598 L2 300 Z" fill="none" stroke="#c99a43" strokeWidth="1.35" />
      </svg>
    </div>
  );
}

function formatDegrees(value: number) {
  return `${value.toFixed(4)}°`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function GrahaTable({ grahas }: { grahas: GrahaPosition[] }) {
  if (grahas.length === 0) {
    return (
      <div className="readiness-panel">
        <strong>Грахи ещё не рассчитаны</strong>
        <p>Карта заполнится после ответа бэкенда с эфемеридными позициями.</p>
      </div>
    );
  }

  return (
    <div className="planet-table">
      <div className="table-row table-head">
        <span>Граха</span>
        <span>Долгота</span>
        <span>Раши</span>
        <span>Накшатра</span>
        <span>D9</span>
      </div>
      {grahas.map((graha) => (
        <div className="table-row" key={graha.body}>
          <strong>{labelRu(graha.body)}</strong>
          <span>{formatDegrees(graha.longitude)}</span>
          <span>{graha.rashi}</span>
          <span>
            {graha.nakshatra} {graha.pada}
          </span>
          <span>{graha.navamsa}</span>
        </div>
      ))}
    </div>
  );
}

function VargaTable({ placements }: { placements: VargaPlacement[] }) {
  if (placements.length === 0) {
    return (
      <div className="readiness-panel">
        <strong>Положения D9 ещё не рассчитаны</strong>
        <p>Навамша появится после расчёта грах и лагны.</p>
      </div>
    );
  }

  return (
    <div className="planet-table compact-table">
      <div className="table-row table-head">
        <span>Точка</span>
        <span>Раши D9</span>
      </div>
      {placements.map((placement) => (
        <div className="table-row" key={placement.body}>
          <strong>{labelRu(placement.body)}</strong>
          <span>{placement.rashi}</span>
        </div>
      ))}
    </div>
  );
}

function DashaTimeline({ periods }: { periods: DashaPeriod[] }) {
  if (periods.length === 0) {
    return (
      <div className="pending-strip">
        Периоды даш появятся здесь после расчёта долготы Луны и движка Вимшоттари.
      </div>
    );
  }

  return (
    <div className="dasha-timeline">
      {periods.map((period) => (
        <div className="dasha-period" key={`${period.lord}-${period.starts_at}`}>
          <strong>{labelRu(period.lord)}</strong>
          <span>{period.duration_years.toFixed(2)} г.</span>
          <small>
            {formatDate(period.starts_at)} - {formatDate(period.ends_at)}
          </small>
        </div>
      ))}
    </div>
  );
}

function PersonSummaryPanel({ summary }: { summary: PersonSummary | null }) {
  if (!summary) {
    return (
      <section className="panel person-summary-panel">
        <div className="panel-heading">
          <h2>Сводка по человеку</h2>
          <span>Ожидает расчёт</span>
        </div>
        <div className="pending-strip">Основные факты рождения появятся после расчёта.</div>
      </section>
    );
  }

  return (
    <section className="panel person-summary-panel">
      <div className="panel-heading">
        <h2>Сводка по человеку</h2>
        <span>Пока только расчётные факты</span>
      </div>
      <div className="summary-content">
        <div className="summary-grid">
          {summary.core_factors.map((item) => (
            <div className="summary-card" key={item.label}>
              <span>{labelRu(item.label)}</span>
              <strong>{valueRu(item.value)}</strong>
              {item.detail ? <small>{valueRu(item.detail)}</small> : null}
            </div>
          ))}
        </div>
        <div className="summary-columns">
          <div className="summary-list">
            <h3>Контекст рождения</h3>
            {summary.birth_context.map((item) => (
              <div key={item.label}>
                <span>{labelRu(item.label)}</span>
                <strong>{valueRu(item.value)}</strong>
              </div>
            ))}
          </div>
          <div className="summary-list">
            <h3>Панчанга</h3>
            {summary.panchanga.map((item) => (
              <div key={item.label}>
                <span>{labelRu(item.label)}</span>
                <strong>{valueRu(item.value)}</strong>
              </div>
            ))}
            <div>
              <span>Даша при рождении</span>
              <strong>{summary.dasha.birth_mahadasha_lord ? labelRu(summary.dasha.birth_mahadasha_lord) : "Ожидает"}</strong>
            </div>
            <div>
              <span>Текущая махадаша</span>
              <strong>{summary.dasha.current_mahadasha ? labelRu(summary.dasha.current_mahadasha.lord) : "Ожидает"}</strong>
            </div>
            <div>
              <span>Текущая антардаша</span>
              <strong>
                {summary.dasha.current_antardasha
                  ? `${labelRu(summary.dasha.current_antardasha.parent_lord ?? "")}/${labelRu(summary.dasha.current_antardasha.lord)}`
                  : "Ожидает"}
              </strong>
            </div>
            <div>
              <span>На дату</span>
              <strong>{summary.dasha.as_of ? formatDate(summary.dasha.as_of) : "Ожидает"}</strong>
            </div>
          </div>
        </div>
        <div className="summary-table">
          <div className="summary-row summary-head">
            <span>Граха</span>
            <span>Раши</span>
            <span>Дом</span>
            <span>Накшатра</span>
            <span>D9</span>
          </div>
          {summary.graha_houses.map((row) => (
            <div className="summary-row" key={row.body}>
              <strong>{labelRu(row.body)}</strong>
              <span>{row.rashi}</span>
              <span>{row.house ?? "-"}</span>
              <span>
                {row.nakshatra} {row.pada ?? ""}
              </span>
              <span>{row.navamsa}</span>
            </div>
          ))}
        </div>
        {summary.houses.length ? (
          <div className="house-overview">
            <div>
              <h3>Обзор домов</h3>
              <span>Цельнознаковые дома</span>
            </div>
            <div className="house-grid">
              {summary.houses.map((house) => (
                <div className="house-card" key={house.house}>
                  <span>Дом {house.house}</span>
                  <strong>{house.rashi}</strong>
                  <small>{house.grahas.length ? house.grahas.map(labelRu).join(", ") : "Пусто"}</small>
                </div>
              ))}
            </div>
          </div>
        ) : null}
        {summary.dasha.current_mahadasha_antardashas.length ? (
          <div className="antardasha-panel">
            <div>
              <h3>Антардаши текущей махадаши</h3>
              <span>
                {summary.dasha.current_mahadasha ? labelRu(summary.dasha.current_mahadasha.lord) : "Ожидает"} махадаша
              </span>
            </div>
            <div className="antardasha-strip">
              {summary.dasha.current_mahadasha_antardashas.map((period) => {
                const isActive =
                  period.lord === summary.dasha.current_antardasha?.lord &&
                  period.parent_lord === summary.dasha.current_antardasha?.parent_lord;
                return (
                  <div className={isActive ? "antardasha-item active" : "antardasha-item"} key={`${period.parent_lord}-${period.lord}-${period.starts_at}`}>
                    <strong>{labelRu(period.lord)}</strong>
                    <span>{period.duration_years.toFixed(2)} г.</span>
                    <small>
                      {formatDate(period.starts_at)} - {formatDate(period.ends_at)}
                    </small>
                  </div>
                );
              })}
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}

export default function Home() {
  const [birthDate, setBirthDate] = useState("1990-08-15");
  const [birthTime, setBirthTime] = useState("10:24");
  const [placeName, setPlaceName] = useState("Вриндаван");
  const [placeMatches, setPlaceMatches] = useState<PlaceCandidate[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<PlaceCandidate | null>(null);
  const [manualTimezone, setManualTimezone] = useState("Asia/Yekaterinburg");
  const [manualLatitude, setManualLatitude] = useState("");
  const [manualLongitude, setManualLongitude] = useState("");
  const [chart, setChart] = useState<BirthChart | null>(null);
  const [chartMode, setChartMode] = useState<"D1" | "D9">("D1");
  const [birthReport, setBirthReport] = useState<BirthReport["report"] | null>(null);
  const [status, setStatus] = useState("Расчёт не запускался");
  const [sourceQuery, setSourceQuery] = useState("Krishna protects devotee");
  const [sourceResults, setSourceResults] = useState<VLSearchResult[]>([]);
  const [sourceStatus, setSourceStatus] = useState("Поиск по VL не запускался");

  const calculatedLabel = useMemo(() => {
    if (!chart) return "Карта останется пустой до расчёта эфемеридных позиций.";
    return `${chart.grahas.length} грах рассчитано для ${chart.place.label ?? chart.place.name}.`;
  }, [chart]);
  const vimshottariPeriods = chart?.dashas?.vimshottari?.mahadashas ?? [];
  const d9Placements = chart?.vargas?.D9?.placements ?? [];
  const personSummary = birthReport?.person_summary ?? null;
  const alternatePlaceMatches = useMemo(
    () => placeMatches.filter((place) => place.id !== selectedPlace?.id).slice(0, 4),
    [placeMatches, selectedPlace],
  );
  const chartFacts = useMemo(() => {
    if (!chart) return [];
    return [
      ["Лагна", chart.ascendant?.rashi ?? "Ожидает"],
      ["Титхи", chart.panchanga.tithi ? `${chart.panchanga.tithi.paksha} ${chart.panchanga.tithi.name}` : "Ожидает"],
      ["Вара", chart.panchanga.vara?.name ?? "Ожидает"],
      ["Йога", chart.panchanga.yoga?.name ?? "Ожидает"],
      ["Карана", chart.panchanga.karana?.name ?? "Ожидает"],
    ];
  }, [chart]);

  useEffect(() => {
    let cancelled = false;
    if (placeName.trim().length < 2) {
      setPlaceMatches([]);
      setSelectedPlace(null);
      return;
    }

    searchPlaces(placeName)
      .then((items) => {
        if (cancelled) return;
        setPlaceMatches(items);
        setSelectedPlace(items[0] ?? null);
      })
      .catch(() => {
        if (cancelled) return;
        setPlaceMatches([]);
        setSelectedPlace(null);
      });

    return () => {
      cancelled = true;
    };
  }, [placeName]);

  function selectPlace(place: PlaceCandidate) {
    setSelectedPlace(place);
    setPlaceName(place.label);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Формирую отчёт с приоритетом цитат...");
    try {
      const manualLat = Number(manualLatitude.replace(",", "."));
      const manualLon = Number(manualLongitude.replace(",", "."));
      const hasManualPlace = !selectedPlace && Boolean(manualTimezone.trim() && manualLatitude.trim() && manualLongitude.trim());
      if (hasManualPlace && (!Number.isFinite(manualLat) || !Number.isFinite(manualLon))) {
        setStatus("Для ручного места широта и долгота должны быть числами");
        return;
      }

      const result = await generateBirthReport({
        birth_date: birthDate,
        birth_time: birthTime,
        place_name: selectedPlace?.label ?? placeName,
        ...(selectedPlace
          ? {
              timezone: selectedPlace.timezone,
              latitude: selectedPlace.latitude,
              longitude: selectedPlace.longitude,
            }
          : hasManualPlace
            ? {
                timezone: manualTimezone.trim(),
                latitude: manualLat,
                longitude: manualLon,
              }
            : {}),
      });
      setChart(result.chart);
      setBirthReport(result.report);
      setStatus("Отчёт построен");
    } catch (error) {
      setChart(null);
      setBirthReport(null);
      setStatus(error instanceof Error ? error.message : "Ошибка API");
    }
  }

  async function handleSourceSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSourceStatus("Ищу в VL...");
    try {
      const results = await searchVLSources(sourceQuery);
      setSourceResults(results);
      setSourceStatus(results.length ? `${results.length} результатов` : "В VL ничего не найдено");
    } catch (error) {
      setSourceResults([]);
      setSourceStatus(error instanceof Error ? error.message : "Ошибка поиска VL");
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="mark">Ом</div>
        <div>
          <h1>Jyotish Agent</h1>
          <p>Гаудия-сиддханта джйотиш</p>
        </div>
        <nav aria-label="Основная навигация">
          <a className="active" href="#chart">Карты</a>
          <a href="#reports">Отчёт</a>
          <a href="#sources">Источники</a>
          <a href="#accuracy">Точность</a>
        </nav>
        <blockquote>
          yatha shastram
          <br />
          yatha guru
          <br />
          tatha siddhantah
        </blockquote>
        <div className="operator">
          <strong>Режим проверки</strong>
          <span>Только draft-правила</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="mantra">Hare Krishna Hare Krishna Krishna Krishna Hare Hare</div>
          <div className="top-actions">
            <button type="button">Источники</button>
            <button type="button">Настройки</button>
          </div>
        </header>

        <div className="content-grid">
          <section className="panel birth-panel" id="chart">
            <div className="panel-heading">
              <h2>Данные рождения</h2>
              <button type="button" className="secondary-button">Пример</button>
            </div>
            <form onSubmit={handleSubmit} className="birth-form">
              <label>
                Дата рождения
                <input type="date" value={birthDate} onChange={(event) => setBirthDate(event.target.value)} />
              </label>
              <label>
                Время рождения
                <input type="time" value={birthTime} onChange={(event) => setBirthTime(event.target.value)} />
              </label>
              <label>
                Место рождения
                <input value={placeName} onChange={(event) => setPlaceName(event.target.value)} placeholder="Город или святое место" />
              </label>
              <div className="place-resolution" aria-live="polite">
                {selectedPlace ? (
                  <>
                    <div className="place-resolution-head">
                      <span>Выбранное место</span>
                      <strong>{selectedPlace.label}</strong>
                    </div>
                    <div className="place-detail-grid">
                      <div className="place-detail-item">
                        <span>Часовой пояс</span>
                        <strong>{selectedPlace.timezone}</strong>
                      </div>
                      <div className="place-detail-item">
                        <span>Широта</span>
                        <strong>{formatCoordinate(selectedPlace.latitude)}</strong>
                      </div>
                      <div className="place-detail-item">
                        <span>Долгота</span>
                        <strong>{formatCoordinate(selectedPlace.longitude)}</strong>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="manual-place-panel">
                    <span>Каталог не нашёл точное место. Можно рассчитать вручную по IANA timezone и координатам.</span>
                    <div className="manual-place-grid">
                      <label>
                        Часовой пояс
                        <input
                          value={manualTimezone}
                          onChange={(event) => setManualTimezone(event.target.value)}
                          placeholder="Asia/Yekaterinburg"
                        />
                      </label>
                      <label>
                        Широта
                        <input
                          inputMode="decimal"
                          value={manualLatitude}
                          onChange={(event) => setManualLatitude(event.target.value)}
                          placeholder="56.8389"
                        />
                      </label>
                      <label>
                        Долгота
                        <input
                          inputMode="decimal"
                          value={manualLongitude}
                          onChange={(event) => setManualLongitude(event.target.value)}
                          placeholder="60.6057"
                        />
                      </label>
                    </div>
                  </div>
                )}
              </div>
              {alternatePlaceMatches.length ? (
                <div className="place-match-list">
                  <span>Другие совпадения</span>
                  {alternatePlaceMatches.map((place) => (
                    <button type="button" key={place.id} onClick={() => selectPlace(place)}>
                      <strong>{place.label}</strong>
                      <small>{place.timezone} · {formatCoordinate(place.latitude)}, {formatCoordinate(place.longitude)}</small>
                    </button>
                  ))}
                </div>
              ) : null}
              <div className="notice">
                Политика MVP: айанамша Lahiri, рамка Парашары, обязательные ссылки на источники.
              </div>
              <button className="primary-button" type="submit">Рассчитать карту</button>
              <p className="status-line">{status}</p>
            </form>
          </section>

          <section className="main-stack">
            <section className="panel chart-panel">
              <div className="panel-heading">
                <h2>{chartMode === "D1" ? "Карта раши" : "Карта навамши"}</h2>
                <select
                  value={chartMode}
                  onChange={(event) => setChartMode(event.target.value as "D1" | "D9")}
                >
                  <option value="D1">D1 Раши</option>
                  <option value="D9">D9 Навамша</option>
                </select>
              </div>
              <div className="chart-layout">
                <ChartPreview />
                <div className="chart-data-stack">
                  {chartMode === "D1" ? (
                    <GrahaTable grahas={chart?.grahas ?? []} />
                  ) : (
                    <VargaTable placements={d9Placements} />
                  )}
                  {chartFacts.length ? (
                    <div className="fact-grid">
                      {chartFacts.map(([label, value]) => (
                        <div className="fact-item" key={label}>
                          <span>{label}</span>
                          <strong>{value}</strong>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
              <p className="calculation-result">{calculatedLabel}</p>
            </section>

            <PersonSummaryPanel summary={personSummary} />

            <section className="panel" id="reports">
              <div className="panel-heading">
                <h2>Линия Вимшоттари-даши</h2>
                <span>{vimshottariPeriods.length ? "Уровень махадаши, MVP-движок" : "Ожидает долготу Луны"}</span>
              </div>
              <DashaTimeline periods={vimshottariPeriods} />
            </section>

            <section className="panel report-preview">
              <div className="panel-heading">
                <h2>Предпросмотр отчёта</h2>
                <span>{birthReport ? birthReport.review_status : "Отчёт ожидает расчёт"}</span>
              </div>
              {birthReport ? (
                <div className="report-sections">
                  {birthReport.sections.map((section) => (
                    <article className="report-section" key={section.key}>
                      <div>
                        <strong>{section.title}</strong>
                        <em>{section.review_status}</em>
                      </div>
                      <p>{section.body}</p>
                      {section.citations.length ? (
                        <div className="report-citations">
                          {section.citations.map((citation) => (
                            <a href={citation.public_url || "#"} key={`${section.key}-${citation.title}`} target="_blank" rel="noreferrer">
                              {citation.title || citation.work_title}
                            </a>
                          ))}
                        </div>
                      ) : null}
                    </article>
                  ))}
                </div>
              ) : (
                <div className="pending-strip">Отчёт появится после расчёта карты.</div>
              )}
            </section>

            <section className="panel" id="sources">
              <div className="panel-heading">
                <h2>Цитаты и статус источников</h2>
                <button type="button" className="secondary-button">Все источники</button>
              </div>
              <form className="source-search" onSubmit={handleSourceSearch}>
                <input value={sourceQuery} onChange={(event) => setSourceQuery(event.target.value)} />
                <button type="submit" className="secondary-button">Искать в VL</button>
                <span>{sourceStatus}</span>
              </form>
              {sourceResults.length ? (
                <div className="source-results">
                  {sourceResults.map((result) => (
                    <a href={result.public_url || "#"} key={result.id} target="_blank" rel="noreferrer">
                      <strong>{result.title || result.work_title}</strong>
                      <span>{result.work_title}</span>
                      <p>{result.body}</p>
                    </a>
                  ))}
                </div>
              ) : null}
              <div className="source-table">
                {sourceRows.map(([component, source, citation, state]) => (
                  <div className="source-row" key={component}>
                    <strong>{component}</strong>
                    <span>{source}</span>
                    <span>{citation}</span>
                    <em className={state}>{stateLabels[state] ?? state}</em>
                  </div>
                ))}
              </div>
            </section>
          </section>
        </div>
      </section>
    </main>
  );
}
