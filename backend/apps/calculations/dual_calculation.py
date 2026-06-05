from __future__ import annotations

from typing import Any

from .accuracy import angular_delta_arcseconds, signed_angular_delta_arcseconds
from .chart import build_birth_chart
from .ephemeris import EphemerisProvider

JHORA_DRIK_PROFILE_SETTINGS = {
    "zodiac": "sidereal",
    "calculation_model": "drik_siddhanta",
    "ayanamsa": "lahiri",
    "node_type": "mean",
    "ephemeris": "swiss",
    "house_system": "whole_sign",
    "bhava_system": "whole_sign",
    "varga_scheme": "jhora_uma_shambhu",
    "sunrise_source": "noaa",
    "timezone_source": "iana",
    "shadbala_profile": "bphs_classical",
}

SETTING_KEYS = tuple(JHORA_DRIK_PROFILE_SETTINGS)


def build_dual_calculation_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    primary_input = _birth_input(data)
    jhora_settings = {
        **JHORA_DRIK_PROFILE_SETTINGS,
        **_dict_or_empty(data.get("jhora_profile_settings")),
    }
    jhora_input = {
        **primary_input,
        **jhora_settings,
    }

    primary_chart = build_birth_chart(primary_input, provider=provider)
    jhora_chart = build_birth_chart(jhora_input, provider=provider)
    delta = _chart_delta(primary_chart, jhora_chart)
    settings_diff = _settings_diff(primary_chart.get("settings"), jhora_chart.get("settings"))

    return {
        "status": "calculated_witness_mode",
        "profile_status": "jhora_profile_unverified",
        "primary_calculation": _track_payload("jyotish_agent_primary", primary_chart),
        "jhora_profile_calculation": _track_payload("jhora_drik_profile", jhora_chart),
        "settings_diff": settings_diff,
        "delta": delta,
        "authority_decision": _authority_decision(delta, settings_diff),
    }


def _birth_input(data: dict[str, Any]) -> dict[str, Any]:
    nested = data.get("birth")
    if isinstance(nested, dict):
        return dict(nested)
    return dict(data)


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _track_payload(key: str, chart: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": key,
        "calculation_version": chart.get("calculation_version"),
        "settings": chart.get("settings", {}),
        "birth": chart.get("birth", {}),
        "place": chart.get("place", {}),
        "chart": chart,
    }


def _settings_diff(primary: Any, witness: Any) -> list[dict[str, Any]]:
    primary_settings = primary if isinstance(primary, dict) else {}
    witness_settings = witness if isinstance(witness, dict) else {}
    rows = []
    for key in SETTING_KEYS:
        primary_value = primary_settings.get(key)
        witness_value = witness_settings.get(key)
        rows.append(
            {
                "key": key,
                "primary": primary_value,
                "jhora_profile": witness_value,
                "matches": primary_value == witness_value,
            }
        )
    return rows


def _chart_delta(primary: dict[str, Any], witness: dict[str, Any]) -> dict[str, Any]:
    graha_rows = _graha_delta(primary, witness)
    lagna = _position_delta(primary.get("ascendant"), witness.get("ascendant"), "Lagna")
    vargas = _varga_delta(primary, witness)
    dashas = _dasha_delta(primary, witness)
    shadbala = _shadbala_delta(primary, witness)
    panchanga = _panchanga_delta(primary, witness)

    max_graha_delta = max((row["delta_arcseconds"] for row in graha_rows), default=0.0)
    exact_match = (
        max_graha_delta == 0
        and (lagna is None or lagna["delta_arcseconds"] == 0)
        and vargas["mismatch_count"] == 0
        and dashas["mismatch_count"] == 0
        and shadbala["mismatch_count"] == 0
        and panchanga["mismatch_count"] == 0
    )
    return {
        "exact_match": exact_match,
        "summary": {
            "graha_count": len(graha_rows),
            "max_graha_delta_arcseconds": max_graha_delta,
            "varga_mismatches": vargas["mismatch_count"],
            "dasha_mismatches": dashas["mismatch_count"],
            "shadbala_mismatches": shadbala["mismatch_count"],
            "panchanga_mismatches": panchanga["mismatch_count"],
        },
        "lagna": lagna,
        "grahas": graha_rows,
        "vargas": vargas,
        "dashas": dashas,
        "shadbala": shadbala,
        "panchanga": panchanga,
    }


