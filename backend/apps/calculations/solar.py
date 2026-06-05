from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone, tzinfo
from importlib import import_module
from math import acos, asin, atan, cos, degrees, floor, radians, sin, tan
import os
from typing import Any

WEEKDAY_LORDS = ("Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Surya")

RAHU_KALAM_SEGMENTS = {
    0: 2,
    1: 7,
    2: 5,
    3: 6,
    4: 4,
    5: 3,
    6: 8,
}

YAMAGANDA_SEGMENTS = {
    0: 4,
    1: 3,
    2: 2,
    3: 1,
    4: 7,
    5: 6,
    6: 5,
}

SOLAR_METHOD = "NOAA sunrise equation, apparent sunrise zenith 90.833 degrees."
SWISS_CENTER_NO_REFRACTION_METHOD = (
    "Swiss Ephemeris rise/set, solar disc center, no atmospheric refraction; matches JHora sunrise profile."
)


@dataclass(frozen=True)
class SolarDay:
    date: date
    timezone: str
    sunrise: datetime
    sunset: datetime
    next_sunrise: datetime
    status: str
    method: str = SOLAR_METHOD

    @property
    def daylight_minutes(self) -> int:
        return round((self.sunset - self.sunrise).total_seconds() / 60)

    @property
    def night_minutes(self) -> int:
        return round((self.next_sunrise - self.sunset).total_seconds() / 60)


def solar_day(day: date, latitude: float, longitude: float, tz: tzinfo, source: str = "noaa") -> SolarDay:
    sunrise = _sun_event_for_source(day, latitude, longitude, tz, sunrise=True, source=source)
    sunset = _sun_event_for_source(day, latitude, longitude, tz, sunrise=False, source=source)
    next_sunrise = _sun_event_for_source(day + timedelta(days=1), latitude, longitude, tz, sunrise=True, source=source)
    status = "calculated"
    method = _solar_method(source)

    if sunrise is None or sunset is None or next_sunrise is None or sunset <= sunrise:
        status = "fallback_fixed_clock"
        method = f"{method}; fixed-clock fallback"
        sunrise = datetime.combine(day, datetime.min.time(), tzinfo=tz).replace(hour=6)
        sunset = datetime.combine(day, datetime.min.time(), tzinfo=tz).replace(hour=18)
        next_sunrise = sunrise + timedelta(days=1)

    return SolarDay(
        date=day,
        timezone=_timezone_name(tz),
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_sunrise,
        status=status,
        method=method,
    )


def solar_day_payload(day: SolarDay) -> dict[str, Any]:
    return {
        "date": day.date.isoformat(),
        "timezone": day.timezone,
        "sunrise": day.sunrise.isoformat(),
        "sunset": day.sunset.isoformat(),
        "next_sunrise": day.next_sunrise.isoformat(),
        "daylight_minutes": day.daylight_minutes,
        "night_minutes": day.night_minutes,
        "status": day.status,
        "method": day.method,
        "day_periods": daytime_inauspicious_periods(day),
    }


def daytime_inauspicious_periods(day: SolarDay) -> list[dict[str, Any]]:
    weekday = day.date.weekday()
    return [
        _period_payload("rahu_kalam", "Rahu Kalam", day.sunrise, day.sunset, RAHU_KALAM_SEGMENTS[weekday]),
        _period_payload("yamaganda", "Yamaganda", day.sunrise, day.sunset, YAMAGANDA_SEGMENTS[weekday]),
        _period_payload("gulika_kala", "Gulika Kala", day.sunrise, day.sunset, _saturn_segment(weekday)),
    ]


def gulika_segment_for_moment(
    moment: datetime,
    latitude: float,
    longitude: float,
    source: str = "noaa",
) -> dict[str, Any]:
    if moment.tzinfo is None:
        raise ValueError("moment must be timezone-aware")

    current_day = solar_day(moment.date(), latitude, longitude, moment.tzinfo, source=source)
    if current_day.sunrise <= moment < current_day.sunset:
        segment = _saturn_segment(moment.weekday())
        return _period_payload(
            "gulika",
            "Gulika/Mandi",
            current_day.sunrise,
            current_day.sunset,
            segment,
            period="day",
            status=current_day.status,
        )

    if moment < current_day.sunrise:
        previous_day = solar_day(moment.date() - timedelta(days=1), latitude, longitude, moment.tzinfo, source=source)
        period_start = previous_day.sunset
        period_end = current_day.sunrise
        start_lord_index = moment.weekday()
    else:
        period_start = current_day.sunset
        period_end = current_day.next_sunrise
        start_lord_index = (moment.weekday() + 1) % len(WEEKDAY_LORDS)

    return _period_payload(
        "gulika",
        "Gulika/Mandi",
        period_start,
        period_end,
        _saturn_segment(start_lord_index),
        period="night",
        status=current_day.status,
    )


