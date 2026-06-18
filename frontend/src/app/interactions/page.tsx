"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import {
  fetchCurrentUser,
  listChartProfiles,
  listChartProfileRelationships,
  upsertChartProfileRelationship,
  type ChartProfile,
  type ChartProfileRelationship,
} from "@/lib/api";
import {
  getRelationshipFactor,
  getRelationshipType,
  listRelationshipRecipes,
  type EntityId,
  type RecipeFocus,
  type RelationshipFactorId,
  type RelationshipRecipe,
  type RelationshipTypeDefinition,
  type RelationshipUiMode,
} from "@/astrology";
import { EntityChip, EntityInspector } from "@/ui";

type Direction = "a_to_b" | "b_to_a";

const categoryLabels: Record<RelationshipTypeDefinition["category"], string> = {
  family: "Семья",
  romantic: "Отношения",
  business: "Дело",
  work: "Работа",
  education: "Обучение",
  social: "Социум",
  conflict: "Конфликт",
  custom: "Своя связь",
};

const roleLabels: Record<string, string> = {
  father: "отец",
  mother: "мать",
  parent: "родитель",
  child: "ребёнок",
  elder_sibling: "старший",
  younger_sibling: "младший",
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
  custom: "роль",
};

const backendRoleByRecipe: Record<string, string> = {
  father_child: "father",
  mother_child: "mother",
  parent_child: "father",
  elder_younger_sibling: "sibling",
  siblings: "sibling",
  spouses: "partner",
  romantic_partners: "partner",
  business_partners: "partner",
  boss_subordinate: "boss",
  colleagues: "other",
  guru_student: "other",
  friends: "other",
  opponents: "opponent",
  client_supplier: "other",
  custom: "other",
};

const calculationLabels: Record<string, string> = {
  "varga.D1": "D1",
  "varga.D3": "D3",
  "varga.D7": "D7",
  "varga.D9": "D9",
  "varga.D10": "D10",
  "varga.D12": "D12",
  "varga.D20": "D20",
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
  return `${profile.birth_date} · ${place}`;
}

function getVisibleRecipes(mode: RelationshipUiMode): RelationshipRecipe[] {
  return listRelationshipRecipes().filter((recipe) => {
    if (!(recipe.status !== "disabled")) return false;
    if (mode !== "astrologer" && !(recipe.status !== "draft")) return false;
    return recipe.visibleInModes.includes(mode);
  });
}

function hasD60(focus: RecipeFocus): boolean {
  return [...focus.primaryEntityIds, ...focus.secondaryEntityIds, ...focus.requiredCalculationIds, ...focus.optionalCalculationIds].includes("varga.D60");
}

function hasMissingSource(recipe: RelationshipRecipe): boolean {
  return [recipe.perspectiveAtoB, recipe.perspectiveBtoA, recipe.mutualFocus].some((focus) =>
    focus.warnings.some((warning) => warning.type === "missing_source"),
  );
}

function hasBirthTimeWarning(recipe: RelationshipRecipe): boolean {
  return [recipe.perspectiveAtoB, recipe.perspectiveBtoA, recipe.mutualFocus].some((focus) =>
    focus.warnings.some((warning) => warning.type === "birth_time_accuracy" || warning.type === "expert_only"),
  );
}

function labelCalculation(id: string): string {
  return calculationLabels[id] ?? id.replace("varga.", "");
}

function RelationshipFactorChip({ factorId, mode }: { factorId: RelationshipFactorId; mode: RelationshipUiMode }) {
  const factor = getRelationshipFactor(factorId);
  return (
    <span className="relationship-factor-chip" title={mode === "astrologer" ? factorId : undefined}>
      {factor?.label.ru ?? factor?.label.en ?? "Фактор"}
    </span>
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
          <RelationshipFactorChip key={factorId} factorId={factorId} mode={mode} />
        ))}
      </ChipRow>
      <ChipRow label="Расчёты">
        {[...required, ...optional].map((id) => (
          <span key={id} className="calculation-chip">
            {labelCalculation(id)}
          </span>
        ))}
      </ChipRow>
      {d60Hidden ? <p className="interaction-muted">Есть экспертные дополнительные факторы в режиме астролога.</p> : null}
    </section>
  );
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

