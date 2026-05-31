"use client";

import { FormEvent, useMemo, useState } from "react";
import { fetchEphemerisStatus, type EphemerisStatus } from "@/lib/api";

const dasha = [
  ["Ma", "6Y 2M 18D", "15 Aug 1990"],
  ["Ra", "18Y", "15 Oct 1996"],
  ["Ju", "16Y", "15 Oct 2014"],
  ["Sa", "19Y", "15 Oct 2030"],
  ["Me", "17Y", "15 Oct 2049"],
  ["Ke", "7Y", "15 Oct 2066"],
  ["Ve", "20Y", "15 Oct 2073"],
  ["Su", "6Y", "15 Oct 2093"],
  ["Mo", "10Y", "15 Oct 2099"],
];

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

export default function Home() {
  const [ephemeris, setEphemeris] = useState<EphemerisStatus | null>(null);
  const [status, setStatus] = useState("Calculation not started");

  const calculatedLabel = useMemo(() => {
    if (!ephemeris) return "Chart will stay empty until a real ephemeris provider is available.";
    if (!ephemeris.available) return "Swiss Ephemeris is not installed in this local environment.";
    return "Ephemeris provider is available; full chart calculation can be wired next.";
  }, [ephemeris]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Checking ephemeris...");
    try {
      const result = await fetchEphemerisStatus();
      setEphemeris(result);
      setStatus(result.available ? "Ephemeris available" : "Ephemeris not installed");
    } catch (error) {
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
                <input type="date" defaultValue="1990-08-15" />
              </label>
              <label>
                Time of Birth
                <input type="time" defaultValue="10:24" />
              </label>
              <label>
                Place of Birth
                <input defaultValue="Vrindavan, Uttar Pradesh, India" />
              </label>
              <label>
                Time Zone
                <select defaultValue="Asia/Kolkata">
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
                <div className="readiness-panel">
                  <strong>Calculation readiness</strong>
                  <span>{status}</span>
                  {ephemeris ? <p>{ephemeris.detail}</p> : <p>No placeholder grahas are shown.</p>}
                </div>
              </div>
              <p className="calculation-result">{calculatedLabel}</p>
            </section>

            <section className="panel" id="reports">
              <div className="panel-heading">
                <h2>Vimshottari Dasha Timeline</h2>
                <span>Balance at birth: Mars 6Y 2M 18D</span>
              </div>
              <div className="timeline">
                {dasha.map(([lord, span, date], index) => (
                  <div className={index === 0 ? "period selected" : "period"} key={lord}>
                    <strong>{lord}</strong>
                    <span>{span}</span>
                    <small>{date}</small>
                  </div>
                ))}
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
