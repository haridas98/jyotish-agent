from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from apps.places.catalog import PlaceCandidate
from apps.places.geocoding import geocode_places, geonamescache_places


def test_geonamescache_places_returns_offline_city_with_timezone():
    results = geonamescache_places("London", limit=3)

    assert results[0].name == "London"
    assert results[0].country_code == "GB"
    assert results[0].timezone == "Europe/London"
    assert results[0].latitude
    assert results[0].longitude


def test_geonamescache_places_accepts_full_city_country_label():
    results = geonamescache_places("Shymkent, Kazakhstan, KZ", limit=3)

    assert results[0].name == "Shymkent"
    assert results[0].country_code == "KZ"
    assert results[0].timezone == "Asia/Almaty"


def test_geocode_places_maps_nominatim_result_to_timezone_candidate():
    def fake_fetch(query: str, limit: int):
        assert query == "London"
        assert limit == 5
        return [
            {
                "osm_type": "relation",
                "osm_id": 65606,
                "display_name": "London, Greater London, England, United Kingdom",
                "lat": "51.5074456",
                "lon": "-0.1277653",
                "address": {
                    "city": "London",
                    "state": "England",
                    "country_code": "gb",
                },
            }
        ]

    results = geocode_places(
        "London",
        limit=5,
        fetch_json=fake_fetch,
        timezone_resolver=lambda lat, lon: "Europe/London",
    )

    assert results[0].id == "osm:relation:65606"
    assert results[0].name == "London"
    assert results[0].admin_name == "England"
    assert results[0].country_code == "GB"
    assert results[0].latitude == 51.5074456
    assert results[0].longitude == -0.1277653
    assert results[0].timezone == "Europe/London"


def test_places_search_api_uses_geocoder_when_catalog_misses(monkeypatch):
    cache.clear()
    monkeypatch.setattr(
        "apps.places.views.geocode_places",
        lambda query, limit=10: [
            PlaceCandidate(
                id="osm:relation:65606",
                name="London",
                admin_name="England",
                country_code="GB",
                latitude=51.5074456,
                longitude=-0.1277653,
                timezone="Europe/London",
            )
        ],
    )

    response = APIClient().get(reverse("places-search"), {"q": "London"})

    assert response.status_code == 200
    assert response.data["items"][0]["label"] == "London, England, GB"
    assert response.data["items"][0]["timezone"] == "Europe/London"
    assert response["X-Jyotish-Cache"] == "miss"


def test_places_search_api_caches_geocoder_results(monkeypatch):
    cache.clear()
    calls = {"count": 0}

    def fake_geocode(query, limit=10):
        calls["count"] += 1
        return [
            PlaceCandidate(
                id="osm:relation:65606",
                name="London",
                admin_name="England",
                country_code="GB",
                latitude=51.5074456,
                longitude=-0.1277653,
                timezone="Europe/London",
            )
        ]

    monkeypatch.setattr("apps.places.views.geocode_places", fake_geocode)

    client = APIClient()
    first = client.get(reverse("places-search"), {"q": "London"})
    second = client.get(reverse("places-search"), {"q": " London "})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first["X-Jyotish-Cache"] == "miss"
    assert second["X-Jyotish-Cache"] == "hit"
    assert calls["count"] == 1
    assert second.data["items"][0]["timezone"] == "Europe/London"
