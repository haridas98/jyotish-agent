"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ProductShell } from "@/app/product-shell";
import {
  calculateSavedProfile,
  fetchChartProfile,
  fetchJyotishSettings,
  type ChartProfile,
  type JyotishUserSettings,
} from "@/lib/api";

function profileIdFromParams(value: string | string[] | undefined) {
  const raw = Array.isArray(value) ? value[0] : value;
  const parsed = Number(raw);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

function formatTime(profile: ChartProfile) {
  return profile.birth_time ? profile.birth_time.slice(0, 5) : "время неизвестно";
}

function genderLabel(gender?: ChartProfile["gender"]) {
  if (gender === "male") return "мужской";
  if (gender === "female") return "женский";
  return "не указан";
}

function timeAccuracyLabel(value: string) {
  if (value === "exact") return "точное";
  if (value === "approximate") return "примерное";
  if (value === "unknown") return "неизвестно";
  return value;
}

export default function ChartDetailPage() {
  const params = useParams<{ id: string }>();
  const profileId = profileIdFromParams(params.id);
  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [userSettings, setUserSettings] = useState<JyotishUserSettings | null>(null);
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
        const settings = await fetchJyotishSettings();
        if (!mounted) return;
        setProfile(row);
        setUserSettings(settings);
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
    setStatus("Сохраняю расчёт...");
    try {
      await calculateSavedProfile(profile.id);
      const updated = await fetchChartProfile(profile.id);
      setProfile(updated);
      setStatus("Расчёт сохранён.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось сохранить расчёт.");
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
            <div><dt>Дата рождения</dt><dd>{profile.birth_date}</dd></div>
            <div><dt>Время рождения</dt><dd>{formatTime(profile)}</dd></div>
            <div><dt>Точность времени</dt><dd>{timeAccuracyLabel(profile.birth_time_accuracy)}</dd></div>
            <div><dt>Пол</dt><dd>{genderLabel(profile.gender)}</dd></div>
            <div><dt>Место рождения</dt><dd>{profile.place.label}</dd></div>
            <div><dt>Широта</dt><dd>{profile.place.latitude}</dd></div>
            <div><dt>Долгота</dt><dd>{profile.place.longitude}</dd></div>
            <div><dt>Часовой пояс</dt><dd>{profile.timezone}</dd></div>
            <div><dt>Создана</dt><dd>{new Date(profile.created_at).toLocaleString("ru-RU")}</dd></div>
            <div><dt>Обновлена</dt><dd>{new Date(profile.updated_at).toLocaleString("ru-RU")}</dd></div>
            <div><dt>Расчёт</dt><dd>{profile.latest_calculation?.status ?? "ещё не сохранён"}</dd></div>
            <div><dt>Версия расчёта</dt><dd>{profile.latest_calculation?.calculation_version ?? "нет"}</dd></div>
          </dl>

          <section className="chart-calculation-placeholder">
            <strong>Расчётный блок</strong>
            <span>
              Интерпретации на этом этапе не добавлены. Здесь фиксируется статус последнего сохранённого расчёта карты.
            </span>
            {profile.latest_calculation ? (
              <small>
                Статус: {profile.latest_calculation.status}; грах: {profile.latest_calculation.graha_count}; обновлён {new Date(profile.latest_calculation.updated_at).toLocaleString("ru-RU")}.
              </small>
            ) : (
              <small>Расчёт ещё не создавался.</small>
            )}
          </section>

          {userSettings ? (
            <section className="chart-settings-summary">
              <div>
                <strong>Calculation Settings</strong>
                <dl>
                  <div><dt>ayanamsa</dt><dd>{userSettings.calculation.ayanamsa}</dd></div>
                  <div><dt>zodiacType</dt><dd>{userSettings.calculation.zodiacType}</dd></div>
                  <div><dt>houseSystem</dt><dd>{userSettings.calculation.houseSystem}</dd></div>
                  <div><dt>nodeType</dt><dd>{userSettings.calculation.nodeType}</dd></div>
                  <div><dt>calculationProfile</dt><dd>{userSettings.calculation.calculationProfile}</dd></div>
                  <div><dt>D-карты</dt><dd>{userSettings.calculation.divisionalChartsEnabled.join(", ")}</dd></div>
                </dl>
              </div>
              <div>
                <strong>Display Settings</strong>
                <dl>
                  <div><dt>chartStyle</dt><dd>{userSettings.display.chartStyle}</dd></div>
                  <div><dt>language</dt><dd>{userSettings.display.language}</dd></div>
                  <div><dt>terminologyMode</dt><dd>{userSettings.display.terminologyMode}</dd></div>
                  <div><dt>degreeFormat</dt><dd>{userSettings.display.degreeFormat}</dd></div>
                </dl>
              </div>
            </section>
          ) : null}

          {profile.notes ? (
            <section className="chart-notes-panel">
              <strong>Заметки</strong>
              <p>{profile.notes}</p>
            </section>
          ) : null}

          <div className="chart-detail-actions">
            <a className="primary-link-button" href={`/?profile=${profile.id}#chart`}>Открыть рабочую карту</a>
            <a className="secondary-button" href={`/charts/${profile.id}/edit`}>Редактировать</a>
            <button type="button" className="secondary-button" onClick={() => void handleCalculate()}>Сохранить расчёт</button>
            <a className="secondary-button" href="/charts">К списку</a>
          </div>
        </section>
      ) : null}
    </ProductShell>
  );
}
