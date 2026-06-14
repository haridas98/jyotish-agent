"use client";

import { useEffect, useState } from "react";
import { ProductShell } from "@/app/product-shell";
import { INTERFACE_MODE_STORAGE_KEY, type InterfaceMode } from "@/app/interface-mode-switch";

type ChartStyle = "north" | "south";
type TermLanguage = "sanskrit" | "ru" | "en";

const CHART_STYLE_STORAGE_KEY = "jyotish-chart-style";
const TERM_LANGUAGE_STORAGE_KEY = "jyotish-term-language";
const CHART_HOUSE_HINTS_STORAGE_KEY = "jyotish-chart-house-hints";

function storageAvailable() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function readDisplaySettings() {
  if (!storageAvailable()) {
    return {
      chartStyle: "north" as ChartStyle,
      termLanguage: "sanskrit" as TermLanguage,
      houseHintsEnabled: true,
      interfaceMode: "pro" as InterfaceMode,
    };
  }

  const chartStyle = window.localStorage.getItem(CHART_STYLE_STORAGE_KEY);
  const termLanguage = window.localStorage.getItem(TERM_LANGUAGE_STORAGE_KEY);
  const houseHints = window.localStorage.getItem(CHART_HOUSE_HINTS_STORAGE_KEY);
  const interfaceMode = window.localStorage.getItem(INTERFACE_MODE_STORAGE_KEY);

  return {
    chartStyle: chartStyle === "south" ? "south" as ChartStyle : "north" as ChartStyle,
    termLanguage: termLanguage === "ru" || termLanguage === "en" || termLanguage === "sanskrit" ? termLanguage : "sanskrit" as TermLanguage,
    houseHintsEnabled: houseHints === null ? true : houseHints !== "false",
    interfaceMode: interfaceMode === "beginner" ? "beginner" as InterfaceMode : "pro" as InterfaceMode,
  };
}

export default function SettingsPage() {
  const [chartStyle, setChartStyle] = useState<ChartStyle>("north");
  const [termLanguage, setTermLanguage] = useState<TermLanguage>("sanskrit");
  const [houseHintsEnabled, setHouseHintsEnabled] = useState(true);
  const [interfaceMode, setInterfaceMode] = useState<InterfaceMode>("pro");
  const [status, setStatus] = useState("Настройки загружены для этого браузера.");

  useEffect(() => {
    const saved = readDisplaySettings();
    setChartStyle(saved.chartStyle);
    setTermLanguage(saved.termLanguage);
    setHouseHintsEnabled(saved.houseHintsEnabled);
    setInterfaceMode(saved.interfaceMode);
  }, []);

  function persist(next: {
    chartStyle?: ChartStyle;
    termLanguage?: TermLanguage;
    houseHintsEnabled?: boolean;
    interfaceMode?: InterfaceMode;
  }) {
    const merged = {
      chartStyle,
      termLanguage,
      houseHintsEnabled,
      interfaceMode,
      ...next,
    };

    setChartStyle(merged.chartStyle);
    setTermLanguage(merged.termLanguage);
    setHouseHintsEnabled(merged.houseHintsEnabled);
    setInterfaceMode(merged.interfaceMode);

    if (storageAvailable()) {
      window.localStorage.setItem(CHART_STYLE_STORAGE_KEY, merged.chartStyle);
      window.localStorage.setItem(TERM_LANGUAGE_STORAGE_KEY, merged.termLanguage);
      window.localStorage.setItem(CHART_HOUSE_HINTS_STORAGE_KEY, String(merged.houseHintsEnabled));
      window.localStorage.setItem(INTERFACE_MODE_STORAGE_KEY, merged.interfaceMode);
      window.dispatchEvent(new Event("jyotish-display-settings-changed"));
    }

    setStatus("Сохранено. Новые карты и таблицы будут открываться с этими настройками.");
  }

  return (
    <ProductShell active="settings">
      <header className="product-page-head">
        <div>
          <h1>Настройки</h1>
          <p>Единое место для стиля карты, языка терминов и режима подсказок.</p>
        </div>
        <a className="primary-link-button" href="/">Открыть карту</a>
      </header>

      <div className="product-status">{status}</div>

      <section className="compatibility-saved-role-context" aria-label="Настройки отображения">
        <div className="compatibility-saved-role-head">
          <div>
            <span>Отображение карты</span>
            <strong>Стиль выбирается один раз и применяется ко всем картам</strong>
          </div>
          <small>Северный стиль фиксирует дома, южный стиль фиксирует знаки. Расчёты от этого не меняются.</small>
        </div>
        <div className="settings-grid">
          <label>
            Стиль карты
            <select value={chartStyle} onChange={(event) => persist({ chartStyle: event.target.value as ChartStyle })}>
              <option value="north">Северный: дома фиксированы</option>
              <option value="south">Южный: знаки фиксированы</option>
            </select>
          </label>
          <label>
            Язык терминов
            <select value={termLanguage} onChange={(event) => persist({ termLanguage: event.target.value as TermLanguage })}>
              <option value="sanskrit">Санскрит: Surya, Mithuna</option>
              <option value="ru">Русский: Солнце, Близнецы</option>
              <option value="en">English: Sun, Gemini</option>
            </select>
          </label>
          <label>
            Режим интерфейса
            <select value={interfaceMode} onChange={(event) => persist({ interfaceMode: event.target.value as InterfaceMode })}>
              <option value="pro">Астролог: рабочие панели</option>
              <option value="beginner">Новичок: больше объяснений</option>
            </select>
          </label>
          <label>
            Подсказки внутри карты
            <select value={houseHintsEnabled ? "on" : "off"} onChange={(event) => persist({ houseHintsEnabled: event.target.value === "on" })}>
              <option value="on">Включены</option>
              <option value="off">Выключены</option>
            </select>
          </label>
        </div>
      </section>

      <section className="compatibility-saved-role-context" aria-label="Как это влияет на интерфейс">
        <div className="compatibility-saved-role-head">
          <div>
            <span>Применение</span>
            <strong>Настройки отвечают только за UX и чтение терминов</strong>
          </div>
          <small>Модель расчёта, ayanamsa, дома и эфемериды остаются в настройках расчёта карты.</small>
        </div>
        <div className="compatibility-saved-role-grid">
          <div>
            <span>Северный стиль</span>
            <strong>удобен для чтения домов и бхавешей</strong>
          </div>
          <div>
            <span>Южный стиль</span>
            <strong>удобен для чтения знаков и Джаимини-ракурса</strong>
          </div>
          <div>
            <span>Санскрит / русский / English</span>
            <strong>меняет подписи в карте и таблицах</strong>
          </div>
          <div>
            <span>Подсказки</span>
            <strong>открываются в карте и таблицах без лишних блоков</strong>
          </div>
        </div>
      </section>
    </ProductShell>
  );
}