def _graha_delta(primary: dict[str, Any], witness: dict[str, Any]) -> list[dict[str, Any]]:
    witness_by_body = {
        row.get("body"): row
        for row in witness.get("grahas", [])
        if isinstance(row, dict) and row.get("body")
    }
    rows = []
    for row in primary.get("grahas", []):
        if not isinstance(row, dict) or not row.get("body"):
            continue
        body = str(row["body"])
        witness_row = witness_by_body.get(body)
        delta = _position_delta(row, witness_row, body)
        if delta:
            rows.append(delta)
    return rows


def _position_delta(primary: Any, witness: Any, body: str) -> dict[str, Any] | None:
    if not isinstance(primary, dict) or not isinstance(witness, dict):
        return None
    primary_longitude = primary.get("longitude")
    witness_longitude = witness.get("longitude")
    if primary_longitude is None or witness_longitude is None:
        return None
    return {
        "body": body,
        "primary_longitude": round(float(primary_longitude), 6),
        "jhora_profile_longitude": round(float(witness_longitude), 6),
        "signed_delta_arcseconds": signed_angular_delta_arcseconds(
            float(primary_longitude),
            float(witness_longitude),
        ),
        "delta_arcseconds": angular_delta_arcseconds(
            float(primary_longitude),
            float(witness_longitude),
        ),
        "primary_rashi": primary.get("rashi"),
        "jhora_profile_rashi": witness.get("rashi"),
        "rashi_matches": primary.get("rashi") == witness.get("rashi"),
        "primary_nakshatra": primary.get("nakshatra"),
        "jhora_profile_nakshatra": witness.get("nakshatra"),
        "nakshatra_matches": primary.get("nakshatra") == witness.get("nakshatra"),
        "primary_pada": primary.get("pada"),
        "jhora_profile_pada": witness.get("pada"),
        "pada_matches": primary.get("pada") == witness.get("pada"),
    }


def _varga_delta(primary: dict[str, Any], witness: dict[str, Any]) -> dict[str, Any]:
    primary_vargas = primary.get("vargas") if isinstance(primary.get("vargas"), dict) else {}
    witness_vargas = witness.get("vargas") if isinstance(witness.get("vargas"), dict) else {}
    rows = []
    mismatch_count = 0
    for code in sorted(set(primary_vargas) | set(witness_vargas), key=_varga_sort_key):
        primary_placements = _placements_by_body(primary_vargas.get(code))
        witness_placements = _placements_by_body(witness_vargas.get(code))
        checked = mismatches = missing = 0
        samples = []
        for body in sorted(set(primary_placements) | set(witness_placements)):
            primary_row = primary_placements.get(body)
            witness_row = witness_placements.get(body)
            if primary_row is None or witness_row is None:
                missing += 1
                continue
            checked += 1
            if primary_row.get("rashi") != witness_row.get("rashi"):
                mismatches += 1
                if len(samples) < 5:
                    samples.append(
                        {
                            "body": body,
                            "primary": primary_row.get("rashi"),
                            "jhora_profile": witness_row.get("rashi"),
                        }
                    )
        mismatch_count += mismatches + missing
        rows.append(
            {
                "code": code,
                "checked": checked,
                "mismatches": mismatches,
                "missing": missing,
                "samples": samples,
            }
        )
    return {"mismatch_count": mismatch_count, "rows": rows}


