"use client";

import { WorkflowPage } from "@/app/workflow-page";

export default function SourcesPage() {
  return (
    <WorkflowPage
      active="sources"
      title="Источники"
      description="Локальная библиотека, шлоки, переводы, OCR и ссылки, на которые опирается AI-разбор."
      actionHref="/?analysis=sources#reports"
      actionLabel="Открыть источники"
      eyebrow="Авторитетность"
      lead="Интерпретация должна иметь проверяемую опору, а не быть произвольным текстом"
      note="Раздел отделён под будущую библиотеку BPHS, Jaimini, справочники и локальные OCR-материалы."
      cards={[
        { label: "Тексты", value: "санскрит, транслитерация, перевод, комментарий" },
        { label: "Локально", value: "книги и OCR должны храниться в проектной библиотеке" },
        { label: "Проверка", value: "сверка фрагментов между OCR, интернетом и ручной разметкой" },
        { label: "AI", value: "обзор с цитатой, смыслом и указанием степени уверенности" },
      ]}
    />
  );
}
