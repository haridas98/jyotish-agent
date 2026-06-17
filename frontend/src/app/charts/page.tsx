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

function genderLabel(gender?: ChartProfile["gender"]) {
  if (gender === "male") return "мужской";
  if (gender === "female") return "женский";
  return "пол не указан";
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
        setProfiles([]);
        setStatus("Войдите, чтобы открыть кабинет карт.");
        return;
      }
      const rows = await listChartProfiles();
      setProfiles(rows);
      setNeedsAuth(false);
      setStatus("");
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
          <span>Сохранённые карты текущего пользователя.</span>
        </div>
        {!needsAuth ? <a className="primary-link-button" href="/charts/new">Создать карту</a> : null}
      </section>

      {status ? <div className="product-status">{status}</div> : null}

      {!needsAuth && !status && !profiles.length ? (
        <section className="charts-empty-state">
          <div>
            <strong>Карт ещё нет</strong>
            <span>Создайте первую карту, затем её можно будет открыть, изменить или удалить.</span>
          </div>
          <a className="primary-link-button" href="/charts/new">Создать карту</a>
        </section>
      ) : null}

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
                  {genderLabel(profile.gender)} · обновлена {formatDateTime(profile.updated_at)} · {profile.timezone}
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
    </ProductShell>
  );
}
