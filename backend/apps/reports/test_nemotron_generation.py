import json

import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_generate_birth_chart_nemotron_analysis_saves_openrouter_draft(monkeypatch):
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
                        "title": "Главное",
                        "body": "Nemotron рабочий обзор.",
                        "citation_titles": [],
                    }
                ],
            }
        ),
        refresh_evidence=False,
    )

    assert result["kind"] == "birth_chart_nemotron"
    assert result["provider"] == "openrouter_nemotron"
    assert result["engine_label"] == "Сгенерировано с помощью Nemotron"
    record = GeneratedAnalysisDraft.objects.get()
    assert record.kind == "birth_chart_nemotron"
    assert record.provider == "openrouter_nemotron"


@pytest.mark.django_db
def test_generate_birth_chart_nemotron_analysis_is_single_pass_overview(monkeypatch):
    from apps.reports.nemotron_generation import generate_birth_chart_nemotron_analysis

    monkeypatch.setattr(
        "apps.reports.nemotron_generation.build_analysis_packet",
        lambda *args, **kwargs: {
            "schema_version": "jyotish-analysis-packet-v1",
            "context": {"chart": {"grahas": []}},
        },
    )
    calls = []

    def runner(prompt):
        calls.append(prompt)
        return json.dumps({"language": "ru", "sections": [{"title": "Обзор", "body": "Коротко.", "citation_titles": []}]})

    generate_birth_chart_nemotron_analysis(
        {"birth_date": "1998-04-30"},
        nemotron_runner=runner,
        refresh_evidence=False,
    )

    assert len(calls) == 1


def test_extract_nemotron_text_reads_openai_compatible_choice():
    from apps.reports.nemotron_generation import _extract_nemotron_text

    assert (
        _extract_nemotron_text({"choices": [{"message": {"content": "{\"sections\": []}"}}]})
        == "{\"sections\": []}"
    )


def test_normalize_nemotron_output_converts_section_blocks():
    from apps.reports.nemotron_generation import _normalize_nemotron_output

    output = _normalize_nemotron_output(
        """
Section 1: Главное
Body: Карта сильная, но требует проверки.
Key points: ["Солнце в 10 доме", "Луна в 12 доме"]
Practical steps: ["Проверить в JHora"]
Review notes: ["Не финальный вывод"]

Section 2: Практика
Body: Держать садхану и служение.
"""
    )

    assert [section["title"] for section in output["sections"]] == ["Главное", "Практика"]
    assert output["sections"][0]["key_points"] == ["Солнце в 10 доме", "Луна в 12 доме"]
    assert output["sections"][0]["practical_steps"] == ["Проверить в JHora"]
    assert output["sections"][0]["review_notes"] == ["Не финальный вывод"]


def test_nemotron_client_wraps_timeout(monkeypatch):
    from apps.reports.draft_generation import DraftGenerationUnavailable
    from apps.reports.nemotron_generation import openrouter_nemotron_chat_client

    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr("apps.reports.nemotron_generation.request.urlopen", raise_timeout)

    with pytest.raises(DraftGenerationUnavailable, match="Nemotron API timed out"):
        openrouter_nemotron_chat_client()("prompt")


@pytest.mark.django_db
def test_generate_birth_chart_nemotron_analysis_reuses_matching_cached_record(monkeypatch):
    from apps.reports.models import GeneratedAnalysisDraft
    from apps.reports.nemotron_generation import generate_birth_chart_nemotron_analysis

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
        kind="birth_chart_nemotron",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="openrouter_nemotron",
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        input_snapshot=payload,
        output_json={
            "kind": "birth_chart_nemotron",
            "provider": "openrouter_nemotron",
            "prompt_version": "nemotron-overview-v2",
            "review_status": "private_final",
            "source_policy": "private_shastra_research_first",
            "engine_label": "Сгенерировано с помощью Nemotron",
            "sections": [{"title": "Cached", "body": "Cached.", "citation_titles": []}],
        },
    )

    monkeypatch.setattr(
        "apps.reports.nemotron_generation.build_analysis_packet",
        lambda *args, **kwargs: pytest.fail("cache hit should not rebuild packet"),
    )

    result = generate_birth_chart_nemotron_analysis({**payload, "place_id": "sterlitamak-ru"})

    assert result["sections"][0]["title"] == "Cached"
    assert result["provider"] == "openrouter_nemotron"


@pytest.mark.django_db
def test_generate_birth_chart_nemotron_analysis_ignores_stale_cached_record(monkeypatch):
    from apps.reports.models import GeneratedAnalysisDraft
    from apps.reports.nemotron_generation import generate_birth_chart_nemotron_analysis

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
    stale = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_nemotron",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="openrouter_nemotron",
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        input_snapshot=payload,
        output_json={
            "kind": "birth_chart_nemotron",
            "provider": "openrouter_nemotron",
            "prompt_version": "old",
            "sections": [{"title": "Черновик", "body": "old raw", "citation_titles": []}],
        },
    )
    monkeypatch.setattr(
        "apps.reports.nemotron_generation.build_analysis_packet",
        lambda *args, **kwargs: {
            "schema_version": "jyotish-analysis-packet-v1",
            "context": {"chart": {"grahas": []}},
        },
    )
    monkeypatch.setattr(
        "apps.reports.nemotron_generation.openrouter_nemotron_chat_client",
        lambda: lambda prompt: json.dumps(
            {"language": "ru", "sections": [{"title": "Fresh", "body": "new", "citation_titles": []}]}
        ),
    )

    result = generate_birth_chart_nemotron_analysis(
        payload,
        refresh_evidence=False,
    )

    assert result["id"] != stale.id
    assert result["sections"][0]["title"] == "Fresh"


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_nemotron_analysis_api_returns_saved_draft(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_nemotron_analysis",
        lambda data, citation_search=None, research_search=None, interpretation_provider=None, refresh_evidence=False: {
            "id": 10,
            "kind": "birth_chart_nemotron",
            "provider": "openrouter_nemotron",
            "engine_label": "Сгенерировано с помощью Nemotron",
            "review_status": "private_partial",
            "source_policy": "private_shastra_research_first",
            "sections": [{"title": "Главное", "body": "Nemotron.", "citation_titles": []}],
        },
    )

    response = APIClient().post(
        "/api/reports/birth-chart/nemotron-analysis",
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Стерлитамак",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "birth_chart_nemotron"
    assert response.data["engine_label"] == "Сгенерировано с помощью Nemotron"
