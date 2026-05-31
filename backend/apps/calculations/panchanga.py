from __future__ import annotations

from datetime import datetime
from math import floor
from typing import Any

from .primitives import DEGREES_PER_NAKSHATRA, normalize_degrees

TITHI_NAMES = [
    "Pratipada",
    "Dvitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dvadashi",
    "Trayodashi",
    "Chaturdashi",
    "Purnima",
    "Pratipada",
    "Dvitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dvadashi",
    "Trayodashi",
    "Chaturdashi",
    "Amavasya",
]

YOGA_NAMES = [
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shula",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyan",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
]

VARA_NAMES = [
    "Somavara",
    "Mangalavara",
    "Budhavara",
    "Guruvara",
    "Shukravara",
    "Shanivara",
    "Ravivara",
]

MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti"]
FIXED_KARANAS = {
    0: "Kimstughna",
    57: "Shakuni",
    58: "Chatushpada",
    59: "Naga",
}
DEGREES_PER_TITHI = 12.0
DEGREES_PER_KARANA = 6.0


def panchanga_from_longitudes(
    sun_longitude: float,
    moon_longitude: float,
    local_moment: datetime,
) -> dict[str, Any]:
    if local_moment.tzinfo is None:
        raise ValueError("local_moment must be timezone-aware")

    elongation = normalize_degrees(moon_longitude - sun_longitude)
    tithi_index = min(29, floor(elongation / DEGREES_PER_TITHI))
    yoga_index = min(26, floor(normalize_degrees(sun_longitude + moon_longitude) / DEGREES_PER_NAKSHATRA))
    karana_index = min(59, floor(elongation / DEGREES_PER_KARANA))

    return {
        "tithi": {
            "index": tithi_index,
            "number": tithi_index + 1,
            "name": TITHI_NAMES[tithi_index],
            "paksha": "Shukla" if tithi_index < 15 else "Krishna",
            "elapsed_degrees": elongation % DEGREES_PER_TITHI,
        },
        "vara": {
            "index": local_moment.weekday(),
            "name": VARA_NAMES[local_moment.weekday()],
        },
        "yoga": {
            "index": yoga_index,
            "number": yoga_index + 1,
            "name": YOGA_NAMES[yoga_index],
        },
        "karana": {
            "index": karana_index,
            "name": _karana_name(karana_index),
        },
    }


def _karana_name(karana_index: int) -> str:
    fixed = FIXED_KARANAS.get(karana_index)
    if fixed is not None:
        return fixed
    return MOVABLE_KARANAS[(karana_index - 1) % len(MOVABLE_KARANAS)]
