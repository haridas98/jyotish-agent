from __future__ import annotations

from dataclasses import dataclass

from .primitives import normalize_degrees


@dataclass(frozen=True)
class LongitudeComparison:
    body: str
    expected_degrees: float
    actual_degrees: float
    delta_arcseconds: float
    tolerance_arcseconds: float
    passed: bool


def angular_delta_arcseconds(left_degrees: float, right_degrees: float) -> float:
    left = normalize_degrees(left_degrees)
    right = normalize_degrees(right_degrees)
    delta_degrees = abs(left - right)
    shortest_delta = min(delta_degrees, 360.0 - delta_degrees)
    return round(shortest_delta * 3600.0, 6)


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
        delta_arcseconds=delta,
        tolerance_arcseconds=tolerance_arcseconds,
        passed=delta <= tolerance_arcseconds,
    )
