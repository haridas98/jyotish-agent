"use client";

import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { HelpTerm, HouseTerms, VargaTerms, type HelpItem } from "@/app/relationship-help";
import {
  calculateSavedProfile,
  listIncomingChartProfileRelationshipRequests,
  listChartProfiles,
  listChartProfileRelationships,
  updateChartProfileRelationshipRequest,
  upsertChartProfileRelationship,
  type BirthChart,
  type ChartCalculationRecord,
  type ChartProfile,
  type ChartProfileRelationship,
  type GrahaPosition,
  type VargaChart,
} from "@/lib/api";
import { relationshipRoleDefinitions, relationshipRoleFor, type RelationshipRoleDefinition } from "@/lib/relationshipRoles";

type InteractionRole = Omit<RelationshipRoleDefinition, "houses"> & { houses: string[] };

const interactionRoles: InteractionRole[] = relationshipRoleDefinitions.map((role) => ({
  ...role,
  houses: role.houses.map(String),
}));

function roleFor(key: string): InteractionRole {
  const role = relationshipRoleFor(key);
  return { ...role, houses: role.houses.map(String) };
}

function statusLabel(status: string): string {
  if (status === "accepted") return "подтверждено";
  if (status === "requested") return "ожидает подтверждения";
  if (status === "declined") return "отклонено";
  if (status === "blocked") return "заблокировано";
  return "личная пометка";
}

const statusHelp: Record<string, HelpItem> = {
  private: {
    title: "Личная пометка",
    text: "Связь хранится только у вас. Второй человек не получает запрос и не видит эту связь.",
  },
  requested: {
    title: "Запрос отправлен",
    text: "Вы указали username зарегистрированного человека. Он должен подтвердить связь, прежде чем она станет общей.",
  },
  accepted: {
    title: "Подтверждено",
    text: "Оба зарегистрированных пользователя подтвердили связь и видят её у себя в профиле.",
  },
  declined: {
    title: "Отклонено",
    text: "Пользователь не подтвердил связь. Для AI-разбора используйте только свои сохранённые карты или новый запрос.",
  },
  blocked: {
    title: "Заблокировано",
    text: "Пользователь запретил повторные запросы по этой связи.",
  },
};

function StatusTerm({ status }: { status: string }) {
  return (
    <HelpTerm item={statusHelp[status] ?? statusHelp.private}>
      <em className={`interaction-status ${status}`}>{statusLabel(status)}</em>
    </HelpTerm>
  );
}

function LinkModePreview({ username }: { username: string }) {
  const hasUsername = Boolean(username.trim());
  return (
    <div className="interaction-link-mode-preview" aria-label="Режим приватности связи">
      <div className={!hasUsername ? "active" : ""}>
        <StatusTerm status="private" />
        <strong>Только моя заметка</strong>
        <span>Второй человек не получает уведомление и не видит эту связь.</span>
      </div>
      <div className={hasUsername ? "active" : ""}>
        <StatusTerm status="requested" />
        <strong>Запрос пользователю</strong>
        <span>После подтверждения связь станет общей и появится у обоих аккаунтов.</span>
      </div>
    </div>
  );
}

function ConsentPolicyPanel() {
  return (
    <section className="interaction-consent-policy" aria-label="Приватность взаимодействий">
      <div>
        <strong>Приватность и согласие</strong>
        <span>Разбор взаимодействия может быть личной заметкой или подтверждённой связью двух аккаунтов.</span>
      </div>
      <div>
        <section>
          <StatusTerm status="private" />
          <strong>Без username</strong>
          <span>связь видна только вам; второй человек не узнаёт о сохранённой карте</span>
        </section>
        <section>
          <StatusTerm status="requested" />
          <strong>С username</strong>
          <span>пользователь получает запрос и сам выбирает свою карту для подтверждения</span>
        </section>
        <section>
          <StatusTerm status="accepted" />
          <strong>После согласия</strong>
          <span>связь появляется у обоих, а AI видит её как подтверждённый контекст</span>
        </section>
      </div>
    </section>
  );
}

