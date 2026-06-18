import { redirect } from "next/navigation";
import { buildReportEvidencePack, resolveReportRecipe, validateReportEvidencePack } from "@/astrology";
import { debugRoutesEnabled } from "@/app/debug-route-guard";

export default function ReportEvidenceDebugPage() {
  if (!debugRoutesEnabled()) {
    redirect("/charts");
  }

  const resolvedRecipe = resolveReportRecipe({
    reportTypeId: "personal_overview",
    mode: "novice",
    selectedRelationship: null,
  });
  const pack = buildReportEvidencePack({
    resolvedRecipe,
    mode: "novice",
    primaryProfileId: "debug",
  });
  const validation = validateReportEvidencePack(pack);

  return (
    <main>
      <h1>Report Evidence Debug</h1>
      <p>{validation.ok ? "valid" : validation.errors.join("; ")}</p>
      <pre>{JSON.stringify(pack, null, 2)}</pre>
    </main>
  );
}
