"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AnalysisReader } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { fetchAnalysisHistoryBySlug, type AnalysisHistoryDetail } from "@/lib/api";

function friendlyTransitError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/401|403|auth|credential|forbidden|permission/i.test(message)) {
    return "Войдите в аккаунт, чтобы открыть личный обзор текущего дня.";
  }
  if (/404|not found/i.test(message)) {
    return "Обзор текущего дня не найден или недоступен этому пользователю.";
  }
  return message || "Ошибка загрузки обзора текущего дня";
}

export default function TransitDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = Array.isArray(params.slug) ? params.slug.join("/") : params.slug;
  const [detail, setDetail] = useState<AnalysisHistoryDetail | null>(null);
  const [status, setStatus] = useState("Загружаю обзор текущего дня...");

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
        setStatus(friendlyTransitError(error));
      });
    return () => {
      mounted = false;
    };
  }, [slug]);

  return (
    <ProductShell active="transits">
      {status ? <div className="product-status">{status}</div> : null}
      {detail ? <AnalysisReader detail={detail} chatMode="current-day" /> : null}
    </ProductShell>
  );
}
