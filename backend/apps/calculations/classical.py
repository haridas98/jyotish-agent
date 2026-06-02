from __future__ import annotations

from datetime import datetime, time, timedelta
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

EXALTATION_DEGREES = {
    "Surya": 10.0,
    "Chandra": 33.0,
    "Mangala": 298.0,
    "Budha": 165.0,
    "Guru": 95.0,
    "Shukra": 357.0,
    "Shani": 200.0,
}

DEBILITATION_DEGREES = {
    "Surya": 190.0,
    "Chandra": 213.0,
    "Mangala": 118.0,
    "Budha": 345.0,
    "Guru": 275.0,
    "Shukra": 177.0,
    "Shani": 20.0,
}

NAISARGIKA_BALA = {
    "Surya": 60.0,
    "Chandra": 51.43,
    "Shukra": 42.86,
    "Guru": 34.29,
    "Budha": 25.71,
    "Mangala": 17.14,
    "Shani": 8.57,
}

DIG_BALA_HOUSES = {
    "Surya": 10,
    "Mangala": 10,
    "Chandra": 4,
    "Shukra": 4,
    "Budha": 1,
    "Guru": 1,
    "Shani": 7,
}

ASHTAKAVARGA_SOURCES = ("Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Lagna")
ASHTAKAVARGA_TARGETS = ("Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani")

