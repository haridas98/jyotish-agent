import pytest
from datetime import date, time
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from apps.charts.models import BirthProfile, BirthProfileRelationship, ChartCalculation, Place
from apps.reports.models import GeneratedAnalysisDraft


@pytest.mark.django_db
def test_analysis_history_lists_reports_with_data_slug_and_chat_count():
    user = get_user_model().objects.create_user(username="history-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot={
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Sterlitamak",
            "profile_id": 7,
        },
        output_json={
            "engine_label": "Codex CLI personal overview",
            "sections": [{"title": "Chart", "body": "Readable body."}],
        },
    )
    GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli_chat",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"analysis_id": report.id, "question": "Question?"},
        output_json={"answer": "Answer."},
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/reports/history", {"kind": "birth_chart_codex_cli", "profile_id": 7})

    assert response.status_code == 200
    assert response.data["items"][0]["id"] == report.id
    assert response.data["items"][0]["slug"] == f"birth-1998-04-30-1345-sterlitamak-codex-cli-{report.id}"
    assert response.data["items"][0]["chat_count"] == 1


@pytest.mark.django_db
def test_analysis_history_list_uses_compact_preview_fields():
    user = get_user_model().objects.create_user(username="history-preview-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot={"birth_date": "1998-04-30", "birth_time": "13:45", "place_name": "Sterlitamak"},
        packet_snapshot={"large": "packet" * 2000},
        output_json={
            "engine_label": "Codex CLI personal overview",
            "sections": [{"title": "Main", "body": "Readable preview." + ("x" * 2000)}],
        },
        prompt_markdown="prompt" * 2000,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    with CaptureQueriesContext(connection) as captured:
        response = client.get("/api/reports/history", {"kind": "birth_chart_codex_cli"})

    assert response.status_code == 200
    assert response.data["items"][0]["id"] == report.id
    assert response.data["items"][0]["engine_label"] == "Codex CLI personal overview"
    assert response.data["items"][0]["first_section_title"] == "Main"
    assert response.data["items"][0]["excerpt"].startswith("Readable preview.")
    history_sql = "\n".join(query["sql"].lower() for query in captured.captured_queries)
    assert "output_json" not in history_sql
    assert "packet_snapshot" not in history_sql
    assert "prompt_markdown" not in history_sql


@pytest.mark.django_db
def test_analysis_history_detail_resolves_slug_and_returns_chat_messages():
    user = get_user_model().objects.create_user(username="history-detail-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
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
        user=user,
        kind="birth_chart_codex_cli_chat",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"analysis_id": report.id, "question": "What about work?"},
        output_json={"answer": "Work answer."},
    )

    slug = f"birth-2000-01-01-1530-vrindavan-codex-cli-{report.id}"
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/reports/history/slug/{slug}")

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
    assert response.data["chat_truncated"] is False


@pytest.mark.django_db
def test_analysis_history_chat_uses_parent_analysis_relation():
    user = get_user_model().objects.create_user(username="history-parent-chat-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
        output_json={"sections": [{"title": "Chart", "body": "Body."}]},
    )
    chat = GeneratedAnalysisDraft.objects.create(
        user=user,
        parent_analysis=report,
        kind="birth_chart_codex_cli_chat",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"question": "Question stored without JSON analysis id"},
        output_json={"answer": "Answer from indexed parent relation."},
    )

    client = APIClient()
    client.force_authenticate(user=user)
    list_response = client.get("/api/reports/history", {"kind": "birth_chart_codex_cli"})
    detail_response = client.get(f"/api/reports/history/{report.id}")

    assert list_response.status_code == 200
    assert list_response.data["items"][0]["chat_count"] == 1
    assert detail_response.status_code == 200
    assert detail_response.data["chat_messages"] == [
        {
            "role": "user",
            "content": "Question stored without JSON analysis id",
            "analysis_message_id": chat.id,
            "created_at": chat.created_at.isoformat(),
        },
        {
            "role": "assistant",
            "content": "Answer from indexed parent relation.",
            "analysis_message_id": chat.id,
            "created_at": chat.created_at.isoformat(),
        },
    ]


