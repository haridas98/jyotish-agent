import { PrivateHistoryPage } from "@/app/private-history-page";

export default function ReportsPage() {
  return (
    <PrivateHistoryPage
      active="reports"
      title="Личные обзоры"
      actionHref="/"
      actionLabel="Создать"
      historyKind="birth_chart_codex_cli,current_day_transit_overview"
      basePath="/reports"
      emptyText="Обзоров пока нет."
      authText="Войдите, чтобы видеть свои обзоры."
      errorText="История временно недоступна."
    />
  );
}
