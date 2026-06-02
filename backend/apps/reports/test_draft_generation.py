import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_generate_draft_analysis_for_packet_keeps_review_status_draft_and_saves_record():
    try:
        from apps.reports.draft_generation import generate_draft_analysis_for_packet
        from apps.reports.models import GeneratedAnalysisDraft
    except (ImportError, ModuleNotFoundError):
        pytest.fail("draft analysis generation is not implemented yet")

    packet = {
        "schema_version": "jyotish-analysis-packet-v1",
        "prompt_markdown": "Generate cited draft.",
        "citations": [{"title": "Bhagavad-gita 9.22"}],
    }

    def fake_llm(prompt: str) -> dict[str, object]:
        assert "Generate cited draft" in prompt
        return {
            "review_status": "approved",
            "language": "ru",
            "sections": [
                {
                    "title": "Главное",
                    "body": "Черновик по карте.",
                    "citation_titles": ["Bhagavad-gita 9.22"],
                    "review_notes": [],
                }
            ],
        }

    result = generate_draft_analysis_for_packet(
        packet,
        input_snapshot={"birth_date": "2000-01-01"},
        kind="birth_chart",
        llm_client=fake_llm,
        provider="test",
        model="test-model",
    )

    assert result["review_status"] == "draft"
    assert result["source_policy"] == "citation_first"
    assert result["sections"][0]["citation_titles"] == ["Bhagavad-gita 9.22"]
    record = GeneratedAnalysisDraft.objects.get()
    assert record.kind == "birth_chart"
    assert record.review_status == "draft"
    assert record.output_json["review_status"] == "draft"
    assert record.provider == "test"
    assert record.model == "test-model"


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_draft_analysis_api_returns_saved_draft(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_draft_analysis",
        lambda data, citation_search=None, interpretation_provider=None: {
            "id": 7,
            "kind": "birth_chart",
            "review_status": "draft",
            "source_policy": "citation_first",
            "sections": [{"title": "Главное", "body": "Черновик.", "citation_titles": []}],
        },
    )

    response = APIClient().post(
        "/api/reports/birth-chart/draft-analysis",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["review_status"] == "draft"
    assert response.data["id"] == 7
