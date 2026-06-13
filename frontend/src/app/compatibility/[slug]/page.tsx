"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AnalysisReader } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { fetchAnalysisHistoryBySlug, type AnalysisHistoryDetail } from "@/lib/api";

function friendlyCompatibilityError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/401|403|auth|credential|forbidden|permission/i.test(message)) {
    return "Войдите в аккаунт, чтобы открыть личный обзор совместимости.";
  }
  if (/404|not found/i.test(message)) {
    return "Обзор совместимости не найден или недоступен этому пользователю.";
  }
  return message || "Ошибка загрузки обзора";
}

export default function CompatibilityDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = Array.isArray(params.slug) ? params.slug.join("/") : params.slug;
  const [detail, setDetail] = useState<AnalysisHistoryDetail | null>(null);
  const [status, setStatus] = useState("Загружаю обзор совместимости...");

  useEffect(() => {
    let mounted = true;
    if (!slug) return;
    fetchAnalysisHistoryBySlug(slug)
      .then((result) => {
        if (!mounted) return;
        setDetail(result);
        setStatus("");
      })
      .catch((error) => {
        if (!mounted) return;
        setStatus(friendlyCompatibilityError(error));
      });
    return () => {
      mounted = false;
    };
  }, [slug]);

  const chatMode = detail ? "compatibility" : "disabled";

  return (
    <ProductShell active="compatibility">
      {status ? <div className="product-status">{status}</div> : null}
      {detail ? <AnalysisReader detail={detail} chatMode={chatMode} /> : null}
    </ProductShell>
  );
}
