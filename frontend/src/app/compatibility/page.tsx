"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import {
  createChartRelationship,
  deleteChartRelationship,
  fetchCurrentUser,
  listChartProfiles,
  listChartRelationships,
  updateChartRelationship,
  type ChartProfile,
  type ChartRelationship,
} from "@/lib/api";
import {
  getRelationshipFactor,
  getRelationshipRecipe,
  getRelationshipType,
  type EntityId,
  type RecipeFocus,
  type RelationshipFactorId,
  type RelationshipRecipe,
  type RelationshipTypeId,
  type RelationshipUiMode,
} from "@/astrology";
import {
  compatibilityScope,
  isCompatibilityRelationshipTypeId,
  listCompatibilityRecipes,
  listCompatibilityRelationshipTypes,
  type CompatibilityRelationshipTypeId,
} from "@/astrology/compatibility/compatibilityScope";
import { EntityChip, EntityInspector } from "@/ui";

const calculationLabels: Record<string, string> = {
  "varga.D1": "D1",
  "varga.D9": "D9",
  "varga.D60": "D60",
  "dasha.vimshottari": "Вимшоттари",
  "transits.current": "Транзиты",
};

function profileTitle(profile: ChartProfile | null): string {
  return profile?.display_name ?? "Карта";
}

function profileMeta(profile: ChartProfile | null): string {
  if (!profile) return "Не выбрана";
  const place = profile.place?.label ?? profile.place?.name ?? "место не указано";
  const time = profile.birth_time ?? "время не указано";
  return `${profile.birth_date} · ${time} · ${place} · ${accuracyLabel(profile.birth_time_accuracy)}`;
}

function accuracyLabel(value: string): string {
  if (value === "exact") return "точное время";
  if (value === "approximate") return "примерное время";
  return "время не указано";
}

function relationshipLabel(relationship: ChartRelationship): string {
  const type = getRelationshipType(relationship.relationship_type_id as RelationshipTypeId);
  return type?.label.ru ?? "Пара";
}

function labelCalculation(id: string): string {
  return calculationLabels[id] ?? id.replace("varga.", "");
}

function hasD60(focus: RecipeFocus): boolean {
  return [...focus.primaryEntityIds, ...focus.secondaryEntityIds, ...focus.requiredCalculationIds, ...focus.optionalCalculationIds].includes("varga.D60");
}

