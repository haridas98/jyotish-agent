export type TimingScenarioPreset = {
  id: string;
  label: string;
  category: "business" | "agreement" | "money" | "conversation" | "travel" | "pause";
  context: string;
  planningFactors: string[];
};

export const timingScenarioPresets: TimingScenarioPreset[] = [
  {
    id: "business_launch_investment_window",
    label: "Business launch / investment window",
    category: "business",
    context:
      "Planning context: compare a few candidate moments for a business action or investment discussion. Note operational readiness, risk limits, and who must approve before acting.",
    planningFactors: ["Moon state", "weekday", "tithi", "nakshatra", "transits"],
  },
  {
    id: "contract_signing_window",
    label: "Contract or signing window",
    category: "agreement",
    context:
      "Planning context: review a signing window for clarity and coordination. Keep legal review, counterpart readiness, and document version control outside the timing note.",
    planningFactors: ["weekday", "tithi", "nakshatra", "transits"],
  },
  {
    id: "lend_money_repayment_caution",
    label: "Lend money / repayment caution",
    category: "money",
    context:
      "Planning context: evaluate whether this is a good moment to discuss lending or repayment terms. Use written boundaries and repayment clarity; this note is not financial advice.",
    planningFactors: ["Moon state", "weekday", "tithi", "transits"],
  },
  {
    id: "difficult_conversation",
    label: "Difficult conversation",
    category: "conversation",
    context:
      "Planning context: choose a calmer window for a difficult conversation. Define the topic, limits, desired tone, and what can wait if the moment feels reactive.",
    planningFactors: ["Moon state", "weekday", "nakshatra", "transits"],
  },
  {
    id: "travel_move_planning",
    label: "Travel or move planning",
    category: "travel",
    context:
      "Planning context: compare possible travel or move times against logistics, fatigue, and contingency needs. Keep tickets, documents, and weather checks separate.",
    planningFactors: ["weekday", "tithi", "nakshatra", "transits"],
  },
  {
    id: "quiet_day_postpone",
    label: "Quiet day / postpone non-urgent action",
    category: "pause",
    context:
      "Planning context: mark this as a quieter day for review, cleanup, or postponing non-urgent action. Use it to reduce pressure, not to predict an outcome.",
    planningFactors: ["Moon state", "weekday", "tithi", "nakshatra"],
  },
];
