import type { BirthChart, GrahaPosition } from "@/lib/api";
import type { AiEvidencePack, AiFactor, EvidenceBuilderContext } from "../types";

export function buildSingleChartEvidencePack(chart: BirthChart, context: EvidenceBuilderContext): AiEvidencePack {
  const sun = findGraha(chart, "Surya", "Sun");
  const moon = findGraha(chart, "Chandra", "Moon");
  const ascendant = chart.ascendant;
  const currentDasha = chart.dashas?.vimshottari?.mahadashas?.[0] ?? null;
  const factors: AiFactor[] = [];

  if (ascendant) {
    factors.push({
      entityId: "house.1",
      calcId: "calc.houses",
      value: compactPlacement(ascendant),
      relevance: "primary",
      reason: "Lagna is the base reference for body, temperament, house structure and chart strength.",
      sourceRuleIds: ["bphs.house.1"],
    });
  }

  if (sun) {
    factors.push({
      entityId: `placement.SU.house.${houseForGraha(chart, sun) ?? "unknown"}`,
      calcId: "calc.planetPositions",
      value: compactPlacement(sun),
      relevance: "secondary",
      reason: "Surya is relevant for authority, father, status and vitality; house and rashi refine the result.",
      sourceRuleIds: ["bphs.graha.surya"],
    });
  }

  if (moon) {
    factors.push({
      entityId: `placement.MO.house.${houseForGraha(chart, moon) ?? "unknown"}`,
      calcId: "calc.nakshatras",
      value: compactPlacement(moon),
      relevance: "primary",
      reason: "Chandra and nakshatra anchor the mind, panchanga and Vimshottari timing.",
      sourceRuleIds: ["bphs.graha.chandra", "vimshottari.moon.nakshatra"],
    });
  }

  if (currentDasha) {
    factors.push({
      entityId: `dasha.vimshottari.${currentDasha.lord}`,
      calcId: "calc.vimshottari",
      value: currentDasha,
      relevance: "primary",
      reason: "The active Vimshottari period indicates which natal promises are being timed.",
      sourceRuleIds: ["vimshottari.sequence"],
    });
  }

  return {
    subject: "single_chart",
    profiles: context.profileIds,
    question: context.question,
    calculationPreset: context.preset ?? {
      ayanamsha: chart.settings?.ayanamsa,
      nodeMode: chart.settings?.node_type === "mean" ? "mean" : "true",
      houseSystem: chart.settings?.house_system,
      vargaScheme: chart.settings?.varga_scheme,
      source: "profile",
    },
    factors,
    warnings: chart.birth.time ? [] : [{ code: "birth_time_missing", message: "Birth time is missing; houses and vargas may be unreliable.", severity: "critical" }],
    sourceRules: [
      { sourceId: "bphs", ruleId: "bphs.house.1", entityId: "house.1", status: "pending" },
      { sourceId: "bphs", ruleId: "bphs.graha.surya", entityId: "graha.SU", status: "pending" },
      { sourceId: "bphs", ruleId: "bphs.graha.chandra", entityId: "graha.MO", status: "pending" },
      { sourceId: "tradition", ruleId: "vimshottari.sequence", status: "pending" },
    ],
  };
}

function findGraha(chart: BirthChart, ...names: string[]) {
  return chart.grahas.find((graha) => names.includes(graha.body)) ?? null;
}

function compactPlacement(placement: GrahaPosition) {
  return {
    body: placement.body,
    rashi: placement.rashi,
    rashi_index: placement.rashi_index,
    nakshatra: placement.nakshatra,
    pada: placement.pada,
    navamsa: placement.navamsa,
  };
}

function houseForGraha(chart: BirthChart, graha: GrahaPosition) {
  const rashiIndex = normalizeRashiIndex(graha.rashi_index);
  if (rashiIndex === null) return null;
  return chart.houses.find((house) => normalizeRashiIndex(house.rashi_index) === rashiIndex)?.house ?? null;
}

function normalizeRashiIndex(index: number | null | undefined) {
  if (index === null || index === undefined) return null;
  if (index >= 0 && index <= 11) return index + 1;
  if (index >= 1 && index <= 12) return index;
  return null;
}
