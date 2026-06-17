"use client";

import { type ReactNode, useEffect, useRef, useState } from "react";

export type HelpItem = {
  title: string;
  text: string;
};

export type HelpAiQuestionDetail = {
  question: string;
  title: string;
  text: string;
};

export function requestAiExplanation(item: HelpItem) {
  const question = `Что значит «${item.title}» в этой карте? ${item.text}`;
  const event = new CustomEvent<HelpAiQuestionDetail>("jyotish:ask-ai-context", {
    cancelable: true,
    detail: {
      question,
      title: item.title,
      text: item.text,
    },
  });
  window.dispatchEvent(event);
  if (event.defaultPrevented) return;
  try {
    window.sessionStorage.setItem("jyotish-pending-ai-question", question);
  } catch {
    // The target page still opens; only the suggested prompt is lost.
  }
  window.location.href = "/?analysis=guidance#reports";
}

const houseHelp: Record<string, HelpItem> = {
  "1": { title: "1 дом", text: "Личность, тело, стартовая точка чтения карты и общий тон взаимодействия." },
  "2": { title: "2 дом", text: "Семья, речь, ценности, накопления и устойчивость общего быта." },
  "3": { title: "3 дом", text: "Братья и сёстры, коммуникация, инициатива, смелость и практическое сотрудничество." },
  "4": { title: "4 дом", text: "Мать, дом, сердце, эмоциональная безопасность и внутренняя опора." },
  "5": { title: "5 дом", text: "Дети, интеллект, творчество, мантра, пурва-пунья и тонкий выбор." },
  "6": { title: "6 дом", text: "Служение, обязанности, конфликты, конкуренты, долги и рабочее напряжение." },
  "7": { title: "7 дом", text: "Партнёрство, брак, договорённости и открытое взаимодействие с другим человеком." },
  "8": { title: "8 дом", text: "Кризисы, тайны, уязвимость, трансформация и скрытое напряжение в контакте." },
  "9": { title: "9 дом", text: "Отец, гуру, дхарма, благословения, наставление и старший авторитет." },
  "10": { title: "10 дом", text: "Карьера, статус, власть, ответственность и видимая роль человека в действии." },
  "11": { title: "11 дом", text: "Друзья, старшие братья/сёстры, результаты, поддержка сети и исполнение целей." },
  "12": { title: "12 дом", text: "Расходы, сон, уединение, потери, близость и скрытая сторона отношений." },
};

const vargaHelp: Record<string, HelpItem> = {
  D1: { title: "D1 / Раши", text: "Основная карта. Любой разбор взаимодействия сначала сверяется с D1 обеих карт." },
  D3: { title: "D3 / Дреккана", text: "Дополнительный слой для братьев, сестёр, инициативы, усилий и смелости." },
  D4: { title: "D4", text: "Дом, недвижимость, внутренний комфорт и опора семьи." },
  D6: { title: "D6", text: "Слой болезней, долгов, споров, врагов и конфликтного взаимодействия." },
  D7: { title: "D7 / Саптамша", text: "Дети, потомство, продолжение рода и творческое плодоношение пары." },
  D9: { title: "D9 / Навамша", text: "Дхарма, зрелость связи, брак и тонкая сила положения грах." },
  D10: { title: "D10 / Дашамша", text: "Карьера, статус, начальники, подчинённые и профессиональная роль." },
  D12: { title: "D12 / Двадашамша", text: "Родители, родовая линия, наследственность и связь с отцом/матерью." },
  D30: { title: "D30 / Тримшамша", text: "Скрытые напряжения, неприятности, риски и конфликтные паттерны." },
  D60: { title: "D60 / Шаштьямша", text: "Глубокий кармический слой; читается осторожно и требует очень точного времени рождения." },
};

export function houseHelpText(house: number | string): string {
  return houseHelp[String(house)]?.text ?? "Дом показывает сферу жизни для выбранного ракурса.";
}

export function vargaHelpText(varga: string): string {
  return vargaHelp[varga]?.text ?? "D-карта уточняет выбранную сферу жизни.";
}

export function HelpTerm({ item, children }: { item: HelpItem; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [pinned, setPinned] = useState(false);
  const wrapRef = useRef<HTMLSpanElement | null>(null);

  useEffect(() => {
    if (!open) return;
    function handlePointerDown(event: PointerEvent) {
      if (wrapRef.current?.contains(event.target as Node)) return;
      setOpen(false);
      setPinned(false);
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key !== "Escape") return;
      setOpen(false);
      setPinned(false);
    }
    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  return (
    <span
      ref={wrapRef}
      className={`reader-help reader-help-inline${open ? " open" : ""}`}
      data-open={open ? "true" : "false"}
      onBlur={(event) => {
        if (event.currentTarget.contains(event.relatedTarget as Node | null)) return;
        if (!pinned) setOpen(false);
      }}
    >
      <button
        type="button"
        className="reader-help-trigger"
        onPointerDown={(event) => event.stopPropagation()}
        onClick={(event) => {
          event.stopPropagation();
          setPinned((currentPinned) => {
            const nextPinned = !currentPinned;
            setOpen(nextPinned);
            return nextPinned;
          });
        }}
        aria-expanded={open}
      >
        {children}
      </button>
      {open ? (
        <span className="reader-help-popover" role="tooltip">
          <strong>{item.title}</strong>
          <span>{item.text}</span>
          <button
            type="button"
            className="help-ai-action"
            onClick={(event) => {
              event.stopPropagation();
              requestAiExplanation(item);
            }}
          >
            Спросить
          </button>
        </span>
      ) : null}
    </span>
  );
}

export function HouseTerms({ houses }: { houses: Array<number | string> }) {
  return (
    <span className="interaction-term-row">
      {houses.map((house) => {
        const key = String(house);
        return (
          <HelpTerm item={houseHelp[key] ?? { title: `${key} дом`, text: "Дом показывает сферу жизни для выбранного ракурса." }} key={`house-help-${key}`}>
            {key}
          </HelpTerm>
        );
      })}
    </span>
  );
}

export function VargaTerms({ vargas }: { vargas: string[] }) {
  return (
    <span className="interaction-term-row">
      {vargas.map((varga) => (
        <HelpTerm item={vargaHelp[varga] ?? { title: varga, text: "D-карта уточняет выбранную сферу жизни." }} key={`varga-help-${varga}`}>
          {varga}
        </HelpTerm>
      ))}
    </span>
  );
}
