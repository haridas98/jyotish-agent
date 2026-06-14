"use client";

import { WorkflowPage } from "@/app/workflow-page";

export default function AccuracyPage() {
  return (
    <WorkflowPage
      active="accuracy"
      title="Точность"
      description="Сверка времени, летнего времени, ayanamsa, JHora, Parashara Light и внутренних расчётов."
      actionHref="/?analysis=accuracy#reports"
      actionLabel="Открыть сверку"
      eyebrow="Контроль качества"
      lead="Астросервис не может быть полезным без воспроизводимых расчётов"
      note="Здесь будет журнал сверок и расхождений, чтобы видно было, какие настройки дали результат."
      cards={[
        { label: "Время", value: "UTC, IANA timezone, историческое летнее время" },
        { label: "Модель", value: "sidereal, ayanamsa, nodes, whole sign, bhava" },
        { label: "Сверка", value: "JHora, Parashara Light, тесты backend" },
        { label: "Результат", value: "расхождение, причина, выбранное правило" },
      ]}
    />
  );
}