function hasBirthTimeWarning(recipe: RelationshipRecipe): boolean {
  return [recipe.perspectiveAtoB, recipe.perspectiveBtoA, recipe.mutualFocus].some((focus) =>
    focus.warnings.some((warning) => warning.type === "birth_time_accuracy" || warning.type === "expert_only"),
  );
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

function RecipeFocusPanel({
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
  const primary = focus.primaryEntityIds.filter((entityId) => mode === "astrologer" || entityId !== "varga.D60");
  const secondary = focus.secondaryEntityIds.filter((entityId) => mode === "astrologer" || entityId !== "varga.D60");
  const required = focus.requiredCalculationIds.filter((id) => mode === "astrologer" || id !== "varga.D60");
  const optional = focus.optionalCalculationIds.filter((id) => mode === "astrologer" || id !== "varga.D60");
  const d60Hidden = mode !== "astrologer" && hasD60(focus);

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
        {[...required, ...optional].map((id) => (
          <span key={id} className="calculation-chip">
            {labelCalculation(id)}
          </span>
        ))}
      </ChipRow>
      {d60Hidden ? <p className="interaction-muted">Есть дополнительные экспертные факторы в режиме астролога.</p> : null}
    </section>
  );
}

export default function CompatibilityPage() {
  const [mode, setMode] = useState<RelationshipUiMode>("novice");
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartRelationship[]>([]);
  const [selectedRelationshipId, setSelectedRelationshipId] = useState<number | null>(null);
  const [profileAId, setProfileAId] = useState<number | null>(null);
  const [profileBId, setProfileBId] = useState<number | null>(null);
  const [relationshipTypeId, setRelationshipTypeId] = useState<CompatibilityRelationshipTypeId>("romantic_partners");
  const [notes, setNotes] = useState("");
  const [activeEntityId, setActiveEntityId] = useState<EntityId | null>(null);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [needsAuth, setNeedsAuth] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const recipes = useMemo(() => listCompatibilityRecipes(mode), [mode]);
  const relationshipTypes = useMemo(() => listCompatibilityRelationshipTypes(), []);
  const compatibilityTypeIds = compatibilityScope.relationshipTypeIds;
  const selectedRecipe = useMemo(() => getRelationshipRecipe(relationshipTypeId) ?? recipes[0] ?? null, [relationshipTypeId, recipes]);
  const selectedType = useMemo(() => getRelationshipType(relationshipTypeId), [relationshipTypeId]);
  const profileA = profiles.find((profile) => profile.id === profileAId) ?? null;
  const profileB = profiles.find((profile) => profile.id === profileBId) ?? null;
  const savedPairs = relationships.filter(
    (relationship) => compatibilityTypeIds.includes(relationship.relationship_type_id as CompatibilityRelationshipTypeId) && isCompatibilityRelationshipTypeId(relationship.relationship_type_id),
  );
  const canSave = Boolean(profileAId && profileBId && profileAId !== profileBId && selectedType && selectedRecipe);
  const bothExact = profileA?.birth_time_accuracy === "exact" && profileB?.birth_time_accuracy === "exact";

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const user = await fetchCurrentUser();
        if (!user) {
          if (!cancelled) {
            setNeedsAuth(true);
            setStatus("Войдите, чтобы выбрать сохранённые карты и сохранить пару.");
          }
          return;
        }
        const [profileList, relationshipList] = await Promise.all([listChartProfiles(), listChartRelationships()]);
        if (cancelled) return;
        setProfiles(profileList);
        setRelationships(relationshipList);
        setProfileAId((current) => current ?? profileList[0]?.id ?? null);
        setProfileBId((current) => current ?? profileList.find((profile) => profile.id !== profileList[0]?.id)?.id ?? null);
        setStatus(profileList.length < 2 ? "Для совместимости нужны две разные сохранённые карты." : "Выберите две карты и тип пары.");
      } catch (error) {
        if (!cancelled) setStatus(error instanceof Error ? error.message : "Не удалось загрузить совместимость.");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  function openRelationship(relationship: ChartRelationship) {
    if (!isCompatibilityRelationshipTypeId(relationship.relationship_type_id)) return;
    setSelectedRelationshipId(relationship.id);
    setProfileAId(relationship.chart_a_id);
    setProfileBId(relationship.chart_b_id);
    setRelationshipTypeId(relationship.relationship_type_id);
    setNotes(relationship.notes ?? "");
    setStatus("Пара открыта.");
  }

  function newPair() {
    setSelectedRelationshipId(null);
    setNotes("");
    setStatus("Новая пара.");
  }

  function swapProfiles() {
    setProfileAId(profileBId);
    setProfileBId(profileAId);
  }

  async function savePair() {
    if (!canSave || !profileAId || !profileBId || !selectedType) return;
    setSaving(true);
    setStatus("Сохраняю пару...");
    const payload = {
      chart_a_id: profileAId,
      chart_b_id: profileBId,
      relationship_type_id: relationshipTypeId,
      role_a_id: selectedType.roleA,
      role_b_id: selectedType.roleB,
      notes,
    };
    try {
      const relationship = selectedRelationshipId
        ? await updateChartRelationship(selectedRelationshipId, payload)
        : await createChartRelationship(payload);
      setRelationships((current) => [relationship, ...current.filter((item) => item.id !== relationship.id)]);
      setSelectedRelationshipId(relationship.id);
      setStatus("Пара сохранена.");
    } catch (error) {
      setStatus(error instanceof Error && error.message.includes("already exists") ? "Такая пара уже сохранена. Откройте её из списка." : error instanceof Error ? error.message : "Не удалось сохранить пару.");
    } finally {
      setSaving(false);
    }
  }

  async function deletePair(relationship: ChartRelationship) {
    const nameA = relationship.chart_a?.display_name ?? "карта A";
    const nameB = relationship.chart_b?.display_name ?? "карта B";
    if (!window.confirm(`Удалить пару между «${nameA}» и «${nameB}»? Карты удалены не будут.`)) return;
    setDeletingId(relationship.id);
    try {
      await deleteChartRelationship(relationship.id);
      setRelationships((current) => current.filter((item) => item.id !== relationship.id));
      if (selectedRelationshipId === relationship.id) setSelectedRelationshipId(null);
      setStatus("Пара удалена.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось удалить пару.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <ProductShell active="compatibility">
      <header className="product-page-head compatibility-workspace-head">
        <div>
          <h1>Совместимость пары</h1>
          <p>Выберите две сохранённые карты и тип отношений. Здесь отображается структура факторов пары без автоматических выводов.</p>
        </div>
        <div className="interaction-mode-toggle" aria-label="Режим просмотра">
          <button type="button" className={mode === "novice" ? "active" : ""} onClick={() => setMode("novice")}>
            Новичок
          </button>
          <button type="button" className={mode === "astrologer" ? "active" : ""} onClick={() => setMode("astrologer")}>
            Астролог
          </button>
          <button type="button" onClick={newPair}>
            Новая пара
          </button>
          <Link href="/charts">Кабинет карт</Link>
        </div>
      </header>

      <p className="interaction-status-line">{status}</p>

      {needsAuth ? (
        <section className="interaction-empty panel">
          <h2>Нужен вход</h2>
          <p>Войдите, чтобы выбрать сохранённые карты и сохранить пару.</p>
        </section>
      ) : (
        <section className="compatibility-workspace" aria-label="Рабочее место совместимости пары">
          <aside className="compatibility-saved-pairs panel" aria-label="Сохранённые пары">
            <h2>Сохранённые пары</h2>
            {savedPairs.length ? (
              savedPairs.map((relationship) => (
                <article key={relationship.id} className={selectedRelationshipId === relationship.id ? "compatibility-pair-row active" : "compatibility-pair-row"}>
                  <strong>{relationship.chart_a?.display_name ?? "Карта A"}</strong>
                  <span>↔ {relationship.chart_b?.display_name ?? "Карта B"}</span>
                  <em>{relationshipLabel(relationship)}</em>
                  {relationship.notes ? <small>{relationship.notes}</small> : null}
                  <div>
                    <button type="button" onClick={() => openRelationship(relationship)}>
                      Открыть
                    </button>
                    <button type="button" disabled={deletingId === relationship.id} onClick={() => void deletePair(relationship)}>
                      Удалить
                    </button>
                  </div>
                </article>
              ))
            ) : (
              <p>Сохранённых пар пока нет. Выберите две карты, чтобы создать связь.</p>
            )}
          </aside>

          <main className="compatibility-pair-workbench panel">
            <section className="compatibility-pair-selector">
              <h2>Пара</h2>
              {profiles.length < 2 ? (
                <div className="interaction-empty">
                  <strong>Сначала создайте две карты.</strong>
                  <Link href="/charts/new">Создать карту</Link>
                </div>
              ) : (
                <>
                  <label>
                    Карта A
                    <select value={profileAId ?? ""} onChange={(event) => setProfileAId(Number(event.target.value))}>
                      {profiles.map((profile) => (
                        <option key={profile.id} value={profile.id} disabled={profile.id === profileBId}>
                          {profile.display_name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <small>{profileMeta(profileA)}</small>

                  <label>
                    Карта B
                    <select value={profileBId ?? ""} onChange={(event) => setProfileBId(Number(event.target.value))}>
                      {profiles.map((profile) => (
                        <option key={profile.id} value={profile.id} disabled={profile.id === profileAId}>
                          {profile.display_name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <small>{profileMeta(profileB)}</small>

                  <button type="button" className="secondary-button" onClick={swapProfiles}>
                    Поменять карты местами
                  </button>
                </>
              )}
            </section>

            <section className="compatibility-type-selector">
              <h2>Тип пары</h2>
              <div className="compatibility-type-grid">
                {relationshipTypes.map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    className={relationshipTypeId === type.id ? "interaction-type-card active" : "interaction-type-card"}
                    onClick={() => setRelationshipTypeId(type.id as CompatibilityRelationshipTypeId)}
                  >
                    <strong>{type.label.ru}</strong>
                    <span>{type.symmetric ? "симметричная" : "направленная"}</span>
                  </button>
                ))}
              </div>
              <label>
                Заметка
                <textarea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Короткий контекст пары" />
              </label>
              <button type="button" className="primary-button" disabled={!canSave || saving} onClick={() => void savePair()}>
                {saving ? "Сохраняю..." : selectedRelationshipId ? "Обновить пару" : "Сохранить пару"}
              </button>
            </section>

            <section className="compatibility-recipe-panel">
              {selectedRecipe ? (
                <>
                  <div className="interaction-preview-head">
                    <div>
                      <span>Структура факторов</span>
                      <h2>{selectedRecipe.label.ru}</h2>
                      <p>
                        {profileTitle(profileA)} ↔ {profileTitle(profileB)}
                      </p>
                    </div>
                    <em>{selectedType?.symmetric ? "симметричная" : "направленная"}</em>
                  </div>
                  <RecipeFocusPanel title="A → B" focus={selectedRecipe.perspectiveAtoB} mode={mode} activeEntityId={activeEntityId} onSelectEntity={setActiveEntityId} />
                  <RecipeFocusPanel title="B → A" focus={selectedRecipe.perspectiveBtoA} mode={mode} activeEntityId={activeEntityId} onSelectEntity={setActiveEntityId} />
                  <RecipeFocusPanel title="Взаимный слой" focus={selectedRecipe.mutualFocus} mode={mode} activeEntityId={activeEntityId} onSelectEntity={setActiveEntityId} />
                  {mode === "astrologer" && hasBirthTimeWarning(selectedRecipe) ? (
                    <p className="interaction-warning">
                      D60 остаётся дополнительным экспертным фактором и требует точного времени рождения обеих карт.
                      {!bothExact ? " D60 скрыта, поскольку время рождения одной или обеих карт не подтверждено как точное." : ""}
                    </p>
                  ) : null}
                </>
              ) : (
                <div className="interaction-empty">
                  <strong>Структура анализа для этого типа отношений пока недоступна.</strong>
                </div>
              )}
            </section>
          </main>

          <aside className="compatibility-inspector panel" aria-label="Описание выбранной сущности">
            <EntityInspector entityId={activeEntityId} onClose={() => setActiveEntityId(null)} />
          </aside>
        </section>
      )}
    </ProductShell>
  );
}
