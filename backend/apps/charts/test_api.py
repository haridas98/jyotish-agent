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
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert create_response.status_code == 201
    profile_id = create_response.data["profile"]["id"]
    assert client.get("/api/charts").data["profiles"][0]["id"] == profile_id

    detail_response = client.get(f"/api/charts/{profile_id}")
    assert detail_response.status_code == 200
    assert detail_response.data["profile"]["display_name"] == "Client chart"

    update_response = client.patch(
        f"/api/charts/{profile_id}",
        {
            "display_name": "Updated client chart",
            "birth_date": "1990-08-16",
            "birth_time": "11:25",
            "birth_time_accuracy": "approximate",
            "place_name": "Mayapur",
        },
        format="json",
    )

    assert update_response.status_code == 200
    assert update_response.data["profile"]["display_name"] == "Updated client chart"
    assert update_response.data["profile"]["birth_date"] == "1990-08-16"
    assert update_response.data["profile"]["birth_time"] == "11:25"
    assert update_response.data["profile"]["birth_time_accuracy"] == "approximate"

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
