"use client";

import { useEffect, useState } from "react";
import { GenerationJobsPanel } from "@/app/generation-jobs-ui";
import { HistoryList } from "@/app/analysis-history-ui";
import { ProductShell } from "@/app/product-shell";
import { HelpTerm, HouseTerms, VargaTerms, type HelpItem } from "@/app/relationship-help";
import {
  fetchAnalysisHistory,
  listChartProfileRelationships,
  type AnalysisHistoryItem,
  type ChartProfileRelationship,
} from "@/lib/api";
import { relationshipRoleDefinitions, relationshipRoleFor } from "@/lib/relationshipRoles";

type CompatibilityRoleView = {
  label: string;
  focus: string;
  houses: string[];
  vargas: string[];
};

const compatibilityRoleViews: Record<string, CompatibilityRoleView> = Object.fromEntries(
  relationshipRoleDefinitions.map((role) => [
    role.key,
    {
      label: role.label,
      focus: role.focus,
      houses: role.houses.map(String),
      vargas: role.vargas,
    },
  ]),
);

function roleView(role: string): CompatibilityRoleView {
  const sharedRole = relationshipRoleFor(role);
  return compatibilityRoleViews[sharedRole.key] ?? compatibilityRoleViews.other;
}

const statusHelp: Record<string, HelpItem> = {
  private: {
    title: "Личная пометка",
    text: "Связь хранится только у вас. Второй человек не видит её и не получает уведомление.",
  },
  requested: {
    title: "Ожидает подтверждения",
    text: "Запрос отправлен зарегистрированному пользователю. До принятия это не считается общей подтверждённой связью.",
  },
  accepted: {
    title: "Подтверждённая связь",
    text: "Оба зарегистрированных пользователя подтвердили связь и видят её у себя.",
  },
  declined: {
    title: "Отклонено",
    text: "Пользователь не подтвердил связь. Такой статус нельзя подавать как взаимное согласие.",
  },
  blocked: {
    title: "Заблокировано",
    text: "Пользователь запретил повторные запросы по этой связи.",
  },
};

function relationshipStatusLabel(status: string): string {
  if (status === "accepted") return "подтверждено";
  if (status === "requested") return "ожидает подтверждения";
  if (status === "declined") return "отклонено";
  if (status === "blocked") return "заблокировано";
  return "личная пометка";
}

function RoleTerm({ role }: { role: CompatibilityRoleView }) {
  return (
    <HelpTerm item={{ title: role.label, text: `Ракурс чтения: ${role.focus}. Дома и D-карты ниже выбираются именно под эту роль.` }}>
      {role.label}
    </HelpTerm>
  );
}

function StatusTerm({ status }: { status: string }) {
  return (
    <HelpTerm item={statusHelp[status] ?? statusHelp.private}>
      <em className={`interaction-status ${status}`}>{relationshipStatusLabel(status)}</em>
    </HelpTerm>
  );
}

function profileName(profile: ChartProfileRelationship["profile"]): string {
  return profile?.display_name ?? "Карта";
}

function profileMeta(profile: ChartProfileRelationship["profile"]): string {
  return [profile?.birth_date, profile?.place_label].filter(Boolean).join(" · ") || "данные карты";
}

function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => reject(new Error(`${label}: API не ответил вовремя`)), ms);
    promise
      .then((value) => {
        window.clearTimeout(timer);
        resolve(value);
      })
      .catch((error) => {
        window.clearTimeout(timer);
        reject(error);
      });
  });
}

function friendlyHistoryError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  if (/401|403|auth|credential|forbidden|permission/i.test(message)) {
    return "Войдите в аккаунт, чтобы увидеть свои обзоры совместимости и сохранённые связи.";
  }
  if (/Unexpected token|JSON|API returned|fetch|network/i.test(message)) {
    return "Не удалось загрузить историю. Проверьте, что API запущен, и обновите страницу.";
  }
  return message || "Ошибка загрузки истории";
}

