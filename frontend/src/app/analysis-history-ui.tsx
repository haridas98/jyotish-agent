"use client";

import Link from "next/link";
import { FormEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";
import { HouseTerms, VargaTerms } from "@/app/relationship-help";
import {
  askAnalysis,
  isAnalysisInProgressError,
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
  chatMode: "birth" | "compatibility" | "current-day" | "disabled";
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

const readerHelp = {
  house_1: {
    title: "1 дом",
    text: "Лагна: тело, характер, жизненный старт, внешний способ действовать и главная точка отсчёта карты.",
  },
  house_2: {
    title: "2 дом",
    text: "Семья, речь, питание, накопления, ценности и ресурсы, которые человек удерживает.",
  },
  house_3: {
    title: "3 дом",
    text: "Усилия, смелость, навыки, коммуникация, младшие братья и сёстры, инициативность.",
  },
  house_4: {
    title: "4 дом",
    text: "Дом, мать, внутренний покой, недвижимость, образование и эмоциональная опора.",
  },
  house_5: {
    title: "5 дом",
    text: "Дети, интеллект, мантра, творчество, пурва-пунья и способность делать тонкий выбор.",
  },
  house_6: {
    title: "6 дом",
    text: "Болезни, долги, служение, конфликты, оппоненты и повседневное преодоление.",
  },
  house_7: {
    title: "7 дом",
    text: "Партнерство, брак, договоры и открытое взаимодействие. В совместимости это первая ось проверки.",
  },
  house_8: {
    title: "8 дом",
    text: "Кризисы, тайны, трансформация, долговечность, наследство и скрытые страхи.",
  },
  house_9: {
    title: "9 дом",
    text: "Дхарма, отец, гуру, удача, высшее знание, паломничество и благословения.",
  },
  house_10: {
    title: "10 дом",
    text: "Карьера, действие в мире, статус, обязанности, публичная роль и видимая карма.",
  },
  house_11: {
    title: "11 дом",
    text: "Доходы, друзья, старшие братья и сёстры, сети, исполнение желаний и результаты.",
  },
  house_12: {
    title: "12 дом",
    text: "Расходы, сон, уединение, близость, потери и скрытая сторона отношений.",
  },
  focus_houses: {
    title: "Фокусные дома",
    text: "Дома, которые важнее всего для выбранной роли: например отец, мать, партнер, руководитель или оппонент.",
  },
  d1: {
    title: "D1 / Rashi",
    text: "Основная карта рождения. Все дробные карты читаются вместе с D1, а не отдельно от нее.",
  },
  d3: {
    title: "D3 / Drekkana",
    text: "Drekkana. Важна для братьев, сестёр, усилий, инициативы и смелости.",
  },
  d6: {
    title: "D6",
    text: "Shashtamsha. Помогает смотреть конфликты, болезни, долги и оппонентов.",
  },
  d7: {
    title: "D7",
    text: "Saptamsha. Часто используется для тем детей и продолжения рода.",
  },
  d9: {
    title: "D9 / Navamsa",
    text: "Навамша: важна для брака, дхармы и тонкой силы положения грах.",
  },
  d10: {
    title: "D10 / Dashamsha",
    text: "Dashamsha. Главная D-карта для карьеры, статуса, действия в мире и иерархии.",
  },
  d12: {
    title: "D12",
    text: "Dvadashamsha. Используется для родителей, рода и наследственных тем.",
  },
  d30: {
    title: "D30",
    text: "Trimshamsha. Помогает смотреть риски, напряжения и неприятные скрытые факторы.",
  },
  d60: {
    title: "D60",
    text: "Shashtyamsha. Глубокий кармический слой; требует особенно аккуратной трактовки.",
  },
  ashta_kuta: {
    title: "Ашта-кута",
    text: "Классическая система баллов совместимости по лунным факторам. Это не единственный слой вывода.",
  },
  shadbala: {
    title: "Шадбала",
    text: "Шесть групп расчётной силы грахи. Это слой проверки, а не самостоятельный окончательный вывод.",
  },
  combustion: {
    title: "Аста / сожжение",
    text: "Граха слишком близко к Солнцу и может слабее проявлять свои качества.",
  },
  varga: {
    title: "D-карта",
    text: "Дробная карта для конкретной сферы жизни. Ее нужно сверять с D1 и контекстом вопроса.",
  },
  consent: {
    title: "Статус связи",
    text: "Показывает, является ли связь личной заметкой или подтверждена вторым зарегистрированным пользователем.",
  },
} as const;

type ReaderHelpKey = keyof typeof readerHelp;

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

      {chatMode === "birth" ? <BirthChartContext detail={detail} /> : null}
      {chatMode === "compatibility" ? <CompatibilityPairContext detail={detail} /> : null}
      {chatMode === "current-day" ? <CurrentDayContext detail={detail} /> : null}

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
        initialLimit={detail.chat_record_limit}
        initialMessages={detail.chat_messages}
        initialTotal={detail.chat_record_total}
        initialTruncated={detail.chat_truncated}
        mode={chatMode}
      />
    </div>
  );
}

