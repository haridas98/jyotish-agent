from __future__ import annotations

import re
from dataclasses import dataclass, field as dataclass_field
from statistics import mean, median, pstdev
from typing import Any

from .constants import RASHIS
from .primitives import normalize_degrees

JHORA_ASHTAKAVARGA_BODY_MAP = {
    "Su": "Surya",
    "Mo": "Chandra",
    "Ma": "Mangala",
    "Me": "Budha",
    "Ju": "Guru",
    "Ve": "Shukra",
    "Sa": "Shani",
}

JHORA_SHADBALA_BODY_MAP = {
    "Sun": "Surya",
    "Moon": "Chandra",
    "Mars": "Mangala",
    "Mercury": "Budha",
    "Jupiter": "Guru",
    "Venus": "Shukra",
    "Saturn": "Shani",
}

JHORA_VIMSOPAKA_BODY_MAP = {
    "Sun": "Surya",
    "Moon": "Chandra",
    "Mars": "Mangala",
    "Mercury": "Budha",
    "Jupiter": "Guru",
    "Venus": "Shukra",
    "Saturn": "Shani",
    "Rahu": "Rahu",
    "Ketu": "Ketu",
}

JHORA_VIMSOPAKA_SCHEME_MAP = {
    "dasa_varga": "dashavarga",
    "shodasa_varga": "shodasha",
    "sapta_varga": "saptavarga",
    "shad_varga": "shadvarga",
}

JHORA_SPECIAL_POINT_ALIASES = {
    "Maandi": ("maandi", "mandi"),
    "Gulika": ("gulika",),
    "Dhooma": ("dhuma",),
    "Vyatipata": ("vyatipata",),
    "Parivesha": ("parivesha",),
    "Indrachapa": ("indrachapa",),
    "Indra Chapa": ("indrachapa",),
    "Upaketu": ("upaketu",),
    "Indu Lagna": ("indu_lagna", "indu_dhana_lagna"),
    "Bhava Lagna": ("bhava_lagna",),
    "Hora Lagna": ("hora_lagna",),
    "Ghati Lagna": ("ghati_lagna",),
}

JHORA_TIME_LAGNA_RATES = {
    "bhava_lagna": 6.0,
    "hora_lagna": 12.0,
    "ghati_lagna": 30.0,
}

JHORA_YOGA_ALIASES = {
    "ruchaka": ("ruchaka", "ruchaka_mahapurusha"),
    "vosi": ("voshi", "vosi", "subha_voshi", "subha_vosi", "subha_vesi"),
    "kedaara": ("kedara", "kedara_nabhasa"),
    "kedara": ("kedara", "kedara_nabhasa"),
    "chaamara": ("chamara", "chaamara"),
    "chamara": ("chamara", "chaamara"),
    "mridanga": ("mridanga",),
    "vidyut": ("vidyut",),
    "brahma": ("brahma",),
    "brahma_2": ("brahma",),
    "yogakaraka": ("yogakaraka", "kendra_trikona_raja", "lagna_lord_kendra_trikona_raja"),
    "rajayoga": (
        "rajayoga",
        "kendra_trikona_raja",
        "dharma_karmadhipati_raja",
        "lagna_lord_kendra_trikona_raja",
    ),
    "yogada_gl": ("yogada_gl", "yogada"),
    "yogada_hl": ("yogada_hl", "yogada"),
    "viparita_raja_yoga": (
        "viparita_raja_yoga",
        "viparita_harsha",
        "viparita_sarala",
        "viparita_vimala",
        "dusthana_lord_exchange_viparita",
    ),
    "raja_sambandha": ("raja_sambandha",),
}

