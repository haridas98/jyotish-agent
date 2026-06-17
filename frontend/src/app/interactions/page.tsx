"use client";

import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import {
  calculateSavedProfile,
  fetchCurrentUser,
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

function StatusTerm({ status }: { status: string }) {
  return <em className={`interaction-status ${status}`}>{statusLabel(status)}</em>;
}

function houseList(houses: Array<number | string>): string {
  return houses.map((house) => `${house}`).join(", ");
}

function vargaList(vargas: string[]): string {
  return vargas.join(", ");
}

function profileLabel(profile: ChartProfileRelationship["profile"], fallback?: ChartProfile): string {
  return profile?.display_name ?? fallback?.display_name ?? "Карта";
}

function profileMeta(profile: ChartProfileRelationship["profile"], fallback?: ChartProfile): string {
  const date = profile?.birth_date ?? fallback?.birth_date ?? "дата не указана";
  const place = profile?.place_label ?? fallback?.place.label ?? "место не указано";
  return `${date} · ${place}`;
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
            <strong>{code}</strong>
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
    return "Не удалось загрузить сохранённые связи. Обновите страницу.";
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
  const [createOpen, setCreateOpen] = useState(false);
  const [incomingRequests, setIncomingRequests] = useState<ChartProfileRelationship[]>([]);
  const [acceptedProfileIds, setAcceptedProfileIds] = useState<Record<number, string>>({});
  const [previewCalculations, setPreviewCalculations] = useState<Record<number, ChartCalculationRecord>>({});
  const [previewChartStatus, setPreviewChartStatus] = useState("Карты загрузятся после сохранения связи.");
  const [loadingPreviewCharts, setLoadingPreviewCharts] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [needsAuth, setNeedsAuth] = useState(false);

  useEffect(() => {
    let mounted = true;
    const reloadOnAuthChanged = () => window.location.reload();
    window.addEventListener("jyotish-auth-changed", reloadOnAuthChanged);

    fetchCurrentUser()
      .then((user) => {
        if (!mounted) return null;
        setAuthChecked(true);
        setNeedsAuth(!user);
        if (!user) {
          setStatus("");
          return null;
        }
        return Promise.all([listChartProfiles(), listChartProfileRelationships(), listIncomingChartProfileRelationshipRequests()]);
      })
      .then((result) => {
        if (!result) return;
        const [profileResult, relationshipResult, incomingResult] = result;
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
        setAuthChecked(true);
        setStatus(friendlyLoadError(error));
      });
    return () => {
      mounted = false;
      window.removeEventListener("jyotish-auth-changed", reloadOnAuthChanged);
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
  const showStatus = !needsAuth && /ошиб|не удалось|войдите|сервис|выберите/i.test(status);
  const showPreviewStatus = /ошиб|не удалось|сервис/i.test(previewChartStatus);

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
      {showStatus ? <div className="product-status">{status}</div> : null}

      {authChecked && needsAuth ? (
        <section className="history-empty private-history-gate">
          <span>Войдите для доступа.</span>
        </section>
      ) : null}

      {!needsAuth && incomingRequests.length ? (
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
                  Заблокировать
                </button>
              </div>
            );
          })}
        </section>
      ) : null}

      {!needsAuth ? (
      <section id="new-interaction" className={`interaction-create-panel${createOpen ? " open" : ""}`} aria-label="Создать взаимодействие">
        <div>
          <h2>Новая связь</h2>
          <button type="button" className="secondary-button" onClick={() => setCreateOpen((value) => !value)}>
            {createOpen ? "Скрыть" : "Выбрать карты"}
          </button>
        </div>
        {createOpen ? (
          <>
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
              Логин для подтверждения
              <input
                value={requestedUsername}
                onChange={(event) => setRequestedUsername(event.target.value)}
                placeholder="необязательно"
              />
            </label>
            <button type="button" className="primary-link-button" disabled={!canCreateRelationship} onClick={handleCreateRelationship}>
              {saving ? "Сохраняю..." : requestedUsername.trim() ? "Отправить запрос" : "Сохранить связь"}
            </button>
          </>
        ) : null}
      </section>
      ) : null}

      {!needsAuth && selectedExistingRelationship ? (
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
                Открыть пару
              </a>
              <a className="primary-link-button" href={`/?analysis=compatibility&relationship=${selectedExistingRelationship.id}#reports`}>
                Открыть разбор
              </a>
            </div>
          ) : (
            <em>Сначала сохраните связь</em>
          )}
        </div>
        {selectedExistingRelationship && showPreviewStatus ? <div className="product-status">{previewChartStatus}</div> : null}
        <div className="interaction-pair-preview-grid">
          {selectedExistingRelationship ? (
          <div>
            <span>Ракурс</span>
            <strong>{selectedRole.label}</strong>
          </div>
          ) : (
            <>
              <div>
                <span>Карта A</span>
                <strong>{selectedBaseProfile?.display_name ?? "Выберите базовую карту"}</strong>
                <small>{selectedBaseProfile ? profileMeta(null, selectedBaseProfile) : ""}</small>
              </div>
              <div>
                <span>Карта B</span>
                <strong>{selectedRelatedProfile?.display_name ?? "Выберите второго человека"}</strong>
                <small>{selectedRelatedProfile ? profileMeta(null, selectedRelatedProfile) : ""}</small>
              </div>
            </>
          )}
          <div>
            <span>Дома</span>
            <strong>{houseList(selectedRole.houses)}</strong>
          </div>
          <div>
            <span>D-карты</span>
            <strong>{vargaList(selectedRole.vargas)}</strong>
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
                    <dt>{house} дом</dt>
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
                    <dt>{house} дом</dt>
                    <dd>{houseLine(selectedRelatedChart, house)}</dd>
                  </div>
                ))}
              </dl>
              <InteractionChartBoard chart={selectedRelatedChart} role={selectedRole} />
            </article>
          </div>
        ) : null}
      </section>
      ) : null}

      {!needsAuth && visibleRelationships.length ? (
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
                <div className="interaction-actions">
                  <a className="secondary-button" href={`/compatibility/pair/${relationship.id}`}>
                    Открыть пару
                  </a>
                  <a className="primary-link-button" href={`/?analysis=compatibility&relationship=${relationship.id}#reports`}>
                    Открыть разбор
                  </a>
                </div>
              </article>
            );
          })}
        </section>
      ) : !needsAuth ? (
        <section className="history-empty">
          <strong>Нет сохранённых взаимодействий</strong>
          <a className="primary-link-button" href="/people">К картам</a>
        </section>
      ) : null}
    </ProductShell>
  );
}
