from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition
from apps.calculations.primitives import zodiac_placement


class AnalysisProvider:
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
            "Shani": BodyPosition(
                body="Shani",
                longitude=280.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=0.1,
                placement=zodiac_placement(280.0),
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


def test_build_analysis_packet_contains_codex_ready_prompt_policy_and_citations():
    try:
        from apps.reports.analysis_packet import build_analysis_packet
    except ModuleNotFoundError:
        pytest.fail("analysis packet service is not implemented yet")

    packet = build_analysis_packet(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "as_of_date": "2026-06-02",
        },
        provider=AnalysisProvider(),
        citation_search=lambda query: [
            {
                "title": "Bhagavad-gita 9.22",
                "work_title": "Bhagavad-gita As It Is",
                "body": "Krishna protects His devotee.",
                "public_url": "http://127.0.0.1:3100/bhagavad-gita/9/22",
            }
        ],
        interpretation_provider=lambda chart: [
            {
                "key": "interpretation:test",
                "title": "Test interpretation",
                "body": "Use service to Krishna as the framing.",
                "review_status": "approved",
                "calculation_only": False,
                "citations": [
                    {
                        "title": "Srimad-Bhagavatam 1.2.6",
                        "work_title": "Srimad-Bhagavatam",
                        "snippet": "Pure devotional service is supreme dharma.",
                        "public_url": "http://127.0.0.1:3100/srimad-bhagavatam/1/2/6",
                    }
                ],
            }
        ],
        research_search=lambda query: [
            {
                "title": "private full text chunk 0001",
                "work_title": "Phaladipika",
                "body": "Research-only yoga wording from private OCR.",
                "review_status": "research_only",
                "is_public_citation": False,
                "public_quote_policy": "blocked_until_approved",
            }
        ],
    )

    assert packet["schema_version"] == "jyotish-analysis-packet-v1"
    assert packet["status"] == "ready_for_generation"
    assert packet["generator_policy"]["language"] == "ru"
    assert packet["generator_policy"]["forbidden_outputs"][0] == "independent_demigod_worship"
    assert "compare_multiple_translation_variants" in packet["generator_policy"]["required_behaviors"]
    assert "public_quotation_from_unreviewed_translation" in packet["generator_policy"]["forbidden_outputs"]
    assert packet["report"]["source_policy"] == "citation_first"
    assert packet["context"]["birth"]["date"] == "2000-01-01"
    assert packet["context"]["explanation_schedule"][0]["key"] == "calculation_audit"
    assert packet["context"]["explanation_schedule"][-1]["key"] == "source_review_notes"
    assert packet["context"]["yoga_catalog_overview"]["total_yogas"] >= 90
    assert "nabhasa_akriti" in packet["context"]["yoga_catalog_overview"]["categories"]
    yoga_map = packet["context"]["detected_yoga_source_map"]
    assert yoga_map
    assert all(row["citation_policy"] == "required_for_public_interpretation" for row in yoga_map)
    assert any(row["source_mapping_status"] == "mapped_research_only" for row in yoga_map)
    citation_requests = packet["citation_requests"]
    assert citation_requests
    assert any(request["kind"] == "detected_yoga" for request in citation_requests)
    assert all(request["required_for_public_text"] for request in citation_requests)
    assert packet["context"]["chart_facts"]["grahas"]["Chandra"]["house"] == 2
    assert {citation["title"] for citation in packet["citations"]} == {
        "Srimad-Bhagavatam 1.2.6",
        "Bhagavad-gita 9.22",
    }
    assert packet["research_context"]["status"] == "private_research_not_public_citation"
    assert packet["research_context"]["items"][0]["work_title"] == "Phaladipika"
    assert packet["research_context"]["items"][0]["is_public_citation"] is False
    assert "OUTPUT JSON schema" in packet["prompt_markdown"]
    assert "explanation_schedule" in packet["prompt_markdown"]
    assert "detected_yoga_source_map" in packet["prompt_markdown"]
    assert "citation_requests" in packet["prompt_markdown"]
    assert "research_context" in packet["prompt_markdown"]
    assert "compare_multiple_translation_variants" in packet["prompt_markdown"]
    assert "cite_exact_edition_translator_and_reference" in packet["prompt_markdown"]
    assert "flag_translation_conflicts" in packet["prompt_markdown"]
    assert "не выдумывай цитаты" in packet["prompt_markdown"]
    assert "independent demigod" in packet["prompt_markdown"]


