from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


class PlaceNotFound(ValueError):
    pass


@dataclass(frozen=True)
class PlaceCandidate:
    id: str
    name: str
    admin_name: str
    country_code: str
    latitude: float
    longitude: float
    timezone: str
    aliases: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        return ", ".join(part for part in (self.name, self.admin_name, self.country_code) if part)

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "admin_name": self.admin_name,
            "country_code": self.country_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
        }


PLACES = (
    PlaceCandidate(
        id="in-vrindavan",
        name="Vrindavan",
        admin_name="Uttar Pradesh",
        country_code="IN",
        latitude=27.565,
        longitude=77.6593,
        timezone="Asia/Kolkata",
        aliases=(
            "vrindavan",
            "vrindavana",
            "vrindavan india",
            "vrindavan up",
            "вриндаван",
            "вриндавана",
        ),
    ),
    PlaceCandidate(
        id="in-mayapur",
        name="Mayapur",
        admin_name="West Bengal",
        country_code="IN",
        latitude=23.4241,
        longitude=88.3883,
        timezone="Asia/Kolkata",
        aliases=(
            "mayapur",
            "sri mayapur",
            "sridham mayapur",
            "navadvipa",
            "маяпур",
            "майапур",
            "шри маяпур",
            "навадвипа",
        ),
    ),
    PlaceCandidate(
        id="ru-yekaterinburg",
        name="Yekaterinburg",
        admin_name="Sverdlovsk Oblast",
        country_code="RU",
        latitude=56.8389,
        longitude=60.6057,
        timezone="Asia/Yekaterinburg",
        aliases=("ekaterinburg", "yekaterinburg", "екатеринбург"),
    ),
    PlaceCandidate(
        id="ru-sterlitamak",
        name="Sterlitamak",
        admin_name="Bashkortostan",
        country_code="RU",
        latitude=53.6304,
        longitude=55.9502,
        timezone="Asia/Yekaterinburg",
        aliases=(
            "sterlitamak",
            "sterlitamak russia",
            "sterlitamak bashkortostan",
            "sterlitamak republic of bashkortostan",
            "стерлитамак",
            "стерлитамак россия",
            "стерлитамак башкортостан",
        ),
    ),
    PlaceCandidate(
        id="ru-gelendzhik",
        name="Gelendzhik",
        admin_name="Russia",
        country_code="RU",
        latitude=44.5622,
        longitude=38.0848,
        timezone="Europe/Moscow",
        aliases=(
            "gelendzhik",
            "gelendzhik russia",
            "gelendzhik russia ru",
            "gelendzhik krasnodar krai",
            "gelendzhik krasnodar",
            "геленджик",
            "геленджик россия",
            "геленджик краснодарский край",
        ),
    ),
    PlaceCandidate(
        id="ru-moscow",
        name="Moscow",
        admin_name="Moscow",
        country_code="RU",
        latitude=55.7558,
        longitude=37.6173,
        timezone="Europe/Moscow",
        aliases=("moscow", "москва"),
    ),
)


def search_places(query: str, limit: int = 10) -> list[PlaceCandidate]:
    return list(_search_places_cached(_normalize(query), limit))


@lru_cache(maxsize=512)
def _search_places_cached(normalized_query: str, limit: int) -> tuple[PlaceCandidate, ...]:
    if not normalized_query:
        return ()

    scored: list[tuple[int, PlaceCandidate]] = []
    for place in PLACES:
        searchable = [place.name, place.admin_name, place.country_code, place.label, *place.aliases]
        normalized_values = [_normalize(value) for value in searchable]
        if normalized_query in normalized_values:
            scored.append((0, place))
        elif all(
            any(token in value.split() or token in value for value in normalized_values)
            for token in normalized_query.split()
        ):
            scored.append((1, place))
        elif any(value.startswith(normalized_query) for value in normalized_values):
            scored.append((1, place))
        elif any(normalized_query in value for value in normalized_values):
            scored.append((2, place))

    scored.sort(key=lambda item: (item[0], item[1].name))
    return tuple(place for _, place in scored[:limit])


def resolve_place(query: str) -> PlaceCandidate:
    results = search_places(query, limit=1)
    if not results:
        raise PlaceNotFound(f"Place not found: {query}")
    return results[0]


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace(",", " ").split())
