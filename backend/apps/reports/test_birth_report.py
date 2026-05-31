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
        },
        provider=ReportProvider(),
        citation_search=citation_search,
    )

    assert result["chart"]["ascendant"]["rashi"] == "Karka"
    assert result["report"]["review_status"] == "draft"
    assert result["report"]["sections"][0]["key"] == "calculation_summary"
    guidance = next(section for section in result["report"]["sections"] if section["key"] == "devotional_guidance")
    assert guidance["citations"][0]["title"] == "Bhagavad-gita 9.22"
    assert "Krishna" in guidance["body"]
    assert "Worship Shani" not in guidance["body"]


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_report_api_returns_report(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.compose_birth_report",
        lambda data, citation_search=None: {
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