@pytest.mark.django_db
def test_analysis_history_detail_limits_long_chat_history():
    user = get_user_model().objects.create_user(username="history-long-chat-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
        output_json={"sections": [{"title": "Chart", "body": "Body."}]},
    )
    for index in range(25):
        GeneratedAnalysisDraft.objects.create(
            user=user,
            kind="birth_chart_codex_cli_chat",
            review_status="private_final",
            source_policy="private_shastra_research_first",
            input_snapshot={"analysis_id": report.id, "question": f"Question {index}"},
            output_json={"answer": f"Answer {index}"},
        )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/reports/history/{report.id}")

    assert response.status_code == 200
    assert response.data["chat_record_total"] == 25
    assert response.data["chat_record_limit"] == 20
    assert response.data["chat_truncated"] is True
    assert len(response.data["chat_messages"]) == 40
    assert response.data["chat_messages"][0]["content"] == "Question 5"
    assert response.data["chat_messages"][-1]["content"] == "Answer 24"


@pytest.mark.django_db
def test_analysis_history_filters_compatibility_by_related_profile():
    user = get_user_model().objects.create_user(username="history-compat-owner", password="strong-pass-108")
    record = GeneratedAnalysisDraft.objects.create(
        user=user,
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

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/reports/history", {"kind": "compatibility_codex_cli", "profile_id": 11})

    assert response.status_code == 200
    assert [item["id"] for item in response.data["items"]] == [record.id]


@pytest.mark.django_db
def test_analysis_history_requires_authentication_even_when_private_app_auth_is_off(settings):
    settings.PRIVATE_APP_REQUIRE_AUTH = False
    GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Private", "body": "Must not be public."}]},
    )

    response = APIClient().get("/api/reports/history", {"kind": "birth_chart_codex_cli"})

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_analysis_history_is_scoped_to_authenticated_user():
    user = get_user_model().objects.create_user(username="owner-a", password="strong-pass-108")
    other = get_user_model().objects.create_user(username="owner-b", password="strong-pass-108")
    own_report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
        output_json={"sections": [{"title": "Own", "body": "Own body."}]},
    )
    other_report = GeneratedAnalysisDraft.objects.create(
        user=other,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"birth_date": "2001-01-01", "birth_time": "15:30", "place_name": "Mayapur"},
        output_json={"sections": [{"title": "Other", "body": "Other body."}]},
    )
    client = APIClient()
    client.force_authenticate(user=user)

    list_response = client.get("/api/reports/history", {"kind": "birth_chart_codex_cli"})
    detail_response = client.get(f"/api/reports/history/{other_report.id}")

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.data["items"]] == [own_report.id]
    assert detail_response.status_code == 404


