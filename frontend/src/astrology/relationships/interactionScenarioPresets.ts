import type { RelationshipTypeId } from "./relationshipTypes";

export type InteractionScenarioPreset = {
  id: string;
  label: string;
  relationshipTypeId: RelationshipTypeId;
  direction: "a_to_b" | "b_to_a";
  context: string;
};

export const interactionScenarioPresets: InteractionScenarioPreset[] = [
  {
    id: "sibling_brother_loan",
    label: "Sibling or brother loan",
    relationshipTypeId: "siblings",
    direction: "a_to_b",
    context:
      "Practical question: a sibling or brother is asking for money. Review trust, pressure, repayment clarity, and boundaries before deciding. This is context, not financial advice.",
  },
  {
    id: "boss_subordinate_conflict",
    label: "Boss/subordinate conflict",
    relationshipTypeId: "boss_subordinate",
    direction: "a_to_b",
    context:
      "Practical question: tension with a boss or subordinate needs a calmer plan. Review role pressure, timing, communication tone, and where to set limits.",
  },
  {
    id: "friend_trust",
    label: "Friend trust",
    relationshipTypeId: "friends",
    direction: "a_to_b",
    context:
      "Practical question: decide how much to trust a friend with a sensitive matter. Review consistency, mutual support, mixed signals, and safer next steps.",
  },
  {
    id: "business_partner_decision",
    label: "Business partner decision",
    relationshipTypeId: "business_partners",
    direction: "a_to_b",
    context:
      "Practical question: evaluate a business partner decision. Review responsibility split, incentives, communication style, and risk boundaries before committing.",
  },
  {
    id: "client_supplier_pressure",
    label: "Client/supplier pressure",
    relationshipTypeId: "client_supplier",
    direction: "a_to_b",
    context:
      "Practical question: client or supplier pressure is affecting the deal. Review leverage, delivery risk, negotiation tone, and fallback options.",
  },
  {
    id: "opponent_conflict_handling",
    label: "Opponent/conflict handling",
    relationshipTypeId: "opponents",
    direction: "a_to_b",
    context:
      "Practical question: handle an opponent or active conflict. Review escalation risk, timing, defensive boundaries, and the least reactive response.",
  },
];
