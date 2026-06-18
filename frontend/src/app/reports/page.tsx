"use client";

import Link from "next/link";
import type { ReactNode } from "react";
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
  getRelationshipFactor,
  getRelationshipType,
  getReportRecipe,
  listReportRecipes,
  listRelationshipRecipes,
  type EntityId,
  type ReportRecipe,
  type ReportRecipeId,
  type RecipeFocus,
  type RelationshipFactorId,
  type RelationshipTypeId,
  type RelationshipRecipe,
  type RelationshipUiMode,
} from "@/astrology";
import { EntityChip, EntityInspector } from "@/ui";

const reportRecipes = listReportRecipes();

const calculationLabels: Record<string, string> = {
  "varga.D1": "D1",
  "varga.D3": "D3",
  "varga.D7": "D7",
  "varga.D9": "D9",
  "varga.D10": "D10",
  "varga.D12": "D12",
  "varga.D30": "D30",
  "varga.D60": "D60",
  "dasha.vimshottari": "Вимшоттари",
  "transits.current": "Транзиты",
};

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

function labelCalculation(id: string): string {
  return calculationLabels[id] ?? id.replace("varga.", "");
}

function visibleEntityIds(entityIds: EntityId[], mode: RelationshipUiMode): EntityId[] {
  return entityIds.filter((entityId) => mode === "astrologer" || entityId !== "varga.D60");
}

function visibleCalculationIds(calculationIds: string[], mode: RelationshipUiMode): string[] {
  return calculationIds.filter((id) => mode === "astrologer" || id !== "varga.D60");
}

function hasD60(reportType: ReportRecipe, recipe: RelationshipRecipe | null): boolean {
  const recipeEntities = recipe
    ? [
        ...recipe.perspectiveAtoB.primaryEntityIds,
        ...recipe.perspectiveBtoA.primaryEntityIds,
        ...recipe.mutualFocus.primaryEntityIds,
        ...recipe.perspectiveAtoB.secondaryEntityIds,
        ...recipe.perspectiveBtoA.secondaryEntityIds,
        ...recipe.mutualFocus.secondaryEntityIds,
      ]
    : [];
  const recipeCalculations = recipe
    ? [
        ...recipe.perspectiveAtoB.requiredCalculationIds,
        ...recipe.perspectiveBtoA.requiredCalculationIds,
        ...recipe.mutualFocus.requiredCalculationIds,
        ...recipe.perspectiveAtoB.optionalCalculationIds,
        ...recipe.perspectiveBtoA.optionalCalculationIds,
        ...recipe.mutualFocus.optionalCalculationIds,
      ]
    : [];
  return [...reportType.primaryEntityIds, ...reportType.secondaryEntityIds, ...reportType.calculationIds, ...recipeEntities, ...recipeCalculations].includes("varga.D60");
}

function RelationshipFactorChip({ factorId }: { factorId: RelationshipFactorId }) {
  const factor = getRelationshipFactor(factorId);
  return <span className="relationship-factor-chip">{factor?.label.ru ?? factor?.label.en ?? "Фактор"}</span>;
}

function ChipRow({ children, label }: { children: ReactNode; label: string }) {
  const childArray = Array.isArray(children) ? children.filter(Boolean) : children;
  const isEmpty = Array.isArray(childArray) ? childArray.length === 0 : !childArray;
  return (
    <div className="interaction-chip-row">
      <span>{label}</span>
      <div>{isEmpty ? <em>не задано</em> : childArray}</div>
    </div>
  );
}

function ReportRecipeFocus({
  activeEntityId,
  focus,
  mode,
  onSelectEntity,
  title,
}: {
  activeEntityId: EntityId | null;
  focus: RecipeFocus;
  mode: RelationshipUiMode;
  onSelectEntity: (entityId: EntityId) => void;
  title: string;
}) {
  const primary = visibleEntityIds(focus.primaryEntityIds, mode);
  const secondary = visibleEntityIds(focus.secondaryEntityIds, mode);
  const calculations = visibleCalculationIds([...focus.requiredCalculationIds, ...focus.optionalCalculationIds], mode);

  return (
    <section className="interaction-layer">
      <h3>{title}</h3>
      <ChipRow label="Главные точки">
        {primary.map((entityId) => (
          <EntityChip key={entityId} entityId={entityId} active={activeEntityId === entityId} onSelect={onSelectEntity} />
        ))}
      </ChipRow>
      <ChipRow label="Дополнительно">
        {secondary.map((entityId) => (
          <EntityChip key={entityId} entityId={entityId} active={activeEntityId === entityId} onSelect={onSelectEntity} />
        ))}
      </ChipRow>
      <ChipRow label="Факторы">
        {focus.relationshipFactorIds.map((factorId) => (
          <RelationshipFactorChip key={factorId} factorId={factorId} />
        ))}
      </ChipRow>
      <ChipRow label="Расчёты">
        {calculations.map((id) => (
          <span key={id} className="calculation-chip">
            {labelCalculation(id)}
          </span>
        ))}
      </ChipRow>
    </section>
  );
}

