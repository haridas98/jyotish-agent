"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { timingScenarioPresets, type TimingScenarioPreset } from "@/astrology/timing/timingScenarioPresets";

type DecisionMode = "compare" | "postpone" | "prepare";
type CandidateWindow = {
  id: string;
  title: string;
  date: string;
  time: string;
  note: string;
};

const decisionModes: Array<{ id: DecisionMode; label: string }> = [
  { id: "compare", label: "compare" },
  { id: "postpone", label: "postpone" },
  { id: "prepare", label: "prepare" },
];

const defaultCandidateWindows: CandidateWindow[] = [
  { id: "candidate_1", title: "Window A", date: "", time: "", note: "Primary option to compare." },
  { id: "candidate_2", title: "Window B", date: "", time: "", note: "Fallback or lower-pressure option." },
  { id: "candidate_3", title: "Window C", date: "", time: "", note: "Later option if preparation is incomplete." },
];

const constraintDefaults = [
  "approvals",
  "documents",
  "budget/risk limit",
  "travel/logistics",
  "counterpart readiness",
];

export default function MuhurtaPage() {
  const [selectedPresetId, setSelectedPresetId] = useState(timingScenarioPresets[0]?.id ?? "");
  const selectedPreset = useMemo(
    () => timingScenarioPresets.find((preset) => preset.id === selectedPresetId) ?? timingScenarioPresets[0],
    [selectedPresetId],
  );
  const [planningContext, setPlanningContext] = useState(selectedPreset?.context ?? "");
  const [candidateWindows, setCandidateWindows] = useState<CandidateWindow[]>(defaultCandidateWindows);
  const [decisionMode, setDecisionMode] = useState<DecisionMode>("compare");
  const [constraints, setConstraints] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(constraintDefaults.map((item) => [item, false])),
  );

  function applyPreset(preset: TimingScenarioPreset) {
    setSelectedPresetId(preset.id);
    setPlanningContext(preset.context);
  }

  function updateCandidate(id: string, field: keyof CandidateWindow, value: string) {
    setCandidateWindows((current) => current.map((row) => (row.id === id ? { ...row, [field]: value } : row)));
  }

  return (
    <ProductShell active="muhurta">
      <section className="product-main">
        <header className="product-page-head">
          <div>
            <h1>Muhurta planning</h1>
            <p>Timing planning workspace for comparing practical windows before continuing into transit review.</p>
          </div>
          <Link className="secondary-button" href="/transits">
            Continue in transits
          </Link>
        </header>

        <section className="product-page-card" aria-label="Timing scenario presets">
          <div className="panel-heading">
            <div>
              <h2>Scenario preset</h2>
              <span>Select a planning context, then edit it.</span>
            </div>
          </div>
          <div className="dasha-control-bar transit-view-switch">
            {timingScenarioPresets.map((preset) => (
              <button
                key={preset.id}
                type="button"
                className={selectedPresetId === preset.id ? "active" : ""}
                onClick={() => applyPreset(preset)}
              >
                {preset.label}
              </button>
            ))}
          </div>
          <div className="dasha-control-bar">
            {(selectedPreset?.planningFactors ?? []).map((factor) => (
              <span key={factor}>{factor}</span>
            ))}
          </div>
          <label>
            Planning context
            <textarea value={planningContext} onChange={(event) => setPlanningContext(event.target.value)} />
          </label>
        </section>

        <section className="product-page-card" aria-label="Candidate windows">
          <div className="panel-heading">
            <div>
              <h2>Candidate windows</h2>
              <span>Keep at least three local options before comparing in `/transits`.</span>
            </div>
          </div>
          <div className="dasha-toolbar">
            {candidateWindows.map((candidate) => (
              <div key={candidate.id} className="interaction-layer">
                <label>
                  Title
                  <input value={candidate.title} onChange={(event) => updateCandidate(candidate.id, "title", event.target.value)} />
                </label>
                <label>
                  Date
                  <input type="date" value={candidate.date} onChange={(event) => updateCandidate(candidate.id, "date", event.target.value)} />
                </label>
                <label>
                  Time
                  <input type="time" value={candidate.time} onChange={(event) => updateCandidate(candidate.id, "time", event.target.value)} />
                </label>
                <label>
                  Note
                  <textarea value={candidate.note} onChange={(event) => updateCandidate(candidate.id, "note", event.target.value)} />
                </label>
              </div>
            ))}
          </div>
        </section>

        <section className="product-page-card" aria-label="Decision controls">
          <div className="panel-heading">
            <div>
              <h2>Decision mode</h2>
              <span>Use this as a planning stance, not a final decision.</span>
            </div>
          </div>
          <div className="dasha-control-bar transit-view-switch">
            {decisionModes.map((mode) => (
              <button key={mode.id} type="button" className={decisionMode === mode.id ? "active" : ""} onClick={() => setDecisionMode(mode.id)}>
                {mode.label}
              </button>
            ))}
          </div>
          <div className="dasha-control-bar">
            {constraintDefaults.map((item) => (
              <label key={item}>
                <input
                  type="checkbox"
                  checked={Boolean(constraints[item])}
                  onChange={(event) => setConstraints((current) => ({ ...current, [item]: event.target.checked }))}
                />
                {item}
              </label>
            ))}
          </div>
          <p className="product-status">
            Current mode: {decisionMode}. Use candidate notes and constraints to prepare questions before opening the transit workbench.
          </p>
        </section>
      </section>
    </ProductShell>
  );
}
