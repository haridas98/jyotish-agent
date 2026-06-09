"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AnalysisReader } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { fetchAnalysisHistoryBySlug, type AnalysisHistoryDetail } from "@/lib/api";

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
        setStatus(error instanceof Error ? error.message : "Ошибка загрузки обзора");
      });
    return () => {
      mounted = false;
    };
  }, [slug]);

  const chatMode = detail?.analysis.kind === "compatibility_codex_cli" ? "compatibility" : "disabled";

  return (
    <ProductShell active="compatibility">
      {status ? <div className="product-status">{status}</div> : null}
      {detail ? <AnalysisReader detail={detail} chatMode={chatMode} /> : null}
    </ProductShell>
  );
}
