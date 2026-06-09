"use client";

import { useEffect, useState } from "react";
import { HistoryList } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { fetchAnalysisHistory, type AnalysisHistoryItem } from "@/lib/api";

export default function CompatibilityPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [status, setStatus] = useState("Загружаю историю совместимости...");

  useEffect(() => {
    let mounted = true;
    fetchAnalysisHistory({ kind: "compatibility_codex_cli", limit: 60 })
      .then((result) => {
        if (!mounted) return;
        setItems(result);
        setStatus(result.length ? `${result.length} сохранённых обзоров совместимости` : "История пока пустая");
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
    <ProductShell active="compatibility">
      <header className="product-page-head">
        <div>
          <h1>Совместимость</h1>
          <p>История парных обзоров и продолжение диалогов по сохранённым картам.</p>
        </div>
        <a className="primary-link-button" href="/#reports">Создать обзор</a>
      </header>
      <div className="product-status">{status}</div>
      <HistoryList items={items} basePath="/compatibility" emptyText="Обзоров совместимости ещё нет." />
    </ProductShell>
  );
}
