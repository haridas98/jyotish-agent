from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .manual_witness_comparison import _normalize_body, _witness_longitude, _witness_payload

SwissLongitudeProvider = Callable[[dict[str, Any]], dict[str, dict[str, float]]]


def build_parashara_light_forensic_dump(
    packet_path: str | Path,
    manual_witness_values_path: str | Path,
    *,
    swiss_longitude_provider: SwissLongitudeProvider | None = None,
    tolerance_arcseconds: float = 60.0,
) -> dict[str, Any]:
    packet_source = Path(packet_path)
    manual_source = Path(manual_witness_values_path)
    packet = json.loads(packet_source.read_text(encoding="utf-8-sig"))
    chart = packet.get("jyotish_agent_chart") if isinstance(packet.get("jyotish_agent_chart"), dict) else {}
    manual_values = json.loads(manual_source.read_text(encoding="utf-8-sig"))
    if not isinstance(manual_values, list):
        manual_values = []

    provider = swiss_longitude_provider or _direct_swiss_lahiri_longitudes
    swiss_rows = provider(chart)
    metadata = swiss_rows.get("_metadata") if isinstance(swiss_rows.get("_metadata"), dict) else {}
    engine_by_body = {
        str(row.get("body")): row
        for row in chart.get("grahas") or []
        if isinstance(row, dict) and row.get("body") and row.get("longitude") is not None
    }

    rows = []
    for witness in manual_values:
        if not isinstance(witness, dict):
            continue
        payload = _witness_payload(witness)
        body = _normalize_body(witness.get("body") or payload.get("body"))
        engine = engine_by_body.get(body)
        swiss = swiss_rows.get(body)
        pl_longitude = _witness_longitude(payload)
        if engine is None or swiss is None or pl_longitude is None:
            continue
        engine_longitude = float(engine["longitude"])
        swiss_sidereal = float(swiss["sidereal"])
        pl_minus_engine = _delta_arcseconds(pl_longitude, engine_longitude)
        engine_minus_swiss = _delta_arcseconds(engine_longitude, swiss_sidereal)
        pl_minus_swiss = _delta_arcseconds(pl_longitude, swiss_sidereal)
        rows.append(
            {
                "body": body,
                "swiss_tropical": _round_or_none(swiss.get("tropical")),
                "swiss_lahiri_sidereal": round(swiss_sidereal, 9),
                "swiss_sidereal_speed_deg_per_day": _round_or_none(swiss.get("sidereal_speed")),
                "engine_longitude": round(engine_longitude, 9),
                "pl_witness_longitude": round(pl_longitude, 9),
                "engine_minus_swiss_arcsec": round(engine_minus_swiss, 6),
                "pl_minus_swiss_arcsec": round(pl_minus_swiss, 6),
                "pl_minus_engine_arcsec": round(pl_minus_engine, 6),
                "status": "matched" if abs(pl_minus_engine) <= tolerance_arcseconds else "diff_open",
            }
        )

    engine_swiss_abs = [abs(float(row["engine_minus_swiss_arcsec"])) for row in rows]
    pl_swiss_abs = [abs(float(row["pl_minus_swiss_arcsec"])) for row in rows]
    pl_engine_abs = [abs(float(row["pl_minus_engine_arcsec"])) for row in rows]
    engine_swiss_diff_count = len([value for value in engine_swiss_abs if value > 0.001])
    pl_diff_count = len([row for row in rows if row["status"] == "diff_open"])
    return {
        "source": "parashara_light_forensic_dump",
        "source_packet": str(packet_source),
        "manual_witness_source": str(manual_source),
        "metadata": metadata,
        "summary": {
            "manual_values_count": len([row for row in manual_values if isinstance(row, dict)]),
            "rows_count": len(rows),
            "engine_swiss_diff_count": engine_swiss_diff_count,
            "pl_diff_count": pl_diff_count,
            "engine_swiss_max_abs_arcsec": round(max(engine_swiss_abs, default=0.0), 6),
            "pl_swiss_max_abs_arcsec": round(max(pl_swiss_abs, default=0.0), 6),
            "pl_engine_max_abs_arcsec": round(max(pl_engine_abs, default=0.0), 6),
            "conclusion": _conclusion(engine_swiss_diff_count, pl_diff_count),
        },
        "diagnostics": _diagnostics(rows, tolerance_arcseconds=tolerance_arcseconds),
        "rows": rows,
    }


