"use client";

import { useEffect, useState } from "react";
import { HistoryList } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import type { AppNavKey } from "@/app/app-navigation";
import { fetchAnalysisHistory, fetchCurrentUser, type AnalysisHistoryItem } from "@/lib/api";

type PrivateHistoryPageProps = {
  active: AppNavKey;
  title: string;
  actionHref: string;
  actionLabel: string;
  historyKind: string;
  basePath: "/reports" | "/compatibility" | "/transits";
  emptyText: string;
  authText: string;
  errorText: string;
  timeoutMs?: number;
};

function withTimeout<T>(promise: Promise<T>, ms?: number): Promise<T> {
  if (!ms) return promise;
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => reject(new Error("timeout")), ms);
    promise
      .then((value) => {
        window.clearTimeout(timer);
        resolve(value);
      })
      .catch((error) => {
        window.clearTimeout(timer);
        reject(error);
      });
  });
}

export function PrivateHistoryPage({
  active,
  actionHref,
  actionLabel,
  historyKind,
  basePath,
  emptyText,
  errorText,
  timeoutMs,
}: PrivateHistoryPageProps) {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [status, setStatus] = useState("");
  const [authChecked, setAuthChecked] = useState(false);
  const [needsAuth, setNeedsAuth] = useState(false);

  useEffect(() => {
    let mounted = true;
    const reloadOnAuthChanged = () => window.location.reload();
    window.addEventListener("jyotish-auth-changed", reloadOnAuthChanged);

    async function loadHistory() {
      try {
        const user = await fetchCurrentUser();
        if (!mounted) return;
        setAuthChecked(true);
        setNeedsAuth(!user);
        if (!user) {
          setItems([]);
          return;
        }
        const result = await withTimeout(fetchAnalysisHistory({ kind: historyKind, limit: 60 }), timeoutMs);
        if (!mounted) return;
        setItems(result);
      } catch {
        if (!mounted) return;
        setAuthChecked(true);
        setStatus(errorText);
      }
    }

    void loadHistory();
    return () => {
      mounted = false;
      window.removeEventListener("jyotish-auth-changed", reloadOnAuthChanged);
    };
  }, [errorText, historyKind, timeoutMs]);

  return (
    <ProductShell active={active}>
      {authChecked && !needsAuth ? (
        <div className="page-action-strip">
          <a className="primary-link-button" href={actionHref}>{actionLabel}</a>
        </div>
      ) : null}

      {status ? <div className="product-status">{status}</div> : null}

      {authChecked && needsAuth ? (
        <section className="history-empty private-history-gate">
          <span>Войдите для доступа.</span>
        </section>
      ) : null}

      {authChecked && !needsAuth ? <HistoryList items={items} basePath={basePath} emptyText={emptyText} /> : null}
    </ProductShell>
  );
}
