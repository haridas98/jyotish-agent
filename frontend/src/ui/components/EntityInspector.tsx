"use client";

import { getEntity, type EntityId } from "@/astrology";

const grahaNames: Record<string, string> = {
  SU: "Солнце",
  MO: "Луна",
  MA: "Марс",
  ME: "Меркурий",
  JU: "Юпитер",
  VE: "Венера",
  SA: "Сатурн",
  RA: "Раху",
  KE: "Кету",
  AS: "Лагна",
};

export function EntityInspector({ entityId }: { entityId: EntityId | null }) {
  const explanation = entityId ? resolveExplanation(entityId) : null;

  if (!explanation) {
    return (
      <aside className="v2-inspector">
        <h2>Объяснение</h2>
        <p>Нажмите на граху, дом, знак, накшатру, статус или значение в таблице.</p>
      </aside>
    );
  }

  return (
    <aside className="v2-inspector">
      <div className="v2-inspector-title">
        <span>{explanation.kind}</span>
        <h2>{explanation.title}</h2>
      </div>
      <div className="v2-inspector-tabs" aria-label="Разделы объяснения">
        <button type="button">Смысл</button>
        <button type="button">В карте</button>
        <button type="button">Проверки</button>
        <button type="button">Источники</button>
      </div>
      {explanation.paragraphs.map((paragraph) => (
        <p key={paragraph}>{paragraph}</p>
      ))}
      {explanation.warning ? <p className="v2-warning">{explanation.warning}</p> : null}
      <div className="v2-source-list">
        {explanation.sources.map((sourceId) => (
          <span key={sourceId}>{sourceId}</span>
        ))}
      </div>
    </aside>
  );
}

function resolveExplanation(entityId: EntityId) {
  const registered = getEntity(entityId);
  if (registered) {
    return {
      kind: registered.kind,
      title: registered.terms.ru,
      paragraphs: [registered.summary],
      warning: registered.warning,
      sources: registered.sourceIds ?? ["source.pending"],
    };
  }

  const placement = /^placement\.([A-Z]{2})\.house\.(\d{1,2})$/.exec(entityId);
  if (placement) {
    const [, grahaCode, houseNumber] = placement;
    const graha = getEntity(`graha.${grahaCode}` as EntityId);
    const house = getEntity(`house.${houseNumber}` as EntityId);
    const grahaName = grahaNames[grahaCode] ?? grahaCode;
    return {
      kind: "placement",
      title: `${grahaName} в ${houseNumber} доме`,
      paragraphs: [
        `${grahaName} даёт свои естественные значения через сферу ${houseNumber} дома. Поэтому сначала смотрят природу грахи, затем темы дома, знак, управителя знака, аспекты, соединения, силу и текущую дашу.`,
        house?.summary ?? `${houseNumber} дом нужно читать как отдельную сферу карты, а не как изолированную фразу.`,
        graha?.summary ?? "Значение грахи уточняется через достоинство, скорость, ретроградность, сожжение, накшатру и управляемые дома.",
        "Итог нельзя делать по одному фактору. Для шастрического вывода нужно сверить D1, соответствующую D-карту, силу планеты, дашу и подтверждение из источников.",
      ],
      warning: "Это рабочее объяснение. Точные ссылки на шлоки будут подключаться из библиотеки источников.",
      sources: [`bphs.house.${houseNumber}`, `bphs.graha.${grahaCode.toLowerCase()}`, "source.pending.exact_verse"],
    };
  }

  if (entityId.startsWith("nakshatra.")) {
    const name = entityId.replace("nakshatra.", "");
    return {
      kind: "nakshatra",
      title: name,
      paragraphs: [
        "Накшатра уточняет психологический и событийный слой положения. Для Луны она особенно важна, потому что от неё строится Вимшоттари-даша.",
        "В разборе нужно смотреть управителя накшатры, паду, навамшу, связь с домом и текущий период.",
      ],
      sources: ["vimshottari.moon.nakshatra", "source.pending.nakshatra"],
    };
  }

  return null;
}
