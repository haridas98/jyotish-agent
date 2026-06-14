"use client";

import { WorkflowPage } from "@/app/workflow-page";

export default function VargasPage() {
  return (
    <WorkflowPage
      active="vargas"
      title="D-карты"
      description="Отдельный рабочий слой для варг: D1-D60, назначение каждой карты и связь с основной Rashi."
      actionHref="/#varga-charts"
      actionLabel="Открыть атлас D-карт"
      eyebrow="Дробные карты"
      lead="Варга читается только вместе с D1 и вопросом, ради которого она открыта"
      note="Этот раздел отделяет навигацию по D-картам от главной формы рождения и готовит место для полноценного атласа."
      cards={[
        { label: "D1", value: "основа карты, тело, характер, дома" },
        { label: "D9", value: "дхарма, брак, внутренняя сила положения" },
        { label: "D10", value: "карьера, статус, действие в мире" },
        { label: "D12", value: "родители, род, наследственные темы" },
        { label: "D30", value: "риски, слабые места, скрытые напряжения" },
        { label: "D60", value: "тонкий кармический слой, требует точного времени" },
      ]}
    />
  );
}
