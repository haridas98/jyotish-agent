"use client";

import type { ReactNode } from "react";

import { getEntity, registerCoreEntities, type EntityId } from "@/astrology";

type EntityChipProps = {
  entityId: EntityId;
  active?: boolean;
  className?: string;
  children?: ReactNode;
  onSelect?: (entityId: EntityId) => void;
};

registerCoreEntities();

export function EntityChip({ entityId, active = false, className, children, onSelect }: EntityChipProps) {
  const entity = getEntity(entityId);
  const label = children ?? entity?.terms.short ?? entity?.terms.ru ?? entityId;
  const title = entity ? `${entity.terms.ru}: ${entity.summary}` : String(entityId);
  const ariaLabel = entity ? `Открыть объяснение: ${entity.terms.ru}` : `Открыть объяснение: ${entityId}`;
  const classes = ["entity-chip", active ? "is-active" : "", className ?? ""].filter(Boolean).join(" ");

  if (onSelect) {
    return (
      <button type="button" aria-label={ariaLabel} className={classes} title={title} onClick={() => onSelect(entityId)}>
        {label}
      </button>
    );
  }

  return (
    <span className={classes} title={title}>
      {label}
    </span>
  );
}
