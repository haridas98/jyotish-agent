import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition
from apps.calculations.primitives import zodiac_placement
from apps.reports.birth_report import compose_birth_report


class ReportProvider:
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
                longitude=132.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(132.0),
            ),
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


def test_compose_birth_report_uses_chart_facts_citations_and_vaishnava_guard():
    def citation_search(query: str):
        return [
            {
                "title": "Bhagavad-gita 9.22",
                "work_title": "Bhagavad-gita As It Is",
                "body": "Krishna protects His devotee.",
                "public_url": "http://127.0.0.1:3001/texts/20",
            }
        ]

    result = compose_birth_report(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "as_of_date": "2025-01-01",
        },
        provider=ReportProvider(),
        citation_search=citation_search,
    )

    assert result["chart"]["ascendant"]["rashi"] == "Karka"
    assert result["report"]["review_status"] == "draft"
    assert result["report"]["chart_facts"]["grahas"]["Chandra"]["house"] == 2
    assert result["report"]["person_summary"]["core_factors"][0]["label"] == "Lagna"
    assert result["report"]["person_summary"]["core_factors"][0]["value"] == "Karka"
    birth_context = {row["label"]: row["value"] for row in result["report"]["person_summary"]["birth_context"]}
    assert birth_context["Calculation model"] == "drik_siddhanta"
    assert birth_context["Node type"] == "true"
    assert birth_context["House system"] == "whole_sign"
    assert birth_context["Timezone source"] == "iana"
    assert result["report"]["person_summary"]["graha_houses"][1]["body"] == "Chandra"
    assert result["report"]["person_summary"]["graha_houses"][1]["house"] == 2
    assert result["report"]["person_summary"]["detailed_positions"][0]["body"] == "Surya"
    assert result["report"]["person_summary"]["detailed_positions"][0]["sign_degrees_dms"]
    assert result["report"]["person_summary"]["detailed_positions"][0]["rashi_lord"] == "Surya"
    assert result["report"]["person_summary"]["dasha"]["birth_mahadasha_lord"] == "Ketu"
    assert result["report"]["person_summary"]["dasha"]["current_mahadasha"]["lord"] == "Surya"
    assert result["report"]["person_summary"]["dasha"]["current_antardasha"]["parent_lord"] == "Surya"
    assert len(result["report"]["person_summary"]["dasha"]["current_mahadasha_antardashas"]) == 9
    houses = result["report"]["person_summary"]["houses"]
    assert len(houses) == 12
    assert houses[0]["house"] == 1
    assert houses[0]["rashi"] == "Karka"
    assert houses[0]["grahas"] == []
    assert houses[1]["grahas"] == ["Surya", "Chandra"]
    assert result["report"]["sections"][0]["key"] == "calculation_summary"
    assert result["report"]["sections"][0]["title"] == "Расчётная сводка"
    assert "Место рождения сопоставлено" in result["report"]["sections"][0]["body"]
    assert result["report"]["sections"][1]["title"] == "Панчанга"
    assert "Титхи:" in result["report"]["sections"][1]["body"]
    assert result["report"]["sections"][2]["title"] == "Вимшоттари"
    assert "махадаша" in result["report"]["sections"][2]["body"]
    guidance = next(section for section in result["report"]["sections"] if section["key"] == "devotional_guidance")
    assert guidance["title"] == "Вайшнавские рекомендации"
    assert guidance["citations"][0]["title"] == "Bhagavad-gita 9.22"
    assert "Кришн" in guidance["body"]
    assert "Харе Кришна" in guidance["body"]
    assert "Worship Shani" not in guidance["body"]


def test_compose_birth_report_accepts_interpretation_sections():
    result = compose_birth_report(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=ReportProvider(),
        interpretation_provider=lambda chart: [
            {
                "key": "interpretation:kanya-lagna-service",
                "title": "Service Orientation",
                "body": f"{chart['ascendant']['rashi']} lagna section.",
                "review_status": "approved",
                "calculation_only": False,
                "citations": [
                    {
                        "title": "Bhagavad-gita 9.22",
                        "work_title": "Bhagavad-gita As It Is",
                        "snippet": "Krishna protects His devotee.",
                        "public_url": "http://127.0.0.1:3001/bg/9/22",
                    }
                ],
            }
        ],
    )

    keys = [section["key"] for section in result["report"]["sections"]]

    assert "interpretation:kanya-lagna-service" in keys


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_report_api_returns_report(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.compose_birth_report",
        lambda data, citation_search=None, interpretation_provider=None: {
            "chart": {"grahas": []},
            "report": {
                "review_status": "draft",
                "sections": [],
            },
        },
    )

    response = APIClient().post(
        "/api/reports/birth-chart",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["report"]["review_status"] == "draft"