@pytest.mark.django_db
def test_compatibility_history_and_chat_are_scoped_to_owner():
    owner = get_user_model().objects.create_user(username="compat-owner-a", password="strong-pass-108")
    viewer = get_user_model().objects.create_user(username="compat-owner-b", password="strong-pass-108")
    own_report = GeneratedAnalysisDraft.objects.create(
        user=owner,
        kind="compatibility_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={
            "person_a": {"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
            "person_b": {"birth_date": "2001-02-03", "birth_time": "09:10", "place_name": "Mayapur"},
        },
        output_json={"sections": [{"title": "Owner pair", "body": "Owner only."}]},
    )
    other_report = GeneratedAnalysisDraft.objects.create(
        user=viewer,
        kind="compatibility_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={
            "person_a": {"birth_date": "1990-01-01", "birth_time": "10:00", "place_name": "Moscow"},
            "person_b": {"birth_date": "1991-01-01", "birth_time": "11:00", "place_name": "Kazan"},
        },
        output_json={"sections": [{"title": "Viewer pair", "body": "Viewer body."}]},
    )
    own_chat = GeneratedAnalysisDraft.objects.create(
        user=owner,
        kind="compatibility_codex_cli_chat",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"analysis_id": own_report.id, "question": "Owner question"},
        output_json={"answer": "Owner answer"},
    )
    GeneratedAnalysisDraft.objects.create(
        user=viewer,
        kind="compatibility_codex_cli_chat",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"analysis_id": own_report.id, "question": "Wrong user question"},
        output_json={"answer": "Wrong user answer"},
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    list_response = client.get("/api/reports/history", {"kind": "compatibility_codex_cli"})
    detail_response = client.get(f"/api/reports/history/{own_report.id}")
    other_detail_response = client.get(f"/api/reports/history/{other_report.id}")
    other_slug = f"compatibility-1990-01-01-1000-moscow-1991-01-01-1100-kazan-codex-cli-{other_report.id}"
    other_slug_response = client.get(f"/api/reports/history/slug/{other_slug}")

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.data["items"]] == [own_report.id]
    assert list_response.data["items"][0]["chat_count"] == 1
    assert detail_response.status_code == 200
    assert detail_response.data["chat_messages"] == [
        {
            "role": "user",
            "content": "Owner question",
            "analysis_message_id": own_chat.id,
            "created_at": own_chat.created_at.isoformat(),
        },
        {
            "role": "assistant",
            "content": "Owner answer",
            "analysis_message_id": own_chat.id,
            "created_at": own_chat.created_at.isoformat(),
        },
    ]
    assert other_detail_response.status_code == 404
    assert other_slug_response.status_code == 404


