import json
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from apps.calculations.chart import CALCULATION_VERSION

from .models import BirthProfile, BirthProfileRelationship, ChartCalculation
from .services import _profile_input


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
def test_birth_profile_create_persists_calculation_settings(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Settings chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "birth_time_accuracy": "exact",
            "place_name": "Vrindavan",
            "calculation_model": "drik_siddhanta",
            "ayanamsa": "lahiri",
            "node_type": "mean",
            "ephemeris": "swiss",
            "house_system": "whole_sign",
            "bhava_system": "whole_sign",
            "varga_scheme": "parashara",
            "sunrise_source": "noaa",
            "timezone_source": "iana",
            "shadbala_profile": "bphs_classical",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["profile"]["calculation_settings"]["node_type"] == "mean"
    profile = BirthProfile.objects.get(user=user, display_name="Settings chart")
    assert profile.calculation_settings["node_type"] == "mean"


@pytest.mark.django_db
def test_birth_profile_create_accepts_unknown_birth_time(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Unknown time chart",
            "birth_date": "1990-08-15",
            "birth_time": "",
            "birth_time_accuracy": "unknown",
            "place_name": "Vrindavan",
            "is_self_profile": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["profile"]["birth_time"] is None
    assert response.data["profile"]["birth_time_accuracy"] == "unknown"
    profile = BirthProfile.objects.get(user=user, display_name="Unknown time chart")
    assert profile.birth_time is None
    assert profile.birth_time_accuracy == BirthProfile.TimeAccuracy.UNKNOWN


@pytest.mark.django_db
def test_profile_input_carries_birth_time_accuracy_for_d60_gate(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Approximate time chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "birth_time_accuracy": "approximate",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 201
    profile = BirthProfile.objects.get(id=response.data["profile"]["id"])
    assert _profile_input(profile)["birth_time_accuracy"] == "approximate"

@pytest.mark.django_db
def test_birth_profile_create_marks_single_self_profile(user):
    client = APIClient()
    client.force_authenticate(user=user)

    first_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "My first chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
            "is_self_profile": True,
        },
        format="json",
    )
    second_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "My current chart",
            "birth_date": "1991-01-01",
            "birth_time": "06:00",
            "place_name": "Mayapur",
            "is_self_profile": True,
        },
        format="json",
    )

    assert first_response.status_code == 201
    assert first_response.data["profile"]["is_self_profile"] is True
    assert second_response.status_code == 201
    assert second_response.data["profile"]["is_self_profile"] is True
    assert BirthProfile.objects.get(user=user, display_name="My first chart").is_self_profile is False
    assert BirthProfile.objects.get(user=user, display_name="My current chart").is_self_profile is True
    list_response = client.get("/api/charts/profiles")
    assert [item["is_self_profile"] for item in list_response.data["profiles"]].count(True) == 1


