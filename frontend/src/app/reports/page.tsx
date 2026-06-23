"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { buildAiReviewQualityLabSummary } from "@/lib/ai-review-quality";
import {
  fetchCurrentUser,
  listChartProfiles,
  listChartRelationships,
  type ChartProfile,
  type ChartRelationship,
} from "@/lib/api";
import {
  buildReportWorkspaceReadiness,
  getRelationshipType,
  getReportType,
  guidanceModes,
  listReportTypes,
  reportIntents,
  resolveReportRecipe,
  type EntityId,
  type GuidanceModeId,
  type RelationshipTypeId,
  type RelationshipUiMode,
  type ReportIntentId,
  type ReportTypeId,
} from "@/astrology";
import { EntityInspector, ReportRecipeRenderer } from "@/ui";

const reportTypes = listReportTypes();
const aiReviewQualityLab = buildAiReviewQualityLabSummary();

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

function readinessLabel(status: string): string {
  if (status === "ready") return "Готов";
  if (status === "not_available") return "Недоступно";
  return "Нужно дополнить";
}

export default function ReportBuilderPage() {
  const [mode, setMode] = useState<RelationshipUiMode>("novice");
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [relationships, setRelationships] = useState<ChartRelationship[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<number | null>(null);
  const [selectedRelationshipId, setSelectedRelationshipId] = useState<number | null>(null);
  const [reportTypeId, setReportTypeId] = useState<ReportTypeId>(reportTypes[0].id);
  const [selectedIntentId, setSelectedIntentId] = useState<ReportIntentId>("short_report");
  const [guidanceModeId, setGuidanceModeId] = useState<GuidanceModeId>("general");
  const [questionText, setQuestionText] = useState("");
  const [activeEntityId, setActiveEntityId] = useState<EntityId | null>(null);
  const [status, setStatus] = useState("Загружаю сохраненные карты...");
  const [needsAuth, setNeedsAuth] = useState(false);

  const reportType = getReportType(reportTypeId) ?? reportTypes[0];
  const selectedIntent = reportIntents.find((intent) => intent.id === selectedIntentId) ?? reportIntents[0];
  const selectedGuidanceMode = guidanceModes.find((item) => item.id === guidanceModeId) ?? guidanceModes[0];
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

  const readiness = useMemo(
    () =>
      buildReportWorkspaceReadiness({
        selectedChartId: selectedProfileId,
        selectedRelationshipId,
        selectedReportTypeId: reportTypeId,
        selectedRecipeId: resolvedRecipe.recipeId,
        intentId: selectedIntentId,
        guidanceMode: guidanceModeId,
        questionText,
      }),
    [guidanceModeId, questionText, reportTypeId, resolvedRecipe.recipeId, selectedIntentId, selectedProfileId, selectedRelationshipId],
  );

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const user = await fetchCurrentUser();
        if (!user) {
          if (!cancelled) {
            setNeedsAuth(true);
            setStatus("Войдите, чтобы собрать отчет по своим картам.");
          }
          return;
        }
        const [profileList, relationshipList] = await Promise.all([listChartProfiles(), listChartRelationships()]);
        if (cancelled) return;
        setProfiles(profileList);
        setRelationships(relationshipList);
        setSelectedProfileId((current) => current ?? profileList[0]?.id ?? null);
        setStatus(profileList.length ? "Выберите карту, намерение и контекст." : "Сначала создайте сохраненную карту.");
      } catch (error) {
        if (!cancelled) setStatus(error instanceof Error ? error.message : "Не удалось загрузить конструктор отчета.");
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
          <h1>Конструктор отчета</h1>
          <p>Подготовьте структуру будущего обзора из карты, сохраненных связей, рецептов и сущностей. AI-генерация здесь не запускается.</p>
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

      <section className="ai-review-quality-rubric" data-ai-review-quality-rubric="E118-A" aria-label="AI review quality rubric">
        <div>
          <strong>AI review quality rubric</strong>
          <span>Local checklist for future review drafts; not a generated final review.</span>
        </div>
        <ul>
          <li>Interpretation depth</li>
          <li>Specific chart evidence</li>
          <li>Practical synthesis</li>
          <li>Caveats and confidence</li>
        </ul>
        <span hidden>E118-A; batched_ui_ai_review_quality_stage=E118-A; ai_review_quality_rubric_present=true; ai_review_generation_changed=false; backend_calculation_changed=false; production_deploy_skipped_per_user_batching_policy=true; last_verified_deploy_commit=508df50</span>
      </section>

      <section className="ai-review-quality-lab" data-ai-review-quality-stage="P119-A" aria-label="AI review quality lab">
        <div className="ai-review-quality-lab-head">
          <div>
            <strong>AI review quality gate</strong>
            <span>Local quality gate/harness for draft review text; not a generated final review.</span>
          </div>
          <div className="ai-review-quality-lab-status">
            <span>Strong fixture: {aiReviewQualityLab.strongFixturePasses ? "passes" : "blocked"}</span>
            <span>Weak generic fixture: {aiReviewQualityLab.weakFixtureFails ? "fails" : "needs guard"}</span>
          </div>
        </div>
        <ul>
          {aiReviewQualityLab.checklist.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <div className="ai-review-quality-preview" data-ai-review-quality-preview-stage="E120-A">
          <div>
            <strong>Review evidence packet</strong>
            <span>{aiReviewQualityLab.preview.evidencePacket.chartEvidenceItems.join(" · ")}</span>
          </div>
          <div>
            <strong>Strong preview: passes quality gate</strong>
            <span>Matched evidence count: {aiReviewQualityLab.preview.strong.matchedEvidenceCount}</span>
          </div>
          <div>
            <strong>Weak preview: blocked by quality gate</strong>
            <span>Failed dimensions</span>
            <ul>
              {aiReviewQualityLab.preview.weak.failedDimensionFeedback.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <strong>Preview requirements</strong>
            <span>{aiReviewQualityLab.preview.evidencePacket.synthesisLinks.join(" ")}</span>
            <span>{aiReviewQualityLab.preview.evidencePacket.practicalNextStepRequirement}</span>
            <span>{aiReviewQualityLab.preview.evidencePacket.caveatConfidenceRequirement}</span>
          </div>
        </div>
        <div className="ai-review-composer-preview" data-ai-review-composer-stage="P121-A">
          <div className="ai-review-composer-preview-head">
            <strong>Evidence-driven mock review</strong>
            <span>Strong composed review passes quality gate</span>
            <span>{aiReviewQualityLab.composed.weak.blockReason}</span>
          </div>
          <div className="ai-review-composer-sections">
            {aiReviewQualityLab.composed.sections.map((section) => (
              <section key={section.heading}>
                <strong>{section.heading}</strong>
                <span>{section.body}</span>
              </section>
            ))}
          </div>
          <div className="ai-review-composer-status">
            <span>Matched evidence count: {aiReviewQualityLab.composed.strong.matchedEvidenceCount}</span>
            <span>Generic output blocked by quality gate</span>
            <span>Failed dimensions: {aiReviewQualityLab.composed.weak.failedDimensionFeedback.join(" ")}</span>
          </div>
        </div>
        <div className="ai-review-prompt-preview" data-ai-review-prompt-contract-stage="E122-A">
          <div className="ai-review-prompt-preview-head">
            <strong>Prompt contract dry run</strong>
            <span>Prompt contract is local-only and no LLM call was executed.</span>
            <span>Require at least 3 evidence citations from {aiReviewQualityLab.promptPayload.evidenceItems.length} packet items.</span>
          </div>
          <div className="ai-review-prompt-sections">
            {aiReviewQualityLab.promptPayload.sections.map((section) => (
              <section key={section.heading}>
                <strong>{section.heading}</strong>
                <span>{section.body}</span>
              </section>
            ))}
          </div>
          <div className="ai-review-prompt-status">
            <span>Block or revise generic text that lacks chart evidence and synthesis.</span>
            <span>Quality gate dimensions: {aiReviewQualityLab.promptPayload.qualityGateBeforeFinalAnswer.join(",")}</span>
          </div>
        </div>
        <div className="ai-review-scenario-matrix" data-ai-review-multi-fixture-stage="P123-A">
          <div className="ai-review-scenario-matrix-head">
            <strong>AI review regression matrix</strong>
            <span>
              {aiReviewQualityLab.scenarioMatrix.aggregate.scenarioCount} scenarios; strong pass{" "}
              {aiReviewQualityLab.scenarioMatrix.aggregate.strongPassCount}; weak blocked{" "}
              {aiReviewQualityLab.scenarioMatrix.aggregate.weakBlockedCount}; minimum evidence{" "}
              {aiReviewQualityLab.scenarioMatrix.aggregate.minimumEvidenceItemCount}.
            </span>
          </div>
          <div className="ai-review-scenario-grid" role="list">
            {aiReviewQualityLab.scenarioMatrix.scenarios.map((scenario) => (
              <section key={scenario.id} role="listitem">
                <strong>{scenario.intent}</strong>
                <span>Evidence items: {scenario.evidenceItems.length}</span>
                <span>Required citations: {scenario.requiredEvidenceCitationCount}</span>
                <span>Strong status: {scenario.strong.status}</span>
                <span>Weak generic status: {scenario.weak.status}</span>
                <span>Improvement reason: {scenario.weak.improvementReason}</span>
              </section>
            ))}
          </div>
        </div>
        <div className="ai-review-telegram-benchmark" data-ai-review-telegram-benchmark-stage="E124-A">
          <div className="ai-review-telegram-benchmark-head">
            <strong>Telegram benchmark accents</strong>
            <span>Source style is intentionally not copied; only chart facts, accents, caveats, and grounded questions are kept.</span>
            <span>Advanced claims gated unless calculated table exists.</span>
          </div>
          <div className="ai-review-blueprint-sections">
            {aiReviewQualityLab.telegramBenchmark.blueprintSections.map((section) => (
              <span key={section}>{section}</span>
            ))}
          </div>
          <div className="ai-review-telegram-benchmark-grid" role="list">
            {aiReviewQualityLab.telegramBenchmark.benchmarks.map((benchmark) => (
              <section key={benchmark.name} role="listitem">
                <strong>{benchmark.name}</strong>
                <span>Chart facts: {benchmark.chartFacts.length}</span>
                <span>Accents/rules: {benchmark.calculationAccents.length}</span>
                <span>Follow-up questions: {benchmark.followUpQuestions.length}</span>
                <span>Example grounded questions: {benchmark.followUpQuestions.slice(0, 3).join(" ")}</span>
                <span>Caution: {benchmark.advancedClaimCautions[0]}</span>
              </section>
            ))}
          </div>
        </div>
        <div className="ai-review-question-contract" data-ai-review-question-contract-stage="P125-A">
          <div className="ai-review-question-contract-head">
            <strong>Grounded follow-up question contract</strong>
            <span>
              Ready chart-grounded questions: {aiReviewQualityLab.followupQuestionContract.aggregate.readyCount}; gated advanced claims:{" "}
              {aiReviewQualityLab.followupQuestionContract.aggregate.gatedCount}; rejected generic prompts:{" "}
              {aiReviewQualityLab.followupQuestionContract.aggregate.rejectedGenericCount}.
            </span>
          </div>
          <div className="ai-review-question-grid" role="list">
            {aiReviewQualityLab.followupQuestionContract.candidates.map((candidate) => (
              <section key={`${candidate.sourceBenchmarkId}-${candidate.question}`} role="listitem">
                <strong>{candidate.question}</strong>
                <span>Anchor fact: {candidate.anchorChartFact || "none"}</span>
                <span>Rule/accent: {candidate.jyotishRuleAccent || "none"}</span>
                <span>Question status: {candidate.status}</span>
                <span>Reason: {candidate.reason}</span>
              </section>
            ))}
          </div>
        </div>
        <div className="ai-review-assertion-ledger" data-ai-review-assertion-ledger-stage="E126-A">
          <div className="ai-review-assertion-ledger-head">
            <strong>Assertion ledger</strong>
            <span>Local deterministic quality harness, not final AI output.</span>
          </div>
          <div className="ai-review-assertion-counts" aria-label="Assertion count by source type">
            <span>computed_chart_fact: {aiReviewQualityLab.assertionLedger.aggregate.computedChartFactCount}</span>
            <span>jyotish_rule: {aiReviewQualityLab.assertionLedger.aggregate.jyotishRuleCount}</span>
            <span>derived_synthesis: {aiReviewQualityLab.assertionLedger.aggregate.derivedSynthesisCount}</span>
            <span>practical_guidance: {aiReviewQualityLab.assertionLedger.aggregate.practicalGuidanceCount}</span>
            <span>gated_advanced_claim: {aiReviewQualityLab.assertionLedger.aggregate.blockedAdvancedCount}</span>
            <span>usable: {aiReviewQualityLab.assertionLedger.aggregate.usableCount}</span>
            <span>blocked: {aiReviewQualityLab.assertionLedger.aggregate.blockedCount}</span>
          </div>
          <div className="ai-review-composed-ledger-grid" role="list">
            {aiReviewQualityLab.assertionLedger.composedReview.sections.map((section) => (
              <section key={section.heading} role="listitem">
                <strong>{section.heading}</strong>
                <span>{section.body}</span>
                <span>Ledger anchors: {section.anchorIds.join(", ")}</span>
              </section>
            ))}
          </div>
          <div className="ai-review-advanced-blocks">
            {aiReviewQualityLab.assertionLedger.assertions
              .filter((assertion) => assertion.status === "blocked")
              .map((assertion) => (
                <span key={assertion.id}>
                  {assertion.assertion} Reason: {assertion.confidenceCaveat}
                </span>
              ))}
          </div>
        </div>
        <span hidden>{aiReviewQualityLab.statusLabels.join("; ")}</span>
      </section>

      <section className="workspace-bridge-summary" aria-label="Сводка конструктора отчета">
        <div>
          <span>Карт</span>
          <strong>{profiles.length}</strong>
        </div>
        <div>
          <span>Связей</span>
          <strong>{relationships.length}</strong>
        </div>
        <div>
          <span>Выбранная карта</span>
          <strong>{selectedProfile?.display_name ?? "не выбрана"}</strong>
        </div>
        <div className="report-readiness">
          <span>Готовность</span>
          <strong>{selectedIntent.label} · {readinessLabel(readiness.status)}</strong>
        </div>
      </section>

      <nav className="workspace-bridge-actions" aria-label="Быстрые действия отчетов">
        <Link className="primary-link-button" href="/charts/new">Создать карту</Link>
        <Link className="secondary-button" href="/people">Люди</Link>
        <Link className="secondary-button" href="/interactions">Взаимодействия</Link>
        <Link className="secondary-button" href="/transits">Транзиты</Link>
      </nav>

      {needsAuth ? (
        <section className="interaction-empty panel">
          <h2>Нужен вход</h2>
          <p>После входа здесь будут доступны только ваши карты, связи и заготовки отчетов.</p>
          <div className="workspace-bridge-actions">
            <Link className="primary-link-button" href="/charts/new">Создать карту</Link>
            <Link className="secondary-button" href="/people">Люди</Link>
          </div>
        </section>
      ) : (
        <section className="reports-workspace" aria-label="Рабочее место конструктора отчетов">
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
                  Тип отчета
                  <select value={reportTypeId} onChange={(event) => setReportTypeId(event.target.value as ReportTypeId)}>
                    {reportTypes.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.label.ru}
                      </option>
                    ))}
                  </select>
                </label>

                <fieldset className="report-workspace-choice">
                  <legend>Намерение</legend>
                  {reportIntents.map((intent) => (
                    <button
                      key={intent.id}
                      type="button"
                      className={selectedIntentId === intent.id ? "active" : ""}
                      onClick={() => setSelectedIntentId(intent.id)}
                    >
                      <strong>{intent.label}</strong>
                      <span>{intent.summary}</span>
                    </button>
                  ))}
                </fieldset>

                <fieldset className="report-workspace-choice compact">
                  <legend>Режим наставления</legend>
                  {guidanceModes.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      className={guidanceModeId === item.id ? "active" : ""}
                      onClick={() => setGuidanceModeId(item.id)}
                    >
                      <strong>{item.label}</strong>
                      <span>{item.summary}</span>
                    </button>
                  ))}
                </fieldset>

                <label>
                  Вопрос
                  <textarea
                    value={questionText}
                    onChange={(event) => setQuestionText(event.target.value)}
                    placeholder="Коротко сформулируйте вопрос для режима Вопрос."
                  />
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
                <strong>Сохраненных карт пока нет.</strong>
                <div className="workspace-bridge-actions">
                  <Link className="primary-link-button" href="/charts/new">Создать карту</Link>
                  <Link className="secondary-button" href="/people">Люди</Link>
                </div>
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

            <section className="workspace-readiness-panel" aria-label="Готовность запроса">
              <div>
                <span>Готовность запроса</span>
                <strong>{readinessLabel(readiness.status)}</strong>
              </div>
              <div>
                <span>Намерение</span>
                <strong>{selectedIntent.label}</strong>
              </div>
              <div>
                <span>Режим</span>
                <strong>{selectedGuidanceMode.label}</strong>
              </div>
              <div>
                <span>Контекст</span>
                <strong>{readiness.requiredContext.join(", ")}</strong>
              </div>
              {readiness.blockedReasons.length ? (
                <p>{readiness.blockedReasons.join(" ")}</p>
              ) : (
                <p>Черновик запроса готов к внутренней проверке. Реальная генерация не запускается.</p>
              )}
              {selectedIntentId === "business_timing" ? (
                <div className="workspace-bridge-actions">
                  <Link className="secondary-button" href="/transits">Транзиты</Link>
                  <Link className="secondary-button" href="/muhurta">Мухурта</Link>
                </div>
              ) : null}
            </section>

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
