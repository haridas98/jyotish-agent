import { redirect } from "next/navigation";
import {
  buildAiEligibilityPack,
  buildAiReportRequest,
  buildReportEvidencePack,
  resolveEvidenceProvenance,
  resolveReportRecipe,
  runMockAiDryRun,
} from "@/astrology";
import { debugRoutesEnabled } from "@/app/debug-route-guard";

export default function ReportMockReviewPage() {
  if (!debugRoutesEnabled()) redirect("/charts");

  const resolvedRecipe = resolveReportRecipe({
    reportTypeId: "personal_overview",
    mode: "novice",
    selectedRelationship: null,
  });
  const evidence = buildReportEvidencePack({
    resolvedRecipe,
    mode: "novice",
    primaryProfileId: "mock-review-subject",
  });
  const enriched = resolveEvidenceProvenance(evidence);
  const eligibility = buildAiEligibilityPack(enriched);
  const request = buildAiReportRequest(eligibility);
  const dryRun = runMockAiDryRun(request);

  return (
    <main style={{ background: "#eef5f4", minHeight: "100vh", padding: 24 }}>
      <section style={{ background: "#fff", border: "1px solid #d5e3e0", borderRadius: 12, margin: "0 auto", maxWidth: 1120, padding: 24 }}>
        <p style={{ color: "#00665f", fontWeight: 700, margin: 0 }}>Internal mock review</p>
        <h1 style={{ margin: "6px 0 8px" }}>Human-review экран mock-отчёта</h1>
        <p style={{ color: "#53656b", marginTop: 0 }}>
          Только offline mock: проверяем request/response/citation gate без реальной модели, без API-вызова и без сохранения ответа.
        </p>

        <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", margin: "20px 0" }}>
          <Metric label="Response gate" value={dryRun.validation.ok ? "passed" : "failed"} />
          <Metric label="Provider" value={dryRun.response.provider} />
          <Metric label="Eligible items" value={String(request.items.length)} />
          <Metric label="Excluded items" value={String(request.excludedSummary.total)} />
          <Metric label="Theses" value={String(dryRun.response.theses.length)} />
        </div>

        {dryRun.validation.ok ? null : (
          <section style={{ border: "1px solid #f2b8b5", borderRadius: 10, padding: 12 }}>
            <h2>Validation errors</h2>
            <ul>
              {dryRun.validation.errors.map((error) => (
                <li key={error}>{error}</li>
              ))}
            </ul>
          </section>
        )}

        <section style={{ display: "grid", gap: 16, gridTemplateColumns: "minmax(0, 1fr)", marginTop: 20 }}>
          {dryRun.response.theses.map((thesis) => (
            <article key={thesis.id} style={{ border: "1px solid #d5e3e0", borderRadius: 10, padding: 16 }}>
              <strong>{thesis.title}</strong>
              <p>{thesis.body}</p>
              <small>Evidence: {thesis.evidenceItemIds.join(", ")}</small>
              <ul>
                {thesis.citations.map((citation) => (
                  <li key={`${thesis.id}-${citation.evidenceItemId}-${citation.ruleId}-${citation.passageId}`}>
                    {citation.evidenceItemId} → {citation.ruleId} → {citation.passageId} → {citation.sourceId}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ background: "#f8fbfa", border: "1px solid #d5e3e0", borderRadius: 10, padding: 12 }}>
      <span style={{ color: "#60747a", display: "block", fontSize: 12 }}>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
