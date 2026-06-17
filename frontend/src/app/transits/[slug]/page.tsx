"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AnalysisReader } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { fetchAnalysisHistoryBySlug, type AnalysisHistoryDetail } from "@/lib/api";

function friendlyTransitError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/401|403|auth|credential|forbidden|permission/i.test(message)) {
    return "Войдите, чтобы открыть обзор.";
  }
  if (/404|not found/i.test(message)) {
    return "Обзор не найден.";
  }
  return "Не удалось открыть обзор.";
}

export default function TransitDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = Array.isArray(params.slug) ? params.slug.join("/") : params.slug;
  const [detail, setDetail] = useState<AnalysisHistoryDetail | null>(null);
  const [status, setStatus] = useState("Загружаю обзор...");

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

  const showStatus = /ошиб|не удалось|войдите|не найден|недоступ/i.test(status);

  return (
    <ProductShell active="transits">
      {showStatus ? <div className="product-status">{status}</div> : null}
      {detail ? <AnalysisReader detail={detail} chatMode="current-day" /> : null}
    </ProductShell>
  );
}
