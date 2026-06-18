import json

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
    return get_user_model().objects.create_user(username="ai-staging-user", password="strong-pass-108", email="user@example.test")


@pytest.fixture
def client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def place():
    return Place.objects.create(
        external_id="staging-place",
        name="Private Birth City",
        country_code="IN",
        latitude="23.424100",
        longitude="88.388600",
        timezone_name="Asia/Kolkata",
    )


def make_profile(owner, place, name="Private profile name"):
    return BirthProfile.objects.create(
        user=owner,
        display_name=name,
        birth_date="1990-05-14",
        birth_time="07:15",
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        gender=BirthProfile.Gender.UNKNOWN,
        place=place,
        timezone_name=place.timezone_name,
        notes="private user note",
    )


def attach_complete_calculation(profile):
    return ChartCalculation.objects.create(
        profile=profile,
        calculation_version="staging-test",
        status=ChartCalculation.Status.COMPLETE,
        result={
            "houses": [{"house": 1, "sign": "Taurus"}],
            "grahas": [{"body": "Surya"}, {"body": "Chandra"}],
            "vargas": {"D1": {}, "D9": {}},
            "dashas": {"vimshottari": []},
        },
    )


def valid_payload(profile, relationship=None):
    return {
        "report_type_id": "personal_overview",
        "chart_id": profile.id,
        "relationship_id": relationship.id if relationship else None,
        "language": "ru",
        "audience": "novice",
    }


def provider_response_from_payload(provider_payload):
    item = provider_payload["items"][0]
    return {
        "schema_version": 1,
        "provider": "real",
        "report_type_id": provider_payload["report_type_id"],
        "report_recipe_id": provider_payload["report_recipe_id"],
        "theses": [
            {
                "id": f"real.thesis.01.{item['evidence_item_id']}",
                "title": "Validated staging thesis",
                "body": "A limited staging response based only on verified evidence.",
                "evidence_item_ids": [item["evidence_item_id"]],
                "citations": [{"evidence_item_id": item["evidence_item_id"], **item["citation_chains"][0]}],
                "confidence": "medium",
            }
        ],
    }


