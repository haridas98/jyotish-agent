from __future__ import annotations

import re
from typing import Any

from .accuracy import compare_longitude
from .constants import RASHIS

BODY_ALIASES = {
    "Asc": "Lagna",
    "Ascendant": "Lagna",
    "Lagna": "Lagna",
    "Sun": "Surya",
    "Moon": "Chandra",
    "Mars": "Mangala",
    "Mercury": "Budha",
    "Jupiter": "Guru",
    "Venus": "Shukra",
    "Saturn": "Shani",
    "Rahu": "Rahu",
    "Ketu": "Ketu",
    "Surya": "Surya",
    "Chandra": "Chandra",
    "Mangala": "Mangala",
    "Budha": "Budha",
    "Guru": "Guru",
    "Shukra": "Shukra",
    "Shani": "Shani",
}

EXACT_FIELDS = ("rashi", "nakshatra", "pada", "house")


def compare_manual_witness_values(
    chart: dict[str, Any],
    witness_values: list[dict[str, Any]],
    *,
    default_longitude_tolerance_arcseconds: float = 60.0,
) -> dict[str, Any]:
    values = [value for value in witness_values if isinstance(value, dict)]
    if not values:
        return {
            "status": "no_manual_values",
            "summary": {
                "manual_values_count": 0,
                "checked_count": 0,
                "passed_count": 0,
                "failed_count": 0,
                "missing_count": 0,
            },
            "diffs": [],
        }

    bodies = _chart_body_index(chart)
    houses_by_rashi = _houses_by_rashi(chart)
    diffs: list[dict[str, Any]] = []
    checked = 0
    passed = 0
    missing = 0

    for witness in values:
        source = str(witness.get("source") or "")
        body = _normalize_body(witness.get("body"))
        calculated = bodies.get(body)
        if calculated is None:
            missing += 1
            diffs.append(
                {
                    "source": source,
                    "body": body,
                    "field": "body",
                    "witness": witness.get("body"),
                    "calculated": None,
                    "passed": False,
                    "missing": True,
                }
            )
            continue

        calculated_with_house = dict(calculated)
        calculated_with_house["house"] = _calculated_house(body, calculated, houses_by_rashi)

        for field in EXACT_FIELDS:
            if field not in witness:
                continue
            checked += 1
            witness_value = witness.get(field)
            calculated_value = calculated_with_house.get(field)
            if _normalize_exact(witness_value) == _normalize_exact(calculated_value):
                passed += 1
                continue
            diffs.append(
                {
                    "source": source,
                    "body": body,
                    "field": field,
                    "witness": witness_value,
                    "calculated": calculated_value,
                    "passed": False,
                }
            )

        witness_longitude = _witness_longitude(witness)
        if witness_longitude is None:
            continue
        actual_longitude = _float_or_none(calculated.get("longitude"))
        if actual_longitude is None:
            missing += 1
            diffs.append(
                {
                    "source": source,
                    "body": body,
                    "field": "longitude",
                    "witness": witness_longitude,
                    "calculated": None,
                    "passed": False,
                    "missing": True,
                }
            )
            continue
        checked += 1
        tolerance = _float_or_none(witness.get("longitude_tolerance_arcseconds"))
        comparison = compare_longitude(
            body,
            expected_degrees=witness_longitude,
            actual_degrees=actual_longitude,
            tolerance_arcseconds=tolerance if tolerance is not None else default_longitude_tolerance_arcseconds,
        )
        if comparison.passed:
            passed += 1
            continue
        diffs.append(
            {
                "source": source,
                "body": body,
                "field": "longitude",
                "witness": round(comparison.expected_degrees, 6),
                "calculated": round(comparison.actual_degrees, 6),
                "delta_arcseconds": comparison.delta_arcseconds,
                "tolerance_arcseconds": comparison.tolerance_arcseconds,
                "passed": False,
            }
        )

    failed = len([diff for diff in diffs if not diff.get("missing")])
    status = "diff_open" if failed else "matched" if checked else "no_checked_fields"
    return {
        "status": status,
        "summary": {
            "manual_values_count": len(values),
            "checked_count": checked,
            "passed_count": passed,
            "failed_count": failed,
            "missing_count": missing,
        },
        "diffs": diffs,
    }


def _chart_body_index(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    bodies: dict[str, dict[str, Any]] = {}
    ascendant = chart.get("ascendant")
    if isinstance(ascendant, dict):
        bodies["Lagna"] = ascendant
    for graha in chart.get("grahas") or []:
        if isinstance(graha, dict) and graha.get("body"):
            bodies[str(graha["body"])] = graha
    return bodies


def _houses_by_rashi(chart: dict[str, Any]) -> dict[int, int]:
    houses: dict[int, int] = {}
    for row in chart.get("houses") or []:
        if not isinstance(row, dict):
            continue
        rashi_index = _rashi_index(row)
        house = _int_or_none(row.get("house"))
        if rashi_index is not None and house is not None:
            houses[rashi_index] = house
    return houses


def _calculated_house(body: str, calculated: dict[str, Any], houses_by_rashi: dict[int, int]) -> int | None:
    if body == "Lagna":
        return 1
    rashi_index = _rashi_index(calculated)
    if rashi_index is None:
        return None
    return houses_by_rashi.get(rashi_index)


def _normalize_body(value: object) -> str:
    return BODY_ALIASES.get(str(value or "").strip(), str(value or "").strip())


def _normalize_exact(value: object) -> object:
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _witness_longitude(witness: dict[str, Any]) -> float | None:
    longitude = _float_or_none(witness.get("longitude"))
    if longitude is not None:
        return longitude
    dms = witness.get("longitude_dms") or witness.get("degree_dms") or witness.get("degrees_in_sign")
    sign_degrees = _parse_dms(dms)
    if sign_degrees is None:
        return None
    rashi_index = _rashi_index(witness)
    return sign_degrees if rashi_index is None else rashi_index * 30.0 + sign_degrees


def _parse_dms(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    pieces = [piece for piece in re.split(r"[^0-9.]+", str(value).strip()) if piece]
    if not pieces:
        return None
    degrees = float(pieces[0])
    minutes = float(pieces[1]) if len(pieces) > 1 else 0.0
    seconds = float(pieces[2]) if len(pieces) > 2 else 0.0
    return degrees + minutes / 60.0 + seconds / 3600.0


def _rashi_index(row: dict[str, Any]) -> int | None:
    raw = _int_or_none(row.get("rashi_index"))
    if raw is not None:
        return raw
    rashi = row.get("rashi")
    if isinstance(rashi, str) and rashi in RASHIS:
        return RASHIS.index(rashi)
    return None


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
