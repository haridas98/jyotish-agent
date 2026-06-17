"use client";

import { useCallback, useEffect, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { deleteChartProfile, fetchCurrentUser, listChartProfiles, type ChartProfile } from "@/lib/api";

function formatTime(profile: ChartProfile) {
  if (!profile.birth_time) return "время неизвестно";
  return profile.birth_time.slice(0, 5);
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("ru-RU", { dateStyle: "short", timeStyle: "short" });
}

function profileMeta(profile: ChartProfile) {
  return `${profile.birth_date} · ${formatTime(profile)} · ${profile.place.label}`;
}

export default function ChartsPage() {
  const [profiles, setProfiles] = useState<ChartProfile[]>([]);
  const [status, setStatus] = useState("Загружаю карты...");
  const [needsAuth, setNeedsAuth] = useState(false);

  const loadProfiles = useCallback(async () => {
    try {
      const user = await fetchCurrentUser();
      if (!user) {
        setNeedsAuth(true);
        setStatus("Войдите, чтобы открыть кабинет карт.");
        return;
      }
      const rows = await listChartProfiles();
      setProfiles(rows);
      setNeedsAuth(false);
      setStatus(rows.length ? "" : "Сохранённых карт ещё нет.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось загрузить карты.");
    }
  }, []);

  useEffect(() => {
    void loadProfiles();
  }, [loadProfiles]);

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
          <span>Ваши сохранённые данные рождения.</span>
        </div>
        {!needsAuth ? <a className="primary-link-button" href="/charts/new">Создать карту</a> : null}
      </section>

      {status ? <div className="product-status">{status}</div> : null}

      {!needsAuth && profiles.length ? (
        <section className="charts-dashboard-list">
          {profiles.map((profile) => (
            <article className="chart-profile-card" key={profile.id}>
              <div>
                <strong>
                  {profile.display_name}
                  {profile.is_self_profile ? <em>моя карта</em> : null}
                </strong>
                <span>{profileMeta(profile)}</span>
                <small>
                  Обновлена {formatDateTime(profile.updated_at)} · {profile.timezone}
                </small>
              </div>
              <div className="chart-profile-card-actions">
                <a href={`/charts/${profile.id}`}>Открыть</a>
                <a href={`/charts/${profile.id}/edit`}>Редактировать</a>
                <button type="button" onClick={() => void handleDelete(profile)}>Удалить</button>
              </div>
            </article>
          ))}
        </section>
      ) : null}

      {!needsAuth && !profiles.length && !status ? (
        <section className="charts-empty-state">
          <strong>Карт ещё нет</strong>
          <a className="primary-link-button" href="/charts/new">Создать первую карту</a>
        </section>
      ) : null}
    </ProductShell>
  );
}
