"use client";

import { WorkflowPage } from "@/app/workflow-page";

export default function DashasPage() {
  return (
    <WorkflowPage
      active="timeline"
      title="Даши"
      description="Периоды времени, подпериоды и привязка текущих событий к натальной карте."
      actionHref="/?analysis=timeline#reports"
      actionLabel="Открыть даши"
      eyebrow="Временной слой"
      lead="Сначала карта и Луна, затем период, подпериод и подтверждение транзитами"
      note="Раздел выделен отдельно, чтобы позже расширить его до полноценной временной ленты и мобильного сценария."
      cards={[
        { label: "Основной метод", value: "Вимшоттари как первый рабочий слой" },
        { label: "Проверка", value: "махадаша, антардаша, пратьянтардаша" },
        { label: "Контекст", value: "управители домов, положение в D1 и D9" },
        { label: "Будущее", value: "отдельные системы периодов и сравнение методов" },
      ]}
    />
  );
}
