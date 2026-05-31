"use client";

import { FormEvent, useMemo, useState } from "react";
import {
  calculateBirthChart,
  type BirthChart,
  type BirthChartRequest,
  type GrahaPosition,
} from "@/lib/api";

const sourceRows = [
  ["Ayanamsa", "Lahiri", "Review required", "draft"],
  ["Chart system", "Parashara siddhanta", "Source mapping pending", "draft"],
  ["VL corpus", "Srila Prabhupada database", "Read-only link planned", "ready"],
];

const knownPlaces: Record<string, Pick<BirthChartRequest, "latitude" | "longitude" | "timezone">> = {
  vrindavan: {
    latitude: 27.565,
    longitude: 77.6593,
    timezone: "Asia/Kolkata",
  },
};

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
  return `${value.toFixed(4)}°`;
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

export default function Home() {
  const [birthDate, setBirthDate] = useState("1990-08-15");
  const [birthTime, setBirthTime] = useState("10:24");
  const [placeName, setPlaceName] = useState("Vrindavan, Uttar Pradesh, India");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [chart, setChart] = useState<BirthChart | null>(null);
  const [status, setStatus] = useState("Calculation not started");

  const calculatedLabel = useMemo(() => {
    if (!chart) return "Chart will stay empty until real ephemeris positions are available.";
    return `${chart.grahas.length} grahas calculated for ${chart.place.name}.`;
  }, [chart]);

  function resolvePlace(): Pick<BirthChartRequest, "latitude" | "longitude" | "timezone"> | null {
    const normalized = placeName.toLowerCase();
    if (normalized.includes("vrindavan")) return knownPlaces.vrindavan;
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const place = resolvePlace();
    if (!place) {
      setStatus("Place lookup is not wired yet. Use the Vrindavan example for now.");
      setChart(null);
      return;
    }

    setStatus("Calculating chart...");
    try {
      const result = await calculateBirthChart({
        birth_date: birthDate,
        birth_time: birthTime,
        timezone: timezone || place.timezone,
        place_name: placeName,
        latitude: place.latitude,
        longitude: place.longitude,
      });
      setChart(result);
      setStatus("Chart calculated");
    } catch (error) {
      setChart(null);
      setStatus(error instanceof Error ? error.message : "API check failed");
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="mark">ॐ</div>
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
              <label>
                Time Zone
                <select value={timezone} onChange={(event) => setTimezone(event.target.value)}>
                  <option>Asia/Kolkata</option>
                  <option>Asia/Yekaterinburg</option>
                  <option>UTC</option>
                </select>
              </label>
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
                <GrahaTable grahas={chart?.grahas ?? []} />
              </div>
              <p className="calculation-result">{calculatedLabel}</p>
            </section>

            <section className="panel" id="reports">
              <div className="panel-heading">
                <h2>Vimshottari Dasha Timeline</h2>
                <span>Pending Moon longitude and dasha engine</span>
              </div>
              <div className="pending-strip">
                Real dasha periods will appear here after the Vimshottari engine is connected.
              </div>
            </section>

            <section className="panel" id="sources">
              <div className="panel-heading">
                <h2>Citation & Source Status</h2>
                <button type="button" className="secondary-button">View all sources</button>
              </div>
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