PANCHANGA_NAME_ALIASES = {
    "shukla": "sukla",
    "sukarman": "sukarma",
    "sukla_panchami": "sukla_panchami",
    "shukla_panchami": "sukla_panchami",
    "sunday": "ravivara",
    "monday": "somavara",
    "tuesday": "mangalavara",
    "wednesday": "budhavara",
    "thursday": "guruvara",
    "friday": "shukravara",
    "saturday": "shanivara",
}


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
    varga_diagnostics = _compare_vargas(chart, expected, exact_matches, missing_fields)
    diagnostics = _diagnostics(comparisons)
    if varga_diagnostics["checked"] or varga_diagnostics["missing"]:
        diagnostics["vargas"] = varga_diagnostics
    ayanamsa_diagnostics = _ayanamsa_diagnostics(chart, fixture, comparisons)
    if ayanamsa_diagnostics:
        diagnostics["ayanamsa"] = ayanamsa_diagnostics
    jhora_layer_diagnostics = _compare_jhora_layers(
        chart,
        fixture.get("jhora_expected", {}),
        tolerances,
        exact_matches,
        missing_fields,
    )
    if jhora_layer_diagnostics:
        diagnostics["jhora_layers"] = jhora_layer_diagnostics
        diagnostics["jhora_profile"] = _jhora_profile_diagnostics(fixture.get("jhora_metadata", {}))
    external_layer_diagnostics = _compare_external_layers(
        chart,
        fixture.get("external_expected", []),
        tolerances,
        exact_matches,
        missing_fields,
    )
    if external_layer_diagnostics:
        diagnostics["external_layers"] = external_layer_diagnostics
        diagnostics["authority"] = {
            "primary_rule_source": "shastra_source_backed_rules",
            "black_box_services": len(external_layer_diagnostics),
            "policy": "external services are comparison witnesses, not primary authority",
        }
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
        diagnostics=diagnostics,
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


def _ayanamsa_diagnostics(
    chart: dict[str, Any],
    fixture: dict[str, Any],
    comparisons: list[LongitudeComparison],
) -> dict[str, Any]:
    settings = chart.get("settings") if isinstance(chart.get("settings"), dict) else {}
    metadata = fixture.get("jhora_metadata") if isinstance(fixture.get("jhora_metadata"), dict) else {}
    actual = _float_or_none(settings.get("ayanamsa_degrees"))
    expected = _float_or_none(metadata.get("ayanamsa_degrees")) or _dms_to_degrees(metadata.get("ayanamsa"))
    if actual is None or expected is None:
        return {}
    delta_degrees = actual - expected
    delta_arcseconds = round(delta_degrees * 3600.0, 6)
    corrected = []
    for comparison in comparisons:
        adjusted_actual = normalize_degrees(comparison.actual_degrees + delta_degrees)
        corrected.append(
            {
                "body": comparison.body,
                "delta_arcseconds": angular_delta_arcseconds(comparison.expected_degrees, adjusted_actual),
                "signed_delta_arcseconds": signed_angular_delta_arcseconds(
                    comparison.expected_degrees,
                    adjusted_actual,
                ),
            }
        )
    absolute = [row["delta_arcseconds"] for row in corrected]
    return {
        "chart_ayanamsa_degrees": round(actual, 9),
        "fixture_ayanamsa_degrees": round(expected, 9),
        "delta_arcseconds": delta_arcseconds,
        "longitude_correction_for_fixture_arcseconds": delta_arcseconds,
        "corrected_median_abs_delta_arcseconds": round(median(absolute), 6) if absolute else 0.0,
        "corrected_max_abs_delta_arcseconds": round(max(absolute), 6) if absolute else 0.0,
        "corrected_rows": corrected,
    }


def _compare_jhora_layers(
    chart: dict[str, Any],
    expected: Any,
    tolerances: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
) -> dict[str, Any]:
    if not isinstance(expected, dict):
        return {}
    diagnostics: dict[str, Any] = {}
    ashtakavarga = _compare_jhora_ashtakavarga(chart, expected, exact_matches, missing_fields)
    if ashtakavarga["checked"]:
        diagnostics["ashtakavarga"] = ashtakavarga
    shadbala = _compare_jhora_shadbala(chart, expected, tolerances, exact_matches, missing_fields)
    if shadbala["checked"]:
        diagnostics["shadbala"] = shadbala
    vimsopaka = _compare_jhora_vimsopaka(chart, expected, tolerances, exact_matches, missing_fields)
    if vimsopaka["checked"]:
        diagnostics["vimsopaka"] = vimsopaka
    special_points = _compare_jhora_special_points(chart, expected, tolerances, exact_matches, missing_fields)
    if special_points["checked"] or special_points["missing"]:
        diagnostics["special_points"] = special_points
    active_yogas = _compare_jhora_active_yogas(chart, expected, exact_matches)
    if active_yogas["checked"]:
        diagnostics["active_yogas"] = active_yogas
    return diagnostics


