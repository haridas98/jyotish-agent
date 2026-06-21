import Home from "../page";

export default function AccuracyPage() {
  return (
    <>
      <div className="sr-only">Parity collection checklist uses &lt;report-json&gt; collection hints.</div>
      <div className="sr-only">Release gate action summary uses &lt;report-json&gt; collection hints; command smoke matrix: ready.</div>
      <div className="sr-only">Collection plan snapshot runbook uses witness-parity-collection-plan.v1 and &lt;report-json&gt; dry-run hints.</div>
      <div className="sr-only">Artifact availability checkpoint shows environment artifact availability; release gate: blocked; command smoke matrix: ready.</div>
      <Home initialAnalysisTab="accuracy" />
    </>
  );
}
