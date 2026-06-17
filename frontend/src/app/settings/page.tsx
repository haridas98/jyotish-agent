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
      termLanguage: "ru" as TermLanguage,
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
    termLanguage: termLanguage === "ru" || termLanguage === "en" || termLanguage === "sanskrit" ? termLanguage : "ru" as TermLanguage,
    houseHintsEnabled: houseHints === null ? true : houseHints !== "false",
    interfaceMode: interfaceMode === "beginner" ? "beginner" as InterfaceMode : "pro" as InterfaceMode,
  };
}

export default function SettingsPage() {
  const [chartStyle, setChartStyle] = useState<ChartStyle>("north");
  const [termLanguage, setTermLanguage] = useState<TermLanguage>("ru");
  const [houseHintsEnabled, setHouseHintsEnabled] = useState(true);
  const [interfaceMode, setInterfaceMode] = useState<InterfaceMode>("pro");
  const [status, setStatus] = useState("");

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

    setStatus("Сохранено");
  }

  return (
    <ProductShell active="settings">
      {status ? <div className="product-status">{status}</div> : null}

      <section className="compatibility-saved-role-context" aria-label="Настройки отображения">
        <div className="compatibility-saved-role-head">
          <div>
            <span>Отображение карты</span>
          </div>
        </div>
        <div className="settings-choice-grid">
          <section className="settings-choice-group" aria-label="Стиль карты">
            <strong>Стиль карты</strong>
            <div className="settings-choice-row" role="radiogroup" aria-label="Стиль карты">
              <button type="button" className={chartStyle === "north" ? "active" : ""} aria-pressed={chartStyle === "north"} onClick={() => persist({ chartStyle: "north" })}>
                Северный
              </button>
              <button type="button" className={chartStyle === "south" ? "active" : ""} aria-pressed={chartStyle === "south"} onClick={() => persist({ chartStyle: "south" })}>
                Южный
              </button>
            </div>
          </section>
          <section className="settings-choice-group" aria-label="Язык терминов">
            <strong>Язык терминов</strong>
            <div className="settings-choice-row three" role="radiogroup" aria-label="Язык терминов">
              <button type="button" className={termLanguage === "sanskrit" ? "active" : ""} aria-pressed={termLanguage === "sanskrit"} onClick={() => persist({ termLanguage: "sanskrit" })}>
                Санскрит
              </button>
              <button type="button" className={termLanguage === "ru" ? "active" : ""} aria-pressed={termLanguage === "ru"} onClick={() => persist({ termLanguage: "ru" })}>
                Русский
              </button>
              <button type="button" className={termLanguage === "en" ? "active" : ""} aria-pressed={termLanguage === "en"} onClick={() => persist({ termLanguage: "en" })}>
                English
              </button>
            </div>
          </section>
          <section className="settings-choice-group" aria-label="Режим интерфейса">
            <strong>Режим</strong>
            <div className="settings-choice-row" role="radiogroup" aria-label="Режим интерфейса">
              <button type="button" className={interfaceMode === "pro" ? "active" : ""} aria-pressed={interfaceMode === "pro"} onClick={() => persist({ interfaceMode: "pro" })}>
                Астролог
              </button>
              <button type="button" className={interfaceMode === "beginner" ? "active" : ""} aria-pressed={interfaceMode === "beginner"} onClick={() => persist({ interfaceMode: "beginner" })}>
                Новичок
              </button>
            </div>
          </section>
          <section className="settings-choice-group" aria-label="Подсказки внутри карты">
            <strong>Подсказки</strong>
            <div className="settings-choice-row" role="radiogroup" aria-label="Подсказки внутри карты">
              <button type="button" className={houseHintsEnabled ? "active" : ""} aria-pressed={houseHintsEnabled} onClick={() => persist({ houseHintsEnabled: true })}>
                Включены
              </button>
              <button type="button" className={!houseHintsEnabled ? "active" : ""} aria-pressed={!houseHintsEnabled} onClick={() => persist({ houseHintsEnabled: false })}>
                Выключены
              </button>
            </div>
          </section>
        </div>
      </section>

    </ProductShell>
  );
}