@pytest.mark.django_db
def test_birth_profile_patch_updates_single_self_profile(user):
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Me",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
            "is_self_profile": True,
        },
        format="json",
    ).data["profile"]
    second = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Other saved chart",
            "birth_date": "1991-01-01",
            "birth_time": "06:00",
            "place_name": "Mayapur",
        },
        format="json",
    ).data["profile"]

    response = client.patch(
        f"/api/charts/profiles/{second['id']}",
        {"is_self_profile": True},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["profile"]["is_self_profile"] is True
    assert BirthProfile.objects.get(id=first["id"]).is_self_profile is False
    assert BirthProfile.objects.get(id=second["id"]).is_self_profile is True


@pytest.mark.django_db
def test_chart_alias_routes_support_list_detail_update_and_delete(user):
    client = APIClient()
    client.force_authenticate(user=user)

    create_response = client.post(
        "/api/charts",
        {
            "display_name": "Client chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "birth_time_accuracy": "exact",
            "gender": "male",
            "place_name": "Vrindavan",
            "notes": "first saved chart",
        },
        format="json",
    )

    assert create_response.status_code == 201
    profile_id = create_response.data["profile"]["id"]
    assert client.get("/api/charts").data["profiles"][0]["id"] == profile_id

    detail_response = client.get(f"/api/charts/{profile_id}")
    assert detail_response.status_code == 200
    assert detail_response.data["profile"]["display_name"] == "Client chart"
    assert detail_response.data["profile"]["gender"] == "male"
    assert detail_response.data["profile"]["notes"] == "first saved chart"

    update_response = client.patch(
        f"/api/charts/{profile_id}",
        {
            "display_name": "Updated client chart",
            "birth_date": "1990-08-16",
            "birth_time": "11:25",
            "birth_time_accuracy": "approximate",
            "gender": "female",
            "place_name": "Mayapur",
            "notes": "updated notes",
        },
        format="json",
    )

    assert update_response.status_code == 200
    assert update_response.data["profile"]["display_name"] == "Updated client chart"
    assert update_response.data["profile"]["birth_date"] == "1990-08-16"
    assert update_response.data["profile"]["birth_time"] == "11:25"
    assert update_response.data["profile"]["birth_time_accuracy"] == "approximate"
    assert update_response.data["profile"]["gender"] == "female"
    assert update_response.data["profile"]["notes"] == "updated notes"

    delete_response = client.delete(f"/api/charts/{profile_id}")
    assert delete_response.status_code == 204
    assert BirthProfile.objects.filter(id=profile_id).exists() is False


@pytest.mark.django_db
def test_chart_detail_does_not_expose_other_users_profile(user):
    other_user = get_user_model().objects.create_user(username="other", password="strong-pass-108")
    owner_client = APIClient()
    owner_client.force_authenticate(user=user)
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)

    profile = owner_client.post(
        "/api/charts",
        {
            "display_name": "Private chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    ).data["profile"]

    assert other_client.get(f"/api/charts/{profile['id']}").status_code == 404
    assert other_client.patch(f"/api/charts/{profile['id']}", {"display_name": "Leak"}, format="json").status_code == 404
    assert other_client.delete(f"/api/charts/{profile['id']}").status_code == 404


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
def test_birth_profile_create_accepts_gelendzhik_catalog_place(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Gelendzhik chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "birth_time_accuracy": "exact",
            "place_name": "Gelendzhik, Russia, RU",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["profile"]["place"]["label"] == "Gelendzhik, Russia, RU"
    assert response.data["profile"]["timezone"] == "Europe/Moscow"


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
def test_birth_profile_list_batches_latest_calculation_queries(user):
    client = APIClient()
    client.force_authenticate(user=user)
    for index in range(3):
        create_response = client.post(
            "/api/charts/profiles",
            {
                "display_name": f"Calculated chart {index}",
                "birth_date": "1990-08-15",
                "birth_time": "10:24",
                "place_name": "Vrindavan",
            },
            format="json",
        )
        ChartCalculation.objects.create(
            profile_id=create_response.data["profile"]["id"],
            calculation_version="mvp-test",
            status=ChartCalculation.Status.COMPLETE,
            result={"grahas": [{"body": "Surya"}]},
        )

    with CaptureQueriesContext(connection) as captured:
        response = client.get("/api/charts/profiles")

    assert response.status_code == 200
    assert len(response.data["profiles"]) == 3
    assert all(item["latest_calculation"]["graha_count"] == 1 for item in response.data["profiles"])
    assert len(captured.captured_queries) <= 5
    sql = "\n".join(query["sql"].lower() for query in captured.captured_queries)
    assert '"charts_chartcalculation"."input_snapshot"' not in sql
    assert '"charts_chartcalculation"."result"' not in sql


@pytest.mark.django_db
def test_birth_profile_calculate_reuses_current_complete_calculation(user):
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Reusable chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    profile = BirthProfile.objects.select_related("place").get(id=create_response.data["profile"]["id"])
    existing = ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
        status=ChartCalculation.Status.COMPLETE,
        result={"grahas": [{"body": "Surya"}]},
    )

    response = client.post(f"/api/charts/profiles/{profile.id}/calculate")

    assert response.status_code == 200
    assert response.data["calculation"]["id"] == existing.id
    assert response.data["calculation"]["reused"] is True
    assert ChartCalculation.objects.filter(profile=profile).count() == 1


@pytest.mark.django_db
def test_profile_relationship_api_creates_and_updates_private_role(user):
    client = APIClient()
    client.force_authenticate(user=user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Father", "birth_date": "1960-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]

    create_response = client.post(
        "/api/charts/profile-relationships",
        {"profile_id": profile_a["id"], "related_profile_id": profile_b["id"], "role": "father"},
        format="json",
    )
    update_response = client.post(
        "/api/charts/profile-relationships",
        {"profile_id": profile_a["id"], "related_profile_id": profile_b["id"], "role": "boss"},
        format="json",
    )
    list_response = client.get("/api/charts/profile-relationships")

    assert create_response.status_code == 201
    assert update_response.status_code == 201
    assert update_response.data["relationship"]["id"] == create_response.data["relationship"]["id"]
    assert update_response.data["relationship"]["role"] == "boss"
    assert update_response.data["relationship"]["link_status"] == BirthProfileRelationship.LinkStatus.PRIVATE
    assert list_response.data["relationships"][0]["role"] == "boss"
    assert BirthProfileRelationship.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_profile_relationship_detail_returns_owned_relationship(user):
    client = APIClient()
    client.force_authenticate(user=user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Boss", "birth_date": "1970-01-01", "birth_time": "09:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]
    create_response = client.post(
        "/api/charts/profile-relationships",
        {"profile_id": profile_a["id"], "related_profile_id": profile_b["id"], "role": "boss"},
        format="json",
    )

    response = client.get(f"/api/charts/profile-relationships/{create_response.data['relationship']['id']}")

    assert response.status_code == 200
    assert response.data["relationship"]["role"] == "boss"
    assert response.data["relationship"]["profile"]["display_name"] == "Me"
    assert response.data["relationship"]["related_profile"]["display_name"] == "Boss"


@pytest.mark.django_db
@pytest.mark.parametrize("role", ["brother", "sister"])
def test_profile_relationship_api_accepts_specific_sibling_roles(user, role):
    client = APIClient()
    client.force_authenticate(user=user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Relative", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]

    response = client.post(
        "/api/charts/profile-relationships",
        {"profile_id": profile_a["id"], "related_profile_id": profile_b["id"], "role": role},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["relationship"]["role"] == role
    assert BirthProfileRelationship.objects.get(user=user).role == role


@pytest.mark.django_db
def test_profile_relationship_api_rejects_other_users_profile(user):
    other_user = get_user_model().objects.create_user(username="other-owner", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    other_profile = other_client.post(
        "/api/charts/profiles",
        {"display_name": "Hidden", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]

    response = client.post(
        "/api/charts/profile-relationships",
        {"profile_id": profile_a["id"], "related_profile_id": other_profile["id"], "role": "father"},
        format="json",
    )

    assert response.status_code == 404
    assert BirthProfileRelationship.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_profile_relationship_request_inbox_and_accept(user):
    target_user = get_user_model().objects.create_user(username="target", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    target_client = APIClient()
    target_client.force_authenticate(user=target_user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Target draft", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]
    target_real_profile = target_client.post(
        "/api/charts/profiles",
        {"display_name": "Target real", "birth_date": "1992-02-02", "birth_time": "07:30", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]

    create_response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_b["id"],
            "role": "partner",
            "requested_username": "target",
        },
        format="json",
    )
    inbox_response = target_client.get("/api/charts/profile-relationships/inbox")
    action_response = target_client.post(
        f"/api/charts/profile-relationships/{create_response.data['relationship']['id']}/action",
        {"action": "accept", "accepted_profile_id": target_real_profile["id"]},
        format="json",
    )
    target_list_response = target_client.get("/api/charts/profile-relationships")

    assert create_response.status_code == 201
    assert create_response.data["relationship"]["link_status"] == BirthProfileRelationship.LinkStatus.REQUESTED
    assert inbox_response.status_code == 200
    assert inbox_response.data["relationships"][0]["user"]["username"] == "haridas"
    assert inbox_response.data["relationships"][0]["related_profile"]["display_name"] == "Target draft"
    assert action_response.status_code == 200
    assert action_response.data["relationship"]["link_status"] == BirthProfileRelationship.LinkStatus.ACCEPTED
    assert action_response.data["relationship"]["related_profile"]["display_name"] == "Target real"
    assert BirthProfileRelationship.objects.get(id=create_response.data["relationship"]["id"]).link_status == "accepted"
    assert target_list_response.status_code == 200
    assert target_list_response.data["relationships"][0]["link_status"] == BirthProfileRelationship.LinkStatus.ACCEPTED
    assert target_list_response.data["relationships"][0]["profile"]["display_name"] == "Target real"
    assert target_list_response.data["relationships"][0]["related_profile"]["display_name"] == "Me"
    target_detail_response = target_client.get(
        f"/api/charts/profile-relationships/{target_list_response.data['relationships'][0]['id']}"
    )
    assert target_detail_response.status_code == 200
    assert target_detail_response.data["relationship"]["profile"]["display_name"] == "Target real"
    assert target_detail_response.data["relationship"]["related_profile"]["display_name"] == "Me"
    assert BirthProfileRelationship.objects.filter(
        user=target_user,
        profile_id=target_real_profile["id"],
        related_profile_id=profile_a["id"],
        link_status=BirthProfileRelationship.LinkStatus.ACCEPTED,
    ).exists()


@pytest.mark.django_db
def test_profile_relationship_request_username_is_case_insensitive(user):
    target_user = get_user_model().objects.create_user(username="TargetCase", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Target draft", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]

    response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_b["id"],
            "role": "partner",
            "requested_username": "targetcase",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["relationship"]["requested_user"]["id"] == target_user.id
    assert response.data["relationship"]["link_status"] == BirthProfileRelationship.LinkStatus.REQUESTED


@pytest.mark.django_db
def test_profile_relationship_request_accept_requires_recipient_profile(user):
    target_user = get_user_model().objects.create_user(username="target-no-profile", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    target_client = APIClient()
    target_client.force_authenticate(user=target_user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Target draft", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]
    create_response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_b["id"],
            "role": "partner",
            "requested_username": "target-no-profile",
        },
        format="json",
    )

    response = target_client.post(
        f"/api/charts/profile-relationships/{create_response.data['relationship']['id']}/action",
        {"action": "accept"},
        format="json",
    )

    assert response.status_code == 400
    assert "accepted_profile_id" in response.data["error"]


@pytest.mark.django_db
def test_profile_relationship_request_accept_rejects_profile_not_owned_by_recipient(user):
    target_user = get_user_model().objects.create_user(username="target-wrong-profile", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    target_client = APIClient()
    target_client.force_authenticate(user=target_user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Target draft", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]
    create_response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_b["id"],
            "role": "partner",
            "requested_username": target_user.username,
        },
        format="json",
    )

    response = target_client.post(
        f"/api/charts/profile-relationships/{create_response.data['relationship']['id']}/action",
        {"action": "accept", "accepted_profile_id": profile_a["id"]},
        format="json",
    )

    assert response.status_code == 400
    assert "recipient user" in response.data["error"]
    assert BirthProfileRelationship.objects.get(id=create_response.data["relationship"]["id"]).link_status == "requested"
    assert BirthProfileRelationship.objects.filter(user=target_user).count() == 0


@pytest.mark.django_db
def test_profile_relationship_request_action_forbidden_for_non_recipient(user):
    target_user = get_user_model().objects.create_user(username="target2", password="strong-pass-108")
    intruder = get_user_model().objects.create_user(username="intruder", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    intruder_client = APIClient()
    intruder_client.force_authenticate(user=intruder)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Target draft", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]
    create_response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_b["id"],
            "role": "partner",
            "requested_user_id": target_user.id,
        },
        format="json",
    )

    response = intruder_client.post(
        f"/api/charts/profile-relationships/{create_response.data['relationship']['id']}/action",
        {"action": "accept"},
        format="json",
    )

    assert response.status_code == 404
    assert BirthProfileRelationship.objects.get(id=create_response.data["relationship"]["id"]).link_status == "requested"


@pytest.mark.django_db
def test_profile_relationship_request_rejects_self_requested_user(user):
    client = APIClient()
    client.force_authenticate(user=user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Draft", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]

    response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_b["id"],
            "role": "partner",
            "requested_username": user.username,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "another registered user" in response.data["error"]
    assert BirthProfileRelationship.objects.filter(user=user).count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("action,expected_status", [("decline", "declined"), ("block", "blocked")])
def test_profile_relationship_decline_or_block_does_not_create_reciprocal_link(user, action, expected_status):
    target_user = get_user_model().objects.create_user(username=f"target-{action}", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    target_client = APIClient()
    target_client.force_authenticate(user=target_user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Target draft", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]

    create_response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_b["id"],
            "role": "partner",
            "requested_username": target_user.username,
        },
        format="json",
    )
    response = target_client.post(
        f"/api/charts/profile-relationships/{create_response.data['relationship']['id']}/action",
        {"action": action},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["relationship"]["link_status"] == expected_status
    assert BirthProfileRelationship.objects.filter(user=target_user).count() == 0
    assert target_client.get("/api/charts/profile-relationships/inbox").data["relationships"] == []


@pytest.mark.django_db
def test_profile_relationship_block_prevents_repeated_request(user):
    target_user = get_user_model().objects.create_user(username="target-block-repeat", password="strong-pass-108")
    client = APIClient()
    client.force_authenticate(user=user)
    target_client = APIClient()
    target_client.force_authenticate(user=target_user)
    profile_a = client.post(
        "/api/charts/profiles",
        {"display_name": "Me", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]
    profile_b = client.post(
        "/api/charts/profiles",
        {"display_name": "Target draft", "birth_date": "1991-01-01", "birth_time": "06:00", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]
    profile_c = client.post(
        "/api/charts/profiles",
        {"display_name": "Target draft 2", "birth_date": "1993-03-03", "birth_time": "08:15", "place_name": "Mayapur"},
        format="json",
    ).data["profile"]
    create_response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_b["id"],
            "role": "partner",
            "requested_username": target_user.username,
        },
        format="json",
    )
    block_response = target_client.post(
        f"/api/charts/profile-relationships/{create_response.data['relationship']['id']}/action",
        {"action": "block"},
        format="json",
    )

    repeated_response = client.post(
        "/api/charts/profile-relationships",
        {
            "profile_id": profile_a["id"],
            "related_profile_id": profile_c["id"],
            "role": "partner",
            "requested_username": target_user.username,
        },
        format="json",
    )

    assert block_response.status_code == 200
    assert repeated_response.status_code == 400
    assert "blocked" in repeated_response.data["error"]
    assert target_client.get("/api/charts/profile-relationships/inbox").data["relationships"] == []


@pytest.mark.django_db
def test_birth_profiles_require_authentication():
    response = APIClient().get("/api/charts/profiles")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
@override_settings(PRIVATE_APP_REQUIRE_AUTH=True)
def test_birth_profiles_private_gate_rejects_inactive_user():
    inactive = get_user_model().objects.create_user(
        username="inactive-chart-user",
        password="strong-pass-108",
        is_active=False,
    )
    client = APIClient()
    client.force_authenticate(user=inactive)

    response = client.get("/api/charts/profiles")

    assert response.status_code in {401, 403}
@pytest.mark.django_db
def test_chart_workbench_returns_latest_complete_d1(user):
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Workbench chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    profile = BirthProfile.objects.select_related("place").get(id=create_response.data["profile"]["id"])
    calculation = ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
        status=ChartCalculation.Status.COMPLETE,
        result={
            "ascendant": {"body": "Lagna", "longitude": 90.0, "rashi": "Cancer", "rashi_index": 3, "nakshatra": "Pushya", "pada": 1, "navamsa": "Cancer"},
            "grahas": [{"body": "Surya", "longitude": 120.0, "rashi": "Leo", "rashi_index": 4, "nakshatra": "Magha", "pada": 1, "navamsa": "Aries"}],
            "houses": [{"house": 1, "rashi": "Cancer", "rashi_index": 3}, {"house": 2, "rashi": "Leo", "rashi_index": 4}],
            "vargas": {"D2": {"code": "D2", "name": "Hora", "method": "Parashara", "methodId": "varga.parashara_shodasha.v1", "methodVersion": "1", "calculationPreset": "parashara", "placements": [{"body": "Lagna", "rashi": "Karka", "rashi_index": 3}, {"body": "Surya", "rashi": "Simha", "rashi_index": 4}]}, "D30": {"code": "D30", "name": "Trimsamsha", "method": "BPHS 6.27-28 Parashara unequal Trimsamsha segments.", "methodId": "varga.d30.parashara_unequal.v1", "methodVersion": "1", "calculationPreset": "parashara", "placements": [{"body": "Lagna", "rashi": "Mesha", "rashi_index": 0}, {"body": "Surya", "rashi": "Kumbha", "rashi_index": 10}]}, "D60": {"code": "D60", "name": "Shashtyamsha", "method": "Parashara Shashtyamsha", "methodId": "varga.d60.parashara_shashtyamsha.v1", "methodVersion": "1", "calculationPreset": "parashara", "placements": [{"body": "Lagna", "rashi": "Mesha", "rashi_index": 0}, {"body": "Surya", "rashi": "Vrishabha", "rashi_index": 1}]}, "D4": {"code": "D4", "name": "Chaturthamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Mesha", "rashi_index": 0}, {"body": "Surya", "rashi": "Karka", "rashi_index": 3}]}, "D16": {"code": "D16", "name": "Shodashamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Mesha", "rashi_index": 0}, {"body": "Surya", "rashi": "Kanya", "rashi_index": 5}]}, "D20": {"code": "D20", "name": "Vimshamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Vrishabha", "rashi_index": 1}, {"body": "Surya", "rashi": "Vrischika", "rashi_index": 7}]}, "D24": {"code": "D24", "name": "Siddhamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Kanya", "rashi_index": 5}, {"body": "Surya", "rashi": "Dhanu", "rashi_index": 8}]}, "D3": {"code": "D3", "name": "Drekkana", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Meena", "rashi_index": 11}, {"body": "Surya", "rashi": "Simha", "rashi_index": 4}]}, "D7": {"code": "D7", "name": "Saptamsa", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Mithuna", "rashi_index": 2}, {"body": "Surya", "rashi": "Karka", "rashi_index": 3}]}, "D9": {"code": "D9", "name": "Navamsa", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Karka", "rashi_index": 3}, {"body": "Surya", "rashi": "Makara", "rashi_index": 9}]}, "D10": {"code": "D10", "name": "Dashamsa", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Vrischika", "rashi_index": 7}, {"body": "Surya", "rashi": "Kanya", "rashi_index": 5}]}, "D12": {"code": "D12", "name": "Dvadashamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Vrishabha", "rashi_index": 1}, {"body": "Surya", "rashi": "Tula", "rashi_index": 6}]}},
            "birth": {},
            "place": {},
            "panchanga": {},
        },
    )

    response = client.get(f"/api/charts/{profile.id}/workbench?scope=d1")

    assert response.status_code == 200
    assert response.data["scope"] == "d1"
    assert response.data["profile"]["id"] == profile.id
    assert response.data["calculation"]["id"] == calculation.id
    assert response.data["result"]["grahas"][0]["body"] == "Surya"
    assert response.data["method"] == {"methodId": "varga.parashara_shodasha.v1", "methodVersion": "1", "calculationPreset": "parashara"}
    d9_response = client.get(f"/api/charts/{profile.id}/workbench?scope=d9")

    assert d9_response.status_code == 200
    assert d9_response.data["scope"] == "d9"
    assert d9_response.data["profile"]["id"] == profile.id
    assert d9_response.data["calculation"]["id"] == calculation.id
    assert d9_response.data["result"]["vargas"]["D9"]["placements"][0]["body"] == "Lagna"
    d10_response = client.get(f"/api/charts/{profile.id}/workbench?scope=d10")
    assert d10_response.status_code == 200
    assert d10_response.data["scope"] == "d10"
    assert d10_response.data["result"]["vargas"]["D10"]["placements"][0]["body"] == "Lagna"
    d12_response = client.get(f"/api/charts/{profile.id}/workbench?scope=d12")
    assert d12_response.status_code == 200
    assert d12_response.data["scope"] == "d12"
    assert d12_response.data["result"]["vargas"]["D12"]["placements"][0]["body"] == "Lagna"
    d3_response = client.get(f"/api/charts/{profile.id}/workbench?scope=d3")
    assert d3_response.status_code == 200
    assert d3_response.data["scope"] == "d3"
    assert d3_response.data["result"]["vargas"]["D3"]["placements"][0]["body"] == "Lagna"

    d7_response = client.get(f"/api/charts/{profile.id}/workbench?scope=d7")
    assert d7_response.status_code == 200
    assert d7_response.data["scope"] == "d7"
    assert d7_response.data["result"]["vargas"]["D7"]["placements"][0]["body"] == "Lagna"

    d30_response = client.get(f"/api/charts/{profile.id}/workbench?scope=d30")
    assert d30_response.status_code == 200
    assert d30_response.data["scope"] == "d30"
    assert d30_response.data["result"]["vargas"]["D30"]["methodId"] == "varga.d30.parashara_unequal.v1"
    assert d30_response.data["method"] == {"methodId": "varga.d30.parashara_unequal.v1", "methodVersion": "1", "calculationPreset": "parashara"}

    for scope in ("d2", "d4", "d16", "d20", "d24"):
        scope_response = client.get(f"/api/charts/{profile.id}/workbench?scope={scope}")
        assert scope_response.status_code == 200
        assert scope_response.data["scope"] == scope
        assert scope_response.data["result"]["vargas"][scope.upper()]["placements"][0]["body"] == "Lagna"

    d60_response = client.get(f"/api/charts/{profile.id}/workbench?scope=d60")
    assert d60_response.status_code == 200
    assert d60_response.data["scope"] == "d60"
    assert d60_response.data["result"]["vargas"]["D60"]["methodId"] == "varga.d60.parashara_shashtyamsha.v1"
    assert d60_response.data["method"] == {"methodId": "varga.d60.parashara_shashtyamsha.v1", "methodVersion": "1", "calculationPreset": "parashara"}
    assert any(warning["code"] == "d60_birth_time_accuracy" for warning in d60_response.data["warnings"])


