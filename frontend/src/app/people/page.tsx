"use client";

import { useEffect, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { relationshipRoleFor } from "@/lib/relationshipRoles";
import {
  fetchCurrentUser,
  listChartProfileRelationships,
  listChartProfiles,
  listIncomingChartProfileRelationshipRequests,
  type ChartProfile,
  type ChartProfileRelationship,
} from "@/lib/api";

function friendlyPeopleError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/401|403|auth|credential|forbidden|permission/i.test(message)) {
    return "Войдите, чтобы открыть сохранённые карты.";
  }
  if (/Unexpected token|JSON|API returned|fetch|network|Backend API/i.test(message)) {
    return "Не удалось загрузить карты людей. Обновите страницу.";
  }
  return message || "Ошибка загрузки сохранённых карт";
}

function formatProfileTime(profile: ChartProfile) {
  return profile.birth_time ? profile.birth_time.slice(0, 5) : "время неизвестно";
}

function formatRelationshipStatus(status: string) {
  if (status === "accepted") return "связь подтверждена";
  if (status === "requested") return "запрос отправлен";
  if (status === "declined") return "запрос отклонён";
  if (status === "blocked") return "связь заблокирована";
  return "сохранённая связь";
}

function formatCalculationStatus(status: string | null | undefined) {
  if (status === "complete" || status === "success" || status === "ready") return "рассчитано";
  if (status === "queued") return "в очереди";
  if (status === "running" || status === "processing") return "считается";
  if (status === "failed" || status === "error") return "ошибка расчёта";
  return "расчёт сохранён";
}

function formatBirthTimeAccuracy(value: string | null | undefined) {
  if (value === "exact") return "точное время";
  if (value === "approximate") return "примерное время";
  if (value === "unknown") return "время неизвестно";
  return "точность не указана";
}

export default function PeoplePage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartProfileRelationship[]>([]);
  const [incoming, setIncoming] = useState<ChartProfileRelationship[]>([]);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [authChecked, setAuthChecked] = useState(false);
  const [needsAuth, setNeedsAuth] = useState(false);

  useEffect(() => {
    let mounted = true;
    const reloadOnAuthChanged = () => window.location.reload();
    window.addEventListener("jyotish-auth-changed", reloadOnAuthChanged);

    async function loadPeople() {
      try {
        const user = await fetchCurrentUser();
        if (!mounted) return;
        setAuthChecked(true);
        if (!user) {
          setNeedsAuth(true);
          setStatus("Войдите, чтобы открыть сохранённые карты.");
          return;
        }
        const [profileRows, relationshipRows, incomingRows] = await Promise.all([
          listChartProfiles(),
          listChartProfileRelationships(),
          listIncomingChartProfileRelationshipRequests(),
        ]);
        if (!mounted) return;
        setProfiles(profileRows);
        setRelationships(relationshipRows);
        setIncoming(incomingRows);
        setStatus(`${profileRows.length} карт, ${relationshipRows.length} связей, ${incomingRows.length} входящих запросов`);
      } catch (error) {
        if (!mounted) return;
        setAuthChecked(true);
        setStatus(friendlyPeopleError(error));
      }
    }

    void loadPeople();
    return () => {
      mounted = false;
      window.removeEventListener("jyotish-auth-changed", reloadOnAuthChanged);
    };
  }, []);

  const showStatus = !needsAuth && /ошиб|не удалось/i.test(status);

  return (
    <ProductShell active="people">
      {authChecked && !needsAuth ? (
        <div className="page-action-strip">
          <a className="primary-link-button" href="/">Добавить карту</a>
        </div>
      ) : null}

      {showStatus ? <div className="product-status">{status}</div> : null}

      {needsAuth ? (
        <section className="history-empty private-history-gate">
          <span>Войдите для доступа.</span>
        </section>
      ) : null}

      {!needsAuth ? (
        <>
          <section className="compatibility-saved-role-context" aria-label="Сохранённые карты">
            <div className="compatibility-saved-role-head">
              <div>
                <span>Сохранённые карты</span>
              </div>
            </div>
            {profiles.length ? (
              <div className="history-list">
                {profiles.map((profile) => (
                  <a className="history-row" href={`/?profile=${profile.id}#chart`} key={profile.id}>
                    <div>
                      <strong>{profile.display_name}{profile.is_self_profile ? " · моя карта" : ""}</strong>
                      <span>{profile.birth_date} · {formatProfileTime(profile)} · {profile.place.label}</span>
                      <small className="history-row-meta">
                        {profile.latest_calculation
                          ? `${formatCalculationStatus(profile.latest_calculation.status)} · ${profile.latest_calculation.graha_count} грах`
                          : "расчёт ещё не сохранён"}
                        {" · "}
                        {formatBirthTimeAccuracy(profile.birth_time_accuracy)}
                      </small>
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <div className="history-empty">Сохранённых карт ещё нет.</div>
            )}
          </section>

          <section className="compatibility-saved-role-context" aria-label="Связи людей">
            <div className="compatibility-saved-role-head">
              <div>
                <span>Роли и связи</span>
              </div>
            </div>
            {relationships.length ? (
              <div className="compatibility-saved-role-grid">
                {relationships.map((relationship) => {
                  const role = relationshipRoleFor(relationship.role);
                  return (
                    <div key={relationship.id}>
                      <span>{role.label} · {formatRelationshipStatus(relationship.link_status)}</span>
                      <strong>{relationship.profile?.display_name ?? "Карта"} → {relationship.related_profile?.display_name ?? "Связанная карта"}</strong>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="history-empty">Связей между картами ещё нет.</div>
            )}
          </section>

          {incoming.length ? (
          <section className="compatibility-saved-role-context" aria-label="Входящие запросы связей">
            <div className="compatibility-saved-role-head">
              <div>
                <span>Входящие запросы</span>
              </div>
            </div>
            <div className="compatibility-saved-role-grid">
                {incoming.map((request) => {
                  const role = relationshipRoleFor(request.role);
                  return (
                    <div key={request.id}>
                      <span>{role.label} · {formatRelationshipStatus(request.link_status)}</span>
                      <strong>{request.profile?.display_name ?? "Карта"} → {request.related_profile?.display_name ?? "ваша карта"}</strong>
                    </div>
                  );
                })}
            </div>
          </section>
          ) : null}
        </>
      ) : null}
    </ProductShell>
  );
}
