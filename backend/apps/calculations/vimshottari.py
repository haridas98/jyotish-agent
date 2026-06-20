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
VIMSHOTTARI_METHOD_ID = "dasha.vimshottari.parashara.v1"
VIMSHOTTARI_METHOD_VERSION = "1"
VIMSHOTTARI_SOURCE_ANCHOR = "BPHS 46.2-16"
DASHA_BOUNDARY_POLICY = "start_inclusive_end_exclusive"


@dataclass(frozen=True)
class VimshottariPeriod:
    lord: str
    level: int
    starts_at: datetime
    ends_at: datetime
    duration_years: float
    sequence_index: int


@dataclass(frozen=True)
class VimshottariBirthBalance:
    moon_nakshatra_index: int
    lord_index: int
    elapsed_fraction: float
    remaining_fraction: float


def vimshottari_mahadashas(
    moon_longitude: float,
    birth_moment: datetime,
    count: int = 9,
) -> list[VimshottariPeriod]:
    if birth_moment.tzinfo is None:
        raise ValueError("birth_moment must be timezone-aware")
    if count < 1:
        return []

    balance = _birth_balance(moon_longitude)
    periods: list[VimshottariPeriod] = []
    starts_at = birth_moment
    for offset in range(count):
        sequence_index = (balance.lord_index + offset) % len(VIMSHOTTARI_SEQUENCE)
        lord = VIMSHOTTARI_SEQUENCE[sequence_index]
        years = VIMSHOTTARI_YEARS[lord]
        duration_years = years * balance.remaining_fraction if offset == 0 else years
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
    balance = _birth_balance(moon_longitude)
    mahadashas = vimshottari_mahadashas(moon_longitude, birth_moment, count=count)
    return {
        "system": "vimshottari",
        "level": "mahadasha",
        "methodId": VIMSHOTTARI_METHOD_ID,
        "methodVersion": VIMSHOTTARI_METHOD_VERSION,
        "sourceAnchor": VIMSHOTTARI_SOURCE_ANCHOR,
        "boundary_policy": DASHA_BOUNDARY_POLICY,
        "year_length_days": VIMSHOTTARI_YEAR_DAYS,
        "moon_nakshatra_index": balance.moon_nakshatra_index,
        "birth_elapsed_fraction": round(balance.elapsed_fraction, 10),
        "birth_balance_fraction": round(balance.remaining_fraction, 10),
        "mahadashas": [
            {
                **_period_payload(period),
                "boundary_policy": DASHA_BOUNDARY_POLICY,
                "antardashas": [
                    _period_payload(antardasha, parent_lord=period.lord)
                    for antardasha in _antardashas_for(period)
                ],
            }
            for period in mahadashas
        ],
    }


def active_vimshottari_periods(
    moon_longitude: float,
    birth_moment: datetime,
    as_of: datetime,
    count: int = 9,
) -> dict[str, object]:
    if as_of.tzinfo is None:
        raise ValueError("as_of must be timezone-aware")

    mahadashas = vimshottari_mahadashas(moon_longitude, birth_moment, count=count)
    mahadasha = _active_period(mahadashas, as_of)
    if mahadasha is None:
        return {
            "as_of": as_of.isoformat(),
            "mahadasha": None,
            "antardasha": None,
            "mahadasha_antardashas": [],
        }

    antardashas = _antardashas_for(mahadasha)
    antardasha = _active_period(antardashas, as_of)
    return {
        "as_of": as_of.isoformat(),
        "mahadasha": _period_payload(mahadasha),
        "antardasha": _period_payload(antardasha, parent_lord=mahadasha.lord)
        if antardasha
        else None,
        "mahadasha_antardashas": [
            _period_payload(period, parent_lord=mahadasha.lord) for period in antardashas
        ],
    }


def _birth_balance(moon_longitude: float) -> VimshottariBirthBalance:
    normalized = normalize_degrees(moon_longitude)
    nak_idx = nakshatra_index(normalized)
    lord_index = nak_idx % len(VIMSHOTTARI_SEQUENCE)
    nakshatra_start = nak_idx * DEGREES_PER_NAKSHATRA
    elapsed_fraction = (normalized - nakshatra_start) / DEGREES_PER_NAKSHATRA
    remaining_fraction = max(0.0, min(1.0, 1.0 - elapsed_fraction))
    return VimshottariBirthBalance(
        moon_nakshatra_index=nak_idx,
        lord_index=lord_index,
        elapsed_fraction=elapsed_fraction,
        remaining_fraction=remaining_fraction,
    )


def _active_period(
    periods: list[VimshottariPeriod],
    as_of: datetime,
) -> VimshottariPeriod | None:
    for period in periods:
        if period.starts_at <= as_of < period.ends_at:
            return period
    return None


def _antardashas_for(mahadasha: VimshottariPeriod) -> list[VimshottariPeriod]:
    total_days = (mahadasha.ends_at - mahadasha.starts_at).total_seconds() / 86_400
    periods: list[VimshottariPeriod] = []
    starts_at = mahadasha.starts_at
    parent_index = VIMSHOTTARI_SEQUENCE.index(mahadasha.lord)
    for offset in range(len(VIMSHOTTARI_SEQUENCE)):
        sequence_index = (parent_index + offset) % len(VIMSHOTTARI_SEQUENCE)
        lord = VIMSHOTTARI_SEQUENCE[sequence_index]
        duration_days = total_days * (VIMSHOTTARI_YEARS[lord] / 120.0)
        ends_at = starts_at + timedelta(days=duration_days)
        periods.append(
            VimshottariPeriod(
                lord=lord,
                level=2,
                starts_at=starts_at,
                ends_at=ends_at,
                duration_years=round(duration_days / VIMSHOTTARI_YEAR_DAYS, 10),
                sequence_index=sequence_index,
            )
        )
        starts_at = ends_at
    return periods


def _period_payload(
    period: VimshottariPeriod,
    parent_lord: str | None = None,
) -> dict[str, object]:
    payload = {
        "lord": period.lord,
        "level": period.level,
        "starts_at": period.starts_at.isoformat(),
        "ends_at": period.ends_at.isoformat(),
        "duration_years": period.duration_years,
        "sequence_index": period.sequence_index,
    }
    if parent_lord:
        payload["parent_lord"] = parent_lord
    return payload