@pytest.mark.django_db
def test_chart_workbench_does_not_expose_other_users_profile(user):
    other_user = get_user_model().objects.create_user(username="workbench-other", password="strong-pass-108")
    owner_client = APIClient()
    owner_client.force_authenticate(user=user)
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)
    profile = owner_client.post(
        "/api/charts/profiles",
        {
            "display_name": "Private workbench chart",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    ).data["profile"]

    response = other_client.get(f"/api/charts/{profile['id']}/workbench?scope=d1")

    assert response.status_code == 404
@pytest.mark.django_db
@override_settings(ENABLE_DEV_LOGIN=True, DEV_LOGIN_TOKEN="dev-token")
def test_dev_d1_workbench_check_returns_summary_with_token(user):
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "D1 external check",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    profile = BirthProfile.objects.select_related("place").get(id=create_response.data["profile"]["id"])
    ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
        status=ChartCalculation.Status.COMPLETE,
        result={
            "ascendant": {"body": "Lagna", "longitude": 90.0, "rashi": "Cancer", "rashi_index": 3, "nakshatra": "Pushya", "pada": 1, "navamsa": "Cancer"},
            "grahas": [{"body": "Surya", "longitude": 120.0, "rashi": "Leo", "rashi_index": 4, "nakshatra": "Magha", "pada": 1, "navamsa": "Aries"}],
            "houses": [{"house": item, "rashi": "Cancer", "rashi_index": item - 1} for item in range(1, 13)],
            "vargas": {"D2": {"code": "D2", "name": "Hora", "method": "Parashara", "methodId": "varga.parashara_shodasha.v1", "methodVersion": "1", "calculationPreset": "parashara", "placements": [{"body": "Lagna", "rashi": "Karka", "rashi_index": 3}, {"body": "Surya", "rashi": "Simha", "rashi_index": 4}]}, "D30": {"code": "D30", "name": "Trimsamsha", "method": "BPHS 6.27-28 Parashara unequal Trimsamsha segments.", "methodId": "varga.d30.parashara_unequal.v1", "methodVersion": "1", "calculationPreset": "parashara", "placements": [{"body": "Lagna", "rashi": "Mesha", "rashi_index": 0}, {"body": "Surya", "rashi": "Kumbha", "rashi_index": 10}]}, "D60": {"code": "D60", "name": "Shashtyamsha", "method": "Parashara Shashtyamsha", "methodId": "varga.d60.parashara_shashtyamsha.v1", "methodVersion": "1", "calculationPreset": "parashara", "placements": [{"body": "Lagna", "rashi": "Mesha", "rashi_index": 0}, {"body": "Surya", "rashi": "Vrishabha", "rashi_index": 1}]}, "D4": {"code": "D4", "name": "Chaturthamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Mesha", "rashi_index": 0}, {"body": "Surya", "rashi": "Karka", "rashi_index": 3}]}, "D16": {"code": "D16", "name": "Shodashamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Mesha", "rashi_index": 0}, {"body": "Surya", "rashi": "Kanya", "rashi_index": 5}]}, "D20": {"code": "D20", "name": "Vimshamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Vrishabha", "rashi_index": 1}, {"body": "Surya", "rashi": "Vrischika", "rashi_index": 7}]}, "D24": {"code": "D24", "name": "Siddhamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Kanya", "rashi_index": 5}, {"body": "Surya", "rashi": "Dhanu", "rashi_index": 8}]}, "D3": {"code": "D3", "name": "Drekkana", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Meena", "rashi_index": 11}, {"body": "Surya", "rashi": "Simha", "rashi_index": 4}]}, "D7": {"code": "D7", "name": "Saptamsa", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Mithuna", "rashi_index": 2}, {"body": "Surya", "rashi": "Karka", "rashi_index": 3}]}, "D9": {"code": "D9", "name": "Navamsa", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Karka", "rashi_index": 3}, {"body": "Surya", "rashi": "Makara", "rashi_index": 9}]}, "D10": {"code": "D10", "name": "Dashamsa", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Vrischika", "rashi_index": 7}, {"body": "Surya", "rashi": "Kanya", "rashi_index": 5}]}, "D12": {"code": "D12", "name": "Dvadashamsha", "method": "Parashara", "placements": [{"body": "Lagna", "rashi": "Vrishabha", "rashi_index": 1}, {"body": "Surya", "rashi": "Tula", "rashi_index": 6}]}},
            "birth": {},
            "place": {},
            "panchanga": {},
        },
    )
    public_client = APIClient()

    response = public_client.get(f"/api/dev/d1-workbench-check?token=dev-token&chart_id={profile.id}")

    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    assert response.data["status"] == "ok"
    assert response.data["schemaVersion"] == "d1-workbench-check.v2"
    assert response.data["chartId"] == profile.id
    assert response.data["scopeId"] == "D1"
    assert response.data["houseCount"] == 12
    assert response.data["rashiCount"] == 12
    assert response.data["grahaCount"] == 1
    assert response.data["specialPointCount"] == 1
    assert response.data["chartObjectCount"] == 2
    assert response.data["supportedStyles"] == ["north", "south"]
    assert response.data["supportedModes"] == ["novice", "astrologer"]
    assert response.data["entityInspectorCount"] == 1
    assert response.data["clickTargets"] == {"houses": 12, "rashis": 12, "grahas": 1, "specialPoints": 1}
    assert response.data["forbiddenScopesPresent"] == {"D60": False, "AI": False, "rawEvidence": False}
    assert response.data["supportedScopes"] == ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D30", "D60"]
    assert response.data["expertOnlyScopes"] == ["D30", "D60"]
    assert response.data["methodId"] == "varga.parashara_shodasha.v1"
    assert response.data["methodVersion"] == "1"
    assert response.data["calculationPreset"] == "parashara"
    assert response.data["warnings"] == []

    scopes = response.data["vargaScopes"]
    assert [item["code"] for item in scopes] == response.data["supportedScopes"]
    assert {item["category"] for item in scopes} == {"main", "family", "professional", "spiritual", "expert"}
    assert next(item for item in scopes if item["code"] == "D1") == {
        "code": "D1",
        "name": "Rashi",
        "category": "main",
        "methodId": "varga.parashara_shodasha.v1",
        "methodVersion": "1",
        "calculationPreset": "parashara",
        "expertOnly": False,
        "timeAccuracyRequired": "",
    }
    d60_scope = next(item for item in scopes if item["code"] == "D60")
    assert d60_scope["category"] == "expert"
    assert d60_scope["expertOnly"] is True
    assert d60_scope["timeAccuracyRequired"] == "exact"
    assert d60_scope["methodId"] == "varga.d60.parashara_shashtyamsha.v1"

    d3_response = public_client.get(f"/api/dev/d1-workbench-check?token=dev-token&chart_id={profile.id}&scope=d3")
    assert d3_response.status_code == 200
    assert d3_response.data["scopeId"] == "D3"
    assert d3_response.data["houseCount"] == 12
    assert d3_response.data["rashiCount"] == 12
    assert d3_response.data["grahaCount"] == 1
    assert d3_response.data["specialPointCount"] == 1
    assert d3_response.data["supportedScopes"] == ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D30", "D60"]

    d7_response = public_client.get(f"/api/dev/d1-workbench-check?token=dev-token&chart_id={profile.id}&scope=d7")
    assert d7_response.status_code == 200
    assert d7_response.data["scopeId"] == "D7"
    assert d7_response.data["houseCount"] == 12
    assert d7_response.data["rashiCount"] == 12
    assert d7_response.data["grahaCount"] == 1
    assert d7_response.data["specialPointCount"] == 1
    assert d7_response.data["supportedScopes"] == ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D30", "D60"]

    for scope, scope_id in (("d2", "D2"), ("d4", "D4"), ("d16", "D16"), ("d20", "D20"), ("d24", "D24"), ("d30", "D30")):
        scope_response = public_client.get(f"/api/dev/d1-workbench-check?token=dev-token&chart_id={profile.id}&scope={scope}")
        assert scope_response.status_code == 200
        assert scope_response.data["scopeId"] == scope_id
        assert scope_response.data["houseCount"] == 12
        assert scope_response.data["rashiCount"] == 12
        assert scope_response.data["grahaCount"] == 1
        assert scope_response.data["specialPointCount"] == 1
        assert scope_response.data["supportedScopes"] == ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D30", "D60"]
        assert scope_response.data["warnings"] == []
        if scope_id == "D30":
            assert scope_response.data["methodId"] == "varga.d30.parashara_unequal.v1"
            assert scope_response.data["methodVersion"] == "1"

    d9_response = public_client.get(f"/api/dev/d1-workbench-check?token=dev-token&chart_id={profile.id}&scope=d9")

    assert d9_response.status_code == 200
    assert d9_response.data["schemaVersion"] == "varga-workbench-check.v1"
    assert d9_response.data["scopeId"] == "D9"
    assert d9_response.data["houseCount"] == 12
    assert d9_response.data["grahaCount"] == 1
    assert d9_response.data["specialPointCount"] == 1
    assert d9_response.data["chartObjectCount"] == 2
    assert d9_response.data["tabIds"] == ["overview", "grahas", "houses"]
    assert d9_response.data["forbiddenScopesPresent"] == {"D60": False, "AI": False, "rawEvidence": False}
    assert d9_response.data["warnings"] == []
    alias_response = public_client.get(f"/api/dev/varga-workbench-check?token=dev-token&chart_id={profile.id}&scope=d9")
    assert alias_response.status_code == 200
    assert alias_response.data == d9_response.data
    d12_response = public_client.get(f"/api/dev/varga-workbench-check?token=dev-token&chart_id={profile.id}&scope=d12")
    assert d12_response.status_code == 200
    assert d12_response.data["scopeId"] == "D12"
    assert d12_response.data["warnings"] == []
    d60_response = public_client.get(f"/api/dev/varga-workbench-check?token=dev-token&chart_id={profile.id}&scope=d60")
    assert d60_response.status_code == 200
    assert d60_response.data["scopeId"] == "D60"
    assert [warning["code"] for warning in d60_response.data["warnings"]] == ["d60_birth_time_accuracy"]
    assert "birth_date" not in response.data
    assert "birth" not in response.data



