"use client";

import { ProductShell } from "@/app/product-shell";
import type { AppNavKey } from "@/app/app-navigation";

type WorkflowCard = {
  label: string;
  value: string;
};

type WorkflowPageProps = {
  active: AppNavKey;
  title: string;
  description: string;
  actionHref: string;
  actionLabel: string;
  eyebrow: string;
  lead: string;
  note: string;
  cards: WorkflowCard[];
};

export function WorkflowPage({
  active,
  title,
  description,
  actionHref,
  actionLabel,
  eyebrow,
  lead,
  note,
  cards,
}: WorkflowPageProps) {
  return (
    <ProductShell active={active}>
      <header className="product-page-head">
        <div>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
        <a className="primary-link-button" href={actionHref}>{actionLabel}</a>
      </header>

      <section className="compatibility-saved-role-context" aria-label={title}>
        <div className="compatibility-saved-role-head">
          <div>
            <span>{eyebrow}</span>
            <strong>{lead}</strong>
          </div>
          <small>{note}</small>
        </div>
        <div className="compatibility-saved-role-grid">
          {cards.map((card) => (
            <div key={card.label}>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
            </div>
          ))}
        </div>
      </section>
    </ProductShell>
  );
}
