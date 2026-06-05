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

CHART_TOKEN_BODY_MAP = {
    "As": "Lagna",
    "Su": "Surya",
    "Mo": "Chandra",
    "Ma": "Mangala",
    "Me": "Budha",
    "Ju": "Guru",
    "Ve": "Shukra",
    "Sa": "Shani",
    "Ra": "Rahu",
    "Ke": "Ketu",
}

SUPPORTED_VARGA_CODES = {
    "D2",
    "D3",
    "D4",
    "D7",
    "D9",
    "D10",
    "D12",
    "D16",
    "D20",
    "D24",
    "D27",
    "D30",
    "D40",
    "D45",
    "D60",
}

SOUTH_INDIAN_RASHI_CELLS = {
    0: ("Pi", "Ar", "Ta", "Ge"),
    1: ("Aq", "Cn"),
    2: ("Cp", "Le"),
    3: ("Sg", "Sc", "Li", "Vi"),
}

VIMSOPAKA_SCHEME_MAP = {
    "dasa_varga": "Dasa Varga (10)",
    "shodasa_varga": "Shodasa Varga (16)",
    "sapta_varga": "Sapta Varga (7)",
    "shad_varga": "Shad Varga (6)",
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
    ascendant = positions.pop("Lagna", {})
    grahas = {body: row for body, row in positions.items() if body in BODY_MAP.values()}
    special_points = {
        body: row
        for body, row in positions.items()
        if body not in BODY_MAP.values()
    }
    panchanga = _parse_panchanga(lines)
    ayanamsa = _value_after_colon(lines, "Ayanamsa")
    metadata = {"ayanamsa": ayanamsa, "ayanamsa_degrees": _dms_to_degrees(ayanamsa)}
    return {
        "metadata": metadata,
        "expected": {
            "ascendant": ascendant,
            "grahas": grahas,
            "panchanga": panchanga,
            "vargas": _parse_varga_charts(lines),
        },
        "jhora_expected": {
            "special_points": special_points,
            "ashtakavarga": _parse_ashtakavarga(lines),
            "shadbala": _parse_shadbala(lines),
            "vimsopaka": _parse_vimsopaka(lines),
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
        body = _position_name(raw_body)
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


def _parse_vimsopaka(lines: list[str]) -> dict[str, dict[str, dict[str, float]]]:
    start = _line_index(lines, "Vimsopaka Dasa Varga")
    if start is None:
        return {}
    rows: dict[str, dict[str, dict[str, float]]] = {}
    value_re = re.compile(r"(?P<score>\d+(?:\.\d+)?)\s+\((?P<percent>\d+(?:\.\d+)?)%\)")
    for line in lines[start + 1 :]:
        if not line.strip():
            if rows:
                break
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or parts[0] not in BODY_MAP:
            continue
        values = list(value_re.finditer(parts[1]))
        if len(values) < len(VIMSOPAKA_SCHEME_MAP):
            continue
        rows[parts[0]] = {
            scheme_key: {
                "score": float(match.group("score")),
                "percent": float(match.group("percent")),
                "label": scheme_label,
            }
            for (scheme_key, scheme_label), match in zip(VIMSOPAKA_SCHEME_MAP.items(), values, strict=True)
        }
    return rows


def _parse_varga_charts(lines: list[str]) -> dict[str, dict[str, dict[str, Any]]]:
    charts = {}
    for block in _ascii_chart_blocks(lines):
        code = _chart_code(block)
        if code not in SUPPORTED_VARGA_CODES:
            continue
        placements = _parse_south_indian_chart_block(block)
        if placements:
            charts[code] = placements
    return charts


def _ascii_chart_blocks(lines: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("+---"):
            if current:
                current.append(line)
                blocks.append(current)
                current = []
            else:
                current = [line]
            continue
        if current:
            current.append(line)
    return blocks


def _chart_code(block: list[str]) -> str:
    for line in block:
        match = re.search(r"\bD-(?P<number>\d+)\b", line)
        if match:
            return f"D{match.group('number')}"
    return ""


def _parse_south_indian_chart_block(block: list[str]) -> dict[str, dict[str, Any]]:
    placements: dict[str, dict[str, Any]] = {}
    zone = 0
    for line in block:
        if line.startswith("|-----------+-----------------------+-----------|"):
            zone = 1 if zone < 1 else 3
            continue
        if line.startswith("|-----------|"):
            zone = 2
            continue
        if not line.startswith("|") or line.startswith("+"):
            continue
        segments = line.split("|")[1:-1]
        if zone in {0, 3} and len(segments) == 4:
            for rashi_abbr, cell in zip(SOUTH_INDIAN_RASHI_CELLS[zone], segments, strict=True):
                _add_chart_cell_tokens(placements, rashi_abbr, cell)
        elif zone in {1, 2} and len(segments) >= 3:
            _add_chart_cell_tokens(placements, SOUTH_INDIAN_RASHI_CELLS[zone][0], segments[0])
            _add_chart_cell_tokens(placements, SOUTH_INDIAN_RASHI_CELLS[zone][1], segments[-1])
    return placements


def _add_chart_cell_tokens(placements: dict[str, dict[str, Any]], rashi_abbr: str, cell: str) -> None:
    rashi = RASHI_ABBR[rashi_abbr]
    for token in re.findall(r"\b(?:As|Su|Mo|Ma|Me|Ju|Ve|Sa|Ra|Ke)\b", cell):
        body = CHART_TOKEN_BODY_MAP[token]
        placements[body] = {
            "rashi": rashi,
            "rashi_index": RASHIS.index(rashi),
        }


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


def _position_name(raw_body: str) -> str:
    base = raw_body.split("-", maxsplit=1)[0].strip()
    if base == "Lagna":
        return "Lagna"
    return BODY_MAP.get(base) or base


def _absolute_longitude(rashi: str, degree: int, minute: int, second: float) -> float:
    return round(RASHIS.index(rashi) * 30.0 + degree + minute / 60.0 + second / 3600.0, 6)


def _dms_to_degrees(value: str) -> float | None:
    match = re.match(r"^(?P<degree>\d+)-(?P<minute>\d{2})-(?P<second>\d{2}(?:\.\d+)?)$", value.strip())
    if not match:
        return None
    return round(
        int(match.group("degree"))
        + int(match.group("minute")) / 60.0
        + float(match.group("second")) / 3600.0,
        9,
    )
