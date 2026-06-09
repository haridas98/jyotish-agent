"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import {
  askBirthCodexAnalysis,
  askCompatibilityCodexAnalysis,
  type AnalysisHistoryDetail,
  type AnalysisHistoryItem,
  type CodexAnalysisChatMessage,
  type GeneratedDraftAnalysis,
} from "@/lib/api";

type HistoryListProps = {
  items: AnalysisHistoryItem[];
  basePath: "/reports" | "/compatibility";
  emptyText: string;
};

type AnalysisReaderProps = {
  detail: AnalysisHistoryDetail;
  chatMode: "birth" | "compatibility" | "disabled";
};

type AnalysisSection = GeneratedDraftAnalysis["sections"][number];

export function HistoryList({ items, basePath, emptyText }: HistoryListProps) {
  if (!items.length) {
    return <div className="history-empty">{emptyText}</div>;
  }

  return (
    <div className="history-list">
      {items.map((item) => (
        <Link href={`${basePath}/${item.slug}`} className="history-row" key={item.id}>
          <div>
            <strong>{formatHistoryTitle(item)}</strong>
            <span>{formatSnapshot(item.input_snapshot)}</span>
            {item.excerpt ? <p>{item.excerpt}</p> : null}
          </div>
          <aside>
            <span>{formatDate(item.created_at)}</span>
            <small>{item.section_count} разд. · {item.chat_count} диал.</small>
          </aside>
        </Link>
      ))}
    </div>
  );
}

export function AnalysisReader({ detail, chatMode }: AnalysisReaderProps) {
  const output = detail.analysis.output_json;
  const sections = useMemo(
    () => (Array.isArray(output?.sections) ? (output.sections as AnalysisSection[]) : []),
    [output],
  );

  return (
    <div className="analysis-reader">
      <header className="analysis-hero">
        <div>
          <Link href={chatMode === "compatibility" ? "/compatibility" : "/reports"}>← Назад</Link>
          <h1>{formatHistoryTitle(detail.analysis)}</h1>
          <p>{formatSnapshot(detail.analysis.input_snapshot)}</p>
        </div>
        <dl>
          <div>
            <dt>Дата</dt>
            <dd>{formatDate(detail.analysis.created_at)}</dd>
          </div>
          <div>
            <dt>Slug</dt>
            <dd>{detail.analysis.slug}</dd>
          </div>
          <div>
            <dt>Статус</dt>
            <dd>{detail.analysis.review_status}</dd>
          </div>
        </dl>
      </header>

      <section className="analysis-body">
        {sections.length ? (
          sections.map((section, index) => (
            <article className="analysis-section" key={`${section.title}-${index}`}>
              <div>
                <h2>{section.title || `Раздел ${index + 1}`}</h2>
                {section.citation_titles?.length ? <span>{section.citation_titles.length} источн.</span> : null}
              </div>
              <p>{section.body}</p>
              {section.key_points?.length ? (
                <ul>
                  {section.key_points.map((point) => <li key={point}>{point}</li>)}
                </ul>
              ) : null}
              {section.practical_steps?.length ? (
                <div className="analysis-steps">
                  <strong>Практика</strong>
                  {section.practical_steps.map((step) => <span key={step}>{step}</span>)}
                </div>
              ) : null}
            </article>
          ))
        ) : (
          <div className="history-empty">В записи нет разделов отчёта.</div>
        )}
      </section>

      <AnalysisChatBox
        analysisId={detail.analysis.id}
        initialMessages={detail.chat_messages}
        mode={chatMode}
      />
    </div>
  );
}

function AnalysisChatBox({
  analysisId,
  initialMessages,
  mode,
}: {
  analysisId: number;
  initialMessages: CodexAnalysisChatMessage[];
  mode: "birth" | "compatibility" | "disabled";
}) {
  const [messages, setMessages] = useState<CodexAnalysisChatMessage[]>(initialMessages);
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState(
    mode === "disabled" ? "Диалог пока доступен только для Codex-обзоров." : "Можно задать вопрос по сохранённому обзору.",
  );
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanQuestion = question.trim();
    if (!cleanQuestion || mode === "disabled" || busy) return;
    const nextMessages = [...messages, { role: "user" as const, content: cleanQuestion }];
    setMessages(nextMessages);
    setQuestion("");
    setBusy(true);
    setStatus("Готовлю ответ по сохранённому обзору...");
    try {
      const result =
        mode === "compatibility"
          ? await askCompatibilityCodexAnalysis(analysisId, cleanQuestion, nextMessages)
          : await askBirthCodexAnalysis(analysisId, cleanQuestion, nextMessages);
      setMessages([...nextMessages, { role: "assistant", content: result.answer }]);
      setStatus("Ответ сохранён в истории диалога.");
    } catch (error) {
      setMessages([
        ...nextMessages,
        { role: "assistant", content: error instanceof Error ? error.message : "Ошибка ответа" },
      ]);
      setStatus("Не удалось получить ответ.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="analysis-chat">
      <div className="analysis-chat-head">
        <h2>Диалог</h2>
        <span>{status}</span>
      </div>
      <div className="analysis-chat-thread">
        {messages.length ? (
          messages.map((message, index) => (
            <div className={`chat-message ${message.role}`} key={`${message.role}-${index}`}>
              <strong>{message.role === "user" ? "Вопрос" : "Ответ"}</strong>
              <p>{message.content}</p>
            </div>
          ))
        ) : (
          <div className="history-empty">История диалога пока пустая.</div>
        )}
      </div>
      <form className="analysis-chat-form" onSubmit={handleSubmit}>
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={mode === "disabled" || busy}
          placeholder="Вопрос по этому обзору"
        />
        <button type="submit" disabled={mode === "disabled" || busy || !question.trim()}>
          Спросить
        </button>
      </form>
    </section>
  );
}

function formatHistoryTitle(item: AnalysisHistoryItem) {
  return item.engine_label || item.first_section_title || `Обзор #${item.id}`;
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatSnapshot(snapshot: Record<string, unknown>) {
  const personA = snapshot.person_a;
  const personB = snapshot.person_b;
  if (isRecord(personA) || isRecord(personB)) {
    return [formatBirthSnapshot(isRecord(personA) ? personA : {}), formatBirthSnapshot(isRecord(personB) ? personB : {})]
      .filter(Boolean)
      .join(" / ");
  }
  return formatBirthSnapshot(snapshot);
}

function formatBirthSnapshot(snapshot: Record<string, unknown>) {
  const date = asText(snapshot.birth_date);
  const time = asText(snapshot.birth_time);
  const place = asText(snapshot.place_name || snapshot.place_id);
  return [date, time, place].filter(Boolean).join(" · ") || "Данные рождения не указаны";
}

function asText(value: unknown) {
  return typeof value === "string" || typeof value === "number" ? String(value) : "";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
