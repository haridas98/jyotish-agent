from datetime import datetime
from zoneinfo import ZoneInfo

from .panchanga import panchanga_from_longitudes


def test_panchanga_starts_shukla_pratipada_at_sun_moon_conjunction():
    result = panchanga_from_longitudes(
        sun_longitude=0.0,
        moon_longitude=0.0,
        local_moment=datetime(2026, 6, 1, 6, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
    )

    assert result["tithi"]["name"] == "Pratipada"
    assert result["tithi"]["paksha"] == "Shukla"
    assert result["karana"]["name"] == "Kimstughna"
    assert result["yoga"]["name"] == "Vishkambha"
    assert result["vara"]["name"] == "Somavara"


def test_panchanga_uses_elapsed_half_tithi_for_karana():
    result = panchanga_from_longitudes(
        sun_longitude=0.0,
        moon_longitude=13.0,
        local_moment=datetime(2026, 6, 2, 6, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
    )

    assert result["tithi"]["name"] == "Dvitiya"
    assert result["tithi"]["paksha"] == "Shukla"
    assert result["karana"]["name"] == "Balava"


def test_panchanga_wraps_krishna_paksha_and_final_yoga():
    result = panchanga_from_longitudes(
        sun_longitude=180.0,
        moon_longitude=170.0,
        local_moment=datetime(2026, 6, 7, 6, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
    )

    assert result["tithi"]["name"] == "Amavasya"
    assert result["tithi"]["paksha"] == "Krishna"
    assert result["yoga"]["name"] == "Vaidhriti"
    assert result["vara"]["name"] == "Ravivara"
