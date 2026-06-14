"use client";

import { useEffect, useState } from "react";
import { GenerationJobsPanel } from "@/app/generation-jobs-ui";
import { HistoryList } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { fetchAnalysisHistory, fetchCurrentUser, type AnalysisHistoryItem } from "@/lib/api";

const CURRENT_DAY_HISTORY_KIND = "current_day_transit_overview";

function friendlyTransitHistoryError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/401|403|auth|credential|forbidden|permission/i.test(message)) {
    return "Войдите в аккаунт, чтобы увидеть свои обзоры текущих дней.";
  }
  if (/Unexpected token|JSON|API returned|fetch|network/i.test(message)) {
    return "Не удалось загрузить историю транзитов. Проверьте, что API запущен, и обновите страницу.";
  }
  return message || "Ошибка загрузки истории транзитов";
}

export default function TransitsPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [status, setStatus] = useState("Загружаю историю обзоров текущего дня...");
  const [authChecked, setAuthChecked] = useState(false);
  const [canLoadPrivateData, setCanLoadPrivateData] = useState(false);

  useEffect(() => {
    let mounted = true;
    const reloadOnAuthChanged = () => window.location.reload();
    window.addEventListener("jyotish-auth-changed", reloadOnAuthChanged);

    async function loadTransits() {
      try {
        const user = await fetchCurrentUser();
        if (!mounted) return;
        setAuthChecked(true);
        setCanLoadPrivateData(Boolean(user));
        if (!user) {
          setItems([]);
          setStatus("Войдите в аккаунт, чтобы увидеть свои обзоры текущих дней.");
          return;
        }
        const result = await fetchAnalysisHistory({ kind: CURRENT_DAY_HISTORY_KIND, limit: 60 });
        if (!mounted) return;
        setItems(result);
        setStatus(result.length ? `${result.length} сохранённых обзоров текущего дня` : "История транзитов пока пустая");
      } catch (error) {
        if (!mounted) return;
        setAuthChecked(true);
        setStatus(friendlyTransitHistoryError(error));
      }
    }

    void loadTransits();
    return () => {
      mounted = false;
      window.removeEventListener("jyotish-auth-changed", reloadOnAuthChanged);
    };
  }, []);

  const needsAuth = authChecked && !canLoadPrivateData;

  return (
    <ProductShell active="transits">
      <header className="product-page-head">
        <div>
          <h1>Транзиты</h1>
          <p>Обзоры текущего дня, гочары, краткая динамика и продолжение диалогов по сохранённым картам.</p>
        </div>
        <a className="primary-link-button" href="/?analysis=transits#reports">Создать обзор дня</a>
      </header>

      <div className="product-status">{status}</div>

      {needsAuth ? (
        <section className="history-empty private-history-gate">
          <strong>История личная</strong>
          <span>Обзоры текущего дня и диалоги показываются только владельцу аккаунта.</span>
        </section>
      ) : (
        <GenerationJobsPanel basePath="/transits" kind={CURRENT_DAY_HISTORY_KIND} title="AI-задачи текущего дня" />
      )}

      <section className="compatibility-saved-role-context" aria-label="Минимум обзора текущего дня">
        <div className="compatibility-saved-role-head">
          <div>
            <span>Перед чтением транзитов</span>
            <strong>Сначала натальная карта, потом текущий день</strong>
          </div>
          <small>Гочара читается как временный слой поверх D1, даш и ключевых домов.</small>
        </div>
        <div className="compatibility-saved-role-grid">
          <div>
            <span>Основа</span>
            <strong>D1, лагна, Луна, текущая даша</strong>
          </div>
          <div>
            <span>Текущий слой</span>
            <strong>Сатурн, Юпитер, Раху/Кету, Луна дня</strong>
          </div>
          <div>
            <span>Фокус</span>
            <strong>1, 4, 7, 10 и активные дома карты</strong>
          </div>
          <div>
            <span>Вывод</span>
            <strong>не фатальный прогноз, а рабочие акценты дня</strong>
          </div>
        </div>
      </section>

      {!needsAuth ? <HistoryList items={items} basePath="/transits" emptyText="Обзоров текущего дня ещё нет." /> : null}
    </ProductShell>
  );
}
