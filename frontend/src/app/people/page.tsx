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
    return "Войдите в аккаунт, чтобы увидеть свои сохранённые карты и связи.";
  }
  if (/Unexpected token|JSON|API returned|fetch|network|Backend API/i.test(message)) {
    return "Не удалось загрузить карты людей. Проверьте, что API запущен, и обновите страницу.";
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
  return "личная сохранённая связь";
}

export default function PeoplePage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartProfileRelationship[]>([]);
  const [incoming, setIncoming] = useState<ChartProfileRelationship[]>([]);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [needsAuth, setNeedsAuth] = useState(false);

  useEffect(() => {
    let mounted = true;
    const reloadOnAuthChanged = () => window.location.reload();
    window.addEventListener("jyotish-auth-changed", reloadOnAuthChanged);

    async function loadPeople() {
      try {
        const user = await fetchCurrentUser();
        if (!mounted) return;
        if (!user) {
          setNeedsAuth(true);
          setStatus("Войдите в аккаунт, чтобы увидеть свои сохранённые карты и связи.");
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
        setStatus(friendlyPeopleError(error));
      }
    }

    void loadPeople();
    return () => {
      mounted = false;
      window.removeEventListener("jyotish-auth-changed", reloadOnAuthChanged);
    };
  }, []);

  return (
    <ProductShell active="people">
      <header className="product-page-head">
        <div>
          <h1>Люди</h1>
          <p>Сохранённые карты, роли родственников и связи с другими пользователями.</p>
        </div>
        <a className="primary-link-button" href="/">Добавить карту</a>
      </header>

      <div className="product-status">{status}</div>

      {needsAuth ? (
        <section className="history-empty private-history-gate">
          <strong>Личное пространство</strong>
          <span>Карты людей, роли и запросы связей доступны только владельцу аккаунта.</span>
        </section>
      ) : null}

      {!needsAuth ? (
        <>
          <section className="compatibility-saved-role-context" aria-label="Сохранённые карты">
            <div className="compatibility-saved-role-head">
              <div>
                <span>Сохранённые карты</span>
                <strong>Кого можно подключать к личным обзорам и взаимодействиям</strong>
              </div>
              <small>Основная карта отмечается отдельно; чужие карты можно хранить бесплатно, AI-разбор запускается отдельным действием.</small>
            </div>
            {profiles.length ? (
              <div className="history-list">
                {profiles.map((profile) => (
                  <a className="history-row" href={`/?profile=${profile.id}#chart`} key={profile.id}>
                    <div>
                      <strong>{profile.display_name}{profile.is_self_profile ? " · моя карта" : ""}</strong>
                      <span>{profile.birth_date} · {formatProfileTime(profile)} · {profile.place.label}</span>
                      <p>{profile.latest_calculation ? `последний расчёт: ${profile.latest_calculation.status}, ${profile.latest_calculation.graha_count} грах` : "расчёт ещё не сохранён"}</p>
                    </div>
                    <aside>
                      <span>{profile.timezone}</span>
                      <small>{profile.birth_time_accuracy}</small>
                    </aside>
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
                <strong>Отец, мать, партнёр, брат, начальник и другие ракурсы чтения</strong>
              </div>
              <small>Роль определяет дома, D-карты и контекст, с которым AI должен читать взаимодействие.</small>
            </div>
            {relationships.length ? (
              <div className="compatibility-saved-role-grid">
                {relationships.map((relationship) => {
                  const role = relationshipRoleFor(relationship.role);
                  return (
                    <div key={relationship.id}>
                      <span>{role.label} · {formatRelationshipStatus(relationship.link_status)}</span>
                      <strong>{relationship.profile?.display_name ?? "Карта"} → {relationship.related_profile?.display_name ?? "Связанная карта"}</strong>
                      <small>{role.focus}; дома {role.houses.join(", ")}; {role.vargas.join(", ")}</small>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="history-empty">Связей между картами ещё нет.</div>
            )}
          </section>

          <section className="compatibility-saved-role-context" aria-label="Входящие запросы связей">
            <div className="compatibility-saved-role-head">
              <div>
                <span>Входящие запросы</span>
                <strong>Привязка к зарегистрированным пользователям должна подтверждаться</strong>
              </div>
              <small>Если другой пользователь хочет связать карту с вами, запрос должен быть принят или отклонён.</small>
            </div>
            {incoming.length ? (
              <div className="compatibility-saved-role-grid">
                {incoming.map((request) => {
                  const role = relationshipRoleFor(request.role);
                  return (
                    <div key={request.id}>
                      <span>{role.label} · {formatRelationshipStatus(request.link_status)}</span>
                      <strong>{request.profile?.display_name ?? "Карта"} → {request.related_profile?.display_name ?? "ваша карта"}</strong>
                      <small>Запрос от {request.user?.username ?? "пользователя"}</small>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="history-empty">Входящих запросов нет.</div>
            )}
          </section>
        </>
      ) : null}
    </ProductShell>
  );
}