function profileLabel(profile: ChartProfileRelationship["profile"], fallback?: ChartProfile): string {
  return profile?.display_name ?? fallback?.display_name ?? "Карта";
}

function profileMeta(profile: ChartProfileRelationship["profile"], fallback?: ChartProfile): string {
  const date = profile?.birth_date ?? fallback?.birth_date ?? "дата не указана";
  const place = profile?.place_label ?? fallback?.place.label ?? "место не указано";
  return `${date} · ${place}`;
}

function roleReadingNote(role: InteractionRole): string {
  const notes: Record<string, string> = {
    partner: "Смотреть обе D1 от лагны и 7 дома, затем D9 и семейные дома 2/8/12.",
    father: "Читать связь через 9 дом, Сурью, D12 и родовой контекст обеих карт.",
    mother: "Читать связь через 4 дом, Чандру, D12 и эмоциональную опору в обеих картах.",
    sibling: "Читать связь через 3 и 11 дома, D3 и повторяющиеся показатели поддержки/соперничества.",
    brother: "Читать связь через 3 дом, D3, Марс и темы инициативы, защиты и конкуренции.",
    sister: "Читать связь через 3/11 дома, D3, Луну/Венеру и эмоциональную коммуникацию.",
    boss: "Читать связь через 10 и 6 дома, D10, статус, обязанности и границы власти.",
    subordinate: "Читать связь через 6 и 10 дома, D10, делегирование, служение и результат.",
    opponent: "Читать связь через 6/8/12 дома, D30 и открытые или скрытые конфликты.",
    other: "Читать связь от лагны и 7 дома как общий контакт двух людей.",
  };
  return notes[role.key] ?? notes.other;
}

const rashiNames = [
  "Mesha",
  "Vrishabha",
  "Mithuna",
  "Karka",
  "Simha",
  "Kanya",
  "Tula",
  "Vrishchika",
  "Dhanu",
  "Makara",
  "Kumbha",
  "Meena",
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
    Ascendant: "As",
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

function houseLine(chart: BirthChart | null, house: string): string {
  const item = chart?.houses?.find((row) => String(row.house) === house);
  return item?.rashi ?? "-";
}

function chartVarga(chart: BirthChart | null, code: string): VargaChart | null {
  if (!chart || code === "D1") return null;
  return chart.vargas?.[code] ?? null;
}

function InteractionMiniChart({ chart, code }: { chart: BirthChart | null; code: string }) {
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
      const label = bodyLabel(placement.body);
      if (label === "As") lagnaIndex = signIndex;
      bySign.set(signIndex, [...(bySign.get(signIndex) ?? []), label]);
    }
  }

  return (
    <div className="compatibility-mini-rashi-grid" aria-label={`${code}: мини-карта`}>
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

function InteractionChartBoard({ chart, role }: { chart: BirthChart | null; role: InteractionRole }) {
  const codes = Array.from(new Set(["D1", ...role.vargas])).slice(0, 4);
  return (
    <div className="compatibility-mini-chart-board" aria-label="Мини-карты для роли взаимодействия">
      {codes.map((code) => (
        <div className="compatibility-mini-chart-card" key={`interaction-mini-${code}`}>
          <div>
            <strong><VargaTerms vargas={[code]} /></strong>
            <span>{code === "D1" ? "основа" : chart?.vargas?.[code]?.name ?? "роль"}</span>
          </div>
          {chart ? <InteractionMiniChart chart={chart} code={code} /> : <small>Нажмите «Загрузить карты»</small>}
        </div>
      ))}
    </div>
  );
}

function friendlyLoadError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/Unexpected token|JSON|API returned|fetch|network/i.test(message)) {
    return "Не удалось загрузить сохранённые связи. Проверьте, что API запущен, и обновите страницу.";
  }
  return message || "Не удалось загрузить взаимодействия";
}

