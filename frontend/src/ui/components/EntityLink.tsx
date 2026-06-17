"use client";

import type { ReactNode } from "react";
import { getEntity, type EntityId } from "@/astrology";

export function EntityLink({
  entityId,
  children,
  onSelect,
}: {
  entityId: EntityId;
  children?: ReactNode;
  onSelect: (entityId: EntityId) => void;
}) {
  const entity = getEntity(entityId);
  return (
    <button type="button" className="entity-link" onClick={() => onSelect(entityId)}>
      {children ?? entity?.terms.ru ?? entityId}
    </button>
  );
}
