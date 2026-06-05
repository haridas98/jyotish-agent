from django.urls import reverse
from rest_framework.test import APIClient

from apps.places.catalog import PlaceNotFound, resolve_place, search_places


def test_resolve_place_finds_vrindavan_by_alias():
    place = resolve_place("Vrindavan, Uttar Pradesh")

    assert place.name == "Vrindavan"
    assert place.country_code == "IN"
    assert place.timezone == "Asia/Kolkata"
    assert place.latitude == 27.565
    assert place.longitude == 77.6593


def test_search_places_matches_mayapur():
    results = search_places("maya")

    assert results[0].name == "Mayapur"
    assert results[0].timezone == "Asia/Kolkata"


def test_search_places_matches_cyrillic_aliases():
    assert search_places("Екатеринбург")[0].name == "Yekaterinburg"
    assert search_places("Москва")[0].name == "Moscow"
    assert search_places("Стерлитамак")[0].name == "Sterlitamak"
    assert search_places("Вриндаван")[0].name == "Vrindavan"
    assert search_places("Маяпур")[0].name == "Mayapur"


def test_resolve_place_finds_gelendzhik_full_label():
    place = resolve_place("Gelendzhik, Russia, RU")

    assert place.name == "Gelendzhik"
    assert place.country_code == "RU"
    assert place.timezone == "Europe/Moscow"
    assert place.latitude == 44.5622
    assert place.longitude == 38.0848


def test_resolve_place_raises_for_unknown_place():
    try:
        resolve_place("Unknown test place")
    except PlaceNotFound as exc:
        assert "Unknown test place" in str(exc)
    else:
        raise AssertionError("expected PlaceNotFound")


def test_places_search_api_returns_candidates():
    response = APIClient().get(reverse("places-search"), {"q": "vrind"})

    assert response.status_code == 200
    assert response.data["items"][0]["name"] == "Vrindavan"
