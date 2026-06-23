"use client";

import { ProductShell } from "@/app/product-shell";

const launchFacts = [
  { label: "Technical chart service", value: "Ready for private use", detail: "Saved chart create, calculate, detail, edit, and demo flows are covered by launch smoke." },
  { label: "D-scope visibility", value: "D1-D60 visible", detail: "Workbench scope matrix exposes implemented D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60 scopes." },
  { label: "AI review quality", value: "Contract gated", detail: "Audio, Telegram, JH, and PL material is witness-only; generated analysis quality is gated and not treated as finished expert output." },
  { label: "OCR literature", value: "Separate track", detail: "Book OCR, Devanagari, charts, and source artifacts stay outside the calculator launch checkpoint." },
];

const verificationRows = [
  { command: "npm.cmd run smoke:calculator-launch", purpose: "Local create/calculate/detail/edit/demo smoke with all required D-scopes." },
  { command: "npm.cmd run test:launch-readiness", purpose: "Source contract for launch guardrails, smoke coverage, and witness-only policies." },
  { command: "npm.cmd run smoke:production-live", purpose: "Read-only production health/pages/API smoke against expected deploy_commit." },
];

export default function LaunchStatusPage() {
  return (
    <ProductShell active="charts">
      <section className="charts-dashboard-head" data-launch-status-stage="E148-A">
        <div>
          <h1>Launch status</h1>
          <span>Private calculator launch checklist for the technical Jyotish chart workflow.</span>
        </div>
        <nav className="charts-quick-actions" aria-label="Launch status actions">
          <a className="primary-link-button" href="/charts/new">Create chart</a>
          <a className="secondary-button" href="/charts/demo-d1">Open demo</a>
          <a className="secondary-button" href="/charts">Charts</a>
        </nav>
      </section>

      <section className="charts-summary-grid" aria-label="Launch readiness facts">
        {launchFacts.map((fact) => (
          <div key={fact.label}>
            <span>{fact.label}</span>
            <strong>{fact.value}</strong>
            <small>{fact.detail}</small>
          </div>
        ))}
      </section>

      <section className="settings-panel" aria-label="Launch verification commands">
        <div className="settings-panel-head">
          <div>
            <h1>Verification</h1>
            <span>Run locally first; deploy checkpoints are only for meaningful batches.</span>
          </div>
        </div>
        <div className="settings-form-grid">
          {verificationRows.map((row) => (
            <div key={row.command}>
              <span>{row.command}</span>
              <strong>{row.purpose}</strong>
            </div>
          ))}
        </div>
      </section>

      <span hidden>
        launch_ready_technical_chart_service=true; d_scope_visibility=D1-D60; ai_review_quality_contract_gated=true;
        jh_pl_witness_only=true; ocr_literature_track_separate=true; production_deploy_checkpoint_visible=true;
        smoke:calculator-launch; smoke:production-live; backend_calculation_changed=false;
        production_deploy_commit_checked_by_health=true
      </span>
    </ProductShell>
  );
}
