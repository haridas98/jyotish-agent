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
type MuhurtaActionPreset = {
  id: string;
  label: string;
  focus: string;
  nextStep: string;
  attention: string;
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

const muhurtaActionPresets: MuhurtaActionPreset[] = [
  {
    id: "project_start",
    label: "Project start",
    focus: "opening work with clear owners and a realistic first milestone",
    nextStep: "confirm scope, owner, and the first checkpoint before comparing windows",
    attention: "unclear ownership or rushed kickoff details",
  },
  {
    id: "contract_signing",
    label: "Contract signing",
    focus: "signing or approval timing after terms are already reviewed",
    nextStep: "confirm document version, signers, and fallback window",
    attention: "missing approvals, unclear terms, or counterpart readiness",
  },
  {
    id: "investment_review",
    label: "Investment review",
    focus: "reviewing a commitment window without treating timing as advice",
    nextStep: "write the risk limit and independent review checkpoint",
    attention: "pressure to decide before budget and risk limits are explicit",
  },
  {
    id: "important_meeting",
    label: "Important meeting",
    focus: "planning a conversation where preparation and tone matter",
    nextStep: "prepare agenda, decision owner, and a lower-pressure backup slot",
    attention: "missing agenda, escalation pressure, or unready counterpart",
  },
  {
    id: "travel_start",
    label: "Travel start",
    focus: "choosing a departure window with logistics already visible",
    nextStep: "confirm route, buffers, documents, and contingency time",
    attention: "thin travel buffer, document gaps, or weather/logistics uncertainty",
  },
  {
    id: "product_launch",
    label: "Product launch",
    focus: "coordinating a launch window with readiness checks",
    nextStep: "confirm launch owner, rollback plan, and support coverage",
    attention: "missing support coverage, unclear rollback, or rushed readiness",
  },
];

export default function MuhurtaPage() {
  const [selectedPresetId, setSelectedPresetId] = useState(timingScenarioPresets[0]?.id ?? "");
  const [selectedActionPresetId, setSelectedActionPresetId] = useState(muhurtaActionPresets[0]?.id ?? "");
  const selectedPreset = useMemo(
    () => timingScenarioPresets.find((preset) => preset.id === selectedPresetId) ?? timingScenarioPresets[0],
    [selectedPresetId],
  );
  const selectedActionPreset = useMemo(
    () => muhurtaActionPresets.find((preset) => preset.id === selectedActionPresetId) ?? muhurtaActionPresets[0],
    [selectedActionPresetId],
  );
  const [planningContext, setPlanningContext] = useState(selectedPreset?.context ?? "");
  const [candidateWindows, setCandidateWindows] = useState<CandidateWindow[]>(defaultCandidateWindows);
  const [decisionMode, setDecisionMode] = useState<DecisionMode>("compare");
  const [constraints, setConstraints] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(constraintDefaults.map((item) => [item, false])),
  );
  const checkedConstraints = constraintDefaults.filter((item) => constraints[item]);
  const openConstraints = constraintDefaults.filter((item) => !constraints[item]);
  const missingCandidateDetails = candidateWindows.filter(
    (candidate) => !candidate.title.trim() || !candidate.date.trim() || !candidate.time.trim() || !candidate.note.trim(),
  ).length;
  const readinessStatus =
    openConstraints.length > 0 ? "Prepare first" : missingCandidateDetails > 0 || !planningContext.trim() ? "Needs details" : "Ready to compare";
  const firstCandidate = candidateWindows[0];
  const actionDecisionBrief = {
    label: selectedActionPreset?.label ?? "Custom action",
    focus: selectedActionPreset?.focus ?? "local action planning",
    contextWindow: `${firstCandidate?.date || "Missing action context"} ${firstCandidate?.time || ""}`.trim(),
    planningContext: planningContext.trim() || "Missing action context",
    nextStep: selectedActionPreset?.nextStep ?? "add practical context before comparing windows",
    attention: selectedActionPreset?.attention ?? "missing action context",
    missingCopy:
      !planningContext.trim() || missingCandidateDetails > 0
        ? "Missing action context"
        : openConstraints.length > 0
          ? "Open constraints remain"
          : "Ready for local review",
  };
  const planningBrief = {
    scenarioLabel: selectedPreset?.label ?? "Custom timing scenario",
    scenarioCategory: selectedPreset?.category ?? "custom",
    actionDecisionBrief,
    decisionMode,
    planningContext,
    candidateWindows,
    checkedConstraints,
    openConstraints,
    readinessStatus,
  };

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

        <section className="product-page-card" aria-label="Action presets">
          <div className="panel-heading">
            <div>
              <h2>Action presets</h2>
              <span>Select the practical action being timed.</span>
            </div>
          </div>
          <div className="dasha-control-bar transit-view-switch">
            {muhurtaActionPresets.map((preset) => (
              <button
                key={preset.id}
                type="button"
                className={selectedActionPresetId === preset.id ? "active" : ""}
                onClick={() => setSelectedActionPresetId(preset.id)}
              >
                {preset.label}
              </button>
            ))}
          </div>
          <p className="product-status">{selectedActionPreset?.focus}</p>
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

        <section className="product-page-card" aria-label="Planning brief">
          <div className="panel-heading">
            <div>
              <h2>Planning brief</h2>
              <span>Local review before opening `/transits`.</span>
            </div>
            <span className="product-status">{planningBrief.readinessStatus}</span>
          </div>
          <div className="dasha-toolbar">
            <div className="interaction-layer">
              <strong>Selected scenario</strong>
              <p>
                {planningBrief.scenarioLabel} · {planningBrief.scenarioCategory}
              </p>
            </div>
            <div className="interaction-layer">
              <strong>Decision mode</strong>
              <p>{planningBrief.decisionMode}</p>
            </div>
          </div>
          <div className="interaction-layer">
            <strong>Planning context</strong>
            <p>{planningBrief.planningContext || "Needs details"}</p>
          </div>
          <div className="dasha-toolbar" aria-label="Action decision brief">
            <div className="interaction-layer">
              <strong>Selected action</strong>
              <p>
                {planningBrief.actionDecisionBrief.label} В· {planningBrief.actionDecisionBrief.focus}
              </p>
            </div>
            <div className="interaction-layer">
              <strong>Current window/context</strong>
              <p>
                {planningBrief.actionDecisionBrief.contextWindow} В· {planningBrief.actionDecisionBrief.planningContext}
              </p>
            </div>
            <div className="interaction-layer">
              <strong>Practical next step</strong>
              <p>{planningBrief.actionDecisionBrief.nextStep}</p>
            </div>
            <div className="interaction-layer">
              <strong>Risk/attention point</strong>
              <p>{planningBrief.actionDecisionBrief.attention}</p>
            </div>
            <div className="interaction-layer">
              <strong>Action readiness</strong>
              <p>{planningBrief.actionDecisionBrief.missingCopy}</p>
            </div>
          </div>
          <div className="transit-table-wrap">
            <table>
              <caption>Candidate window brief</caption>
              <thead>
                <tr>
                  <th>Window</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Note</th>
                </tr>
              </thead>
              <tbody>
                {planningBrief.candidateWindows.map((candidate) => (
                  <tr key={candidate.id}>
                    <td>
                      <strong>{candidate.title || candidate.id}</strong>
                    </td>
                    <td>{candidate.date || "Needs details"}</td>
                    <td>{candidate.time || "Needs details"}</td>
                    <td>{candidate.note || "Needs details"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="dasha-toolbar">
            <div className="interaction-layer">
              <strong>Checked constraints</strong>
              <p>{planningBrief.checkedConstraints.length ? planningBrief.checkedConstraints.join(", ") : "None checked"}</p>
            </div>
            <div className="interaction-layer">
              <strong>Open constraints</strong>
              <p>{planningBrief.openConstraints.length ? planningBrief.openConstraints.join(", ") : "None open"}</p>
            </div>
          </div>
        </section>
      </section>
    </ProductShell>
  );
}