def test_build_compatibility_analysis_packet_contains_two_chart_context_and_perspective_requests():
    try:
        from apps.reports.analysis_packet import build_compatibility_analysis_packet
    except ImportError:
        pytest.fail("compatibility analysis packet service is not implemented yet")

    packet = build_compatibility_analysis_packet(
        {
            "person_a": {
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
            },
            "person_b": {
                "birth_date": "2001-02-03",
                "birth_time": "09:10",
                "place_name": "Mayapur",
            },
        },
        provider=AnalysisProvider(),
        citation_search=lambda query: [
            {
                "title": "Vivaha source anchor",
                "work_title": "Muhurta Chintamani",
                "body": "Marriage compatibility requires more than one factor.",
                "public_url": "http://127.0.0.1:3100/vivaha/source",
            }
        ],
    )

    assert packet["schema_version"] == "jyotish-compatibility-analysis-packet-v1"
    assert packet["status"] == "needs_citation_review"
    assert packet["generator_policy"]["required_behaviors"][0] == "compare_both_charts_from_multiple_angles"
    assert "compare_multiple_translation_variants" in packet["generator_policy"]["required_behaviors"]
    assert packet["context"]["compatibility"]["coverage"]["system"] == "ashtakuta_plus_chart_analysis"
    assert packet["context"]["person_a"]["chart"]["birth"]["date"] == "2000-01-01"
    assert packet["context"]["person_b"]["chart"]["birth"]["date"] == "2001-02-03"
    assert packet["context"]["compatibility"]["analysis"]["perspectives"]
    assert any(request["kind"] == "compatibility_perspective" for request in packet["citation_requests"])
    assert all(request["required_for_public_text"] for request in packet["citation_requests"])
    assert packet["citations"][0]["title"] == "Vivaha source anchor"
    assert "compatibility" in packet["prompt_markdown"]
    assert "person_a" in packet["prompt_markdown"]
    assert "person_b" in packet["prompt_markdown"]
    assert "compare_multiple_translation_variants" in packet["prompt_markdown"]
    assert "independent demigod" in packet["prompt_markdown"]


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_analysis_packet_api_returns_packet(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.build_analysis_packet",
        lambda data, citation_search=None, research_search=None, interpretation_provider=None: {
            "schema_version": "jyotish-analysis-packet-v1",
            "status": "ready_for_generation",
            "prompt_markdown": "prompt",
        },
    )

    response = APIClient().post(
        "/api/reports/birth-chart/analysis-packet",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["schema_version"] == "jyotish-analysis-packet-v1"


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_compatibility_analysis_packet_api_returns_packet(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.build_compatibility_analysis_packet",
        lambda data, citation_search=None, research_search=None: {
            "schema_version": "jyotish-compatibility-analysis-packet-v1",
            "status": "needs_citation_review",
            "prompt_markdown": "prompt",
        },
    )

    response = APIClient().post(
        "/api/reports/compatibility/analysis-packet",
        {
            "person_a": {
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
            },
            "person_b": {
                "birth_date": "2001-02-03",
                "birth_time": "09:10",
                "place_name": "Mayapur",
            },
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["schema_version"] == "jyotish-compatibility-analysis-packet-v1"


def test_build_analysis_packet_command_writes_json_and_prompt(monkeypatch, tmp_path):
    json_path = tmp_path / "packet.json"
    prompt_path = tmp_path / "packet.prompt.md"
    citation_requests_path = tmp_path / "citation-requests.json"

    monkeypatch.setattr(
        "apps.reports.management.commands.build_analysis_packet.build_analysis_packet",
        lambda data, citation_search=None, research_search=None, interpretation_provider=None: {
            "schema_version": "jyotish-analysis-packet-v1",
            "status": "ready_for_generation",
            "citation_requests": [{"key": "gaja_kesari", "kind": "detected_yoga"}],
            "prompt_markdown": "# Prompt\nUse packet.",
        },
    )

    call_command(
        "build_analysis_packet",
        "--birth-date",
        "2000-01-01",
        "--birth-time",
        "15:30",
        "--place-name",
        "Vrindavan",
        "--output",
        str(json_path),
        "--prompt-output",
        str(prompt_path),
        "--citation-requests-output",
        str(citation_requests_path),
    )

    assert '"schema_version": "jyotish-analysis-packet-v1"' in Path(json_path).read_text(encoding="utf-8")
    assert Path(prompt_path).read_text(encoding="utf-8") == "# Prompt\nUse packet."
    assert '"gaja_kesari"' in Path(citation_requests_path).read_text(encoding="utf-8")
