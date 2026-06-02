from __future__ import annotations

from pathlib import Path
from typing import Any

JHORA_VERSION_REQUIRED = "8.0"


def parse_jhd_text(text: str, *, source_name: str = "") -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines()]
    values = [line for line in lines if line != ""]
    if len(values) < 7:
        raise ValueError("JHora .jhd file must contain at least 7 non-empty lines")

    month = int(float(values[0]))
    day = int(float(values[1]))
    year = int(float(values[2]))
    birth_time_decimal = float(values[3])
    compact_timezone = _compact_time_to_decimal_hours(float(values[4]))
    longitude = _jhora_longitude_to_east_degrees(float(values[5]))
    latitude = _compact_angle_to_degrees(float(values[6]))
    decimal_timezone = _jhora_timezone_decimal(values, compact_timezone)
    source_title = _name_from_source(source_name)
    place_name = _place_name(values[12] if len(values) > 12 else "", source_title)
    country = values[13] if len(values) > 13 else ""

    return {
        "source_name": source_name,
        "birth_date": f"{year:04d}-{month:02d}-{day:02d}",
        "birth_time": _decimal_hours_to_hhmm(birth_time_decimal),
        "place_name": place_name,
        "country": country,
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "timezone": _timezone_guess(country, decimal_timezone),
        "jhora_time_decimal_hours": birth_time_decimal,
        "jhora_timezone_compact": float(values[4]),
        "jhora_timezone_offset_hours": round(decimal_timezone, 6),
        "jhora_raw_line_count": len(values),
    }


def jhd_to_accuracy_fixture(text: str, *, source_name: str = "") -> dict[str, Any]:
    parsed = parse_jhd_text(text, source_name=source_name)
    return {
        "id": f"jhora-input-{_slug(_name_from_source(source_name) or parsed['place_name'])}",
        "source": "jhora_sample_jhd",
        "review_status": "draft",
        "notes": "Input imported from JHora .jhd sample. Expected outputs require manual JHora export.",
        "input": {
            "birth_date": parsed["birth_date"],
            "birth_time": parsed["birth_time"],
            "place_name": parsed["place_name"],
            "timezone": parsed["timezone"],
            "latitude": parsed["latitude"],
            "longitude": parsed["longitude"],
        },
        "jhora_metadata": {
            "version_required": JHORA_VERSION_REQUIRED,
            "source_name": parsed["source_name"],
            "timezone_offset_hours": parsed["jhora_timezone_offset_hours"],
            "timezone_compact": parsed["jhora_timezone_compact"],
            "raw_line_count": parsed["jhora_raw_line_count"],
        },
        "expected": {},
    }


def _jhora_timezone_decimal(values: list[str], fallback: float) -> float:
    if len(values) > 8:
        return abs(float(values[8]))
    return abs(fallback)


def _jhora_longitude_to_east_degrees(value: float) -> float:
    return -_compact_angle_to_degrees(value)


def _compact_angle_to_degrees(value: float) -> float:
    sign = -1.0 if value < 0 else 1.0
    value = abs(value)
    degrees = int(value)
    minutes = (value - degrees) * 100.0
    return sign * (degrees + minutes / 60.0)


def _compact_time_to_decimal_hours(value: float) -> float:
    return _compact_angle_to_degrees(value)


def _decimal_hours_to_hhmm(value: float) -> str:
    total_minutes = int(round((value % 24.0) * 60.0))
    total_minutes %= 24 * 60
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


def _timezone_guess(country: str, offset_hours: float) -> str:
    if country.lower() == "india" and abs(offset_hours - 5.5) < 0.01:
        return "Asia/Kolkata"
    if abs(offset_hours - 5.5) < 0.01:
        return "Asia/Kolkata"
    return "UTC"


def _name_from_source(source_name: str) -> str:
    return Path(source_name).stem if source_name else "JHora imported chart"


def _place_name(value: str, fallback: str) -> str:
    normalized = value.strip()
    if not normalized or normalized.lower() == "unknown":
        return fallback
    if not any(char.isalpha() for char in normalized):
        return fallback
    return normalized


def _slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in slug.split("-") if part)
