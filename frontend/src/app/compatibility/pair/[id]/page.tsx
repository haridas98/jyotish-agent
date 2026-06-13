"use client";

import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { HelpTerm, HouseTerms, VargaTerms, houseHelpText, vargaHelpText, type HelpItem } from "@/app/relationship-help";
import {
  calculateSavedProfile,
  fetchChartProfileRelationship,
  type BirthChart,
  type ChartCalculationRecord,
  type ChartProfileRelationship,
  type GrahaPosition,
  type VargaChart,
} from "@/lib/api";
import { relationshipRoleFor, type RelationshipRoleDefinition } from "@/lib/relationshipRoles";

const rashiNames = [
  "Mesha",
  "Vrishabha",
  "Mithuna",
  "Karka",
  "Simha",
  "Kanya",
  "Tula",
  "Vrischika",
  "Dhanu",
  "Makara",
  "Kumbha",
  "Meena",
];

const rashiLords = [
  "Mangala",
  "Shukra",
  "Budha",
  "Chandra",
  "Surya",
  "Budha",
  "Shukra",
  "Mangala",
  "Guru",
  "Shani",
  "Shani",
  "Guru",
];

const southIndianSignCells: Record<number, { row: number; col: number }> = {
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

function statusLabel(status: string): string {
  if (status === "accepted") return "подтверждённая связь";
  if (status === "requested") return "ожидает подтверждения";
  if (status === "declined") return "отклонено";
  if (status === "blocked") return "заблокировано";
  return "личная заметка";
}

function statusVisibilityText(status: string): string {
  if (status === "accepted") return "Оба зарегистрированных пользователя подтвердили связь и видят её у себя.";
  if (status === "requested") return "Запрос отправлен зарегистрированному пользователю, но связь ещё не стала общей.";
  if (status === "declined") return "Запрос отклонён; используйте только свои сохранённые карты и не считайте связь подтверждённой.";
  if (status === "blocked") return "Пользователь запретил повторные запросы по этой связи.";
  return "Это только ваша личная пометка. Второй человек не видит эту связь и не получает уведомление.";
}

function statusAiPolicyText(status: string): string {
  if (status === "accepted") return "AI может явно учитывать роль и факт подтверждённой связи.";
  if (status === "requested") return "AI должен трактовать связь как ожидающую согласия, без вывода о взаимном подтверждении.";
  if (status === "declined" || status === "blocked") return "AI не должен подавать такую связь как согласованную между пользователями.";
  return "AI может использовать эту пару как вашу частную заметку, но не как подтверждённую связь двух аккаунтов.";
}

function statusHelp(status: string): HelpItem {
  return {
    title: statusLabel(status),
    text: `${statusVisibilityText(status)} ${statusAiPolicyText(status)}`,
  };
}

function roleHelp(role: RelationshipRoleDefinition): HelpItem {
  return {
    title: role.label,
    text: `Ракурс чтения: ${role.focus}. Под него выбраны фокусные дома и D-карты в этом паспорте пары.`,
  };
}

function profileTitle(profile: ChartProfileRelationship["profile"]): string {
  return profile?.display_name || "Карта";
}

function profileMeta(profile: ChartProfileRelationship["profile"]): string {
  return [profile?.birth_date, profile?.place_label].filter(Boolean).join(" · ") || "данные карты";
}

function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => reject(new Error(`${label}: API не ответил вовремя`)), ms);
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

function StatusTerm({ status }: { status: string }) {
  return (
    <HelpTerm item={statusHelp(status)}>
      <span>{statusLabel(status)}</span>
    </HelpTerm>
  );
}

function bodyLabel(body: string | null | undefined): string {
  const labels: Record<string, string> = {
    Surya: "Su",
    Chandra: "Mo",
    Mangala: "Ma",
    Budha: "Me",
    Guru: "Ju",
    Shukra: "Ve",
    Shani: "Sa",
    Rahu: "Ra",
    Ketu: "Ke",
    Lagna: "As",
  };
  return body ? labels[body] ?? body : "-";
}

function normalizeRashiIndex(value: number | null | undefined): number | null {
  if (typeof value !== "number" || Number.isNaN(value)) return null;
  if (value >= 0 && value <= 11) return value;
  if (value >= 1 && value <= 12) return value - 1;
  return null;
}

function rashiIndexFromName(name: string | null | undefined): number | null {
  if (!name) return null;
  const normalized = name.trim().toLowerCase();
  const index = rashiNames.findIndex((item) => item.toLowerCase() === normalized);
  return index >= 0 ? index : null;
}

function placementSignIndex(placement: Pick<GrahaPosition, "rashi" | "rashi_index"> | { rashi: string; rashi_index?: number }): number | null {
  return normalizeRashiIndex(placement.rashi_index) ?? rashiIndexFromName(placement.rashi);
}

