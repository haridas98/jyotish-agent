"use client";

import { FormEvent, useEffect, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import {
  fetchJyotishSettings,
  updateJyotishSettings,
  type JyotishCalculationSettings,
  type JyotishDisplaySettings,
  type JyotishUserSettings,
} from "@/lib/api";

const DEFAULT_CALCULATION: JyotishCalculationSettings = {
  ayanamsa: "lahiri",
  zodiacType: "sidereal",
  houseSystem: "whole_sign",
  nodeType: "mean",
  calculationProfile: "gaudiya_default",
  divisionalChartsEnabled: ["D1", "D9"],
  defaultDivisionalChart: "D1",
  timezoneMode: "birth_place_timezone",
};

const DEFAULT_DISPLAY: JyotishDisplaySettings = {
  chartStyle: "north_indian",
  language: "ru",
  terminologyMode: "mixed",
  degreeFormat: "dms",
  showSanskritNames: true,
  showTransliteration: true,
  themeMode: "system",
};

const DIVISIONAL_CHARTS = ["D1", "D9", "D10", "D60"] as const;

function toggleChart(settings: JyotishCalculationSettings, chart: string): JyotishCalculationSettings {
  const enabled = new Set(settings.divisionalChartsEnabled);
  if (enabled.has(chart)) {
    enabled.delete(chart);
  } else {
    enabled.add(chart);
  }
  if (!enabled.size) enabled.add("D1");
  if (!enabled.has(settings.defaultDivisionalChart)) {
    return { ...settings, divisionalChartsEnabled: [...enabled], defaultDivisionalChart: "D1" };
  }
  return { ...settings, divisionalChartsEnabled: [...enabled] };
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<JyotishUserSettings | null>(null);
  const [calculation, setCalculation] = useState<JyotishCalculationSettings>(DEFAULT_CALCULATION);
  const [display, setDisplay] = useState<JyotishDisplaySettings>(DEFAULT_DISPLAY);
  const [status, setStatus] = useState("Загружаю настройки...");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let mounted = true;
    async function loadSettings() {
      try {
        const row = await fetchJyotishSettings();
        if (!mounted) return;
        setSettings(row);
        setCalculation(row.calculation);
        setDisplay(row.display);
        setStatus("");
      } catch (error) {
        if (!mounted) return;
        setStatus(error instanceof Error ? error.message : "Не удалось загрузить настройки.");
      }
    }
    void loadSettings();
    return () => {
      mounted = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setStatus("Сохраняю...");
    try {
      const saved = await updateJyotishSettings({ calculation, display });
      setSettings(saved);
      setCalculation(saved.calculation);
      setDisplay(saved.display);
      setStatus("Сохранено.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось сохранить настройки.");
    } finally {
      setSaving(false);
    }
  }

  async function resetDefaults() {
    setSaving(true);
    setStatus("Сбрасываю настройки...");
    try {
      const saved = await updateJyotishSettings({ calculation: DEFAULT_CALCULATION, display: DEFAULT_DISPLAY });
      setSettings(saved);
      setCalculation(saved.calculation);
      setDisplay(saved.display);
      setStatus("Настройки сброшены.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Не удалось сбросить настройки.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <ProductShell active="settings">
      {status ? <div className="product-status">{status}</div> : null}

      <form className="settings-workspace" onSubmit={handleSubmit}>
        <section className="settings-panel">
          <div className="settings-panel-head">
            <div>
              <h1>Настройки расчёта</h1>
              <span>Влияют на будущую математику карты.</span>
            </div>
          </div>

          <div className="settings-form-grid">
            <label>
              <span>Аянамша</span>
              <select value={calculation.ayanamsa} onChange={(event) => setCalculation({ ...calculation, ayanamsa: event.target.value as JyotishCalculationSettings["ayanamsa"] })}>
                <option value="lahiri">Lahiri</option>
                <option value="raman">Raman</option>
                <option value="krishnamurti">Krishnamurti</option>
                <option value="yukteshwar">Yukteshwar</option>
              </select>
            </label>
            <label>
              <span>Система домов</span>
              <select value={calculation.houseSystem} onChange={(event) => setCalculation({ ...calculation, houseSystem: event.target.value as JyotishCalculationSettings["houseSystem"] })}>
                <option value="whole_sign">Whole sign</option>
                <option value="sripati">Sripati</option>
                <option value="equal">Equal</option>
              </select>
            </label>
            <label>
              <span>Раху/Кету</span>
              <select value={calculation.nodeType} onChange={(event) => setCalculation({ ...calculation, nodeType: event.target.value as JyotishCalculationSettings["nodeType"] })}>
                <option value="mean">Mean node</option>
                <option value="true">True node</option>
              </select>
            </label>
            <label>
              <span>Профиль расчёта</span>
              <select value={calculation.calculationProfile} onChange={(event) => setCalculation({ ...calculation, calculationProfile: event.target.value as JyotishCalculationSettings["calculationProfile"] })}>
                <option value="gaudiya_default">Gaudiya default</option>
                <option value="bphs_research">BPHS research</option>
                <option value="default">Default</option>
              </select>
            </label>
            <label>
              <span>Основная D-карта</span>
              <select value={calculation.defaultDivisionalChart} onChange={(event) => setCalculation({ ...calculation, defaultDivisionalChart: event.target.value as JyotishCalculationSettings["defaultDivisionalChart"] })}>
                {DIVISIONAL_CHARTS.map((chart) => (
                  <option key={chart} value={chart} disabled={!calculation.divisionalChartsEnabled.includes(chart)}>
                    {chart}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <fieldset className="settings-checkbox-grid">
            <legend>Включённые D-карты</legend>
            {DIVISIONAL_CHARTS.map((chart) => (
              <label key={chart}>
                <input
                  type="checkbox"
                  checked={calculation.divisionalChartsEnabled.includes(chart)}
                  onChange={() => setCalculation(toggleChart(calculation, chart))}
                />
                <span>{chart}</span>
              </label>
            ))}
          </fieldset>
        </section>

        <section className="settings-panel">
          <div className="settings-panel-head">
            <div>
              <h1>Настройки отображения</h1>
              <span>Меняют только интерфейс, не расчёт.</span>
            </div>
          </div>

          <div className="settings-form-grid">
            <label>
              <span>Стиль карты</span>
              <select value={display.chartStyle} onChange={(event) => setDisplay({ ...display, chartStyle: event.target.value as JyotishDisplaySettings["chartStyle"] })}>
                <option value="north_indian">Северный индийский</option>
                <option value="south_indian">Южный индийский</option>
              </select>
            </label>
            <label>
              <span>Язык</span>
              <select value={display.language} onChange={(event) => setDisplay({ ...display, language: event.target.value as JyotishDisplaySettings["language"] })}>
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </label>
            <label>
              <span>Термины</span>
              <select value={display.terminologyMode} onChange={(event) => setDisplay({ ...display, terminologyMode: event.target.value as JyotishDisplaySettings["terminologyMode"] })}>
                <option value="mixed">Смешанные</option>
                <option value="russian">Русские</option>
                <option value="sanskrit">Санскрит</option>
              </select>
            </label>
            <label>
              <span>Градусы</span>
              <select value={display.degreeFormat} onChange={(event) => setDisplay({ ...display, degreeFormat: event.target.value as JyotishDisplaySettings["degreeFormat"] })}>
                <option value="dms">DMS</option>
                <option value="decimal">Decimal</option>
              </select>
            </label>
            <label>
              <span>Тема</span>
              <select value={display.themeMode} onChange={(event) => setDisplay({ ...display, themeMode: event.target.value as JyotishDisplaySettings["themeMode"] })}>
                <option value="system">Системная</option>
                <option value="light">Светлая</option>
                <option value="dark">Тёмная</option>
              </select>
            </label>
          </div>

          <fieldset className="settings-checkbox-grid">
            <legend>Терминология</legend>
            <label>
              <input type="checkbox" checked={display.showSanskritNames} onChange={(event) => setDisplay({ ...display, showSanskritNames: event.target.checked })} />
              <span>Показывать санскритские названия</span>
            </label>
            <label>
              <input type="checkbox" checked={display.showTransliteration} onChange={(event) => setDisplay({ ...display, showTransliteration: event.target.checked })} />
              <span>Показывать транслитерацию</span>
            </label>
          </fieldset>
        </section>

        <div className="settings-actions">
          <button className="primary-button" type="submit" disabled={saving || !settings}>
            Сохранить
          </button>
          <button className="secondary-button" type="button" disabled={saving} onClick={() => void resetDefaults()}>
            Сбросить defaults
          </button>
        </div>
      </form>
    </ProductShell>
  );
}