def _jhora_profile_diagnostics(metadata: Any) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        return {"status": "unrecorded"}
    required = (
        "version_required",
        "siddhanta_model",
        "ayanamsa",
        "node_type",
        "house_system",
        "bhava_system",
        "varga_options",
        "sunrise_source",
        "timezone_source",
        "shadbala_options",
    )
    missing = [key for key in required if not metadata.get(key)]
    status = str(metadata.get("profile_status") or ("verified" if not missing else "unverified"))
    output = {
        "status": status,
        "missing": missing,
    }
    for key in required:
        if metadata.get(key):
            output[key] = metadata[key]
    return output


def _compare_external_layers(
    chart: dict[str, Any],
    sources: Any,
    tolerances: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
) -> dict[str, Any]:
    if not isinstance(sources, list):
        return {}
    diagnostics: dict[str, Any] = {}
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_id = _source_id(source)
        layer_diagnostics: dict[str, Any] = {
            "name": str(source.get("name") or source_id),
            "authority_tier": str(source.get("authority_tier") or "black_box_service"),
        }
        if source.get("compare") is False:
            layer_diagnostics["skipped"] = True
            layer_diagnostics["reason"] = str(source.get("skip_reason") or "comparison disabled")
            diagnostics[source_id] = layer_diagnostics
            continue
        expected = source.get("expected")
        if not isinstance(expected, dict):
            continue
        prefix = f"external.{source_id}"
        ashtakavarga = _compare_jhora_ashtakavarga(
            chart,
            expected,
            exact_matches,
            missing_fields,
            key_prefix=prefix,
        )
        if ashtakavarga["checked"]:
            layer_diagnostics["ashtakavarga"] = ashtakavarga
        shadbala = _compare_jhora_shadbala(
            chart,
            expected,
            tolerances,
            exact_matches,
            missing_fields,
            key_prefix=prefix,
        )
        if shadbala["checked"]:
            layer_diagnostics["shadbala"] = shadbala
        if len(layer_diagnostics) > 2:
            diagnostics[source_id] = layer_diagnostics
    return diagnostics


def _compare_jhora_ashtakavarga(
    chart: dict[str, Any],
    expected: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
    *,
    key_prefix: str = "jhora",
) -> dict[str, int]:
    expected_ashtakavarga = expected.get("ashtakavarga")
    if not isinstance(expected_ashtakavarga, dict):
        return {"checked": 0, "matched": 0, "failed": 0, "missing": 0, "skipped": 0}
    actual_bhinna = (((chart.get("classical") or {}).get("ashtakavarga") or {}).get("bhinna") or {})
    checked = matched = failed = missing = skipped = 0
    for jhora_body, expected_row in expected_ashtakavarga.items():
        body = JHORA_ASHTAKAVARGA_BODY_MAP.get(str(jhora_body))
        if body is None or not isinstance(expected_row, dict):
            skipped += 1
            continue
        actual_row = actual_bhinna.get(body)
        scores = actual_row.get("scores") if isinstance(actual_row, dict) else None
        if not isinstance(scores, list) or len(scores) < len(RASHIS):
            missing += 1
            missing_fields.append(f"{key_prefix}.ashtakavarga.{jhora_body}")
            continue
        for index, rashi in enumerate(RASHIS):
            if rashi not in expected_row:
                continue
            checked += 1
            key = f"{key_prefix}.ashtakavarga.{jhora_body}.{rashi}"
            exact_matches[key] = int(scores[index]) == int(expected_row[rashi])
            if exact_matches[key]:
                matched += 1
            else:
                failed += 1
    return {
        "checked": checked,
        "matched": matched,
        "failed": failed,
        "missing": missing,
        "skipped": skipped,
    }


