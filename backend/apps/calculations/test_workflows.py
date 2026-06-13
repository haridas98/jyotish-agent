from datetime import datetime

import pytest
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition, CalculationSettings
from apps.calculations.primitives import zodiac_placement


class WorkflowProvider:
    def __init__(self):
        self.settings_seen: list[CalculationSettings] = []

    def planet_positions(
        self,
        moment: datetime,
        bodies: list[str],
        settings: CalculationSettings,
    ) -> dict[str, BodyPosition]:
        self.settings_seen.append(settings)
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


class TithiPraveshaProvider:
    def __init__(self):
        self.settings_seen: list[CalculationSettings] = []

    def planet_positions(
        self,
        moment: datetime,
        bodies: list[str],
        settings: CalculationSettings,
    ) -> dict[str, BodyPosition]:
        self.settings_seen.append(settings)
        sun_longitude = 0.0
        if moment.year == 2000:
            moon_longitude = 24.0
        else:
            year_start = datetime(moment.year, 1, 1, tzinfo=moment.tzinfo)
            elapsed_days = (moment - year_start).total_seconds() / 86400.0
            moon_longitude = (elapsed_days * 24.0) % 360.0
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
        return BodyPosition(
            body="Lagna",
            longitude=90.0,
            latitude=None,
            distance_au=None,
            speed_longitude=None,
            placement=zodiac_placement(90.0),
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
    assert result["interpretation_plan"]["kind"] == "transits"
    assert "gochara" in result["interpretation_plan"]["source_anchors"]
    assert "house_from_moon" in result["interpretation_plan"]["required_factors"]
    assert surya["rashi"] == "Mesha"
    assert surya["house_from_lagna"] == 1
    assert surya["house_from_moon"] == 1


def test_build_transit_report_reuses_calculation_settings_for_transit_chart():
    from apps.calculations.workflows import build_transit_report

    provider = WorkflowProvider()

    build_transit_report(
        {
            "birth_date": "2000-01-01",
            "birth_time": "10:00",
            "place_name": "Vrindavan",
            "node_type": "mean",
            "as_of_date": "2026-06-01",
            "as_of_time": "09:00",
        },
        provider=provider,
    )

    assert [settings.node_type for settings in provider.settings_seen[:2]] == ["mean", "mean"]


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
            "relationship_context": {
                "role": "father",
                "label": "Отец",
                "focus_houses": [1, 9, 10, 4],
                "focus_vargas": ["D1", "D12"],
                "prompt_hint": "читать как связь с отцом",
                "link_status": "accepted",
            },
        },
        provider=WorkflowProvider(),
    )

    assert result["status"] == "calculated_needs_tradition_review"
    assert result["coverage"]["system"] == "ashtakuta_plus_chart_analysis"
    assert result["coverage"]["calculated_kutas"] == 8
    assert result["coverage"]["total_kutas"] == 8
    assert result["coverage"]["calculated_perspectives"] >= 7
    assert result["coverage"]["status"] == "multi_factor_needs_shastra_citation_review"
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
    assert "Кришне" in result["vaishnava_note"]


    analysis = result["analysis"]
    perspective_keys = {row["key"] for row in analysis["perspectives"]}
    assert analysis["status"] == "calculated_needs_shastra_citation_review"
    assert {
        "ashtakuta",
        "lagna_lagna",
        "moon_mind",
        "seventh_house",
        "shukra_mangala",
        "guru_shukra",
        "dasha_context",
    } <= perspective_keys
    assert analysis["chart_summaries"]["person_a"]["lagna"]["rashi"] == "Mesha"
    assert analysis["chart_summaries"]["person_a"]["seventh_house"]["rashi"] == "Tula"
    assert analysis["chart_summaries"]["person_a"]["seventh_house"]["lord"] == "Shukra"
    assert analysis["chart_summaries"]["person_a"]["seventh_lord"]["house"] == 8
    seventh = next(row for row in analysis["perspectives"] if row["key"] == "seventh_house")
    assert seventh["status"] == "caution"
    assert any("person_a seventh lord Shukra in house 8" in item for item in seventh["findings"])
    assert analysis["vaishnava_guard"] == "final_guidance_requires_sadhu_guru_shastra_review"
    assert result["interpretation_plan"]["kind"] == "compatibility"
    assert result["relationship_context"]["role"] == "father"
    assert result["relationship_context"]["focus_houses"] == [1, 9, 10, 4]
    assert result["relationship_context"]["focus_vargas"] == ["D1", "D12"]
    assert result["relationship_context"]["link_status"] == "accepted"
    assert "ashtakuta" in result["interpretation_plan"]["required_factors"]
    assert "seventh_house" in result["interpretation_plan"]["required_factors"]
    assert "relationship_role:father" in result["interpretation_plan"]["required_factors"]
    assert "house_9" in result["interpretation_plan"]["required_factors"]
    assert "varga_d12" in result["interpretation_plan"]["required_factors"]
    assert result["interpretation_plan"]["client_text_sequence"][-1] == "gaudiya_guard"


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
    assert result["purpose"] == "general"
    assert result["interpretation_plan"]["kind"] == "muhurta"
    assert "panchanga" in result["interpretation_plan"]["required_factors"]
    assert result["candidates"][0]["date"] == "2026-06-01"
    assert result["candidates"][0]["panchanga"]["tithi"]["name"] == "Ekadashi"
    assert result["candidates"][0]["purpose_profile"] == "General"
    assert result["candidates"][0]["score"] > result["candidates"][-1]["score"]
    assert "Кришн" in result["vaishnava_note"]


