"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import {
  askAnalysis,
  type AnalysisChatProvider,
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
type MiniChartPlacement = { body: string; rashi: string };
type CompatibilityReferenceCard = {
  title: string;
  hint: string;
  lines: string[];
  placements: MiniChartPlacement[];
  highlightRashi: string;
};

const miniRashiNames = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"];
const miniRashiShort = ["Me", "Vr", "Mi", "Ka", "Si", "Kn", "Tu", "Vr", "Dh", "Mk", "Ku", "Pi"];
const miniSouthCells: Record<number, { row: number; col: number }> = {
  11: { row: 0, col: 0 },
  0: { row: 0, col: 1 },
  1: { row: 0, col: 2 },
  2: { row: 0, col: 3 },
  10: { row: 1, col: 0 },
  3: { row: 1, col: 3 },
  9: { row: 2, col: 0 },
  4: { row: 2, col: 3 },
  8: { row: 3, col: 0 },
  7: { row: 3, col: 1 },
  6: { row: 3, col: 2 },
  5: { row: 3, col: 3 },
};

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

      {chatMode === "compatibility" ? <CompatibilityPairContext detail={detail} /> : null}

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

function CompatibilityPairContext({ detail }: { detail: AnalysisHistoryDetail }) {
  const packet = isRecord(detail.analysis.packet_snapshot) ? detail.analysis.packet_snapshot : {};
  const snapshot = detail.analysis.input_snapshot;
  const context = recordOrNull(packet.context) ?? {};
  const personA = recordOrNull(context.person_a) ?? recordOrNull(packet.person_a) ?? {};
  const personB = recordOrNull(context.person_b) ?? recordOrNull(packet.person_b) ?? {};
  const personAInput = recordOrNull(personA.input) ?? recordOrNull(snapshot.person_a) ?? {};
  const personBInput = recordOrNull(personB.input) ?? recordOrNull(snapshot.person_b) ?? {};
  const compatibility = recordOrNull(context.compatibility) ?? recordOrNull(packet.compatibility) ?? {};
  const analysis = recordOrNull(compatibility.analysis) ?? {};
  const summaries = recordOrNull(analysis.chart_summaries) ?? {};
  const score = recordOrNull(compatibility.score) ?? {};
  const assessment = recordOrNull(compatibility.assessment) ?? {};
  const kutaRows = recordArray(compatibility.kuta_rows).slice(0, 6);
  const hasSavedPacket = Object.keys(packet).length > 0;

  return (
    <section className="compatibility-detail-context">
      <div className="compatibility-context-head">
        <div>
          <h2>Данные пары</h2>
          <p>
            {hasSavedPacket
              ? "Сохранённый пакет расчёта: D1, ключевые варги, 7 дом и факторы совместимости."
              : "Старый обзор без сохранённого расчётного пакета: показываю входные данные и обязательные слои проверки."}
          </p>
        </div>
        <div className="compatibility-context-score">
          <span>Ашта-кута</span>
          <strong>{scoreText(score)}</strong>
          <small>{asText(assessment.level) || asText(assessment.note) || "оценка в тексте обзора"}</small>
        </div>
      </div>

      <div className="compatibility-context-grid">
        <CompatibilityPersonContextCard
          label="Человек A"
          input={personAInput}
          chart={recordOrNull(personA.chart) ?? {}}
          summary={recordOrNull(summaries.person_a) ?? {}}
        />
        <CompatibilityPersonContextCard
          label="Человек B"
          input={personBInput}
          chart={recordOrNull(personB.chart) ?? {}}
          summary={recordOrNull(summaries.person_b) ?? {}}
        />
      </div>

      <div className="compatibility-checklist">
        <strong>Что обязательно учитывать</strong>
        <span>7 дом, управитель 7 дома и планеты в 7 доме в обеих D1.</span>
        <span>D9: навамша лагны, Шукры/Гуру, брачная устойчивость и дхармический слой союза.</span>
        <span>2, 4, 8, 12 дома: семья, быт, близость, расходы, уединение и скрытые напряжения.</span>
        <span>D7/D12/D30/D60: дети, родители/родовые темы, риски и глубинная кармическая подоплёка.</span>
      </div>

      {kutaRows.length ? (
        <div className="compatibility-context-table">
          {kutaRows.map((row) => (
            <div key={asText(row.key) || asText(row.name)}>
              <strong>{asText(row.name) || asText(row.key)}</strong>
              <span>{asText(row.score)}/{asText(row.max_score)}</span>
              <small>{asText(row.details) || asText(row.status)}</small>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function CompatibilityPersonContextCard({
  label,
  input,
  chart,
  summary,
}: {
  label: string;
  input: Record<string, unknown>;
  chart: Record<string, unknown>;
  summary: Record<string, unknown>;
}) {
  const seventhHouse = recordOrNull(summary.seventh_house) ?? {};
  const seventhLord = recordOrNull(summary.seventh_lord) ?? {};
  const relationshipGrahas = recordOrNull(summary.relationship_grahas) ?? {};
  const birthDashaLord = bodyLabel(asText(summary.birth_dasha_lord));
  const twelfthHouse = houseLine(chart, 12);
  const familyHouses = [2, 4, 8, 12].map((house) => houseLine(chart, house)).join(" · ");
  const chartCards = compatibilityReferenceCards(chart, summary);

  return (
    <article className="compatibility-person-card">
      <div>
        <span>{label}</span>
        <strong>{formatBirthSnapshot(input)}</strong>
      </div>
      <dl className="compatibility-person-facts">
        <div>
          <dt>Лагна</dt>
          <dd>{placementLine(recordOrNull(summary.lagna) ?? recordOrNull(chart.ascendant), "Лагна")}</dd>
        </div>
        <div>
          <dt>Луна</dt>
          <dd>{placementLine(recordOrNull(summary.moon) ?? findGraha(chart, ["Chandra", "Moon"]), "Луна")}</dd>
        </div>
        <div>
          <dt>7 дом</dt>
          <dd>
            {asText(seventhHouse.rashi) || "-"}
            {asText(seventhHouse.lord) ? `, упр. ${bodyLabel(asText(seventhHouse.lord))}` : ""}
            {textArray(seventhHouse.planets).length ? `, планеты: ${textArray(seventhHouse.planets).map(bodyLabel).join(", ")}` : ""}
          </dd>
        </div>
        <div>
          <dt>Управитель 7</dt>
          <dd>{placementLine(seventhLord, bodyLabel(asText(seventhLord.body) || asText(seventhHouse.lord)))}</dd>
        </div>
        <div>
          <dt>12 дом</dt>
          <dd>{twelfthHouse}</dd>
        </div>
        <div>
          <dt>2/4/8/12</dt>
          <dd>{familyHouses}</dd>
        </div>
      </dl>
      <div className="compatibility-focus-list">
        <div>
          <span>D1: 7 дом</span>
          <strong>{houseLine(chart, 7)}</strong>
        </div>
        <div>
          <span>D1: 12 дом</span>
          <strong>{twelfthHouse}</strong>
        </div>
        <div>
          <span>Даша рождения</span>
          <strong>{birthDashaLord || "нет данных"}</strong>
        </div>
      </div>
      <div className="compatibility-mini-chart-board" aria-label={`${label}: опорные карты и отсчёты`}>
        {chartCards.map((card) => (
          <div className="compatibility-mini-chart-card" key={card.title}>
            <div>
              <strong>{card.title}</strong>
              <span>{card.hint}</span>
            </div>
            {card.placements.length ? (
              <MiniRashiGrid placements={card.placements} highlightRashi={card.highlightRashi} />
            ) : null}
            {card.lines.map((line) => (
              <small key={line}>{line}</small>
            ))}
          </div>
        ))}
      </div>
      <div className="compatibility-graha-list">
        {["Shukra", "Mangala", "Guru"].map((body) => (
          <div key={body}>
            <span>{bodyLabel(body)}</span>
            <small>{placementLine(recordOrNull(relationshipGrahas[body]) ?? findGraha(chart, [body]), bodyLabel(body))}</small>
          </div>
        ))}
      </div>
      <div className="compatibility-varga-list">
        {["D7", "D9", "D12", "D30", "D60"].map((code) => (
          <div key={code}>
            <span>{code}</span>
            <small>{vargaLine(chart, code)}</small>
          </div>
        ))}
      </div>
    </article>
  );
}

function compatibilityReferenceCards(chart: Record<string, unknown>, summary: Record<string, unknown>) {
  const seventhHouse = recordOrNull(summary.seventh_house) ?? {};
  const seventhLord = recordOrNull(summary.seventh_lord) ?? {};
  const lagna = placementLine(recordOrNull(summary.lagna) ?? recordOrNull(chart.ascendant), "Лагна");
  const moon = placementLine(recordOrNull(summary.moon) ?? findGraha(chart, ["Chandra", "Moon"]), "Луна");
  const d1Placements = d1MiniPlacements(chart);
  const lagnaRashi = asText((recordOrNull(summary.lagna) ?? recordOrNull(chart.ascendant))?.rashi);
  const seventhRashi = asText(seventhHouse.rashi) || houseRashi(chart, 7);
  const twelfthRashi = houseRashi(chart, 12);
  const seventh = [
    asText(seventhHouse.rashi) ? `7 дом: ${asText(seventhHouse.rashi)}` : houseLine(chart, 7),
    placementLine(seventhLord, bodyLabel(asText(seventhLord.body) || asText(seventhHouse.lord))),
  ].filter((line) => line && line !== "-");
  const cards: CompatibilityReferenceCard[] = [
    {
      title: "D1",
      hint: "лагна / Луна",
      lines: [lagna, moon].filter((line) => line && line !== "-"),
      placements: d1Placements,
      highlightRashi: lagnaRashi,
    },
    {
      title: "D1 от 7",
      hint: "брак",
      lines: seventh.length ? seventh : [houseLine(chart, 7)],
      placements: d1Placements,
      highlightRashi: seventhRashi,
    },
    {
      title: "D1 от 12",
      hint: "близость",
      lines: [houseLine(chart, 12), houseLine(chart, 8)],
      placements: d1Placements,
      highlightRashi: twelfthRashi,
    },
    {
      title: "D7",
      hint: "дети",
      lines: vargaFocusLines(chart, "D7", ["Lagna", "Ascendant", "Guru", "Jupiter", "Shukra", "Venus"]),
      placements: vargaMiniPlacements(chart, "D7"),
      highlightRashi: vargaLagnaRashi(chart, "D7"),
    },
    {
      title: "D9",
      hint: "навамша",
      lines: vargaFocusLines(chart, "D9", ["Lagna", "Ascendant", "Shukra", "Venus", "Guru", "Jupiter"]),
      placements: vargaMiniPlacements(chart, "D9"),
      highlightRashi: vargaLagnaRashi(chart, "D9"),
    },
    {
      title: "D12",
      hint: "род",
      lines: vargaFocusLines(chart, "D12", ["Lagna", "Ascendant", "Surya", "Sun", "Chandra", "Moon"]),
      placements: vargaMiniPlacements(chart, "D12"),
      highlightRashi: vargaLagnaRashi(chart, "D12"),
    },
  ];
  return cards.map((card) => ({ ...card, lines: card.lines.length ? card.lines.slice(0, 3) : ["нет данных"] }));
}

function MiniRashiGrid({ placements, highlightRashi }: { placements: MiniChartPlacement[]; highlightRashi: string }) {
  const byRashi = new Map<number, MiniChartPlacement[]>();
  placements.forEach((placement) => {
    const index = rashiIndex(placement.rashi);
    if (index === null) return;
    const existing = byRashi.get(index) ?? [];
    existing.push(placement);
    byRashi.set(index, existing);
  });
  const highlightIndex = rashiIndex(highlightRashi);

  return (
    <div className="compatibility-mini-rashi-grid" aria-hidden="true">
      {Array.from({ length: 16 }, (_, cellIndex) => {
        const row = Math.floor(cellIndex / 4);
        const col = cellIndex % 4;
        const signEntry = Object.entries(miniSouthCells).find(([, cell]) => cell.row === row && cell.col === col);
        if (!signEntry) return <div className="compatibility-mini-rashi-center" key={cellIndex} />;
        const signIndex = Number(signEntry[0]);
        const items = byRashi.get(signIndex) ?? [];
        return (
          <div className={highlightIndex === signIndex ? "compatibility-mini-rashi-cell active" : "compatibility-mini-rashi-cell"} key={signIndex}>
            <span>{miniRashiShort[signIndex]}</span>
            {items.slice(0, 3).map((item) => (
              <strong key={`${signIndex}-${item.body}`}>{miniBodyLabel(item.body)}</strong>
            ))}
            {items.length > 3 ? <em>+{items.length - 3}</em> : null}
          </div>
        );
      })}
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
  const [provider, setProvider] = useState<AnalysisChatProvider>("qwen");
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
      const result = await askAnalysis(analysisId, provider, cleanQuestion, nextMessages);
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
        <div className="analysis-chat-tools">
          <select value={provider} onChange={(event) => setProvider(event.target.value as AnalysisChatProvider)} disabled={mode === "disabled" || busy}>
            <option value="qwen">Qwen</option>
            <option value="deepseek">DeepSeek</option>
            <option value="codex">Codex</option>
          </select>
          <span>{status}</span>
        </div>
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

function scoreText(score: Record<string, unknown>) {
  const total = asText(score.total);
  const max = asText(score.max);
  const percent = typeof score.percent === "number" ? `${score.percent.toFixed(1)}%` : asText(score.percent);
  return [total && max ? `${total}/${max}` : "", percent].filter(Boolean).join(" · ") || "-";
}

function houseLine(chart: Record<string, unknown>, houseNumber: number) {
  const houses = recordArray(chart.houses);
  const house = houses.find((row) => Number(row.house) === houseNumber);
  const grahas = recordArray(chart.grahas)
    .filter((row) => Number(row.house) === houseNumber)
    .map((row) => bodyLabel(asText(row.body)))
    .filter(Boolean);
  const rashi = asText(house?.rashi);
  return `${houseNumber}: ${rashi || "-"}${grahas.length ? ` (${grahas.join(", ")})` : ""}`;
}

function houseRashi(chart: Record<string, unknown>, houseNumber: number) {
  const houses = recordArray(chart.houses);
  const house = houses.find((row) => Number(row.house) === houseNumber);
  return asText(house?.rashi);
}

function d1MiniPlacements(chart: Record<string, unknown>) {
  const ascendant = recordOrNull(chart.ascendant);
  const placements = recordArray(chart.grahas)
    .map((row) => ({ body: asText(row.body), rashi: asText(row.rashi) }))
    .filter((row) => row.body && row.rashi);
  if (ascendant && asText(ascendant.rashi)) {
    placements.unshift({ body: "Lagna", rashi: asText(ascendant.rashi) });
  }
  return placements;
}

function vargaLine(chart: Record<string, unknown>, code: string) {
  const vargas = recordOrNull(chart.vargas) ?? {};
  const varga = recordOrNull(vargas[code]);
  const placements = recordArray(varga?.placements);
  if (!placements.length) return "нет данных";
  const important = placements.filter((row) => {
    const body = asText(row.body);
    return ["Lagna", "Ascendant", "Shukra", "Venus", "Mangala", "Mars", "Guru", "Jupiter", "Chandra", "Moon"].includes(body);
  });
  return (important.length ? important : placements.slice(0, 4))
    .slice(0, 6)
    .map((row) => `${bodyLabel(asText(row.body))} ${asText(row.rashi) || "-"}`)
    .join("; ");
}

function vargaFocusLines(chart: Record<string, unknown>, code: string, bodies: string[]) {
  const vargas = recordOrNull(chart.vargas) ?? {};
  const varga = recordOrNull(vargas[code]);
  const placements = recordArray(varga?.placements);
  if (!placements.length) return [];
  const selected = placements.filter((row) => bodies.includes(asText(row.body)));
  const rows = selected.length ? selected : placements.slice(0, 3);
  return rows.map((row) => `${bodyLabel(asText(row.body))} ${asText(row.rashi) || "-"}`);
}

function vargaMiniPlacements(chart: Record<string, unknown>, code: string) {
  const vargas = recordOrNull(chart.vargas) ?? {};
  const varga = recordOrNull(vargas[code]);
  return recordArray(varga?.placements)
    .map((row) => ({ body: asText(row.body), rashi: asText(row.rashi) }))
    .filter((row) => row.body && row.rashi);
}

function vargaLagnaRashi(chart: Record<string, unknown>, code: string) {
  return vargaMiniPlacements(chart, code).find((row) => row.body === "Lagna" || row.body === "Ascendant")?.rashi ?? "";
}

function placementLine(row: Record<string, unknown> | null, fallbackBody = "") {
  if (!row) return "-";
  const body = bodyLabel(asText(row.body) || fallbackBody);
  const rashi = asText(row.rashi);
  const house = asText(row.house);
  const nakshatra = asText(row.nakshatra);
  const parts = [body, rashi, house ? `дом ${house}` : "", nakshatra ? `накш. ${nakshatra}` : ""].filter(Boolean);
  return parts.join(" · ") || "-";
}

function findGraha(chart: Record<string, unknown>, names: string[]) {
  return recordArray(chart.grahas).find((row) => names.includes(asText(row.body))) ?? null;
}

function bodyLabel(value: string) {
  const labels: Record<string, string> = {
    Ascendant: "Лагна",
    Lagna: "Лагна",
    Chandra: "Луна",
    Moon: "Луна",
    Surya: "Солнце",
    Sun: "Солнце",
    Shukra: "Шукра",
    Venus: "Шукра",
    Mangala: "Мангала",
    Mars: "Мангала",
    Guru: "Гуру",
    Jupiter: "Гуру",
    Budha: "Будха",
    Mercury: "Будха",
    Shani: "Шани",
    Saturn: "Шани",
    Rahu: "Раху",
    Ketu: "Кету",
  };
  return labels[value] ?? value;
}

function miniBodyLabel(value: string) {
  const labels: Record<string, string> = {
    Ascendant: "As",
    Lagna: "As",
    Chandra: "Mo",
    Moon: "Mo",
    Surya: "Su",
    Sun: "Su",
    Shukra: "Ve",
    Venus: "Ve",
    Mangala: "Ma",
    Mars: "Ma",
    Guru: "Ju",
    Jupiter: "Ju",
    Budha: "Me",
    Mercury: "Me",
    Shani: "Sa",
    Saturn: "Sa",
    Rahu: "Ra",
    Ketu: "Ke",
  };
  return labels[value] ?? value.slice(0, 2);
}

function rashiIndex(value: string) {
  if (!value) return null;
  const normalized = value.trim().toLowerCase();
  const aliases: Record<string, number> = {
    aries: 0,
    taurus: 1,
    gemini: 2,
    cancer: 3,
    leo: 4,
    virgo: 5,
    libra: 6,
    scorpio: 7,
    sagittarius: 8,
    capricorn: 9,
    aquarius: 10,
    pisces: 11,
  };
  const byName = miniRashiNames.findIndex((name) => name.toLowerCase() === normalized);
  if (byName >= 0) return byName;
  return aliases[normalized] ?? null;
}

function recordOrNull(value: unknown): Record<string, unknown> | null {
  return isRecord(value) ? value : null;
}

function recordArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter(isRecord) : [];
}

function textArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(asText).filter(Boolean) : [];
}

function asText(value: unknown) {
  return typeof value === "string" || typeof value === "number" ? String(value) : "";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