export default function CompatibilityPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [relationships, setRelationships] = useState<ChartProfileRelationship[]>([]);
  const [status, setStatus] = useState("Загружаю историю совместимости...");

  useEffect(() => {
    let mounted = true;
    const reloadOnAuthChanged = () => window.location.reload();
    window.addEventListener("jyotish-auth-changed", reloadOnAuthChanged);
    Promise.allSettled([
      withTimeout(fetchAnalysisHistory({ kind: "compatibility_codex_cli", limit: 60 }), 7000, "История"),
      withTimeout(listChartProfileRelationships(), 7000, "Связи"),
    ])
      .then(([historyResult, relationshipResult]) => {
        if (!mounted) return;
        const historyItems = historyResult.status === "fulfilled" ? historyResult.value : [];
        const relationshipItems = relationshipResult.status === "fulfilled" ? relationshipResult.value : [];
        setItems(historyItems);
        setRelationships(relationshipItems.filter((relationship) => !["declined", "blocked"].includes(relationship.link_status)));
        if (historyResult.status === "rejected" && relationshipResult.status === "rejected") {
          setStatus(friendlyHistoryError(historyResult.reason));
          return;
        }
        setStatus(
          historyItems.length || relationshipItems.length
            ? `${historyItems.length} сохранённых обзоров, ${relationshipItems.length} связей`
            : "История пока пустая",
        );
      })
      .catch((error) => {
        if (!mounted) return;
        setStatus(friendlyHistoryError(error));
      });
    return () => {
      mounted = false;
      window.removeEventListener("jyotish-auth-changed", reloadOnAuthChanged);
    };
  }, []);

  return (
    <ProductShell active="compatibility">
      <header className="product-page-head">
        <div>
          <h1>Совместимость</h1>
          <p>История парных обзоров и продолжение диалогов по сохранённым картам.</p>
        </div>
        <a className="primary-link-button" href="/?analysis=compatibility#reports">Создать обзор</a>
      </header>
      <div className="product-status">{status}</div>
      <GenerationJobsPanel basePath="/compatibility" kind="compatibility_codex_cli" title="AI-задачи совместимости" />

      <section className="beginner-context-panel" aria-label="Как новичку читать совместимость">
        <div>
          <strong>1. Сначала выберите пару</strong>
          <span>Пара берётся из сохранённых карт и роли человека: партнёр, отец, мать, руководитель или другой ракурс.</span>
        </div>
        <div>
          <strong>2. Откройте паспорт пары</strong>
          <span>Там видны две карты, нужные дома, D-карты и расчётная сводка перед AI-разбором.</span>
        </div>
        <div>
          <strong>3. Продолжайте диалог</strong>
          <span>После AI-разбора история сохраняется, и можно задавать уточняющие вопросы по этой же паре.</span>
        </div>
      </section>

      <section className="compatibility-saved-role-context" aria-label="Расчётный минимум совместимости">
        <div className="compatibility-saved-role-head">
          <div>
            <span>Минимум перед AI-разбором</span>
            <strong>Что астролог проверяет первым</strong>
          </div>
          <small>Эти пункты должны быть понятны даже без сохранённых пар.</small>
        </div>
        <div className="compatibility-saved-role-grid">
          <div>
            <span>Брак / партнёрство</span>
            <strong><HouseTerms houses={["1", "7", "2", "8", "12"]} /></strong>
          </div>
          <div>
            <span>Ключевые D-карты</span>
            <strong><VargaTerms vargas={["D1", "D9", "D7", "D12"]} /></strong>
          </div>
          <div>
            <span>Родители</span>
            <strong><HouseTerms houses={["4", "9"]} /> · <VargaTerms vargas={["D12", "D60"]} /></strong>
          </div>
          <div>
            <span>Конфликты</span>
            <strong><HouseTerms houses={["6", "8"]} /> · <VargaTerms vargas={["D6", "D30"]} /></strong>
          </div>
        </div>
      </section>

      {relationships.length ? (
        <section className="compatibility-pair-launcher" aria-label="Сохранённые пары и роли">
          <div className="compatibility-pair-launcher-head">
            <div>
              <h2>Сохранённые пары и роли</h2>
              <p>Открывайте совместимость сразу с нужным ракурсом: партнёр, отец, мать, руководитель, оппонент и т.д.</p>
            </div>
            <a className="secondary-button" href="/interactions">
              Управлять связями
            </a>
          </div>
          <div className="compatibility-pair-launcher-grid">
            {relationships.map((relationship) => {
              const role = roleView(relationship.role);
              return (
                <article className="compatibility-pair-card" key={relationship.id}>
                  <div className="compatibility-pair-card-head">
                    <div>
                      <span><RoleTerm role={role} /></span>
                      <strong>
                        {profileName(relationship.profile)} → {profileName(relationship.related_profile)}
                      </strong>
                      <small>
                        {profileMeta(relationship.profile)} / {profileMeta(relationship.related_profile)}
                      </small>
                    </div>
                    <StatusTerm status={relationship.link_status} />
                  </div>
                  <div className="compatibility-pair-focus">
                    <div>
                      <span>Ракурс</span>
                      <strong>{role.focus}</strong>
                    </div>
                    <div>
                      <span>Дома</span>
                      <strong><HouseTerms houses={role.houses} /></strong>
                    </div>
                    <div>
                      <span>D-карты</span>
                      <strong><VargaTerms vargas={role.vargas} /></strong>
                    </div>
                  </div>
                  <p>
                    При запуске эти данные передаются в пакет разбора: обе карты, роль второго человека,
                    нужные дома и D-карты.
                  </p>
                  <div className="compatibility-actions">
                    <a className="secondary-button" href={`/compatibility/pair/${relationship.id}`}>
                      Паспорт пары
                    </a>
                    <a className="primary-link-button" href={`/?analysis=compatibility&relationship=${relationship.id}#reports`}>
                    Открыть разбор
                    </a>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      ) : null}

      <HistoryList items={items} basePath="/compatibility" emptyText="Обзоров совместимости ещё нет." />
    </ProductShell>
  );
}
