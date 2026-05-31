import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_creates_user_and_session():
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
    assert response.data["user"]["username"] == "haridas"
    assert get_user_model().objects.filter(username="haridas").exists()


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

