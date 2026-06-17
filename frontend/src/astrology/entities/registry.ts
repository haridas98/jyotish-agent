import type { EntityDefinition, EntityId } from "./types";

const entities = new Map<EntityId, EntityDefinition>();

export function registerEntity(entity: EntityDefinition): EntityDefinition {
  entities.set(entity.id, entity);
  return entity;
}

export function getEntity(entityId: EntityId): EntityDefinition | null {
  return entities.get(entityId) ?? null;
}

export function listEntities(): EntityDefinition[] {
  return Array.from(entities.values());
}
