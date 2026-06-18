import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient

from apps.charts.models import BirthProfile, ChartCalculation, ChartRelationship, Place


@pytest.fixture(autouse=True)
def clear_rate_limit_cache():
    cache.clear()


@pytest.fixture
def user():
    return get_user_model().objects.create_user(username="ai-gateway-user", password="strong-pass-108")


@pytest.fixture
def other_user():
    return get_user_model().objects.create_user(username="ai-gateway-other", password="strong-pass-108")


@pytest.fixture
def client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def place():
    return Place.objects.create(
        external_id="ai-gateway-place",
        name="Mayapur",
        country_code="IN",
        latitude="23.424100",
        longitude="88.388600",
        timezone_name="Asia/Kolkata",
    )


def make_profile(owner, place, name="Gateway chart"):
    return BirthProfile.objects.create(
        user=owner,
        display_name=name,
        birth_date="1990-05-14",
        birth_time="07:15",
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        gender=BirthProfile.Gender.UNKNOWN,
        place=place,
        timezone_name=place.timezone_name,
    )


def attach_complete_calculation(profile):
    return ChartCalculation.objects.create(
        profile=profile,
        calculation_version="gateway-test",
        status=ChartCalculation.Status.COMPLETE,
        result={
            "houses": [{"house": 1, "sign": "Taurus"}],
            "grahas": [{"body": "Surya"}, {"body": "Chandra"}],
            "vargas": {"D1": {}, "D9": {}},
            "dashas": {"vimshottari": []},
        },
    )


@pytest.mark.django_db
def test_ai_report_gateway_is_unavailable_when_feature_flag_is_off(client, user, place):
    profile = make_profile(user, place)

    response = client.post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_requires_authentication(user, place):
    profile = make_profile(user, place)

    response = APIClient().post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code in {401, 403}


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_rejects_client_prompt_and_evidence(client, user, place):
    profile = make_profile(user, place)

    for forbidden_field in ["prompt", "evidence", "eligibleItems", "citations", "rules", "passages", "system"]:
        response = client.post(
            "/api/ai/report-dry-run",
            {
                "report_type_id": "personal_overview",
                "chart_id": profile.id,
                "language": "ru",
                "audience": "novice",
                forbidden_field: "client supplied",
            },
            format="json",
        )
        assert response.status_code == 400
        assert forbidden_field in response.data["error"]


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_rejects_foreign_chart(client, other_user, place):
    foreign_profile = make_profile(other_user, place)

    response = client.post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": foreign_profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_rejects_foreign_relationship(client, user, other_user, place):
    profile = make_profile(user, place, "Own")
    other_a = make_profile(other_user, place, "Other A")
    other_b = make_profile(other_user, place, "Other B")
    relationship = ChartRelationship.objects.create(
        owner_user=other_user,
        chart_a=other_a,
        chart_b=other_b,
        relationship_type_id="spouses",
        role_a_id="spouse",
        role_b_id="spouse",
        pair_key=f"{min(other_a.id, other_b.id)}:{max(other_a.id, other_b.id)}",
    )

    response = client.post(
        "/api/ai/report-dry-run",
        {
            "report_type_id": "personal_overview",
            "chart_id": profile.id,
            "relationship_id": relationship.id,
            "language": "ru",
            "audience": "novice",
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_returns_validated_mock_response(client, user, place):
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["response"]["provider"] == "mock"
    assert response.data["response"]["schema_version"] == 1
    assert response.data["response"]["theses"]
    assert response.data["metadata"]["provider"] == "mock"
    assert "request" not in response.data
    assert "raw_provider_response" not in response.data
    assert all(thesis["citations"] for thesis in response.data["response"]["theses"])


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_does_not_send_excluded_items_to_provider(monkeypatch, client, user, place):
    from apps.reports import ai_gateway

    captured = {}

    class CapturingProvider:
        provider_id = "mock"

        def generate(self, request):
            captured["request"] = request
            return ai_gateway.MockAiProvider().generate(request)

    monkeypatch.setattr(ai_gateway, "provider_for_settings", lambda: CapturingProvider())
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code == 200
    assert captured["request"]["excluded_summary"]["total"] >= 1
    assert "excluded_items" not in captured["request"]
    assert all("house.5" not in item["evidence_item_id"] for item in captured["request"]["items"])


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_rejects_invalid_thesis_reference(monkeypatch, client, user, place):
    from apps.reports import ai_gateway

    class InvalidProvider:
        provider_id = "mock"

        def generate(self, request):
            response = ai_gateway.MockAiProvider().generate(request)
            response["theses"][0]["evidence_item_ids"] = ["unknown.item"]
            return response

    monkeypatch.setattr(ai_gateway, "provider_for_settings", lambda: InvalidProvider())
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code == 502
    assert "unknown evidence item" in response.data["error"]


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_rejects_invalid_citation_reference(monkeypatch, client, user, place):
    from apps.reports import ai_gateway

    class InvalidCitationProvider:
        provider_id = "mock"

        def generate(self, request):
            response = ai_gateway.MockAiProvider().generate(request)
            response["theses"][0]["citations"][0]["passage_id"] = "missing.passage"
            return response

    monkeypatch.setattr(ai_gateway, "provider_for_settings", lambda: InvalidCitationProvider())
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code == 502
    assert "missing citation chain" in response.data["error"]


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_handles_provider_timeout(monkeypatch, client, user, place):
    from apps.reports import ai_gateway

    class TimeoutProvider:
        provider_id = "mock"

        def generate(self, request):
            raise ai_gateway.AiProviderTimeout("provider timeout")

    monkeypatch.setattr(ai_gateway, "provider_for_settings", lambda: TimeoutProvider())
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code == 504


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=True, AI_PROVIDER="mock")
def test_ai_report_gateway_rejects_malformed_provider_response(monkeypatch, client, user, place):
    from apps.reports import ai_gateway

    class MalformedProvider:
        provider_id = "mock"

        def generate(self, request):
            return {"schema_version": 1, "provider": "mock"}

    monkeypatch.setattr(ai_gateway, "provider_for_settings", lambda: MalformedProvider())
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post(
        "/api/ai/report-dry-run",
        {"report_type_id": "personal_overview", "chart_id": profile.id, "language": "ru", "audience": "novice"},
        format="json",
    )

    assert response.status_code == 502
    assert "theses" in response.data["error"]