@pytest.mark.django_db
@override_settings(ENABLE_DEV_LOGIN=True, DEV_LOGIN_TOKEN="dev-token")
def test_dev_varga_workbench_check_blocks_d60_without_exact_birth_time(user):
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Approximate D60 check",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "birth_time_accuracy": "approximate",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    profile = BirthProfile.objects.select_related("place").get(id=create_response.data["profile"]["id"])
    ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
        status=ChartCalculation.Status.COMPLETE,
        result={"vargas": {}, "birth": {"time_accuracy": "approximate"}},
    )

    public_client = APIClient()
    response = public_client.get(f"/api/dev/varga-workbench-check?token=dev-token&chart_id={profile.id}&scope=d60")

    assert response.status_code == 400
    d1_response = public_client.get(f"/api/dev/varga-workbench-check?token=dev-token&chart_id={profile.id}&scope=d1")
    assert d1_response.status_code == 200
    assert "D60" not in d1_response.data["supportedScopes"]
    assert "D60" not in d1_response.data["expertOnlyScopes"]
    assert d1_response.data["accuracyGates"]["D60"]["status"] == "blocked"
    assert d1_response.data["warnings"] == []

@pytest.mark.django_db
@override_settings(ENABLE_DEV_LOGIN=False, DEV_LOGIN_TOKEN="dev-token")
def test_dev_d1_workbench_check_hidden_when_disabled(user):
    response = APIClient().get("/api/dev/d1-workbench-check?token=dev-token&chart_id=1")

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(ENABLE_DEV_LOGIN=True, DEV_LOGIN_TOKEN="dev-token")
def test_dev_d1_workbench_check_rejects_bad_token(user):
    response = APIClient().get("/api/dev/d1-workbench-check?token=bad&chart_id=1")

    assert response.status_code == 403

