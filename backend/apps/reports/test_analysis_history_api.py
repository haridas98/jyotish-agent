import pytest
from datetime import date, time
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.charts.models import BirthProfile, ChartCalculation, Place
from apps.reports.models import GeneratedAnalysisDraft


@pytest.mark.django_db
def test_analysis_history_lists_reports_with_data_slug_and_chat_count():
    report = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_qwen",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="qwen",
        model="qwen-test",
        input_snapshot={
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Sterlitamak",
            "profile_id": 7,
        },
        output_json={
            "engine_label": "QWEN personal overview",
            "sections": [{"title": "Chart", "body": "Readable body."}],
        },
    )
    GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli_chat",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"analysis_id": report.id, "question": "Question?"},
        output_json={"answer": "Answer."},
    )

    response = APIClient().get("/api/reports/history", {"kind": "birth_chart_qwen", "profile_id": 7})

    assert response.status_code == 200
    assert response.data["items"][0]["id"] == report.id
    assert response.data["items"][0]["slug"] == f"birth-1998-04-30-1345-sterlitamak-qwen-{report.id}"
    assert response.data["items"][0]["chat_count"] == 1


@pytest.mark.django_db
def test_analysis_history_detail_resolves_slug_and_returns_chat_messages():
    report = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot={"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
        packet_snapshot={"schema_version": "saved-packet-v1", "context": {"lagna": "Mesha"}},
        output_json={"sections": [{"title": "Career", "body": "Body."}]},
    )
    chat = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli_chat",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"analysis_id": report.id, "question": "What about work?"},
        output_json={"answer": "Work answer."},
    )

    slug = f"birth-2000-01-01-1530-vrindavan-codex-cli-{report.id}"
    response = APIClient().get(f"/api/reports/history/slug/{slug}")

    assert response.status_code == 200
    assert response.data["analysis"]["id"] == report.id
    assert response.data["analysis"]["output_json"]["sections"][0]["title"] == "Career"
    assert response.data["analysis"]["packet_snapshot"]["schema_version"] == "saved-packet-v1"
    assert response.data["chat_messages"] == [
        {
            "role": "user",
            "content": "What about work?",
            "analysis_message_id": chat.id,
            "created_at": chat.created_at.isoformat(),
        },
        {
            "role": "assistant",
            "content": "Work answer.",
            "analysis_message_id": chat.id,
            "created_at": chat.created_at.isoformat(),
        },
    ]


@pytest.mark.django_db
def test_analysis_history_filters_compatibility_by_related_profile():
    record = GeneratedAnalysisDraft.objects.create(
        kind="compatibility_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={
            "person_a": {"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan", "profile_id": 10},
            "person_b": {"birth_date": "2001-02-03", "birth_time": "09:10", "place_name": "Mayapur", "profile_id": 11},
        },
        output_json={"sections": [{"title": "Compatibility", "body": "Body."}]},
    )

    response = APIClient().get("/api/reports/history", {"kind": "compatibility_codex_cli", "profile_id": 11})

    assert response.status_code == 200
    assert [item["id"] for item in response.data["items"]] == [record.id]


@pytest.mark.django_db
def test_universal_analysis_chat_saves_qwen_answer(monkeypatch):
    report = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_qwen",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="qwen",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Chart", "body": "Saved body."}]},
    )

    monkeypatch.setattr(
        "apps.reports.views.qwen_chat_completions_client",
        lambda: (lambda prompt: '{"answer":"Qwen answer","evidence_references":[],"source_traces":[]}'),
    )

    response = APIClient().post(
        "/api/reports/analysis/chat",
        {"analysis_id": report.id, "provider": "qwen", "question": "What now?", "history": []},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "birth_chart_qwen_chat"
    assert response.data["answer"] == "Qwen answer"
    assert GeneratedAnalysisDraft.objects.filter(kind="birth_chart_qwen_chat", input_snapshot__analysis_id=report.id).exists()


@pytest.mark.django_db
def test_current_day_overview_is_saved(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.build_transit_report",
        lambda data: {
            "as_of": {"date": data["as_of_date"], "time": data["as_of_time"], "timezone": "Asia/Kolkata"},
            "transits": [
                {"body": "Chandra", "rashi": "Mesha", "house_from_lagna": 1, "house_from_moon": 5},
                {"body": "Shani", "rashi": "Kumbha", "house_from_lagna": 11, "house_from_moon": 3},
            ],
        },
    )

    response = APIClient().post(
        "/api/reports/birth-chart/current-day",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "as_of_date": "2026-06-09",
            "as_of_time": "12:00",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "current_day_transit_overview"
    assert response.data["id"] == GeneratedAnalysisDraft.objects.get(kind="current_day_transit_overview").id


@pytest.mark.django_db
def test_birth_analysis_request_includes_related_profile_context(monkeypatch):
    user = get_user_model().objects.create_user(username="tester", password="strong-pass-108")
    place = Place.objects.create(
        external_id="test:vrindavan",
        name="Vrindavan",
        country_code="IN",
        latitude=27.5650,
        longitude=77.6593,
        timezone_name="Asia/Kolkata",
        metadata={"label": "Vrindavan, IN"},
    )
    profile = BirthProfile.objects.create(
        user=user,
        display_name="Mother",
        birth_date=date(1970, 1, 1),
        birth_time=time(8, 0),
        place=place,
        timezone_name="Asia/Kolkata",
    )
    ChartCalculation.objects.create(
        profile=profile,
        calculation_version="test",
        status=ChartCalculation.Status.COMPLETE,
        result={"birth": {"date": "1970-01-01"}, "grahas": [{"body": "Chandra", "rashi": "Karka"}]},
    )
    GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_qwen",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="qwen",
        input_snapshot={"profile_id": profile.id},
        output_json={"sections": [{"title": "Mother", "body": "Existing review."}]},
    )
    captured = {}

    def fake_generate(data, **kwargs):
        captured["data"] = data
        return {
            "id": 77,
            "kind": "birth_chart_qwen",
            "provider": "qwen",
            "review_status": "private_partial",
            "source_policy": "private_shastra_research_first",
            "sections": [],
        }

    monkeypatch.setattr("apps.reports.views.generate_birth_chart_qwen_analysis", fake_generate)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/qwen-analysis",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "related_profile_ids": [profile.id],
        },
        format="json",
    )

    assert response.status_code == 200
    related = captured["data"]["related_profile_context"]
    assert related[0]["profile"]["display_name"] == "Mother"
    assert related[0]["chart"]["grahas"][0]["body"] == "Chandra"
    assert related[0]["latest_reviews"][0]["excerpt"] == "Existing review."
