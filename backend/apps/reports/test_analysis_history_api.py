import pytest
from rest_framework.test import APIClient

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
