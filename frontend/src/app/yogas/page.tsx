"use client";

import { WorkflowPage } from "@/app/workflow-page";

export default function YogasPage() {
  return (
    <WorkflowPage
      active="yogas"
      title="Йоги"
      description="Комбинации карты, их условия, сила проявления и ссылки на расчётные основания."
      actionHref="/?analysis=yogas#reports"
      actionLabel="Открыть йоги"
      eyebrow="Комбинации"
      lead="Йога должна показывать формулу, статус проверки и практический смысл"
      note="Здесь будет отдельный каталог йог, чтобы пользователь видел не просто текст AI, а проверяемое условие."
      cards={[
        { label: "Формула", value: "какие грахи, дома и знаки образуют комбинацию" },
        { label: "Статус", value: "обнаружена, частичная, не подтверждена" },
        { label: "Сила", value: "достоинство, шадбала, аспект, варга" },
        { label: "Источник", value: "ссылка на шастрический или справочный слой" },
      ]}
    />
  );
}