def _direct_swiss_lahiri_longitudes(chart: dict[str, Any]) -> dict[str, dict[str, float]]:
    try:
        import swisseph as swe
    except ImportError as exc:
        raise RuntimeError("pyswisseph is required for direct Swiss forensic dump") from exc

    settings = chart.get("settings") if isinstance(chart.get("settings"), dict) else {}
    ayanamsa = str(settings.get("ayanamsa") or "lahiri").lower()
    if ayanamsa != "lahiri":
        raise ValueError(f"Unsupported forensic ayanamsa: {ayanamsa}")

    utc_datetime = ((chart.get("birth") or {}).get("utc_datetime") if isinstance(chart.get("birth"), dict) else None)
    if not isinstance(utc_datetime, str) or not utc_datetime:
        raise ValueError("chart.birth.utc_datetime is required")
    moment = datetime.fromisoformat(utc_datetime.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    moment = moment.astimezone(UTC)
    hour = moment.hour + moment.minute / 60.0 + moment.second / 3600.0 + moment.microsecond / 3_600_000_000.0
    jd_ut = swe.julday(moment.year, moment.month, moment.day, hour)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    body_ids = {
        "Surya": swe.SUN,
        "Chandra": swe.MOON,
        "Mangala": swe.MARS,
        "Budha": swe.MERCURY,
        "Guru": swe.JUPITER,
        "Shukra": swe.VENUS,
        "Shani": swe.SATURN,
        "Rahu": swe.TRUE_NODE,
    }
    output: dict[str, dict[str, float]] = {
        "_metadata": {
            "utc": moment.isoformat(),
            "jd_ut": jd_ut,
            "ayanamsa_lahiri_degrees": swe.get_ayanamsa_ut(jd_ut),
        }
    }
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    for body, body_id in body_ids.items():
        tropical_row = swe.calc_ut(jd_ut, body_id, flags)[0]
        sidereal_row = swe.calc_ut(jd_ut, body_id, flags | swe.FLG_SIDEREAL)[0]
        output[body] = {
            "tropical": tropical_row[0] % 360.0,
            "sidereal": sidereal_row[0] % 360.0,
            "sidereal_speed": sidereal_row[3],
        }
    output["Ketu"] = {
        "tropical": (output["Rahu"]["tropical"] + 180.0) % 360.0,
        "sidereal": (output["Rahu"]["sidereal"] + 180.0) % 360.0,
        "sidereal_speed": output["Rahu"]["sidereal_speed"],
    }
    return output


def _delta_arcseconds(left: float, right: float) -> float:
    return ((left - right + 180.0) % 360.0 - 180.0) * 3600.0


def _round_or_none(value: object) -> float | None:
    try:
        return round(float(value), 9)
    except (TypeError, ValueError):
        return None


def _conclusion(engine_swiss_diff_count: int, pl_diff_count: int) -> str:
    if engine_swiss_diff_count == 0 and pl_diff_count > 0:
        return "engine_matches_swiss_pl_profile_diff_open"
    if engine_swiss_diff_count > 0:
        return "engine_swiss_diff_open"
    if pl_diff_count == 0:
        return "matched"
    return "pl_profile_diff_open"


def _diagnostics(rows: list[dict[str, Any]], *, tolerance_arcseconds: float) -> dict[str, Any]:
    observed = [float(row["pl_minus_engine_arcsec"]) for row in rows]
    uniform = _uniform_offset_diagnostic(observed, tolerance_arcseconds=tolerance_arcseconds)
    time_shift = _time_shift_diagnostic(rows, tolerance_arcseconds=tolerance_arcseconds)
    return {
        "uniform_offset": uniform,
        "time_shift": time_shift,
        "next_action": _next_action(uniform, time_shift),
    }


def _uniform_offset_diagnostic(
    observed_arcseconds: list[float],
    *,
    tolerance_arcseconds: float,
) -> dict[str, Any]:
    if not observed_arcseconds:
        return {"status": "insufficient_data", "reason": "no observed PL deltas"}
    mean = sum(observed_arcseconds) / len(observed_arcseconds)
    residuals = [value - mean for value in observed_arcseconds]
    max_residual = max(abs(value) for value in residuals)
    return {
        "status": "rejected" if max_residual > tolerance_arcseconds else "possible",
        "mean_offset_arcsec": round(mean, 6),
        "max_residual_arcsec": round(max_residual, 6),
        "tolerance_arcseconds": tolerance_arcseconds,
    }


def _time_shift_diagnostic(
    rows: list[dict[str, Any]],
    *,
    tolerance_arcseconds: float,
) -> dict[str, Any]:
    usable = []
    for row in rows:
        speed = _float_or_none(row.get("swiss_sidereal_speed_deg_per_day"))
        if speed is None or abs(speed) < 1e-9:
            continue
        observed = float(row["pl_minus_engine_arcsec"])
        speed_arcsec_per_second = speed * 3600.0 / 86400.0
        usable.append(
            {
                "body": row["body"],
                "observed_arcsec": observed,
                "speed_arcsec_per_second": speed_arcsec_per_second,
                "inferred_seconds": observed / speed_arcsec_per_second,
            }
        )
    if len(usable) < 2:
        return {"status": "insufficient_data", "reason": "need at least two body speeds"}
    inferred = sorted(item["inferred_seconds"] for item in usable)
    mid = len(inferred) // 2
    median_seconds = inferred[mid] if len(inferred) % 2 else (inferred[mid - 1] + inferred[mid]) / 2.0
    residuals = [
        item["observed_arcsec"] - item["speed_arcsec_per_second"] * median_seconds
        for item in usable
    ]
    max_residual = max(abs(value) for value in residuals)
    return {
        "status": "rejected" if max_residual > tolerance_arcseconds else "possible",
        "median_inferred_seconds": round(median_seconds, 6),
        "max_residual_arcsec": round(max_residual, 6),
        "tolerance_arcseconds": tolerance_arcseconds,
        "samples": [
            {
                "body": item["body"],
                "inferred_seconds": round(item["inferred_seconds"], 6),
            }
            for item in usable
        ],
    }


def _next_action(uniform: dict[str, Any], time_shift: dict[str, Any]) -> str:
    if uniform.get("status") == "rejected" and time_shift.get("status") == "rejected":
        return "capture_parashara_light_profile_settings"
    if uniform.get("status") == "possible":
        return "verify_parashara_light_ayanamsa_value"
    if time_shift.get("status") == "possible":
        return "verify_parashara_light_birth_time_timezone"
    return "capture_parashara_light_profile_settings"


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