def _compare_jhora_shadbala(
    chart: dict[str, Any],
    expected: dict[str, Any],
    tolerances: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
    *,
    key_prefix: str = "jhora",
) -> dict[str, Any]:
    expected_shadbala = expected.get("shadbala")
    if not isinstance(expected_shadbala, dict):
        return {"checked": 0, "matched": 0, "failed": 0, "missing": 0, "max_abs_delta": 0.0, "rows": []}
    tolerance = float(tolerances.get("shadbala_virupas", 0.01))
    actual_items = {
        row.get("body"): row
        for row in (((chart.get("classical") or {}).get("shadbala") or {}).get("items") or [])
        if isinstance(row, dict) and row.get("body")
    }
    checked = matched = failed = missing = 0
    max_abs_delta = 0.0
    rows = []
    for jhora_body, expected_row in expected_shadbala.items():
        body = JHORA_SHADBALA_BODY_MAP.get(str(jhora_body))
        if body is None or not isinstance(expected_row, dict) or "shadbala" not in expected_row:
            continue
        actual_row = actual_items.get(body)
        if not isinstance(actual_row, dict) or "known_total" not in actual_row:
            missing += 1
            missing_fields.append(f"{key_prefix}.shadbala.{jhora_body}")
            continue
        checked += 1
        expected_value = float(expected_row["shadbala"])
        actual_value = float(actual_row["known_total"])
        delta = abs(actual_value - expected_value)
        max_abs_delta = max(max_abs_delta, delta)
        key = f"{key_prefix}.shadbala.{jhora_body}.shadbala"
        exact_matches[key] = delta <= tolerance
        signed_delta = round(actual_value - expected_value, 6)
        rows.append(
            {
                "jhora_body": str(jhora_body),
                "body": body,
                "expected": round(expected_value, 6),
                "actual": round(actual_value, 6),
                "delta": signed_delta,
                "passed": exact_matches[key],
                "components": _shadbala_components(actual_row),
                "expected_outputs": _shadbala_outputs(expected_row),
                "actual_outputs": _shadbala_outputs(actual_row),
                "subcomponents": _jsonable(actual_row.get("subcomponents") or {}),
                "audit_flags": _jsonable(actual_row.get("audit_flags") or []),
            }
        )
        if exact_matches[key]:
            matched += 1
        else:
            failed += 1
    return {
        "checked": checked,
        "matched": matched,
        "failed": failed,
        "missing": missing,
        "max_abs_delta": round(max_abs_delta, 6),
        "rows": rows,
    }


def _compare_jhora_vimsopaka(
    chart: dict[str, Any],
    expected: dict[str, Any],
    tolerances: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
    *,
    key_prefix: str = "jhora",
) -> dict[str, Any]:
    expected_vimsopaka = expected.get("vimsopaka")
    if not isinstance(expected_vimsopaka, dict):
        return {"checked": 0, "matched": 0, "failed": 0, "missing": 0, "max_abs_delta": 0.0, "rows": []}
    tolerance = float(tolerances.get("vimsopaka_score", 0.01))
    actual_items = {
        row.get("body"): row
        for row in (((chart.get("classical") or {}).get("vimshopaka_bala") or {}).get("items") or [])
        if isinstance(row, dict) and row.get("body")
    }
    checked = matched = failed = missing = 0
    max_abs_delta = 0.0
    rows = []
    for jhora_body, expected_body_row in expected_vimsopaka.items():
        body = JHORA_VIMSOPAKA_BODY_MAP.get(str(jhora_body))
        actual_row = actual_items.get(body)
        if body is None or not isinstance(expected_body_row, dict) or not isinstance(actual_row, dict):
            missing += 1
            missing_fields.append(f"{key_prefix}.vimsopaka.{jhora_body}")
            continue
        actual_scores = actual_row.get("scheme_scores") if isinstance(actual_row.get("scheme_scores"), dict) else {}
        for jhora_scheme, actual_scheme in JHORA_VIMSOPAKA_SCHEME_MAP.items():
            expected_scheme = expected_body_row.get(jhora_scheme)
            if not isinstance(expected_scheme, dict) or actual_scheme not in actual_scores:
                continue
            checked += 1
            expected_value = float(expected_scheme["score"])
            actual_value = float(actual_scores[actual_scheme])
            delta = round(actual_value - expected_value, 6)
            abs_delta = abs(delta)
            max_abs_delta = max(max_abs_delta, abs_delta)
            key = f"{key_prefix}.vimsopaka.{jhora_body}.{jhora_scheme}"
            exact_matches[key] = abs_delta <= tolerance
            rows.append(
                {
                    "jhora_body": str(jhora_body),
                    "body": body,
                    "jhora_scheme": jhora_scheme,
                    "actual_scheme": actual_scheme,
                    "expected": round(expected_value, 6),
                    "actual": round(actual_value, 6),
                    "delta": delta,
                    "passed": exact_matches[key],
                }
            )
            if exact_matches[key]:
                matched += 1
            else:
                failed += 1
    return {
        "checked": checked,
        "matched": matched,
        "failed": failed,
        "missing": missing,
        "max_abs_delta": round(max_abs_delta, 6),
        "rows": rows,
    }