@pytest.mark.django_db
def test_universal_analysis_chat_uses_codex_answer(monkeypatch):
    user = get_user_model().objects.create_user(username="chat-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Chart", "body": "Saved body."}]},
    )

    monkeypatch.setattr(
        "apps.reports.views.ask_birth_chart_codex_cli_analysis",
        lambda **kwargs: {"kind": "birth_chart_codex_cli_chat", "answer": "Codex answer"},
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/analysis/chat",
        {"analysis_id": report.id, "provider": "codex", "question": "What now?", "history": []},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "birth_chart_codex_cli_chat"
    assert response.data["answer"] == "Codex answer"


@pytest.mark.django_db
def test_universal_analysis_chat_rejects_duplicate_running_answer(monkeypatch):
    user = get_user_model().objects.create_user(username="chat-lock-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Chart", "body": "Saved body."}]},
    )
    cache.clear()
    monkeypatch.setattr("apps.reports.views.cache.add", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        "apps.reports.views.ask_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("universal chat must not run while lock is active"),
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/analysis/chat",
        {"analysis_id": report.id, "provider": "codex", "question": "What now?", "history": []},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["error"] == "analysis_chat_in_progress"


@pytest.mark.django_db
def test_universal_analysis_chat_rejects_other_users_report(monkeypatch):
    owner = get_user_model().objects.create_user(username="chat-real-owner", password="strong-pass-108")
    viewer = get_user_model().objects.create_user(username="chat-viewer", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=owner,
        kind="birth_chart_codex_cli",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Private", "body": "Saved body."}]},
    )
    monkeypatch.setattr(
        "apps.reports.views.ask_birth_chart_codex_cli_analysis",
        lambda **kwargs: {"kind": "birth_chart_codex_cli_chat", "answer": "Should not run"},
    )
    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.post(
        "/api/reports/analysis/chat",
        {"analysis_id": report.id, "provider": "codex", "question": "What now?", "history": []},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_current_day_overview_is_saved(monkeypatch):
    user = get_user_model().objects.create_user(username="today-save-owner", password="strong-pass-108")
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

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
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
def test_current_day_overview_reuses_cached_transit_report(monkeypatch):
    cache.clear()
    user = get_user_model().objects.create_user(username="today-cache-owner", password="strong-pass-108")
    calls = {"count": 0}

    def fake_transit_report(data):
        calls["count"] += 1
        return {
            "as_of": {"date": data["as_of_date"], "time": data["as_of_time"], "timezone": "Asia/Kolkata"},
            "transits": [{"body": "Chandra", "rashi": "Mesha", "house_from_lagna": 1, "house_from_moon": 5}],
        }

    monkeypatch.setattr("apps.reports.views.build_transit_report", fake_transit_report)
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {
        "birth_date": "2000-01-01",
        "birth_time": "15:30",
        "place_name": "Vrindavan",
        "as_of_date": "2026-06-09",
        "as_of_time": "12:00",
    }

    first = client.post("/api/reports/birth-chart/current-day", payload, format="json")
    second = client.post("/api/reports/birth-chart/current-day", payload, format="json")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first["X-Jyotish-Transit-Cache"] == "miss"
    assert second["X-Jyotish-Transit-Cache"] == "hit"
    assert calls["count"] == 1
    assert GeneratedAnalysisDraft.objects.filter(kind="current_day_transit_overview", user=user).count() == 2


@pytest.mark.django_db
def test_current_day_overview_requires_authentication():
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

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_current_day_overview_is_saved_for_authenticated_user(monkeypatch):
    user = get_user_model().objects.create_user(username="today-owner", password="strong-pass-108")
    monkeypatch.setattr(
        "apps.reports.views.build_transit_report",
        lambda data: {
            "as_of": {"date": data["as_of_date"], "time": data["as_of_time"], "timezone": "Asia/Kolkata"},
            "transits": [],
        },
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
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
    assert GeneratedAnalysisDraft.objects.get(id=response.data["id"]).user == user


@pytest.mark.django_db
def test_current_day_overview_includes_related_profile_context(monkeypatch):
    user = get_user_model().objects.create_user(username="today-related", password="strong-pass-108")
    place = Place.objects.create(
        external_id="test:sterlitamak",
        name="Sterlitamak",
        country_code="RU",
        latitude=53.6304,
        longitude=55.9308,
        timezone_name="Asia/Yekaterinburg",
        metadata={"label": "Sterlitamak, RU"},
    )
    mother_profile = BirthProfile.objects.create(
        user=user,
        display_name="Mother",
        birth_date=date(1970, 1, 1),
        birth_time=time(8, 0),
        place=place,
        timezone_name="Asia/Yekaterinburg",
    )
    ChartCalculation.objects.create(
        profile=mother_profile,
        calculation_version="test",
        status=ChartCalculation.Status.COMPLETE,
        result={"birth": {"date": "1970-01-01"}, "grahas": [{"body": "Chandra", "rashi": "Karka"}]},
    )
    GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"profile_id": mother_profile.id},
        output_json={"sections": [{"title": "Mother", "body": "Existing related review."}]},
    )
    monkeypatch.setattr(
        "apps.reports.views.build_transit_report",
        lambda data: {
            "as_of": {"date": data["as_of_date"], "time": data["as_of_time"], "timezone": "Asia/Yekaterinburg"},
            "transits": [],
        },
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/current-day",
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Sterlitamak",
            "as_of_date": "2026-06-12",
            "as_of_time": "12:00",
            "related_profile_ids": [mother_profile.id],
        },
        format="json",
    )

    assert response.status_code == 200
    record = GeneratedAnalysisDraft.objects.get(id=response.data["id"])
    related = record.input_snapshot["related_profile_context"]
    assert related[0]["profile"]["display_name"] == "Mother"
    assert related[0]["chart"]["grahas"][0]["body"] == "Chandra"
    assert related[0]["latest_reviews"][0]["excerpt"] == "Existing related review."


