"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  fetchAnalysisGenerationJobs,
  type AnalysisGenerationJob,
  type AnalysisGenerationJobQuery,
} from "@/lib/api";

type GenerationJobsPanelProps = {
  basePath: "/reports" | "/compatibility" | "/transits";
  kind?: string;
  title: string;
};

const statusLabels: Record<AnalysisGenerationJob["status"], string> = {
  queued: "в очереди",
  running: "генерируется",
  complete: "готово",
  failed: "ошибка",
};

export function GenerationJobsPanel({ basePath, kind, title }: GenerationJobsPanelProps) {
  const [jobs, setJobs] = useState<AnalysisGenerationJob[]>([]);
  const [status, setStatus] = useState("Проверяю AI-задачи...");

  useEffect(() => {
    let mounted = true;
    let timer: number | undefined;

    const load = () => {
      const query: AnalysisGenerationJobQuery = { limit: 6 };
      if (kind) query.kind = kind;
      fetchAnalysisGenerationJobs(query)
        .then((result) => {
          if (!mounted) return;
          setJobs(result);
          const running = result.filter((job) => job.status === "running" || job.status === "queued").length;
          setStatus(running ? `${running} AI-задач выполняется` : result.length ? "Последние AI-задачи" : "Активных AI-задач нет");
        })
        .catch((error) => {
          if (!mounted) return;
          setStatus(error instanceof Error ? error.message : "Не удалось загрузить AI-задачи");
        });
    };

    load();
    timer = window.setInterval(load, 10000);
    return () => {
      mounted = false;
      if (timer) window.clearInterval(timer);
    };
  }, [kind]);

  const visibleJobs = jobs.filter((job) => ["queued", "running", "complete", "failed"].includes(job.status)).slice(0, 4);
  if (!visibleJobs.length) {
    return (
      <section className="generation-jobs-panel" aria-label={title}>
        <div>
          <strong>{title}</strong>
          <span>{status}</span>
        </div>
      </section>
    );
  }

  return (
    <section className="generation-jobs-panel" aria-label={title}>
      <div className="generation-jobs-head">
        <div>
          <strong>{title}</strong>
          <span>{status}</span>
        </div>
      </div>
      <div className="generation-jobs-list">
        {visibleJobs.map((job) => (
          <div className="generation-job-row" key={job.id}>
            <div>
              <em className={`generation-job-status ${job.status}`}>{statusLabels[job.status]}</em>
              <span>{formatJobSummary(job)}</span>
            </div>
            {job.analysis_slug ? (
              <Link href={`${basePath}/${job.analysis_slug}`}>Открыть</Link>
            ) : (
              <small>{formatDate(job.updated_at)}</small>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function formatJobSummary(job: AnalysisGenerationJob): string {
  const summary = job.input_summary ?? {};
  const date = typeof summary.birth_date === "string" ? summary.birth_date : "";
  const time = typeof summary.birth_time === "string" ? summary.birth_time : "";
  const place = typeof summary.place_name === "string" ? summary.place_name : "";
  const personA = recordOrNull(summary.person_a);
  const personB = recordOrNull(summary.person_b);
  if (personA || personB) {
    return [formatPersonSummary(personA), formatPersonSummary(personB)].filter(Boolean).join(" / ") || job.kind;
  }
  return [date, time, place].filter(Boolean).join(" · ") || job.kind;
}

function formatPersonSummary(value: Record<string, unknown> | null): string {
  if (!value) return "";
  return [value.birth_date, value.birth_time, value.place_name].filter((item) => typeof item === "string" && item).join(" · ");
}

function recordOrNull(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("ru-RU", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}
