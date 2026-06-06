from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def build_parashara_light_profile_report(
    birth_xml: str | Path,
    *,
    packet_path: str | Path | None = None,
) -> dict[str, Any]:
    source = Path(birth_xml)
    root = ET.fromstring(source.read_text(encoding="utf-16"))
    birth_info = root.find("BirthInfo")
    if birth_info is None:
        birth_info = ET.Element("BirthInfo")

    raw = {
        "birth_date_jd_raw": _float_text(birth_info, "BirthDate"),
        "longitude": _float_text(birth_info, "Longitude"),
        "latitude": _float_text(birth_info, "Latitude"),
        "timezone": _float_text(birth_info, "TimeZone"),
        "dst": _float_text(birth_info, "DST"),
        "city": _text(birth_info, "City"),
        "state": _text(birth_info, "State"),
        "country": _text(birth_info, "Country"),
    }
    packet_reference = _packet_reference(packet_path)
    candidates = _candidate_normalization(raw)
    return {
        "source": "parashara_light_birth_xml_profile",
        "source_xml": str(source),
        "packet_source": str(packet_path) if packet_path else "",
        "subject": {
            "first_name": _text(birth_info, "FirstName"),
            "last_name": _text(birth_info, "LastName"),
            "gender_raw": _int_text(birth_info, "Gender"),
        },
        "raw_birth_info": raw,
        "candidate_normalization": candidates,
        "packet_reference": packet_reference,
        "packet_comparison": _packet_comparison(candidates, packet_reference),
        "data_quality_flags": _data_quality_flags(raw, candidates, packet_reference),
        "interpretation_notes": [
            "PL7 XML values are preserved raw; candidate fields are not treated as authoritative until the PL profile/settings screen is captured.",
            "PL7 appears to store eastern longitudes/timezones with a negative sign in this chart, but the report records that as a convention candidate, not a silent correction.",
            "BirthDate is stored as a raw Julian-day-like value; timezone semantics remain unverified without the PL profile/settings screen.",
        ],
    }


def _candidate_normalization(raw: dict[str, Any]) -> dict[str, Any]:
    longitude = _float_or_none(raw.get("longitude"))
    timezone = _float_or_none(raw.get("timezone"))
    dst = _float_or_none(raw.get("dst")) or 0.0
    return {
        "longitude_east_candidate": round(abs(longitude), 7) if longitude is not None else None,
        "latitude_candidate": raw.get("latitude"),
        "timezone_offset_hours_candidate": round(-(timezone - dst), 2) if timezone is not None else None,
        "timezone_formula": "-(TimeZone - DST)",
    }


def _packet_reference(packet_path: str | Path | None) -> dict[str, Any]:
    if not packet_path:
        return {}
    source = Path(packet_path)
    packet = json.loads(source.read_text(encoding="utf-8-sig"))
    fixture = packet.get("fixture") if isinstance(packet.get("fixture"), dict) else {}
    input_data = fixture.get("input") if isinstance(fixture.get("input"), dict) else {}
    chart = packet.get("jyotish_agent_chart") if isinstance(packet.get("jyotish_agent_chart"), dict) else {}
    birth = chart.get("birth") if isinstance(chart.get("birth"), dict) else {}
    place = chart.get("place") if isinstance(chart.get("place"), dict) else {}
    return {
        "longitude": _float_or_none(input_data.get("longitude") or place.get("longitude")),
        "latitude": _float_or_none(input_data.get("latitude") or place.get("latitude")),
        "timezone_offset": input_data.get("timezone_offset") or birth.get("utc_offset") or "",
    }


def _packet_comparison(candidates: dict[str, Any], packet_reference: dict[str, Any]) -> dict[str, Any]:
    longitude = _float_or_none(candidates.get("longitude_east_candidate"))
    packet_longitude = _float_or_none(packet_reference.get("longitude"))
    latitude = _float_or_none(candidates.get("latitude_candidate"))
    packet_latitude = _float_or_none(packet_reference.get("latitude"))
    timezone = _float_or_none(candidates.get("timezone_offset_hours_candidate"))
    packet_timezone = _parse_offset_hours(packet_reference.get("timezone_offset"))
    return {
        "longitude_delta_degrees": _rounded_delta(longitude, packet_longitude),
        "latitude_delta_degrees": _rounded_delta(latitude, packet_latitude),
        "timezone_delta_hours": _rounded_delta(timezone, packet_timezone),
    }


def _data_quality_flags(
    raw: dict[str, Any],
    candidates: dict[str, Any],
    packet_reference: dict[str, Any],
) -> list[str]:
    flags = []
    longitude = _float_or_none(raw.get("longitude"))
    if longitude is not None and longitude < 0:
        flags.append("PL_LONGITUDE_EAST_NEGATIVE_CONVENTION")
    timezone = _float_or_none(raw.get("timezone"))
    if timezone is not None and timezone < 0 and candidates.get("timezone_offset_hours_candidate"):
        flags.append("PL_TIMEZONE_EAST_NEGATIVE_WITH_DST_CONVENTION")
    comparison = _packet_comparison(candidates, packet_reference)
    if abs(float(comparison.get("longitude_delta_degrees") or 0.0)) > 0.01:
        flags.append("PL_PACKET_COORDINATE_VARIANCE")
    if abs(float(comparison.get("timezone_delta_hours") or 0.0)) > 0.01:
        flags.append("PL_PACKET_TIMEZONE_VARIANCE")
    return flags


def _text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    return (child.text or "").strip() if child is not None else ""


def _float_text(element: ET.Element, name: str) -> float | None:
    return _float_or_none(_text(element, name))


def _int_text(element: ET.Element, name: str) -> int | None:
    try:
        return int(float(_text(element, name)))
    except (TypeError, ValueError):
        return None


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_offset_hours(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    text = str(value or "").strip()
    if not text:
        return None
    sign = -1.0 if text.startswith("-") else 1.0
    parts = text.lstrip("+-").split(":")
    try:
        hours = float(parts[0])
        minutes = float(parts[1]) if len(parts) > 1 else 0.0
    except (TypeError, ValueError):
        return None
    return sign * (hours + minutes / 60.0)


def _rounded_delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return round(left - right, 6)
