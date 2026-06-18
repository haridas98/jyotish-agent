import type { ResolvedReportWarning } from "@/astrology";

export function ReportWarningList({ warnings }: { warnings: ResolvedReportWarning[] }) {
  if (!warnings.length) return null;
  return (
    <>
      {warnings.map((warning) => (
        <p key={warning.type} className="interaction-warning">
          {warning.label.ru}
        </p>
      ))}
    </>
  );
}