@pytest.mark.django_db
@override_settings(ENABLE_DEV_LOGIN=True, DEV_LOGIN_TOKEN="dev-token")
def test_dev_dasha_workbench_check_returns_vimshottari_contract(user, monkeypatch):
    monkeypatch.setenv("JYOTISH_DEPLOY_COMMIT", "test-dasha-commit")
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Dasha external check",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    profile = BirthProfile.objects.select_related("place").get(id=create_response.data["profile"]["id"])
    ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
        status=ChartCalculation.Status.COMPLETE,
        result={
            "dashas": {
                "vimshottari": {
                    "system": "vimshottari",
                    "level": "mahadasha",
                    "year_length_days": 365.25,
                    "mahadashas": [
                        {"lord": "Ketu", "level": 1, "starts_at": "1990-08-15T10:24:00+00:00", "ends_at": "1995-01-01T00:00:00+00:00", "duration_years": 4.4, "sequence_index": 0, "boundary_policy": "start_inclusive_end_exclusive", "antardashas": [{"lord": "Ketu", "parent_lord": "Ketu", "level": 2, "starts_at": "1990-08-15T10:24:00+00:00", "ends_at": "1991-01-01T00:00:00+00:00", "duration_years": 0.38, "sequence_index": 0}, {"lord": "Shukra", "parent_lord": "Ketu", "level": 2, "starts_at": "1991-01-01T00:00:00+00:00", "ends_at": "1991-10-01T00:00:00+00:00", "duration_years": 0.73, "sequence_index": 1}]},
                        {"lord": "Shukra", "level": 1, "starts_at": "1995-01-01T00:00:00+00:00", "ends_at": "2015-01-01T00:00:00+00:00", "duration_years": 20.0, "sequence_index": 1},
                    ],
                }
            },
            "birth": {},
        },
    )

    response = APIClient().get(f"/api/dev/dasha-workbench-check?token=dev-token&chart_id={profile.id}")

    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    assert response.data["status"] == "ok"
    assert response.data["schemaVersion"] == "dasha-workbench-check.v3"
    assert response.data["deployCommit"] == "test-dasha-commit"
    assert response.data["supportedViews"] == ["tree", "table", "timeline"]
    assert response.data["defaultView"] == "tree"
    assert response.data["supportsControlDate"] is True
    assert response.data["supportsGoToCurrentPeriod"] is True
    assert response.data["collapsibleLevels"] == ["mahadasha", "antardasha", "pratyantardasha"]
    assert response.data["boundaryDisplayPolicy"] == "start_inclusive_end_exclusive"
    assert response.data["chartId"] == profile.id
    assert response.data["hasCalculation"] is True
    assert response.data["supportedSystems"] == ["vimshottari"]
    assert response.data["activeSystem"] == "vimshottari"
    assert response.data["methodId"] == "dasha.vimshottari.parashara.v1"
    assert response.data["methodVersion"] == "1"
    assert response.data["sourceAnchor"] == "BPHS 46.2-16"
    assert response.data["boundaryPolicy"] == "start_inclusive_end_exclusive"
    assert response.data["yearLengthDays"] == 365.25
    assert response.data["mahadashaCount"] == 2
    assert response.data["antardashaCount"] == 2
    assert response.data["currentMahadashaLord"] == "Ketu"
    assert response.data["currentAntardashaLord"] == "Ketu"
    assert response.data["currentAntardashaParentLord"] == "Ketu"
    assert response.data["pratyantardashaCount"] == 9
    assert response.data["currentPratyantardashaLord"] == "Ketu"
    assert response.data["currentPratyantardashaParentLord"] == "Ketu"
    assert response.data["entityInspectorCount"] == 1
    assert response.data["supportedModes"] == ["novice", "astrologer"]
    assert response.data["forbiddenScopesPresent"] == {"AI": False, "rawEvidence": False}