ASHTAKAVARGA_RULES = {
    "Surya": {
        "Surya": (1, 2, 4, 7, 8, 9, 10, 11),
        "Chandra": (3, 6, 10, 11),
        "Mangala": (1, 2, 4, 7, 8, 9, 10, 11),
        "Budha": (3, 5, 6, 9, 10, 11, 12),
        "Guru": (5, 6, 9, 11),
        "Shukra": (6, 7, 12),
        "Shani": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (3, 4, 6, 10, 11, 12),
    },
    "Chandra": {
        "Surya": (3, 6, 7, 8, 10, 11),
        "Chandra": (1, 3, 6, 7, 10, 11),
        "Mangala": (2, 3, 5, 6, 9, 10, 11),
        "Budha": (1, 3, 4, 5, 7, 8, 10, 11),
        "Guru": (1, 4, 7, 8, 10, 11, 12),
        "Shukra": (3, 4, 5, 7, 9, 10, 11),
        "Shani": (3, 5, 6, 11),
        "Lagna": (3, 6, 10, 11),
    },
    "Mangala": {
        "Surya": (3, 5, 6, 10, 11),
        "Chandra": (3, 6, 11),
        "Mangala": (1, 2, 4, 7, 8, 10, 11),
        "Budha": (3, 5, 6, 11),
        "Guru": (6, 10, 11, 12),
        "Shukra": (6, 8, 11, 12),
        "Shani": (1, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 3, 6, 10, 11),
    },
    "Budha": {
        "Surya": (5, 6, 9, 11, 12),
        "Chandra": (2, 4, 6, 8, 10, 11),
        "Mangala": (1, 2, 4, 7, 8, 9, 10, 11),
        "Budha": (1, 3, 5, 6, 9, 10, 11, 12),
        "Guru": (6, 8, 11, 12),
        "Shukra": (1, 2, 3, 4, 5, 8, 9, 11),
        "Shani": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 2, 4, 6, 8, 10, 11),
    },
    "Guru": {
        "Surya": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "Chandra": (2, 5, 7, 9, 11),
        "Mangala": (1, 2, 4, 7, 8, 10, 11),
        "Budha": (1, 2, 4, 5, 6, 9, 10, 11),
        "Guru": (1, 2, 3, 4, 7, 8, 10, 11),
        "Shukra": (2, 5, 6, 9, 10, 11),
        "Shani": (3, 5, 6, 12),
        "Lagna": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "Shukra": {
        "Surya": (8, 11, 12),
        "Chandra": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "Mangala": (3, 5, 6, 9, 11, 12),
        "Budha": (3, 5, 6, 9, 11),
        "Guru": (5, 8, 9, 10, 11),
        "Shukra": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "Shani": (3, 4, 5, 8, 9, 10, 11),
        "Lagna": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "Shani": {
        "Surya": (1, 2, 4, 7, 8, 10, 11),
        "Chandra": (3, 6, 11),
        "Mangala": (3, 5, 6, 10, 11, 12),
        "Budha": (6, 8, 9, 10, 11, 12),
        "Guru": (5, 6, 11, 12),
        "Shukra": (6, 11, 12),
        "Shani": (3, 5, 6, 11),
        "Lagna": (1, 3, 4, 6, 10, 11),
    },
}

WEEKDAY_LORDS = ("Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Surya")


def classical_calculations(chart: dict[str, Any]) -> dict[str, Any]:
    return {
        "avasthas": {
            "status": "calculated",
            "method": "Baladi avastha by 6-degree sign portions; even signs reverse the sequence.",
            "baladi": _baladi_rows(chart),
        },
        "vimshopaka_bala": vimshopaka_bala(chart),
        "ashtakavarga": ashtakavarga(chart),
        "shadbala": shadbala_summary(chart),
        "yogas": {
            "status": "draft_needs_citation",
            "method": "Only simple signature detection; interpretation requires shastra citations.",
            "items": yoga_signatures(chart),
        },
        "argala": argala_summary(chart),
        "special_points": special_points(chart),
        "transits": {
            "status": "api_available",
            "method": "Transit API compares as-of grahas to natal Lagna and Moon.",
        },
        "compatibility": {
            "status": "api_available",
            "method": "Compatibility API exposes ashtakuta baseline for two birth profiles.",
        },
        "muhurta": {
            "status": "api_available",
            "method": "Muhurta API ranks panchanga candidates in a date window.",
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
        "upagrahas": _upagrahas(chart),
        "vedic_points": {
            "status": "pending_jhora_audit",
            "method": "Indu lagna, bhrigu bindu, and related points need source mapping.",
        },
    }


def ashtakavarga(chart: dict[str, Any]) -> dict[str, object]:
    sources = _ashtakavarga_sources(chart)
    bhinna = {}
    sarva_scores = [0] * len(RASHIS)
    missing_sources = [source for source in ASHTAKAVARGA_SOURCES if source not in sources]
    for target in ASHTAKAVARGA_TARGETS:
        scores = [0] * len(RASHIS)
        for source, houses in ASHTAKAVARGA_RULES[target].items():
            source_index = sources.get(source)
            if source_index is None:
                continue
            for house in houses:
                scores[(source_index + house - 1) % len(RASHIS)] += 1
        for index, value in enumerate(scores):
            sarva_scores[index] += value
        bhinna[target] = {
            "scores": scores,
            "total": sum(scores),
        }
    return {
        "status": "draft_needs_jhora_audit",
        "method": "Bhinna/Sarva Ashtakavarga bindu tables; pending JHora fixture parity.",
        "missing_sources": missing_sources,
        "bhinna": bhinna,
        "sarva": {
            "scores": sarva_scores,
            "total": sum(sarva_scores),
        },
    }


def shadbala_summary(chart: dict[str, Any]) -> dict[str, object]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    items = []
    for graha in chart.get("grahas", []):
        body = str(graha.get("body") or "")
        longitude = _body_longitude(graha)
        rashi_index = _int_or_none(graha.get("rashi_index"))
        if body not in NAISARGIKA_BALA or longitude is None:
            continue
        components = {
            "naisargika": NAISARGIKA_BALA[body],
            "uccha": _uccha_bala(body, longitude),
            "dig": _dig_bala(body, lagna_index, rashi_index),
        }
        items.append(
            {
                "body": body,
                "components": components,
                "known_total": round(sum(components.values()), 2),
            }
        )
    return {
        "status": "draft_needs_jhora_audit",
        "method": "Partial Shadbala: naisargika, uccha, and whole-sign dig bala only.",
        "items": items,
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


def _upagrahas(chart: dict[str, Any]) -> dict[str, object]:
    birth = chart.get("birth", {})
    raw_moment = birth.get("local_datetime") if isinstance(birth, dict) else None
    ascendant = _body_longitude(chart.get("ascendant"))
    if not isinstance(raw_moment, str):
        return {
            "status": "missing_birth_time",
            "items": [],
            "method": "Needs local birth datetime.",
        }
    try:
        moment = datetime.fromisoformat(raw_moment)
    except ValueError:
        return {
            "status": "invalid_birth_time",
            "items": [],
            "method": "Needs ISO local birth datetime.",
        }
    gulika_time = _saturn_segment_midpoint(moment)
    offset_hours = (gulika_time.hour + gulika_time.minute / 60) - (moment.hour + moment.minute / 60)
    base_longitude = ascendant if ascendant is not None else 0.0
    gulika_longitude = normalize_degrees(base_longitude + offset_hours * 15.0)
    item = _point_payload("gulika", "Gulika/Mandi", gulika_longitude)
    item["local_time"] = gulika_time.strftime("%H:%M")
    item["calculation_note"] = "Approximate weekday Saturn segment; sunrise/sunset audit pending."
    return {
        "status": "draft_needs_jhora_audit",
        "method": "Civil 06:00-18:00/18:00-06:00 Saturn segment approximation pending JHora audit.",
        "items": [item],
    }


def _saturn_segment_midpoint(moment: datetime) -> time:
    day_start = moment.replace(hour=6, minute=0, second=0, microsecond=0)
    day_end = moment.replace(hour=18, minute=0, second=0, microsecond=0)
    if day_start <= moment < day_end:
        period_start = day_start
        segment_hours = 12 / 8
        start_lord_index = moment.weekday()
    else:
        if moment < day_start:
            period_start = day_start - timedelta(hours=12)
        else:
            period_start = day_end
        segment_hours = 12 / 8
        start_lord_index = (moment.weekday() + 1) % len(WEEKDAY_LORDS)

    sequence = [WEEKDAY_LORDS[(start_lord_index + offset) % len(WEEKDAY_LORDS)] for offset in range(8)]
    saturn_segment = sequence.index("Shani")
    midpoint = period_start + timedelta(hours=segment_hours * saturn_segment + segment_hours / 2)
    return midpoint.timetz().replace(tzinfo=None)


def _ashtakavarga_sources(chart: dict[str, Any]) -> dict[str, int]:
    sources = {}
    ascendant_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    if ascendant_index is not None:
        sources["Lagna"] = ascendant_index
    for graha in chart.get("grahas", []):
        body = graha.get("body")
        rashi_index = _int_or_none(graha.get("rashi_index"))
        if body in ASHTAKAVARGA_TARGETS and rashi_index is not None:
            sources[str(body)] = rashi_index
    return sources


def _uccha_bala(body: str, longitude: float) -> float:
    debilitation = DEBILITATION_DEGREES.get(body)
    if debilitation is None:
        return 0.0
    distance = abs(normalize_degrees(longitude) - debilitation)
    distance = min(distance, 360.0 - distance)
    return round(distance / 3.0, 2)


def _dig_bala(body: str, lagna_index: int | None, rashi_index: int | None) -> float:
    target_house = DIG_BALA_HOUSES.get(body)
    if target_house is None or lagna_index is None or rashi_index is None:
        return 0.0
    house = _house_from(lagna_index, rashi_index)
    distance = abs(house - target_house)
    distance = min(distance, 12 - distance)
    return round(60.0 * max(0.0, 1 - distance / 6.0), 2)


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
