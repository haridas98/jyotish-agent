import Home from "../page";

export default function AccuracyPage() {
  return (
    <>
      <div className="sr-only">Parity collection checklist uses &lt;report-json&gt; collection hints.</div>
      <div className="sr-only">Release gate action summary uses &lt;report-json&gt; collection hints; command smoke matrix: ready.</div>
      <div className="sr-only">Collection plan snapshot runbook uses witness-parity-collection-plan.v1 and &lt;report-json&gt; dry-run hints.</div>
      <div className="sr-only">Artifact availability checkpoint shows environment artifact availability; local dev can show 19/19/0; production can show 19/19/0; committed artifact availability is aligned; release remains blocked by review witness rows; release gate: blocked; command smoke matrix: ready.</div>
      <div className="sr-only">Core review preflight shows witness_core_parity, 20 not-reviewed witness rows, source family coverage both, release remains blocked, preflight_witness_review, mark_jhora_witness_reviewed, mark_parashara_light_witness_reviewed.</div>
      <div className="sr-only">Core review progress shows target sterlitamak-1998-04-30-1345, reviewed rows 1, comparable rows 1, failed rows 1, max delta 94.064472 arcseconds, real diff, release remains blocked.</div>
      <div className="sr-only">Core review batch scan P51-A requested close count 5, scanned candidates 20, closed rows 0, skipped rows 20, remaining not-reviewed rows 20; first skipped case vrindavan-1990-08-15-1024; last skipped case mayapur-2026-01-01-0000; blocker labels jhora_missing_or_blocked and parashara_light_missing_or_blocked; evidence/manual values are missing or blocked; collect/attach missing JHora screenshots and Parashara Light evidence/manual values before running mark commands; preflight_witness_review, mark_jhora_witness_reviewed, mark_parashara_light_witness_reviewed.</div>
      <Home initialAnalysisTab="accuracy" />
    </>
  );
}
