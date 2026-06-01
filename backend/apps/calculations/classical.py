from __future__ import annotations

from math import floor
from typing import Any

from .constants import RASHIS
from .primitives import normalize_degrees, zodiac_placement

BALADI_STATES = (
    ("Bala", 0.25),
    ("Kumara", 0.5),
    ("Yuva", 1.0),
    ("Vriddha", 0.5),
    ("Mrita", 0.0),
)

OWN_SIGNS = {
    "Surya": {"Simha"},
    "Chandra": {"Karka"},
    "Mangala": {"Mesha", "Vrischika"},
    "Budha": {"Mithuna", "Kanya"},
    "Guru": {"Dhanu", "Meena"},
    "Shukra": {"Vrishabha", "Tula"},
    "Shani": {"Makara", "Kumbha"},
}

EXALTATION_SIGNS = {
    "Surya": "Mesha",
    "Chandra": "Vrishabha",
    "Mangala": "Makara",
    "Budha": "Kanya",
    "Guru": "Karka",
    "Shukra": "Meena",
    "Shani": "Tula",
}


def classical_calculations(chart: dict[str, Any]) -> dict[str, Any]:
    return {
        "avasthas": {
            "status": "calculated",
            "method": "Baladi avastha by 6-degree sign portions; even signs reverse the sequence.",
            "baladi": _baladi_rows(chart),
        },
        "vimshopaka_bala": vimshopaka_bala(chart),
        "ashtakavarga": {
            "status": "pending_jhora_audit",
            "method": "BAV/SAV tables are not exposed until rule tables are checked against JHora fixtures.",
        },
        "shadbala": {
            "status": "pending_jhora_audit",
            "method": "Requires full sixfold bala pipeline and parity fixtures before user-facing claims.",
        },
        "yogas": {
            "status": "draft_needs_citation",
            "method": "Only simple signature detection; interpretation requires shastra citations.",
            "items": yoga_signatures(chart),
        },
        "argala": argala_summary(chart),
        "special_points": special_points(chart),
        "transits": {
            "status": "pending_endpoint",
            "method": "Transit API will reuse the same ephemeris engine for an as-of datetime.",
        },
        "compatibility": {
            "status": "pending_separate_chart_pair",
            "method": "Requires two birth profiles and ethical wording policy.",
        },
        "muhurta": {
            "status": "pending_separate_workflow",
            "method": "Requires task type, location, time window, and Vaishnava remedial policy.",
        },
    }


def baladi_avastha(longitude: float) -> dict[str, object]:
    normalized = normalize_degrees(longitude)
    sign_index = min(11, floor(normalized / 30.0))
    sign_degree = normalized % 30.0
    band_index = min(4, floor(sign_degree / 6.0))
    state_index = band_index if _is_odd_sign(sign_index) else 4 - band_index
    state, strength = BALADI_STATES[state_index]
    return {
        "state": state,
        "strength": strength,
        "degree_band": f"{band_index * 6}-{(band_index + 1) * 6}",
    }


def yoga_signatures(chart: dict[str, Any]) -> list[dict[str, object]]:
    grahas = _graha_index(chart)
    items: list[dict[str, object]] = []

    moon = grahas.get("Chandra")
    jupiter = grahas.get("Guru")
    if moon and jupiter and _house_from(moon["rashi_index"], jupiter["rashi_index"]) in {1, 4, 7, 10}:
        items.append(
            {
                "key": "gaja_kesari",
                "name": "Gaja Kesari",
                "bodies": ["Chandra", "Guru"],
                "status": "signature_only",
            }
        )

    sun = grahas.get("Surya")
    mercury = grahas.get("Budha")
    if sun and mercury and sun["rashi_index"] == mercury["rashi_index"]:
        items.append(
            {
                "key": "budha_aditya",
                "name": "Budha Aditya",
                "bodies": ["Surya", "Budha"],
                "status": "signature_only",
            }
        )

    mars = grahas.get("Mangala")
    if moon and mars and moon["rashi_index"] == mars["rashi_index"]:
        items.append(
            {
                "key": "chandra_mangala",
                "name": "Chandra Mangala",
                "bodies": ["Chandra", "Mangala"],
                "status": "signature_only",
            }
        )

    return items


