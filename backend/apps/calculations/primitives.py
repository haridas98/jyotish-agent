from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import floor

from .constants import NAKSHATRAS, RASHIS

DEGREES_PER_RASHI = 30.0
DEGREES_PER_NAKSHATRA = 360.0 / 27.0
DEGREES_PER_PADA = 360.0 / 108.0
DEGREES_PER_NAVAMSA = 360.0 / 108.0
BOUNDARY_EPSILON = 1e-9


@dataclass(frozen=True)
class ZodiacPlacement:
    longitude: float
    rashi_index: int
    rashi: str
    nakshatra_index: int
    nakshatra: str
    pada: int
    navamsa_index: int
    navamsa: str


def normalize_degrees(value: float) -> float:
    normalized = value % 360.0
    if normalized == 360.0:
        return 0.0
    return normalized


def julian_day(moment: datetime) -> float:
    if moment.tzinfo is None:
        raise ValueError("moment must be timezone-aware")

    utc = moment.astimezone(timezone.utc)
    year = utc.year
    month = utc.month
    day = utc.day + (
        utc.hour + (utc.minute + (utc.second + utc.microsecond / 1_000_000) / 60.0) / 60.0
    ) / 24.0

    if month <= 2:
        year -= 1
        month += 12

    century = floor(year / 100)
    gregorian_correction = 2 - century + floor(century / 4)

    return (
        floor(365.25 * (year + 4716))
        + floor(30.6001 * (month + 1))
        + day
        + gregorian_correction
        - 1524.5
    )


def rashi_index(longitude: float) -> int:
    return min(11, floor((normalize_degrees(longitude) + BOUNDARY_EPSILON) / DEGREES_PER_RASHI))


def nakshatra_index(longitude: float) -> int:
    return min(
        26,
        floor((normalize_degrees(longitude) + BOUNDARY_EPSILON) / DEGREES_PER_NAKSHATRA),
    )


def pada(longitude: float) -> int:
    nak_start = nakshatra_index(longitude) * DEGREES_PER_NAKSHATRA
    offset = normalize_degrees(longitude) - nak_start
    return min(4, floor((offset + BOUNDARY_EPSILON) / DEGREES_PER_PADA) + 1)


def navamsa_index(longitude: float) -> int:
    return floor((normalize_degrees(longitude) + BOUNDARY_EPSILON) / DEGREES_PER_NAVAMSA) % 12


def zodiac_placement(longitude: float) -> ZodiacPlacement:
    normalized = normalize_degrees(longitude)
    sign_idx = rashi_index(normalized)
    nak_idx = nakshatra_index(normalized)
    nav_idx = navamsa_index(normalized)
    return ZodiacPlacement(
        longitude=normalized,
        rashi_index=sign_idx,
        rashi=RASHIS[sign_idx],
        nakshatra_index=nak_idx,
        nakshatra=NAKSHATRAS[nak_idx],
        pada=pada(normalized),
        navamsa_index=nav_idx,
        navamsa=RASHIS[nav_idx],
    )
