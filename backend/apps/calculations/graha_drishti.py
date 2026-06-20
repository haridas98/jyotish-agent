from __future__ import annotations

from typing import Any

GRAHA_DRISHTI_METHOD_ID = "aspect.graha_drishti.parashara.v1"
GRAHA_DRISHTI_METHOD_VERSION = 1
GRAHA_DRISHTI_SOURCE_ANCHOR = "parashara_graha_drishti"
GRAHA_CODES = {
    "Sun": "SU",
    "Surya": "SU",
    "Moon": "MO",
    "Chandra": "MO",
    "Mars": "MA",
    "Mangala": "MA",
    "Mercury": "ME",
    "Budha": "ME",
    "Jupiter": "JU",
    "Guru": "JU",
    "Venus": "VE",
    "Shukra": "VE",
    "Saturn": "SA",
    "Shani": "SA",
    "Rahu": "RA",
    "Ketu": "KE",
}
ASPECT_RULES = {
    "default": {7: "opposition_7th"},
    "MA": {4: "special_4th", 7: "opposition_7th", 8: "special_8th"},
    "JU": {5: "special_5th", 7: "opposition_7th", 9: "special_9th"},
    "SA": {3: "special_3rd", 7: "opposition_7th", 10: "special_10th"},
}
EXCLUDED_SOURCE_CODES = {"RA", "KE"}


def graha_drishti_method_contract(method_id: str = GRAHA_DRISHTI_METHOD_ID) -> dict[str, Any]:
    if method_id != GRAHA_DRISHTI_METHOD_ID:
        raise ValueError(f"unknown aspect method: {method_id}")
    return {
        "methodId": GRAHA_DRISHTI_METHOD_ID,
        "methodVersion": GRAHA_DRISHTI_METHOD_VERSION,
        "system": "parashara_graha_drishti",
        "usesSignDistance": True,
        "usesDegreeOrbs": False,
        "treatsConjunctionAsAspect": False,
        "includesRahuKetu": False,
        "sourceRuleIds": [],
    }


def build_graha_drishti_aspects(
    source_chart: dict[str, Any],
    target_chart: dict[str, Any],
    *,
    source_context: str = "transit",
    target_context: str = "natal",
    method_id: str = GRAHA_DRISHTI_METHOD_ID,
    chart_style: str | None = None,
) -> list[dict[str, Any]]:
    contract = graha_drishti_method_contract(method_id)
    aspects: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    targets = [*_target_houses(target_chart, target_context), *_target_grahas(target_chart, target_context)]

    for source in _source_grahas(source_chart, source_context):
        rules = ASPECT_RULES.get(source["code"], ASPECT_RULES["default"])
        for target in targets:
            distance = sign_distance(source["rashiIndex"], target["rashiIndex"])
            aspect_kind = rules.get(distance)
            if not aspect_kind:
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
                    "signDistance": distance,
                    "sourceRuleIds": [],
                }
            )
    return aspects


def sign_distance(source_rashi_index: int, target_rashi_index: int) -> int:
    return ((int(target_rashi_index) - int(source_rashi_index)) % 12) + 1


def _source_grahas(chart: dict[str, Any], context: str) -> list[dict[str, Any]]:
    rows = chart.get("grahas") if isinstance(chart, dict) else []
    result = []
    for item in rows if isinstance(rows, list) else []:
        if not isinstance(item, dict):
            continue
        code = _graha_code(item.get("body"))
        if not code or code in EXCLUDED_SOURCE_CODES:
            continue
        rashi_index = item.get("rashi_index")
        if rashi_index is None:
            continue
        result.append({"code": code, "rashiIndex": int(rashi_index), "entityRef": f"{context}:graha.{code}"})
    return result


def _target_grahas(chart: dict[str, Any], context: str) -> list[dict[str, Any]]:
    rows = chart.get("grahas") if isinstance(chart, dict) else []
    result = []
    for item in rows if isinstance(rows, list) else []:
        if not isinstance(item, dict):
            continue
        code = _graha_code(item.get("body"))
        if not code:
            continue
        rashi_index = item.get("rashi_index")
        if rashi_index is None:
            continue
        result.append({"kind": "graha", "rashiIndex": int(rashi_index), "entityRef": f"{context}:graha.{code}"})
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
        result.append({"kind": "house", "rashiIndex": int(rashi_index), "entityRef": f"{context}:house.{int(house)}"})
    return result


def _graha_code(body: object) -> str | None:
    return GRAHA_CODES.get(str(body or ""))
