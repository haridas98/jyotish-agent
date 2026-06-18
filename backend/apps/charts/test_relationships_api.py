import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import BirthProfile, ChartRelationship, Place


@pytest.fixture
def user():
    return get_user_model().objects.create_user(username="rel-user", password="strong-pass-108")


@pytest.fixture
def other_user():
    return get_user_model().objects.create_user(username="other-rel-user", password="strong-pass-108")


@pytest.fixture
def client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def place():
    return Place.objects.create(
        external_id="test-place",
        name="Sterlitamak",
        country_code="RU",
        latitude="53.630400",
        longitude="55.930800",
        timezone_name="Asia/Yekaterinburg",
        metadata={"label": "Sterlitamak, RU"},
    )


def make_profile(user, place, name):
    return BirthProfile.objects.create(
        user=user,
        display_name=name,
        birth_date="1990-05-14",
        birth_time="07:15",
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        gender=BirthProfile.Gender.UNKNOWN,
        place=place,
        timezone_name=place.timezone_name,
    )


@pytest.mark.django_db
def test_relationship_create_symmetric_and_list_for_owner(client, user, place):
    first = make_profile(user, place, "REL-A")
    second = make_profile(user, place, "REL-B")

    response = client.post(
        "/api/relationships",
        {
            "chart_a_id": first.id,
            "chart_b_id": second.id,
            "relationship_type_id": "business_partners",
            "role_a_id": "business_partner",
            "role_b_id": "business_partner",
            "notes": "working context",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["relationship"]["relationship_type_id"] == "business_partners"
    assert response.data["relationship"]["role_a_id"] == "business_partner"
    assert response.data["relationship"]["role_b_id"] == "business_partner"
    assert response.data["relationship"]["pair_key"] == f"{min(first.id, second.id)}:{max(first.id, second.id)}"
    assert "recipe" not in response.data["relationship"]
    assert "ownerUserId" not in response.data["relationship"]

    list_response = client.get("/api/relationships")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.data["relationships"]] == [response.data["relationship"]["id"]]


@pytest.mark.django_db
def test_relationship_create_asymmetric_preserves_direction(client, user, place):
    father = make_profile(user, place, "Father")
    child = make_profile(user, place, "Child")

    response = client.post(
        "/api/relationships",
        {
            "chart_a_id": father.id,
            "chart_b_id": child.id,
            "relationship_type_id": "father_child",
            "role_a_id": "father",
            "role_b_id": "child",
        },
        format="json",
    )

    assert response.status_code == 201
    relationship = ChartRelationship.objects.get(id=response.data["relationship"]["id"])
    assert relationship.chart_a_id == father.id
    assert relationship.chart_b_id == child.id
    assert relationship.role_a_id == "father"
    assert relationship.role_b_id == "child"


@pytest.mark.django_db
def test_relationship_rejects_self_foreign_invalid_and_duplicates(client, user, other_user, place):
    first = make_profile(user, place, "A")
    second = make_profile(user, place, "B")
    foreign = make_profile(other_user, place, "Foreign")

    assert client.post(
        "/api/relationships",
        {
            "chart_a_id": first.id,
            "chart_b_id": first.id,
            "relationship_type_id": "business_partners",
            "role_a_id": "business_partner",
            "role_b_id": "business_partner",
        },
        format="json",
    ).status_code == 400

    assert client.post(
        "/api/relationships",
        {
            "chart_a_id": first.id,
            "chart_b_id": foreign.id,
            "relationship_type_id": "business_partners",
            "role_a_id": "business_partner",
            "role_b_id": "business_partner",
        },
        format="json",
    ).status_code == 404

    assert client.post(
        "/api/relationships",
        {
            "chart_a_id": first.id,
            "chart_b_id": second.id,
            "relationship_type_id": "father_child",
            "role_a_id": "mother",
            "role_b_id": "child",
        },
        format="json",
    ).status_code == 400

    created = client.post(
        "/api/relationships",
        {
            "chart_a_id": first.id,
            "chart_b_id": second.id,
            "relationship_type_id": "business_partners",
            "role_a_id": "business_partner",
            "role_b_id": "business_partner",
        },
        format="json",
    )
    assert created.status_code == 201

    duplicate = client.post(
        "/api/relationships",
        {
            "chart_a_id": second.id,
            "chart_b_id": first.id,
            "relationship_type_id": "business_partners",
            "role_a_id": "business_partner",
            "role_b_id": "business_partner",
        },
        format="json",
    )
    assert duplicate.status_code == 409

    different_type = client.post(
        "/api/relationships",
        {
            "chart_a_id": second.id,
            "chart_b_id": first.id,
            "relationship_type_id": "spouses",
            "role_a_id": "spouse",
            "role_b_id": "spouse",
        },
        format="json",
    )
    assert different_type.status_code == 201


@pytest.mark.django_db
def test_relationship_patch_delete_and_profile_delete_cascade(client, user, place):
    first = make_profile(user, place, "A")
    second = make_profile(user, place, "B")
    response = client.post(
        "/api/relationships",
        {
            "chart_a_id": first.id,
            "chart_b_id": second.id,
            "relationship_type_id": "father_child",
            "role_a_id": "father",
            "role_b_id": "child",
            "notes": "old",
        },
        format="json",
    )
    relationship_id = response.data["relationship"]["id"]

    patch_response = client.patch(
        f"/api/relationships/{relationship_id}",
        {
            "chart_a_id": second.id,
            "chart_b_id": first.id,
            "relationship_type_id": "mother_child",
            "role_a_id": "mother",
            "role_b_id": "child",
            "notes": "updated",
        },
        format="json",
    )
    assert patch_response.status_code == 200
    assert patch_response.data["relationship"]["chart_a_id"] == second.id
    assert patch_response.data["relationship"]["role_a_id"] == "mother"
    assert patch_response.data["relationship"]["notes"] == "updated"

    read_response = client.get(f"/api/relationships/{relationship_id}")
    assert read_response.status_code == 200

    delete_response = client.delete(f"/api/relationships/{relationship_id}")
    assert delete_response.status_code == 204
    assert ChartRelationship.objects.filter(id=relationship_id).count() == 0

    cascade_response = client.post(
        "/api/relationships",
        {
            "chart_a_id": first.id,
            "chart_b_id": second.id,
            "relationship_type_id": "business_partners",
            "role_a_id": "business_partner",
            "role_b_id": "business_partner",
        },
        format="json",
    )
    assert cascade_response.status_code == 201
    first.delete()
    assert ChartRelationship.objects.count() == 0


@pytest.mark.django_db
def test_relationships_require_auth():
    response = APIClient().get("/api/relationships")
    assert response.status_code in {401, 403}
