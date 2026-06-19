import { ProductShell } from "@/app/product-shell";

const dashaRows = [
  { label: "Махадаша", value: "главный период", note: "долгая тема жизни" },
  { label: "Антардаша", value: "подпериод", note: "активный слой периода" },
  { label: "Пратьянтардаша", value: "детализация", note: "для точной консультации" },
];

const supportedSystems = [
  { code: "Vimshottari", title: "Вимшоттари", status: "основная система" },
];

export default function DashasPage() {
  return (
    <ProductShell active="timeline">
      <header className="product-page-head">
        <div>
          <h1>Даши</h1>
          <p>Периоды карты. Сначала подключается Вимшоттари; данные берутся из сохранённой карты.</p>
        </div>
      </header>

      <section className="product-page-card dasha-workbench-shell" aria-label="Рабочее место даш">
        <div className="source-explorer-grid">
          <article className="source-explorer-card">
            <div className="source-explorer-card-head">
              <span>Система</span>
              <strong>Вимшоттари</strong>
            </div>
            <div className="source-list">
              {supportedSystems.map((system) => (
                <div className="source-list-row" key={system.code}>
                  <strong>{system.title}</strong>
                  <span>{system.status}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="source-explorer-card">
            <div className="source-explorer-card-head">
              <span>Слои чтения</span>
              <strong>Периоды</strong>
            </div>
            <div className="source-list">
              {dashaRows.map((row) => (
                <div className="source-list-row" key={row.label}>
                  <strong>{row.label}</strong>
                  <span>
                    {row.value} · {row.note}
                  </span>
                </div>
              ))}
            </div>
          </article>

          <article className="source-explorer-card">
            <div className="source-explorer-card-head">
              <span>Объяснение</span>
              <strong>EntityInspector</strong>
            </div>
            <p className="source-explorer-copy">
              Нажатие на период, граху или дату будет открывать одно общее объяснение без лишних блоков на странице.
            </p>
          </article>
        </div>
      </section>
    </ProductShell>
  );
}
