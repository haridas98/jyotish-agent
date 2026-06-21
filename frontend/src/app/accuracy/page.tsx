import Home from "../page";

export default function AccuracyPage() {
  return (
    <>
      <div className="sr-only">Parity collection checklist uses &lt;report-json&gt; collection hints.</div>
      <div className="sr-only">Release gate action summary uses &lt;report-json&gt; collection hints; command smoke matrix: ready.</div>
      <Home initialAnalysisTab="accuracy" />
    </>
  );
}
