from __future__ import annotations

import re
from typing import Any

from .constants import RASHIS

RASHI_ABBR = {
    "Ar": "Mesha",
    "Ta": "Vrishabha",
    "Ge": "Mithuna",
    "Cn": "Karka",
    "Le": "Simha",
    "Vi": "Kanya",
    "Li": "Tula",
    "Sc": "Vrischika",
    "Sg": "Dhanu",
    "Cp": "Makara",
    "Aq": "Kumbha",
    "Pi": "Meena",
}

NAKSHATRA_ABBR = {
    "Aswi": "Ashwini",
    "Bhar": "Bharani",
    "Krit": "Krittika",
    "Rohi": "Rohini",
    "Mrig": "Mrigashira",
    "Ardr": "Ardra",
    "Puna": "Punarvasu",
    "Push": "Pushya",
    "Asre": "Ashlesha",
    "Magh": "Magha",
    "PPha": "Purva Phalguni",
    "UPha": "Uttara Phalguni",
    "Hast": "Hasta",
    "Chit": "Chitra",
    "Swat": "Swati",
    "Visa": "Vishakha",
    "Anu": "Anuradha",
    "Jye": "Jyeshtha",
    "Mool": "Mula",
    "PSha": "Purva Ashadha",
    "USha": "Uttara Ashadha",
    "Srav": "Shravana",
    "Dhan": "Dhanishtha",
    "Sata": "Shatabhisha",
    "PBha": "Purva Bhadrapada",
    "UBha": "Uttara Bhadrapada",
    "Reva": "Revati",
}

BODY_MAP = {
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

POSITION_RE = re.compile(
    r"^(?P<body>.+?)\s{2,}"
    r"(?P<degree>\d+)\s(?P<rashi>[A-Z][a-z])\s"
    r"(?P<minute>\d{2})'\s(?P<second>\d{2}\.\d+)\"\s+"
    r"(?P<nakshatra>\S+)\s+(?P<pada>\d+)\s+(?P<rasi_col>\S+)\s+(?P<navamsa>\S+)"
)


def parse_jhora_complete_calculations(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    positions = _parse_positions(lines)
    panchanga = _parse_panchanga(lines)
    metadata = {"ayanamsa": _value_after_colon(lines, "Ayanamsa")}
    return {
        "metadata": metadata,
        "expected": {
            "ascendant": positions.pop("Lagna", {}),
            "grahas": {body: row for body, row in positions.items() if body in BODY_MAP.values()},
            "panchanga": panchanga,
        },
        "jhora_expected": {
            "ashtakavarga": _parse_ashtakavarga(lines),
            "shadbala": _parse_shadbala(lines),
            "vimshottari_raw": _section_lines(lines, "Vimsottari Dasa", stop_prefixes=("Moola Dasa",)),
        },
    }


def _parse_positions(lines: list[str]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    in_table = False
    for line in lines:
        if line.startswith("Body") and "Longitude" in line:
            in_table = True
            continue
        if not in_table:
            continue
        if not line.strip():
            continue
        match = POSITION_RE.match(line.rstrip())
        if not match:
            if rows:
                break
            continue
        raw_body = match.group("body").strip()
        body = _body_name(raw_body)
        if not body:
            continue
        rashi = RASHI_ABBR[match.group("rashi")]
        longitude = _absolute_longitude(
            rashi,
            int(match.group("degree")),
            int(match.group("minute")),
            float(match.group("second")),
        )
        rows[body] = {
            "longitude": longitude,
            "rashi": rashi,
            "nakshatra": NAKSHATRA_ABBR.get(match.group("nakshatra"), match.group("nakshatra")),
            "pada": int(match.group("pada")),
            "navamsa": RASHI_ABBR.get(match.group("navamsa"), match.group("navamsa")),
        }
    return rows


def _parse_panchanga(lines: list[str]) -> dict[str, str]:
    return {
        "tithi": _clean_panchanga_value(_value_after_colon(lines, "Tithi")),
        "vara": _clean_panchanga_value(_value_after_colon(lines, "Vedic Weekday")),
        "nakshatra": _clean_panchanga_value(_value_after_colon(lines, "Nakshatra")),
        "yoga": _clean_panchanga_value(_value_after_colon(lines, "Yoga")),
        "karana": _clean_panchanga_value(_value_after_colon(lines, "Karana")),
    }


def _parse_ashtakavarga(lines: list[str]) -> dict[str, dict[str, int]]:
    start = _line_index(lines, "Ashtakavarga of Rasi Chart:")
    if start is None:
        return {}
    rows: dict[str, dict[str, int]] = {}
    for line in lines[start + 1 :]:
        if line.startswith("      Ar"):
            continue
        if line.startswith("      Sodhya"):
            break
        parts = line.split()
        if len(parts) != 13 or parts[0] not in {"As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa"}:
            continue
        rows[parts[0]] = {
            rashi: int(value.rstrip("*"))
            for rashi, value in zip(RASHIS, parts[1:], strict=True)
        }
    return rows


def _parse_shadbala(lines: list[str]) -> dict[str, dict[str, float]]:
    start = _line_index(lines, "Planet  Shadbala In rupas")
    if start is None:
        return {}
    rows: dict[str, dict[str, float]] = {}
    for line in lines[start + 1 :]:
        parts = line.split()
        if len(parts) < 6:
            if rows:
                break
            continue
        body = parts[0]
        rows[body] = {
            "shadbala": float(parts[1]),
            "rupas": float(parts[2]),
            "percent_strength": float(parts[3]),
            "ishta_phala": float(parts[4]),
            "kashta_phala": float(parts[5]),
        }
    return rows


def _section_lines(
    lines: list[str],
    heading_prefix: str,
    *,
    stop_prefixes: tuple[str, ...],
) -> list[str]:
    start = next((index for index, line in enumerate(lines) if line.startswith(heading_prefix)), None)
    if start is None:
        return []
    rows = []
    for line in lines[start + 1 :]:
        if any(line.startswith(prefix) for prefix in stop_prefixes):
            break
        if line.strip():
            rows.append(line.rstrip())
    return rows


def _value_after_colon(lines: list[str], key: str) -> str:
    prefix = f"{key}:"
    for line in lines:
        if line.startswith(prefix):
            return line.split(":", maxsplit=1)[1].strip()
    return ""


def _clean_panchanga_value(value: str) -> str:
    return value.split("(", maxsplit=1)[0].strip()


def _line_index(lines: list[str], prefix: str) -> int | None:
    return next((index for index, line in enumerate(lines) if line.startswith(prefix)), None)


def _body_name(raw_body: str) -> str:
    base = raw_body.split("-", maxsplit=1)[0].strip()
    if base == "Lagna":
        return "Lagna"
    return BODY_MAP.get(base, "")


def _absolute_longitude(rashi: str, degree: int, minute: int, second: float) -> float:
    return round(RASHIS.index(rashi) * 30.0 + degree + minute / 60.0 + second / 3600.0, 6)
