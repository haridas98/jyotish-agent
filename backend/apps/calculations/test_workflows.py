from datetime import datetime

import pytest
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition, CalculationSettings
from apps.calculations.primitives import zodiac_placement


class WorkflowProvider:
    def planet_positions(
        self,
        moment: datetime,
        bodies: list[str],
        settings: CalculationSettings,
    ) -> dict[str, BodyPosition]:
        if moment.year == 2000:
            moon_longitude = 0.0 if moment.day == 1 else 40.0
            sun_longitude = 10.0
        elif moment.day == 1:
            moon_longitude = 120.0
            sun_longitude = 0.0
        elif moment.day == 2:
            moon_longitude = 96.0
            sun_longitude = 0.0
        else:
            moon_longitude = 24.0
            sun_longitude = 0.0

        values = {
            "Surya": sun_longitude,
            "Chandra": moon_longitude,
            "Mangala": 150.0,
            "Budha": 160.0,
            "Guru": 180.0,
            "Shukra": 210.0,
            "Shani": 240.0,
            "Rahu": 270.0,
            "Ketu": 90.0,
        }
        return {
            body: BodyPosition(
                body=body,
                longitude=values[body],
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=0.1,
                placement=zodiac_placement(values[body]),
            )
            for body in bodies
            if body in values
        }

    def ascendant_position(self, moment, latitude, longitude, settings):
        longitude_value = 0.0 if moment.year == 2000 else 90.0
        return BodyPosition(
            body="Lagna",
            longitude=longitude_value,
            latitude=None,
            distance_au=None,
            speed_longitude=None,
            placement=zodiac_placement(longitude_value),
        )


def test_build_transit_report_compares_transits_to_natal_lagna_and_moon():
    from apps.calculations.workflows import build_transit_report

    result = build_transit_report(
        {
            "birth_date": "2000-01-01",
            "birth_time": "10:00",
            "place_name": "Vrindavan",
            "as_of_date": "2026-06-01",
            "as_of_time": "09:00",
        },
        provider=WorkflowProvider(),
    )

    surya = next(row for row in result["transits"] if row["body"] == "Surya")

    assert result["status"] == "calculated"
    assert result["natal"]["lagna"]["rashi"] == "Mesha"
    assert result["natal"]["moon"]["nakshatra"] == "Ashwini"
    assert result["as_of"]["date"] == "2026-06-01"
    assert surya["rashi"] == "Mesha"
    assert surya["house_from_lagna"] == 1
    assert surya["house_from_moon"] == 1


def test_build_compatibility_report_scores_moon_tara_and_rashi_distance():
    from apps.calculations.workflows import build_compatibility_report

    result = build_compatibility_report(
        {
            "person_a": {
                "birth_date": "2000-01-01",
                "birth_time": "10:00",
                "place_name": "Vrindavan",
            },
            "person_b": {
                "birth_date": "2000-01-02",
                "birth_time": "10:00",
                "place_name": "Vrindavan",
            },
        },
        provider=WorkflowProvider(),
    )

    assert result["status"] == "calculated_needs_tradition_review"
    assert result["score"] == {
        "total": 14.5,
        "max": 36.0,
        "percent": 40.28,
    }
    assert result["moon"]["person_a"]["nakshatra"] == "Ashwini"
    assert result["moon"]["person_b"]["nakshatra"] == "Rohini"
    assert result["moon"]["rashi_distance_a_to_b"] == 2
    assert set(result["kuta"]) == {
        "varna",
        "vashya",
        "tara",
        "yoni",
        "graha_maitri",
        "gana",
        "bhakoot",
        "nadi",
    }
    assert result["kuta"]["varna"]["score"] == 1.0
    assert result["kuta"]["vashya"]["score"] == 2.0
    assert result["kuta"]["tara"]["score"] == 1.5
    assert result["kuta"]["tara"]["max_score"] == 3.0
    assert result["kuta"]["bhakoot"]["score"] == 0.0
    assert result["kuta"]["nadi"]["score"] == 0.0
    assert [row["key"] for row in result["kuta_rows"]] == [
        "varna",
        "vashya",
        "tara",
        "yoni",
        "graha_maitri",
        "gana",
        "bhakoot",
        "nadi",
    ]
    assert result["kuta_rows"][0] == {
        "key": "varna",
        "name": "Varna",
        "score": 1.0,
        "max_score": 1.0,
        "status": "calculated",
        "details": "Kshatriya / Vaishya",
    }
    assert result["assessment"]["level"] == "caution"
    assert result["assessment"]["caution_count"] == 2
    assert "садху-сангу" in result["assessment"]["note"]


def test_build_muhurta_report_ranks_candidates_by_panchanga_rules():
    from apps.calculations.workflows import build_muhurta_report

    result = build_muhurta_report(
        {
            "place_name": "Vrindavan",
            "start_date": "2026-06-01",
            "end_date": "2026-06-03",
            "time": "09:00",
        },
        provider=WorkflowProvider(),
    )

    assert result["status"] == "calculated_needs_task_review"
    assert result["candidates"][0]["date"] == "2026-06-01"
    assert result["candidates"][0]["panchanga"]["tithi"]["name"] == "Ekadashi"
    assert result["candidates"][0]["score"] > result["candidates"][-1]["score"]
    assert "Кришн" in result["vaishnava_note"]


def test_build_muhurta_report_penalizes_rahu_kalam_candidate_time():
    from apps.calculations.workflows import build_muhurta_report

    result = build_muhurta_report(
        {
            "place_name": "Vrindavan",
            "start_date": "2026-06-02",
            "end_date": "2026-06-02",
            "time": "16:00",
        },
        provider=WorkflowProvider(),
    )

    candidate = result["candidates"][0]

    assert candidate["day_periods"][0]["key"] == "rahu_kalam"
    assert candidate["blocked_periods"][0]["key"] == "rahu_kalam"
    assert any("Rahu Kalam" in reason for reason in candidate["reasons"])
    assert candidate["score"] <= 20


@pytest.mark.django_db
def test_transit_api_returns_400_for_missing_birth_data():
    response = APIClient().post("/api/calculations/transits", {"birth_date": "2000-01-01"}, format="json")

    assert response.status_code == 400
    assert "birth_time" in response.data["error"]
