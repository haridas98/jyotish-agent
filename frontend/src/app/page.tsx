"use client";

import { FormEvent, useEffect, useMemo, useState, type Dispatch, type SetStateAction } from "react";
import {
  calculateCompatibility,
  calculateSavedProfile,
  calculateMuhurta,
  calculateTransits,
  createChartProfile,
  fetchCurrentUser,
  generateBirthReport,
  listChartProfiles,
  loginUser,
  logoutUser,
  registerUser,
  searchPlaces,
  searchVLSources,
  type BirthReport,
  type BirthChart,
  type BirthChartRequest,
  type ChartProfile,
  type CompatibilityReport,
  type DayPeriod,
  type DashaPeriod,
  type GrahaPosition,
  type MuhurtaReport,
  type PersonSummary,
  type PlaceCandidate,
  type TransitReport,
  type User,
  type VargaPlacement,
  type VLSearchResult,
} from "@/lib/api";

const sourceRows = [
  ["Айанамша", "Lahiri", "Нужна проверка", "draft"],
  ["Система карты", "Парашара-сиддханта", "Сопоставление источников в работе", "draft"],
  ["Корпус VL", "База Шрилы Прабхупады", "Поиск подключён", "ready"],
];

const analysisTabs = [
  { key: "overview", label: "Обзор", hint: "главное" },
  { key: "calculations", label: "Расчёты", hint: "D1, D9, дома" },
  { key: "yogas", label: "Йоги и силы", hint: "draft + аудит" },
  { key: "timeline", label: "Периоды", hint: "даши" },
  { key: "guidance", label: "Разбор", hint: "текст и цитаты" },
  { key: "workflows", label: "Практика", hint: "транзиты, мухурта, совместимость" },
  { key: "sources", label: "Источники", hint: "VL и статус" },
] as const;

type AnalysisTab = (typeof analysisTabs)[number]["key"];

const stateLabels: Record<string, string> = {
  draft: "черновик",
  ready: "готово",
};

const calculationStatusLabelsRu: Record<string, string> = {
  calculated: "рассчитано",
  partial: "частично",
  draft_needs_citation: "нужны цитаты",
  draft_needs_jhora_audit: "нужна сверка JHora",
  calculated_needs_citation: "рассчитано, нужны цитаты",
  calculated_needs_jhora_audit: "рассчитано, нужна сверка JHora",
  calculated_source_backed_needs_jhora_profile_audit: "рассчитано по шастре, открыт JHora profile diff",
  calculated_needs_tradition_review: "рассчитано, нужна традиционная проверка",
  calculated_needs_task_review: "рассчитано, нужна проверка задачи",
  partial_calculated_needs_citation: "частично рассчитано, нужны цитаты",
  partial_calculated_needs_jhora_audit: "частично рассчитано, нужна сверка JHora",
  partial_calculated_needs_jhora_profile_audit: "частично рассчитано, открыт JHora profile diff",
  calculated_needs_source_audit: "рассчитано, нужен аудит источника",
  pending_source_mapping: "нужна привязка источника",
  pending_jhora_audit: "ждёт сверку JHora",
  pending_endpoint: "ждёт API",
  api_available: "API готов",
  complete_baseline_needs_jhora_audit: "8/8, нужна сверка JHora",
  pending_separate_chart_pair: "нужны две карты",
  pending_separate_workflow: "отдельный режим",
  signature_only: "только признак",
  missing_lagna: "нет лагны",
};

const compatibilityLevelLabelsRu: Record<string, string> = {
  supportive: "поддерживающе",
  mixed: "смешанно",
  caution: "нужна осторожность",
};

const bodyLabelsRu: Record<string, string> = {
  Ascendant: "Асцендент",
  Lagna: "Лагна",
  Surya: "Сурья",
  Chandra: "Чандра",
  Mangala: "Мангала",
  Budha: "Будха",
  Guru: "Гуру",
  Shukra: "Шукра",
  Shani: "Шани",
  Rahu: "Раху",
  Ketu: "Кету",
  Moon: "Луна",
  Sun: "Солнце",
};

const summaryLabelsRu: Record<string, string> = {
  Ayanamsa: "Айанамша",
  Birth: "Рождение",
  Ephemeris: "Эфемериды",
  Karana: "Карана",
  Lagna: "Лагна",
  Moon: "Луна",
  Panchanga: "Панчанга",
  Place: "Место",
  Sun: "Солнце",
  Tithi: "Титхи",
  Vara: "Вара",
  Yoga: "Йога",
};

function labelRu(value: string) {
  return summaryLabelsRu[value] ?? bodyLabelsRu[value] ?? value;
}

function valueRu(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return "Ожидает";
  return String(value).replace(/house (\d+)/g, "дом $1");
}

function statusRu(value: string | null | undefined) {
  if (!value) return "ожидает";
  return calculationStatusLabelsRu[value] ?? value;
}

function formatCoordinate(value: number) {
  return value.toFixed(4);
}

function ChartPreview() {
  return (
    <div className="chart-box" aria-label="Предпросмотр карты раши">
      <svg viewBox="0 0 600 600" role="img" aria-label="Североиндийская сетка карты">
        <rect x="2" y="2" width="596" height="596" fill="white" stroke="#b88a2f" strokeWidth="2" />
        <path d="M2 2 L598 598 M598 2 L2 598" stroke="#c99a43" strokeWidth="1.35" />
        <path d="M300 2 L598 300 L300 598 L2 300 Z" fill="none" stroke="#c99a43" strokeWidth="1.35" />
      </svg>
    </div>
  );
}