def test_build_muhurta_report_applies_purpose_specific_profile():
    from apps.calculations.workflows import build_muhurta_report

    result = build_muhurta_report(
        {
            "place_name": "Vrindavan",
            "start_date": "2026-06-01",
            "end_date": "2026-06-01",
            "time": "09:00",
            "purpose": "travel",
        },
        provider=WorkflowProvider(),
    )

    candidate = result["candidates"][0]

    assert result["purpose"] == "travel"
    assert result["purpose_profile"] == "Travel"
    assert candidate["purpose"] == "travel"
    assert any(
        row["field"] == "tithi" and row["status"] == "supporting"
        for row in candidate["purpose_adjustments"]
    )


def test_build_muhurta_report_reuses_calculation_settings_for_candidate_charts():
    from apps.calculations.workflows import build_muhurta_report

    provider = WorkflowProvider()

    build_muhurta_report(
        {
            "place_name": "Vrindavan",
            "start_date": "2026-06-01",
            "end_date": "2026-06-02",
            "time": "09:00",
            "node_type": "mean",
        },
        provider=provider,
    )

    assert [settings.node_type for settings in provider.settings_seen] == ["mean", "mean"]


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


def test_build_tithi_pravesha_report_finds_same_solar_lunar_angle_return():
    from apps.calculations.workflows import build_tithi_pravesha_report

    provider = TithiPraveshaProvider()

    result = build_tithi_pravesha_report(
        {
            "birth_date": "2000-01-01",
            "birth_time": "10:00",
            "place_name": "Vrindavan",
            "target_year": 2026,
            "search_days": 3,
            "node_type": "mean",
        },
        provider=provider,
    )

    assert result["status"] == "calculated_needs_jhora_audit"
    assert result["target_year"] == 2026
    assert result["natal"]["solar_lunar_angle"] == 24.0
    assert result["return"]["date"] == "2026-01-01"
    assert result["return"]["time"].startswith("23:59")
    assert result["return"]["delta_degrees"] <= 0.01
    assert result["return"]["chart"]["ascendant"]["rashi"] == "Karka"
    assert result["annual_context"]["panchanga"]["tithi"]["number"] == 2
    assert result["interpretation_plan"]["kind"] == "tithi_pravesha"
    assert "annual_chart" in result["interpretation_plan"]["required_factors"]
    assert result["annual_context"]["tajaka"]["status"] == "baseline_calculated_needs_tajaka_review"
    assert result["annual_context"]["tajaka"]["muntha"]["rashi"] == "Kanya"
    assert result["annual_context"]["tajaka"]["muntha"]["house_from_annual_lagna"] == 3
    assert all(settings.node_type == "mean" for settings in provider.settings_seen)


