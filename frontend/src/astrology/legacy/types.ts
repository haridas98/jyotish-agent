export type LegacyMigrationStatus = "legacy" | "adapter_ready" | "migrated";

export type LegacyMigrationAction =
  | "wrap_as_view_block"
  | "move_text_to_registry"
  | "replace_with_entity_link"
  | "replace_with_relationship_recipe"
  | "remove_duplicate_page_copy";

export type LegacyMigrationItem = {
  id: string;
  legacyName: string;
  targetBlockId: string;
  entityIds: string[];
  contextIds: string[];
  action: LegacyMigrationAction;
  status: LegacyMigrationStatus;
  notes: string;
};
