import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import UserJyotishSettings
from apps.charts.models import BirthProfile


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
def test_register_normalizes_username_and_login_is_case_insensitive():
    client = APIClient()

    response = client.post(
        reverse("auth-register"),
        {
            "username": "HariDas",
            "email": "HariDas@Example.Test",
            "password": "strong-pass-108",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["user"]["username"] == "haridas"
    user = get_user_model().objects.get(username="haridas")
    assert user.email == "haridas@example.test"

    client.post(reverse("auth-logout"), format="json")
    login_response = client.post(
        reverse("auth-login"),
        {"username": "HARIDAS", "password": "strong-pass-108"},
        format="json",
    )

    assert login_response.status_code == 200
    assert login_response.data["user"]["username"] == "haridas"


@pytest.mark.django_db
def test_register_rejects_username_duplicate_with_different_case():
    get_user_model().objects.create_user(username="haridas", password="strong-pass-108")
    client = APIClient()

    response = client.post(
        reverse("auth-register"),
        {"username": "HariDas", "password": "strong-pass-108"},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["error"] == "username already exists"


@pytest.mark.django_db
def test_register_can_create_self_profile_without_birth_time():
    client = APIClient()

    response = client.post(
        reverse("auth-register"),
        {
            "username": "new-person",
            "email": "new-person@example.test",
            "password": "strong-pass-108",
            "birth_date": "2000-01-01",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["profile"]["is_self_profile"] is True
    assert response.data["profile"]["birth_time"] is None
    assert response.data["profile"]["birth_time_accuracy"] == "unknown"
    profile = BirthProfile.objects.get(user__username="new-person")
    assert profile.is_self_profile is True
    assert profile.birth_time is None


@pytest.mark.django_db
def test_register_rejects_partial_birth_profile_and_rolls_back_user():
    client = APIClient()

    response = client.post(
        reverse("auth-register"),
        {
            "username": "partial-birth",
            "password": "strong-pass-108",
            "birth_date": "2000-01-01",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "birth_date and place_name" in response.data["error"]
    assert not get_user_model().objects.filter(username="partial-birth").exists()


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


@pytest.mark.django_db
def test_user_settings_defaults_are_created_for_authenticated_user():
    user = get_user_model().objects.create_user(username="settings-user", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse("user-settings"))

    assert response.status_code == 200
    assert response.data["userId"] == user.id
    assert response.data["calculation"]["ayanamsa"] == "lahiri"
    assert response.data["calculation"]["divisionalChartsEnabled"] == ["D1", "D9"]
    assert response.data["display"]["chartStyle"] == "north_indian"
    assert UserJyotishSettings.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_user_settings_patch_updates_calculation_and_display():
    user = get_user_model().objects.create_user(username="settings-patch", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        reverse("user-settings"),
        {
            "calculation": {
                "ayanamsa": "raman",
                "zodiacType": "sidereal",
                "houseSystem": "sripati",
                "nodeType": "true",
                "calculationProfile": "bphs_research",
                "divisionalChartsEnabled": ["D1", "D9", "D10"],
                "defaultDivisionalChart": "D9",
                "timezoneMode": "birth_place_timezone",
            },
            "display": {
                "chartStyle": "south_indian",
                "language": "en",
                "terminologyMode": "sanskrit",
                "degreeFormat": "decimal",
                "showSanskritNames": False,
                "showTransliteration": False,
                "themeMode": "dark",
            },
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["calculation"]["ayanamsa"] == "raman"
    assert response.data["calculation"]["defaultDivisionalChart"] == "D9"
    assert response.data["display"]["chartStyle"] == "south_indian"
    assert response.data["display"]["showSanskritNames"] is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload,error",
    [
        ({"calculation": {"ayanamsa": "unknown"}}, "calculation.ayanamsa"),
        ({"display": {"chartStyle": "east_indian"}}, "display.chartStyle"),
        ({"display": {"language": "de"}}, "display.language"),
        ({"calculation": {"divisionalChartsEnabled": ["D1"], "defaultDivisionalChart": "D9"}}, "defaultDivisionalChart"),
    ],
)
def test_user_settings_reject_invalid_values(payload, error):
    user = get_user_model().objects.create_user(username=f"settings-invalid-{error}", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(reverse("user-settings"), payload, format="json")

    assert response.status_code == 400
    assert error in response.data["error"]


@pytest.mark.django_db
def test_user_settings_are_scoped_to_current_user():
    first = get_user_model().objects.create_user(username="settings-first", password="strong-pass-108")
    second = get_user_model().objects.create_user(username="settings-second", password="strong-pass-108")
    first_client = APIClient()
    first_client.force_authenticate(user=first)
    second_client = APIClient()
    second_client.force_authenticate(user=second)

    first_client.patch(reverse("user-settings"), {"display": {"chartStyle": "south_indian"}}, format="json")
    response = second_client.get(reverse("user-settings"))

    assert response.status_code == 200
    assert response.data["display"]["chartStyle"] == "north_indian"
