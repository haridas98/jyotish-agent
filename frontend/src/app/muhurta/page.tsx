"use client";

import { WorkflowPage } from "@/app/workflow-page";

export default function MuhurtaPage() {
  return (
    <WorkflowPage
      active="muhurta"
      title="Мухурта"
      description="Выбор времени по панчанге, задаче, месту и базовым запретам неблагоприятных отрезков дня."
      actionHref="/?analysis=muhurta#reports"
      actionLabel="Открыть расчёт мухурты"
      eyebrow="Выбор времени"
      lead="Мухурта не должна быть общей датой: цель действия определяет правила оценки"
      note="Backend уже ранжирует кандидатов по панчанге и профилю задачи; этот раздел отделяет элективную работу от натальной карты."
      cards={[
        { label: "Панчанга", value: "титхи, вара, накшатра, йога, карана" },
        { label: "Задача", value: "путешествие, обучение, сделка, семейное действие" },
        { label: "Ограничения", value: "Rahu Kalam, Yamaganda, Gulika и осторожные титхи" },
        { label: "Проверка", value: "лагна окна, текущие транзиты и контекст натальной карты" },
      ]}
    />
  );
}
