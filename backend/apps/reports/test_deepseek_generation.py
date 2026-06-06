import io
import json

import pytest
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_generate_birth_chart_deepseek_analysis_saves_free_deepseek_draft(monkeypatch):
    from apps.reports.deepseek_generation import generate_birth_chart_deepseek_analysis
    from apps.reports.models import GeneratedAnalysisDraft

    monkeypatch.setattr(
        "apps.reports.deepseek_generation.build_analysis_packet",
        lambda *args, **kwargs: {
            "schema_version": "jyotish-analysis-packet-v1",
            "context": {"chart": {"grahas": []}},
        },
    )

    result = generate_birth_chart_deepseek_analysis(
        {"birth_date": "1998-04-30"},
        deepseek_runner=lambda prompt: json.dumps(
            {
                "language": "ru",
                "sections": [
                    {
                        "title": "Главное",
                        "body": "DeepSeek рабочий обзор.",
                        "citation_titles": [],
                    }
                ],
            }
        ),
        refresh_evidence=False,
    )

    assert result["kind"] == "birth_chart_deepseek"
    assert result["provider"] == "free_deepseek"
    assert result["engine_label"] == "Сгенерировано с помощью DeepSeek"
    record = GeneratedAnalysisDraft.objects.get()
    assert record.kind == "birth_chart_deepseek"
    assert record.provider == "free_deepseek"


def test_extract_deepseek_text_reads_openai_compatible_choice():
    from apps.reports.deepseek_generation import _extract_deepseek_text

    assert (
        _extract_deepseek_text({"choices": [{"message": {"content": "{\"sections\": []}"}}]})
        == "{\"sections\": []}"
    )


@override_settings(FREE_DEEPSEEK_MODEL="deepseek-chat")
def test_smoke_free_deepseek_command_outputs_provider_json(monkeypatch):
    def fake_chat_client():
        return lambda prompt: json.dumps(
            {
                "language": "ru",
                "sections": [{"title": "Smoke", "body": "ok", "citation_titles": []}],
            }
        )

    monkeypatch.setattr("apps.reports.deepseek_generation.free_deepseek_chat_client", fake_chat_client)

    stdout = io.StringIO()
    call_command("smoke_free_deepseek", "--prompt", "ping", stdout=stdout)

    payload = json.loads(stdout.getvalue())
    assert payload["status"] == "ok"
    assert payload["provider"] == "free_deepseek"
    assert payload["model"] == "deepseek-chat"
    assert payload["section_count"] == 1
    assert payload["message_excerpt"] == "ok"


def test_deepseek_client_wraps_timeout(monkeypatch):
    from apps.reports.deepseek_generation import free_deepseek_chat_client
    from apps.reports.draft_generation import DraftGenerationUnavailable

    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr("apps.reports.deepseek_generation.request.urlopen", raise_timeout)

    with pytest.raises(DraftGenerationUnavailable, match="DeepSeek API timed out"):
        free_deepseek_chat_client()("prompt")


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_deepseek_analysis_api_returns_saved_draft(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_deepseek_analysis",
        lambda data, citation_search=None, research_search=None, interpretation_provider=None, refresh_evidence=False: {
            "id": 11,
            "kind": "birth_chart_deepseek",
            "provider": "free_deepseek",
            "engine_label": "Сгенерировано с помощью DeepSeek",
            "review_status": "private_partial",
            "source_policy": "private_shastra_research_first",
            "sections": [{"title": "Главное", "body": "DeepSeek.", "citation_titles": []}],
        },
    )

    response = APIClient().post(
        "/api/reports/birth-chart/deepseek-analysis",
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Стерлитамак",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "birth_chart_deepseek"
    assert response.data["engine_label"] == "Сгенерировано с помощью DeepSeek"
