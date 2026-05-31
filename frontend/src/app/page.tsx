"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  calculateBirthChart,
  searchPlaces,
  searchVLSources,
  type BirthChart,
  type DashaPeriod,
  type GrahaPosition,
  type PlaceCandidate,
  type VLSearchResult,
} from "@/lib/api";

const sourceRows = [
  ["Ayanamsa", "Lahiri", "Review required", "draft"],
  ["Chart system", "Parashara siddhanta", "Source mapping pending", "draft"],
  ["VL corpus", "Srila Prabhupada database", "Read-only link planned", "ready"],
];

function ChartPreview() {
  return (
    <div className="chart-box" aria-label="Rashi chart preview">
      <svg viewBox="0 0 600 600" role="img" aria-label="North Indian chart grid">
        <rect x="2" y="2" width="596" height="596" fill="white" stroke="#b88a2f" strokeWidth="2" />
        <path d="M2 2 L598 598 M598 2 L2 598" stroke="#c99a43" strokeWidth="1.35" />
        <path d="M300 2 L598 300 L300 598 L2 300 Z" fill="none" stroke="#c99a43" strokeWidth="1.35" />
      </svg>
    </div>
  );
}

function formatDegrees(value: number) {
  return `${value.toFixed(4)} deg`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function GrahaTable({ grahas }: { grahas: GrahaPosition[] }) {
  if (grahas.length === 0) {
    return (
      <div className="readiness-panel">
        <strong>No calculated grahas yet</strong>
        <p>The chart stays empty until the backend returns real ephemeris positions.</p>
      </div>
    );
  }

  return (
    <div className="planet-table">
      <div className="table-row table-head">
        <span>Graha</span>
        <span>Longitude</span>
        <span>Rashi</span>
        <span>Nakshatra</span>
        <span>D9</span>
      </div>
      {grahas.map((graha) => (
        <div className="table-row" key={graha.body}>
          <strong>{graha.body}</strong>
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

function DashaTimeline({ periods }: { periods: DashaPeriod[] }) {
  if (periods.length === 0) {
    return (
      <div className="pending-strip">
        Real dasha periods will appear here after Moon longitude and the Vimshottari engine are
        connected.
      </div>
    );
  }

  return (
    <div className="dasha-timeline">
      {periods.map((period) => (
        <div className="dasha-period" key={`${period.lord}-${period.starts_at}`}>
          <strong>{period.lord}</strong>
          <span>{period.duration_years.toFixed(2)}Y</span>
          <small>
            {formatDate(period.starts_at)} - {formatDate(period.ends_at)}
          </small>
        </div>
      ))}
    </div>
  );
}

export default function Home() {
  const [birthDate, setBirthDate] = useState("1990-08-15");
  const [birthTime, setBirthTime] = useState("10:24");
  const [placeName, setPlaceName] = useState("Vrindavan, Uttar Pradesh, India");
  const [placeMatches, setPlaceMatches] = useState<PlaceCandidate[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<PlaceCandidate | null>(null);
  const [chart, setChart] = useState<BirthChart | null>(null);
  const [status, setStatus] = useState("Calculation not started");
  const [sourceQuery, setSourceQuery] = useState("Krishna protects devotee");
  const [sourceResults, setSourceResults] = useState<VLSearchResult[]>([]);
  const [sourceStatus, setSourceStatus] = useState("VL search not started");

  const calculatedLabel = useMemo(() => {
    if (!chart) return "Chart will stay empty until real ephemeris positions are available.";
    return `${chart.grahas.length} grahas calculated for ${chart.place.label ?? chart.place.name}.`;
  }, [chart]);
  const vimshottariPeriods = chart?.dashas?.vimshottari?.mahadashas ?? [];
  const chartFacts = useMemo(() => {
    if (!chart) return [];
    return [
      ["Lagna", chart.ascendant?.rashi ?? "Pending"],
      ["Tithi", chart.panchanga.tithi ? `${chart.panchanga.tithi.paksha} ${chart.panchanga.tithi.name}` : "Pending"],
      ["Vara", chart.panchanga.vara?.name ?? "Pending"],
      ["Yoga", chart.panchanga.yoga?.name ?? "Pending"],
      ["Karana", chart.panchanga.karana?.name ?? "Pending"],
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

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Calculating chart...");
    try {
      const result = await calculateBirthChart({
        birth_date: birthDate,
        birth_time: birthTime,
        place_name: placeName,
      });
      setChart(result);
      setStatus("Chart calculated");
    } catch (error) {
      setChart(null);
      setStatus(error instanceof Error ? error.message : "API check failed");
    }
  }

  async function handleSourceSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSourceStatus("Searching VL...");
    try {
      const results = await searchVLSources(sourceQuery);
      setSourceResults(results);
      setSourceStatus(results.length ? `${results.length} source results` : "No VL results");
    } catch (error) {
      setSourceResults([]);
      setSourceStatus(error instanceof Error ? error.message : "VL search failed");
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="mark">Om</div>
        <div>
          <h1>Jyotish Agent</h1>
          <p>Gaudiya Siddhanta Jyotish</p>
        </div>
        <nav aria-label="Primary">
          <a className="active" href="#chart">Charts</a>
          <a href="#reports">Reports</a>
          <a href="#sources">Sources</a>
          <a href="#accuracy">Accuracy</a>
        </nav>
        <blockquote>
          yatha shastram
          <br />
          yatha guru
          <br />
          tatha siddhantah
        </blockquote>
        <div className="operator">
          <strong>Review mode</strong>
          <span>Draft rules only</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="mantra">Hare Krishna Hare Krishna Krishna Krishna Hare Hare</div>
          <div className="top-actions">
            <button type="button">Sources</button>
            <button type="button">Settings</button>
          </div>
        </header>

        <div className="content-grid">
          <section className="panel birth-panel" id="chart">
            <div className="panel-heading">
              <h2>Birth Data</h2>
              <button type="button" className="secondary-button">Load example</button>
            </div>
            <form onSubmit={handleSubmit} className="birth-form">
              <label>
                Date of Birth
                <input type="date" value={birthDate} onChange={(event) => setBirthDate(event.target.value)} />
              </label>
              <label>
                Time of Birth
                <input type="time" value={birthTime} onChange={(event) => setBirthTime(event.target.value)} />
              </label>
              <label>
                Place of Birth
                <input value={placeName} onChange={(event) => setPlaceName(event.target.value)} />
              </label>
              <div className="place-hints">
                {selectedPlace ? (
                  <button type="button" onClick={() => setPlaceName(selectedPlace.label)}>
                    {selectedPlace.label} - {selectedPlace.timezone}
                  </button>
                ) : (
                  <span>Place will be resolved on the backend.</span>
                )}
              </div>
              {placeMatches.length > 1 ? (
                <div className="place-match-list">
                  {placeMatches.slice(1, 4).map((place) => (
                    <button type="button" key={place.id} onClick={() => setPlaceName(place.label)}>
                      {place.label} - {place.timezone}
                    </button>
                  ))}
                </div>
              ) : null}
              <div className="notice">
                MVP calculation policy: Lahiri ayanamsa target, Parashara framing, citations required.
              </div>
              <button className="primary-button" type="submit">Calculate chart</button>
              <p className="status-line">{status}</p>
            </form>
          </section>

          <section className="main-stack">
            <section className="panel chart-panel">
              <div className="panel-heading">
                <h2>Rashi Chart</h2>
                <select defaultValue="D1">
                  <option>D1 Rashi</option>
                  <option>D9 Navamsa</option>
                </select>
              </div>
              <div className="chart-layout">
                <ChartPreview />
                <div className="chart-data-stack">
                  <GrahaTable grahas={chart?.grahas ?? []} />
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

            <section className="panel" id="reports">
              <div className="panel-heading">
                <h2>Vimshottari Dasha Timeline</h2>
                <span>{vimshottariPeriods.length ? "Mahadasha level, MVP engine" : "Pending Moon longitude"}</span>
              </div>
              <DashaTimeline periods={vimshottariPeriods} />
            </section>

            <section className="panel" id="sources">
              <div className="panel-heading">
                <h2>Citation & Source Status</h2>
                <button type="button" className="secondary-button">View all sources</button>
              </div>
              <form className="source-search" onSubmit={handleSourceSearch}>
                <input value={sourceQuery} onChange={(event) => setSourceQuery(event.target.value)} />
                <button type="submit" className="secondary-button">Search VL</button>
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
                    <em className={state}>{state}</em>
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
