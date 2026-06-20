"use client";

import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import {
  fetchCurrentUser,
  listChartProfiles,
  listChartRelationships,
  type ChartProfile,
  type ChartRelationship,
} from "@/lib/api";
import { getRelationshipType, type RelationshipTypeId } from "@/astrology";

const roleLabels: Record<string, string> = {
  father: "отец",
  mother: "мать",
  child: "ребёнок",
  sibling: "родственник",
  spouse: "супруг",
  romantic_partner: "партнёр",
  business_partner: "партнёр",
  boss: "руководитель",
  subordinate: "подчинённый",
  colleague: "коллега",
  guru: "наставник",
  student: "ученик",
  friend: "друг",
  opponent: "оппонент",
  client: "клиент",
  supplier: "поставщик",
};

function formatProfileTime(profile: ChartProfile) {
  return profile.birth_time ? profile.birth_time.slice(0, 5) : "время неизвестно";
}

function formatCalculationStatus(status: string | null | undefined) {
  if (status === "complete" || status === "success" || status === "ready") return "рассчитано";
  if (status === "queued") return "в очереди";
  if (status === "running" || status === "processing") return "считается";
  if (status === "failed" || status === "error") return "ошибка расчёта";
  return "расчёт не сохранён";
}

function relationshipTypeLabel(relationship: ChartRelationship) {
  return getRelationshipType(relationship.relationship_type_id as RelationshipTypeId)?.label.ru ?? relationship.relationship_type_id;
}

function relationshipDate(value: string) {
  return new Date(value).toLocaleDateString("ru-RU");
}

function relationshipLabelShort(relationship: ChartRelationship) {
  return `${relationship.chart_a?.display_name ?? "A"} — ${relationship.chart_b?.display_name ?? "B"}`;
}

function latestPeopleObject(profiles: ChartProfile[], relationships: ChartRelationship[]) {
  const profile = [...profiles].sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at))[0] ?? null;
  const relationship = [...relationships].sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at))[0] ?? null;
  if (!relationship) return profile ? `Карта: ${profile.display_name}` : "нет данных";
  if (!profile) return `Связь: ${relationshipLabelShort(relationship)}`;
  return Date.parse(relationship.updated_at) > Date.parse(profile.updated_at)
    ? `Связь: ${relationshipLabelShort(relationship)}`
    : `Карта: ${profile.display_name}`;
}

export default function PeoplePage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartRelationship[]>([]);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [needsAuth, setNeedsAuth] = useState(false);

  const selfProfile = useMemo(() => profiles.find((profile) => profile.is_self_profile) ?? null, [profiles]);

  useEffect(() => {
    let mounted = true;

    async function loadPeople() {
      try {
        const user = await fetchCurrentUser();
        if (!mounted) return;
        if (!user) {
          setNeedsAuth(true);
          setStatus("Войдите, чтобы открыть сохранённые карты.");
          return;
        }
        const [profileRows, relationshipRows] = await Promise.all([listChartProfiles(), listChartRelationships()]);
        if (!mounted) return;
        setProfiles(profileRows);
        setRelationships(relationshipRows);
        setStatus(`${profileRows.length} карт, ${relationshipRows.length} связей`);
      } catch (error) {
        if (!mounted) return;
        setStatus(error instanceof Error ? error.message : "Ошибка загрузки сохранённых карт");
      }
    }

    void loadPeople();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <ProductShell active="people">
      <section className="charts-dashboard-head people-workspace-head">
        <div>
          <h1>Люди и профили</h1>
          <span>Карты, роли и сохранённые связи для рабочих разборов.</span>
        </div>
        <nav className="workspace-bridge-actions" aria-label="Быстрые действия людей">
          <a className="primary-link-button" href="/charts/new">Создать карту</a>
          <a className="secondary-button" href="/charts">Кабинет карт</a>
          <a className="secondary-button" href="/interactions">Взаимодействия</a>
          <a className="secondary-button" href="/reports">Обзор</a>
          <a className="secondary-button" href="/transits">Транзиты</a>
        </nav>
      </section>

      <section className="workspace-bridge-summary" aria-label="Сводка людей">
        <div>
          <span>Всего карт</span>
          <strong>{profiles.length}</strong>
        </div>
        <div>
          <span>Моя карта</span>
          <strong>{selfProfile ? selfProfile.display_name : "не выбрана"}</strong>
        </div>
        <div>
          <span>Связей</span>
          <strong>{relationships.length}</strong>
        </div>
        <div>
          <span>Последнее обновление</span>
          <strong>{profiles.length || relationships.length ? latestPeopleObject(profiles, relationships) : "нет данных"}</strong>
        </div>
      </section>

      <div className="product-status">{status}</div>

      {needsAuth ? (
        <section className="history-empty private-history-gate">
          <span>Войдите для доступа.</span>
          <a className="primary-link-button" href="/charts/new">Создать карту</a>
        </section>
      ) : (
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
                  <article className="history-row" key={profile.id}>
                    <div>
                      <strong>{profile.display_name}{profile.is_self_profile ? " · моя карта" : ""}</strong>
                      <span>{profile.birth_date} · {formatProfileTime(profile)} · {profile.place.label}</span>
                      <small className="history-row-meta">
                        {profile.latest_calculation
                          ? `${formatCalculationStatus(profile.latest_calculation.status)} · ${profile.latest_calculation.graha_count} грах`
                          : "расчёт ещё не сохранён"}
                      </small>
                    </div>
                    <div className="people-card-actions">
                      <a href={`/charts/${profile.id}`}>Открыть</a>
                      <a href={`/charts/${profile.id}/edit`}>Редактировать</a>
                      <a href="/reports">Обзор</a>
                      <a href="/interactions">Связи</a>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="history-empty">
                <span>Сохранённых карт пока нет.</span>
                <div className="workspace-bridge-actions">
                  <a className="primary-link-button" href="/charts/new">Создать карту</a>
                  <a className="secondary-button" href="/charts">Кабинет карт</a>
                  <a className="secondary-button" href="/transits">Транзиты</a>
                </div>
              </div>
            )}
          </section>

          <section className="compatibility-saved-role-context" aria-label="Связи между картами">
            <div className="compatibility-saved-role-head">
              <div>
                <span>Связи между картами</span>
              </div>
            </div>
            {relationships.length ? (
              <div className="compatibility-saved-role-grid">
                {relationships.map((relationship) => (
                  <div key={relationship.id}>
                    <span>
                      {relationshipTypeLabel(relationship)} · обновлено {relationshipDate(relationship.updated_at)}
                    </span>
                    <strong>
                      {relationship.chart_a?.display_name ?? "Карта A"} · {roleLabels[relationship.role_a_id] ?? relationship.role_a_id}
                      {" ↔ "}
                      {relationship.chart_b?.display_name ?? "Карта B"} · {roleLabels[relationship.role_b_id] ?? relationship.role_b_id}
                    </strong>
                    {relationship.notes ? <small>{relationship.notes.slice(0, 140)}</small> : null}
                    <div className="people-relationship-actions">
                      <a href="/interactions">Открыть</a>
                      <a href="/reports">Обзор</a>
                      <a href="/people">Люди</a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="history-empty">
                <span>Связей между картами ещё нет.</span>
                <div className="workspace-bridge-actions">
                  <a className="primary-link-button" href="/interactions">Создать связь</a>
                  <a className="secondary-button" href="/charts/new">Создать карту</a>
                </div>
              </div>
            )}
          </section>
        </>
      )}
    </ProductShell>
  );
}