@pytest.mark.django_db
@override_settings(ENABLE_DEV_LOGIN=True, DEV_LOGIN_TOKEN="dev-token")
def test_dev_dasha_workbench_check_derives_antardashas_for_legacy_payload(user):
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Legacy dasha check",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    profile = BirthProfile.objects.select_related("place").get(id=create_response.data["profile"]["id"])
    ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
        status=ChartCalculation.Status.COMPLETE,
        result={
            "dashas": {
                "vimshottari": {
                    "system": "vimshottari",
                    "level": "mahadasha",
                    "year_length_days": 365.25,
                    "mahadashas": [
                        {"lord": "Ketu", "level": 1, "starts_at": "2000-01-01T00:00:00+00:00", "ends_at": "2006-12-31T18:00:00+00:00", "duration_years": 7.0, "sequence_index": 0},
                    ],
                }
            },
            "birth": {},
        },
    )

    response = APIClient().get(f"/api/dev/dasha-workbench-check?token=dev-token&chart_id={profile.id}")

    assert response.status_code == 200
    assert response.data["schemaVersion"] == "dasha-workbench-check.v3"
    assert response.data["supportedViews"] == ["tree", "table", "timeline"]
    assert response.data["defaultView"] == "tree"
    assert response.data["supportsControlDate"] is True
    assert response.data["supportsGoToCurrentPeriod"] is True
    assert response.data["collapsibleLevels"] == ["mahadasha", "antardasha", "pratyantardasha"]
    assert response.data["boundaryDisplayPolicy"] == "start_inclusive_end_exclusive"
    assert response.data["antardashaCount"] == 9
    assert response.data["currentAntardashaLord"] == "Ketu"
    assert response.data["currentAntardashaParentLord"] == "Ketu"
    assert response.data["pratyantardashaCount"] == 9
    assert response.data["currentPratyantardashaLord"] == "Ketu"
    assert response.data["currentPratyantardashaParentLord"] == "Ketu"

@pytest.mark.django_db
def test_transit_workbench_requires_authentication():
    response = APIClient().get("/api/charts/1/transit-workbench")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_transit_workbench_rejects_other_users_chart(user):
    other_user = get_user_model().objects.create_user(username="transit-other", password="strong-pass-108")
    owner_client = APIClient()
    owner_client.force_authenticate(user=user)
    response = owner_client.post(
        "/api/charts/profiles",
        {"display_name": "Transit private", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    )
    profile_id = response.data["profile"]["id"]
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)

    response = other_client.get(f"/api/charts/{profile_id}/transit-workbench")

    assert response.status_code == 404


@pytest.mark.django_db
def test_transit_workbench_validates_query(user):
    client = APIClient()
    client.force_authenticate(user=user)
    profile = client.post(
        "/api/charts/profiles",
        {"display_name": "Transit validation", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]

    assert client.get(f"/api/charts/{profile['id']}/transit-workbench?at=not-date").status_code == 400
    assert client.get(f"/api/charts/{profile['id']}/transit-workbench?timezone=Bad/Zone").status_code == 400
    assert client.get(f"/api/charts/{profile['id']}/transit-workbench?latitude=91").status_code == 400
    assert client.get(f"/api/charts/{profile['id']}/transit-workbench?longitude=181").status_code == 400
    assert client.get(f"/api/charts/{profile['id']}/transit-workbench?scope=d9").status_code == 400




@pytest.mark.django_db
def test_transit_workbench_builds_chart_for_control_moment(user, monkeypatch):
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Transit calculation contract",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
            "calculation_model": "drik_siddhanta",
        },
        format="json",
    )
    profile_id = create_response.data["profile"]["id"]
    seen_inputs = []

    def fake_build_birth_chart(data):
        seen_inputs.append(data)
        assert data["birth_date"] == "2026-06-20"
        assert data["birth_time"] == "12:30:00"
        assert data["birth_time_accuracy"] == "exact"
        assert data["timezone"] == "Europe/Berlin"
        assert data["latitude"] == 52.5
        assert data["longitude"] == 13.4
        bodies = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]
        return {
            "ascendant": {"body": "Lagna", "longitude": 90.0, "rashi": "Cancer", "rashi_index": 3, "nakshatra": "Pushya", "pada": 1},
            "grahas": [
                {"body": body, "longitude": 10.0 + index, "rashi": "Aries", "rashi_index": 0, "nakshatra": "Ashwini", "pada": 1}
                for index, body in enumerate(bodies)
            ],
            "houses": [{"house": item, "rashi": f"Rashi {item}", "rashi_index": item - 1} for item in range(1, 13)],
            "settings": {"ayanamsa": "lahiri", "node_type": "true", "calculation_model": "drik_siddhanta"},
        }

    monkeypatch.setattr("apps.charts.views.build_birth_chart", fake_build_birth_chart)

    response = client.get(
        f"/api/charts/{profile_id}/transit-workbench"
        "?at=2026-06-20T12:30:00&timezone=Europe/Berlin&latitude=52.5&longitude=13.4&location=Berlin"
    )

    assert response.status_code == 200
    assert len(seen_inputs) == 1
    assert response.data["schemaVersion"] == "transit-workbench.v3"
    assert response.data["transitMoment"] == {"isoDateTime": "2026-06-20T12:30:00+02:00", "timezone": "Europe/Berlin"}
    assert response.data["location"] == {"label": "Berlin", "latitude": 52.5, "longitude": 13.4}
    assert response.data["method"]["methodId"] == "transit.d1.drik.v1"
    assert response.data["method"]["methodVersion"] == "1"
    assert response.data["method"]["positionContext"] == "transit"
    assert response.data["calculationContract"]["usesNatalOverlay"] is True
    assert response.data["calculationContract"]["usesAspects"] is True
    assert response.data["grahas"][0]["objectRef"] == "transit:graha.SU"
    assert response.data["grahas"][0]["context"] == "transit"
    assert response.data["specialPoints"][0]["objectRef"] == "transit:point.LAGNA"
    assert response.data["overlay"]["supportedViews"] == ["transit_only", "overlay", "side_by_side"]
    assert response.data["overlay"]["housesRelativeTo"] == "natal"
    assert response.data["overlay"]["natalObjectCount"] == 0
    assert response.data["overlay"]["transitObjectCount"] == 10
    assert response.data["overlay"]["aspects"] is True
    assert response.data["overlay"]["ai"] is False
    assert response.data["capabilities"]["ai"] is False
    assert "raw" not in response.data


