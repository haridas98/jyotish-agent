import json

import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_generate_birth_chart_qwen_analysis_saves_qwen_draft(monkeypatch):
    from apps.reports.models import GeneratedAnalysisDraft
    from apps.reports.qwen_generation import generate_birth_chart_qwen_analysis

    monkeypatch.setattr(
        "apps.reports.qwen_generation.build_analysis_packet",
        lambda *args, **kwargs: {
            "schema_version": "jyotish-analysis-packet-v1",
            "context": {"chart": {"grahas": []}},
        },
    )

    result = generate_birth_chart_qwen_analysis(
        {"birth_date": "1998-04-30"},
        qwen_runner=lambda prompt: json.dumps(
            {
                "language": "ru",
                "sections": [
                    {
                        "title": "Главное",
                        "body": "Альтернативный рабочий разбор.",
                        "citation_titles": [],
                    }
                ],
            }
        ),
        refresh_evidence=False,
    )

    assert result["kind"] == "birth_chart_qwen"
    assert result["provider"] == "qwen"
    assert result["engine_label"] == "Сгенерировано с помощью QWEN"
    record = GeneratedAnalysisDraft.objects.get()
    assert record.kind == "birth_chart_qwen"
    assert record.provider == "qwen"


def test_extract_qwen_text_reads_openai_compatible_choice():
    from apps.reports.qwen_generation import _extract_qwen_text

    assert (
        _extract_qwen_text({"choices": [{"message": {"content": "{\"sections\": []}"}}]})
        == "{\"sections\": []}"
    )


def test_qwen_client_wraps_timeout(monkeypatch):
    from apps.reports.draft_generation import DraftGenerationUnavailable
    from apps.reports.qwen_generation import qwen_chat_completions_client

    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr("apps.reports.qwen_generation.request.urlopen", raise_timeout)

    with pytest.raises(DraftGenerationUnavailable, match="QWEN API timed out"):
        qwen_chat_completions_client()("prompt")


@pytest.mark.django_db
def test_generate_birth_chart_qwen_analysis_reuses_matching_cached_record(monkeypatch):
    from apps.reports.models import GeneratedAnalysisDraft
    from apps.reports.qwen_generation import generate_birth_chart_qwen_analysis

    payload = {
        "birth_date": "1998-04-30",
        "birth_time": "13:45",
        "gender": "male",
        "timezone": "Asia/Yekaterinburg",
        "latitude": 53.6304,
        "longitude": 55.9502,
        "zodiac": "sidereal",
        "calculation_model": "drik_siddhanta",
        "ayanamsa": "lahiri",
        "node_type": "true",
        "ephemeris": "swiss",
        "house_system": "whole_sign",
        "bhava_system": "whole_sign",
        "varga_scheme": "parashara",
        "sunrise_source": "noaa",
        "timezone_source": "iana",
        "shadbala_profile": "bphs_classical",
    }
    GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_qwen",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="qwen",
        model="qwen3.7-max",
        input_snapshot=payload,
        output_json={
            "kind": "birth_chart_qwen",
            "provider": "qwen",
            "prompt_version": "qwen-overview-v1",
            "review_status": "private_final",
            "source_policy": "private_shastra_research_first",
            "engine_label": "Сгенерировано с помощью QWEN",
            "sections": [{"title": "Cached", "body": "Cached.", "citation_titles": []}],
        },
    )

    monkeypatch.setattr(
        "apps.reports.qwen_generation.build_analysis_packet",
        lambda *args, **kwargs: pytest.fail("cache hit should not rebuild packet"),
    )

    result = generate_birth_chart_qwen_analysis({**payload, "place_id": "sterlitamak-ru"})

    assert result["sections"][0]["title"] == "Cached"
    assert result["provider"] == "qwen"


@pytest.mark.django_db
def test_generate_birth_chart_qwen_analysis_uses_compact_overview_prompt(monkeypatch):
    from apps.reports.qwen_generation import generate_birth_chart_qwen_analysis

    captured = {}
    monkeypatch.setattr(
        "apps.reports.qwen_generation.build_analysis_packet",
        lambda *args, **kwargs: {
            "schema_version": "jyotish-analysis-packet-v1",
            "prompt_markdown": "x" * 100_000,
            "context": {
                "birth": {"date": "1998-04-30", "time": "13:45"},
                "chart": {"grahas": [{"body": "Sun", "rashi": "Aries"}]},
            },
        },
    )

    def runner(prompt):
        captured["prompt"] = prompt
        return json.dumps(
            {
                "language": "ru",
                "sections": [{"title": "Smoke", "body": "qwen compact ok", "citation_titles": []}],
            }
        )

    result = generate_birth_chart_qwen_analysis(
        {"birth_date": "1998-04-30"},
        qwen_runner=runner,
        refresh_evidence=False,
    )

    assert result["provider"] == "qwen"
    assert result["prompt_version"] == "qwen-overview-v1"
    assert captured["prompt"].count("OVERVIEW PACKET JSON") == 1
    assert "x" * 1000 not in captured["prompt"]
    assert len(captured["prompt"]) < 5000


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_qwen_analysis_api_returns_saved_draft(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_qwen_analysis",
        lambda data, citation_search=None, research_search=None, interpretation_provider=None, refresh_evidence=False: {
            "id": 9,
            "kind": "birth_chart_qwen",
            "provider": "qwen",
            "engine_label": "Сгенерировано с помощью QWEN",
            "review_status": "private_partial",
            "source_policy": "private_shastra_research_first",
            "sections": [{"title": "Главное", "body": "Qwen.", "citation_titles": []}],
        },
    )

    response = APIClient().post(
        "/api/reports/birth-chart/qwen-analysis",
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Стерлитамак",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "birth_chart_qwen"
    assert response.data["engine_label"] == "Сгенерировано с помощью QWEN"
