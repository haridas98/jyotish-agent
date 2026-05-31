from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition, CalculationSettings, EphemerisUnavailable
from apps.calculations.primitives import zodiac_placement


class FakeProvider:
    def __init__(self):
        self.moment = None
        self.bodies = None
        self.settings = None

    def planet_positions(self, moment, bodies, settings):
        self.moment = moment
        self.bodies = bodies
        self.settings = settings
        return {
            "Surya": BodyPosition(
                body="Surya",
                longitude=30.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(30.0),
            )
        }


def test_build_birth_chart_uses_local_timezone_and_provider():
    from apps.calculations.chart import build_birth_chart

    provider = FakeProvider()

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=provider,
    )

    assert provider.moment == datetime(2000, 1, 1, 15, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
    assert provider.settings == CalculationSettings()
    assert provider.bodies == ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]
    assert result["place"]["name"] == "Vrindavan"
    assert result["grahas"][0]["body"] == "Surya"
    assert result["grahas"][0]["rashi"] == "Vrishabha"
    assert result["grahas"][0]["nakshatra"] == "Krittika"


def test_build_birth_chart_rejects_missing_time():
    from apps.calculations.chart import ChartInputError, build_birth_chart

    with pytest.raises(ChartInputError, match="birth_time"):
        build_birth_chart(
            {
                "birth_date": "2000-01-01",
                "place_name": "Vrindavan",
            },
            provider=FakeProvider(),
        )


@pytest.mark.django_db
def test_birth_chart_api_returns_400_for_bad_input():
    response = APIClient().post(reverse("birth-chart"), {"birth_date": "2000-01-01"}, format="json")

    assert response.status_code == 400
    assert "birth_time" in response.data["error"]


@pytest.mark.django_db
def test_birth_chart_api_returns_503_when_ephemeris_missing(monkeypatch):
    def raise_unavailable(data):
        raise EphemerisUnavailable("install pyswisseph")

    monkeypatch.setattr("apps.calculations.views.build_birth_chart", raise_unavailable)

    response = APIClient().post(
        reverse("birth-chart"),
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 503
    assert response.data["error"] == "install pyswisseph"


@pytest.mark.django_db
def test_birth_chart_api_returns_chart(monkeypatch):
    def fake_build(data):
        return {
            "calculation_version": "mvp-0.1",
            "place": {"name": data["place_name"], "latitude": 27.58, "longitude": 77.7},
            "grahas": [{"body": "Surya", "longitude": 30.0, "rashi": "Vrishabha"}],
        }

    monkeypatch.setattr("apps.calculations.views.build_birth_chart", fake_build)

    response = APIClient().post(
        reverse("birth-chart"),
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["grahas"][0]["body"] == "Surya"