def test_build_tithi_pravesha_report_requires_target_year():
    from apps.calculations.workflows import build_tithi_pravesha_report

    with pytest.raises(ValueError, match="target_year"):
        build_tithi_pravesha_report(
            {
                "birth_date": "2000-01-01",
                "birth_time": "10:00",
                "place_name": "Vrindavan",
            },
            provider=TithiPraveshaProvider(),
        )


@pytest.mark.django_db
def test_transit_api_returns_400_for_missing_birth_data():
    response = APIClient().post("/api/calculations/transits", {"birth_date": "2000-01-01"}, format="json")

    assert response.status_code == 400
    assert "birth_time" in response.data["error"]


@pytest.mark.django_db
def test_tithi_pravesha_api_returns_400_for_missing_birth_data():
    response = APIClient().post("/api/calculations/tithi-pravesha", {"target_year": 2026}, format="json")

    assert response.status_code == 400
    assert "birth_date" in response.data["error"]


def test_build_tajaka_report_wraps_tithi_pravesha_and_muntha():
    from apps.calculations.workflows import build_tajaka_report

    result = build_tajaka_report(
        {
            "birth_date": "2000-01-01",
            "birth_time": "10:00",
            "place_name": "Vrindavan",
            "target_year": 2026,
            "search_days": 3,
        },
        provider=TithiPraveshaProvider(),
    )

    assert result["status"] == "baseline_calculated_needs_full_tajaka_audit"
    assert result["tithi_pravesha"]["target_year"] == 2026
    assert result["tajaka"]["muntha"]["rashi"] == "Kanya"
    assert result["interpretation_plan"]["kind"] == "tajaka"
    assert "muntha" in result["interpretation_plan"]["required_factors"]
    assert "sahams" in result["tajaka"]["open_items"]


def test_build_prashna_report_returns_horary_anchors():
    from apps.calculations.workflows import build_prashna_report

    result = build_prashna_report(
        {
            "question": "Should I travel?",
            "question_date": "2026-06-04",
            "question_time": "09:30",
            "place_name": "Vrindavan",
        },
        provider=WorkflowProvider(),
    )

    assert result["status"] == "baseline_calculated_needs_prashna_tradition_review"
    assert result["question"]["text"] == "Should I travel?"
    assert result["indicators"]["lagna"]["rashi"] == "Karka"
    assert result["indicators"]["lagna_lord"] == "Chandra"
    assert result["interpretation_plan"]["kind"] == "prashna"
    assert "question_lagna" in result["interpretation_plan"]["required_factors"]
    assert result["audit"]["public_interpretation_status"] == "blocked_until_prashna_text_review"


def test_build_mundane_report_returns_event_chart_anchors():
    from apps.calculations.workflows import build_mundane_report

    result = build_mundane_report(
        {
            "event_type": "ingress",
            "event_date": "2026-06-04",
            "event_time": "09:30",
            "place_name": "Vrindavan",
        },
        provider=WorkflowProvider(),
    )

    assert result["status"] == "baseline_event_chart_needs_mundane_rules_review"
    assert result["event"]["type"] == "ingress"
    assert result["interpretation_plan"]["kind"] == "mundane"
    assert "slow_planets" in result["interpretation_plan"]["required_factors"]
    assert result["indicators"]["tenth_house_rashi"] == "Mesha"
    assert result["indicators"]["slow_planets"][0]["body"] == "Guru"
