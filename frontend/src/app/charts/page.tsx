"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { D1_WORKBENCH_POLISH_STAGE, D1_WORKBENCH_SMOKE_INTERNAL_MARKER, D1_WORKBENCH_SMOKE_ROUTE } from "@/astrology/d1-workbench-smoke-fixture";
import { deleteChartProfile, fetchCurrentUser, listChartProfiles, type ChartProfile } from "@/lib/api";

const quickActions = [
  { label: "Создать карту", href: "/charts/new", kind: "primary" },
  { label: "Launch status", href: "/launch-status" },
  { label: "Люди", href: "/people" },
  { label: "Обзор", href: "/reports" },
  { label: "Взаимодействия", href: "/interactions" },
  { label: "Транзиты", href: "/transits" },
];

function formatTime(profile: ChartProfile) {
  if (!profile.birth_time) return "время не указано";
  return profile.birth_time.slice(0, 5);
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("ru-RU", { dateStyle: "short", timeStyle: "short" });
}

function genderLabel(gender?: ChartProfile["gender"]) {
  if (gender === "male") return "мужской";
  if (gender === "female") return "женский";
  return "пол не указан";
}

function profileMeta(profile: ChartProfile) {
  return `${profile.birth_date} · ${formatTime(profile)} · ${profile.place.label}`;
}

function workflowStateLabel(profile: ChartProfile) {
  const state = profile.calculation_state;
  if (state?.status === "complete") return "расчет готов";
  if (state?.status === "stale") return "нужен пересчет";
  if (state?.status === "failed") return "расчет не выполнен";
  if (state?.status === "calculation_requested") return "расчет запрошен";
  return "расчет не сохранен";
}

function latestProfile(profiles: ChartProfile[]) {
  return [...profiles].sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at))[0] ?? null;
}

function DemoD1Link({ label }: { label: string }) {
  return (
    <a
      className="secondary-button"
      href={D1_WORKBENCH_SMOKE_ROUTE}
      data-chart-demo-path={D1_WORKBENCH_SMOKE_ROUTE}
      data-chart-detail-smoke-fixture={D1_WORKBENCH_SMOKE_INTERNAL_MARKER}
      data-chart-detail-polish-stage={D1_WORKBENCH_POLISH_STAGE}
      aria-label={`${label}: пример D1, только просмотр`}
    >
      {label}
      <span hidden>P107-A E108-A read-only D1 demo path</span>
    </a>
  );
}

export default function ChartsPage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [status, setStatus] = useState("Загружаю карты...");
  const [needsAuth, setNeedsAuth] = useState(false);
  const [hasLoadError, setHasLoadError] = useState(false);

  const loadProfiles = useCallback(async () => {
    try {
      setHasLoadError(false);
      const user = await fetchCurrentUser();
      if (!user) {
        setNeedsAuth(true);
        setProfiles([]);
        setStatus("");
        return;
      }
      const rows = await listChartProfiles();
      setProfiles(rows);
      setNeedsAuth(false);
      setStatus("");
    } catch (error) {
      setNeedsAuth(false);
      setProfiles([]);
      setHasLoadError(true);
      setStatus("Не удалось загрузить сохранённые карты. Можно открыть пример D1 без сохранения данных.");
    }
  }, []);

  useEffect(() => {
    void loadProfiles();
  }, [loadProfiles]);

  const selfProfile = useMemo(() => profiles.find((profile) => profile.is_self_profile) ?? null, [profiles]);
  const lastUpdated = useMemo(() => latestProfile(profiles), [profiles]);
  const readiness = profiles.length
    ? selfProfile
      ? "Кабинет готов"
      : "Нужна моя карта"
    : needsAuth
      ? "Требуется вход"
      : "Карт пока нет";

  async function handleDelete(profile: ChartProfile) {
    if (!window.confirm(`Удалить карту "${profile.display_name}"?`)) return;
    await deleteChartProfile(profile.id);
    await loadProfiles();
  }

  return (
    <ProductShell active="charts">
      <section className="charts-dashboard-head">
        <div>
          <h1>Кабинет карт</h1>
          <span>Сохранённые карты, связи и рабочие переходы.</span>
        </div>
        <nav className="charts-quick-actions" aria-label="Быстрые действия кабинета карт">
          {quickActions.map((action) => (
            <a className={action.kind === "primary" ? "primary-link-button" : "secondary-button"} href={action.href} key={action.href}>
              {action.label}
            </a>
          ))}
        </nav>
      </section>

      <section className="charts-summary-grid" aria-label="Сводка кабинета карт">
        <div>
          <span>Всего карт</span>
          <strong>{profiles.length}</strong>
        </div>
        <div>
          <span>Моя карта</span>
          <strong>{selfProfile ? selfProfile.display_name : "не выбрана"}</strong>
        </div>
        <div>
          <span>Последнее обновление</span>
          <strong>{lastUpdated ? formatDateTime(lastUpdated.updated_at) : "нет данных"}</strong>
        </div>
        <div>
          <span>Статус</span>
          <strong>{readiness}</strong>
        </div>
      </section>

      {status ? <div className="product-status">{status}</div> : null}

      {needsAuth ? (
        <section className="charts-empty-state">
          <div>
            <strong>Войдите в аккаунт</strong>
            <span>После входа здесь появятся ваши сохранённые карты.</span>
          </div>
          <a className="primary-link-button" href="/charts/new">Создать карту</a>
          <DemoD1Link label="Посмотреть пример" />
        </section>
      ) : null}

      {hasLoadError && !profiles.length ? (
        <section className="charts-empty-state" data-chart-load-error-fallback="true">
          <div>
            <strong>Сохранённые карты временно недоступны</strong>
            <span>Пример D1 можно открыть без сохранения данных и без записи в аккаунт.</span>
          </div>
          <div className="charts-empty-actions">
            <DemoD1Link label="Открыть пример D1" />
            <a className="secondary-button" href="/charts/new">Создать карту</a>
          </div>
        </section>
      ) : null}

      {!needsAuth && !status && !profiles.length ? (
        <section className="charts-empty-state">
          <div>
            <strong>Карт пока нет</strong>
            <span>Создайте первую карту или откройте раздел людей для будущих связей.</span>
          </div>
          <div className="charts-empty-actions">
            <a className="primary-link-button" href="/charts/new">Создать карту</a>
            <DemoD1Link label="Открыть пример D1" />
            <a className="secondary-button" href="/people">Люди</a>
            <a className="secondary-button" href="/transits">Транзиты</a>
          </div>
        </section>
      ) : null}

      {!needsAuth && profiles.length ? (
        <section className="charts-dashboard-list" aria-label="Сохранённые карты">
          {profiles.map((profile) => (
            <article className="chart-profile-card" key={profile.id}>
              <div>
                <strong>
                  {profile.display_name}
                  {profile.is_self_profile ? <em>моя карта</em> : null}
                </strong>
                <span>{profileMeta(profile)}</span>
                <small>
                  {genderLabel(profile.gender)} · создана {formatDateTime(profile.created_at)} · обновлена {formatDateTime(profile.updated_at)} · {profile.timezone}
                </small>
                <small>{workflowStateLabel(profile)}</small>
              </div>
              <div className="chart-profile-card-actions">
                <a href={`/charts/${profile.id}`}>Открыть</a>
                <a href={`/charts/${profile.id}/edit`}>Редактировать</a>
                <a href="/reports">Обзор</a>
                <a href="/interactions">Взаимодействия</a>
                <button type="button" onClick={() => void handleDelete(profile)}>Удалить</button>
              </div>
            </article>
          ))}
        </section>
      ) : null}
    </ProductShell>
  );
}
