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

INDU_KALAS = {
    "Surya": 30,
    "Chandra": 16,
    "Mangala": 6,
    "Budha": 8,
    "Guru": 10,
    "Shukra": 12,
    "Shani": 1,
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

RASHI_LORDS = {
    0: "Mangala",
    1: "Shukra",
    2: "Budha",
    3: "Chandra",
    4: "Surya",
    5: "Budha",
    6: "Shukra",
    7: "Mangala",
    8: "Guru",
    9: "Shani",
    10: "Shani",
    11: "Guru",
}

YOGA_PLANETS = ("Mangala", "Budha", "Guru", "Shukra", "Shani")
NATURAL_BENEFICS = {"Budha", "Guru", "Shukra"}
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
DAY_STRONG_BODIES = {"Surya", "Guru", "Shukra"}
NIGHT_STRONG_BODIES = {"Chandra", "Mangala", "Shani"}
MAHAPURUSHA_YOGAS = {
    "Mangala": ("ruchaka_mahapurusha", "Ruchaka Mahapurusha"),
    "Budha": ("bhadra_mahapurusha", "Bhadra Mahapurusha"),
    "Guru": ("hamsa_mahapurusha", "Hamsa Mahapurusha"),
    "Shukra": ("malavya_mahapurusha", "Malavya Mahapurusha"),
    "Shani": ("shasha_mahapurusha", "Shasha Mahapurusha"),
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
            "status": "partial_calculated_needs_citation",
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

    items.extend(_mahapurusha_yogas(chart, grahas))
    items.extend(_moon_adjacent_yogas(grahas))
    items.extend(_sun_adjacent_yogas(grahas))
    items.extend(_amala_yogas(chart, grahas))
    items.extend(_lordship_yogas(chart, grahas))
    items.extend(_neecha_bhanga_yogas(chart, grahas))

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
        "vedic_points": _vedic_points(chart),
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
    status = (
        "partial_calculated_needs_jhora_profile_audit"
        if missing_sources
        else "calculated_source_backed_needs_jhora_profile_audit"
    )
    return {
        "status": status,
        "method": "Bhinna/Sarva Ashtakavarga bindu tables using standard benefic-place constants.",
        "source_basis": "Brihat Jataka chapter IX Ashtakavarga rules; B.V. Raman-style 337 bindu constants.",
        "audit_status": "jhora_profile_diff_open",
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
            "sthana": _sthana_bala(body, str(graha.get("rashi") or "")),
            "dig": _dig_bala(body, lagna_index, rashi_index),
            "chesta": _chesta_bala(graha),
            "kala": _kala_bala(body, chart),
        }
        items.append(
            {
                "body": body,
                "components": components,
                "known_total": round(sum(components.values()), 2),
            }
        )
    return {
        "status": "partial_calculated_needs_jhora_audit",
        "method": "Partial Shadbala: naisargika, uccha, sthana dignity, whole-sign dig, chesta, and day/night kala bala.",
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
        "status": "partial_calculated_needs_jhora_audit",
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


def _mahapurusha_yogas(chart: dict[str, Any], grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    if lagna_index is None:
        return []
    rows = []
    for body, (key, name) in MAHAPURUSHA_YOGAS.items():
        graha = grahas.get(body)
        rashi_index = _int_or_none(graha.get("rashi_index") if graha else None)
        rashi = str(graha.get("rashi") or "") if graha else ""
        if rashi_index is None:
            continue
        is_kendra = _house_from(lagna_index, rashi_index) in KENDRA_HOUSES
        is_strong_sign = rashi in OWN_SIGNS.get(body, set()) or rashi == EXALTATION_SIGNS.get(body)
        if is_kendra and is_strong_sign:
            rows.append(
                _yoga_payload(
                    key,
                    name,
                    [body],
                    "calculated_needs_citation",
                    reference="Lagna",
                )
            )
    return rows


def _moon_adjacent_yogas(grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    moon = grahas.get("Chandra")
    moon_index = _int_or_none(moon.get("rashi_index") if moon else None)
    if moon_index is None:
        return []
    second = _planets_in_house_from(grahas, moon_index, 2)
    twelfth = _planets_in_house_from(grahas, moon_index, 12)
    if second and twelfth:
        return [_yoga_payload("durudhara", "Durudhara", sorted(second + twelfth), "calculated_needs_citation", reference="Chandra")]
    if second:
        return [_yoga_payload("sunapha", "Sunapha", sorted(second), "calculated_needs_citation", reference="Chandra")]
    if twelfth:
        return [_yoga_payload("anapha", "Anapha", sorted(twelfth), "calculated_needs_citation", reference="Chandra")]
    return [_yoga_payload("kemadruma", "Kemadruma", ["Chandra"], "calculated_needs_citation", reference="Chandra")]


def _sun_adjacent_yogas(grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    sun = grahas.get("Surya")
    sun_index = _int_or_none(sun.get("rashi_index") if sun else None)
    if sun_index is None:
        return []
    second = _planets_in_house_from(grahas, sun_index, 2)
    twelfth = _planets_in_house_from(grahas, sun_index, 12)
    rows = []
    if second:
        rows.append(_yoga_payload("veshi", "Veshi", sorted(second), "calculated_needs_citation", reference="Surya"))
    if twelfth:
        rows.append(_yoga_payload("voshi", "Voshi", sorted(twelfth), "calculated_needs_citation", reference="Surya"))
    if second and twelfth:
        rows.append(
            _yoga_payload(
                "ubhayachari",
                "Ubhayachari",
                sorted(second + twelfth),
                "calculated_needs_citation",
                reference="Surya",
            )
        )
    return rows


def _amala_yogas(chart: dict[str, Any], grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    rows = []
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    if lagna_index is not None:
        benefics = _benefics_in_house_from(grahas, lagna_index, 10)
        if benefics:
            rows.append(_yoga_payload("amala", "Amala", benefics, "calculated_needs_citation", reference="Lagna"))
    moon = grahas.get("Chandra")
    moon_index = _int_or_none(moon.get("rashi_index") if moon else None)
    if moon_index is not None:
        benefics = _benefics_in_house_from(grahas, moon_index, 10)
        if benefics:
            rows.append(_yoga_payload("amala_chandra", "Amala from Chandra", benefics, "calculated_needs_citation", reference="Chandra"))
    return rows


def _planets_in_house_from(grahas: dict[str, dict[str, Any]], reference_index: int, house: int) -> list[str]:
    bodies = []
    for body in YOGA_PLANETS:
        rashi_index = _int_or_none((grahas.get(body) or {}).get("rashi_index"))
        if rashi_index is not None and _house_from(reference_index, rashi_index) == house:
            bodies.append(body)
    return bodies


def _benefics_in_house_from(grahas: dict[str, dict[str, Any]], reference_index: int, house: int) -> list[str]:
    return [body for body in _planets_in_house_from(grahas, reference_index, house) if body in NATURAL_BENEFICS]


def _lordship_yogas(chart: dict[str, Any], grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    if lagna_index is None:
        return []
    rows = []
    ninth_lord = _house_lord(lagna_index, 9)
    tenth_lord = _house_lord(lagna_index, 10)
    if _associated(grahas, ninth_lord, tenth_lord):
        rows.append(
            _yoga_payload(
                "dharma_karmadhipati_raja",
                "Dharma Karmadhipati Raja",
                _unique_bodies([ninth_lord, tenth_lord]),
                "calculated_needs_citation",
                reference="Lagna",
            )
        )

    for kendra in KENDRA_HOUSES:
        for trikona in TRIKONA_HOUSES:
            kendra_lord = _house_lord(lagna_index, kendra)
            trikona_lord = _house_lord(lagna_index, trikona)
            if kendra_lord != trikona_lord and _associated(grahas, kendra_lord, trikona_lord):
                rows.append(
                    _yoga_payload(
                        "kendra_trikona_raja",
                        "Kendra Trikona Raja",
                        _unique_bodies([kendra_lord, trikona_lord]),
                        "calculated_needs_citation",
                        reference="Lagna",
                    )
                )
                break
        if any(row["key"] == "kendra_trikona_raja" for row in rows):
            break

    second_lord = _house_lord(lagna_index, 2)
    eleventh_lord = _house_lord(lagna_index, 11)
    if _associated(grahas, second_lord, eleventh_lord):
        rows.append(
            _yoga_payload(
                "second_lord_eleventh_lord_link",
                "Second/Eleventh Lord Link",
                _unique_bodies([second_lord, eleventh_lord]),
                "calculated_needs_citation",
                reference="Lagna",
            )
        )

    rows.extend(_viparita_yogas(lagna_index, grahas))
    return rows


def _viparita_yogas(lagna_index: int, grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    rows = []
    for house, key, name in (
        (6, "viparita_harsha", "Harsha Viparita Raja"),
        (8, "viparita_sarala", "Sarala Viparita Raja"),
        (12, "viparita_vimala", "Vimala Viparita Raja"),
    ):
        lord = _house_lord(lagna_index, house)
        placement = grahas.get(lord)
        rashi_index = _int_or_none(placement.get("rashi_index") if placement else None)
        if rashi_index is None:
            continue
        placed_house = _house_from(lagna_index, rashi_index)
        if placed_house in DUSTHANA_HOUSES and placed_house != house:
            rows.append(_yoga_payload(key, name, [lord], "calculated_needs_citation", reference="Lagna"))
    return rows


def _neecha_bhanga_yogas(chart: dict[str, Any], grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    moon_index = _int_or_none((grahas.get("Chandra") or {}).get("rashi_index"))
    rows = []
    for body, graha in grahas.items():
        rashi = str(graha.get("rashi") or "")
        rashi_index = _int_or_none(graha.get("rashi_index"))
        if rashi_index is None or rashi != _debilitation_sign(body):
            continue
        debility_lord = _rashi_lord(rashi_index)
        lord_index = _int_or_none((grahas.get(debility_lord) or {}).get("rashi_index"))
        if lord_index is None:
            continue
        from_lagna = lagna_index is not None and _house_from(lagna_index, lord_index) in KENDRA_HOUSES
        from_moon = moon_index is not None and _house_from(moon_index, lord_index) in KENDRA_HOUSES
        if from_lagna or from_moon:
            rows.append(
                _yoga_payload(
                    "neecha_bhanga_raja",
                    "Neecha Bhanga Raja",
                    _unique_bodies([body, debility_lord]),
                    "calculated_needs_citation",
                    reference="Lagna/Moon",
                )
            )
    return rows


def _yoga_payload(
    key: str,
    name: str,
    bodies: list[str],
    status: str,
    *,
    reference: str,
) -> dict[str, object]:
    return {
        "key": key,
        "name": name,
        "bodies": bodies,
        "status": status,
        "reference": reference,
    }


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
    context = chart.get("upagraha_context")
    if isinstance(context, dict):
        segment = context.get("gulika")
        gulika_ascendant = context.get("gulika_ascendant")
        longitude = _body_longitude(gulika_ascendant)
        if longitude is None:
            longitude = _body_longitude(chart.get("ascendant"))
        if isinstance(segment, dict) and longitude is not None:
            item = _point_payload("gulika", "Gulika/Mandi", longitude)
            item["local_time"] = str(segment.get("local_time") or "")
            item["period"] = str(segment.get("period") or "")
            item["segment"] = segment.get("segment")
            item["starts_at"] = segment.get("starts_at")
            item["ends_at"] = segment.get("ends_at")
            item["midpoint"] = segment.get("midpoint")
            item["calculation_note"] = (
                "Actual sunrise/sunset segment with Lagna at Gulika midpoint; pending JHora fixture parity."
            )
            return {
                "status": "calculated_needs_jhora_audit",
                "method": "Gulika/Mandi uses actual sunrise/sunset period segmentation and midpoint Lagna.",
                "items": [item],
            }

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
        "status": "calculated_needs_jhora_audit",
        "method": "Civil 06:00-18:00/18:00-06:00 Saturn segment approximation pending JHora audit.",
        "items": [item],
    }


def _vedic_points(chart: dict[str, Any]) -> dict[str, object]:
    items = []
    indu = _indu_lagna(chart)
    if indu:
        items.append(indu)
    return {
        "status": "calculated_needs_source_audit" if items else "pending_source_mapping",
        "method": "Indu/Dhana Lagna by ninth lords from Lagna and Moon; source passage and JHora parity still required.",
        "items": items,
    }


def _indu_lagna(chart: dict[str, Any]) -> dict[str, object] | None:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    moon_index = _int_or_none((_graha_index(chart).get("Chandra") or {}).get("rashi_index"))
    if lagna_index is None or moon_index is None:
        return None
    lagna_ninth_lord = _house_lord(lagna_index, 9)
    moon_ninth_lord = _house_lord(moon_index, 9)
    if lagna_ninth_lord not in INDU_KALAS or moon_ninth_lord not in INDU_KALAS:
        return None
    kala_sum = INDU_KALAS[lagna_ninth_lord] + INDU_KALAS[moon_ninth_lord]
    remainder = kala_sum % 12 or 12
    rashi_index = (moon_index + remainder - 1) % len(RASHIS)
    longitude = rashi_index * 30.0
    point = _point_payload("indu_lagna", "Indu/Dhana Lagna", longitude)
    point["metadata"] = {
        "lagna_ninth_lord": lagna_ninth_lord,
        "moon_ninth_lord": moon_ninth_lord,
        "kala_sum": kala_sum,
        "remainder": remainder,
        "counted_from": "Chandra",
        "audit_status": "needs_source_and_jhora_fixture",
    }
    return point


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


def _sthana_bala(body: str, rashi: str) -> float:
    if not rashi:
        return 0.0
    if rashi == EXALTATION_SIGNS.get(body):
        return 60.0
    if rashi == _debilitation_sign(body):
        return 0.0
    if rashi in OWN_SIGNS.get(body, set()):
        return 45.0
    return 15.0


def _debilitation_sign(body: str) -> str:
    degree = DEBILITATION_DEGREES.get(body)
    if degree is None:
        return ""
    return zodiac_placement(degree).rashi


def _chesta_bala(graha: dict[str, Any]) -> float:
    speed = _float_or_none(graha.get("speed_longitude"))
    if graha.get("retrograde") is True or (speed is not None and speed < 0):
        return 60.0
    if speed is None:
        return 0.0
    return round(min(60.0, abs(speed) * 15.0), 2)


def _kala_bala(body: str, chart: dict[str, Any]) -> float:
    moment = _birth_moment(chart)
    if moment is None:
        return 0.0
    is_day = 6 <= moment.hour < 18
    if body == "Budha":
        return 30.0
    if is_day:
        return 60.0 if body in DAY_STRONG_BODIES else 0.0
    return 60.0 if body in NIGHT_STRONG_BODIES else 0.0


def _dig_bala(body: str, lagna_index: int | None, rashi_index: int | None) -> float:
    target_house = DIG_BALA_HOUSES.get(body)
    if target_house is None or lagna_index is None or rashi_index is None:
        return 0.0
    house = _house_from(lagna_index, rashi_index)
    distance = abs(house - target_house)
    distance = min(distance, 12 - distance)
    return round(60.0 * max(0.0, 1 - distance / 6.0), 2)


def _house_lord(lagna_index: int, house: int) -> str:
    return _rashi_lord((lagna_index + house - 1) % len(RASHIS))


def _rashi_lord(rashi_index: int) -> str:
    return RASHI_LORDS[rashi_index % len(RASHIS)]


def _associated(grahas: dict[str, dict[str, Any]], first: str, second: str) -> bool:
    first_index = _int_or_none((grahas.get(first) or {}).get("rashi_index"))
    second_index = _int_or_none((grahas.get(second) or {}).get("rashi_index"))
    return first_index is not None and first_index == second_index


def _unique_bodies(bodies: list[str]) -> list[str]:
    unique = []
    for body in bodies:
        if body not in unique:
            unique.append(body)
    return unique


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


def _birth_moment(chart: dict[str, Any]) -> datetime | None:
    raw = (chart.get("birth") or {}).get("local_datetime")
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _house_from(reference_index: int, target_index: int) -> int:
    return ((target_index - reference_index) % len(RASHIS)) + 1


def _is_odd_sign(sign_index: int) -> bool:
    return sign_index % 2 == 0


def _int_or_none(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None