function ReportRecipePreview({
  activeEntityId,
  mode,
  onSelectEntity,
  selectedRecipe,
}: {
  activeEntityId: EntityId | null;
  mode: RelationshipUiMode;
  onSelectEntity: (entityId: EntityId) => void;
  selectedRecipe: RelationshipRecipe | null;
}) {
  if (!selectedRecipe) {
    return (
      <section className="interaction-layer">
        <h3>Контекст связи</h3>
        <p className="interaction-muted">Связь не выбрана. Отчёт будет строиться только вокруг основной карты.</p>
      </section>
    );
  }

  return (
    <>
      <ReportRecipeFocus title="A → B" focus={selectedRecipe.perspectiveAtoB} mode={mode} activeEntityId={activeEntityId} onSelectEntity={onSelectEntity} />
      <ReportRecipeFocus title="B → A" focus={selectedRecipe.perspectiveBtoA} mode={mode} activeEntityId={activeEntityId} onSelectEntity={onSelectEntity} />
      <ReportRecipeFocus title="Взаимный слой" focus={selectedRecipe.mutualFocus} mode={mode} activeEntityId={activeEntityId} onSelectEntity={onSelectEntity} />
    </>
  );
}

export default function ReportBuilderPage() {
  const [mode, setMode] = useState<RelationshipUiMode>("novice");
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartRelationship[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<number | null>(null);
  const [selectedRelationshipId, setSelectedRelationshipId] = useState<number | null>(null);
  const [reportTypeId, setReportTypeId] = useState<ReportRecipeId>(reportRecipes[0].id);
  const [activeEntityId, setActiveEntityId] = useState<EntityId | null>(null);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [needsAuth, setNeedsAuth] = useState(false);

  const reportType = getReportRecipe(reportTypeId) ?? reportRecipes[0];
  const selectedProfile = profiles.find((profile) => profile.id === selectedProfileId) ?? null;
  const relatedRelationships = relationships.filter(
    (relationship) => selectedProfileId && (relationship.chart_a_id === selectedProfileId || relationship.chart_b_id === selectedProfileId),
  );
  const selectedRelationship = relatedRelationships.find((relationship) => relationship.id === selectedRelationshipId) ?? null;
  const selectedRecipe = selectedRelationship
    ? listRelationshipRecipes().find((recipe) => recipe.relationshipTypeId === selectedRelationship.relationship_type_id) ?? null
    : null;
  const selectedRelationshipType = selectedRelationship ? getRelationshipType(selectedRelationship.relationship_type_id as RelationshipTypeId) : null;
  const selectedRelationshipProfiles = selectedRelationship
    ? [
        profiles.find((profile) => profile.id === selectedRelationship.chart_a_id) ?? null,
        profiles.find((profile) => profile.id === selectedRelationship.chart_b_id) ?? null,
      ]
    : [];
  const calculations = useMemo(() => {
    const recipeCalculations = selectedRecipe
      ? [
          ...selectedRecipe.perspectiveAtoB.requiredCalculationIds,
          ...selectedRecipe.perspectiveBtoA.requiredCalculationIds,
          ...selectedRecipe.mutualFocus.requiredCalculationIds,
          ...selectedRecipe.perspectiveAtoB.optionalCalculationIds,
          ...selectedRecipe.perspectiveBtoA.optionalCalculationIds,
          ...selectedRecipe.mutualFocus.optionalCalculationIds,
        ]
      : [];
    return Array.from(new Set(visibleCalculationIds([...reportType.calculationIds, ...recipeCalculations], mode)));
  }, [mode, reportType, selectedRecipe]);
  const d60Hidden = mode !== "astrologer" && hasD60(reportType, selectedRecipe);
  const birthTimeWarning =
    selectedProfile?.birth_time_accuracy !== "exact" ||
    selectedRelationshipProfiles.some((profile) => profile?.birth_time_accuracy !== "exact");

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
                  <select value={reportTypeId} onChange={(event) => setReportTypeId(event.target.value as ReportRecipeId)}>
                    {reportRecipes.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.label}
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
                        {getRelationshipType(relationship.relationship_type_id as RelationshipTypeId)?.label.ru ?? relationship.relationship_type_id}
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
                <h2>{reportType.label}</h2>
                <p>{reportType.summary}</p>
              </div>
              <em>{selectedRelationshipType?.label.ru ?? "одна карта"}</em>
            </div>

            <section className="interaction-layer">
              <h3>Карта</h3>
              <ChipRow label="Главные точки">
                {visibleEntityIds(reportType.primaryEntityIds, mode).map((entityId) => (
                  <EntityChip key={entityId} entityId={entityId} active={activeEntityId === entityId} onSelect={setActiveEntityId} />
                ))}
              </ChipRow>
              <ChipRow label="Дополнительно">
                {visibleEntityIds(reportType.secondaryEntityIds, mode).map((entityId) => (
                  <EntityChip key={entityId} entityId={entityId} active={activeEntityId === entityId} onSelect={setActiveEntityId} />
                ))}
              </ChipRow>
              <ChipRow label="Расчёты">
                {calculations.map((id) => (
                  <span key={id} className="calculation-chip">
                    {labelCalculation(id)}
                  </span>
                ))}
              </ChipRow>
            </section>

            <ReportRecipePreview selectedRecipe={selectedRecipe} mode={mode} activeEntityId={activeEntityId} onSelectEntity={setActiveEntityId} />

            {d60Hidden ? <p className="interaction-warning">D60 скрыта в режиме новичка. Включите режим астролога, если время рождения подтверждено.</p> : null}
            {mode === "astrologer" && birthTimeWarning ? <p className="interaction-warning">Проверьте точность времени рождения перед использованием тонких варг.</p> : null}
          </main>

          <aside className="reports-inspector-panel panel" aria-label="Описание выбранной сущности">
            <EntityInspector entityId={activeEntityId} onClose={() => setActiveEntityId(null)} />
          </aside>
        </section>
      )}
    </ProductShell>
  );
}
