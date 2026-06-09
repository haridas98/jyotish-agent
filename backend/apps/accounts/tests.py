import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_creates_active_user_and_logs_in():
    client = APIClient()

    response = client.post(
        reverse("auth-register"),
        {
            "username": "haridas",
            "email": "haridas@example.test",
            "password": "strong-pass-108",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == "active"
    assert response.data["user"]["username"] == "haridas"
    user = get_user_model().objects.get(username="haridas")
    assert user.is_active is True
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_login_rejects_pending_user():
    get_user_model().objects.create_user(username="haridas", password="strong-pass-108", is_active=False)
    client = APIClient()

    response = client.post(
        reverse("auth-login"),
        {"username": "haridas", "password": "strong-pass-108"},
        format="json",
    )

    assert response.status_code == 403
    assert response.data["error"] == "account pending approval"


@pytest.mark.django_db
def test_login_accepts_approved_user():
    get_user_model().objects.create_user(username="haridas", password="strong-pass-108", is_active=True)
    client = APIClient()

    response = client.post(
        reverse("auth-login"),
        {"username": "haridas", "password": "strong-pass-108"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["user"]["is_active"] is True


@pytest.mark.django_db
def test_login_rejects_wrong_password():
    get_user_model().objects.create_user(username="haridas", password="strong-pass-108")
    client = APIClient()

    response = client.post(
        reverse("auth-login"),
        {"username": "haridas", "password": "wrong-pass-108"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_csrf_endpoint_sets_csrf_cookie():
    client = APIClient()

    response = client.get(reverse("auth-csrf"))

    assert response.status_code == 200
    assert response.data == {"status": "ok"}
    assert "csrftoken" in response.cookies


@pytest.mark.django_db
@override_settings(PRIVATE_APP_REQUIRE_AUTH=True)
def test_private_app_requires_approved_login_for_calculation_api():
    client = APIClient()

    anonymous = client.post(
        reverse("birth-chart"),
        {"birth_date": "2000-01-01", "birth_time": "10:00", "place_name": "Vrindavan"},
        format="json",
    )

    assert anonymous.status_code in {401, 403}

    user = get_user_model().objects.create_user(username="approved", password="strong-pass-108", is_active=True)
    client.force_authenticate(user=user)
    authenticated = client.post(
        reverse("birth-chart"),
        {"birth_date": "2000-01-01", "birth_time": "10:00", "place_name": "Vrindavan"},
        format="json",
    )

    assert authenticated.status_code in {200, 503}
