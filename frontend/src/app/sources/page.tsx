import { ProductShell } from "@/app/product-shell";
import { getEntity, listPassages, listRules, listSources, registerCoreEntities, type EntityId } from "@/astrology";

function statusLabel(status: string): string {
  if (status === "verified") return "проверено";
  if (status === "needs_source") return "нужен источник";
  if (status === "draft") return "черновик";
  if (status === "disputed") return "спорно";
  return status;
}

function sourceTypeLabel(type: string): string {
  if (type === "primary_shastra") return "первичная шастра";
  if (type === "traditional_commentary") return "традиционный комментарий";
  if (type === "modern_commentary") return "современный комментарий";
  if (type === "research") return "исследование";
  if (type === "internal_note") return "внутренняя заметка";
  return type;
}

function languageLabel(language: string): string {
  if (language === "sanskrit") return "санскрит";
  if (language === "english") return "английский";
  if (language === "russian") return "русский";
  if (language === "hindi") return "хинди";
  return "другой";
}

function domainLabel(domain: string): string {
  if (domain === "graha") return "грахи";
  if (domain === "house") return "дома";
  if (domain === "rashi") return "знаки";
  if (domain === "nakshatra") return "накшатры";
  if (domain === "varga") return "варги";
  if (domain === "dasha") return "даши";
  if (domain === "yoga") return "йоги";
  if (domain === "relationship") return "связи";
  if (domain === "strength") return "сила";
  if (domain === "transit") return "транзиты";
  return domain;
}

function locatorLabel(locator: { chapter?: string; verseStart?: string; verseEnd?: string; section?: string; page?: number }): string {
  const parts = [
    locator.chapter ? `гл. ${locator.chapter}` : null,
    locator.verseStart ? `ст. ${locator.verseEnd ? `${locator.verseStart}-${locator.verseEnd}` : locator.verseStart}` : null,
    locator.section ?? null,
    locator.page ? `стр. ${locator.page}` : null,
  ].filter(Boolean);
  return parts.length ? parts.join(", ") : "локатор уточняется";
}

function entityLabels(entityIds: string[]): string {
  if (!entityIds.length) return "расчётный слой";
  return entityIds.map((entityId) => getEntity(entityId as EntityId)?.terms.ru ?? getEntity(entityId as EntityId)?.terms.short ?? "сущность").join(", ");
}

export default function SourcesPage() {
  registerCoreEntities();

  const sources = listSources();
  const passages = listPassages();
  const rules = listRules();

  return (
    <ProductShell active="sources">
      <section className="product-page-card">
        <div>
          <h1>Источники</h1>
          <p>Минимальный реестр шастр, мест и правил для будущих отчётов с проверяемым происхождением выводов.</p>
        </div>
      </section>

      <section className="source-filter-row" aria-label="Фильтры источников">
        <span>Поиск</span>
        <span>Статус</span>
        <span>Тема</span>
      </section>

      <section className="source-explorer-grid">
        <div className="product-page-card source-explorer-card">
          <h2>Шастры</h2>
          {sources.map((source, sourceIndex) => {
            const sourcePassages = passages.filter((passage) => passage.sourceId === source.id);
            const sourceRules = rules.filter((rule) => rule.passageIds.some((passageId) => sourcePassages.some((passage) => passage.id === passageId)));
            return (
              <article className="source-row-card" key={`source-${sourceIndex}`}>
                <h3>{source.title.ru}</h3>
                <p>{source.shortTitle}</p>
                <dl>
                  <div>
                    <dt>Тип</dt>
                    <dd>{sourceTypeLabel(source.sourceType)}</dd>
                  </div>
                  <div>
                    <dt>Язык</dt>
                    <dd>{languageLabel(source.language)}</dd>
                  </div>
                  <div>
                    <dt>Статус</dt>
                    <dd>{statusLabel(source.status)}</dd>
                  </div>
                  <div>
                    <dt>Места / правила</dt>
                    <dd>
                      {sourcePassages.length} / {sourceRules.length}
                    </dd>
                  </div>
                </dl>
              </article>
            );
          })}
        </div>

        <div className="product-page-card source-explorer-card">
          <h2>Места</h2>
          {passages.map((passage, passageIndex) => {
            const source = sources.find((item) => item.id === passage.sourceId);
            const linkedRules = rules.filter((rule) => rule.passageIds.includes(passage.id));
            return (
              <article className="source-row-card" key={`passage-${passageIndex}`}>
                <h3>{passage.citationLabel.ru}</h3>
                <small>{source?.shortTitle ?? "Источник уточняется"}</small>
                <p>{passage.shortExcerpt?.ru ?? "Краткая выдержка будет добавлена после проверки текста."}</p>
                <dl>
                  <div>
                    <dt>Локатор</dt>
                    <dd>{locatorLabel(passage.locator)}</dd>
                  </div>
                  <div>
                    <dt>Статус</dt>
                    <dd>{statusLabel(passage.status)}</dd>
                  </div>
                  <div>
                    <dt>Правила</dt>
                    <dd>{linkedRules.length}</dd>
                  </div>
                </dl>
              </article>
            );
          })}
        </div>

        <div className="product-page-card source-explorer-card">
          <h2>Правила</h2>
          {rules.map((rule, ruleIndex) => (
            <article className="source-row-card" key={`rule-${ruleIndex}`}>
              <h3>{rule.label.ru}</h3>
              <p>{entityLabels(rule.appliesToEntityIds)}</p>
              <dl>
                <div>
                  <dt>Тема</dt>
                  <dd>{domainLabel(rule.domain)}</dd>
                </div>
                <div>
                  <dt>Статус</dt>
                  <dd>{statusLabel(rule.status)}</dd>
                </div>
                <div>
                  <dt>Источники</dt>
                  <dd>{rule.passageIds.length}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      </section>
    </ProductShell>
  );
}