def _placements_by_body(varga: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(varga, dict):
        return {}
    return {
        row.get("body"): row
        for row in varga.get("placements", [])
        if isinstance(row, dict) and row.get("body")
    }


def _varga_sort_key(code: str) -> tuple[int, str]:
    try:
        return int(str(code).removeprefix("D")), str(code)
    except ValueError:
        return 999, str(code)


def _shadbala_delta(primary: dict[str, Any], witness: dict[str, Any]) -> dict[str, Any]:
    primary_rows = _shadbala_by_body(primary)
    witness_rows = _shadbala_by_body(witness)
    rows = []
    mismatch_count = 0
    for body in sorted(set(primary_rows) | set(witness_rows)):
        primary_row = primary_rows.get(body)
        witness_row = witness_rows.get(body)
        if not primary_row or not witness_row:
            mismatch_count += 1
            rows.append({"body": body, "status": "missing"})
            continue
        primary_total = float(primary_row.get("known_total") or 0)
        witness_total = float(witness_row.get("known_total") or 0)
        delta = round(witness_total - primary_total, 6)
        if delta:
            mismatch_count += 1
        rows.append(
            {
                "body": body,
                "primary": round(primary_total, 6),
                "jhora_profile": round(witness_total, 6),
                "delta": delta,
                "components": {
                    "primary": primary_row.get("components", {}),
                    "jhora_profile": witness_row.get("components", {}),
                },
            }
        )
    return {"mismatch_count": mismatch_count, "rows": rows}


def _dasha_delta(primary: dict[str, Any], witness: dict[str, Any]) -> dict[str, Any]:
    primary_periods = _vimshottari_periods(primary)
    witness_periods = _vimshottari_periods(witness)
    rows = []
    mismatch_count = 0
    for index in range(max(len(primary_periods), len(witness_periods))):
        primary_row = primary_periods[index] if index < len(primary_periods) else None
        witness_row = witness_periods[index] if index < len(witness_periods) else None
        if not isinstance(primary_row, dict) or not isinstance(witness_row, dict):
            mismatch_count += 1
            rows.append({"index": index, "status": "missing"})
            continue
        matches = (
            primary_row.get("lord") == witness_row.get("lord")
            and primary_row.get("starts_at") == witness_row.get("starts_at")
            and primary_row.get("ends_at") == witness_row.get("ends_at")
        )
        if not matches:
            mismatch_count += 1
        rows.append(
            {
                "index": index,
                "primary_lord": primary_row.get("lord"),
                "jhora_profile_lord": witness_row.get("lord"),
                "primary_starts_at": primary_row.get("starts_at"),
                "jhora_profile_starts_at": witness_row.get("starts_at"),
                "primary_ends_at": primary_row.get("ends_at"),
                "jhora_profile_ends_at": witness_row.get("ends_at"),
                "matches": matches,
            }
        )
    return {"mismatch_count": mismatch_count, "rows": rows}


def _vimshottari_periods(chart: dict[str, Any]) -> list[dict[str, Any]]:
    periods = (((chart.get("dashas") or {}).get("vimshottari") or {}).get("mahadashas") or [])
    return [row for row in periods if isinstance(row, dict)]


def _shadbala_by_body(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = (((chart.get("classical") or {}).get("shadbala") or {}).get("items") or [])
    return {row.get("body"): row for row in items if isinstance(row, dict) and row.get("body")}


def _panchanga_delta(primary: dict[str, Any], witness: dict[str, Any]) -> dict[str, Any]:
    rows = []
    mismatch_count = 0
    for key in ("tithi", "vara", "yoga", "karana"):
        primary_value = ((primary.get("panchanga") or {}).get(key) or {}).get("name")
        witness_value = ((witness.get("panchanga") or {}).get(key) or {}).get("name")
        matches = primary_value == witness_value
        if not matches:
            mismatch_count += 1
        rows.append(
            {
                "key": key,
                "primary": primary_value,
                "jhora_profile": witness_value,
                "matches": matches,
            }
        )
    return {"mismatch_count": mismatch_count, "rows": rows}


def _authority_decision(
    delta: dict[str, Any],
    settings_diff: list[dict[str, Any]],
) -> dict[str, Any]:
    differing_settings = [row["key"] for row in settings_diff if not row["matches"]]
    needs_review = bool(differing_settings) or not delta["exact_match"]
    return {
        "accepted_track": "primary_calculation",
        "status": "primary_kept_pending_jhora_profile_review" if needs_review else "tracks_match",
        "needs_review": needs_review,
        "reason": (
            "JHora profile is a black-box witness. The primary calculation is retained until "
            "the JHora settings profile is fully recorded and any deltas are explained."
        ),
        "differing_settings": differing_settings,
    }
