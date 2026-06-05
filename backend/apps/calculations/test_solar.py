from datetime import date, datetime
from importlib import import_module
from zoneinfo import ZoneInfo

import pytest

try:
    from apps.calculations.solar import (
        SolarDay,
        daytime_inauspicious_periods,
        gulika_segment_for_moment,
        solar_day,
    )
except ModuleNotFoundError:
    SolarDay = None
    daytime_inauspicious_periods = None
    gulika_segment_for_moment = None
    solar_day = None


def require_solar_module():
    if solar_day is None:
        pytest.fail("solar calculation module is not implemented yet")


def test_solar_day_estimates_real_sunrise_and_sunset_for_place_timezone():
    require_solar_module()
    tz = ZoneInfo("Asia/Kolkata")

    result = solar_day(date(2026, 6, 2), 27.565, 77.659, tz)

    assert result.status == "calculated"
    assert result.sunrise.tzinfo == tz
    assert result.sunset.tzinfo == tz
    assert result.sunrise.date() == date(2026, 6, 2)
    assert result.sunset.date() == date(2026, 6, 2)
    assert result.sunrise.hour == 5
    assert result.sunset.hour == 19
    assert 800 <= result.daylight_minutes <= 840


def test_solar_day_supports_jhora_center_no_refraction_profile():
    require_solar_module()
    try:
        import_module("swisseph")
    except ImportError:
        pytest.skip("pyswisseph is optional")
    tz = ZoneInfo("Asia/Yekaterinburg")

    result = solar_day(date(1998, 4, 30), 53.6304, 55.9502, tz, source="swiss_center_no_refraction")

    assert result.status == "calculated"
    assert result.sunrise.strftime("%H:%M") == "06:50"
    assert result.sunset.strftime("%H:%M") == "21:37"
    assert "disc center" in result.method


def test_daytime_inauspicious_periods_use_weekday_segment_tables():
    require_solar_module()
    tz = ZoneInfo("Asia/Kolkata")
    day = SolarDay(
        date=date(2026, 6, 2),
        timezone="Asia/Kolkata",
        sunrise=datetime(2026, 6, 2, 6, 0, tzinfo=tz),
        sunset=datetime(2026, 6, 2, 18, 0, tzinfo=tz),
        next_sunrise=datetime(2026, 6, 3, 6, 0, tzinfo=tz),
        status="calculated",
    )

    periods = {period["key"]: period for period in daytime_inauspicious_periods(day)}

    assert periods["rahu_kalam"]["segment"] == 7
    assert periods["rahu_kalam"]["starts_at"].endswith("15:00:00+05:30")
    assert periods["yamaganda"]["segment"] == 3
    assert periods["yamaganda"]["starts_at"].endswith("09:00:00+05:30")
    assert periods["gulika_kala"]["segment"] == 5
    assert periods["gulika_kala"]["starts_at"].endswith("12:00:00+05:30")


def test_gulika_segment_for_moment_uses_actual_day_or_night_window():
    require_solar_module()
    tz = ZoneInfo("Asia/Kolkata")
    day_moment = datetime(2026, 6, 2, 10, 0, tzinfo=tz)
    night_moment = datetime(2026, 6, 2, 22, 0, tzinfo=tz)

    day_segment = gulika_segment_for_moment(day_moment, 27.565, 77.659)
    night_segment = gulika_segment_for_moment(night_moment, 27.565, 77.659)

    assert day_segment["period"] == "day"
    assert day_segment["segment"] == 5
    assert day_segment["midpoint"].startswith("2026-06-02T13:")
    assert night_segment["period"] == "night"
    assert night_segment["midpoint"] > night_moment.isoformat()
