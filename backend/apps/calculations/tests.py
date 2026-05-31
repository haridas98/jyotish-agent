from datetime import datetime, timezone

import pytest

from apps.calculations.primitives import julian_day, zodiac_placement


def test_julian_day_j2000_epoch():
    moment = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)

    assert julian_day(moment) == pytest.approx(2451545.0)


def test_julian_day_requires_timezone():
    with pytest.raises(ValueError, match="timezone-aware"):
        julian_day(datetime(2000, 1, 1, 12, 0))


def test_zodiac_placement_for_zero_aries():
    placement = zodiac_placement(0)

    assert placement.rashi == "Mesha"
    assert placement.nakshatra == "Ashwini"
    assert placement.pada == 1
    assert placement.navamsa == "Mesha"


def test_zodiac_placement_wraps_degrees():
    placement = zodiac_placement(360 + 30)

    assert placement.longitude == 30
    assert placement.rashi == "Vrishabha"
    assert placement.nakshatra == "Krittika"
    assert placement.pada == 2
    assert placement.navamsa == "Makara"


def test_zodiac_placement_handles_nakshatra_boundary():
    placement = zodiac_placement(26 + 40 / 60)

    assert placement.nakshatra == "Krittika"
    assert placement.pada == 1