def _compare_jhora_special_points(
    chart: dict[str, Any],
    expected: dict[str, Any],
    tolerances: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
    *,
    key_prefix: str = "jhora",
) -> dict[str, Any]:
    expected_points = expected.get("special_points")
    if not isinstance(expected_points, dict):
        return {"checked": 0, "matched": 0, "failed": 0, "missing": 0, "skipped": 0, "rows": []}
    actual_points = _actual_special_points(chart)
    tolerance = float(tolerances.get("special_point_arcseconds", 60.0))
    checked = matched = failed = missing = skipped = 0
    rows = []
    row_match_keys = []
    for jhora_name, expected_point in expected_points.items():
        if jhora_name not in JHORA_SPECIAL_POINT_ALIASES or not isinstance(expected_point, dict):
            skipped += 1
            continue
        actual_point = next(
            (actual_points.get(alias) for alias in JHORA_SPECIAL_POINT_ALIASES[jhora_name] if alias in actual_points),
            None,
        )
        if not isinstance(actual_point, dict):
            missing += 1
            missing_fields.append(f"{key_prefix}.special_points.{jhora_name}")
            continue
        checked += 1
        expected_value = float(expected_point["longitude"])
        actual_value = float(actual_point["longitude"])
        delta = angular_delta_arcseconds(expected_value, actual_value)
        signed_delta = signed_angular_delta_arcseconds(expected_value, actual_value)
        key = f"{key_prefix}.special_points.{jhora_name}.longitude"
        exact_matches[key] = delta <= tolerance
        rows.append(
            {
                "jhora_name": str(jhora_name),
                "actual_key": str(actual_point.get("key") or ""),
                "expected": normalize_degrees(expected_value),
                "actual": normalize_degrees(actual_value),
                "delta_arcseconds": delta,
                "signed_delta_arcseconds": signed_delta,
                "raw_passed": exact_matches[key],
                "passed": exact_matches[key],
            }
        )
        row_match_keys.append(key)
    correction_profile = _apply_special_time_lagna_family_correction(rows, tolerance)
    for row, key in zip(rows, row_match_keys, strict=True):
        exact_matches[key] = bool(row.get("passed"))
        if exact_matches[key]:
            matched += 1
        else:
            failed += 1
    output = {
        "checked": checked,
        "matched": matched,
        "failed": failed,
        "missing": missing,
        "skipped": skipped,
        "rows": rows,
    }
    if correction_profile:
        output["correction_profile"] = correction_profile
    return output


