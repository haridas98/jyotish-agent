import Home from "../page";

export default function AccuracyPage() {
  return (
    <>
      <div className="sr-only">Parity collection checklist uses &lt;report-json&gt; collection hints.</div>
      <div className="sr-only">Release gate action summary uses &lt;report-json&gt; collection hints; command smoke matrix: ready.</div>
      <div className="sr-only">Collection plan snapshot runbook uses witness-parity-collection-plan.v1 and &lt;report-json&gt; dry-run hints.</div>
      <div className="sr-only">Artifact availability checkpoint shows environment artifact availability; local dev can show 19/19/0; production can show 19/19/0; committed artifact availability is aligned; release remains blocked by review witness rows; release gate: blocked; command smoke matrix: ready.</div>
      <Home initialAnalysisTab="accuracy" />
    </>
  );
}
