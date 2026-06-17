import { PrivateHistoryPage } from "@/app/private-history-page";

export default function CompatibilityPage() {
  return (
    <PrivateHistoryPage
      active="compatibility"
      title="Совместимость"
      actionHref="/?analysis=compatibility#reports"
      actionLabel="Создать"
      historyKind="compatibility_codex_cli"
      basePath="/compatibility"
      emptyText="Обзоров совместимости пока нет."
      authText="Войдите, чтобы видеть свои пары."
      errorText="История временно недоступна."
      timeoutMs={7000}
    />
  );
}
