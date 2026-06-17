"use client";

import { FormEvent, useMemo, useState } from "react";
import { createChartProfile, updateChartProfile, type ChartProfile } from "@/lib/api";

type ChartProfileFormProps = {
  mode: "create" | "edit";
  profile?: ChartProfile;
  onSaved: (profile: ChartProfile) => void;
};

type ChartProfileDraft = {
  displayName: string;
  birthDate: string;
  birthTime: string;
  birthTimeAccuracy: string;
  placeName: string;
  timezone: string;
  latitude: string;
  longitude: string;
  gender: "male" | "female" | "unknown";
  notes: string;
  isSelfProfile: boolean;
};

function draftFromProfile(profile?: ChartProfile): ChartProfileDraft {
  return {
    displayName: profile?.display_name ?? "",
    birthDate: profile?.birth_date ?? "",
    birthTime: profile?.birth_time?.slice(0, 5) ?? "",
    birthTimeAccuracy: profile?.birth_time_accuracy ?? "exact",
    placeName: profile?.place.label ?? "",
    timezone: profile?.timezone ?? "",
    latitude: profile?.place.latitude === undefined ? "" : String(profile.place.latitude),
    longitude: profile?.place.longitude === undefined ? "" : String(profile.place.longitude),
    gender: profile?.gender ?? "unknown",
    notes: profile?.notes ?? "",
    isSelfProfile: profile?.is_self_profile ?? false,
  };
}

function numberOrUndefined(value: string) {
  const normalized = value.trim().replace(",", ".");
  if (!normalized) return undefined;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : Number.NaN;
}

function validateDraft(draft: ChartProfileDraft) {
  if (!draft.displayName.trim()) return "Укажите имя карты.";
  if (!draft.birthDate.trim()) return "Укажите дату рождения.";
  if (Number.isNaN(Date.parse(`${draft.birthDate}T00:00:00`))) return "Дата рождения некорректна.";
  if (!draft.birthTime.trim() && draft.birthTimeAccuracy !== "unknown") {
    return "Укажите время рождения или выберите точность времени «неизвестно».";
  }
  if (draft.birthTime.trim() && !/^\d{2}:\d{2}$/.test(draft.birthTime.trim())) {
    return "Время должно быть в формате HH:mm.";
  }
  if (!draft.placeName.trim()) return "Укажите город рождения.";

  const latitude = numberOrUndefined(draft.latitude);
  const longitude = numberOrUndefined(draft.longitude);
  if (Number.isNaN(latitude) || Number.isNaN(longitude)) return "Координаты должны быть числами.";
  if ((latitude === undefined) !== (longitude === undefined)) return "Широту и долготу нужно указывать вместе.";
  if (latitude !== undefined && (latitude < -90 || latitude > 90)) return "Широта должна быть от -90 до 90.";
  if (longitude !== undefined && (longitude < -180 || longitude > 180)) return "Долгота должна быть от -180 до 180.";
  if (latitude !== undefined && !draft.timezone.trim()) return "Для ручных координат нужен часовой пояс.";
  return "";
}

export function ChartProfileForm({ mode, profile, onSaved }: ChartProfileFormProps) {
  const [draft, setDraft] = useState(() => draftFromProfile(profile));
  const [status, setStatus] = useState("");
  const [saving, setSaving] = useState(false);
  const title = mode === "create" ? "Новая карта" : "Редактирование карты";
  const submitLabel = mode === "create" ? "Создать карту" : "Сохранить";

  const payload = useMemo(() => {
    const latitude = numberOrUndefined(draft.latitude);
    const longitude = numberOrUndefined(draft.longitude);
    const birthTime = draft.birthTime.trim();
    return {
      display_name: draft.displayName.trim(),
      birth_date: draft.birthDate.trim(),
      birth_time: birthTime,
      birth_time_accuracy: draft.birthTimeAccuracy,
      gender: draft.gender,
      place_name: draft.placeName.trim(),
      notes: draft.notes.trim(),
      is_self_profile: draft.isSelfProfile,
      ...(draft.timezone.trim() ? { timezone: draft.timezone.trim() } : {}),
      ...(latitude !== undefined ? { latitude } : {}),
      ...(longitude !== undefined ? { longitude } : {}),
    };
  }, [draft]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const error = validateDraft(draft);
    if (error) {
      setStatus(error);
      return;
    }

    setSaving(true);
    setStatus("Сохраняю...");
    try {
      const saved = mode === "create" ? await createChartProfile(payload) : await updateChartProfile(profile!.id, payload);
      setStatus("Сохранено.");
      onSaved(saved);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось сохранить карту.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="chart-profile-form" onSubmit={handleSubmit}>
      <div className="chart-profile-form-head">
        <div>
          <h2>{title}</h2>
          <span>Данные рождения хранятся отдельно от логина и используются для расчётов карт.</span>
        </div>
      </div>

      <div className="chart-profile-form-grid">
        <label>
          <span>Имя карты</span>
          <input value={draft.displayName} onChange={(event) => setDraft({ ...draft, displayName: event.target.value })} />
        </label>
        <label>
          <span>Дата рождения</span>
          <input type="date" value={draft.birthDate} onChange={(event) => setDraft({ ...draft, birthDate: event.target.value })} />
        </label>
        <label>
          <span>Время рождения</span>
          <input type="time" value={draft.birthTime} onChange={(event) => setDraft({ ...draft, birthTime: event.target.value })} />
        </label>
        <label>
          <span>Точность времени</span>
          <select value={draft.birthTimeAccuracy} onChange={(event) => setDraft({ ...draft, birthTimeAccuracy: event.target.value })}>
            <option value="exact">Точное</option>
            <option value="approximate">Примерное</option>
            <option value="unknown">Неизвестно</option>
          </select>
        </label>
        <label>
          <span>Пол</span>
          <select value={draft.gender} onChange={(event) => setDraft({ ...draft, gender: event.target.value as ChartProfileDraft["gender"] })}>
            <option value="unknown">Не указан</option>
            <option value="male">Мужской</option>
            <option value="female">Женский</option>
          </select>
        </label>
        <label className="wide">
          <span>Место рождения</span>
          <input value={draft.placeName} onChange={(event) => setDraft({ ...draft, placeName: event.target.value })} placeholder="Sterlitamak, Bashkortostan, RU" />
        </label>
        <label>
          <span>Часовой пояс</span>
          <input value={draft.timezone} onChange={(event) => setDraft({ ...draft, timezone: event.target.value })} placeholder="Asia/Yekaterinburg" />
        </label>
        <label>
          <span>Широта</span>
          <input value={draft.latitude} onChange={(event) => setDraft({ ...draft, latitude: event.target.value })} />
        </label>
        <label>
          <span>Долгота</span>
          <input value={draft.longitude} onChange={(event) => setDraft({ ...draft, longitude: event.target.value })} />
        </label>
        <label className="wide">
          <span>Заметки</span>
          <textarea value={draft.notes} onChange={(event) => setDraft({ ...draft, notes: event.target.value })} rows={4} />
        </label>
      </div>

      <label className="chart-profile-checkbox">
        <input type="checkbox" checked={draft.isSelfProfile} onChange={(event) => setDraft({ ...draft, isSelfProfile: event.target.checked })} />
        <span>Это моя основная карта</span>
      </label>

      <div className="chart-profile-form-actions">
        <button className="primary-button" type="submit" disabled={saving}>
          {submitLabel}
        </button>
        <a className="secondary-button" href="/charts">К списку</a>
      </div>
      {status ? <p className="chart-profile-status">{status}</p> : null}
    </form>
  );
}
