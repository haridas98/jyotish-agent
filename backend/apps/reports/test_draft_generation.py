import pytest
from django.contrib.auth import get_user_model
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
                    "title": "Main",
                    "body": "Draft body.",
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


def test_normalize_llm_output_extracts_json_markdown_fence():
    from apps.reports.draft_generation import _normalize_llm_output

    output = _normalize_llm_output(
        """```json
{
  "review_status": "draft",
  "language": "ru",
  "sections": [
    {
      "title": "Core",
      "body": "Analysis.",
      "source_traces": [
        {"condition_key": "lagna", "work_title": "Brhat Jataka"}
      ],
      "citation_titles": []
    }
  ]
}
```"""
    )

    assert output["sections"][0]["title"] == "Core"
    assert output["sections"][0]["source_traces"][0]["work_title"] == "Brhat Jataka"


@pytest.mark.django_db
def test_birth_chart_draft_analysis_without_client_is_disabled(monkeypatch):
    from apps.reports import draft_generation

    monkeypatch.setattr(
        draft_generation,
        "build_analysis_packet",
        lambda *_args, **_kwargs: {"prompt_markdown": "Legacy prompt"},
    )

    with pytest.raises(draft_generation.DraftGenerationUnavailable, match="codex_cli"):
        draft_generation.generate_birth_chart_draft_analysis({"birth_date": "2000-01-01"})


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_draft_analysis_api_is_disabled():
    user = get_user_model().objects.create_user(username="draft-api-owner", password="strong-pass-108")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/draft-analysis",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 410
    assert response.data["error"] == "draft_analysis_disabled"
    assert "codex-analysis" in response.data["message"]


@pytest.mark.django_db
def test_birth_draft_analysis_api_requires_authentication():
    response = APIClient().post(
        "/api/reports/birth-chart/draft-analysis",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code in {401, 403}