def argala_summary(chart: dict[str, Any]) -> dict[str, object]:
    ascendant = chart.get("ascendant") or {}
    lagna_index = _int_or_none(ascendant.get("rashi_index"))
    if lagna_index is None:
        return {
            "status": "missing_lagna",
            "reference": "Lagna",
            "primary": [],
            "obstruction": [],
        }

    return {
        "status": "calculated",
        "reference": "Lagna",
        "primary": _argala_rows(chart, lagna_index, (2, 4, 11)),
        "obstruction": _argala_rows(chart, lagna_index, (12, 10, 3)),
        "method": "Primary Jaimini argala houses 2/4/11 with obstruction from 12/10/3.",
    }


def special_points(chart: dict[str, Any]) -> dict[str, object]:
    ascendant = _body_longitude(chart.get("ascendant"))
    sun = _body_longitude(_graha_index(chart).get("Surya"))
    moon = _body_longitude(_graha_index(chart).get("Chandra"))
    lots = []
    if ascendant is not None and sun is not None and moon is not None:
        lots = [
            _point_payload("part_of_fortune_day", "Part of Fortune day", ascendant + moon - sun),
            _point_payload("part_of_fortune_night", "Part of Fortune night", ascendant + sun - moon),
        ]
    return {
        "status": "partial",
        "arabic_lots": lots,
        "upagrahas": {
            "status": "pending_jhora_audit",
            "method": "Gulika/Mandi and other upagrahas need weekday/day-night segment fixtures.",
        },
        "vedic_points": {
            "status": "pending_jhora_audit",
            "method": "Indu lagna, bhrigu bindu, and related points need source mapping.",
        },
    }


def vimshopaka_bala(chart: dict[str, Any]) -> dict[str, object]:
    grahas = _graha_index(chart)
    rows = []
    for body in grahas:
        if body not in OWN_SIGNS and body not in EXALTATION_SIGNS:
            continue
        supportive = []
        for code, varga in (chart.get("vargas") or {}).items():
            placement = _varga_placement(varga, body)
            if not placement:
                continue
            rashi = str(placement.get("rashi") or "")
            if rashi in OWN_SIGNS.get(body, set()) or rashi == EXALTATION_SIGNS.get(body):
                supportive.append(code)
        rows.append(
            {
                "body": body,
                "supportive_vargas": supportive,
                "support_count": len(supportive),
            }
        )
    return {
        "status": "draft_needs_jhora_audit",
        "method": "Temporary own/exaltation varga support count; not final Vimshopaka/Shadbala.",
        "items": rows,
    }


def _baladi_rows(chart: dict[str, Any]) -> list[dict[str, object]]:
    rows = []
    for graha in chart.get("grahas", []):
        longitude = _body_longitude(graha)
        if longitude is None:
            continue
        rows.append({"body": graha.get("body"), **baladi_avastha(longitude)})
    return rows


def _argala_rows(chart: dict[str, Any], reference_index: int, houses: tuple[int, ...]) -> list[dict[str, object]]:
    rows = []
    for house in houses:
        bodies = [
            str(graha.get("body"))
            for graha in chart.get("grahas", [])
            if _int_or_none(graha.get("rashi_index")) is not None
            and _house_from(reference_index, int(graha["rashi_index"])) == house
        ]
        if bodies:
            rows.append({"house": house, "bodies": bodies})
    return rows


def _point_payload(key: str, name: str, longitude: float) -> dict[str, object]:
    placement = zodiac_placement(longitude)
    return {
        "key": key,
        "name": name,
        "longitude": round(placement.longitude, 6),
        "rashi": placement.rashi,
        "rashi_index": placement.rashi_index,
        "nakshatra": placement.nakshatra,
        "pada": placement.pada,
    }


def _graha_index(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(graha.get("body")): graha
        for graha in chart.get("grahas", [])
        if isinstance(graha, dict) and graha.get("body")
    }


def _varga_placement(varga: object, body: str) -> dict[str, Any] | None:
    if not isinstance(varga, dict):
        return None
    for placement in varga.get("placements", []):
        if isinstance(placement, dict) and placement.get("body") == body:
            return placement
    return None


def _body_longitude(body: object) -> float | None:
    if not isinstance(body, dict):
        return None
    try:
        return float(body["longitude"])
    except (KeyError, TypeError, ValueError):
        return None


def _house_from(reference_index: int, target_index: int) -> int:
    return ((target_index - reference_index) % len(RASHIS)) + 1


def _is_odd_sign(sign_index: int) -> bool:
    return sign_index % 2 == 0


def _int_or_none(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None