@pytest.mark.django_db
@override_settings(AI_REPORTS_ENABLED=False, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True)
def test_staging_gateway_is_unavailable_when_feature_flag_is_off(client, user, place):
    profile = make_profile(user, place)
    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")
    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(
    DEBUG=False,
    AI_REPORTS_ENABLED=True,
    AI_PROVIDER="real",
    AI_REAL_PROVIDER_ENABLED=True,
    AI_REPORTS_STAGING_ONLY=True,
)
def test_production_environment_blocks_real_provider(client, user, place):
    profile = make_profile(user, place)
    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")
    assert response.status_code in {403, 404}


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True)
def test_staging_gateway_rejects_client_control_fields(client, user, place):
    profile = make_profile(user, place)
    for field in [
        "prompt",
        "system",
        "messages",
        "evidence",
        "eligibleItems",
        "excludedItems",
        "citations",
        "rules",
        "passages",
        "sources",
        "model",
        "temperature",
        "maxTokens",
        "provider",
    ]:
        response = client.post(
            "/api/ai/report-staging-run",
            {**valid_payload(profile), field: "client supplied"},
            format="json",
        )
        assert response.status_code == 400
        assert field in response.data["error"]


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True, AI_REAL_PROVIDER_API_KEY="")
def test_real_provider_missing_api_key_returns_controlled_error(client, user, place):
    profile = make_profile(user, place)
    attach_complete_calculation(profile)
    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")
    assert response.status_code == 502
    assert "api key" in response.data["error"]


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True, AI_REAL_PROVIDER_API_KEY="test-key")
def test_real_provider_receives_anonymized_verified_request_only(monkeypatch, client, user, place):
    from apps.reports import ai_real_provider

    captured = {}

    def transport(url, payload, headers, timeout, max_response_bytes):
        captured["payload"] = payload
        return json.dumps(provider_response_from_payload(payload)).encode("utf-8")

    monkeypatch.setattr(ai_real_provider, "post_json_bytes", transport)
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")

    assert response.status_code == 200
    serialized = json.dumps(captured["payload"], ensure_ascii=False)
    assert "excluded_items" not in captured["payload"]
    assert "chart_id" not in captured["payload"]
    assert "relationship_id" not in captured["payload"]
    assert profile.display_name not in serialized
    assert str(profile.birth_date) not in serialized
    assert str(profile.birth_time) not in serialized
    assert profile.place.name not in serialized
    assert str(profile.place.latitude) not in serialized
    assert user.email not in serialized
    assert all(item["citation_chains"] for item in captured["payload"]["items"])


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True, AI_REAL_PROVIDER_API_KEY="test-key")
def test_insufficient_verified_evidence_does_not_call_real_provider(monkeypatch, client, user, place):
    from apps.reports import ai_real_provider

    def transport(url, payload, headers, timeout, max_response_bytes):
        raise AssertionError("network must not be called")

    monkeypatch.setattr(ai_real_provider, "post_json_bytes", transport)
    profile = make_profile(user, place)

    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")

    assert response.status_code == 422
    assert response.data["error"] == "insufficient_verified_evidence"


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True, AI_REAL_PROVIDER_API_KEY="test-key")
def test_malformed_real_provider_json_is_rejected(monkeypatch, client, user, place):
    from apps.reports import ai_real_provider

    monkeypatch.setattr(ai_real_provider, "post_json_bytes", lambda *args: b"{bad json")
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")

    assert response.status_code == 502
    assert "valid JSON" in response.data["error"]


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True, AI_REAL_PROVIDER_API_KEY="test-key")
def test_real_provider_unknown_evidence_ref_is_rejected(monkeypatch, client, user, place):
    from apps.reports import ai_real_provider

    def transport(url, payload, headers, timeout, max_response_bytes):
        response = provider_response_from_payload(payload)
        response["theses"][0]["evidence_item_ids"] = ["unknown.item"]
        return json.dumps(response).encode("utf-8")

    monkeypatch.setattr(ai_real_provider, "post_json_bytes", transport)
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")

    assert response.status_code == 502
    assert "unknown evidence item" in response.data["error"]


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True, AI_REAL_PROVIDER_API_KEY="test-key")
def test_real_provider_unknown_citation_ref_is_rejected(monkeypatch, client, user, place):
    from apps.reports import ai_real_provider

    def transport(url, payload, headers, timeout, max_response_bytes):
        response = provider_response_from_payload(payload)
        response["theses"][0]["citations"][0]["source_id"] = "source.unverified"
        return json.dumps(response).encode("utf-8")

    monkeypatch.setattr(ai_real_provider, "post_json_bytes", transport)
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")

    assert response.status_code == 502
    assert "missing citation chain" in response.data["error"]


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True, AI_REAL_PROVIDER_API_KEY="test-key")
def test_real_provider_html_and_links_are_rejected(monkeypatch, client, user, place):
    from apps.reports import ai_real_provider

    def transport(url, payload, headers, timeout, max_response_bytes):
        response = provider_response_from_payload(payload)
        response["theses"][0]["body"] = "<script>alert(1)</script> https://example.test"
        return json.dumps(response).encode("utf-8")

    monkeypatch.setattr(ai_real_provider, "post_json_bytes", transport)
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post("/api/ai/report-staging-run", valid_payload(profile), format="json")

    assert response.status_code == 502
    assert "unsafe text" in response.data["error"]


@pytest.mark.django_db
@override_settings(DEBUG=True, AI_REPORTS_ENABLED=True, AI_PROVIDER="real", AI_REAL_PROVIDER_ENABLED=True, AI_REAL_PROVIDER_API_KEY="test-key")
def test_mock_dry_run_remains_mock_only(monkeypatch, client, user, place):
    from apps.reports import ai_real_provider

    def transport(url, payload, headers, timeout, max_response_bytes):
        raise AssertionError("dry-run must not call real provider")

    monkeypatch.setattr(ai_real_provider, "post_json_bytes", transport)
    profile = make_profile(user, place)
    attach_complete_calculation(profile)

    response = client.post("/api/ai/report-dry-run", valid_payload(profile), format="json")

    assert response.status_code == 200
    assert response.data["response"]["provider"] == "mock"