function placementLine(placement: GrahaPosition | null | undefined): string {
  if (!placement) return "-";
  return `${bodyLabel(placement.body)} · ${placement.rashi} ${placement.nakshatra ?? ""} ${placement.pada ?? ""}`.trim();
}

function moon(chart: BirthChart | null): GrahaPosition | null {
  return chart?.grahas.find((graha) => graha.body === "Chandra") ?? null;
}

function sun(chart: BirthChart | null): GrahaPosition | null {
  return chart?.grahas.find((graha) => graha.body === "Surya") ?? null;
}

function grahaByBody(chart: BirthChart | null, body: string | null): GrahaPosition | null {
  if (!chart || !body) return null;
  return chart.grahas.find((graha) => graha.body === body) ?? null;
}

function houseFromLagna(chart: BirthChart | null, placement: GrahaPosition | null): number | null {
  const lagnaIndex = chart?.ascendant ? placementSignIndex(chart.ascendant) : null;
  const signIndex = placement ? placementSignIndex(placement) : null;
  if (lagnaIndex === null || signIndex === null) return null;
  return ((signIndex - lagnaIndex + 12) % 12) + 1;
}

function houseLine(chart: BirthChart | null, house: number): string {
  const item = chart?.houses?.find((row) => row.house === house);
  if (!item) return "-";
  return item.rashi;
}

function houseLord(chart: BirthChart | null, house: number): string | null {
  const item = chart?.houses?.find((row) => row.house === house);
  const signIndex = normalizeRashiIndex(item?.rashi_index);
  return signIndex === null ? null : rashiLords[signIndex] ?? null;
}

function houseLordLine(chart: BirthChart | null, house: number): string {
  const lord = houseLord(chart, house);
  const placement = grahaByBody(chart, lord);
  if (!lord || !placement) return "-";
  const placementHouse = houseFromLagna(chart, placement);
  const dignity = placement.dignity ? ` · ${placement.dignity}` : "";
  return `${bodyLabel(lord)} в ${placement.rashi}${placementHouse ? ` · ${placementHouse} дом` : ""}${dignity}`;
}

function vargaLine(chart: BirthChart | null, code: string): string {
  if (code === "D1") return `Лагна: ${placementLine(chart?.ascendant)}`;
  const varga = chart?.vargas?.[code];
  if (!varga) return "нет расчёта";
  const lagna = varga.placements?.find((item) => item.body === "Lagna" || item.body === "Ascendant");
  const moonPlacement = varga.placements?.find((item) => item.body === "Chandra");
  return [lagna ? `As ${lagna.rashi}` : "", moonPlacement ? `Mo ${moonPlacement.rashi}` : ""].filter(Boolean).join(" · ") || "есть расчёт";
}

function chartVarga(chart: BirthChart | null, code: string): VargaChart | null {
  if (!chart || code === "D1") return null;
  return chart.vargas?.[code] ?? null;
}

function PairCalculationLedger({ chart, role }: { chart: BirthChart | null; role: RelationshipRoleDefinition }) {
  const focusVargas = Array.from(new Set(["D9", ...role.vargas])).slice(0, 4);
  const rows = [
    { label: "Лагна", value: placementLine(chart?.ascendant), help: "исходная точка чтения характера и тела" },
    { label: "Луна", value: placementLine(moon(chart)), help: "ум, эмоциональный отклик и совместимость по накшатре" },
    { label: "Солнце", value: placementLine(sun(chart)), help: "самость, авторитет, отец и видимое эго" },
    ...role.houses.slice(0, 5).map((house) => ({
      label: `${house} дом`,
      value: `${houseLine(chart, house)} · хозяин: ${houseLordLine(chart, house)}`,
      help: houseHelpText(house),
    })),
    ...focusVargas.map((code) => ({
      label: code,
      value: vargaLine(chart, code),
      help: vargaHelpText(code),
    })),
  ];

  return (
    <div className="compatibility-calculation-ledger" aria-label="Расчётная сводка пары">
      <div className="compatibility-calculation-ledger-head">
        <strong>Расчёты</strong>
        <span>первое, что проверяет астролог</span>
      </div>
      <div className="compatibility-calculation-ledger-grid">
        {rows.map((row) => (
          <div key={`${row.label}-${row.value}`}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
            <small>{row.help}</small>
          </div>
        ))}
      </div>
    </div>
  );
}