@pytest.mark.django_db
def test_universal_analysis_chat_supports_current_day_overview(monkeypatch):
    user = get_user_model().objects.create_user(username="today-chat", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="current_day_transit_overview",
        review_status="calculation_draft",
        source_policy="calculation_first",
        provider="internal_transit",
        model="workflow-v1",
        input_snapshot={
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Sterlitamak",
            "as_of_date": "2026-06-12",
            "as_of_time": "12:00",
        },
        packet_snapshot={"transit_report": {"transits": []}},
        output_json={
            "sections": [
                {
                    "title": "Фон дня",
                    "body": "Сегодня важно смотреть транзиты вместе с натальной картой.",
                }
            ]
        },
    )

    monkeypatch.setattr(
        "apps.reports.codex_cli_generation.configured_analysis_runner",
        lambda prompt: {"answer": "Ответ по текущему дню.", "evidence_references": [], "source_traces": []},
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/reports/analysis/chat",
        {"analysis_id": report.id, "provider": "codex", "question": "Что важно сегодня?", "history": []},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "current_day_transit_overview_chat"
    assert response.data["answer"] == "Ответ по текущему дню."
    detail_response = client.get(f"/api/reports/history/{report.id}")
    assert detail_response.status_code == 200
    assert detail_response.data["chat_messages"] == [
        {
            "role": "user",
            "content": "Что важно сегодня?",
            "analysis_message_id": response.data["id"],
            "created_at": GeneratedAnalysisDraft.objects.get(id=response.data["id"]).created_at.isoformat(),
        },
        {
            "role": "assistant",
            "content": "Ответ по текущему дню.",
            "analysis_message_id": response.data["id"],
            "created_at": GeneratedAnalysisDraft.objects.get(id=response.data["id"]).created_at.isoformat(),
        },
    ]


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
    base_profile = BirthProfile.objects.create(
        user=user,
        display_name="Me",
        birth_date=date(2000, 1, 1),
        birth_time=time(15, 30),
        place=place,
        timezone_name="Asia/Kolkata",
        is_self_profile=True,
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
        kind="birth_chart_codex_cli",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"profile_id": profile.id},
        output_json={"sections": [{"title": "Mother", "body": "Existing review."}]},
    )
    captured = {}

    def fake_generate(data, **kwargs):
        captured["data"] = data
        return {
            "id": 77,
            "kind": "birth_chart_codex_cli",
            "provider": "codex_cli",
            "review_status": "private_partial",
            "source_policy": "private_shastra_research_first",
            "sections": [],
        }

    monkeypatch.setattr("apps.reports.views.generate_birth_chart_codex_cli_analysis", fake_generate)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
            {
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
                "profile_id": base_profile.id,
                "related_profile_ids": [profile.id],
            },
            format="json",
        )

    assert response.status_code == 200
    related = captured["data"]["related_profile_context"]
    assert related[0]["profile"]["display_name"] == "Mother"
    assert related[0]["chart"]["grahas"][0]["body"] == "Chandra"
    assert related[0]["latest_reviews"][0]["excerpt"] == "Existing review."


@pytest.mark.django_db
def test_birth_analysis_request_includes_accepted_relationship_context(monkeypatch):
    user = get_user_model().objects.create_user(username="tester-rel", password="strong-pass-108")
    place = Place.objects.create(
        external_id="test:mayapur",
        name="Mayapur",
        country_code="IN",
        latitude=23.4241,
        longitude=88.3883,
        timezone_name="Asia/Kolkata",
        metadata={"label": "Mayapur, IN"},
    )
    base_profile = BirthProfile.objects.create(
        user=user,
        display_name="Me",
        birth_date=date(1990, 1, 1),
        birth_time=time(8, 0),
        place=place,
        timezone_name="Asia/Kolkata",
        is_self_profile=True,
    )
    father_profile = BirthProfile.objects.create(
        user=user,
        display_name="Father",
        birth_date=date(1960, 1, 1),
        birth_time=time(6, 0),
        place=place,
        timezone_name="Asia/Kolkata",
    )
    ChartCalculation.objects.create(
        profile=father_profile,
        calculation_version="test",
        status=ChartCalculation.Status.COMPLETE,
        result={"birth": {"date": "1960-01-01"}, "grahas": [{"body": "Surya", "rashi": "Mesha"}]},
    )
    BirthProfileRelationship.objects.create(
        user=user,
        profile=base_profile,
        related_profile=father_profile,
        role=BirthProfileRelationship.Role.FATHER,
        link_status=BirthProfileRelationship.LinkStatus.ACCEPTED,
    )
    captured = {}

    def fake_generate(data, **kwargs):
        captured["data"] = data
        return {
            "id": 78,
            "kind": "birth_chart_codex_cli",
            "provider": "codex_cli",
            "review_status": "private_partial",
            "source_policy": "private_shastra_research_first",
            "sections": [],
        }

    monkeypatch.setattr("apps.reports.views.generate_birth_chart_codex_cli_analysis", fake_generate)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "birth_date": "1990-01-01",
            "birth_time": "08:00",
            "place_name": "Mayapur",
            "profile_id": base_profile.id,
        },
        format="json",
    )

    assert response.status_code == 200
    related = captured["data"]["related_profile_context"]
    assert related[0]["profile"]["display_name"] == "Father"
    assert related[0]["relationship"]["role"] == "father"
    assert related[0]["relationship"]["link_status"] == "accepted"
    assert related[0]["chart"]["grahas"][0]["body"] == "Surya"