def moment_hits_periods(moment: datetime, periods: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits = []
    for period in periods:
        starts_at = datetime.fromisoformat(str(period["starts_at"]))
        ends_at = datetime.fromisoformat(str(period["ends_at"]))
        if starts_at <= moment < ends_at:
            hits.append(period)
    return hits


def _period_payload(
    key: str,
    name: str,
    period_start: datetime,
    period_end: datetime,
    segment: int,
    *,
    period: str = "day",
    status: str = "calculated",
) -> dict[str, Any]:
    segment_start, segment_end = _segment_bounds(period_start, period_end, segment)
    midpoint = segment_start + (segment_end - segment_start) / 2
    return {
        "key": key,
        "name": name,
        "period": period,
        "segment": segment,
        "starts_at": segment_start.isoformat(),
        "ends_at": segment_end.isoformat(),
        "midpoint": midpoint.isoformat(),
        "local_time": midpoint.strftime("%H:%M"),
        "status": status,
    }


def _segment_bounds(period_start: datetime, period_end: datetime, segment: int) -> tuple[datetime, datetime]:
    if segment < 1 or segment > 8:
        raise ValueError("segment must be between 1 and 8")
    segment_delta = (period_end - period_start) / 8
    starts_at = period_start + segment_delta * (segment - 1)
    return starts_at, starts_at + segment_delta


def _saturn_segment(start_lord_index: int) -> int:
    sequence = [WEEKDAY_LORDS[(start_lord_index + offset) % len(WEEKDAY_LORDS)] for offset in range(8)]
    return sequence.index("Shani") + 1


def _sun_event_for_source(
    day: date,
    latitude: float,
    longitude: float,
    tz: tzinfo,
    *,
    sunrise: bool,
    source: str,
) -> datetime | None:
    if source == "swiss_center_no_refraction":
        return _swiss_sun_event(day, latitude, longitude, tz, sunrise=sunrise)
    return _sun_event(day, latitude, longitude, tz, sunrise=sunrise)


def _solar_method(source: str) -> str:
    if source == "swiss_center_no_refraction":
        return SWISS_CENTER_NO_REFRACTION_METHOD
    return SOLAR_METHOD


def _swiss_sun_event(day: date, latitude: float, longitude: float, tz: tzinfo, *, sunrise: bool) -> datetime | None:
    try:
        swe = import_module("swisseph")
    except ImportError:
        return None

    ephemeris_path = os.getenv("SWISSEPH_EPHE_PATH")
    if ephemeris_path and hasattr(swe, "set_ephe_path"):
        swe.set_ephe_path(ephemeris_path)

    jd = swe.julday(day.year, day.month, day.day, 0.0)
    rsmi = swe.CALC_RISE if sunrise else swe.CALC_SET
    rsmi |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
    try:
        result, values = swe.rise_trans(jd, swe.SUN, rsmi, (longitude, latitude, 0), 0, 0, swe.FLG_SWIEPH)
    except Exception:
        return None
    if result < 0:
        return None
    year, month, event_day, hour = swe.revjul(values[0])
    utc_moment = datetime(year, month, event_day, tzinfo=timezone.utc) + timedelta(hours=hour)
    return utc_moment.astimezone(tz).replace(microsecond=0)


def _sun_event(day: date, latitude: float, longitude: float, tz: tzinfo, *, sunrise: bool) -> datetime | None:
    zenith = 90.833
    day_of_year = day.timetuple().tm_yday
    longitude_hour = longitude / 15.0
    target_hour = 6 if sunrise else 18
    approx_time = day_of_year + ((target_hour - longitude_hour) / 24)
    mean_anomaly = (0.9856 * approx_time) - 3.289
    true_longitude = normalize_angle(
        mean_anomaly
        + (1.916 * sin(radians(mean_anomaly)))
        + (0.020 * sin(radians(2 * mean_anomaly)))
        + 282.634
    )
    right_ascension = degrees(atan(0.91764 * tan(radians(true_longitude))))
    right_ascension = normalize_angle(right_ascension)
    longitude_quadrant = floor(true_longitude / 90) * 90
    right_ascension_quadrant = floor(right_ascension / 90) * 90
    right_ascension = (right_ascension + longitude_quadrant - right_ascension_quadrant) / 15

    sin_declination = 0.39782 * sin(radians(true_longitude))
    cos_declination = cos(asin(sin_declination))
    cos_hour_angle = (
        cos(radians(zenith)) - (sin_declination * sin(radians(latitude)))
    ) / (cos_declination * cos(radians(latitude)))
    if cos_hour_angle > 1 or cos_hour_angle < -1:
        return None

    hour_angle = 360 - degrees(acos(cos_hour_angle)) if sunrise else degrees(acos(cos_hour_angle))
    local_mean_time = (hour_angle / 15) + right_ascension - (0.06571 * approx_time) - 6.622
    utc_hour = (local_mean_time - longitude_hour) % 24
    utc_moment = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=utc_hour)
    local_moment = utc_moment.astimezone(tz)
    if local_moment.date() < day:
        local_moment += timedelta(days=1)
    elif local_moment.date() > day:
        local_moment -= timedelta(days=1)
    return local_moment.replace(microsecond=0)


def normalize_angle(value: float) -> float:
    return value % 360.0


def _timezone_name(tz: tzinfo) -> str:
    return getattr(tz, "key", None) or str(tz)
