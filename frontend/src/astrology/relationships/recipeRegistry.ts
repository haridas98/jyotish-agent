import type { EntityId } from "../entities";
import type { RelationshipFactorId } from "./factorTypes";
import type { RelationshipTypeId } from "./relationshipTypes";
import type { RecipeFocus, RecipeWarning, RelationshipRecipe } from "./recipeTypes";

const missingSource = (ruleIds: string[]): RecipeWarning => ({ type: "missing_source", ruleIds });

const emptyFocus = (): RecipeFocus => ({
  primaryEntityIds: [],
  secondaryEntityIds: [],
  relationshipFactorIds: [],
  requiredCalculationIds: [],
  optionalCalculationIds: [],
  ruleIds: [],
  warnings: [],
});

function focus(input: Partial<RecipeFocus>): RecipeFocus {
  return {
    ...emptyFocus(),
    ...input,
  };
}

function recipe(
  relationshipTypeId: RelationshipTypeId,
  ru: string,
  en: string,
  perspectiveAtoB: RecipeFocus,
  perspectiveBtoA: RecipeFocus,
  mutualFocus: RecipeFocus,
  status: RelationshipRecipe["status"] = "needs_source",
  visibleInModes: RelationshipRecipe["visibleInModes"] = ["novice", "astrologer"],
): RelationshipRecipe {
  return {
    id: relationshipTypeId,
    version: 1,
    relationshipTypeId,
    label: { ru, en },
    status,
    perspectiveAtoB,
    perspectiveBtoA,
    mutualFocus,
    visibleInModes,
    sourcePolicy: {
      requireVerifiedRulesForNormalUi: true,
    },
  };
}

const mutualBasic = (ruleId: string): RecipeFocus =>
  focus({
    relationshipFactorIds: [
      "factor.overlay.planets_a_to_b",
      "factor.overlay.planets_b_to_a",
      "factor.moon.relationship",
      "factor.lagna.relationship",
      "factor.mutual.aspects",
      "factor.dasha.overlap",
    ],
    requiredCalculationIds: ["varga.D1"],
    optionalCalculationIds: ["dasha.vimshottari"],
    ruleIds: [ruleId],
    warnings: [missingSource([ruleId])],
  });

