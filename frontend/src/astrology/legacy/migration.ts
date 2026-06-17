import type { LegacyMigrationItem } from "./types";

export const legacyMigrationItems: LegacyMigrationItem[] = [
  {
    id: "legacy.main.birth_chart_form",
    legacyName: "Old birth chart form and chart stack",
    targetBlockId: "block.chart.main",
    entityIds: ["varga.D1", "house.1"],
    contextIds: ["page.chart"],
    action: "wrap_as_view_block",
    status: "adapter_ready",
    notes: "Keep the calculation inputs, but render the result through the modular workbench.",
  },
  {
    id: "legacy.quick_house_explanations",
    legacyName: "Quick house explanation grid",
    targetBlockId: "block.panel.entityInspector",
    entityIds: ["house.1", "house.2", "house.3", "house.4", "house.5", "house.6", "house.7", "house.8", "house.9", "house.10", "house.11", "house.12"],
    contextIds: ["page.chart", "interaction.click"],
    action: "move_text_to_registry",
    status: "adapter_ready",
    notes: "Explanations should appear by click on the house number, not as permanent page text.",
  },
  {
    id: "legacy.d9_marriage_card",
    legacyName: "D9 marriage card",
    targetBlockId: "block.chart.vargaSelector",
    entityIds: ["varga.D9", "house.7"],
    contextIds: ["relationship.spouse"],
    action: "replace_with_entity_link",
    status: "adapter_ready",
    notes: "D9 is a varga entity, not a repeated marriage card on every page.",
  },
  {
    id: "legacy.d60_karma_card",
    legacyName: "D60 karma card",
    targetBlockId: "block.chart.vargaSelector",
    entityIds: ["varga.D60"],
    contextIds: ["time_accuracy.warning"],
    action: "replace_with_entity_link",
    status: "adapter_ready",
    notes: "D60 should be selectable and carry a time-accuracy warning.",
  },
  {
    id: "legacy.relationship_copy_blocks",
    legacyName: "Compatibility and interaction explanatory blocks",
    targetBlockId: "block.compare.roleFactors",
    entityIds: ["house.7", "varga.D9", "relationship.moonRelationship", "relationship.lagnaRelationship"],
    contextIds: ["relationship.spouse", "relationship.custom"],
    action: "replace_with_relationship_recipe",
    status: "adapter_ready",
    notes: "Role-specific logic belongs to relationship recipes, not duplicated page text.",
  },
  {
    id: "legacy.page_level_technical_notes",
    legacyName: "Technical MVP notes on user pages",
    targetBlockId: "layout.page.header",
    entityIds: [],
    contextIds: ["navigation.cleanup"],
    action: "remove_duplicate_page_copy",
    status: "adapter_ready",
    notes: "Remove project-internal explanatory copy from product screens.",
  },
];

export function listLegacyMigrationItems() {
  return legacyMigrationItems;
}