export default function InteractionsPage() {
  const [mode, setMode] = useState<RelationshipUiMode>("novice");
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartProfileRelationship[]>([]);
  const [profileAId, setProfileAId] = useState<number | null>(null);
  const [profileBId, setProfileBId] = useState<number | null>(null);
  const [recipeId, setRecipeId] = useState("father_child");
  const [direction, setDirection] = useState<Direction>("a_to_b");
  const [note, setNote] = useState("");
  const [activeEntityId, setActiveEntityId] = useState<EntityId | null>(null);
  const [status, setStatus] = useState("Загружаю сохранённые карты...");
  const [needsAuth, setNeedsAuth] = useState(false);
  const [saving, setSaving] = useState(false);

  const recipes = useMemo(() => getVisibleRecipes(mode), [mode]);
  const selectedRecipe = useMemo(() => recipes.find((recipe) => recipe.id === recipeId) ?? recipes[0], [recipeId, recipes]);
  const relationshipType = selectedRecipe ? getRelationshipType(selectedRecipe.relationshipTypeId) : null;
  const profileA = profiles.find((profile) => profile.id === profileAId) ?? null;
  const profileB = profiles.find((profile) => profile.id === profileBId) ?? null;
  const canSave = Boolean(profileAId && profileBId && profileAId !== profileBId && selectedRecipe);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const user = await fetchCurrentUser();
        if (!user) {
          if (!cancelled) {
            setNeedsAuth(true);
            setStatus("Войдите, чтобы видеть только свои связи.");
          }
          return;
        }

        const [profileList, relationshipList] = await Promise.all([listChartProfiles(), listChartProfileRelationships()]);
        if (cancelled) return;
        setProfiles(profileList);
        setRelationships(relationshipList);
        setProfileAId((current) => current ?? profileList[0]?.id ?? null);
        setProfileBId((current) => current ?? profileList.find((profile) => profile.id !== profileList[0]?.id)?.id ?? null);
        setStatus(profileList.length < 2 ? "Для экрана нужны минимум две сохранённые карты." : "Выберите карты и тип связи.");
      } catch (error) {
        if (!cancelled) {
          setStatus(error instanceof Error ? error.message : "Не удалось загрузить взаимодействия.");
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedRecipe && recipes[0]) setRecipeId(recipes[0].id);
  }, [recipes, selectedRecipe]);

  function swapProfiles() {
    setProfileAId(profileBId);
    setProfileBId(profileAId);
    setDirection((current) => (current === "a_to_b" ? "b_to_a" : "a_to_b"));
  }

  async function saveRelationship() {
    if (!canSave || !selectedRecipe || !profileAId || !profileBId) return;
    setSaving(true);
    setStatus("Сохраняю связь...");
    try {
      const relationship = await upsertChartProfileRelationship({
        profile_id: profileAId,
        related_profile_id: profileBId,
        role: backendRoleByRecipe[selectedRecipe.id] ?? "other",
        notes: note,
        metadata: {
          relationshipTypeId: selectedRecipe.relationshipTypeId,
          direction,
        },
      });
      setRelationships((current) => [relationship, ...current.filter((item) => item.id !== relationship.id)]);
      setStatus("Связь сохранена.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось сохранить связь.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <ProductShell active="interactions">
      <header className="product-page-head">
        <div>
          <h1>Взаимодействия</h1>
          <p>Выберите две сохранённые карты и тип связи. Разбор AI здесь не запускается.</p>
        </div>
        <div className="interaction-mode-toggle" aria-label="Режим просмотра">
          <button type="button" className={mode === "novice" ? "active" : ""} onClick={() => setMode("novice")}>
            Новичок
          </button>
          <button type="button" className={mode === "astrologer" ? "active" : ""} onClick={() => setMode("astrologer")}>
            Астролог
          </button>
        </div>
      </header>

      <p className="interaction-status-line">{status}</p>

      {needsAuth ? (
        <section className="interaction-empty panel">
          <h2>Нужен вход</h2>
          <p>После входа здесь будут доступны только ваши сохранённые карты и связи.</p>
        </section>
      ) : (
        <section className="interaction-workspace" aria-label="Рабочее место взаимодействий">
          <aside className="interaction-type-list panel" aria-label="Типы связей">
            <h2>Тип связи</h2>
            {recipes.map((recipe) => {
              const type = getRelationshipType(recipe.relationshipTypeId);
              if (!type) return null;
              return (
                <button
                  key={recipe.id}
                  type="button"
                  className={recipe.id === selectedRecipe?.id ? "interaction-type-card active" : "interaction-type-card"}
                  onClick={() => setRecipeId(recipe.id)}
                >
                  <strong>{recipe.label.ru}</strong>
                  <span>
                    {categoryLabels[type.category]} · {type.symmetric ? "симметричная" : "направленная"}
                  </span>
                  {mode === "astrologer" ? <em>{recipe.status}</em> : null}
                </button>
              );
            })}
          </aside>

          <section className="interaction-setup-panel panel">
            <h2>Настройка</h2>
            {profiles.length < 2 ? (
              <div className="interaction-empty">
                <strong>Нужны минимум две карты.</strong>
                <p>Создайте или сохраните вторую карту, чтобы сравнивать взаимодействие людей.</p>
                <div className="interaction-actions">
                  <Link href="/charts/new">Создать карту</Link>
                  <Link href="/charts">Кабинет карт</Link>
                </div>
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

                <label>
                  Тип связи
                  <select value={selectedRecipe?.id ?? ""} onChange={(event) => setRecipeId(event.target.value)}>
                    {recipes.map((recipe) => (
                      <option key={recipe.id} value={recipe.id}>
                        {recipe.label.ru}
                      </option>
                    ))}
                  </select>
                </label>

                {relationshipType && !relationshipType.symmetric ? (
                  <div className="interaction-direction">
                    <span>Направление</span>
                    <button type="button" className={direction === "a_to_b" ? "active" : ""} onClick={() => setDirection("a_to_b")}>
                      A как {roleLabels[relationshipType.roleA] ?? relationshipType.roleA}
                    </button>
                    <button type="button" className={direction === "b_to_a" ? "active" : ""} onClick={() => setDirection("b_to_a")}>
                      B как {roleLabels[relationshipType.roleA] ?? relationshipType.roleA}
                    </button>
                  </div>
                ) : null}

                <button type="button" className="secondary-button" onClick={swapProfiles}>
                  Поменять карты местами
                </button>

                <label>
                  Заметка
                  <textarea value={note} onChange={(event) => setNote(event.target.value)} placeholder="Короткий контекст связи" />
                </label>

                <button type="button" className="primary-button" disabled={!canSave || saving} onClick={saveRelationship}>
                  {saving ? "Сохраняю..." : "Сохранить связь"}
                </button>
              </>
            )}

            <div className="interaction-saved-list">
              <h3>Сохранённые связи</h3>
              {relationships.length ? (
                relationships.slice(0, 6).map((relationship) => (
                  <div key={relationship.id} className="interaction-saved-row">
                    <strong>{relationship.profile?.display_name ?? "Карта"}</strong>
                    <span>{relationship.related_profile?.display_name ?? "Связанная карта"}</span>
                    <em>{relationship.link_status}</em>
                  </div>
                ))
              ) : (
                <p>Связей пока нет.</p>
              )}
            </div>
          </section>

          <section className="interaction-preview-panel panel">
            {selectedRecipe && relationshipType ? (
              <>
                <div className="interaction-preview-head">
                  <div>
                    <span>Recipe preview</span>
                    <h2>{selectedRecipe.label.ru}</h2>
                    <p>
                      {profileTitle(profileA)} ↔ {profileTitle(profileB)}
                    </p>
                  </div>
                  <em>{relationshipType.symmetric ? "симметричная" : direction === "a_to_b" ? "A → B" : "B → A"}</em>
                </div>

                <RecipeFocusPanel
                  title="Перспектива A → B"
                  focus={selectedRecipe.perspectiveAtoB}
                  mode={mode}
                  activeEntityId={activeEntityId}
                  onSelectEntity={setActiveEntityId}
                />
                <RecipeFocusPanel
                  title="Перспектива B → A"
                  focus={selectedRecipe.perspectiveBtoA}
                  mode={mode}
                  activeEntityId={activeEntityId}
                  onSelectEntity={setActiveEntityId}
                />
                <RecipeFocusPanel
                  title="Взаимный слой"
                  focus={selectedRecipe.mutualFocus}
                  mode={mode}
                  activeEntityId={activeEntityId}
                  onSelectEntity={setActiveEntityId}
                />

                {mode === "astrologer" && hasBirthTimeWarning(selectedRecipe) ? (
                  <p className="interaction-warning">
                    D60 требует точного времени рождения и остаётся только дополнительным экспертным фактором.
                    {[profileA, profileB].some((profile) => profile?.birth_time_accuracy !== "exact") ? " В одной из карт время рождения не точное." : ""}
                  </p>
                ) : null}

                {hasMissingSource(selectedRecipe) ? (
                  <p className="interaction-warning">Часть источников будет подключена отдельным этапом.</p>
                ) : null}

                <EntityInspector entityId={activeEntityId} onClose={() => setActiveEntityId(null)} />
              </>
            ) : (
              <div className="interaction-empty">
                <strong>Recipe не выбран.</strong>
                <p>Выберите тип связи слева.</p>
              </div>
            )}
          </section>
        </section>
      )}
    </ProductShell>
  );
}