export default function InteractionsPage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartProfileRelationship[]>([]);
  const [status, setStatus] = useState("Загружаю сохранённые карты и связи...");
  const [baseProfileId, setBaseProfileId] = useState("");
  const [relatedProfileId, setRelatedProfileId] = useState("");
  const [roleKey, setRoleKey] = useState("partner");
  const [requestedUsername, setRequestedUsername] = useState("");
  const [saving, setSaving] = useState(false);
  const [incomingRequests, setIncomingRequests] = useState<ChartProfileRelationship[]>([]);
  const [acceptedProfileIds, setAcceptedProfileIds] = useState<Record<number, string>>({});
  const [previewCalculations, setPreviewCalculations] = useState<Record<number, ChartCalculationRecord>>({});
  const [previewChartStatus, setPreviewChartStatus] = useState("Карты загрузятся после сохранения связи.");
  const [loadingPreviewCharts, setLoadingPreviewCharts] = useState(false);

  useEffect(() => {
    let mounted = true;
    Promise.all([listChartProfiles(), listChartProfileRelationships(), listIncomingChartProfileRelationshipRequests()])
      .then(([profileResult, relationshipResult, incomingResult]) => {
        if (!mounted) return;
        setProfiles(profileResult);
        setRelationships(relationshipResult);
        setIncomingRequests(incomingResult);
        const first = profileResult[0]?.id ? String(profileResult[0].id) : "";
        const second = profileResult.find((profile) => String(profile.id) !== first)?.id;
        setBaseProfileId((current) => current || first);
        setRelatedProfileId((current) => current || (second ? String(second) : ""));
        setAcceptedProfileIds((current) => {
          const fallback = first;
          return Object.fromEntries(
            incomingResult.map((request) => [
              request.id,
              current[request.id] && profileResult.some((profile) => String(profile.id) === current[request.id])
                ? current[request.id]
                : fallback,
            ]),
          );
        });
        setStatus(
          relationshipResult.length || incomingResult.length
            ? `${relationshipResult.length} связей, ${incomingResult.length} входящих запросов`
            : "Связей пока нет: задайте роль человеку в сохранённых картах.",
        );
      })
      .catch((error) => {
        if (!mounted) return;
        setStatus(friendlyLoadError(error));
      });
    return () => {
      mounted = false;
    };
  }, []);

  const profileById = useMemo(() => new Map(profiles.map((profile) => [profile.id, profile])), [profiles]);
  const visibleRelationships = relationships.filter((relationship) => !["declined", "blocked"].includes(relationship.link_status));
  const canCreateRelationship = Boolean(baseProfileId && relatedProfileId && baseProfileId !== relatedProfileId && !saving);
  const selectedRole = roleFor(roleKey);
  const selectedBaseProfile = baseProfileId ? profileById.get(Number(baseProfileId)) : undefined;
  const selectedRelatedProfile = relatedProfileId ? profileById.get(Number(relatedProfileId)) : undefined;
  const selectedExistingRelationship = visibleRelationships.find(
    (relationship) =>
      String(relationship.profile_id) === baseProfileId &&
      String(relationship.related_profile_id) === relatedProfileId,
  );
  const selectedBaseChart = selectedExistingRelationship ? previewCalculations[selectedExistingRelationship.profile_id]?.result ?? null : null;
  const selectedRelatedChart = selectedExistingRelationship ? previewCalculations[selectedExistingRelationship.related_profile_id]?.result ?? null : null;

  async function refreshRelationships() {
    const [relationshipResult, incomingResult] = await Promise.all([
      listChartProfileRelationships(),
      listIncomingChartProfileRelationshipRequests(),
    ]);
    setRelationships(relationshipResult);
    setIncomingRequests(incomingResult);
    setStatus(
      relationshipResult.length || incomingResult.length
        ? `${relationshipResult.length} связей, ${incomingResult.length} входящих запросов`
        : "Связей пока нет: задайте роль человеку в сохранённых картах.",
    );
  }

  async function handleCreateRelationship() {
    if (!canCreateRelationship) return;
    setSaving(true);
    setStatus("Сохраняю связь...");
    try {
      await upsertChartProfileRelationship({
        profile_id: Number(baseProfileId),
        related_profile_id: Number(relatedProfileId),
        role: roleKey,
        ...(requestedUsername.trim() ? { requested_username: requestedUsername.trim() } : {}),
      });
      setRequestedUsername("");
      await refreshRelationships();
      setStatus(requestedUsername.trim() ? "Запрос на связь отправлен." : "Личная связь сохранена.");
    } catch (error) {
      setStatus(friendlyLoadError(error));
    } finally {
      setSaving(false);
    }
  }

  async function handleIncomingAction(relationshipId: number, action: "accept" | "decline" | "block") {
    const acceptedProfileId = Number(acceptedProfileIds[relationshipId]);
    if (action === "accept" && !acceptedProfileId) {
      setStatus("Выберите свою карту для подтверждения связи.");
      return;
    }
    setSaving(true);
    setStatus(action === "accept" ? "Подтверждаю связь..." : "Обновляю запрос...");
    try {
      await updateChartProfileRelationshipRequest(relationshipId, action, action === "accept" ? acceptedProfileId : undefined);
      await refreshRelationships();
      setStatus(action === "accept" ? "Связь подтверждена." : action === "decline" ? "Запрос отклонён." : "Пользователь заблокирован.");
    } catch (error) {
      setStatus(friendlyLoadError(error));
    } finally {
      setSaving(false);
    }
  }

  async function handleLoadPreviewCharts() {
    if (!selectedExistingRelationship || loadingPreviewCharts) return;
    setLoadingPreviewCharts(true);
    setPreviewChartStatus("Загружаю расчёты двух карт...");
    try {
      const [base, related] = await Promise.all([
        previewCalculations[selectedExistingRelationship.profile_id]
          ? Promise.resolve(previewCalculations[selectedExistingRelationship.profile_id])
          : calculateSavedProfile(selectedExistingRelationship.profile_id),
        previewCalculations[selectedExistingRelationship.related_profile_id]
          ? Promise.resolve(previewCalculations[selectedExistingRelationship.related_profile_id])
          : calculateSavedProfile(selectedExistingRelationship.related_profile_id),
      ]);
      setPreviewCalculations((current) => ({
        ...current,
        [selectedExistingRelationship.profile_id]: base,
        [selectedExistingRelationship.related_profile_id]: related,
      }));
      setPreviewChartStatus("Карты загружены: можно смотреть D1 и D-карты по выбранной роли.");
    } catch (error) {
      setPreviewChartStatus(friendlyLoadError(error));
    } finally {
      setLoadingPreviewCharts(false);
    }
  }

  return (
    <ProductShell active="interactions">
      <header className="product-page-head">
        <div>
          <h1>Взаимодействия</h1>
          <p>Роли людей, ракурсы чтения, дома, D-карты и статус связи.</p>
        </div>
        <a className="primary-link-button" href="/#chart">Настроить роли</a>
      </header>

      <div className="product-status">{status}</div>

      <section className="beginner-context-panel" aria-label="Как новичку создавать взаимодействия">
        <div>
          <strong>1. Выберите две карты</strong>
          <span>Базовая карта — от чьего лица читается связь; вторая карта — человек, с которым смотрится взаимодействие.</span>
        </div>
        <div>
          <strong>2. Укажите роль</strong>
          <span>Роль меняет фокус: для отца важны 9 дом и D12, для руководителя — 10 дом и D10, для оппонента — 6/8 дома.</span>
        </div>
        <div>
          <strong>3. Username нужен только для согласия</strong>
          <span>Без username это личная пометка. С username уйдёт запрос, и после принятия связь будет видна обоим пользователям.</span>
        </div>
      </section>

      {incomingRequests.length ? (
        <section className="profile-relationship-inbox" aria-label="Входящие запросы на связь">
          <strong>Входящие запросы на подтверждение связи</strong>
          {incomingRequests.map((request) => {
            const role = roleFor(request.role);
            return (
              <div className="profile-relationship-request" key={request.id}>
                <div>
                  <span>{request.user?.username ?? "Пользователь"} просит подтвердить связь</span>
                  <strong>{profileLabel(request.profile)} → {profileLabel(request.related_profile)}</strong>
                  <small>{role.label} · {request.profile?.birth_date ?? ""}</small>
                </div>
                <label>
                  Моя карта
                  <select
                    value={acceptedProfileIds[request.id] ?? ""}
                    onChange={(event) =>
                      setAcceptedProfileIds((current) => ({
                        ...current,
                        [request.id]: event.target.value,
                      }))
                    }
                  >
                    <option value="">Выберите</option>
                    {profiles.map((profile) => (
                      <option value={String(profile.id)} key={`incoming-${request.id}-${profile.id}`}>
                        {profile.display_name}
                      </option>
                    ))}
                  </select>
                </label>
                <button type="button" className="secondary-button" disabled={saving} onClick={() => handleIncomingAction(request.id, "accept")}>
                  Принять
                </button>
                <button type="button" className="secondary-button" disabled={saving} onClick={() => handleIncomingAction(request.id, "decline")}>
                  Отклонить
                </button>
                <button type="button" className="secondary-button" disabled={saving} onClick={() => handleIncomingAction(request.id, "block")}>
                  Блок
                </button>
              </div>
            );
          })}
        </section>
      ) : null}

      <ConsentPolicyPanel />

      <section className="interaction-create-panel" aria-label="Создать взаимодействие">
        <div>
          <h2>Создать взаимодействие</h2>
          <p>Выберите две сохранённые карты и роль. Если второй человек зарегистрирован, укажите его username: тогда связь станет запросом на подтверждение.</p>
        </div>
        <label>
          Базовая карта
          <select value={baseProfileId} onChange={(event) => setBaseProfileId(event.target.value)}>
            <option value="">Выберите карту</option>
            {profiles.map((profile) => (
              <option value={String(profile.id)} key={`base-${profile.id}`}>
                {profile.display_name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Второй человек
          <select value={relatedProfileId} onChange={(event) => setRelatedProfileId(event.target.value)}>
            <option value="">Выберите карту</option>
            {profiles
              .filter((profile) => String(profile.id) !== baseProfileId)
              .map((profile) => (
                <option value={String(profile.id)} key={`related-${profile.id}`}>
                  {profile.display_name}
                </option>
              ))}
          </select>
        </label>
        <label>
          Роль
          <select value={roleKey} onChange={(event) => setRoleKey(event.target.value)}>
            {interactionRoles.map((role) => (
              <option value={role.key} key={`role-${role.key}`}>
                {role.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Username для подтверждения
          <input
            value={requestedUsername}
            onChange={(event) => setRequestedUsername(event.target.value)}
            placeholder="необязательно"
          />
        </label>
        <LinkModePreview username={requestedUsername} />
        <button type="button" className="primary-link-button" disabled={!canCreateRelationship} onClick={handleCreateRelationship}>
          {saving ? "Сохраняю..." : requestedUsername.trim() ? "Отправить запрос" : "Сохранить связь"}
        </button>
      </section>

      <section className="interaction-reading-plan" aria-label="Как будет читаться выбранная роль">
        <div>
          <span>Выбранный ракурс</span>
          <strong>{selectedRole.label}</strong>
          <p>{selectedRole.focus}</p>
        </div>
        <div>
          <span>Что AI обязан проверить</span>
          <strong>
            Дома <HouseTerms houses={selectedRole.houses} /> · D-карты <VargaTerms vargas={selectedRole.vargas} />
          </strong>
          <p>Эти факторы попадут в пакет разбора вместе с двумя картами и ролью второго человека.</p>
        </div>
        <div>
          <span>Приватность</span>
          <strong>{requestedUsername.trim() ? "Запрос на подтверждение" : "Личная связь"}</strong>
          <p>
            {requestedUsername.trim()
              ? "Если пользователь подтвердит запрос, связь станет общей для двух аккаунтов."
              : "Без username это только ваша сохранённая пометка; второй человек ничего не видит."}
          </p>
        </div>
      </section>

      <section className="interaction-pair-preview" aria-label="Предпросмотр парного разбора">
        <div className="interaction-pair-preview-head">
          <div>
            <span>Предпросмотр разбора</span>
            <strong>{selectedRole.label}: две карты в одном контексте</strong>
          </div>
          {selectedExistingRelationship ? (
            <div className="interaction-actions">
              <button type="button" className="secondary-button" disabled={loadingPreviewCharts} onClick={handleLoadPreviewCharts}>
                {loadingPreviewCharts ? "Загружаю..." : "Загрузить карты"}
              </button>
              <a className="secondary-button" href={`/compatibility/pair/${selectedExistingRelationship.id}`}>
                Паспорт пары
              </a>
              <a className="primary-link-button" href={`/?analysis=compatibility&relationship=${selectedExistingRelationship.id}#reports`}>
                Открыть разбор
              </a>
            </div>
          ) : (
            <em>Сначала сохраните связь</em>
          )}
        </div>
        {selectedExistingRelationship ? <div className="product-status">{previewChartStatus}</div> : null}
        <div className="interaction-pair-preview-grid">
          <div>
            <span>Карта A</span>
            <strong>{selectedBaseProfile?.display_name ?? "Выберите базовую карту"}</strong>
            <small>{selectedBaseProfile ? profileMeta(null, selectedBaseProfile) : "от неё читается роль второго человека"}</small>
          </div>
          <div>
            <span>Карта B</span>
            <strong>{selectedRelatedProfile?.display_name ?? "Выберите второго человека"}</strong>
            <small>{selectedRelatedProfile ? profileMeta(null, selectedRelatedProfile) : "эта карта сравнивается с базовой"}</small>
          </div>
          <div>
            <span>Дома</span>
            <strong><HouseTerms houses={selectedRole.houses} /></strong>
            <small>эти дома будут видны в пакете AI и истории разбора</small>
          </div>
          <div>
            <span>D-карты</span>
            <strong><VargaTerms vargas={selectedRole.vargas} /></strong>
            <small>{roleReadingNote(selectedRole)}</small>
          </div>
        </div>
        {selectedExistingRelationship ? (
          <div className="compatibility-context-grid interaction-preview-chart-grid" aria-label="Карты выбранного взаимодействия">
            <article className="compatibility-person-card">
              <div>
                <span>Карта A</span>
                <strong>{selectedBaseProfile?.display_name ?? profileLabel(selectedExistingRelationship.profile)}</strong>
                <small>{selectedBaseProfile ? profileMeta(null, selectedBaseProfile) : profileMeta(selectedExistingRelationship.profile)}</small>
              </div>
              <dl className="compatibility-person-facts">
                <div>
                  <dt>Лагна</dt>
                  <dd>{placementLine(selectedBaseChart?.ascendant)}</dd>
                </div>
                <div>
                  <dt>Луна</dt>
                  <dd>{placementLine(moon(selectedBaseChart))}</dd>
                </div>
                {selectedRole.houses.slice(0, 4).map((house) => (
                  <div key={`interaction-base-house-${house}`}>
                    <dt><HouseTerms houses={[house]} /></dt>
                    <dd>{houseLine(selectedBaseChart, house)}</dd>
                  </div>
                ))}
              </dl>
              <InteractionChartBoard chart={selectedBaseChart} role={selectedRole} />
            </article>
            <article className="compatibility-person-card">
              <div>
                <span>Карта B</span>
                <strong>{selectedRelatedProfile?.display_name ?? profileLabel(selectedExistingRelationship.related_profile)}</strong>
                <small>{selectedRelatedProfile ? profileMeta(null, selectedRelatedProfile) : profileMeta(selectedExistingRelationship.related_profile)}</small>
              </div>
              <dl className="compatibility-person-facts">
                <div>
                  <dt>Лагна</dt>
                  <dd>{placementLine(selectedRelatedChart?.ascendant)}</dd>
                </div>
                <div>
                  <dt>Луна</dt>
                  <dd>{placementLine(moon(selectedRelatedChart))}</dd>
                </div>
                {selectedRole.houses.slice(0, 4).map((house) => (
                  <div key={`interaction-related-house-${house}`}>
                    <dt><HouseTerms houses={[house]} /></dt>
                    <dd>{houseLine(selectedRelatedChart, house)}</dd>
                  </div>
                ))}
              </dl>
              <InteractionChartBoard chart={selectedRelatedChart} role={selectedRole} />
            </article>
          </div>
        ) : null}
      </section>

      <section className="interaction-guide-grid" aria-label="Ракурсы чтения взаимодействий">
        {interactionRoles.map((role) => (
          <article className="interaction-guide-card" key={role.key}>
            <div>
              <span>{role.label}</span>
              <strong>{role.focus}</strong>
            </div>
            <p>
              Дома: <HouseTerms houses={role.houses} /> · Карты: <VargaTerms vargas={role.vargas} />
            </p>
          </article>
        ))}
      </section>

      {visibleRelationships.length ? (
        <section className="interaction-list" aria-label="Сохранённые взаимодействия">
          {visibleRelationships.map((relationship) => {
            const role = roleFor(relationship.role);
            const baseProfile = profileById.get(relationship.profile_id);
            const relatedProfile = profileById.get(relationship.related_profile_id);
            return (
              <article className="interaction-card" key={relationship.id}>
                <div className="interaction-card-head">
                  <div>
                    <span>{role.label}</span>
                    <strong>
                      {profileLabel(relationship.profile, baseProfile)} → {profileLabel(relationship.related_profile, relatedProfile)}
                    </strong>
                    <small>
                      {profileMeta(relationship.profile, baseProfile)} / {profileMeta(relationship.related_profile, relatedProfile)}
                    </small>
                  </div>
                  <StatusTerm status={relationship.link_status} />
                </div>
                <div className="interaction-focus-grid">
                  <div>
                    <span>Ракурс</span>
                    <strong>{role.focus}</strong>
                  </div>
                  <div>
                    <span>Дома</span>
                    <strong>
                      <HouseTerms houses={role.houses} />
                    </strong>
                  </div>
                  <div>
                    <span>D-карты</span>
                    <strong>
                      <VargaTerms vargas={role.vargas} />
                    </strong>
                  </div>
                </div>
                <p>
                  Для AI-разбора эта связь должна передавать обе карты, роль второго человека и нужные дома/D-карты.
                  Подтверждённая связь означает, что оба зарегистрированных пользователя видят связь осознанно.
                </p>
                <div className="interaction-actions">
                  <a className="secondary-button" href={`/compatibility/pair/${relationship.id}`}>
                    Паспорт пары
                  </a>
                  <a className="primary-link-button" href={`/?analysis=compatibility&relationship=${relationship.id}#reports`}>
                    Открыть разбор
                  </a>
                  <a className="secondary-button" href="/compatibility">
                    История совместимости
                  </a>
                </div>
              </article>
            );
          })}
        </section>
      ) : (
        <section className="history-empty">
          <strong>Нет сохранённых взаимодействий</strong>
          <span>Откройте сохранённые карты на главной странице, выберите базовую карту и укажите роль для другого человека.</span>
          <a className="primary-link-button" href="/#chart">Перейти к картам</a>
        </section>
      )}
    </ProductShell>
  );
}
