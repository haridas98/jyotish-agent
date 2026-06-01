import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import BirthProfile, ChartCalculation


@pytest.fixture
def user():
    return get_user_model().objects.create_user(username="haridas", password="strong-pass-108")


@pytest.mark.django_db
def test_birth_profile_create_resolves_place_for_authenticated_user(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Test chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "birth_time_accuracy": "exact",
            "place_name": "Vrindavan, Uttar Pradesh, India",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["profile"]["display_name"] == "Test chart"
    assert response.data["profile"]["place"]["label"] == "Vrindavan, Uttar Pradesh, IN"
    assert response.data["profile"]["timezone"] == "Asia/Kolkata"
    assert BirthProfile.objects.filter(user=user, display_name="Test chart").exists()


@pytest.mark.django_db
def test_birth_profile_create_accepts_geocoded_place_for_authenticated_user(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "London chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "birth_time_accuracy": "exact",
            "place_name": "London, United Kingdom, GB",
            "place_id": "geonames:2643743",
            "timezone": "Europe/London",
            "latitude": 51.50853,
            "longitude": -0.12574,
            "country_code": "GB",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["profile"]["place"]["label"] == "London, United Kingdom, GB"
    assert response.data["profile"]["timezone"] == "Europe/London"


@pytest.mark.django_db
def test_birth_profile_list_only_returns_current_users_profiles(user):
    other_user = get_user_model().objects.create_user(username="other", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)

    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Private chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    assert create_response.status_code == 201

    response = other_client.get("/api/charts/profiles")

    assert response.status_code == 200
    assert response.data == {"profiles": []}


@pytest.mark.django_db
def test_birth_profile_list_includes_latest_calculation_summary(user):
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Calculated chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    profile_id = create_response.data["profile"]["id"]
    ChartCalculation.objects.create(
        profile_id=profile_id,
        calculation_version="mvp-test",
        status=ChartCalculation.Status.COMPLETE,
        result={"grahas": [{"body": "Surya"}]},
    )

    response = client.get("/api/charts/profiles")

    assert response.status_code == 200
    assert response.data["profiles"][0]["latest_calculation"]["status"] == "complete"
    assert response.data["profiles"][0]["latest_calculation"]["graha_count"] == 1


@pytest.mark.django_db
def test_birth_profiles_require_authentication():
    response = APIClient().get("/api/charts/profiles")

    assert response.status_code in {401, 403}
