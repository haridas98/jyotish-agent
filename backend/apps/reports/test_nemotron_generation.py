import json

import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
@override_settings(NEMOTRON_MODEL="nvidia/nemotron-test:free")
def test_generate_birth_chart_nemotron_analysis_saves_nemotron_draft(monkeypatch):
    from apps.reports.models import GeneratedAnalysisDraft
    from apps.reports.nemotron_generation import generate_birth_chart_nemotron_analysis

    monkeypatch.setattr(
        "apps.reports.nemotron_generation.build_analysis_packet",
        lambda *args, **kwargs: {
            "schema_version": "jyotish-analysis-packet-v1",
            "context": {"chart": {"grahas": []}},
        },
    )

    result = generate_birth_chart_nemotron_analysis(
        {"birth_date": "1998-04-30"},
        nemotron_runner=lambda prompt: json.dumps(
            {
                "language": "ru",
                "sections": [
                    {
                        "title": "Main",
                        "body": "Nemotron overview.",
                        "citation_titles": [],
                    }
                ],
            }
        ),
        refresh_evidence=False,
    )

    assert result["kind"] == "birth_chart_nemotron"
    assert result["provider"] == "nemotron"
    assert result["model"] == "nvidia/nemotron-test:free"
    assert result["engine_label"] == "Сгенерировано с помощью Nemotron"
    record = GeneratedAnalysisDraft.objects.get()
    assert record.kind == "birth_chart_nemotron"
    assert record.provider == "nemotron"


def test_extract_nemotron_text_reads_openai_compatible_choice():
    from apps.reports.nemotron_generation import _extract_nemotron_text

    assert (
        _extract_nemotron_text({"choices": [{"message": {"content": "{\"sections\": []}"}}]})
        == "{\"sections\": []}"
    )


@override_settings(OPENROUTER_API_KEY="test-key")
def test_nemotron_client_wraps_timeout(monkeypatch):
    from apps.reports.draft_generation import DraftGenerationUnavailable
    from apps.reports.nemotron_generation import nemotron_chat_completions_client

    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr("apps.reports.nemotron_generation.request.urlopen", raise_timeout)

    with pytest.raises(DraftGenerationUnavailable, match="Nemotron API timed out"):
        nemotron_chat_completions_client()("prompt")


@override_settings(OPENROUTER_API_KEY="")
def test_nemotron_client_requires_openrouter_key():
    from apps.reports.draft_generation import DraftGenerationUnavailable
    from apps.reports.nemotron_generation import nemotron_chat_completions_client

    with pytest.raises(DraftGenerationUnavailable, match="OPENROUTER_API_KEY is missing"):
        nemotron_chat_completions_client()("prompt")


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="", NEMOTRON_ANALYSIS_ENABLED=False)
def test_birth_nemotron_analysis_api_is_disabled_by_default(monkeypatch):
    called = False

    def fail_if_called(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("Nemotron generator should not run when disabled")

    monkeypatch.setattr("apps.reports.views.generate_birth_chart_nemotron_analysis", fail_if_called)

    response = APIClient().post(
        "/api/reports/birth-chart/nemotron-analysis",
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Sterlitamak",
        },
        format="json",
    )

    assert response.status_code == 404
    assert response.data["error"] == "Nemotron analysis is disabled"
    assert called is False


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="", NEMOTRON_ANALYSIS_ENABLED=True)
def test_birth_nemotron_analysis_api_returns_saved_draft(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_nemotron_analysis",
        lambda data, citation_search=None, research_search=None, interpretation_provider=None, refresh_evidence=False: {
            "id": 12,
            "kind": "birth_chart_nemotron",
            "provider": "nemotron",
            "engine_label": "Сгенерировано с помощью Nemotron",
            "review_status": "private_partial",
            "source_policy": "private_shastra_research_first",
            "sections": [{"title": "Main", "body": "Nemotron.", "citation_titles": []}],
        },
    )

    response = APIClient().post(
        "/api/reports/birth-chart/nemotron-analysis",
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Sterlitamak",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "birth_chart_nemotron"
    assert response.data["engine_label"] == "Сгенерировано с помощью Nemotron"
