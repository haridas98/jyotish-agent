from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from statistics import mean, median, pstdev
from typing import Any

from .primitives import normalize_degrees


@dataclass(frozen=True)
class LongitudeComparison:
    body: str
    expected_degrees: float
    actual_degrees: float
    signed_delta_arcseconds: float
    delta_arcseconds: float
    tolerance_arcseconds: float
    passed: bool


@dataclass(frozen=True)
class ChartAccuracyReport:
    fixture_id: str
    longitude_comparisons: list[LongitudeComparison]
    exact_matches: dict[str, bool]
    missing_fields: list[str]
    passed: bool
    diagnostics: dict[str, Any] = dataclass_field(default_factory=dict)


def angular_delta_arcseconds(left_degrees: float, right_degrees: float) -> float:
    left = normalize_degrees(left_degrees)
    right = normalize_degrees(right_degrees)
    delta_degrees = abs(left - right)
    shortest_delta = min(delta_degrees, 360.0 - delta_degrees)
    return round(shortest_delta * 3600.0, 6)


def signed_angular_delta_arcseconds(expected_degrees: float, actual_degrees: float) -> float:
    expected = normalize_degrees(expected_degrees)
    actual = normalize_degrees(actual_degrees)
    delta = (actual - expected + 180.0) % 360.0 - 180.0
    return round(delta * 3600.0, 6)


def compare_longitude(
    body: str,
    expected_degrees: float,
    actual_degrees: float,
    tolerance_arcseconds: float,
) -> LongitudeComparison:
    delta = angular_delta_arcseconds(expected_degrees, actual_degrees)
    return LongitudeComparison(
        body=body,
        expected_degrees=normalize_degrees(expected_degrees),
        actual_degrees=normalize_degrees(actual_degrees),
        signed_delta_arcseconds=signed_angular_delta_arcseconds(expected_degrees, actual_degrees),
        delta_arcseconds=delta,
        tolerance_arcseconds=tolerance_arcseconds,
        passed=delta <= tolerance_arcseconds,
    )


def compare_chart_to_fixture(chart: dict[str, Any], fixture: dict[str, Any]) -> ChartAccuracyReport:
    expected = fixture.get("expected", {})
    tolerances = fixture.get("tolerances", {})
    planet_tolerance = float(tolerances.get("planet_longitude_arcseconds", 1.0))
    lagna_tolerance = float(tolerances.get("lagna_arcseconds", planet_tolerance))
    comparisons: list[LongitudeComparison] = []
    exact_matches: dict[str, bool] = {}
    missing_fields: list[str] = []

    actual_grahas = {
        graha.get("body"): graha
        for graha in chart.get("grahas", [])
        if isinstance(graha, dict) and graha.get("body")
    }
    for body, expected_graha in expected.get("grahas", {}).items():
        actual = actual_grahas.get(body)
        if actual is None:
            missing_fields.append(f"grahas.{body}")
            continue
        comparisons.append(
            compare_longitude(
                body=body,
                expected_degrees=float(expected_graha["longitude"]),
                actual_degrees=float(actual["longitude"]),
                tolerance_arcseconds=planet_tolerance,
            )
        )
        _compare_exact(exact_matches, missing_fields, f"{body}.rashi", actual, expected_graha, "rashi")
        _compare_exact(
            exact_matches,
            missing_fields,
            f"{body}.nakshatra",
            actual,
            expected_graha,
            "nakshatra",
        )
        _compare_exact(exact_matches, missing_fields, f"{body}.pada", actual, expected_graha, "pada")

    expected_ascendant = expected.get("ascendant")
    if expected_ascendant:
        actual_ascendant = chart.get("ascendant")
        if not actual_ascendant:
            missing_fields.append("ascendant")
        else:
            comparisons.append(
                compare_longitude(
                    body="Lagna",
                    expected_degrees=float(expected_ascendant["longitude"]),
                    actual_degrees=float(actual_ascendant["longitude"]),
                    tolerance_arcseconds=lagna_tolerance,
                )
            )
            _compare_exact(
                exact_matches,
                missing_fields,
                "Lagna.rashi",
                actual_ascendant,
                expected_ascendant,
                "rashi",
            )

    _compare_panchanga(chart, expected, exact_matches, missing_fields)
    _compare_vargas(chart, expected, exact_matches, missing_fields)
    passed = (
        not missing_fields
        and all(comparison.passed for comparison in comparisons)
        and all(exact_matches.values())
    )
    return ChartAccuracyReport(
        fixture_id=str(fixture.get("id", "")),
        longitude_comparisons=comparisons,
        exact_matches=exact_matches,
        missing_fields=missing_fields,
        diagnostics=_diagnostics(comparisons),
        passed=passed,
    )


def _diagnostics(comparisons: list[LongitudeComparison]) -> dict[str, Any]:
    if not comparisons:
        return {}
    signed = [comparison.signed_delta_arcseconds for comparison in comparisons]
    absolute = [comparison.delta_arcseconds for comparison in comparisons]
    signed_stddev = round(pstdev(signed), 6)
    return {
        "mean_signed_delta_arcseconds": round(mean(signed), 6),
        "median_abs_delta_arcseconds": round(median(absolute), 6),
        "max_abs_delta_arcseconds": round(max(absolute), 6),
        "signed_delta_stddev_arcseconds": signed_stddev,
        "systematic_offset_suspected": len(comparisons) >= 3
        and median(absolute) >= 10.0
        and signed_stddev <= 2.0,
    }


def _compare_exact(
    exact_matches: dict[str, bool],
    missing_fields: list[str],
    key: str,
    actual: dict[str, Any],
    expected: dict[str, Any],
    field: str,
) -> None:
    if field not in expected:
        return
    if field not in actual:
        missing_fields.append(key)
        return
    exact_matches[key] = actual[field] == expected[field]


def _compare_panchanga(
    chart: dict[str, Any],
    expected: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
) -> None:
    expected_panchanga = expected.get("panchanga", {})
    actual_panchanga = chart.get("panchanga", {})
    for field in ("tithi", "vara", "yoga", "karana"):
        if field not in expected_panchanga:
            continue
        actual_value = actual_panchanga.get(field, {}).get("name")
        key = f"panchanga.{field}"
        if actual_value is None:
            missing_fields.append(key)
            continue
        exact_matches[key] = actual_value == expected_panchanga[field]


def _compare_vargas(
    chart: dict[str, Any],
    expected: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
) -> None:
    expected_vargas = expected.get("vargas", {})
    if not isinstance(expected_vargas, dict):
        return
    actual_vargas = chart.get("vargas", {})
    if not isinstance(actual_vargas, dict):
        actual_vargas = {}

    for code, expected_placements in expected_vargas.items():
        actual_varga = actual_vargas.get(code)
        if not isinstance(actual_varga, dict):
            missing_fields.append(f"vargas.{code}")
            continue
        actual_placements = {
            placement.get("body"): placement
            for placement in actual_varga.get("placements", [])
            if isinstance(placement, dict) and placement.get("body")
        }
        if not isinstance(expected_placements, dict):
            continue
        for body, expected_placement in expected_placements.items():
            actual_placement = actual_placements.get(body)
            if actual_placement is None:
                missing_fields.append(f"vargas.{code}.{body}")
                continue
            if not isinstance(expected_placement, dict):
                continue
            for field in ("rashi", "rashi_index"):
                _compare_exact(
                    exact_matches,
                    missing_fields,
                    f"{code}.{body}.{field}",
                    actual_placement,
                    expected_placement,
                    field,
                )