@pytest.mark.django_db
def test_transit_workbench_contract_matches_snapshot(user, monkeypatch):
    client = APIClient()
    client.force_authenticate(user=user)
    profile_id = client.post(
        "/api/charts/profiles",
        {"display_name": "Transit snapshot", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]["id"]

    def fake_build_birth_chart(data):
        bodies = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]
        return {
            "ascendant": {"body": "Lagna", "longitude": 90.0, "rashi": "Cancer", "rashi_index": 3},
            "grahas": [{"body": body, "longitude": 10.0, "rashi": "Aries", "rashi_index": 0} for body in bodies],
            "houses": [{"house": item, "rashi": f"Rashi {item}", "rashi_index": item - 1} for item in range(1, 13)],
            "settings": {"ayanamsa": "lahiri", "node_type": "true", "calculation_model": "drik_siddhanta"},
        }

    monkeypatch.setattr("apps.charts.views.build_birth_chart", fake_build_birth_chart)
    response = client.get(f"/api/charts/{profile_id}/transit-workbench?at=2026-06-20T12:30:00&timezone=UTC")

    assert response.status_code == 200
    summary = {
        "schemaVersion": response.data["schemaVersion"],
        "scopeId": response.data["scopeId"],
        "method": response.data["method"],
        "calculationContract": response.data["calculationContract"],
        "grahaObjectRefs": [item["objectRef"] for item in response.data["grahas"]],
        "specialPointObjectRefs": [item["objectRef"] for item in response.data["specialPoints"]],
        "capabilityFlags": {key: response.data["capabilities"][key] for key in ["natalOverlay", "aspects", "ashtakavarga", "sadeSati", "ai"]},
    }
    expected = json.loads(Path("backend/apps/charts/fixtures/transit_workbench_contract_v1.json").read_text(encoding="utf-8"))
    assert summary == expected

@pytest.mark.django_db
def test_transit_overlay_keeps_natal_and_transit_contexts_separate(user, monkeypatch):
    client = APIClient()
    client.force_authenticate(user=user)
    profile_id = client.post(
        "/api/charts/profiles",
        {"display_name": "Transit overlay", "birth_date": "1990-08-15", "birth_time": "10:24", "place_name": "Vrindavan"},
        format="json",
    ).data["profile"]["id"]
    profile = BirthProfile.objects.select_related("place").get(id=profile_id)
    bodies = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]
    ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
        status=ChartCalculation.Status.COMPLETE,
        result={
            "ascendant": {"body": "Lagna", "longitude": 90.0, "rashi": "Cancer", "rashi_index": 3},
            "grahas": [{"body": body, "longitude": 20.0 + index, "rashi": "Aries", "rashi_index": 0} for index, body in enumerate(bodies)],
            "houses": [{"house": item, "rashi": f"Natal Rashi {item}", "rashi_index": item - 1} for item in range(1, 13)],
            "settings": {"ayanamsa": "lahiri", "node_type": "true", "calculation_model": "drik_siddhanta"},
        },
    )

    def fake_build_birth_chart(data):
        sun_longitude = 100.0 if data["birth_date"] == "2026-06-20" else 130.0
        return {
            "ascendant": {"body": "Lagna", "longitude": 180.0, "rashi": "Libra", "rashi_index": 6},
            "grahas": [
                {"body": body, "longitude": sun_longitude + index, "rashi": "Leo", "rashi_index": 4}
                for index, body in enumerate(bodies)
            ],
            "houses": [{"house": item, "rashi": f"Transit Rashi {item}", "rashi_index": item - 1} for item in range(1, 13)],
            "settings": {"ayanamsa": "lahiri", "node_type": "true", "calculation_model": "drik_siddhanta"},
        }

    monkeypatch.setattr("apps.charts.views.build_birth_chart", fake_build_birth_chart)
    first = client.get(f"/api/charts/{profile_id}/transit-workbench?at=2026-06-20T12:30:00&timezone=UTC")
    second = client.get(f"/api/charts/{profile_id}/transit-workbench?at=2026-06-21T12:30:00&timezone=UTC")

    assert first.status_code == 200
    assert first.data["overlay"]["natalObjectRefs"][0] == "natal:point.LAGNA"
    assert first.data["overlay"]["transitObjectRefs"][0] == "transit:point.LAGNA"
    assert "graha.TRANSIT_SU" not in json.dumps(first.data)
    assert first.data["natal"]["grahas"][0]["objectRef"] == "natal:graha.SU"
    assert first.data["grahas"][0]["objectRef"] == "transit:graha.SU"
    assert first.data["natal"]["grahas"][0]["longitude"] == second.data["natal"]["grahas"][0]["longitude"]
    assert first.data["grahas"][0]["longitude"] != second.data["grahas"][0]["longitude"]
    assert first.data["overlay"]["natalObjectCount"] == 10
    assert first.data["overlay"]["transitObjectCount"] == 10
    assert first.data["aspectLayer"]["methodId"] == "aspect.graha_drishti.parashara.v1"
    assert first.data["aspectLayer"]["sourceContext"] == "transit"
    assert first.data["aspectLayer"]["targetContext"] == "natal"
    assert first.data["aspectLayer"]["enabledByDefault"] is False
    assert first.data["aspectLayer"]["availableInModes"] == ["astrologer"]
    assert first.data["aspectLayer"]["usesDegreeOrbs"] is False
    assert first.data["aspectLayer"]["treatsConjunctionAsAspect"] is False
    assert first.data["aspectLayer"]["includesRahuKetu"] is False
    assert first.data["aspectLayer"]["aspectCount"] > 0
    assert first.data["aspectLayer"]["sampleRefs"][0]["sourceEntityRef"].startswith("transit:graha.")
    assert first.data["aspectLayer"]["sampleRefs"][0]["targetEntityRef"].startswith("natal:")
    assert not any(item["sourceEntityRef"] in {"transit:graha.RA", "transit:graha.KE"} for item in first.data["aspectLayer"]["sampleRefs"])
    assert first.data["capabilities"]["aspects"] is True
    assert first.data["entityInspectorCount"] == 1


