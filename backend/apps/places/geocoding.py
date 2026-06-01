from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .catalog import PlaceCandidate

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "jyotish-agent-dev/0.1"

FetchJson = Callable[[str, int], list[dict[str, Any]]]
TimezoneResolver = Callable[[float, float], str]


def geocode_places(
    query: str,
    limit: int = 5,
    fetch_json: FetchJson | None = None,
    timezone_resolver: TimezoneResolver | None = None,
) -> list[PlaceCandidate]:
    normalized = query.strip()
    if len(normalized) < 3:
        return []

    if fetch_json is None:
        offline_results = geonamescache_places(normalized, limit)
        if offline_results:
            return offline_results

    fetch_json = fetch_json or _fetch_nominatim
    timezone_resolver = timezone_resolver or timezone_name_for_coordinates
    candidates: list[PlaceCandidate] = []
    for item in fetch_json(normalized, limit):
        candidate = _candidate_from_nominatim(item, timezone_resolver)
        if candidate:
            candidates.append(candidate)
    return candidates


def geonamescache_places(query: str, limit: int = 5) -> list[PlaceCandidate]:
    normalized_query = _normalize(query)
    if len(normalized_query) < 3:
        return []

    countries = _geonames_countries()
    scored: list[tuple[int, int, PlaceCandidate]] = []
    for city in _geonames_cities().values():
        names = [city.get("name", ""), *city.get("alternatenames", [])]
        normalized_names = [_normalize(str(name)) for name in names if name]
        if normalized_query in normalized_names:
            score = 0
        elif any(name.startswith(normalized_query) for name in normalized_names):
            score = 1
        elif any(normalized_query in name for name in normalized_names):
            score = 2
        else:
            continue

        country_code = str(city.get("countrycode") or "")
        timezone = str(city.get("timezone") or "")
        if not country_code or not timezone:
            continue
        scored.append(
            (
                score,
                -int(city.get("population") or 0),
                PlaceCandidate(
                    id=f"geonames:{city['geonameid']}",
                    name=str(city["name"]),
                    admin_name=str(countries.get(country_code, {}).get("name") or ""),
                    country_code=country_code,
                    latitude=float(city["latitude"]),
                    longitude=float(city["longitude"]),
                    timezone=timezone,
                    aliases=tuple(str(name) for name in city.get("alternatenames", [])[:20]),
                ),
            )
        )

    scored.sort(key=lambda item: (item[0], item[1], item[2].name))
    return [candidate for _, _, candidate in scored[:limit]]


def timezone_name_for_coordinates(latitude: float, longitude: float) -> str:
    finder = _timezone_finder()
    timezone = finder.timezone_at(lat=latitude, lng=longitude)
    if timezone:
        return timezone
    certain_timezone = getattr(finder, "certain_timezone_at", None)
    if certain_timezone:
        return certain_timezone(lat=latitude, lng=longitude) or ""
    return ""


def _fetch_nominatim(query: str, limit: int) -> list[dict[str, Any]]:
    params = urlencode(
        {
            "q": query,
            "format": "jsonv2",
            "addressdetails": 1,
            "dedupe": 1,
            "limit": limit,
        }
    )
    request = Request(f"{NOMINATIM_URL}?{params}", headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, list) else []


def _candidate_from_nominatim(
    item: dict[str, Any],
    timezone_resolver: TimezoneResolver,
) -> PlaceCandidate | None:
    try:
        latitude = float(item["lat"])
        longitude = float(item["lon"])
    except (KeyError, TypeError, ValueError):
        return None

    timezone = timezone_resolver(latitude, longitude)
    if not timezone:
        return None

    address = item.get("address") if isinstance(item.get("address"), dict) else {}
    name = _address_name(address) or str(item.get("name") or "").strip()
    if not name:
        name = str(item.get("display_name") or "").split(",", maxsplit=1)[0].strip()
    if not name:
        return None

    osm_type = str(item.get("osm_type") or "place")
    osm_id = str(item.get("osm_id") or abs(hash((name, latitude, longitude))))
    return PlaceCandidate(
        id=f"osm:{osm_type}:{osm_id}",
        name=name,
        admin_name=_admin_name(address),
        country_code=str(address.get("country_code") or "").upper(),
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
    )


def _address_name(address: dict[str, Any]) -> str:
    for key in ("city", "town", "village", "municipality", "hamlet", "county"):
        value = str(address.get(key) or "").strip()
        if value:
            return value
    return ""


def _admin_name(address: dict[str, Any]) -> str:
    for key in ("state", "region", "county", "country"):
        value = str(address.get(key) or "").strip()
        if value:
            return value
    return ""


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace(",", " ").split())


@lru_cache(maxsize=1)
def _geonames_cities() -> dict[str, dict[str, Any]]:
    import geonamescache

    return geonamescache.GeonamesCache().get_cities()


@lru_cache(maxsize=1)
def _geonames_countries() -> dict[str, dict[str, Any]]:
    import geonamescache

    return geonamescache.GeonamesCache().get_countries()


@lru_cache(maxsize=1)
def _timezone_finder():
    from timezonefinder import TimezoneFinder

    return TimezoneFinder(in_memory=True)
