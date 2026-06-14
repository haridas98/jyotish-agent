"use client";

import { WorkflowPage } from "@/app/workflow-page";

export default function CalculationsPage() {
  return (
    <WorkflowPage
      active="calculations"
      title="Расчёты"
      description="Таблицы D1, достоинства, сожжение, шадбала, панчанга и техническая сводка карты."
      actionHref="/#chart"
      actionLabel="Открыть карту"
      eyebrow="Рабочий порядок"
      lead="Расчёты должны быть рядом с картой, а не спрятаны в длинном отчёте"
      note="Главная таблица D1 остаётся возле схемы карты; эта страница фиксирует отдельный workflow для расчётного слоя."
      cards={[
        { label: "D1", value: "грахи, градусы, раши, накшатры, дома, D9" },
        { label: "Статусы", value: "экзальтация, дебилитация, мулатрикона, ретроградность" },
        { label: "Сила", value: "шадбала, аста, вимшопака, аштакаварга" },
        { label: "Контроль", value: "UTC, часовой пояс, айанамша, модель расчёта" },
      ]}
    />
  );
}