function PairMiniChart({ chart, code }: { chart: BirthChart | null; code: string }) {
  const varga = chartVarga(chart, code);
  const bySign = new Map<number, string[]>();
  let lagnaIndex: number | null = null;

  if (chart && code === "D1") {
    lagnaIndex = chart.ascendant ? placementSignIndex(chart.ascendant) : null;
    if (lagnaIndex !== null) bySign.set(lagnaIndex, ["As"]);
    for (const graha of chart.grahas) {
      const signIndex = placementSignIndex(graha);
      if (signIndex === null) continue;
      bySign.set(signIndex, [...(bySign.get(signIndex) ?? []), bodyLabel(graha.body)]);
    }
  } else if (varga) {
    for (const placement of varga.placements) {
      const signIndex = placementSignIndex(placement);
      if (signIndex === null) continue;
      const label = placement.body === "Lagna" || placement.body === "Ascendant" ? "As" : bodyLabel(placement.body);
      if (label === "As") lagnaIndex = signIndex;
      bySign.set(signIndex, [...(bySign.get(signIndex) ?? []), label]);
    }
  }

  return (
    <div className="compatibility-mini-rashi-grid" aria-label={`${code}: южноиндийская мини-карта`}>
      {Array.from({ length: 16 }, (_, cellIndex) => {
        const row = Math.floor(cellIndex / 4);
        const col = cellIndex % 4;
        const signIndexEntry = Object.entries(southIndianSignCells).find(([, cell]) => cell.row === row && cell.col === col);
        if (!signIndexEntry) return <div className="compatibility-mini-rashi-center" key={`center-${cellIndex}`} />;
        const signIndex = Number(signIndexEntry[0]);
        const labels = bySign.get(signIndex) ?? [];
        return (
          <div className={lagnaIndex === signIndex ? "compatibility-mini-rashi-cell active" : "compatibility-mini-rashi-cell"} key={`${code}-${signIndex}`}>
            <span>{signIndex + 1}</span>
            {labels.slice(0, 3).map((label) => (
              <strong key={`${code}-${signIndex}-${label}`}>{label}</strong>
            ))}
            {labels.length > 3 ? <em>+{labels.length - 3}</em> : null}
          </div>
        );
      })}
    </div>
  );
}

function PairChartBoard({ chart, role }: { chart: BirthChart | null; role: RelationshipRoleDefinition }) {
  const codes = Array.from(new Set(["D1", ...role.vargas])).slice(0, 4);
  return (
    <div className="compatibility-mini-chart-board" aria-label="Визуальные карты для выбранной роли">
      {codes.map((code) => (
        <div className="compatibility-mini-chart-card" key={`pair-mini-${code}`}>
          <div>
            <strong><VargaTerms vargas={[code]} /></strong>
            <span>{code === "D1" ? "основа" : chart?.vargas?.[code]?.name ?? "роль"}</span>
          </div>
          {chart ? <PairMiniChart chart={chart} code={code} /> : <small>Нажмите «Загрузить расчёты пары»</small>}
        </div>
      ))}
    </div>
  );
}

function PairPersonCard({
  label,
  profile,
  calculation,
  role,
}: {
  label: string;
  profile: ChartProfileRelationship["profile"];
  calculation: ChartCalculationRecord | null;
  role: RelationshipRoleDefinition;
}) {
  const chart = calculation?.result ?? null;
  return (
    <article className="compatibility-person-card">
      <div>
        <span>{label}</span>
        <strong>{profileTitle(profile)}</strong>
        <small>{profileMeta(profile)}</small>
      </div>
      <dl className="compatibility-person-facts">
        <div>
          <dt>Лагна</dt>
          <dd>{placementLine(chart?.ascendant)}</dd>
        </div>
        <div>
          <dt>Луна</dt>
          <dd>{placementLine(moon(chart))}</dd>
        </div>
        {role.houses.map((house) => (
          <div key={`${profile?.id ?? label}-focus-house-${house}`}>
            <dt><HouseTerms houses={[house]} /></dt>
            <dd>{houseLine(chart, house)}</dd>
          </div>
        ))}
      </dl>
      <PairCalculationLedger chart={chart} role={role} />
      <PairChartBoard chart={chart} role={role} />
      <div className="compatibility-varga-list">
        {role.vargas.map((code) => (
          <div key={code}>
            <span><VargaTerms vargas={[code]} /></span>
            <small>{vargaLine(chart, code)}</small>
          </div>
        ))}
      </div>
    </article>
  );
}