function ReaderHelp({ termKey, children }: { termKey: ReaderHelpKey; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLSpanElement | null>(null);
  const item = readerHelp[termKey];

  useEffect(() => {
    if (!open) return;
    function handlePointerDown(event: PointerEvent) {
      if (wrapRef.current?.contains(event.target as Node)) return;
      setOpen(false);
    }
    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [open]);

  return (
    <span
      ref={wrapRef}
      className={`reader-help${open ? " open" : ""}`}
      data-open={open ? "true" : "false"}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      <button
        type="button"
        className="reader-help-trigger"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        {children}
      </button>
      {open ? (
        <span className="reader-help-popover" role="tooltip">
          <strong>{item.title}</strong>
          <span>{item.text}</span>
        </span>
      ) : null}
    </span>
  );
}

function HouseHelp({ value, suffix }: { value: unknown; suffix: string }) {
  const house = Number(value);
  if (!Number.isFinite(house) || house < 1 || house > 12) return null;
  const key = `house_${house}` as ReaderHelpKey;
  return (
    <span className="reader-help-inline">
      <ReaderHelp termKey={key}>{house}</ReaderHelp> {suffix}
    </span>
  );
}

function TransitHouseSummary({ row }: { row: Record<string, unknown> }) {
  const items = [
    <HouseHelp value={row.house_from_lagna} suffix="от лагны" key="lagna" />,
    <HouseHelp value={row.house_from_moon} suffix="от Луны" key="moon" />,
  ].filter(Boolean);
  if (!items.length) return <>дом не определён</>;
  return (
    <>
      {items.map((item, index) => (
        <span key={`transit-house-${index}`}>
          {index > 0 ? " · " : ""}
          {item}
        </span>
      ))}
    </>
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
  const relationshipContext = recordOrNull(context.relationship_context) ?? {};
  const focusHouses = numberArray(relationshipContext.focus_houses);
  const focusVargas = textArray(relationshipContext.focus_vargas);
  const roleLabel = relationshipRoleLabel(relationshipContext);
  const rolePrompt = asText(relationshipContext.prompt_hint);
  const consentPolicy = asText(relationshipContext.consent_policy);
  const personAChart = recordOrNull(personA.chart) ?? {};
  const personBChart = recordOrNull(personB.chart) ?? {};

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
          <span><ReaderHelp termKey="ashta_kuta">Ашта-кута</ReaderHelp></span>
          <strong>{scoreText(score)}</strong>
          <small>{asText(assessment.level) || asText(assessment.note) || "оценка в тексте обзора"}</small>
        </div>
      </div>

      <div className="compatibility-saved-role-context">
        <div className="compatibility-saved-role-head">
          <div>
            <span>Ракурс взаимодействия</span>
            <strong>{roleLabel}</strong>
          </div>
          <small><ReaderHelp termKey="consent">{consentPolicy || "личная заметка или подтверждённая связь профилей"}</ReaderHelp></small>
        </div>
        {rolePrompt ? <p>{rolePrompt}</p> : null}
        <div className="compatibility-saved-role-grid">
          <div>
            <span>Фокусные дома</span>
            <strong><HouseTerms houses={focusHouses.length ? focusHouses : [7, 12]} /></strong>
          </div>
          <div>
            <span>D-карты</span>
            <strong><VargaTerms vargas={focusVargas.length ? focusVargas : ["D1", "D9"]} /></strong>
          </div>
          <div>
            <span>Человек A</span>
            <strong>{roleFocusLine(personAChart, focusHouses, focusVargas)}</strong>
          </div>
          <div>
            <span>Человек B</span>
            <strong>{roleFocusLine(personBChart, focusHouses, focusVargas)}</strong>
          </div>
        </div>
      </div>

      <div className="compatibility-context-grid">
        <CompatibilityPersonContextCard
          label="Человек A"
          input={personAInput}
          chart={personAChart}
          summary={recordOrNull(summaries.person_a) ?? {}}
          focusVargas={focusVargas}
        />
        <CompatibilityPersonContextCard
          label="Человек B"
          input={personBInput}
          chart={personBChart}
          summary={recordOrNull(summaries.person_b) ?? {}}
          focusVargas={focusVargas}
        />
      </div>

      <div className="compatibility-checklist">
        <strong>Что обязательно учитывать</strong>
        <span><ReaderHelp termKey="house_7">7 дом</ReaderHelp>, управитель 7 дома и планеты в 7 доме в обеих <ReaderHelp termKey="d1">D1</ReaderHelp>.</span>
        <span><ReaderHelp termKey="d9">D9</ReaderHelp>: навамша лагны, Шукры/Гуру, брачная устойчивость и дхармический слой союза.</span>
        <span><HouseTerms houses={[2, 4, 8, 12]} />: семья, быт, близость, расходы, уединение и скрытые напряжения.</span>
        <span><VargaTerms vargas={["D7", "D12", "D30", "D60"]} />: дети, родители/родовые темы, риски и глубинная кармическая подоплёка.</span>
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

function BirthChartContext({ detail }: { detail: AnalysisHistoryDetail }) {
  const packet = isRecord(detail.analysis.packet_snapshot) ? detail.analysis.packet_snapshot : {};
  const context = recordOrNull(packet.context) ?? {};
  const chart = recordOrNull(context.chart) ?? {};
  const layers = recordOrNull(packet.chart_layers) ?? recordOrNull(context.chart_layers) ?? {};
  const birth = recordOrNull(context.birth) ?? recordOrNull(packet.birth) ?? recordOrNull(chart.birth) ?? detail.analysis.input_snapshot;
  const place = recordOrNull(context.place) ?? recordOrNull(packet.place) ?? recordOrNull(chart.place) ?? {};
  const facts = recordOrNull(context.chart_facts) ?? recordOrNull(packet.chart_facts) ?? {};
  const cards = birthReferenceCards(chart, layers);

  return (
    <section className="birth-detail-context">
      <div className="birth-context-head">
        <div>
          <h2>Контекст карты</h2>
          <p>{formatBirthSnapshot(birth)}{asText(place.label || place.name) ? ` · ${asText(place.label || place.name)}` : ""}</p>
        </div>
        <div className="birth-context-facts">
          <div>
            <span>Лагна</span>
            <strong>{placementLine(recordOrNull(chart.ascendant), "Лагна")}</strong>
          </div>
          <div>
            <span>Луна</span>
            <strong>{placementLine(findGraha(chart, ["Chandra", "Moon"]), "Луна")}</strong>
          </div>
          <div>
            <span>Даша</span>
            <strong>{birthDashaLine(chart, layers)}</strong>
          </div>
        </div>
      </div>
      <div className="birth-mini-chart-board" aria-label="Опорные D-карты личного обзора">
        {cards.map((card) => (
          <div className="birth-mini-chart-card" key={card.title}>
            <div>
              <strong>{card.title}</strong>
              <span>{card.hint}</span>
            </div>
            {card.placements.length ? <MiniRashiGrid placements={card.placements} highlightRashi={card.highlightRashi} /> : null}
            {card.lines.map((line) => <small key={line}>{line}</small>)}
          </div>
        ))}
      </div>
      <div className="birth-context-strip">
        <span>{asText(facts.panchanga) || "Panchanga и варги сохранены в расчётном пакете обзора."}</span>
        <span>{asText(facts.vimshopaka) || "D9/D10/D12/D30/D60 вынесены отдельно, чтобы не искать их в тексте."}</span>
      </div>
    </section>
  );
}

function CurrentDayContext({ detail }: { detail: AnalysisHistoryDetail }) {
  const packet = isRecord(detail.analysis.packet_snapshot) ? detail.analysis.packet_snapshot : {};
  const snapshot = detail.analysis.input_snapshot;
  const transitReport = recordOrNull(packet.transit_report) ?? {};
  const asOf = recordOrNull(transitReport.as_of) ?? recordOrNull(detail.analysis.output_json?.as_of) ?? {};
  const transits = recordArray(transitReport.transits).slice(0, 8);
  const relatedProfiles = recordArray(snapshot.related_profile_context);
  const place = asText(snapshot.place_name || snapshot.place_id);
  const moment = [asText(asOf.date || snapshot.as_of_date), asText(asOf.time || snapshot.as_of_time), asText(asOf.timezone || snapshot.timezone)]
    .filter(Boolean)
    .join(" · ");

  return (
    <section className="birth-detail-context current-day-detail-context">
      <div className="birth-context-head">
        <div>
          <h2>Контекст текущего дня</h2>
          <p>{moment || "Момент обзора не указан"}{place ? ` · ${place}` : ""}</p>
        </div>
        <div className="birth-context-facts">
          <div>
            <span>Карта рождения</span>
            <strong>{formatBirthSnapshot(snapshot)}</strong>
          </div>
          <div>
            <span>Связанные карты</span>
            <strong>{relatedProfiles.length ? `${relatedProfiles.length}` : "нет"}</strong>
          </div>
          <div>
            <span>Метод</span>
            <strong>{asText(transitReport.method) || "транзиты от лагны и Луны"}</strong>
          </div>
        </div>
      </div>
      {transits.length ? (
        <div className="compatibility-context-table current-day-transit-table">
          {transits.map((row) => (
            <div key={`${asText(row.body)}-${asText(row.rashi)}-${asText(row.longitude)}`}>
              <strong>{bodyLabel(asText(row.body))}</strong>
              <span>{asText(row.rashi)} {asText(row.nakshatra) ? `· ${asText(row.nakshatra)}` : ""}</span>
              <small>
                <TransitHouseSummary row={row} />
              </small>
            </div>
          ))}
        </div>
      ) : (
        <div className="birth-context-strip">
          <span>Транзитная таблица не сохранена в этом обзоре.</span>
        </div>
      )}
      {relatedProfiles.length ? (
        <div className="birth-context-strip">
          <span>AI-вопросы по этому обзору получают контекст связанных карт из профиля.</span>
          <span>{relatedProfiles.map((profile) => asText(profile.display_name || profile.profile_id)).filter(Boolean).slice(0, 4).join(" · ")}</span>
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
  focusVargas,
}: {
  label: string;
  input: Record<string, unknown>;
  chart: Record<string, unknown>;
  summary: Record<string, unknown>;
  focusVargas: string[];
}) {
  const seventhHouse = recordOrNull(summary.seventh_house) ?? {};
  const seventhLord = recordOrNull(summary.seventh_lord) ?? {};
  const relationshipGrahas = recordOrNull(summary.relationship_grahas) ?? {};
  const birthDashaLord = bodyLabel(asText(summary.birth_dasha_lord));
  const twelfthHouse = houseLine(chart, 12);
  const familyHouses = [2, 4, 8, 12].map((house) => houseLine(chart, house)).join(" · ");
  const visibleVargas = visibleCompatibilityVargas(focusVargas);
  const chartCards = compatibilityReferenceCards(chart, summary, visibleVargas);

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
          <dt><HouseTerms houses={[7]} /></dt>
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
          <dt><HouseTerms houses={[12]} /></dt>
          <dd>{twelfthHouse}</dd>
        </div>
        <div>
          <dt><HouseTerms houses={[2, 4, 8, 12]} /></dt>
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
        {visibleVargas.map((code) => (
          <div key={code}>
            <span><VargaTerms vargas={[code]} /></span>
            <small>{vargaLine(chart, code)}</small>
          </div>
        ))}
      </div>
    </article>
  );
}

function compatibilityReferenceCards(chart: Record<string, unknown>, summary: Record<string, unknown>, focusVargas: string[]) {
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
  const roleVargaCards = focusVargas
    .filter((code) => code.toUpperCase() !== "D1")
    .map((code) => {
      const normalized = code.toUpperCase();
      return {
        title: normalized,
        hint: vargaCardHint(normalized),
        lines: vargaFocusLines(chart, normalized, vargaFocusBodiesForCode(normalized)),
        placements: vargaMiniPlacements(chart, normalized),
        highlightRashi: vargaLagnaRashi(chart, normalized),
      };
    });
  return uniqueCards([...roleVargaCards, ...cards])
    .map((card) => ({ ...card, lines: card.lines.length ? card.lines.slice(0, 3) : ["нет данных"] }));
}

function birthReferenceCards(chart: Record<string, unknown>, layers: Record<string, unknown>) {
  const d1Placements = d1MiniPlacements(chart);
  const fallbackD1Placements = layerGrahaMiniPlacements(layers);
  const d1 = d1Placements.length ? d1Placements : fallbackD1Placements;
  const lagnaRashi = asText(recordOrNull(chart.ascendant)?.rashi) || d1.find((row) => row.body === "Lagna" || row.body === "Ascendant")?.rashi || "";
  const cards: CompatibilityReferenceCard[] = [
    {
      title: "D1",
      hint: "раши",
      lines: [
        placementLine(recordOrNull(chart.ascendant), "Лагна"),
        placementLine(findGraha(chart, ["Chandra", "Moon"]), "Луна"),
      ].filter((line) => line && line !== "-"),
      placements: d1,
      highlightRashi: lagnaRashi,
    },
    birthVargaCard(chart, layers, "D9", "навамша", ["Lagna", "Ascendant", "Shukra", "Venus", "Guru", "Jupiter"]),
    birthVargaCard(chart, layers, "D10", "карьера", ["Lagna", "Ascendant", "Surya", "Sun", "Shani", "Saturn", "Budha", "Mercury"]),
    birthVargaCard(chart, layers, "D12", "род", ["Lagna", "Ascendant", "Surya", "Sun", "Chandra", "Moon"]),
    birthVargaCard(chart, layers, "D30", "риски", ["Lagna", "Ascendant", "Mangala", "Mars", "Shani", "Saturn", "Rahu", "Ketu"]),
    birthVargaCard(chart, layers, "D60", "карма", ["Lagna", "Ascendant", "Surya", "Sun", "Chandra", "Moon", "Guru", "Jupiter"]),
  ];
  return cards.map((card) => ({ ...card, lines: card.lines.length ? card.lines.slice(0, 3) : ["нет данных"] }));
}

function birthVargaCard(chart: Record<string, unknown>, layers: Record<string, unknown>, code: string, hint: string, bodies: string[]): CompatibilityReferenceCard {
  const placements = vargaMiniPlacements(chart, code);
  const fallbackPlacements = layerVargaMiniPlacements(layers, code);
  const activePlacements = placements.length ? placements : fallbackPlacements;
  return {
    title: code,
    hint,
    lines: vargaFocusLinesFromPlacements(activePlacements, bodies),
    placements: activePlacements,
    highlightRashi: activePlacements.find((row) => row.body === "Lagna" || row.body === "Ascendant")?.rashi ?? "",
  };
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
  initialLimit,
  initialMessages,
  initialTotal,
  initialTruncated,
  mode,
}: {
  analysisId: number;
  initialLimit?: number;
  initialMessages: CodexAnalysisChatMessage[];
  initialTotal?: number;
  initialTruncated?: boolean;
  mode: "birth" | "compatibility" | "current-day" | "disabled";
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
      const result = await askAnalysis(analysisId, cleanQuestion, nextMessages);
      setMessages([...nextMessages, { role: "assistant", content: result.answer }]);
      setStatus("Ответ сохранён в истории диалога.");
    } catch (error) {
      setMessages([
        ...nextMessages,
        { role: "assistant", content: error instanceof Error ? error.message : "Ошибка ответа" },
      ]);
      setStatus(isAnalysisInProgressError(error) ? "Ответ уже формируется." : "Не удалось получить ответ.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="analysis-chat">
      <div className="analysis-chat-head">
        <h2>Диалог</h2>
        <div className="analysis-chat-tools">
          <strong>Codex CLI</strong>
          <span>{status}</span>
        </div>
      </div>
      <div className="analysis-chat-thread">
        {initialTruncated ? (
          <div className="history-empty">
            Показаны последние {initialLimit ?? Math.ceil(initialMessages.length / 2)} диалогов из {initialTotal ?? "всей истории"}.
          </div>
        ) : null}
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

function visibleCompatibilityVargas(codes: string[]) {
  const normalized = codes
    .map((code) => code.trim().toUpperCase())
    .filter(Boolean);
  const fallback = ["D7", "D9", "D12", "D30", "D60"];
  const source = normalized.length ? normalized : fallback;
  return Array.from(new Set(source.filter((code) => code !== "D1"))).slice(0, 5);
}

function uniqueCards(cards: CompatibilityReferenceCard[]) {
  const seen = new Set<string>();
  return cards.filter((card) => {
    const key = card.title.toUpperCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function vargaCardHint(code: string) {
  const hints: Record<string, string> = {
    D3: "сиблинги",
    D6: "конфликты",
    D7: "дети",
    D9: "навамша",
    D10: "карьера",
    D12: "род",
    D30: "риски",
    D60: "карма",
  };
  return hints[code.toUpperCase()] ?? "D-карта";
}

function vargaFocusBodiesForCode(code: string) {
  const bodies: Record<string, string[]> = {
    D3: ["Lagna", "Ascendant", "Mangala", "Mars", "Budha", "Mercury"],
    D6: ["Lagna", "Ascendant", "Mangala", "Mars", "Shani", "Saturn", "Rahu", "Ketu"],
    D7: ["Lagna", "Ascendant", "Guru", "Jupiter", "Shukra", "Venus"],
    D9: ["Lagna", "Ascendant", "Shukra", "Venus", "Guru", "Jupiter"],
    D10: ["Lagna", "Ascendant", "Surya", "Sun", "Shani", "Saturn", "Budha", "Mercury"],
    D12: ["Lagna", "Ascendant", "Surya", "Sun", "Chandra", "Moon"],
    D30: ["Lagna", "Ascendant", "Mangala", "Mars", "Shani", "Saturn", "Rahu", "Ketu"],
    D60: ["Lagna", "Ascendant", "Surya", "Sun", "Chandra", "Moon", "Guru", "Jupiter"],
  };
  return bodies[code.toUpperCase()] ?? ["Lagna", "Ascendant"];
}

function relationshipRoleLabel(context: Record<string, unknown>) {
  const label = asText(context.label);
  if (label) return label;
  const labels: Record<string, string> = {
    partner: "партнёр",
    father: "отец",
    mother: "мать",
    brother: "брат",
    sister: "сестра",
    sibling: "брат/сестра",
    boss: "руководитель",
    subordinate: "подчинённый",
    opponent: "оппонент",
    other: "другая роль",
  };
  return labels[asText(context.role)] ?? "совместимость";
}

function roleFocusLine(chart: Record<string, unknown>, houses: number[], vargas: string[]) {
  const houseNumbers = houses.length ? houses.slice(0, 4) : [7, 12];
  const vargaCodes = vargas.length ? vargas.slice(0, 3) : ["D1", "D9"];
  const houseText = houseNumbers.map((house) => houseLine(chart, house)).join("; ");
  const vargaText = vargaCodes.map((code) => `${code}: ${vargaLine(chart, code)}`).join("; ");
  return [houseText, vargaText].filter(Boolean).join(" · ") || "нет данных";
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

function layerGrahaMiniPlacements(layers: Record<string, unknown>) {
  return recordArray(layers.graha_positions)
    .map((row) => ({ body: asText(row.body), rashi: asText(row.rashi) }))
    .filter((row) => row.body && row.rashi);
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

function vargaFocusLinesFromPlacements(placements: MiniChartPlacement[], bodies: string[]) {
  if (!placements.length) return [];
  const selected = placements.filter((row) => bodies.includes(row.body));
  const rows = selected.length ? selected : placements.slice(0, 3);
  return rows.map((row) => `${bodyLabel(row.body)} ${row.rashi || "-"}`);
}

function vargaMiniPlacements(chart: Record<string, unknown>, code: string) {
  const vargas = recordOrNull(chart.vargas) ?? {};
  const varga = recordOrNull(vargas[code]);
  return recordArray(varga?.placements)
    .map((row) => ({ body: asText(row.body), rashi: asText(row.rashi) }))
    .filter((row) => row.body && row.rashi);
}

function layerVargaMiniPlacements(layers: Record<string, unknown>, code: string) {
  const vargas = recordOrNull(layers.vargas) ?? {};
  const varga = recordOrNull(vargas[code]);
  return recordArray(varga?.placements)
    .map((row) => ({ body: asText(row.body), rashi: asText(row.rashi) }))
    .filter((row) => row.body && row.rashi);
}

function vargaLagnaRashi(chart: Record<string, unknown>, code: string) {
  return vargaMiniPlacements(chart, code).find((row) => row.body === "Lagna" || row.body === "Ascendant")?.rashi ?? "";
}

function birthDashaLine(chart: Record<string, unknown>, layers: Record<string, unknown>) {
  const dashas = recordOrNull(chart.dashas) ?? recordOrNull(layers.dashas) ?? {};
  const vimshottari = recordOrNull(dashas.vimshottari) ?? {};
  const first = recordArray(vimshottari.mahadashas)[0];
  return bodyLabel(asText(first?.lord || first?.body || first?.name)) || "нет данных";
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

function numberArray(value: unknown): number[] {
  return Array.isArray(value)
    ? value
        .map((item) => Number(item))
        .filter((item) => Number.isFinite(item))
    : [];
}

function asText(value: unknown) {
  return typeof value === "string" || typeof value === "number" ? String(value) : "";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
