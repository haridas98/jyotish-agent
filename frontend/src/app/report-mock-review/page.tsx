import { redirect } from "next/navigation";
import {
  buildAiEligibilityPack,
  buildAiHumanReviewWorkspace,
  buildAiReportRequest,
  buildReportEvidencePack,
  resolveEvidenceProvenance,
  resolveReportRecipe,
  runMockAiDryRun,
} from "@/astrology";
import { debugRoutesEnabled } from "@/app/debug-route-guard";
import {
  buildAiReviewCalculationPromptPacket,
  buildAiReviewGroundedDraftEvaluator,
  buildAiReviewSharedResponseContractSurfaceSummary,
} from "@/lib/ai-review-quality";

export const dynamic = "force-dynamic";

const pageStyle = {
  background: "#eef5f4",
  minHeight: "100vh",
  padding: 24,
} satisfies React.CSSProperties;

const shellStyle = {
  background: "#fff",
  border: "1px solid #d5e3e0",
  borderRadius: 8,
  margin: "0 auto",
  maxWidth: 1120,
  padding: 24,
} satisfies React.CSSProperties;

const gridStyle = {
  display: "grid",
  gap: 12,
  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
  margin: "20px 0",
} satisfies React.CSSProperties;

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
  const workspace = buildAiHumanReviewWorkspace({ eligibility, request, dryRun });
  const sharedResponseContract = buildAiReviewSharedResponseContractSurfaceSummary("report-mock-review");
  const calculationPromptPacket = buildAiReviewCalculationPromptPacket(sharedResponseContract);
  const groundedDraftEvaluator = buildAiReviewGroundedDraftEvaluator(calculationPromptPacket);

  return (
    <main style={pageStyle}>
      <section style={shellStyle}>
        <p style={{ color: "#00665f", fontWeight: 700, margin: 0 }}>Internal mock review</p>
        <h1 style={{ margin: "6px 0 8px" }}>Внутреннее ревью mock-отчета</h1>
        <p style={{ color: "#53656b", marginTop: 0 }}>
          Offline mock проверяет request, response и citation gate без реальной модели, сетевого вызова и сохранения ответа.
        </p>

        <section aria-label="Gate status" style={gridStyle}>
          <Metric label="Gate status" value={workspace.status === "review_ready" ? "review ready" : "blocked"} />
          <Metric label="Provider mock" value={workspace.provider} />
          <Metric label="Report type" value={workspace.gateSummary.reportTypeId} />
          <Metric label="Recipe" value={workspace.gateSummary.reportRecipeId} />
        </section>

        <section aria-label="Evidence readiness" style={gridStyle}>
          <Metric label="Eligible evidence" value={String(workspace.evidenceSummary.eligibleCount)} />
          <Metric label="Excluded evidence" value={String(workspace.evidenceSummary.excludedCount)} />
          <Metric label="Blocked evidence" value={String(workspace.evidenceSummary.blockedCount)} />
          <Metric label="Review items" value={String(workspace.reviewItems.length)} />
        </section>

        <section aria-label="Validation summary" style={{ border: "1px solid #d5e3e0", borderRadius: 8, padding: 16 }}>
          <h2 style={{ marginTop: 0 }}>Validation summary</h2>
          <p>{workspace.validationSummary.passed ? "Response contract passed." : "Response contract blocked."}</p>
          {workspace.validationSummary.errors.length > 0 ? (
            <ul>
              {workspace.validationSummary.errors.map((error) => (
                <li key={error}>{error}</li>
              ))}
            </ul>
          ) : null}
          <div style={gridStyle}>
            <Metric label="Offline only" value={workspace.safetyFlags.offlineMockOnly ? "yes" : "no"} />
            <Metric label="Real provider call" value={workspace.safetyFlags.realProviderCalled ? "yes" : "no"} />
            <Metric label="Stored content" value={workspace.safetyFlags.rawContentStored ? "yes" : "no"} />
          </div>
        </section>

        <section
          aria-label="Shared response contract"
          data-ai-review-response-contract-shared-stage="P129-A"
          style={{ border: "1px solid #d5e3e0", borderRadius: 8, marginTop: 20, padding: 16 }}
        >
          <h2 style={{ marginTop: 0 }}>Shared response contract</h2>
          <p style={{ color: "#53656b", marginTop: 0 }}>Pre-generation quality gate, not final AI text.</p>
          <div style={gridStyle}>
            <Metric label="Sections" value={String(sharedResponseContract.sectionCount)} />
            <Metric label="Shared source" value={sharedResponseContract.aggregate.sharedSource ? "yes" : "no"} />
            <Metric label="Repair coverage status" value={sharedResponseContract.aggregate.repairGuidanceCoversFailures ? "covered" : "blocked"} />
          </div>
          <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
            {sharedResponseContract.contract.sections.map((section) => (
              <article key={section.name} style={{ background: "#f8fbfa", border: "1px solid #d5e3e0", borderRadius: 8, padding: 12 }}>
                <strong>{section.name}</strong>
                <p style={{ color: "#53656b", margin: "6px 0" }}>Required anchors: {section.requiredSourceAnchorCount}</p>
                <p style={{ color: "#53656b", margin: 0 }}>Repair coverage status: {section.repairInstruction}</p>
              </article>
            ))}
          </div>
          <p style={{ color: "#53656b", marginBottom: 0 }}>
            Failing draft coverage: generic without anchors; advanced overclaim without computed tables; advice without practical next question.
          </p>
          <span hidden>{sharedResponseContract.statusLabels.join("; ")}</span>
        </section>

        <section
          aria-label="Calculation evidence packet"
          data-ai-review-calculation-packet-stage="E130-A"
          style={{ border: "1px solid #d5e3e0", borderRadius: 8, marginTop: 20, padding: 16 }}
        >
          <h2 style={{ marginTop: 0 }}>Calculation evidence packet</h2>
          <p style={{ color: "#53656b", marginTop: 0 }}>
            Sanitized benchmark cases guide calculation focus; raw export text is not committed.
          </p>
          <div style={gridStyle}>
            <Metric label="Evidence groups" value={String(calculationPromptPacket.evidenceGroups.length)} />
            <Metric label="Sanitized benchmark cases" value={String(calculationPromptPacket.sanitizedBenchmarkCases.length)} />
            <Metric label="Prompt packet" value="not final output" />
          </div>
          <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
            {calculationPromptPacket.evidenceGroups.map((group) => (
              <article key={group.id} style={{ background: "#f8fbfa", border: "1px solid #d5e3e0", borderRadius: 8, padding: 12 }}>
                <strong>Evidence group: {group.evidenceGroup}</strong>
                <p style={{ color: "#53656b", margin: "6px 0" }}>Why it matters: {group.whyItMatters}</p>
                <p style={{ color: "#53656b", margin: "6px 0" }}>Required anchor type: {group.requiredAnchorType}</p>
                <p style={{ color: "#53656b", margin: 0 }}>
                  Benchmark-covered status: {group.benchmarkCovered ? "covered" : "missing"}
                </p>
              </article>
            ))}
          </div>
          <span hidden>{calculationPromptPacket.statusLabels.join("; ")}</span>
        </section>

        <section
          aria-label="Grounded draft evaluator"
          data-ai-review-grounded-draft-stage="P131-A"
          style={{ border: "1px solid #d5e3e0", borderRadius: 8, marginTop: 20, padding: 16 }}
        >
          <h2 style={{ marginTop: 0 }}>Grounded draft evaluator</h2>
          <p style={{ color: "#53656b", marginTop: 0 }}>Local deterministic draft gate, not final AI output.</p>
          <div style={gridStyle}>
            <Metric label="Fixtures" value={String(groundedDraftEvaluator.fixtures.length)} />
            <Metric label="Strong fixture" value={groundedDraftEvaluator.aggregate.strongPasses ? "pass" : "fail"} />
            <Metric label="Failing repairs" value={groundedDraftEvaluator.aggregate.repairsPresent ? "present" : "missing"} />
          </div>
          <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
            {groundedDraftEvaluator.evaluations.map((evaluation) => (
              <article key={evaluation.fixture.id} style={{ background: "#f8fbfa", border: "1px solid #d5e3e0", borderRadius: 8, padding: 12 }}>
                <strong>{evaluation.fixture.id}</strong>
                <p style={{ color: "#53656b", margin: "6px 0" }}>Expected result: {evaluation.fixture.expectedResult}</p>
                <p style={{ color: "#53656b", margin: "6px 0" }}>Actual result: {evaluation.passed ? "pass" : "fail"}</p>
                <p style={{ color: "#53656b", margin: "6px 0" }}>Evidence groups hit: {evaluation.evidenceGroupHits.length}</p>
                <p style={{ color: "#53656b", margin: 0 }}>
                  Repair summary: {evaluation.repairInstructions.join(" ") || "none"}
                </p>
              </article>
            ))}
          </div>
          <span hidden>{groundedDraftEvaluator.statusLabels.join("; ")}</span>
        </section>

        <section aria-label="Review items" style={{ display: "grid", gap: 16, marginTop: 20 }}>
          <h2 style={{ margin: 0 }}>Review items</h2>
          {workspace.reviewItems.map((item) => (
            <article key={item.id} style={{ border: "1px solid #d5e3e0", borderRadius: 8, padding: 16 }}>
              <strong>{item.label}</strong>
              <p>{item.body}</p>
              <p style={{ color: "#53656b", marginBottom: 8 }}>Confidence: {item.confidence}</p>
              <p style={{ marginBottom: 8 }}>Evidence ids: {item.evidenceItemIds.join(", ")}</p>
              <ul>
                {item.citationLabels.map((citation) => (
                  <li key={`${item.id}-${citation.evidenceItemId}`}>
                    {citation.evidenceItemId}: {citation.labels.join("; ")}
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
    <div style={{ background: "#f8fbfa", border: "1px solid #d5e3e0", borderRadius: 8, padding: 12 }}>
      <span style={{ color: "#60747a", display: "block", fontSize: 12 }}>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
