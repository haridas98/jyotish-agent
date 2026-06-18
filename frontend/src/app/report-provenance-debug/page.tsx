import { redirect } from "next/navigation";
import {
  buildReportEvidencePack,
  resolveEvidenceProvenance,
  resolveReportRecipe,
  validatePassageRegistry,
  validateRuleRegistry,
  validateSourceRegistry,
} from "@/astrology";
import { debugRoutesEnabled } from "@/app/debug-route-guard";

export default function ReportProvenanceDebugPage() {
  if (!debugRoutesEnabled()) redirect("/charts");

  const resolvedRecipe = resolveReportRecipe({
    reportTypeId: "personal_overview",
    mode: "novice",
    selectedRelationship: null,
  });
  const evidence = buildReportEvidencePack({
    resolvedRecipe,
    mode: "novice",
    primaryProfileId: "debug",
  });
  const enriched = resolveEvidenceProvenance(evidence);
  const validationErrors = [...validateSourceRegistry(), ...validatePassageRegistry(), ...validateRuleRegistry()];

  return (
    <main style={{ padding: 24 }}>
      <h1>Report Provenance Debug</h1>
      <p>{validationErrors.length ? validationErrors.join("; ") : "valid"}</p>
      <pre>{JSON.stringify(enriched, null, 2)}</pre>
    </main>
  );
}
