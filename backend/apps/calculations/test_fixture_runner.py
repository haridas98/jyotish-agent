from datetime import datetime

from apps.calculations.ephemeris import BodyPosition
from apps.calculations.fixture_runner import run_accuracy_fixture
from apps.calculations.primitives import zodiac_placement


class FixtureProvider:
    def planet_positions(self, moment, bodies, settings):
        return {
            "Surya": BodyPosition(
                body="Surya",
                longitude=120.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(120.0),
            ),
            "Chandra": BodyPosition(
                body="Chandra",
                longitude=132.5,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(132.5),
            ),
        }

    def ascendant_position(self, moment: datetime, latitude, longitude, settings):
        return BodyPosition(
            body="Lagna",
            longitude=90.0,
            latitude=None,
            distance_au=None,
            speed_longitude=None,
            placement=zodiac_placement(90.0),
        )


def test_run_accuracy_fixture_builds_chart_and_compares_expected_values():
    fixture = {
        "id": "fixture-runner-sample",
        "source": "unit-test",
        "input": {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        "tolerances": {
            "planet_longitude_arcseconds": 0.1,
            "lagna_arcseconds": 0.1,
        },
        "expected": {
            "grahas": {
                "Surya": {
                    "longitude": 120.0,
                    "rashi": "Simha",
                    "nakshatra": "Magha",
                    "pada": 1,
                }
            },
            "ascendant": {
                "longitude": 90.0,
                "rashi": "Karka",
            },
            "panchanga": {
                "tithi": "Dvitiya",
            },
        },
    }

    result = run_accuracy_fixture(fixture, provider=FixtureProvider())

    assert result.fixture_id == "fixture-runner-sample"
    assert result.passed is True
    assert result.chart["calculation_version"] == "mvp-0.1"


def test_run_accuracy_fixture_marks_unreviewed_expected_source_as_not_authoritative():
    fixture = {
        "id": "unreviewed-case",
        "source": "internal-smoke",
        "review_status": "draft",
        "input": {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        "expected": {},
    }

    result = run_accuracy_fixture(fixture, provider=FixtureProvider())

    assert result.authoritative is False
    assert result.review_status == "draft"
