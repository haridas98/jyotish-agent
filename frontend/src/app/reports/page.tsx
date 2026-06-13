"use client";

import { useEffect, useState } from "react";
import { GenerationJobsPanel } from "@/app/generation-jobs-ui";
import { HistoryList } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { HelpTerm, HouseTerms, VargaTerms } from "@/app/relationship-help";
import { fetchAnalysisHistory, type AnalysisHistoryItem } from "@/lib/api";

const PERSONAL_HISTORY_KINDS = "birth_chart_codex_cli,current_day_transit_overview";

const personalReviewHelp = {
  shadbala: {
    title: "Шадбала",
    text: "Расчётная сила грах. В личном обзоре помогает отличить яркую тему карты от слабой или требующей компенсации.",
  },
  dasha: {
    title: "Даша",
    text: "Период планеты, который показывает, какие темы карты активны сейчас и в ближайшие годы.",
  },
  combustion: {
    title: "Сожжение / аста",
    text: "Граха близко к Солнцу. Её качество может проявляться напряжённее, скрытнее или через внутреннюю работу.",
  },
  dignity: {
    title: "Достоинство грахи",
    text: "Экзальтация, дебилитация, мулатрикона, собственный или враждебный знак показывают качество проявления планеты.",
  },
};

function friendlyHistoryError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/401|403|auth|credential|forbidden|permission/i.test(message)) {
    return "Войдите в аккаунт, чтобы увидеть свои личные обзоры.";
  }
  if (/Unexpected token|JSON|API returned|fetch|network/i.test(message)) {
    return "Не удалось загрузить историю. Проверьте, что API запущен, и обновите страницу.";
  }
  return message || "Ошибка загрузки истории";
}

export default function ReportsPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [status, setStatus] = useState("Загружаю историю личных обзоров...");

  useEffect(() => {
    let mounted = true;
    const reloadOnAuthChanged = () => window.location.reload();
    window.addEventListener("jyotish-auth-changed", reloadOnAuthChanged);
    fetchAnalysisHistory({ kind: PERSONAL_HISTORY_KINDS, limit: 60 })
      .then((result) => {
        if (!mounted) return;
        setItems(result);
        setStatus(result.length ? `${result.length} сохранённых обзоров` : "История пока пустая");
      })
      .catch((error) => {
        if (!mounted) return;
        setStatus(friendlyHistoryError(error));
      });
    return () => {
      mounted = false;
      window.removeEventListener("jyotish-auth-changed", reloadOnAuthChanged);
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
      <GenerationJobsPanel basePath="/reports" kind="birth_chart_codex_cli" title="AI-задачи личных обзоров" />
      <section className="compatibility-saved-role-context" aria-label="Минимум личного обзора">
        <div className="compatibility-saved-role-head">
          <div>
            <span>Минимум перед личным AI-разбором</span>
            <strong>Что астролог проверяет первым</strong>
          </div>
          <small>Эти опоры должны быть видны до чтения длинного текста обзора.</small>
        </div>
        <div className="compatibility-saved-role-grid">
          <div>
            <span>Основа D1</span>
            <strong><HouseTerms houses={[1, 5, 9, 10]} /></strong>
          </div>
          <div>
            <span>Быт и отношения</span>
            <strong><HouseTerms houses={[2, 4, 7, 12]} /></strong>
          </div>
          <div>
            <span>Ключевые D-карты</span>
            <strong><VargaTerms vargas={["D1", "D9", "D10", "D12", "D30", "D60"]} /></strong>
          </div>
          <div>
            <span>Расчётные проверки</span>
            <strong>
              <HelpTerm item={personalReviewHelp.shadbala}>Шадбала</HelpTerm>{" "}
              <HelpTerm item={personalReviewHelp.dasha}>Даши</HelpTerm>{" "}
              <HelpTerm item={personalReviewHelp.combustion}>Аста</HelpTerm>{" "}
              <HelpTerm item={personalReviewHelp.dignity}>Статусы</HelpTerm>
            </strong>
          </div>
        </div>
      </section>
      <HistoryList items={items} basePath="/reports" emptyText="Личных обзоров ещё нет." />
    </ProductShell>
  );
}
