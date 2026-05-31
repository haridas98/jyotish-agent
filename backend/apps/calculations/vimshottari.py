from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .primitives import DEGREES_PER_NAKSHATRA, nakshatra_index, normalize_degrees

VIMSHOTTARI_SEQUENCE = ["Ketu", "Shukra", "Surya", "Chandra", "Mangala", "Rahu", "Guru", "Shani", "Budha"]
VIMSHOTTARI_YEARS = {
    "Ketu": 7.0,
    "Shukra": 20.0,
    "Surya": 6.0,
    "Chandra": 10.0,
    "Mangala": 7.0,
    "Rahu": 18.0,
    "Guru": 16.0,
    "Shani": 19.0,
    "Budha": 17.0,
}
VIMSHOTTARI_YEAR_DAYS = 365.25


@dataclass(frozen=True)
class VimshottariPeriod:
    lord: str
    level: int
    starts_at: datetime
    ends_at: datetime
    duration_years: float
    sequence_index: int


def vimshottari_mahadashas(
    moon_longitude: float,
    birth_moment: datetime,
    count: int = 9,
) -> list[VimshottariPeriod]:
    if birth_moment.tzinfo is None:
        raise ValueError("birth_moment must be timezone-aware")
    if count < 1:
        return []

    normalized = normalize_degrees(moon_longitude)
    nak_idx = nakshatra_index(normalized)
    lord_index = nak_idx % len(VIMSHOTTARI_SEQUENCE)
    nakshatra_start = nak_idx * DEGREES_PER_NAKSHATRA
    elapsed_fraction = (normalized - nakshatra_start) / DEGREES_PER_NAKSHATRA
    remaining_fraction = max(0.0, min(1.0, 1.0 - elapsed_fraction))

    periods: list[VimshottariPeriod] = []
    starts_at = birth_moment
    for offset in range(count):
        sequence_index = (lord_index + offset) % len(VIMSHOTTARI_SEQUENCE)
        lord = VIMSHOTTARI_SEQUENCE[sequence_index]
        years = VIMSHOTTARI_YEARS[lord]
        duration_years = years * remaining_fraction if offset == 0 else years
        ends_at = starts_at + timedelta(days=duration_years * VIMSHOTTARI_YEAR_DAYS)
        periods.append(
            VimshottariPeriod(
                lord=lord,
                level=1,
                starts_at=starts_at,
                ends_at=ends_at,
                duration_years=round(duration_years, 10),
                sequence_index=sequence_index,
            )
        )
        starts_at = ends_at

    return periods


def vimshottari_payload(
    moon_longitude: float,
    birth_moment: datetime,
    count: int = 9,
) -> dict[str, object]:
    return {
        "system": "vimshottari",
        "level": "mahadasha",
        "year_length_days": VIMSHOTTARI_YEAR_DAYS,
        "mahadashas": [
            {
                "lord": period.lord,
                "level": period.level,
                "starts_at": period.starts_at.isoformat(),
                "ends_at": period.ends_at.isoformat(),
                "duration_years": period.duration_years,
                "sequence_index": period.sequence_index,
            }
            for period in vimshottari_mahadashas(moon_longitude, birth_moment, count=count)
        ],
    }