export const relationshipRecipeDefinitions: RelationshipRecipe[] = [
  recipe(
    "father_child",
    "Отец и ребёнок",
    "Father and child",
    focus({
      primaryEntityIds: ["house.5", "graha.JU", "varga.D7"],
      secondaryEntityIds: ["house.2", "house.9"],
      relationshipFactorIds: ["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b"],
      requiredCalculationIds: ["varga.D1", "varga.D7"],
      optionalCalculationIds: ["dasha.vimshottari"],
      ruleIds: ["rule.relationship.father_child.father_to_child"],
      warnings: [missingSource(["rule.relationship.father_child.father_to_child"])],
    }),
    focus({
      primaryEntityIds: ["house.9", "graha.SU", "varga.D12"],
      secondaryEntityIds: ["house.1", "house.4"],
      relationshipFactorIds: ["factor.overlay.houses_b_to_a", "factor.overlay.planets_b_to_a"],
      requiredCalculationIds: ["varga.D1", "varga.D12"],
      optionalCalculationIds: ["dasha.vimshottari"],
      ruleIds: ["rule.relationship.father_child.child_to_father"],
      warnings: [missingSource(["rule.relationship.father_child.child_to_father"])],
    }),
    mutualBasic("rule.relationship.father_child.mutual"),
  ),
  recipe(
    "mother_child",
    "Мать и ребёнок",
    "Mother and child",
    focus({
      primaryEntityIds: ["house.5", "graha.JU", "varga.D7"],
      secondaryEntityIds: ["house.4"],
      relationshipFactorIds: ["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b"],
      requiredCalculationIds: ["varga.D1", "varga.D7"],
      optionalCalculationIds: ["dasha.vimshottari"],
      ruleIds: ["rule.relationship.mother_child.mother_to_child"],
      warnings: [missingSource(["rule.relationship.mother_child.mother_to_child"])],
    }),
    focus({
      primaryEntityIds: ["house.4", "graha.MO", "varga.D12"],
      secondaryEntityIds: ["house.1", "house.9"],
      relationshipFactorIds: ["factor.overlay.houses_b_to_a", "factor.overlay.planets_b_to_a"],
      requiredCalculationIds: ["varga.D1", "varga.D12"],
      optionalCalculationIds: ["dasha.vimshottari"],
      ruleIds: ["rule.relationship.mother_child.child_to_mother"],
      warnings: [missingSource(["rule.relationship.mother_child.child_to_mother"])],
    }),
    mutualBasic("rule.relationship.mother_child.mutual"),
  ),
  recipe(
    "siblings",
    "Братья и сестры",
    "Siblings",
    siblingFocus("rule.relationship.siblings.a_to_b"),
    siblingFocus("rule.relationship.siblings.b_to_a"),
    mutualBasic("rule.relationship.siblings.mutual"),
  ),
  recipe(
    "spouses",
    "Супруги",
    "Spouses",
    spouseFocus("a_to_b", "rule.relationship.spouses.a_to_b"),
    spouseFocus("b_to_a", "rule.relationship.spouses.b_to_a"),
    mutualBasic("rule.relationship.spouses.mutual"),
  ),
  recipe(
    "romantic_partners",
    "\u0420\u043e\u043c\u0430\u043d\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u044b",
    "Romantic partners",
    spouseFocus("a_to_b", "rule.relationship.romantic_partners.a_to_b"),
    spouseFocus("b_to_a", "rule.relationship.romantic_partners.b_to_a"),
    mutualBasic("rule.relationship.romantic_partners.mutual"),
  ),
  recipe(
    "business_partners",
    "Бизнес-партнеры",
    "Business partners",
    businessFocus("rule.relationship.business_partners.a_to_b"),
    businessFocus("rule.relationship.business_partners.b_to_a"),
    mutualBasic("rule.relationship.business_partners.mutual"),
  ),
  recipe(
    "boss_subordinate",
    "Руководитель и подчиненный",
    "Boss and subordinate",
    focus({
      primaryEntityIds: ["house.10", "graha.SA", "varga.D10"],
      secondaryEntityIds: ["house.6"],
      relationshipFactorIds: ["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b"],
      requiredCalculationIds: ["varga.D1", "varga.D10"],
      optionalCalculationIds: ["dasha.vimshottari"],
      ruleIds: ["rule.relationship.boss_subordinate.boss_to_subordinate"],
      warnings: [missingSource(["rule.relationship.boss_subordinate.boss_to_subordinate"])],
    }),
    focus({
      primaryEntityIds: ["house.6", "house.10", "varga.D10"],
      secondaryEntityIds: ["graha.SA"],
      relationshipFactorIds: ["factor.overlay.houses_b_to_a", "factor.overlay.planets_b_to_a"],
      requiredCalculationIds: ["varga.D1", "varga.D10"],
      optionalCalculationIds: ["dasha.vimshottari"],
      ruleIds: ["rule.relationship.boss_subordinate.subordinate_to_boss"],
      warnings: [missingSource(["rule.relationship.boss_subordinate.subordinate_to_boss"])],
    }),
    mutualBasic("rule.relationship.boss_subordinate.mutual"),
  ),
  recipe(
    "guru_student",
    "Гуру и ученик",
    "Guru and student",
    focus({
      primaryEntityIds: ["house.9", "graha.JU", "varga.D20"],
      secondaryEntityIds: ["house.5"],
      relationshipFactorIds: ["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b"],
      requiredCalculationIds: ["varga.D1", "varga.D20"],
      optionalCalculationIds: ["dasha.vimshottari"],
      ruleIds: ["rule.relationship.guru_student.guru_to_student"],
      warnings: [missingSource(["rule.relationship.guru_student.guru_to_student"])],
    }),
    focus({
      primaryEntityIds: ["house.5", "house.9", "varga.D20"],
      secondaryEntityIds: ["graha.JU"],
      relationshipFactorIds: ["factor.overlay.houses_b_to_a", "factor.overlay.planets_b_to_a"],
      requiredCalculationIds: ["varga.D1", "varga.D20"],
      optionalCalculationIds: ["dasha.vimshottari"],
      ruleIds: ["rule.relationship.guru_student.student_to_guru"],
      warnings: [missingSource(["rule.relationship.guru_student.student_to_guru"])],
    }),
    mutualBasic("rule.relationship.guru_student.mutual"),
  ),
  recipe(
    "opponents",
    "Оппоненты",
    "Opponents",
    focus({
      primaryEntityIds: ["house.6", "house.8", "graha.MA"],
      secondaryEntityIds: ["graha.SA"],
      relationshipFactorIds: ["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b", "factor.mutual.aspects"],
      requiredCalculationIds: ["varga.D1"],
      optionalCalculationIds: ["dasha.vimshottari", "transits.current"],
      ruleIds: ["rule.relationship.opponents.a_to_b"],
      warnings: [missingSource(["rule.relationship.opponents.a_to_b"])],
    }),
    focus({
      primaryEntityIds: ["house.6", "house.8", "graha.MA"],
      secondaryEntityIds: ["graha.SA"],
      relationshipFactorIds: ["factor.overlay.houses_b_to_a", "factor.overlay.planets_b_to_a", "factor.mutual.aspects"],
      requiredCalculationIds: ["varga.D1"],
      optionalCalculationIds: ["dasha.vimshottari", "transits.current"],
      ruleIds: ["rule.relationship.opponents.b_to_a"],
      warnings: [missingSource(["rule.relationship.opponents.b_to_a"])],
    }),
    mutualBasic("rule.relationship.opponents.mutual"),
  ),
  recipe(
    "custom",
    "Своя связь",
    "Custom relationship",
    emptyFocus(),
    emptyFocus(),
    focus({
      secondaryEntityIds: ["varga.D60"],
      relationshipFactorIds: ["factor.transit.context"],
      optionalCalculationIds: ["varga.D60", "transits.current"],
      ruleIds: ["rule.relationship.custom.astrologer_context"],
      warnings: [
        { type: "birth_time_accuracy", minimumAccuracy: "exact", affectedEntityIds: ["varga.D60"] },
        { type: "expert_only", entityIds: ["varga.D60"] },
        missingSource(["rule.relationship.custom.astrologer_context"]),
      ],
    }),
    "draft",
    ["astrologer"],
  ),
];

