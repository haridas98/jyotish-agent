from __future__ import annotations

from typing import Any

RASHI_DRISHTI_METHOD_ID = "aspect.rashi_drishti.parashara.v1"
RASHI_DRISHTI_METHOD_VERSION = 1
RASHI_DRISHTI_SOURCE_ANCHOR = "parashara_rashi_drishti"
RASHI_DRISHTI_RULE_MOVABLE_TO_FIXED = "bphs.aspect.rashi_drishti.movable_to_fixed"
RASHI_DRISHTI_RULE_FIXED_TO_MOVABLE = "bphs.aspect.rashi_drishti.fixed_to_movable"
RASHI_DRISHTI_RULE_DUAL_TO_DUAL = "bphs.aspect.rashi_drishti.dual_to_dual"
RASHI_DRISHTI_RULE_GRAHA_PARTICIPATION = "bphs.aspect.rashi_drishti.graha_participation"
RASHI_DRISHTI_SOURCE_RULE_IDS = [
    RASHI_DRISHTI_RULE_MOVABLE_TO_FIXED,
    RASHI_DRISHTI_RULE_FIXED_TO_MOVABLE,
    RASHI_DRISHTI_RULE_DUAL_TO_DUAL,
    RASHI_DRISHTI_RULE_GRAHA_PARTICIPATION,
]

RASHI_ENTITY_NAMES = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]
MOVABLE_RASHIS = {0, 3, 6, 9}
FIXED_RASHIS = {1, 4, 7, 10}
DUAL_RASHIS = {2, 5, 8, 11}


def rashi_drishti_method_contract(method_id: str = RASHI_DRISHTI_METHOD_ID) -> dict[str, Any]:
    if method_id != RASHI_DRISHTI_METHOD_ID:
        raise ValueError(f"unknown aspect method: {method_id}")
    return {
        "methodId": RASHI_DRISHTI_METHOD_ID,
        "methodVersion": RASHI_DRISHTI_METHOD_VERSION,
        "system": "parashara_rashi_drishti",
        "usesSignRelationship": True,
        "usesDegreeOrbs": False,
        "treatsConjunctionAsAspect": False,
        "sourceRuleIds": RASHI_DRISHTI_SOURCE_RULE_IDS,
        "sourceStatus": "verified",
    }


def build_rashi_drishti_aspects(
    source_chart: dict[str, Any],
    target_chart: dict[str, Any],
    *,
    source_context: str = "transit",
    target_context: str = "natal",
    method_id: str = RASHI_DRISHTI_METHOD_ID,
    chart_style: str | None = None,
) -> list[dict[str, Any]]:
    contract = rashi_drishti_method_contract(method_id)
    aspects: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    targets = [*_target_houses(target_chart, target_context), *_target_grahas(target_chart, target_context)]

    for source in _source_rashis(source_chart, source_context):
        target_indices, aspect_kind = _aspected_rashi_indices(source["rashiIndex"])
        for target in targets:
            if target["rashiIndex"] not in target_indices:
                continue
            key = (source["entityRef"], target["entityRef"], aspect_kind)
            if key in seen:
                continue
            seen.add(key)
            aspects.append(
                {
                    **contract,
                    "sourceContext": source_context,
                    "targetContext": target_context,
                    "sourceEntityRef": source["entityRef"],
                    "targetEntityRef": target["entityRef"],
                    "targetKind": target["kind"],
                    "aspectKind": aspect_kind,
                    "sourceRashiIndex": source["rashiIndex"],
                    "targetRashiIndex": target["rashiIndex"],
                    "sourceRuleIds": _source_rule_ids(aspect_kind, target["kind"]),
                }
            )
    return aspects


def _source_rule_ids(aspect_kind: str, target_kind: str) -> list[str]:
    rule_by_kind = {
        "movable_to_fixed": RASHI_DRISHTI_RULE_MOVABLE_TO_FIXED,
        "fixed_to_movable": RASHI_DRISHTI_RULE_FIXED_TO_MOVABLE,
        "dual_to_dual": RASHI_DRISHTI_RULE_DUAL_TO_DUAL,
    }
    rules = [rule_by_kind[aspect_kind]] if aspect_kind in rule_by_kind else []
    if target_kind == "graha":
        rules.append(RASHI_DRISHTI_RULE_GRAHA_PARTICIPATION)
    return rules


def _aspected_rashi_indices(source_rashi_index: int) -> tuple[set[int], str]:
    normalized = int(source_rashi_index) % 12
    if normalized in MOVABLE_RASHIS:
        return FIXED_RASHIS - {((normalized + 1) % 12)}, "movable_to_fixed"
    if normalized in FIXED_RASHIS:
        return MOVABLE_RASHIS - {((normalized - 1) % 12)}, "fixed_to_movable"
    if normalized in DUAL_RASHIS:
        return DUAL_RASHIS - {normalized}, "dual_to_dual"
    return set(), "unknown"


def _source_rashis(chart: dict[str, Any], context: str) -> list[dict[str, Any]]:
    rows = chart.get("grahas") if isinstance(chart, dict) else []
    result: list[dict[str, Any]] = []
    seen: set[int] = set()
    for item in rows if isinstance(rows, list) else []:
        if not isinstance(item, dict):
            continue
        rashi_index = item.get("rashi_index")
        if rashi_index is None:
            continue
        normalized = int(rashi_index) % 12
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append({"rashiIndex": normalized, "entityRef": f"{context}:rashi.{_rashi_name(normalized)}"})
    return result


def _target_grahas(chart: dict[str, Any], context: str) -> list[dict[str, Any]]:
    rows = chart.get("grahas") if isinstance(chart, dict) else []
    result = []
    for item in rows if isinstance(rows, list) else []:
        if not isinstance(item, dict):
            continue
        code = _graha_code(item.get("body"))
        rashi_index = item.get("rashi_index")
        if not code or rashi_index is None:
            continue
        result.append({"kind": "graha", "rashiIndex": int(rashi_index) % 12, "entityRef": f"{context}:graha.{code}"})
    return result


def _target_houses(chart: dict[str, Any], context: str) -> list[dict[str, Any]]:
    rows = chart.get("houses") if isinstance(chart, dict) else []
    result = []
    for item in rows if isinstance(rows, list) else []:
        if not isinstance(item, dict):
            continue
        house = item.get("house")
        rashi_index = item.get("rashi_index")
        if house is None or rashi_index is None:
            continue
        result.append({"kind": "house", "rashiIndex": int(rashi_index) % 12, "entityRef": f"{context}:house.{int(house)}"})
    return result


def _rashi_name(rashi_index: int) -> str:
    return RASHI_ENTITY_NAMES[int(rashi_index) % 12]


def _graha_code(body: object) -> str | None:
    from apps.calculations.graha_drishti import GRAHA_CODES

    return GRAHA_CODES.get(str(body or ""))
