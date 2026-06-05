from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .primitives import DEGREES_PER_NAKSHATRA, nakshatra_index, normalize_degrees

DASHA_YEAR_DAYS = 365.25

YOGINI_SEQUENCE = (
    {"name": "Mangala", "lord": "Chandra", "years": 1.0},
    {"name": "Pingala", "lord": "Surya", "years": 2.0},
    {"name": "Dhanya", "lord": "Guru", "years": 3.0},
    {"name": "Bhramari", "lord": "Mangala", "years": 4.0},
    {"name": "Bhadrika", "lord": "Budha", "years": 5.0},
    {"name": "Ulka", "lord": "Shani", "years": 6.0},
    {"name": "Siddha", "lord": "Shukra", "years": 7.0},
    {"name": "Sankata", "lord": "Rahu", "years": 8.0},
)

ASHTOTTARI_SEQUENCE = (
    {"lord": "Surya", "years": 6.0},
    {"lord": "Chandra", "years": 15.0},
    {"lord": "Mangala", "years": 8.0},
    {"lord": "Budha", "years": 17.0},
    {"lord": "Shani", "years": 10.0},
    {"lord": "Guru", "years": 19.0},
    {"lord": "Rahu", "years": 12.0},
    {"lord": "Shukra", "years": 21.0},
)


@dataclass(frozen=True)
class DashaPeriod:
    name: str
    lord: str
    level: int
    starts_at: datetime
    ends_at: datetime
    duration_years: float
    sequence_index: int


def yogini_mahadashas(
    moon_longitude: float,
    birth_moment: datetime,
    count: int = 8,
) -> list[DashaPeriod]:
    if birth_moment.tzinfo is None:
        raise ValueError("birth_moment must be timezone-aware")
    if count < 1:
        return []

    normalized = normalize_degrees(moon_longitude)
    nak_idx = nakshatra_index(normalized)
    start_index = ((nak_idx + 1 + 3) % len(YOGINI_SEQUENCE)) - 1
    if start_index < 0:
        start_index = len(YOGINI_SEQUENCE) - 1
    nakshatra_start = nak_idx * DEGREES_PER_NAKSHATRA
    elapsed_fraction = (normalized - nakshatra_start) / DEGREES_PER_NAKSHATRA
    remaining_fraction = max(0.0, min(1.0, 1.0 - elapsed_fraction))

    periods: list[DashaPeriod] = []
    starts_at = birth_moment
    for offset in range(count):
        sequence_index = (start_index + offset) % len(YOGINI_SEQUENCE)
        item = YOGINI_SEQUENCE[sequence_index]
        years = float(item["years"])
        duration_years = years * remaining_fraction if offset == 0 else years
        ends_at = starts_at + timedelta(days=duration_years * DASHA_YEAR_DAYS)
        periods.append(
            DashaPeriod(
                name=str(item["name"]),
                lord=str(item["lord"]),
                level=1,
                starts_at=starts_at,
                ends_at=ends_at,
                duration_years=round(duration_years, 10),
                sequence_index=sequence_index,
            )
        )
        starts_at = ends_at
    return periods


def yogini_payload(
    moon_longitude: float,
    birth_moment: datetime,
    count: int = 8,
) -> dict[str, object]:
    return {
        "system": "yogini",
        "status": "baseline_calculated_needs_jhora_audit",
        "level": "mahadasha",
        "cycle_years": 36.0,
        "year_length_days": DASHA_YEAR_DAYS,
        "start_rule": "Moon nakshatra number plus 3, divided by 8; remainder selects Yogini.",
        "mahadashas": [_period_payload(period) for period in yogini_mahadashas(moon_longitude, birth_moment, count=count)],
    }


def ashtottari_metadata_payload() -> dict[str, object]:
    return {
        "system": "ashtottari",
        "status": "metadata_only_needs_applicability_and_start_rule_audit",
        "cycle_years": 108.0,
        "sequence": [dict(item) for item in ASHTOTTARI_SEQUENCE],
        "audit": {
            "reason": "Applicability and nakshatra grouping vary by tradition/JHora profile.",
            "public_interpretation_status": "blocked_until_jhora_and_text_review",
        },
    }


def extra_dasha_payload(moon_longitude: float, birth_moment: datetime) -> dict[str, object]:
    return {
        "status": "partial_extra_dasha_catalog",
        "yogini": yogini_payload(moon_longitude, birth_moment),
        "ashtottari": ashtottari_metadata_payload(),
    }


def _period_payload(period: DashaPeriod) -> dict[str, object]:
    return {
        "name": period.name,
        "lord": period.lord,
        "level": period.level,
        "starts_at": period.starts_at.isoformat(),
        "ends_at": period.ends_at.isoformat(),
        "duration_years": period.duration_years,
        "sequence_index": period.sequence_index,
    }
