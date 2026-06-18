"use client";

import { useEffect, useState } from "react";
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

export default function PeoplePage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartRelationship[]>([]);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [needsAuth, setNeedsAuth] = useState(false);

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
      {!needsAuth ? (
        <div className="page-action-strip">
          <a className="primary-link-button" href="/charts/new">Добавить карту</a>
        </div>
      ) : null}

      <div className="product-status">{status}</div>

      {needsAuth ? (
        <section className="history-empty private-history-gate">
          <span>Войдите для доступа.</span>
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
                  <a className="history-row" href={`/?profile=${profile.id}#chart`} key={profile.id}>
                    <div>
                      <strong>{profile.display_name}{profile.is_self_profile ? " · моя карта" : ""}</strong>
                      <span>{profile.birth_date} · {formatProfileTime(profile)} · {profile.place.label}</span>
                      <small className="history-row-meta">
                        {profile.latest_calculation
                          ? `${formatCalculationStatus(profile.latest_calculation.status)} · ${profile.latest_calculation.graha_count} грах`
                          : "расчёт ещё не сохранён"}
                      </small>
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <div className="history-empty">Сохранённых карт ещё нет.</div>
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
                    <a href="/interactions">Открыть во Взаимодействиях</a>
                  </div>
                ))}
              </div>
            ) : (
              <div className="history-empty">
                <span>Связей между картами ещё нет.</span>
                <a href="/interactions">Создать связь</a>
              </div>
            )}
          </section>
        </>
      )}
    </ProductShell>
  );
}