@pytest.mark.django_db
@override_settings(ENABLE_DEV_LOGIN=True, DEV_LOGIN_TOKEN="dev-token")
def test_dev_transit_workbench_check_returns_foundation_contract(user, monkeypatch):
    monkeypatch.setenv("JYOTISH_DEPLOY_COMMIT", "transit-test-commit")
    client = APIClient()
    client.force_authenticate(user=user)
    create_response = client.post(
        "/api/charts/profiles",
        {
            "display_name": "Transit external check",
            "birth_date": "1990-08-15",
            "birth_time": "10:24",
            "place_name": "Vrindavan",
        },
        format="json",
    )
    profile = BirthProfile.objects.select_related("place").get(id=create_response.data["profile"]["id"])
    ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
        status=ChartCalculation.Status.COMPLETE,
        result={
            "ascendant": {"body": "Lagna", "longitude": 90.0, "rashi": "Cancer", "rashi_index": 3, "nakshatra": "Pushya", "pada": 1},
            "grahas": [
                {"body": body, "longitude": 120.0 + index, "rashi": "Leo", "rashi_index": 4, "nakshatra": "Magha", "pada": 1}
                for index, body in enumerate(["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"])
            ],
            "houses": [{"house": item, "rashi": "Cancer", "rashi_index": item - 1} for item in range(1, 13)],
            "settings": {"ayanamsa": "lahiri", "node_type": "true", "calculation_model": "drik_siddhanta"},
            "birth": {},
            "place": {},
        },
    )

    response = APIClient().get(f"/api/dev/transit-workbench-check?token=dev-token&chart_id={profile.id}")

    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    assert response.data["status"] == "ok"
    assert response.data["schemaVersion"] == "transit-workbench-check.v6"
    assert response.data["deployCommit"] == "transit-test-commit"
    assert response.data["scopeId"] == "D1"
    assert response.data["methodId"] == "transit.d1.drik.v1"
    assert response.data["methodVersion"] == "1"
    assert response.data["boundaryPolicy"] == "instant_exact"
    assert response.data["positionContext"] == "transit"
    assert response.data["objectRefPrefix"] == "transit:"
    assert response.data["calculationContract"]["usesNatalOverlay"] is True
    assert response.data["calculationContract"]["usesAi"] is False
    assert response.data["coordinateGolden"]["schemaVersion"] == "transit-coordinate-golden.v1"
    assert response.data["coordinateGolden"]["caseCount"] == 3
    assert response.data["coordinateGolden"]["independentOfBuildBirthChart"] is True
    assert response.data["coordinateGolden"]["utcMoments"] == [
        "2026-06-20T08:30:00+00:00",
        "1998-04-30T07:45:00+00:00",
        "2026-01-15T17:30:00+00:00",
    ]
    assert response.data["hasCalculation"] is True
    assert response.data["houseCount"] == 12
    assert response.data["rashiCount"] == 12
    assert response.data["grahaCount"] == 9
    assert response.data["specialPointCount"] == 1
    assert response.data["chartObjectCount"] == 10
    assert response.data["supportedStyles"] == ["north", "south"]
    assert response.data["supportedModes"] == ["novice", "astrologer"]
    assert response.data["tabIds"] == ["overview", "grahas", "houses", "nakshatras"]
    assert response.data["entityInspectorCount"] == 1
    assert response.data["supportsNatalOverlay"] is True
    assert response.data["supportedViews"] == ["transit_only", "overlay", "side_by_side"]
    assert response.data["natalObjectCount"] == 10
    assert response.data["transitObjectCount"] == 10
    assert response.data["overlayContract"]["housesRelativeTo"] == "natal"
    assert response.data["overlayContract"]["legendRequired"] is True
    assert response.data["overlayContract"]["aspects"] is True
    assert response.data["overlayContract"]["natalObjectRefs"][0] == "natal:point.LAGNA"
    assert response.data["overlayContract"]["transitObjectRefs"][0] == "transit:point.LAGNA"
    assert response.data["supportsControlDate"] is True
    assert response.data["supportsControlTime"] is True
    assert response.data["supportsTimezone"] is True
    assert response.data["supportsLocation"] is True
    assert response.data["supportsNowAction"] is True
    assert response.data["grahaDrishtiContract"]["methodId"] == "aspect.graha_drishti.parashara.v1"
    assert response.data["grahaDrishtiContract"]["methodVersion"] == 1
    assert response.data["grahaDrishtiContract"]["sourceContext"] == "transit"
    assert response.data["grahaDrishtiContract"]["targetContext"] == "natal"
    assert response.data["grahaDrishtiContract"]["uiCapability"] is True
    assert response.data["grahaDrishtiContract"]["usesDegreeOrbs"] is False
    assert response.data["grahaDrishtiContract"]["treatsConjunctionAsAspect"] is False
    assert response.data["grahaDrishtiContract"]["includesRahuKetu"] is False
    assert response.data["grahaDrishtiContract"]["enabledByDefault"] is False
    assert response.data["grahaDrishtiContract"]["availableInModes"] == ["astrologer"]
    assert response.data["grahaDrishtiContract"]["sourceStatus"] == "verified"
    assert response.data["grahaDrishtiContract"]["sourceRuleIds"] == [
        "bphs.aspect.graha_drishti.general_7th",
        "bphs.aspect.graha_drishti.mars_special",
        "bphs.aspect.graha_drishti.jupiter_special",
        "bphs.aspect.graha_drishti.saturn_special",
    ]
    assert response.data["grahaDrishtiContract"]["aspectCount"] > 0
    assert response.data["grahaDrishtiContract"]["sampleRefs"][0]["sourceEntityRef"].startswith("transit:graha.")
    assert response.data["grahaDrishtiContract"]["sampleRefs"][0]["targetEntityRef"].startswith("natal:")
    assert response.data["grahaDrishtiContract"]["sampleRefs"][0]["sourceRuleIds"]
    assert response.data["rashiDrishtiContract"]["methodId"] == "aspect.rashi_drishti.parashara.v1"
    assert response.data["rashiDrishtiContract"]["methodVersion"] == 1
    assert response.data["rashiDrishtiContract"]["sourceContext"] == "transit"
    assert response.data["rashiDrishtiContract"]["targetContext"] == "natal"
    assert response.data["rashiDrishtiContract"]["sourceStatus"] == "verified"
    assert response.data["rashiDrishtiContract"]["sourceRuleIds"] == [
        "bphs.aspect.rashi_drishti.movable_to_fixed",
        "bphs.aspect.rashi_drishti.fixed_to_movable",
        "bphs.aspect.rashi_drishti.dual_to_dual",
        "bphs.aspect.rashi_drishti.graha_participation",
    ]
    assert response.data["rashiDrishtiContract"]["uiCapability"] is False
    assert response.data["rashiDrishtiContract"]["enabledByDefault"] is False
    assert response.data["rashiDrishtiContract"]["usesDegreeOrbs"] is False
    assert response.data["rashiDrishtiContract"]["treatsConjunctionAsAspect"] is False
    assert response.data["rashiDrishtiContract"]["aspectCount"] > 0
    assert response.data["rashiDrishtiContract"]["sampleRefs"][0]["sourceEntityRef"].startswith("transit:rashi.")
    assert response.data["rashiDrishtiContract"]["sampleRefs"][0]["targetEntityRef"].startswith("natal:")
    assert response.data["rashiDrishtiContract"]["sampleRefs"][0]["sourceRuleIds"]
    assert response.data["capabilities"] == {
        "natalOverlay": True,
        "aspects": True,
        "ashtakavarga": False,
        "sadeSati": False,
        "ai": False,
        "rawEvidence": False,
    }
    assert "birth_date" not in response.data
    assert "raw" not in response.data


@pytest.mark.django_db
@override_settings(ENABLE_DEV_LOGIN=True, DEV_LOGIN_TOKEN="dev-token")
def test_dev_transit_workbench_check_rejects_bad_token():
    response = APIClient().get("/api/dev/transit-workbench-check?token=bad&chart_id=1")

    assert response.status_code == 403
