"use client";

import { useEffect, useState } from "react";
import { HistoryList } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { fetchAnalysisHistory, type AnalysisHistoryItem } from "@/lib/api";

const PERSONAL_HISTORY_KINDS = "birth_chart_codex_cli,birth_chart_qwen,birth_chart_deepseek,birth_chart_nemotron";

export default function ReportsPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [status, setStatus] = useState("Загружаю историю личных обзоров...");

  useEffect(() => {
    let mounted = true;
    fetchAnalysisHistory({ kind: PERSONAL_HISTORY_KINDS, limit: 60 })
      .then((result) => {
        if (!mounted) return;
        setItems(result);
        setStatus(result.length ? `${result.length} сохранённых обзоров` : "История пока пустая");
      })
      .catch((error) => {
        if (!mounted) return;
        setStatus(error instanceof Error ? error.message : "Ошибка загрузки истории");
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <ProductShell active="reports">
      <header className="product-page-head">
        <div>
          <h1>Личные обзоры</h1>
          <p>Сохранённые AI-разборы карт, их slug и история диалогов.</p>
        </div>
        <a className="primary-link-button" href="/">Создать обзор</a>
      </header>
      <div className="product-status">{status}</div>
      <HistoryList items={items} basePath="/reports" emptyText="Личных обзоров ещё нет." />
    </ProductShell>
  );
}