export default function CompatibilityPairPage() {
  const params = useParams<{ id: string }>();
  const relationshipId = Number(Array.isArray(params.id) ? params.id[0] : params.id);
  const [relationship, setRelationship] = useState<ChartProfileRelationship | null>(null);
  const [calculations, setCalculations] = useState<Record<number, ChartCalculationRecord>>({});
  const [status, setStatus] = useState("Загружаю пару...");
  const [loadingCharts, setLoadingCharts] = useState(false);

  useEffect(() => {
    let mounted = true;
    if (!Number.isFinite(relationshipId)) {
      setStatus("Некорректный id пары");
      return;
    }
    withTimeout(fetchChartProfileRelationship(relationshipId), 7000, "Пара")
      .then((result) => {
        if (!mounted) return;
        setRelationship(result);
        setStatus("");
      })
      .catch((error) => {
        if (!mounted) return;
        setStatus(error instanceof Error ? error.message : "Ошибка загрузки пары");
      });
    return () => {
      mounted = false;
    };
  }, [relationshipId]);

  const role = useMemo(() => relationshipRoleFor(relationship?.role ?? "other"), [relationship?.role]);

  useEffect(() => {
    if (!relationship) return;
    if (calculations[relationship.profile_id] && calculations[relationship.related_profile_id]) return;
    void loadPairCharts();
  }, [relationship?.id]);

  async function loadPairCharts() {
    if (!relationship) return;
    setLoadingCharts(true);
    setStatus("Загружаю расчёты обеих карт...");
    try {
      const [base, related] = await Promise.all([
        withTimeout(calculateSavedProfile(relationship.profile_id), 12000, "Карта A"),
        withTimeout(calculateSavedProfile(relationship.related_profile_id), 12000, "Карта B"),
      ]);
      setCalculations({ [relationship.profile_id]: base, [relationship.related_profile_id]: related });
      setStatus("Расчёты пары загружены");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось загрузить расчёты пары");
    } finally {
      setLoadingCharts(false);
    }
  }

  return (
    <ProductShell active="compatibility">
      <header className="product-page-head">
        <div>
          <h1>Паспорт пары</h1>
          <p>Две карты, роль второго человека, фокусные дома и D-карты перед запуском AI-разбора.</p>
        </div>
        <a className="secondary-button" href="/compatibility">Назад</a>
      </header>
      {status ? <div className="product-status">{status}</div> : null}
      {relationship ? (
        <section className="compatibility-detail-context">
          <div className="compatibility-context-head">
            <div>
              <h2>
                {profileTitle(relationship.profile)} → {profileTitle(relationship.related_profile)}
              </h2>
              <p>{profileMeta(relationship.profile)} / {profileMeta(relationship.related_profile)}</p>
            </div>
            <div className="compatibility-context-score">
              <span>Статус связи</span>
              <strong><StatusTerm status={relationship.link_status} /></strong>
              <small>{relationship.requested_user ? `запрос: ${relationship.requested_user.username}` : "без внешнего подтверждения"}</small>
            </div>
          </div>

          <div className="compatibility-saved-role-context">
            <div className="compatibility-saved-role-head">
              <div>
                <span>Ракурс взаимодействия</span>
                <strong>
                  <HelpTerm item={roleHelp(role)}>{role.label}</HelpTerm>
                </strong>
              </div>
              <small>{role.focus}</small>
            </div>
            <div className="compatibility-saved-role-grid">
              <div>
                <span>Фокусные дома</span>
                <strong><HouseTerms houses={role.houses} /></strong>
              </div>
              <div>
                <span>D-карты</span>
                <strong><VargaTerms vargas={role.vargas} /></strong>
              </div>
              <div>
                <span>Человек A</span>
                <strong>{profileTitle(relationship.profile)}</strong>
              </div>
              <div>
                <span>Человек B</span>
                <strong>{profileTitle(relationship.related_profile)}</strong>
              </div>
            </div>
            <div className="compatibility-privacy-note">
              <div>
                <span>Приватность</span>
                <strong><StatusTerm status={relationship.link_status} /></strong>
                <small>{statusVisibilityText(relationship.link_status)}</small>
              </div>
              <div>
                <span>Политика AI</span>
                <strong>{relationship.requested_user ? `запрос: ${relationship.requested_user.username}` : "без внешнего запроса"}</strong>
                <small>{statusAiPolicyText(relationship.link_status)}</small>
              </div>
            </div>
          </div>

          <div className="compatibility-context-grid">
            <PairPersonCard
              label="Человек A"
              profile={relationship.profile}
              calculation={calculations[relationship.profile_id] ?? null}
              role={role}
            />
            <PairPersonCard
              label="Человек B"
              profile={relationship.related_profile}
              calculation={calculations[relationship.related_profile_id] ?? null}
              role={role}
            />
          </div>

          <div className="compatibility-actions">
            <button type="button" className="secondary-button" onClick={loadPairCharts} disabled={loadingCharts}>
              {loadingCharts ? "Загружаю..." : "Загрузить расчёты пары"}
            </button>
            <a className="primary-link-button" href={`/?analysis=compatibility&relationship=${relationship.id}#reports`}>
              Запустить AI-разбор
            </a>
          </div>
        </section>
      ) : null}
    </ProductShell>
  );
}
