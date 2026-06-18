"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import {
  fetchCurrentUser,
  listChartProfiles,
  listChartRelationships,
  type ChartProfile,
  type ChartRelationship,
} from "@/lib/api";
import {
  getRelationshipType,
  getReportType,
  listReportTypes,
  resolveReportRecipe,
  type EntityId,
  type RelationshipTypeId,
  type RelationshipUiMode,
  type ReportTypeId,
} from "@/astrology";
import { EntityInspector, ReportRecipeRenderer } from "@/ui";

const reportTypes = listReportTypes();

function profileMeta(profile: ChartProfile | null): string {
  if (!profile) return "Карта не выбрана";
  const place = profile.place?.label ?? profile.place?.name ?? "место не указано";
  const time = profile.birth_time ?? "время не указано";
  return `${profile.birth_date} · ${time} · ${place} · ${accuracyLabel(profile.birth_time_accuracy)}`;
}

function accuracyLabel(value: string): string {
  if (value === "exact") return "точное время";
  if (value === "approximate") return "примерное время";
  return "время не указано";
}

export default function ReportBuilderPage() {
  const [mode, setMode] = useState<RelationshipUiMode>("novice");
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartRelationship[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<number | null>(null);
  const [selectedRelationshipId, setSelectedRelationshipId] = useState<number | null>(null);
  const [reportTypeId, setReportTypeId] = useState<ReportTypeId>(reportTypes[0].id);
  const [activeEntityId, setActiveEntityId] = useState<EntityId | null>(null);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [needsAuth, setNeedsAuth] = useState(false);

  const reportType = getReportType(reportTypeId) ?? reportTypes[0];
  const selectedProfile = profiles.find((profile) => profile.id === selectedProfileId) ?? null;
  const relatedRelationships = relationships.filter(
    (relationship) => selectedProfileId && (relationship.chart_a_id === selectedProfileId || relationship.chart_b_id === selectedProfileId),
  );
  const selectedRelationship = relatedRelationships.find((relationship) => relationship.id === selectedRelationshipId) ?? null;
  const selectedRelationshipType = selectedRelationship ? getRelationshipType(selectedRelationship.relationship_type_id as RelationshipTypeId) : null;

  const resolvedRecipe = useMemo(
    () =>
      resolveReportRecipe({
        reportTypeId,
        mode,
        primaryBirthTimeAccuracy: selectedProfile?.birth_time_accuracy ?? null,
        selectedRelationship: selectedRelationship
          ? {
              relationshipTypeId: selectedRelationship.relationship_type_id as RelationshipTypeId,
            }
          : null,
      }),
    [mode, reportTypeId, selectedProfile?.birth_time_accuracy, selectedRelationship],
  );

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const user = await fetchCurrentUser();
        if (!user) {
          if (!cancelled) {
            setNeedsAuth(true);
            setStatus("Войдите, чтобы собрать отчёт по своим картам.");
          }
          return;
        }
        const [profileList, relationshipList] = await Promise.all([listChartProfiles(), listChartRelationships()]);
        if (cancelled) return;
        setProfiles(profileList);
        setRelationships(relationshipList);
        setSelectedProfileId((current) => current ?? profileList[0]?.id ?? null);
        setStatus(profileList.length ? "Выберите карту, тип отчёта и контекст." : "Сначала создайте сохранённую карту.");
      } catch (error) {
        if (!cancelled) setStatus(error instanceof Error ? error.message : "Не удалось загрузить конструктор отчёта.");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!relatedRelationships.some((relationship) => relationship.id === selectedRelationshipId)) {
      setSelectedRelationshipId(null);
    }
  }, [relatedRelationships, selectedRelationshipId]);

  return (
    <ProductShell active="reports">
      <header className="product-page-head reports-workspace-head">
        <div>
          <h1>Конструктор отчёта</h1>
          <p>Соберите структуру будущего отчёта из карты, сохранённых связей, рецептов и сущностей. AI-генерация здесь не запускается.</p>
        </div>
        <div className="interaction-mode-toggle" aria-label="Режим просмотра">
          <button type="button" className={mode === "novice" ? "active" : ""} onClick={() => setMode("novice")}>
            Новичок
          </button>
          <button type="button" className={mode === "astrologer" ? "active" : ""} onClick={() => setMode("astrologer")}>
            Астролог
          </button>
          <Link href="/charts">Кабинет карт</Link>
        </div>
      </header>

      <p className="interaction-status-line">{status}</p>

      {needsAuth ? (
        <section className="interaction-empty panel">
          <h2>Нужен вход</h2>
          <p>После входа здесь будут доступны только ваши карты, связи и заготовки отчётов.</p>
        </section>
      ) : (
        <section className="reports-workspace" aria-label="Рабочее место конструктора отчётов">
          <aside className="reports-setup-panel panel">
            <h2>Основа</h2>
            {profiles.length ? (
              <>
                <label>
                  Карта
                  <select value={selectedProfileId ?? ""} onChange={(event) => setSelectedProfileId(Number(event.target.value))}>
                    {profiles.map((profile) => (
                      <option key={profile.id} value={profile.id}>
                        {profile.display_name}
                      </option>
                    ))}
                  </select>
                </label>
                <small>{profileMeta(selectedProfile)}</small>

                <label>
                  Тип отчёта
                  <select value={reportTypeId} onChange={(event) => setReportTypeId(event.target.value as ReportTypeId)}>
                    {reportTypes.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.label.ru}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Связь как контекст
                  <select value={selectedRelationshipId ?? ""} onChange={(event) => setSelectedRelationshipId(event.target.value ? Number(event.target.value) : null)}>
                    <option value="">Без связанной карты</option>
                    {relatedRelationships.map((relationship) => (
                      <option key={relationship.id} value={relationship.id}>
                        {(relationship.chart_a_id === selectedProfileId ? relationship.chart_b?.display_name : relationship.chart_a?.display_name) ?? "Связанная карта"} ·{" "}
                        {getRelationshipType(relationship.relationship_type_id as RelationshipTypeId)?.label.ru ?? "Связь"}
                      </option>
                    ))}
                  </select>
                </label>
              </>
            ) : (
              <div className="interaction-empty">
                <strong>Сохранённых карт пока нет.</strong>
                <Link href="/charts/new">Создать карту</Link>
              </div>
            )}
          </aside>

          <main className="reports-preview-panel panel">
            <div className="interaction-preview-head">
              <div>
                <span>Черновик структуры</span>
                <h2>{resolvedRecipe.label.ru}</h2>
                <p>{reportType.shortDescription.ru}</p>
              </div>
              <em>{selectedRelationshipType?.label.ru ?? "одна карта"}</em>
            </div>

            <ReportRecipeRenderer resolvedRecipe={resolvedRecipe} activeEntityId={activeEntityId} onEntitySelect={setActiveEntityId} />

            {resolvedRecipe.unavailableFactors.length ? <p className="interaction-warning">Раздел пока недоступен.</p> : null}
          </main>

          <aside className="reports-inspector-panel panel" aria-label="Описание выбранной сущности">
            <EntityInspector entityId={activeEntityId} onClose={() => setActiveEntityId(null)} />
          </aside>
        </section>
      )}
    </ProductShell>
  );
}