@pytest.mark.django_db
def test_birth_analysis_related_registered_profile_reviews_are_viewer_scoped(monkeypatch):
    user = get_user_model().objects.create_user(username="viewer-rel", password="strong-pass-108")
    other_user = get_user_model().objects.create_user(username="other-rel", password="strong-pass-108")
    place = Place.objects.create(
        external_id="test:privacy-mayapur",
        name="Mayapur",
        country_code="IN",
        latitude=23.4241,
        longitude=88.3883,
        timezone_name="Asia/Kolkata",
        metadata={"label": "Mayapur, IN"},
    )
    base_profile = BirthProfile.objects.create(
        user=user,
        display_name="Me",
        birth_date=date(1990, 1, 1),
        birth_time=time(8, 0),
        place=place,
        timezone_name="Asia/Kolkata",
        is_self_profile=True,
    )
    related_profile = BirthProfile.objects.create(
        user=other_user,
        display_name="Registered father",
        birth_date=date(1960, 1, 1),
        birth_time=time(6, 0),
        place=place,
        timezone_name="Asia/Kolkata",
    )
    ChartCalculation.objects.create(
        profile=related_profile,
        calculation_version="test",
        status=ChartCalculation.Status.COMPLETE,
        result={"birth": {"date": "1960-01-01"}, "grahas": [{"body": "Surya", "rashi": "Mesha"}]},
    )
    BirthProfileRelationship.objects.create(
        user=user,
        profile=base_profile,
        related_profile=related_profile,
        role=BirthProfileRelationship.Role.FATHER,
        link_status=BirthProfileRelationship.LinkStatus.ACCEPTED,
        requested_user=other_user,
    )
    GeneratedAnalysisDraft.objects.create(
        user=other_user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"profile_id": related_profile.id},
        output_json={"sections": [{"title": "Private", "body": "Other user's private review."}]},
    )
    GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_partial",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        input_snapshot={"profile_id": related_profile.id},
        output_json={"sections": [{"title": "Mine", "body": "My saved context for this linked chart."}]},
    )
    captured = {}

    def fake_generate(data, **kwargs):
        captured["data"] = data
        return {
            "id": 79,
            "kind": "birth_chart_codex_cli",
            "provider": "codex_cli",
            "review_status": "private_partial",
            "source_policy": "private_shastra_research_first",
            "sections": [],
        }

    monkeypatch.setattr("apps.reports.views.generate_birth_chart_codex_cli_analysis", fake_generate)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "birth_date": "1990-01-01",
            "birth_time": "08:00",
            "place_name": "Mayapur",
            "profile_id": base_profile.id,
        },
        format="json",
    )

    assert response.status_code == 200
    reviews = captured["data"]["related_profile_context"][0]["latest_reviews"]
    assert [review["excerpt"] for review in reviews] == ["My saved context for this linked chart."]
