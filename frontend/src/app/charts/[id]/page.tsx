"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ProductShell } from "@/app/product-shell";
import { calculateSavedProfile, fetchChartProfile, type ChartProfile } from "@/lib/api";

function profileIdFromParams(value: string | string[] | undefined) {
  const raw = Array.isArray(value) ? value[0] : value;
  const parsed = Number(raw);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

function formatTime(profile: ChartProfile) {
  return profile.birth_time ? profile.birth_time.slice(0, 5) : "время неизвестно";
}

export default function ChartDetailPage() {
  const params = useParams<{ id: string }>();
  const profileId = profileIdFromParams(params.id);
  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [status, setStatus] = useState("Загружаю карту...");

  useEffect(() => {
    let mounted = true;
    async function loadProfile() {
      if (!profileId) {
        setStatus("Карта не найдена.");
        return;
      }
      try {
        const row = await fetchChartProfile(profileId);
        if (!mounted) return;
        setProfile(row);
        setStatus("");
      } catch (error) {
        if (!mounted) return;
        setStatus(error instanceof Error ? error.message : "Не удалось открыть карту.");
      }
    }
    void loadProfile();
    return () => {
      mounted = false;
    };
  }, [profileId]);

  async function handleCalculate() {
    if (!profile) return;
    setStatus("Считаю карту...");
    try {
      await calculateSavedProfile(profile.id);
      const updated = await fetchChartProfile(profile.id);
      setProfile(updated);
      setStatus("Расчёт сохранён.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось рассчитать карту.");
    }
  }

  return (
    <ProductShell active="charts">
      {status ? <div className="product-status">{status}</div> : null}

      {profile ? (
        <section className="chart-detail-panel">
          <div className="chart-detail-head">
            <div>
              <h1>{profile.display_name}</h1>
              <span>{profile.birth_date} · {formatTime(profile)} · {profile.place.label}</span>
            </div>
            {profile.is_self_profile ? <em>моя карта</em> : null}
          </div>

          <dl className="chart-detail-grid">
            <div><dt>Дата</dt><dd>{profile.birth_date}</dd></div>
            <div><dt>Время</dt><dd>{formatTime(profile)}</dd></div>
            <div><dt>Точность</dt><dd>{profile.birth_time_accuracy}</dd></div>
            <div><dt>Место</dt><dd>{profile.place.label}</dd></div>
            <div><dt>Широта</dt><dd>{profile.place.latitude}</dd></div>
            <div><dt>Долгота</dt><dd>{profile.place.longitude}</dd></div>
            <div><dt>Часовой пояс</dt><dd>{profile.timezone}</dd></div>
            <div><dt>Расчёт</dt><dd>{profile.latest_calculation?.status ?? "ещё не сохранён"}</dd></div>
          </dl>

          <div className="chart-detail-actions">
            <a className="primary-link-button" href={`/?profile=${profile.id}#chart`}>Открыть рабочую карту</a>
            <a className="secondary-button" href={`/charts/${profile.id}/edit`}>Редактировать</a>
            <button type="button" className="secondary-button" onClick={() => void handleCalculate()}>Сохранить расчёт</button>
          </div>
        </section>
      ) : null}
    </ProductShell>
  );
}