function formatDegrees(value: number) {
  return `${value.toFixed(4)}°`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function formatIsoTime(value: string | null | undefined) {
  if (!value) return "";
  const match = value.match(/T(\d{2}:\d{2})/);
  return match?.[1] ?? value;
}

function formatPeriodRange(period: DayPeriod) {
  return `${period.name} ${formatIsoTime(period.starts_at)}-${formatIsoTime(period.ends_at)}`;
}

function isoDateOffset(days: number) {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function GrahaTable({ grahas }: { grahas: GrahaPosition[] }) {
  if (grahas.length === 0) {
    return (
      <div className="readiness-panel">
        <strong>Грахи ещё не рассчитаны</strong>
        <p>Карта заполнится после ответа бэкенда с эфемеридными позициями.</p>
      </div>
    );
  }

  return (
    <div className="planet-table">
      <div className="table-row table-head">
        <span>Граха</span>
        <span>Долгота</span>
        <span>Раши</span>
        <span>Накшатра</span>
        <span>D9</span>
      </div>
      {grahas.map((graha) => (
        <div className="table-row" key={graha.body}>
          <strong>{labelRu(graha.body)}</strong>
          <span>{formatDegrees(graha.longitude)}</span>
          <span>{graha.rashi}</span>
          <span>
            {graha.nakshatra} {graha.pada}
          </span>
          <span>{graha.navamsa}</span>
        </div>
      ))}
    </div>
  );
}

function VargaTable({ placements, code }: { placements: VargaPlacement[]; code: string }) {
  if (placements.length === 0) {
    return (
      <div className="readiness-panel">
        <strong>Положения {code} ещё не рассчитаны</strong>
        <p>Варга появится после расчёта грах и лагны.</p>
      </div>
    );
  }

  return (
    <div className="planet-table compact-table">
      <div className="table-row table-head">
        <span>Точка</span>
        <span>Раши {code}</span>
      </div>
      {placements.map((placement) => (
        <div className="table-row" key={placement.body}>
          <strong>{labelRu(placement.body)}</strong>
          <span>{placement.rashi}</span>
        </div>
      ))}
    </div>
  );
}

function DashaTimeline({ periods }: { periods: DashaPeriod[] }) {
  if (periods.length === 0) {
    return (
      <div className="pending-strip">
        Периоды даш появятся здесь после расчёта долготы Луны и движка Вимшоттари.
      </div>
    );
  }

  return (
    <div className="dasha-timeline">
      {periods.map((period) => (
        <div className="dasha-period" key={`${period.lord}-${period.starts_at}`}>
          <strong>{labelRu(period.lord)}</strong>
          <span>{period.duration_years.toFixed(2)} г.</span>
          <small>
            {formatDate(period.starts_at)} - {formatDate(period.ends_at)}
          </small>
        </div>
      ))}
    </div>
  );
}

function PersonSummaryPanel({ summary }: { summary: PersonSummary | null }) {
  if (!summary) {
    return (
      <section className="panel person-summary-panel">
        <div className="panel-heading">
          <h2>Сводка по человеку</h2>
          <span>Ожидает расчёт</span>
        </div>
        <div className="pending-strip">Основные факты рождения появятся после расчёта.</div>
      </section>
    );
  }

  return (
    <section className="panel person-summary-panel">
      <div className="panel-heading">
        <h2>Сводка по человеку</h2>
        <span>Пока только расчётные факты</span>
      </div>
      <div className="summary-content">
        <div className="summary-grid">
          {summary.core_factors.map((item) => (
            <div className="summary-card" key={item.label}>
              <span>{labelRu(item.label)}</span>
              <strong>{valueRu(item.value)}</strong>
              {item.detail ? <small>{valueRu(item.detail)}</small> : null}
            </div>
          ))}
        </div>
        <div className="summary-columns">
          <div className="summary-list">
            <h3>Контекст рождения</h3>
            {summary.birth_context.map((item) => (
              <div key={item.label}>
                <span>{labelRu(item.label)}</span>
                <strong>{valueRu(item.value)}</strong>
              </div>
            ))}
          </div>
          <div className="summary-list">
            <h3>Панчанга</h3>
            {summary.panchanga.map((item) => (
              <div key={item.label}>
                <span>{labelRu(item.label)}</span>
                <strong>{valueRu(item.value)}</strong>
              </div>
            ))}
            <div>
              <span>Даша при рождении</span>
              <strong>{summary.dasha.birth_mahadasha_lord ? labelRu(summary.dasha.birth_mahadasha_lord) : "Ожидает"}</strong>
            </div>
            <div>
              <span>Текущая махадаша</span>
              <strong>{summary.dasha.current_mahadasha ? labelRu(summary.dasha.current_mahadasha.lord) : "Ожидает"}</strong>
            </div>
            <div>
              <span>Текущая антардаша</span>
              <strong>
                {summary.dasha.current_antardasha
                  ? `${labelRu(summary.dasha.current_antardasha.parent_lord ?? "")}/${labelRu(summary.dasha.current_antardasha.lord)}`
                  : "Ожидает"}
              </strong>
            </div>
            <div>
              <span>На дату</span>
              <strong>{summary.dasha.as_of ? formatDate(summary.dasha.as_of) : "Ожидает"}</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function DetailedCalculationsPanel({ summary }: { summary: PersonSummary | null }) {
  const detailedPositions = summary?.detailed_positions ?? [];
  const houses = summary?.houses ?? [];

  return (
    <section className="panel calculation-detail-panel">
      <div className="panel-heading">
        <h2>Расчёты карты</h2>
        <span>D1, D9, накшатры, дома</span>
      </div>
      <div className="summary-content">
        {!summary ? <div className="pending-strip">Подробные расчёты появятся после построения карты.</div> : null}
        {detailedPositions.length ? (
          <div className="detailed-positions">
            <div>
              <h3>Подробные положения</h3>
              <span>D1, D9, накшатра, достоинство</span>
            </div>
            <div className="detailed-table">
              <div className="detailed-row detailed-head">
                <span>Граха</span>
                <span>Карака</span>
                <span>Градусы</span>
                <span>Раши</span>
                <span>D9</span>
                <span>Накшатра</span>
                <span>Дом</span>
                <span>Упр.</span>
                <span>Сила</span>
              </div>
              {detailedPositions.map((row) => (
                <div className="detailed-row" key={row.body}>
                  <strong>
                    {labelRu(row.body)}
                    {row.retrograde ? " R" : ""}
                  </strong>
                  <span>{row.chara_karaka ?? "-"}</span>
                  <span>{row.sign_degrees_dms}</span>
                  <span>{row.rashi}</span>
                  <span>{row.navamsa}</span>
                  <span>
                    {row.nakshatra} {row.pada ?? ""}
                  </span>
                  <span>{row.house ?? "-"}</span>
                  <span>{row.ruled_houses.length ? row.ruled_houses.join(", ") : "-"}</span>
                  <span>{row.dignity}</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
        {houses.length ? (
          <div className="house-overview">
            <div>
              <h3>Обзор домов</h3>
              <span>Цельнознаковые дома</span>
            </div>
            <div className="house-grid">
              {houses.map((house) => (
                <div className="house-card" key={house.house}>
                  <span>Дом {house.house}</span>
                  <strong>{house.rashi}</strong>
                  <small>{house.grahas.length ? house.grahas.map(labelRu).join(", ") : "Пусто"}</small>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function DashaWorkspacePanel({ summary, periods }: { summary: PersonSummary | null; periods: DashaPeriod[] }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Периоды Вимшоттари</h2>
        <span>{periods.length ? "Махадаши и текущие антардаши" : "Ожидает долготу Луны"}</span>
      </div>
      <DashaTimeline periods={periods} />
      {summary?.dasha.current_mahadasha_antardashas.length ? (
        <div className="antardasha-panel">
          <div>
            <h3>Антардаши текущей махадаши</h3>
            <span>{summary.dasha.current_mahadasha ? labelRu(summary.dasha.current_mahadasha.lord) : "Ожидает"} махадаша</span>
          </div>
          <div className="antardasha-strip">
            {summary.dasha.current_mahadasha_antardashas.map((period) => {
              const isActive =
                period.lord === summary.dasha.current_antardasha?.lord &&
                period.parent_lord === summary.dasha.current_antardasha?.parent_lord;
              return (
                <div className={isActive ? "antardasha-item active" : "antardasha-item"} key={`${period.parent_lord}-${period.lord}-${period.starts_at}`}>
                  <strong>{labelRu(period.lord)}</strong>
                  <span>{period.duration_years.toFixed(2)} г.</span>
                  <small>
                    {formatDate(period.starts_at)} - {formatDate(period.ends_at)}
                  </small>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function ReportPreviewPanel({ birthReport }: { birthReport: BirthReport["report"] | null }) {
  return (
    <section className="panel report-preview">
      <div className="panel-heading">
        <h2>Разбор карты</h2>
        <span>{birthReport ? birthReport.review_status : "Отчёт ожидает расчёт"}</span>
      </div>
      {birthReport ? (
        <div className="report-sections">
          {birthReport.sections.map((section) => (
            <article className="report-section" key={section.key}>
              <div>
                <strong>{section.title}</strong>
                <em>{section.review_status}</em>
              </div>
              <p>{section.body}</p>
              {section.citations.length ? (
                <div className="report-citations">
                  {section.citations.map((citation) => (
                    <a href={citation.public_url || "#"} key={`${section.key}-${citation.title}`} target="_blank" rel="noreferrer">
                      {citation.title || citation.work_title}
                    </a>
                  ))}
                </div>
              ) : null}
            </article>
          ))}
        </div>
      ) : (
        <div className="pending-strip">Отчёт появится после расчёта карты.</div>
      )}
    </section>
  );
}

function ClassicalPanel({ classical }: { classical: BirthChart["classical"] | undefined }) {
  if (!classical) {
    return (
      <section className="panel classical-panel">
        <div className="panel-heading">
          <h2>Дополнительные расчёты</h2>
          <span>Ожидает карту</span>
        </div>
        <div className="pending-strip">Авастхи, варга-сила, йоги и статусы сложных модулей появятся после расчёта.</div>
      </section>
    );
  }

  const statusItems = [
    ["Авастхи", classical.avasthas?.status],
    ["Вимшопака", classical.vimshopaka_bala?.status],
    ["Аштакаварга", classical.ashtakavarga?.status],
    ["Шадбала", classical.shadbala?.status],
    ["Транзиты", classical.transits?.status],
    ["Совместимость", classical.compatibility?.status],
    ["Мухурта", classical.muhurta?.status],
  ];
  const baladi = classical.avasthas?.baladi ?? [];
  const yogas = classical.yogas?.items ?? [];
  const lots = classical.special_points?.arabic_lots ?? [];
  const upagrahas = classical.special_points?.upagrahas.items ?? [];
  const vedicPoints = classical.special_points?.vedic_points.items ?? [];
  const shadbala = classical.shadbala?.items ?? [];
  const ashtakavarga = classical.ashtakavarga;

  return (
    <section className="panel classical-panel">
      <div className="panel-heading">
        <h2>Дополнительные расчёты</h2>
        <span>Черновой слой с явными статусами</span>
      </div>
      <div className="classical-content">
        <div className="classical-status-grid">
          {statusItems.map(([label, status]) => (
            <div className="classical-status" key={label}>
              <span>{label}</span>
              <strong>{statusRu(status)}</strong>
            </div>
          ))}
        </div>
        <div className="classical-columns">
          <div className="classical-list">
            <h3>Авастхи</h3>
            {baladi.slice(0, 9).map((item) => (
              <div key={item.body}>
                <span>{labelRu(item.body)}</span>
                <strong>{item.state}</strong>
                <small>{item.degree_band}°, сила {item.strength}</small>
              </div>
            ))}
          </div>
          <div className="classical-list">
            <h3>Йоги</h3>
            {yogas.length ? (
              yogas.map((item) => (
                <div key={item.key}>
                  <span>{item.name}</span>
                  <strong>{item.bodies.map(labelRu).join(", ")}</strong>
                  <small>{statusRu(item.status)}</small>
                </div>
              ))
            ) : (
              <div>
                <span>Найдено</span>
                <strong>0</strong>
              </div>
            )}
          </div>
          <div className="classical-list">
            <h3>Аргала</h3>
            <div>
              <span>Главная</span>
              <strong>{formatArgalaRows(classical.argala?.primary ?? [])}</strong>
            </div>
            <div>
              <span>Препятствие</span>
              <strong>{formatArgalaRows(classical.argala?.obstruction ?? [])}</strong>
            </div>
          </div>
          <div className="classical-list">
            <h3>Точки</h3>
            {lots.map((point) => (
              <div key={point.key}>
                <span>{point.name}</span>
                <strong>{point.rashi}</strong>
                <small>{formatDegrees(point.longitude)}</small>
              </div>
            ))}
            <div>
              <span>Упаграхи</span>
              <strong>{statusRu(classical.special_points?.upagrahas.status)}</strong>
            </div>
            {upagrahas.map((point) => (
              <div key={point.key}>
                <span>{point.name}</span>
                <strong>{point.local_time ?? formatDegrees(point.longitude)}</strong>
                <small>
                  {point.rashi}
                  {point.period ? ` · ${point.period === "day" ? "день" : "ночь"}` : ""}
                  {point.segment ? ` · сегмент ${point.segment}` : ""}
                </small>
              </div>
            ))}
            <div>
              <span>Ведические точки</span>
              <strong>{statusRu(classical.special_points?.vedic_points.status)}</strong>
            </div>
            {vedicPoints.map((point) => (
              <div key={point.key}>
                <span>{point.name}</span>
                <strong>{point.rashi}</strong>
                <small>{point.nakshatra} {point.pada}</small>
              </div>
            ))}
          </div>
          <div className="classical-list">
            <h3>Аштакаварга</h3>
            <div>
              <span>SAV total</span>
              <strong>{ashtakavarga?.sarva.total ?? "-"}</strong>
              <small>{statusRu(ashtakavarga?.status)}</small>
            </div>
            {Object.entries(ashtakavarga?.bhinna ?? {}).slice(0, 4).map(([body, row]) => (
              <div key={body}>
                <span>{labelRu(body)}</span>
                <strong>{row.total}</strong>
                <small>{row.scores.join(" ")}</small>
              </div>
            ))}
          </div>
          <div className="classical-list">
            <h3>Шадбала</h3>
            {shadbala.slice(0, 4).map((row) => (
              <div key={row.body}>
                <span>{labelRu(row.body)}</span>
                <strong>{row.known_total}</strong>
                <small>
                  N {row.components.naisargika}, U {row.components.uccha}, S {row.components.sthana ?? 0}, D {row.components.dig}, C{" "}
                  {row.components.chesta ?? 0}, K {row.components.kala ?? 0}
                </small>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function formatArgalaRows(rows: { house: number; bodies: string[] }[]) {
  if (!rows.length) return "-";
  return rows.map((row) => `дом ${row.house}: ${row.bodies.map(labelRu).join(", ")}`).join("; ");
}

function TransitPanel({ report, status }: { report: TransitReport | null; status: string }) {
  const rows = report?.transits.slice(0, 9) ?? [];
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2>Транзиты</h2>
        <span>{status}</span>
      </div>
      {rows.length ? (
        <div className="workflow-table">
          <div className="workflow-row workflow-head">
            <span>Граха</span>
            <span>Раши</span>
            <span>От лагны</span>
            <span>От Луны</span>
          </div>
          {rows.map((row) => (
            <div className="workflow-row" key={row.body}>
              <strong>{labelRu(row.body)}</strong>
              <span>{row.rashi}</span>
              <span>{row.house_from_lagna ?? "-"}</span>
              <span>{row.house_from_moon ?? "-"}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="pending-strip">Транзиты появятся после расчёта карты.</div>
      )}
    </section>
  );
}

function MuhurtaPanel({ report, status }: { report: MuhurtaReport | null; status: string }) {
  const rows = report?.candidates.slice(0, 5) ?? [];
  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <h2>Мухурта</h2>
        <span>{status}</span>
      </div>
      {rows.length ? (
        <div className="muhurta-list">
          {rows.map((candidate) => (
            <div className="muhurta-item" key={`${candidate.date}-${candidate.time}`}>
              <strong>{formatDate(candidate.date)} · {candidate.time}</strong>
              <span>{candidate.score}/100</span>
              <small>
                {candidate.panchanga.tithi?.name ?? "Титхи"} · {candidate.panchanga.vara?.name ?? "Вара"}
              </small>
              {candidate.blocked_periods?.length ? (
                <small className="avoid-line">
                  Попадает: {candidate.blocked_periods.map(formatPeriodRange).join("; ")}
                </small>
              ) : null}
              {candidate.day_periods?.length ? (
                <div className="period-chip-row">
                  {candidate.day_periods.map((period) => (
                    <span className="period-chip" key={`${candidate.date}-${period.key}`}>
                      {formatPeriodRange(period)}
                    </span>
                  ))}
                </div>
              ) : null}
              <p>{candidate.reasons.length ? candidate.reasons.join("; ") : "Нейтральная панчанга"}</p>
            </div>
          ))}
          <p className="workflow-note">{report?.vaishnava_note}</p>
        </div>
      ) : (
        <div className="pending-strip">Кандидаты мухурты появятся после расчёта карты.</div>
      )}
    </section>
  );
}

type CompatibilityPanelProps = {
  report: CompatibilityReport | null;
  status: string;
  partnerBirthDate: string;
  setPartnerBirthDate: Dispatch<SetStateAction<string>>;
  partnerBirthTime: string;
  setPartnerBirthTime: Dispatch<SetStateAction<string>>;
  partnerPlaceName: string;
  setPartnerPlaceName: Dispatch<SetStateAction<string>>;
  partnerPlaceMatches: PlaceCandidate[];
  selectedPartnerPlace: PlaceCandidate | null;
  showPartnerPlaceSuggestions: boolean;
  setShowPartnerPlaceSuggestions: Dispatch<SetStateAction<boolean>>;
  partnerPlaceSearchStatus: string;
  onSelectPartnerPlace: (place: PlaceCandidate) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  disabled: boolean;
};

function CompatibilityPanel({
  report,
  status,
  partnerBirthDate,
  setPartnerBirthDate,
  partnerBirthTime,
  setPartnerBirthTime,
  partnerPlaceName,
  setPartnerPlaceName,
  partnerPlaceMatches,
  selectedPartnerPlace,
  showPartnerPlaceSuggestions,
  setShowPartnerPlaceSuggestions,
  partnerPlaceSearchStatus,
  onSelectPartnerPlace,
  onSubmit,
  disabled,
}: CompatibilityPanelProps) {
  const rows = report?.kuta_rows ?? [];
  const scoreLabel = report ? `${report.score.total}/${report.score.max}` : "-";
  const percentLabel = report ? `${report.score.percent.toFixed(1)}%` : "-";
  const levelLabel = report ? compatibilityLevelLabelsRu[report.assessment.level] ?? report.assessment.level : "ожидает";

  return (
    <section className="panel workflow-panel compatibility-panel">
      <div className="panel-heading">
        <h2>Совместимость</h2>
        <span>{status}</span>
      </div>
      <form className="compatibility-form" onSubmit={onSubmit}>
        <div className="compatibility-form-grid">
          <label>
            Дата второго человека
            <input type="date" value={partnerBirthDate} onChange={(event) => setPartnerBirthDate(event.target.value)} />
          </label>
          <label>
            Время второго человека
            <input type="time" value={partnerBirthTime} onChange={(event) => setPartnerBirthTime(event.target.value)} />
          </label>
          <label className="compatibility-place-label">
            Место второго человека
            <input
              value={partnerPlaceName}
              onChange={(event) => {
                setPartnerPlaceName(event.target.value);
                setShowPartnerPlaceSuggestions(true);
              }}
              onFocus={() => setShowPartnerPlaceSuggestions(true)}
              placeholder="Город рождения"
            />
          </label>
        </div>
        <div className="place-suggestions compatibility-suggestions">
          <span>{partnerPlaceSearchStatus}</span>
          {showPartnerPlaceSuggestions && partnerPlaceMatches.length ? (
            <div className="place-suggestion-list">
              {partnerPlaceMatches.slice(0, 5).map((place) => (
                <button type="button" key={place.id} onClick={() => onSelectPartnerPlace(place)}>
                  <strong>{place.label}</strong>
                  <small>{place.timezone} · {formatCoordinate(place.latitude)}, {formatCoordinate(place.longitude)}</small>
                </button>
              ))}
            </div>
          ) : null}
        </div>
        {selectedPartnerPlace ? (
          <div className="compatibility-place-summary">
            <span>Выбрано</span>
            <strong>{selectedPartnerPlace.label}</strong>
            <small>{selectedPartnerPlace.timezone} · {formatCoordinate(selectedPartnerPlace.latitude)}, {formatCoordinate(selectedPartnerPlace.longitude)}</small>
          </div>
        ) : null}
        <button className="secondary-button compatibility-button" type="submit" disabled={disabled}>
          Рассчитать совместимость
        </button>
      </form>

      {report ? (
        <div className="compatibility-result">
          <div className="compatibility-score-grid">
            <div>
              <span>Ашта-кута</span>
              <strong>{scoreLabel}</strong>
              <small>{percentLabel}</small>
            </div>
            <div>
              <span>Оценка</span>
              <strong>{levelLabel}</strong>
              <small>нулевых факторов: {report.assessment.caution_count}</small>
            </div>
            <div>
              <span>Луна A/B</span>
              <strong>{report.moon.person_a.nakshatra} / {report.moon.person_b.nakshatra}</strong>
              <small>{report.moon.person_a.rashi} / {report.moon.person_b.rashi}</small>
            </div>
            <div>
              <span>Покрытие</span>
              <strong>{report.coverage.calculated_kutas}/{report.coverage.total_kutas}</strong>
              <small>{statusRu(report.coverage.status)}</small>
            </div>
          </div>
          <div className="kuta-table">
            <div className="kuta-row kuta-head">
              <span>Кута</span>
              <span>Баллы</span>
              <span>Детали</span>
            </div>
            {rows.map((row) => (
              <div className="kuta-row" key={row.key}>
                <strong>{row.name}</strong>
                <span>{row.score}/{row.max_score}</span>
                <small>{row.details}</small>
              </div>
            ))}
          </div>
          <p className="workflow-note">{report.assessment.note}</p>
        </div>
      ) : (
        <div className="pending-strip">Сначала рассчитай основную карту, затем добавь данные второго человека.</div>
      )}
    </section>
  );
}

export default function Home() {
  const [birthDate, setBirthDate] = useState("1990-08-15");
  const [birthTime, setBirthTime] = useState("10:24");
  const [placeName, setPlaceName] = useState("Вриндаван");
  const [profileName, setProfileName] = useState("Моя карта");
  const [placeMatches, setPlaceMatches] = useState<PlaceCandidate[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<PlaceCandidate | null>(null);
  const [manualTimezone, setManualTimezone] = useState("Asia/Yekaterinburg");
  const [manualLatitude, setManualLatitude] = useState("");
  const [manualLongitude, setManualLongitude] = useState("");
  const [showPlaceSuggestions, setShowPlaceSuggestions] = useState(false);
  const [placeSearchStatus, setPlaceSearchStatus] = useState("Введите город, чтобы увидеть подсказки");
  const [chart, setChart] = useState<BirthChart | null>(null);
  const [chartMode, setChartMode] = useState("D1");
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<AnalysisTab>("overview");
  const [birthReport, setBirthReport] = useState<BirthReport["report"] | null>(null);
  const [transitReport, setTransitReport] = useState<TransitReport | null>(null);
  const [muhurtaReport, setMuhurtaReport] = useState<MuhurtaReport | null>(null);
  const [compatibilityReport, setCompatibilityReport] = useState<CompatibilityReport | null>(null);
  const [lastBirthPayload, setLastBirthPayload] = useState<BirthChartRequest | null>(null);
  const [status, setStatus] = useState("Расчёт не запускался");
  const [workflowStatus, setWorkflowStatus] = useState("Ожидает расчёт карты");
  const [compatibilityStatus, setCompatibilityStatus] = useState("Ожидает основную карту");
  const [partnerBirthDate, setPartnerBirthDate] = useState("1991-01-01");
  const [partnerBirthTime, setPartnerBirthTime] = useState("09:00");
  const [partnerPlaceName, setPartnerPlaceName] = useState("Вриндаван");
  const [partnerPlaceMatches, setPartnerPlaceMatches] = useState<PlaceCandidate[]>([]);
  const [selectedPartnerPlace, setSelectedPartnerPlace] = useState<PlaceCandidate | null>(null);
  const [showPartnerPlaceSuggestions, setShowPartnerPlaceSuggestions] = useState(false);
  const [partnerPlaceSearchStatus, setPartnerPlaceSearchStatus] = useState("Введите город второго человека");
  const [sourceQuery, setSourceQuery] = useState("Krishna protects devotee");
  const [sourceResults, setSourceResults] = useState<VLSearchResult[]>([]);
  const [sourceStatus, setSourceStatus] = useState("Поиск по VL не запускался");
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authUsername, setAuthUsername] = useState("haridas");
  const [authPassword, setAuthPassword] = useState("strong-pass-108");
  const [authStatus, setAuthStatus] = useState("Войдите, чтобы сохранять карты");
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [profileStatus, setProfileStatus] = useState("Сохранённые карты не загружены");

  const calculatedLabel = useMemo(() => {
    if (!chart) return "Карта останется пустой до расчёта эфемеридных позиций.";
    return `${chart.grahas.length} грах рассчитано для ${chart.place.label ?? chart.place.name}.`;
  }, [chart]);
  const vimshottariPeriods = chart?.dashas?.vimshottari?.mahadashas ?? [];
  const vargaOptions = useMemo(
    () => ["D1", ...Object.keys(chart?.vargas ?? {}).filter((code) => code !== "D1")],
    [chart],
  );
  const selectedVarga = chartMode === "D1" ? null : chart?.vargas?.[chartMode] ?? null;
  const selectedVargaPlacements = selectedVarga?.placements ?? [];
  const personSummary = birthReport?.person_summary ?? null;
  const alternatePlaceMatches = useMemo(
    () => placeMatches.filter((place) => place.id !== selectedPlace?.id).slice(0, 4),
    [placeMatches, selectedPlace],
  );
  const chartFacts = useMemo(() => {
    if (!chart) return [];
    return [
      ["Лагна", chart.ascendant?.rashi ?? "Ожидает"],
      ["Титхи", chart.panchanga.tithi ? `${chart.panchanga.tithi.paksha} ${chart.panchanga.tithi.name}` : "Ожидает"],
      ["Вара", chart.panchanga.vara?.name ?? "Ожидает"],
      ["Йога", chart.panchanga.yoga?.name ?? "Ожидает"],
      ["Карана", chart.panchanga.karana?.name ?? "Ожидает"],
      ["UTC-смещение", chart.birth.utc_offset ?? "Ожидает"],
    ];
  }, [chart]);

  useEffect(() => {
    let cancelled = false;
    if (placeName.trim().length < 2) {
      setPlaceMatches([]);
      setSelectedPlace(null);
      setPlaceSearchStatus("Введите город, чтобы увидеть подсказки");
      return;
    }

    setPlaceSearchStatus("Ищу город и часовой пояс...");
    const searchTimeout = window.setTimeout(() => {
      searchPlaces(placeName)
        .then((items) => {
          if (cancelled) return;
          setPlaceMatches(items);
          setSelectedPlace(items[0] ?? null);
          setPlaceSearchStatus(items.length ? `${items.length} подсказок найдено` : "Подсказок нет, можно ввести координаты вручную");
        })
        .catch(() => {
          if (cancelled) return;
          setPlaceMatches([]);
          setSelectedPlace(null);
          setPlaceSearchStatus("Не удалось получить подсказки, можно ввести координаты вручную");
        });
    }, 350);

    return () => {
      cancelled = true;
      window.clearTimeout(searchTimeout);
    };
  }, [placeName]);

  useEffect(() => {
    let cancelled = false;
    if (partnerPlaceName.trim().length < 2) {
      setPartnerPlaceMatches([]);
      setSelectedPartnerPlace(null);
      setPartnerPlaceSearchStatus("Введите город второго человека");
      return;
    }

    setPartnerPlaceSearchStatus("Ищу город второго человека...");
    const searchTimeout = window.setTimeout(() => {
      searchPlaces(partnerPlaceName)
        .then((items) => {
          if (cancelled) return;
          setPartnerPlaceMatches(items);
          setSelectedPartnerPlace(items[0] ?? null);
          setPartnerPlaceSearchStatus(items.length ? `${items.length} подсказок найдено` : "Подсказок нет");
        })
        .catch(() => {
          if (cancelled) return;
          setPartnerPlaceMatches([]);
          setSelectedPartnerPlace(null);
          setPartnerPlaceSearchStatus("Не удалось получить подсказки");
        });
    }, 350);

    return () => {
      cancelled = true;
      window.clearTimeout(searchTimeout);
    };
  }, [partnerPlaceName]);

  useEffect(() => {
    fetchCurrentUser()
      .then((user) => {
        setCurrentUser(user);
        setAuthStatus(user ? `Вход: ${user.username}` : "Войдите, чтобы сохранять карты");
        if (user) {
          refreshProfiles();
        }
      })
      .catch(() => setAuthStatus("Auth API недоступен"));
  }, []);

  function selectPlace(place: PlaceCandidate) {
    setSelectedPlace(place);
    setPlaceName(place.label);
    setShowPlaceSuggestions(false);
  }

  function selectPartnerPlace(place: PlaceCandidate) {
    setSelectedPartnerPlace(place);
    setPartnerPlaceName(place.label);
    setShowPartnerPlaceSuggestions(false);
  }

  function buildBirthPayload(): BirthChartRequest | null {
    const manualLat = Number(manualLatitude.replace(",", "."));
    const manualLon = Number(manualLongitude.replace(",", "."));
    const hasManualPlace = !selectedPlace && Boolean(manualTimezone.trim() && manualLatitude.trim() && manualLongitude.trim());
    if (hasManualPlace && (!Number.isFinite(manualLat) || !Number.isFinite(manualLon))) {
      setStatus("Для ручного места широта и долгота должны быть числами");
      return null;
    }

    return {
      birth_date: birthDate,
      birth_time: birthTime,
      place_name: selectedPlace?.label ?? placeName,
      ...(selectedPlace
        ? {
            place_id: selectedPlace.id,
            country_code: selectedPlace.country_code,
            timezone: selectedPlace.timezone,
            latitude: selectedPlace.latitude,
            longitude: selectedPlace.longitude,
          }
        : hasManualPlace
          ? {
              timezone: manualTimezone.trim(),
              latitude: manualLat,
              longitude: manualLon,
            }
          : {}),
    };
  }

  function buildPartnerPayload(): BirthChartRequest | null {
    if (!selectedPartnerPlace) {
      setCompatibilityStatus("Выбери город второго человека из подсказок");
      return null;
    }
    return {
      birth_date: partnerBirthDate,
      birth_time: partnerBirthTime,
      place_name: selectedPartnerPlace.label,
      place_id: selectedPartnerPlace.id,
      country_code: selectedPartnerPlace.country_code,
      timezone: selectedPartnerPlace.timezone,
      latitude: selectedPartnerPlace.latitude,
      longitude: selectedPartnerPlace.longitude,
    };
  }

  async function refreshProfiles() {
    try {
      const items = await listChartProfiles();
      setProfiles(items);
      setProfileStatus(items.length ? `${items.length} сохранённых карт` : "Сохранённых карт пока нет");
    } catch (error) {
      setProfiles([]);
      setProfileStatus(error instanceof Error ? error.message : "Не удалось загрузить профили");
    }
  }

  async function handleAuth(mode: "login" | "register") {
    setAuthStatus(mode === "login" ? "Вхожу..." : "Создаю пользователя...");
    try {
      const user =
        mode === "login"
          ? await loginUser(authUsername, authPassword)
          : await registerUser(authUsername, authPassword);
      setCurrentUser(user);
      setAuthStatus(`Вход: ${user.username}`);
      await refreshProfiles();
    } catch (error) {
      setCurrentUser(null);
      setProfiles([]);
      setAuthStatus(error instanceof Error ? error.message : "Ошибка авторизации");
    }
  }

  async function handleLogout() {
    await logoutUser();
    setCurrentUser(null);
    setProfiles([]);
    setAuthStatus("Вы вышли");
    setProfileStatus("Сохранённые карты не загружены");
  }

  async function handleSaveProfile() {
    if (!currentUser) {
      setProfileStatus("Сначала войдите или зарегистрируйтесь");
      return;
    }
    const payload = buildBirthPayload();
    if (!payload) return;
    setProfileStatus("Сохраняю карту...");
    try {
      await createChartProfile({
        ...payload,
        display_name: profileName.trim() || "Моя карта",
      });
      await refreshProfiles();
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось сохранить карту");
    }
  }

  async function refreshWorkflowReports(payload: BirthChartRequest) {
    setWorkflowStatus("Считаю транзиты и мухурту...");
    const today = isoDateOffset(0);
    const weekEnd = isoDateOffset(7);
    const [transits, muhurta] = await Promise.allSettled([
      calculateTransits({
        ...payload,
        as_of_date: today,
        as_of_time: "09:00",
      }),
      calculateMuhurta({
        place_name: payload.place_name,
        timezone: payload.timezone,
        latitude: payload.latitude,
        longitude: payload.longitude,
        start_date: today,
        end_date: weekEnd,
        time: "09:00",
      }),
    ]);

    if (transits.status === "fulfilled") {
      setTransitReport(transits.value);
    } else {
      setTransitReport(null);
    }
    if (muhurta.status === "fulfilled") {
      setMuhurtaReport(muhurta.value);
    } else {
      setMuhurtaReport(null);
    }
    setWorkflowStatus(
      transits.status === "fulfilled" && muhurta.status === "fulfilled"
        ? "рассчитано"
        : "частично, см. API",
    );
  }

  async function handleCompatibilitySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const personA = lastBirthPayload ?? buildBirthPayload();
    const personB = buildPartnerPayload();
    if (!personA || !personB) return;

    setCompatibilityStatus("Считаю совместимость...");
    try {
      const result = await calculateCompatibility({
        person_a: personA,
        person_b: personB,
      });
      setCompatibilityReport(result);
      setCompatibilityStatus("рассчитано");
    } catch (error) {
      setCompatibilityReport(null);
      setCompatibilityStatus(error instanceof Error ? error.message : "Ошибка API совместимости");
    }
  }

  async function handleCalculateProfile(profile: ChartProfile) {
    setProfileStatus(`Рассчитываю: ${profile.display_name}`);
    try {
      const calculation = await calculateSavedProfile(profile.id);
      const payload = {
        birth_date: profile.birth_date,
        birth_time: profile.birth_time ?? "",
        place_name: profile.place.label,
        timezone: profile.timezone,
        latitude: profile.place.latitude,
        longitude: profile.place.longitude,
      };
      setChart(calculation.result);
      setChartMode("D1");
      setBirthReport(null);
      setLastBirthPayload(payload);
      setCompatibilityReport(null);
      setCompatibilityStatus("Можно считать совместимость");
      await refreshWorkflowReports(payload);
      setStatus("Сохранённая карта рассчитана");
      await refreshProfiles();
    } catch (error) {
      setProfileStatus(error instanceof Error ? error.message : "Не удалось рассчитать профиль");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Формирую отчёт с приоритетом цитат...");
    try {
      const payload = buildBirthPayload();
      if (!payload) return;
      const result = await generateBirthReport(payload);
      setChart(result.chart);
      setChartMode("D1");
      setBirthReport(result.report);
      setLastBirthPayload(payload);
      setCompatibilityReport(null);
      setCompatibilityStatus("Можно считать совместимость");
      await refreshWorkflowReports(payload);
      setStatus("Отчёт построен");
    } catch (error) {
      setChart(null);
      setBirthReport(null);
      setTransitReport(null);
      setMuhurtaReport(null);
      setCompatibilityReport(null);
      setLastBirthPayload(null);
      setCompatibilityStatus("Ожидает основную карту");
      setStatus(error instanceof Error ? error.message : "Ошибка API");
    }
  }

  async function handleSourceSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSourceStatus("Ищу в VL...");
    try {
      const results = await searchVLSources(sourceQuery);
      setSourceResults(results);
      setSourceStatus(results.length ? `${results.length} результатов` : "В VL ничего не найдено");
    } catch (error) {
      setSourceResults([]);
      setSourceStatus(error instanceof Error ? error.message : "Ошибка поиска VL");
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="mark">Ом</div>
        <div>
          <h1>Jyotish Agent</h1>
          <p>Гаудия-сиддханта джйотиш</p>
        </div>
        <nav aria-label="Основная навигация">
          <a className="active" href="#chart">Карты</a>
          <a href="#reports" onClick={() => setActiveAnalysisTab("guidance")}>Отчёт</a>
          <a href="#reports" onClick={() => setActiveAnalysisTab("sources")}>Источники</a>
          <a href="#accuracy">Точность</a>
        </nav>
        <blockquote>
          yatha shastram
          <br />
          yatha guru
          <br />
          tatha siddhantah
        </blockquote>
        <div className="operator">
          <strong>Режим проверки</strong>
          <span>Только draft-правила</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="mantra">Hare Krishna Hare Krishna Krishna Krishna Hare Hare</div>
          <div className="top-actions">
            <button type="button">Источники</button>
            <button type="button">Настройки</button>
          </div>
        </header>

        <div className="content-grid">
          <section className="panel birth-panel" id="chart">
            <div className="panel-heading">
              <h2>Данные рождения</h2>
              <button type="button" className="secondary-button">Пример</button>
            </div>
            <form onSubmit={handleSubmit} className="birth-form">
              <label>
                Дата рождения
                <input type="date" value={birthDate} onChange={(event) => setBirthDate(event.target.value)} />
              </label>
              <label>
                Время рождения
                <input type="time" value={birthTime} onChange={(event) => setBirthTime(event.target.value)} />
              </label>
              <label>
                Место рождения
                <input
                  value={placeName}
                  onChange={(event) => {
                    setPlaceName(event.target.value);
                    setShowPlaceSuggestions(true);
                  }}
                  onFocus={() => setShowPlaceSuggestions(true)}
                  placeholder="Город или святое место"
                />
              </label>
              <div className="place-suggestions">
                <span>{placeSearchStatus}</span>
                {showPlaceSuggestions && placeMatches.length ? (
                  <div className="place-suggestion-list">
                    {placeMatches.slice(0, 6).map((place) => (
                      <button type="button" key={place.id} onClick={() => selectPlace(place)}>
                        <strong>{place.label}</strong>
                        <small>{place.timezone} · {formatCoordinate(place.latitude)}, {formatCoordinate(place.longitude)}</small>
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
              <div className="place-resolution" aria-live="polite">
                {selectedPlace ? (
                  <>
                    <div className="place-resolution-head">
                      <span>Выбранное место</span>
                      <strong>{selectedPlace.label}</strong>
                    </div>
                    <div className="place-detail-grid">
                      <div className="place-detail-item">
                        <span>Часовой пояс</span>
                        <strong>{selectedPlace.timezone}</strong>
                      </div>
                      <div className="place-detail-item">
                        <span>Широта</span>
                        <strong>{formatCoordinate(selectedPlace.latitude)}</strong>
                      </div>
                      <div className="place-detail-item">
                        <span>Долгота</span>
                        <strong>{formatCoordinate(selectedPlace.longitude)}</strong>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="manual-place-panel">
                    <span>Каталог не нашёл точное место. Можно рассчитать вручную по IANA timezone и координатам.</span>
                    <div className="manual-place-grid">
                      <label>
                        Часовой пояс
                        <input
                          value={manualTimezone}
                          onChange={(event) => setManualTimezone(event.target.value)}
                          placeholder="Asia/Yekaterinburg"
                        />
                      </label>
                      <label>
                        Широта
                        <input
                          inputMode="decimal"
                          value={manualLatitude}
                          onChange={(event) => setManualLatitude(event.target.value)}
                          placeholder="56.8389"
                        />
                      </label>
                      <label>
                        Долгота
                        <input
                          inputMode="decimal"
                          value={manualLongitude}
                          onChange={(event) => setManualLongitude(event.target.value)}
                          placeholder="60.6057"
                        />
                      </label>
                    </div>
                  </div>
                )}
              </div>
              {alternatePlaceMatches.length ? (
                <div className="place-match-list">
                  <span>Другие совпадения</span>
                  {alternatePlaceMatches.map((place) => (
                    <button type="button" key={place.id} onClick={() => selectPlace(place)}>
                      <strong>{place.label}</strong>
                      <small>{place.timezone} · {formatCoordinate(place.latitude)}, {formatCoordinate(place.longitude)}</small>
                    </button>
                  ))}
                </div>
              ) : null}
              <div className="notice">
                Политика MVP: айанамша Lahiri, рамка Парашары, обязательные ссылки на источники.
              </div>
              <button className="primary-button" type="submit">Рассчитать карту</button>
              <p className="status-line">{status}</p>
            </form>
            <div className="account-block">
              <div className="block-heading">
                <h3>Аккаунт и сохранение</h3>
                <span>{authStatus}</span>
              </div>
              {currentUser ? (
                <div className="account-row">
                  <strong>{currentUser.username}</strong>
                  <button type="button" className="secondary-button" onClick={handleLogout}>Выйти</button>
                </div>
              ) : (
                <div className="auth-grid">
                  <label>
                    Логин
                    <input value={authUsername} onChange={(event) => setAuthUsername(event.target.value)} />
                  </label>
                  <label>
                    Пароль
                    <input
                      type="password"
                      value={authPassword}
                      onChange={(event) => setAuthPassword(event.target.value)}
                    />
                  </label>
                  <div className="auth-actions">
                    <button type="button" className="secondary-button" onClick={() => handleAuth("login")}>Войти</button>
                    <button type="button" className="secondary-button" onClick={() => handleAuth("register")}>Регистрация</button>
                  </div>
                </div>
              )}
              <label>
                Название карты
                <input value={profileName} onChange={(event) => setProfileName(event.target.value)} />
              </label>
              <button type="button" className="secondary-button save-profile-button" onClick={handleSaveProfile}>
                Сохранить профиль рождения
              </button>
            </div>
            <div className="profile-block">
              <div className="block-heading">
                <h3>Сохранённые карты</h3>
                <button type="button" className="secondary-button" onClick={refreshProfiles}>Обновить</button>
              </div>
              <p>{profileStatus}</p>
              {profiles.length ? (
                <div className="profile-list">
                  {profiles.map((profile) => (
                    <div className="profile-row" key={profile.id}>
                      <div>
                        <strong>{profile.display_name}</strong>
                        <span>{profile.birth_date} · {profile.place.label}</span>
                        <small>
                          {profile.latest_calculation
                            ? `${profile.latest_calculation.status}, ${profile.latest_calculation.graha_count} грах`
                            : "Расчёт ещё не сохранён"}
                        </small>
                      </div>
                      <button type="button" className="secondary-button" onClick={() => handleCalculateProfile(profile)}>
                        Рассчитать
                      </button>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          </section>

          <section className="main-stack">
            <section className="panel chart-panel">
              <div className="panel-heading">
                <h2>{chartMode === "D1" ? "Карта раши" : `${chartMode} ${selectedVarga?.name ?? "варга"}`}</h2>
                <select
                  value={chartMode}
                  onChange={(event) => setChartMode(event.target.value)}
                >
                  {vargaOptions.map((code) => (
                    <option value={code} key={code}>
                      {code === "D1" ? "D1 Раши" : `${code} ${chart?.vargas?.[code]?.name ?? ""}`}
                    </option>
                  ))}
                </select>
              </div>
              <div className="chart-layout">
                <ChartPreview />
                <div className="chart-data-stack">
                  {chartMode === "D1" ? (
                    <GrahaTable grahas={chart?.grahas ?? []} />
                  ) : (
                    <VargaTable placements={selectedVargaPlacements} code={chartMode} />
                  )}
                  {chartFacts.length ? (
                    <div className="fact-grid">
                      {chartFacts.map(([label, value]) => (
                        <div className="fact-item" key={label}>
                          <span>{label}</span>
                          <strong>{value}</strong>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
              <p className="calculation-result">{calculatedLabel}</p>
            </section>

            <section className="analysis-workspace" id="reports">
              <div className="analysis-tabs" role="tablist" aria-label="Разделы анализа">
                {analysisTabs.map((tab) => (
                  <button
                    type="button"
                    key={tab.key}
                    className={activeAnalysisTab === tab.key ? "active" : ""}
                    onClick={() => setActiveAnalysisTab(tab.key)}
                    role="tab"
                    aria-selected={activeAnalysisTab === tab.key}
                  >
                    <strong>{tab.label}</strong>
                    <span>{tab.hint}</span>
                  </button>
                ))}
              </div>
              <div className="analysis-panel-slot">
                {activeAnalysisTab === "overview" ? <PersonSummaryPanel summary={personSummary} /> : null}
                {activeAnalysisTab === "calculations" ? <DetailedCalculationsPanel summary={personSummary} /> : null}
                {activeAnalysisTab === "yogas" ? <ClassicalPanel classical={chart?.classical} /> : null}
                {activeAnalysisTab === "timeline" ? <DashaWorkspacePanel summary={personSummary} periods={vimshottariPeriods} /> : null}
                {activeAnalysisTab === "guidance" ? <ReportPreviewPanel birthReport={birthReport} /> : null}
                {activeAnalysisTab === "workflows" ? (
                  <div className="analysis-tab-stack">
                    <TransitPanel report={transitReport} status={workflowStatus} />
                    <MuhurtaPanel report={muhurtaReport} status={workflowStatus} />
                    <CompatibilityPanel
                      report={compatibilityReport}
                      status={compatibilityStatus}
                      partnerBirthDate={partnerBirthDate}
                      setPartnerBirthDate={setPartnerBirthDate}
                      partnerBirthTime={partnerBirthTime}
                      setPartnerBirthTime={setPartnerBirthTime}
                      partnerPlaceName={partnerPlaceName}
                      setPartnerPlaceName={setPartnerPlaceName}
                      partnerPlaceMatches={partnerPlaceMatches}
                      selectedPartnerPlace={selectedPartnerPlace}
                      showPartnerPlaceSuggestions={showPartnerPlaceSuggestions}
                      setShowPartnerPlaceSuggestions={setShowPartnerPlaceSuggestions}
                      partnerPlaceSearchStatus={partnerPlaceSearchStatus}
                      onSelectPartnerPlace={selectPartnerPlace}
                      onSubmit={handleCompatibilitySubmit}
                      disabled={!chart}
                    />
                  </div>
                ) : null}
                {activeAnalysisTab === "sources" ? (
                  <section className="panel" id="sources">
                    <div className="panel-heading">
                      <h2>Цитаты и статус источников</h2>
                      <button type="button" className="secondary-button">Все источники</button>
                    </div>
                    <form className="source-search" onSubmit={handleSourceSearch}>
                      <input value={sourceQuery} onChange={(event) => setSourceQuery(event.target.value)} />
                      <button type="submit" className="secondary-button">Искать в VL</button>
                      <span>{sourceStatus}</span>
                    </form>
                    {sourceResults.length ? (
                      <div className="source-results">
                        {sourceResults.map((result) => (
                          <a href={result.public_url || "#"} key={result.id} target="_blank" rel="noreferrer">
                            <strong>{result.title || result.work_title}</strong>
                            <span>{result.work_title}</span>
                            <p>{result.body}</p>
                          </a>
                        ))}
                      </div>
                    ) : null}
                    <div className="source-table">
                      {sourceRows.map(([component, source, citation, state]) => (
                        <div className="source-row" key={component}>
                          <strong>{component}</strong>
                          <span>{source}</span>
                          <span>{citation}</span>
                          <em className={state}>{stateLabels[state] ?? state}</em>
                        </div>
                      ))}
                    </div>
                  </section>
                ) : null}
              </div>
            </section>
          </section>
        </div>
      </section>
    </main>
  );
}
