from datetime import date, time

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient

from apps.charts.models import BirthProfile, Place
from apps.reports.models import GeneratedAnalysisDraft, GeneratedAnalysisJob


def _place() -> Place:
    return Place.objects.create(
        name="Vrindavan",
        country_code="IN",
        latitude="27.565000",
        longitude="77.659000",
        timezone_name="Asia/Kolkata",
    )


def _profile(user, *, display_name: str, is_self_profile: bool) -> BirthProfile:
    return BirthProfile.objects.create(
        user=user,
        display_name=display_name,
        birth_date=date(2000, 1, 1),
        birth_time=time(15, 30),
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        place=_place(),
        timezone_name="Asia/Kolkata",
        is_self_profile=is_self_profile,
    )


@pytest.mark.django_db
@override_settings(CODEX_GENERATION_QUEUE_ENABLED=True)
def test_birth_codex_allows_first_free_self_profile_analysis(monkeypatch):
    user = get_user_model().objects.create_user(username="self-free", password="strong-pass-108")
    profile = _profile(user, display_name="My chart", is_self_profile=True)
    cache.clear()

    monkeypatch.setattr("apps.reports.views._profile_context", lambda profile, **kwargs: {"profile": {"id": profile.id}})

    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("queued free self-profile analysis must not run Codex inline"),
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "profile_id": profile.id,
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 202
    assert response.data["queued"] is True
    assert response.data["job"]["status"] == GeneratedAnalysisJob.Status.QUEUED
    job = GeneratedAnalysisJob.objects.get(user=user, kind="birth_chart_codex_cli")
    assert job.request_snapshot["profile_id"] == profile.id
    assert job.request_snapshot["billing_context"]["free_personal_analysis"] is True


@pytest.mark.django_db
def test_birth_codex_requires_saved_profile_id(monkeypatch):
    user = get_user_model().objects.create_user(username="no-profile-id", password="strong-pass-108")
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("Codex generation should not run without a saved profile"),
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"] == "profile_id_required"
    assert GeneratedAnalysisDraft.objects.count() == 0


@pytest.mark.django_db
def test_birth_codex_requires_payment_for_other_saved_profile(monkeypatch):
    user = get_user_model().objects.create_user(username="paid-other", password="strong-pass-108")
    profile = _profile(user, display_name="Other person", is_self_profile=False)
    monkeypatch.setattr("apps.reports.views._profile_context", lambda profile, **kwargs: {"profile": {"id": profile.id}})
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("Codex generation should not run for unpaid other profile"),
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "profile_id": profile.id,
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 402
    assert response.data["error"] == "payment_required"
    assert response.data["payment_required"] is True
    assert response.data["billing_scope"] == "other_profile_ai_analysis"


@pytest.mark.django_db
def test_birth_codex_reuses_existing_free_self_profile_analysis(monkeypatch):
    user = get_user_model().objects.create_user(username="self-used", password="strong-pass-108")
    profile = _profile(user, display_name="My chart", is_self_profile=True)
    existing = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        input_snapshot={"profile_id": profile.id, "birth_date": "2000-01-01"},
        output_json={"kind": "birth_chart_codex_cli", "sections": [{"title": "Saved", "body": "Saved."}]},
    )
    monkeypatch.setattr("apps.reports.views._profile_context", lambda profile, **kwargs: {"profile": {"id": profile.id}})
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("Existing free personal analysis should be reused"),
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "profile_id": profile.id,
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "force_regenerate": True,
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["id"] == existing.id
    assert response.data["billing_status"] == "free_personal_analysis_already_used"
    assert response.data["force_regenerate_ignored"] is True