export const relationshipRecipes: Record<string, RelationshipRecipe> = Object.fromEntries(
  relationshipRecipeDefinitions.map((definition) => [definition.id, definition]),
);

export function getRelationshipRecipe(id: string): RelationshipRecipe | null {
  return relationshipRecipes[id] ?? null;
}

export function listRelationshipRecipes(): RelationshipRecipe[] {
  return relationshipRecipeDefinitions;
}

function siblingFocus(ruleId: string): RecipeFocus {
  return focus({
    primaryEntityIds: ["house.3", "varga.D3"],
    secondaryEntityIds: ["house.11", "graha.MA"],
    relationshipFactorIds: ["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b"],
    requiredCalculationIds: ["varga.D1", "varga.D3"],
    optionalCalculationIds: ["dasha.vimshottari"],
    ruleIds: [ruleId],
    warnings: [missingSource([ruleId])],
  });
}

function spouseFocus(direction: "a_to_b" | "b_to_a", ruleId: string): RecipeFocus {
  const overlayFactors =
    direction === "b_to_a"
      ? (["factor.overlay.houses_b_to_a", "factor.overlay.planets_b_to_a"] as const)
      : (["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b"] as const);
  return focus({
    primaryEntityIds: ["house.7", "varga.D9"],
    secondaryEntityIds: ["graha.VE", "graha.JU"],
    relationshipFactorIds: [...overlayFactors, "factor.moon.relationship"],
    requiredCalculationIds: ["varga.D1", "varga.D9"],
    optionalCalculationIds: ["dasha.vimshottari"],
    ruleIds: [ruleId],
    warnings: [missingSource([ruleId])],
  });
}

function businessFocus(ruleId: string): RecipeFocus {
  return focus({
    primaryEntityIds: ["house.7", "house.10", "house.11", "varga.D10"],
    secondaryEntityIds: ["house.2", "house.8", "graha.ME", "graha.SA"],
    relationshipFactorIds: ["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b", "factor.dasha.overlap"],
    requiredCalculationIds: ["varga.D1", "varga.D10"],
    optionalCalculationIds: ["dasha.vimshottari"],
    ruleIds: [ruleId],
    warnings: [missingSource([ruleId])],
  });
}
