import { PrivateHistoryPage } from "@/app/private-history-page";

export default function TransitsPage() {
  return (
    <PrivateHistoryPage
      active="transits"
      title="Транзиты"
      actionHref="/?analysis=transits#reports"
      actionLabel="Создать"
      historyKind="current_day_transit_overview"
      basePath="/transits"
      emptyText="Обзоров текущего дня пока нет."
      authText="Войдите, чтобы видеть свои обзоры дня."
      errorText="История временно недоступна."
    />
  );
}
