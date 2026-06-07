from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


def jhd_text_from_birth_input(data: dict[str, Any], *, country: str = "") -> str:
    month, day, year = _date_parts(str(data["birth_date"]))
    timezone_offset_hours = _timezone_offset_hours(data)
    longitude = float(data["longitude"])
    latitude = float(data["latitude"])
    lines = [
        f"{month}",
        f"{day}",
        f"{year}",
        _compact_time(str(data["birth_time"])),
        _compact_timezone(-timezone_offset_hours),
        _compact_angle(-longitude),
        _compact_angle(latitude),
        "0.000000",
        f"{-timezone_offset_hours:.6f}",
        f"{-timezone_offset_hours:.6f}",
        "0",
        "105",
        str(data.get("place_name") or "Unknown"),
        country or _infer_country(data),
    ]
    return "\n".join(lines) + "\n"


def _date_parts(value: str) -> tuple[int, int, int]:
    year_text, month_text, day_text = value.split("-")
    return int(month_text), int(day_text), int(year_text)


def _compact_time(value: str) -> str:
    hours_text, minutes_text, seconds_text = (value.split(":") + ["0", "0"])[:3]
    hours = int(hours_text)
    minutes = int(minutes_text)
    seconds = int(float(seconds_text))
    return f"{hours}.{minutes:02d}{seconds:02d}00"


def _compact_timezone(offset_hours: float) -> str:
    sign = "-" if offset_hours < 0 else ""
    value = abs(offset_hours)
    hours = int(value)
    minutes = int(round((value - hours) * 60.0))
    return f"{sign}{hours}.{minutes:02d}0000"


def _compact_angle(value: float) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    degrees = int(value)
    minutes = (value - degrees) * 60.0
    return f"{sign}{degrees + minutes / 100.0:.6f}"


def _timezone_offset_hours(data: dict[str, Any]) -> float:
    explicit = str(data.get("timezone_offset") or "").strip()
    if explicit:
        return _parse_timezone_offset(explicit)
    birth_date = str(data["birth_date"])
    birth_time = str(data["birth_time"])
    timezone = str(data.get("timezone") or "UTC")
    naive = datetime.fromisoformat(f"{birth_date}T{birth_time}")
    offset = naive.replace(tzinfo=ZoneInfo(timezone)).utcoffset()
    if offset is None:
        return 0.0
    return offset.total_seconds() / 3600.0


def _parse_timezone_offset(value: str) -> float:
    sign = -1.0 if value.startswith("-") else 1.0
    normalized = value.lstrip("+-")
    hours_text, _, minutes_text = normalized.partition(":")
    return sign * (int(hours_text) + (int(minutes_text or "0") / 60.0))


def _infer_country(data: dict[str, Any]) -> str:
    timezone = str(data.get("timezone") or "")
    place = str(data.get("place_name") or "")
    if timezone == "Asia/Kolkata":
        return "India"
    if timezone in {"America/New_York", "America/Los_Angeles", "America/Anchorage", "Pacific/Honolulu"}:
        return "USA"
    if timezone == "Europe/London":
        return "United Kingdom"
    if timezone == "Europe/Moscow" or place == "Sterlitamak":
        return "Russia"
    if timezone == "Asia/Tokyo":
        return "Japan"
    if timezone == "Atlantic/Reykjavik":
        return "Iceland"
    if timezone == "Australia/Sydney":
        return "Australia"
    if timezone == "Africa/Johannesburg":
        return "South Africa"
    if timezone == "America/Sao_Paulo":
        return "Brazil"
    if timezone == "Europe/Paris":
        return "France"
    return "Unknown"