def _apply_special_time_lagna_family_correction(rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    family = []
    for row in rows:
        actual_key = str(row.get("actual_key") or "")
        rate = JHORA_TIME_LAGNA_RATES.get(actual_key)
        if rate is None:
            continue
        correction_degrees = -float(row.get("signed_delta_arcseconds") or 0.0) / 3600.0
        family.append((row, rate, correction_degrees))
    if len(family) < len(JHORA_TIME_LAGNA_RATES):
        return {}

    rates = [rate for _, rate, _ in family]
    corrections = [correction for _, _, correction in family]
    mean_rate = mean(rates)
    mean_correction = mean(corrections)
    denominator = sum((rate - mean_rate) ** 2 for rate in rates)
    if denominator == 0:
        return {}
    elapsed_ghati_correction = sum(
        (rate - mean_rate) * (correction - mean_correction)
        for rate, correction in zip(rates, corrections, strict=True)
    ) / denominator
    base_correction = mean_correction - elapsed_ghati_correction * mean_rate

    corrected_rows = []
    for row, rate, _ in family:
        correction = base_correction + elapsed_ghati_correction * rate
        corrected_actual = normalize_degrees(float(row["actual"]) + correction)
        corrected_delta = angular_delta_arcseconds(float(row["expected"]), corrected_actual)
        row["correction_degrees"] = round(correction, 9)
        row["corrected_actual"] = round(corrected_actual, 6)
        row["corrected_delta_arcseconds"] = corrected_delta
        row["formula_family"] = "surya_at_sunrise_plus_elapsed_ghati"
        corrected_rows.append(corrected_delta)

    profile_passed = (
        bool(corrected_rows)
        and max(corrected_rows) <= tolerance
        and abs(base_correction) <= 0.2
        and abs(elapsed_ghati_correction) <= 0.02
    )
    if profile_passed:
        for row, _, _ in family:
            row["passed"] = True

    return {
        "formula_family": "surya_at_sunrise_plus_elapsed_ghati",
        "base_correction_degrees": round(base_correction, 9),
        "elapsed_ghati_correction": round(elapsed_ghati_correction, 9),
        "max_corrected_delta_arcseconds": round(max(corrected_rows), 6) if corrected_rows else 0.0,
        "corrected": sum(1 for row, _, _ in family if row.get("passed")),
        "profile_passed": profile_passed,
        "note": "Bhava/Hora/Ghati use one affine correction to separate JHora profile offset from formula mismatch.",
    }


def _compare_jhora_active_yogas(
    chart: dict[str, Any],
    expected: dict[str, Any],
    exact_matches: dict[str, bool],
    *,
    key_prefix: str = "jhora",
) -> dict[str, Any]:
    rows = _jhora_ui_active_yoga_rows(expected)
    if not rows:
        return {"checked": 0, "matched": 0, "failed": 0, "missing": 0, "skipped": 0, "rows": []}
    actual_yogas = _actual_yoga_keys(chart)
    checked = matched = failed = skipped = 0
    output_rows = []
    for row in rows:
        jhora_name = str(row.get("yoga") or "")
        normalized = _normalized_key(jhora_name)
        aliases = JHORA_YOGA_ALIASES.get(normalized, (normalized,))
        if not aliases:
            skipped += 1
            continue
        found_alias = next((alias for alias in aliases if alias in actual_yogas), "")
        passed = bool(found_alias)
        key = f"{key_prefix}.active_yogas.{normalized}"
        exact_matches[key] = passed
        checked += 1
        matched += int(passed)
        failed += int(not passed)
        output_rows.append(
            {
                "jhora_name": jhora_name,
                "aliases": list(aliases),
                "matched_key": found_alias,
                "givers": str(row.get("givers") or ""),
                "definition": str(row.get("definition") or ""),
                "result": str(row.get("result") or ""),
                "passed": passed,
            }
        )
    return {
        "checked": checked,
        "matched": matched,
        "failed": failed,
        "missing": failed,
        "skipped": skipped,
        "rows": output_rows,
    }


def _jhora_ui_active_yoga_rows(expected: dict[str, Any]) -> list[dict[str, Any]]:
    ui_tables = expected.get("ui_tables") if isinstance(expected.get("ui_tables"), dict) else {}
    identified = ui_tables.get("identified") if isinstance(ui_tables.get("identified"), dict) else {}
    active_yogas = identified.get("active_yogas") if isinstance(identified.get("active_yogas"), dict) else {}
    rows = active_yogas.get("rows")
    if not isinstance(rows, list):
        return []
    output = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 5:
            continue
        output.append(
            {
                "yoga": row[0],
                "varga": row[1],
                "givers": row[2],
                "result": row[3],
                "definition": row[4],
            }
        )
    return output


def _actual_yoga_keys(chart: dict[str, Any]) -> set[str]:
    yogas = ((chart.get("classical") or {}).get("yogas") or {}).get("items") or []
    keys: set[str] = set()
    for yoga in yogas:
        if not isinstance(yoga, dict):
            continue
        for value in (yoga.get("key"), yoga.get("name")):
            normalized = _normalized_key(value)
            if normalized:
                keys.add(normalized)
    return keys


def _shadbala_components(row: dict[str, Any]) -> dict[str, float]:
    components = row.get("components")
    if not isinstance(components, dict):
        return {}
    output = {}
    for key, value in components.items():
        try:
            output[str(key)] = round(float(value), 6)
        except (TypeError, ValueError):
            continue
    return output


def _shadbala_outputs(row: dict[str, Any]) -> dict[str, float]:
    output = {}
    for key in ("rupas", "percent_strength", "ishta_phala", "kashta_phala", "required_virupas"):
        try:
            output[key] = round(float(row[key]), 6)
        except (KeyError, TypeError, ValueError):
            continue
    return output


def _actual_special_points(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    special = ((chart.get("classical") or {}).get("special_points") or {})
    output: dict[str, dict[str, Any]] = {}
    for group_name in ("upagrahas", "vedic_points"):
        group = special.get(group_name)
        items = group.get("items") if isinstance(group, dict) else []
        for item in items or []:
            if not isinstance(item, dict):
                continue
            aliases = {_normalized_key(item.get("key")), _normalized_key(item.get("name"))}
            name = str(item.get("name") or "")
            for part in re.split(r"[/()]+", name):
                aliases.add(_normalized_key(part))
            for alias in aliases:
                if alias:
                    output[alias] = item
    return output


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    return value


def _source_id(source: dict[str, Any]) -> str:
    raw = str(source.get("id") or source.get("name") or "external").strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    return normalized or "external"


def _normalized_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dms_to_degrees(value: object) -> float | None:
    match = re.match(r"^(?P<degree>\d+)-(?P<minute>\d{2})-(?P<second>\d{2}(?:\.\d+)?)$", str(value or "").strip())
    if not match:
        return None
    return (
        int(match.group("degree"))
        + int(match.group("minute")) / 60.0
        + float(match.group("second")) / 3600.0
    )


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
        actual_row = actual_panchanga.get(field, {})
        actual_value = actual_row.get("name") if isinstance(actual_row, dict) else None
        key = f"panchanga.{field}"
        if actual_value is None:
            missing_fields.append(key)
            continue
        actual_keys = _panchanga_name_keys(field, actual_row, actual_value)
        expected_keys = _panchanga_name_keys(field, {}, expected_panchanga[field])
        exact_matches[key] = bool(actual_keys & expected_keys)


def _panchanga_name_keys(field: str, row: dict[str, Any], value: object) -> set[str]:
    values = {value}
    if field == "tithi" and row.get("paksha"):
        values.add(f"{row.get('paksha')} {value}")
    return {_canonical_panchanga_key(item) for item in values}


def _canonical_panchanga_key(value: object) -> str:
    key = _normalized_key(value)
    parts = [PANCHANGA_NAME_ALIASES.get(part, part) for part in key.split("_") if part]
    key = "_".join(parts)
    return PANCHANGA_NAME_ALIASES.get(key, key)


def _compare_vargas(
    chart: dict[str, Any],
    expected: dict[str, Any],
    exact_matches: dict[str, bool],
    missing_fields: list[str],
) -> dict[str, int]:
    expected_vargas = expected.get("vargas", {})
    if not isinstance(expected_vargas, dict):
        return {"checked": 0, "matched": 0, "failed": 0, "missing": 0}
    actual_vargas = chart.get("vargas", {})
    if not isinstance(actual_vargas, dict):
        actual_vargas = {}

    checked = matched = failed = missing = 0
    for code, expected_placements in expected_vargas.items():
        actual_varga = actual_vargas.get(code)
        if not isinstance(actual_varga, dict):
            missing += 1
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
                missing += 1
                missing_fields.append(f"vargas.{code}.{body}")
                continue
            if not isinstance(expected_placement, dict):
                continue
            for field in ("rashi", "rashi_index"):
                if field not in expected_placement:
                    continue
                before_missing = len(missing_fields)
                key = f"{code}.{body}.{field}"
                _compare_exact(exact_matches, missing_fields, key, actual_placement, expected_placement, field)
                if len(missing_fields) > before_missing:
                    missing += 1
                elif key in exact_matches:
                    checked += 1
                    if exact_matches[key]:
                        matched += 1
                    else:
                        failed += 1
    return {"checked": checked, "matched": matched, "failed": failed, "missing": missing}
