from __future__ import annotations

from datetime import datetime, time, timedelta
from math import asin, degrees, floor, radians, sin
from typing import Any

from .constants import RASHIS
from .primitives import normalize_degrees, zodiac_placement
from .vargas import divisional_placement

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
SHADBALA_REQUIRED_VIRUPAS = {
    "Chandra": 360.0,
    "Budha": 420.0,
    "Guru": 390.0,
    "Shukra": 330.0,
    "default": 300.0,
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

NODE_CO_LORD_SIGNS = {
    "Rahu": {10},
    "Ketu": {7},
}

CLASSICAL_GRAHAS = ("Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani")
VIMSOPAKA_BODIES = (*CLASSICAL_GRAHAS, "Rahu", "Ketu")
YOGA_PLANETS = ("Mangala", "Budha", "Guru", "Shukra", "Shani")
NATURAL_BENEFICS = {"Budha", "Guru", "Shukra"}
NATURAL_MALEFICS = {"Surya", "Mangala", "Shani"}
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
MOVABLE_RASHIS = {0, 3, 6, 9}
FIXED_RASHIS = {1, 4, 7, 10}
DUAL_RASHIS = {2, 5, 8, 11}
DAY_STRONG_BODIES = {"Surya", "Guru", "Shukra"}
NIGHT_STRONG_BODIES = {"Chandra", "Mangala", "Shani"}
SAPTAVARGA_CODES = ("D1", "D2", "D3", "D7", "D9", "D12", "D30")
MALE_BODIES = {"Surya", "Mangala", "Guru"}
FEMALE_BODIES = {"Chandra", "Shukra"}
NEUTER_BODIES = {"Budha", "Shani"}
STHANA_VARGA_DIGNITY_BALA = {
    "moolatrikona": 45.0,
    "own": 30.0,
    "exaltation": 30.0,
    "friend": 15.0,
    "neutral": 10.0,
    "enemy": 4.0,
    "debilitation": 2.0,
    "unknown": 0.0,
    "missing": 0.0,
}
MEAN_DAILY_SPEEDS = {
    "Mangala": 0.524,
    "Budha": 1.383,
    "Guru": 0.083,
    "Shukra": 1.2,
    "Shani": 0.033,
}
CHESTA_STATE_BALA = {
    "vakra": 60.0,
    "anuvakra": 30.0,
    "vikala": 15.0,
    "manda": 30.0,
    "mandatara": 15.0,
    "sama": 7.5,
    "chara": 45.0,
    "atichara": 30.0,
}
MAHAPURUSHA_YOGAS = {
    "Mangala": ("ruchaka_mahapurusha", "Ruchaka Mahapurusha"),
    "Budha": ("bhadra_mahapurusha", "Bhadra Mahapurusha"),
    "Guru": ("hamsa_mahapurusha", "Hamsa Mahapurusha"),
    "Shukra": ("malavya_mahapurusha", "Malavya Mahapurusha"),
    "Shani": ("shasha_mahapurusha", "Shasha Mahapurusha"),
}
SANKHYA_NABHASA_YOGAS = {
    1: ("gola_nabhasa", "Gola Nabhasa"),
    2: ("yuga_nabhasa", "Yuga Nabhasa"),
    3: ("shula_nabhasa", "Shula Nabhasa"),
    4: ("kedara_nabhasa", "Kedara Nabhasa"),
    5: ("pasha_nabhasa", "Pasha Nabhasa"),
    6: ("dama_nabhasa", "Dama/Damini Nabhasa"),
    7: ("vina_nabhasa_variant", "Vina Nabhasa Variant"),
}
AKRITI_NABHASA_PATTERNS = (
    ("gada_nabhasa", "Gada Nabhasa", (frozenset({1, 4}), frozenset({4, 7}), frozenset({7, 10}), frozenset({10, 1}))),
    ("shakata_nabhasa", "Shakata Nabhasa", (frozenset({1, 7}),)),
    ("vihaga_nabhasa", "Vihaga Nabhasa", (frozenset({4, 10}),)),
    ("shringataka_nabhasa", "Shringataka Nabhasa", (frozenset({1, 5, 9}),)),
    ("hala_nabhasa", "Hala Nabhasa", (frozenset({2, 6, 10}), frozenset({3, 7, 11}), frozenset({4, 8, 12}))),
    ("kamala_nabhasa", "Kamala Nabhasa", (frozenset({1, 4, 7, 10}),)),
    ("vapi_nabhasa", "Vapi Nabhasa", (frozenset({2, 5, 8, 11}), frozenset({3, 6, 9, 12}))),
    ("yupa_nabhasa", "Yupa Nabhasa", (frozenset({1, 2, 3, 4}),)),
    ("ishu_nabhasa", "Ishu/Shara Nabhasa", (frozenset({4, 5, 6, 7}),)),
    ("shakti_nabhasa", "Shakti Nabhasa", (frozenset({7, 8, 9, 10}),)),
    ("danda_nabhasa", "Danda Nabhasa", (frozenset({10, 11, 12, 1}),)),
    ("nauka_nabhasa", "Nauka Nabhasa", (frozenset({1, 2, 3, 4, 5, 6, 7}),)),
    ("kuta_nabhasa", "Kuta Nabhasa", (frozenset({4, 5, 6, 7, 8, 9, 10}),)),
    ("chhatra_nabhasa", "Chhatra Nabhasa", (frozenset({7, 8, 9, 10, 11, 12, 1}),)),
    ("chapa_nabhasa", "Chapa/Dhanusha Nabhasa", (frozenset({10, 11, 12, 1, 2, 3, 4}),)),
    (
        "ardha_chandra_nabhasa",
        "Ardha Chandra Nabhasa",
        tuple(frozenset(((start + offset - 1) % 12) + 1 for offset in range(7)) for start in range(1, 13)),
    ),
    ("chakra_nabhasa", "Chakra Nabhasa", (frozenset({1, 3, 5, 7, 9, 11}),)),
    ("samudra_nabhasa", "Samudra Nabhasa", (frozenset({2, 4, 6, 8, 10, 12}),)),
)

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
        "Shukra": (1, 3, 4, 5, 7, 9, 12),
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
        "Mangala": (3, 4, 6, 9, 11, 12),
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
ABBREVIATED_AHARGANA_ORDINAL_OFFSET = 659_133

VIMSHOPAKA_SCHEMES = {
    "shadvarga": {
        "D1": 6.0,
        "D2": 2.0,
        "D3": 4.0,
        "D9": 5.0,
        "D12": 2.0,
        "D30": 1.0,
    },
    "saptavarga": {
        "D1": 5.0,
        "D2": 2.0,
        "D3": 3.0,
        "D7": 1.0,
        "D9": 2.5,
        "D12": 4.5,
        "D30": 2.0,
    },
    "dashavarga": {
        "D1": 3.0,
        "D2": 1.5,
        "D3": 1.5,
        "D7": 1.5,
        "D9": 1.5,
        "D10": 1.5,
        "D12": 1.5,
        "D16": 1.5,
        "D30": 1.5,
        "D60": 5.0,
    },
    "shodasha": {
        "D1": 3.5,
        "D2": 1.0,
        "D3": 1.0,
        "D4": 0.5,
        "D7": 0.5,
        "D9": 3.0,
        "D10": 0.5,
        "D12": 0.5,
        "D16": 2.0,
        "D20": 0.5,
        "D24": 0.5,
        "D27": 0.5,
        "D30": 1.0,
        "D40": 0.5,
        "D45": 0.5,
        "D60": 4.0,
    },
}

NATURAL_FRIENDS = {
    "Surya": {"Chandra", "Mangala", "Guru"},
    "Chandra": {"Surya", "Budha"},
    "Mangala": {"Surya", "Chandra", "Guru"},
    "Budha": {"Surya", "Shukra"},
    "Guru": {"Surya", "Chandra", "Mangala"},
    "Shukra": {"Budha", "Shani"},
    "Shani": {"Budha", "Shukra"},
}

NATURAL_NEUTRALS = {
    "Surya": {"Budha"},
    "Chandra": {"Mangala", "Guru", "Shukra", "Shani"},
    "Mangala": {"Shukra", "Shani"},
    "Budha": {"Mangala", "Guru", "Shani"},
    "Guru": {"Shani"},
    "Shukra": {"Mangala", "Guru"},
    "Shani": {"Guru"},
}

NODE_NATURAL_FRIENDS = {
    "Rahu": {"Shukra", "Shani"},
    "Ketu": {"Shukra", "Shani"},
}

NODE_NATURAL_NEUTRALS = {
    "Rahu": {"Budha", "Guru"},
    "Ketu": {"Budha", "Guru"},
}

TEMPORARY_FRIEND_HOUSES = {2, 3, 4, 10, 11, 12}

VIMSHOPAKA_DIGNITY_FACTORS = {
    "moolatrikona": 1.0,
    "own": 1.0,
    "great_friend": 0.9,
    "friend": 0.75,
    "neutral": 0.5,
    "enemy": 0.35,
    "great_enemy": 0.25,
    "unknown": 0.0,
    "missing": 0.0,
}

MOOLATRIKONA_SIGNS = {
    "Surya": "Simha",
    "Chandra": "Vrishabha",
    "Mangala": "Mesha",
    "Budha": "Kanya",
    "Guru": "Dhanu",
    "Shukra": "Tula",
    "Shani": "Kumbha",
}


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
            "status": "calculated_with_catalog_coverage_needs_citation",
            "method": (
                "Detected signature-ready yogas and exposes full catalog coverage; "
                "catalog-only yogas remain visible until exact formulas and shastra "
                "citations are approved."
            ),
            **yoga_coverage(chart),
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
    items.extend(_nabhasa_yoga_signatures(chart, grahas))
    items.extend(_additional_named_yogas(chart, grahas))

    return _dedupe_yoga_items(items)


def _dedupe_yoga_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[str] = set()
    output = []
    for item in items:
        key = str(item.get("key") or "")
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def yoga_coverage(chart: dict[str, Any]) -> dict[str, object]:
    detected = yoga_signatures(chart)
    detected_by_key = {str(item["key"]): item for item in detected}
    catalog = _yoga_catalog_rows()
    calculated_statuses = {"signature_ready", "partial_signature_ready"}
    coverage = []

    for yoga in catalog:
        key = str(yoga.get("key") or "")
        detected_row = detected_by_key.get(key)
        detection_status = str(yoga.get("detection_status") or "")
        can_check = detection_status in calculated_statuses
        if detected_row:
            status = str(detected_row.get("status") or "detected")
            present = True
            bodies = detected_row.get("bodies", [])
            reference = detected_row.get("reference")
        elif can_check:
            status = "checked_not_present"
            present = False
            bodies = []
            reference = None
        else:
            formula_status = str((yoga.get("formula") or {}).get("status") or "")
            status = "calculation_pending" if formula_status else "formula_pending"
            present = False
            bodies = []
            reference = None

        coverage.append(
            {
                "key": key,
                "name": yoga.get("name"),
                "category": yoga.get("category"),
                "rarity": yoga.get("rarity"),
                "status": status,
                "present": present,
                "bodies": bodies,
                "reference": reference,
                "detection_status": detection_status,
                "source_priority": yoga.get("source_priority", []),
                "citation_policy": yoga.get("citation_policy"),
                "formula": yoga.get("formula", {}),
            }
        )

    catalog_keys = {str(yoga.get("key") or "") for yoga in catalog}
    for detected_row in detected:
        key = str(detected_row.get("key") or "")
        if key in catalog_keys:
            continue
        coverage.append(
            {
                "key": key,
                "name": detected_row.get("name"),
                "category": "uncataloged_detected",
                "rarity": "unknown",
                "status": detected_row.get("status"),
                "present": True,
                "bodies": detected_row.get("bodies", []),
                "reference": detected_row.get("reference"),
                "detection_status": "signature_ready",
                "source_priority": [],
                "citation_policy": "required_for_public_interpretation",
            }
        )

    return {
        "items": detected,
        "coverage": coverage,
        "summary": {
            "catalog_total": len(coverage),
            "detected_count": len(detected),
            "signature_checked_count": sum(
                1 for row in coverage if row["detection_status"] in calculated_statuses
            ),
            "checked_not_present_count": sum(1 for row in coverage if row["status"] == "checked_not_present"),
            "formula_pending_count": sum(1 for row in coverage if row["status"] == "formula_pending"),
            "calculation_pending_count": sum(1 for row in coverage if row["status"] == "calculation_pending"),
            "citation_required_count": sum(
                1 for row in coverage if row.get("citation_policy") == "required_for_public_interpretation"
            ),
        },
    }


def argala_summary(chart: dict[str, Any]) -> dict[str, object]:
    ascendant = chart.get("ascendant") or {}
    lagna_index = _int_or_none(ascendant.get("rashi_index"))
    if lagna_index is None:
        return {
            "status": "missing_lagna",
            "reference": "Lagna",
            "primary": [],
            "obstruction": [],
            "secondary": [],
            "secondary_obstruction": [],
            "net_effects": [],
        }

    primary_pairs = [(2, 12), (4, 10), (11, 3)]
    secondary_pairs = [(5, 9)]
    return {
        "status": "calculated_primary_secondary_lagna_needs_exact_source_review",
        "scope": "primary_and_secondary_lagna_argala",
        "reference": "Lagna",
        "pairs": _argala_pair_rows(chart, lagna_index, primary_pairs, "primary")
        + _argala_pair_rows(chart, lagna_index, secondary_pairs, "secondary"),
        "primary": _argala_rows(chart, lagna_index, (2, 4, 11)),
        "obstruction": _argala_rows(chart, lagna_index, (12, 10, 3)),
        "secondary": _argala_rows(chart, lagna_index, (5,)),
        "secondary_obstruction": _argala_rows(chart, lagna_index, (9,)),
        "net_effects": _argala_pair_rows(chart, lagna_index, primary_pairs + secondary_pairs, "combined"),
        "method": (
            "Primary Jaimini argala houses 2/4/11 with obstruction from 12/10/3; "
            "secondary 5th-house argala with obstruction from the 9th."
        ),
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
        for lot in lots:
            lot["metadata"] = {
                "source_role": "supporting_non_shastra_point",
                "public_release_policy": "supporting_calculation_not_classical_jyotish_claim",
            }
    upagrahas = _upagrahas(chart)
    vedic_points = _vedic_points(chart)
    return {
        "status": _special_points_status(lots, upagrahas, vedic_points),
        "scope": "vedic_points_upagrahas_and_supporting_lots",
        "source_basis": (
            "Vedic points and upagrahas are calculation-backed but interpretation remains source-gated; "
            "Arabic lots are exposed only as supporting non-shastra points."
        ),
        "public_release_policy": "interpretation_requires_exact_source_review",
        "arabic_lots": lots,
        "upagrahas": upagrahas,
        "vedic_points": vedic_points,
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
        else "calculated_jhora_fixture_matched"
    )
    return {
        "status": status,
        "method": "Bhinna/Sarva Ashtakavarga bindu tables using standard benefic-place constants.",
        "source_basis": "Brihat Jataka chapter IX Ashtakavarga rules; B.V. Raman-style 337 bindu constants.",
        "audit_status": "missing_sources" if missing_sources else "single_jhora_fixture_matched",
        "verified_fixture": None if missing_sources else "sterlitamak_1998_jhora_profile_cells",
        "missing_sources": missing_sources,
        "bhinna": bhinna,
        "sarva": {
            "scores": sarva_scores,
            "total": sum(sarva_scores),
        },
        "rule_profile": "jhora_parity_brihat_jataka_standard",
    }


def shadbala_summary(chart: dict[str, Any]) -> dict[str, object]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    graha_index = _graha_index(chart)
    items = []
    for graha in chart.get("grahas", []):
        body = str(graha.get("body") or "")
        longitude = _body_longitude(graha)
        rashi_index = _int_or_none(graha.get("rashi_index"))
        if body not in NAISARGIKA_BALA or longitude is None:
            continue
        sthana = _sthana_bala_full(body, graha, chart)
        dig = _dig_bala_full(body, chart, longitude, lagna_index, rashi_index)
        kala = _kala_bala_full(body, chart, graha_index)
        chesta = _chesta_bala_full(body, graha, kala)
        drik = _drik_bala(body, graha_index)
        components = {
            "naisargika": NAISARGIKA_BALA[body],
            "uccha": sthana["uccha"],
            "sthana": round(float(sthana["total"]) - float(sthana["uccha"]), 2),
            "dig": dig["exact"],
            "chesta": chesta["traditional_state"],
            "kala": kala["total"],
            "drik": drik["value"],
        }
        items.append(
            {
                "body": body,
                "components": components,
                "subcomponents": {
                    "sthana": sthana,
                    "dig": dig,
                    "chesta": chesta,
                    "kala": kala,
                    "drik": drik,
                },
                "known_total": round(sum(components.values()), 2),
                "rupas": round(sum(components.values()) / 60.0, 2),
                "required_virupas": _shadbala_required_virupas(body),
                "percent_strength": round((sum(components.values()) / _shadbala_required_virupas(body)) * 100.0, 2),
                "audit_flags": _shadbala_audit_flags(sthana, dig, kala, chesta, drik),
            }
        )
    approx_components = sorted(
        {
            flag["component"]
            for item in items
            for flag in item.get("audit_flags", [])
            if flag.get("kind") in {"proxy", "approximation", "needs_traditional_review"}
        }
    )
    chesta_quality = _shadbala_chesta_quality(items)
    return {
        "status": "calculated_needs_jhora_component_audit",
        "method": (
            "Shadbala component groups: sthana, dig, kala, chesta, drik and naisargika. "
            "Subcomponent math is explicit and remains JHora/profile-audit gated."
        ),
        "coverage": {
            "implemented_components": [
                "naisargika",
                "uccha",
                "sthana_saptavargaja_bala",
                "sthana_ojayugma_bala",
                "sthana_kendradi_bala",
                "sthana_drekkana_bala",
                "dig_degree_exact_bala",
                "kala_natonnata_bala",
                "kala_paksha_bala",
                "kala_tribhaga_bala",
                "kala_abda_masa_vara_hora_bala",
                "kala_ayana_bala",
                "kala_yuddha_bala",
                "chesta_traditional_state_bala",
                "drik_bala",
            ],
            "missing_components": [],
            "approx_components": approx_components,
            "chesta_input_quality": chesta_quality,
            "public_interpretation_status": "blocked_until_jhora_component_audit",
        },
        "component_table": _shadbala_component_table(items),
        "items": items,
    }


def _shadbala_chesta_quality(items: list[dict[str, object]]) -> dict[str, object]:
    exact = []
    luminary = []
    speed_fallback = []
    missing = []
    for item in items:
        body = str(item.get("body") or "")
        subcomponents = item.get("subcomponents") if isinstance(item.get("subcomponents"), dict) else {}
        chesta = subcomponents.get("chesta") if isinstance(subcomponents.get("chesta"), dict) else {}
        basis = str(chesta.get("calculation_basis") or "")
        state = str(chesta.get("state") or "")
        if basis == "mean_true_seeghrocha":
            exact.append(body)
        elif state in {"surya_ayana_bala", "chandra_paksha_bala"}:
            luminary.append(body)
        elif state == "unknown":
            missing.append(body)
        else:
            speed_fallback.append(body)
    return {
        "exact_mean_true_seeghrocha_bodies": exact,
        "luminary_kala_derived_bodies": luminary,
        "speed_classified_bodies": speed_fallback,
        "missing_chesta_input_bodies": missing,
    }


def _shadbala_component_table(items: list[dict[str, object]]) -> dict[str, object]:
    columns = [
        "body",
        "uccha",
        "saptavargaja",
        "ojayugma",
        "kendradi",
        "drekkana",
        "sthana_total",
        "dig",
        "natonnata",
        "paksha",
        "tribhaga",
        "abda",
        "masa",
        "vara",
        "hora",
        "ayana",
        "yuddha",
        "kala_total",
        "chesta",
        "naisargika",
        "drik",
        "total",
        "rupas",
    ]
    rows = []
    for item in items:
        subcomponents = item.get("subcomponents") if isinstance(item.get("subcomponents"), dict) else {}
        sthana = subcomponents.get("sthana") if isinstance(subcomponents.get("sthana"), dict) else {}
        kala = subcomponents.get("kala") if isinstance(subcomponents.get("kala"), dict) else {}
        abda = kala.get("abda_masa_vara_hora") if isinstance(kala.get("abda_masa_vara_hora"), dict) else {}
        abda_components = abda.get("components") if isinstance(abda.get("components"), dict) else {}
        yuddha = kala.get("yuddha") if isinstance(kala.get("yuddha"), dict) else {}
        components = item.get("components") if isinstance(item.get("components"), dict) else {}
        rows.append(
            {
                "body": item.get("body"),
                "uccha": _rounded(sthana.get("uccha")),
                "saptavargaja": _rounded(sthana.get("saptavargaja")),
                "ojayugma": _rounded(sthana.get("ojayugma")),
                "kendradi": _rounded(sthana.get("kendradi")),
                "drekkana": _rounded(sthana.get("drekkana")),
                "sthana_total": _rounded(sthana.get("total")),
                "dig": _rounded(components.get("dig")),
                "natonnata": _rounded(kala.get("natonnata")),
                "paksha": _rounded(kala.get("paksha")),
                "tribhaga": _rounded(kala.get("tribhaga")),
                "abda": _rounded(abda_components.get("abda")),
                "masa": _rounded(abda_components.get("masa")),
                "vara": _rounded(abda_components.get("vara")),
                "hora": _rounded(abda_components.get("hora")),
                "ayana": _rounded(kala.get("ayana")),
                "yuddha": _rounded(yuddha.get("value")),
                "kala_total": _rounded(kala.get("total")),
                "chesta": _rounded(components.get("chesta")),
                "naisargika": _rounded(components.get("naisargika")),
                "drik": _rounded(components.get("drik")),
                "total": _rounded(item.get("known_total")),
                "rupas": _rounded(item.get("rupas")),
            }
        )
    return {
        "status": "calculated_bphs_component_audit_table",
        "unit": "virupa",
        "columns": columns,
        "rows": rows,
    }


def vimshopaka_bala(chart: dict[str, Any]) -> dict[str, object]:
    grahas = _graha_index(chart)
    vargas = chart.get("vargas") or {}
    rows = []
    for body in grahas:
        if body not in VIMSOPAKA_BODIES:
            continue
        varga_scores = _vimshopaka_varga_scores(body, vargas, grahas)
        scheme_scores = {
            scheme: _vimshopaka_scheme_score(weights, varga_scores)
            for scheme, weights in VIMSHOPAKA_SCHEMES.items()
        }
        primary_score = scheme_scores["shodasha"]
        supportive = [
            code
            for code, score in varga_scores.items()
            if score["factor"] == 1.0 and code in VIMSHOPAKA_SCHEMES["shodasha"]
        ]
        rows.append(
            {
                "body": body,
                "primary_scheme": "shodasha",
                "score": primary_score,
                "percentage": round(primary_score * 5.0, 2),
                "scheme_scores": scheme_scores,
                "scheme_percentages": {
                    scheme: round(score * 5.0, 2) for scheme, score in scheme_scores.items()
                },
                "varga_scores": varga_scores,
                "supportive_vargas": supportive,
                "support_count": len(supportive),
                "missing_vargas": [
                    code for code in VIMSHOPAKA_SCHEMES["shodasha"] if code not in varga_scores
                ],
            }
        )
    return {
        "status": "calculated_bphs_varga_viswa_jhora_fixture_matched",
        "method": (
            "Weighted Vimshopaka Bala across shadvarga, saptavarga, dashavarga and "
            "shodasha-varga schemes using BPHS Varga Viswa factors and the JHora-matched "
            "Rahu/Ketu dignity profile."
        ),
        "dignity_profile": "bphs_varga_viswa_with_jhora_node_profile",
        "node_policy": (
            "Rahu/Ketu use JHora-matched natural relationships: Venus/Saturn friends, "
            "Mercury/Jupiter neutral, Sun/Moon/Mars enemies, with per-varga temporary "
            "relationship."
        ),
        "source_note": "BPHS/Santhanam chapter 7, verses 21-27: Varga Viswa 20/18/15/10/7/5.",
        "items": rows,
    }


def _vimshopaka_varga_scores(
    body: str,
    vargas: object,
    grahas: dict[str, dict[str, Any]],
) -> dict[str, dict[str, object]]:
    if not isinstance(vargas, dict):
        return {}
    scores: dict[str, dict[str, object]] = {}
    for code, weight in VIMSHOPAKA_SCHEMES["shodasha"].items():
        placement = _varga_placement(vargas.get(code), body)
        if not placement:
            continue
        rashi = str(placement.get("rashi") or "")
        dignity = _vimshopaka_dignity(body, rashi, code, vargas.get(code), grahas)
        factor = float(dignity["factor"])
        scores[code] = {
            "rashi": rashi,
            "weight": weight,
            "dignity": dignity["dignity"],
            "factor": factor,
            "score": round(weight * factor, 2),
            "sign_lord": dignity["sign_lord"],
            "natural_relationship": dignity["natural_relationship"],
            "temporary_relationship": dignity["temporary_relationship"],
        }
    return scores


def _vimshopaka_scheme_score(
    weights: dict[str, float],
    varga_scores: dict[str, dict[str, object]],
) -> float:
    total = 0.0
    for code, weight in weights.items():
        factor = _float_or_none(varga_scores.get(code, {}).get("factor"))
        if factor is not None:
            total += weight * factor
    return round(total, 2)


def _vimshopaka_dignity(
    body: str,
    rashi: str,
    code: str,
    varga: object,
    grahas: dict[str, dict[str, Any]],
) -> dict[str, object]:
    if not rashi:
        return _vimshopaka_dignity_payload("missing", 0.0, "", "missing", "missing")
    try:
        rashi_index = RASHIS.index(rashi)
    except ValueError:
        return _vimshopaka_dignity_payload("unknown", 0.0, "", "unknown", "unknown")

    if body not in {"Rahu", "Ketu"}:
        if rashi in OWN_SIGNS.get(body, set()):
            return _vimshopaka_dignity_payload("own", VIMSHOPAKA_DIGNITY_FACTORS["own"], "", "special", "special")
        if _is_vimshopaka_moolatrikona_sign(body, rashi):
            return _vimshopaka_dignity_payload("moolatrikona", VIMSHOPAKA_DIGNITY_FACTORS["moolatrikona"], "", "special", "special")

    lord = _rashi_lord(rashi_index)
    natural = _natural_relationship(body, lord)
    temporary = _temporary_relationship_in_varga(body, lord, rashi_index, code, varga, grahas)
    dignity = _compound_relationship(natural, temporary)
    return _vimshopaka_dignity_payload(
        dignity,
        VIMSHOPAKA_DIGNITY_FACTORS.get(dignity, 0.0),
        lord,
        natural,
        temporary,
    )


def _vimshopaka_dignity_payload(
    dignity: str,
    factor: float,
    sign_lord: str,
    natural_relationship: str,
    temporary_relationship: str,
) -> dict[str, object]:
    return {
        "dignity": dignity,
        "factor": factor,
        "sign_lord": sign_lord,
        "natural_relationship": natural_relationship,
        "temporary_relationship": temporary_relationship,
    }


def _is_vimshopaka_moolatrikona_sign(body: str, rashi: str) -> bool:
    if body == "Chandra":
        return False
    return rashi == MOOLATRIKONA_SIGNS.get(body)


def _natural_relationship(body: str, other: str) -> str:
    if not body or not other:
        return "unknown"
    if body == other:
        return "friend"
    friends = NODE_NATURAL_FRIENDS.get(body, NATURAL_FRIENDS.get(body, set()))
    neutrals = NODE_NATURAL_NEUTRALS.get(body, NATURAL_NEUTRALS.get(body, set()))
    if other in friends:
        return "friend"
    if other in neutrals:
        return "neutral"
    return "enemy"


def _temporary_relationship(
    body: str,
    other: str,
    grahas: dict[str, dict[str, Any]],
) -> str:
    body_index = _graha_rashi_index(grahas.get(body))
    other_index = _graha_rashi_index(grahas.get(other))
    if body_index is None or other_index is None:
        return "unknown"
    house = _house_from(body_index, other_index)
    return "temporary_friend" if house in TEMPORARY_FRIEND_HOUSES else "temporary_enemy"


def _temporary_relationship_in_varga(
    body: str,
    other: str,
    body_rashi_index: int,
    code: str,
    varga: object,
    grahas: dict[str, dict[str, Any]],
) -> str:
    other_placement = _varga_placement(varga, other)
    other_index = _int_or_none(other_placement.get("rashi_index") if other_placement else None)
    if other_index is None and other_placement:
        try:
            other_index = RASHIS.index(str(other_placement.get("rashi") or ""))
        except ValueError:
            other_index = None
    if other_index is None:
        return _temporary_relationship(body, other, grahas)
    house = _house_from(body_rashi_index, other_index)
    return "temporary_friend" if house in TEMPORARY_FRIEND_HOUSES else "temporary_enemy"


def _compound_relationship(natural: str, temporary: str) -> str:
    if temporary == "unknown":
        return natural if natural in {"friend", "neutral", "enemy"} else "unknown"
    if natural == "friend":
        return "great_friend" if temporary == "temporary_friend" else "neutral"
    if natural == "neutral":
        return "friend" if temporary == "temporary_friend" else "enemy"
    if natural == "enemy":
        return "neutral" if temporary == "temporary_friend" else "great_enemy"
    return "unknown"


def _varga_dignity(body: str, rashi: str) -> tuple[str, float]:
    if not rashi:
        return "missing", 0.0
    if body in {"Rahu", "Ketu"}:
        return "node_dignity_pending", 0.25
    if rashi == EXALTATION_SIGNS.get(body):
        return "exaltation", 1.0
    if rashi in OWN_SIGNS.get(body, set()):
        return "own", 1.0
    if rashi == MOOLATRIKONA_SIGNS.get(body):
        return "moolatrikona", 1.0
    if rashi == _debilitation_sign(body):
        return "debilitation", 0.0

    try:
        lord = _rashi_lord(RASHIS.index(rashi))
    except ValueError:
        return "unknown", 0.0
    if lord in NATURAL_FRIENDS.get(body, set()):
        return "friend", 0.75
    if lord in NATURAL_NEUTRALS.get(body, set()):
        return "neutral", 0.5
    return "enemy", 0.25


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


def _nabhasa_yoga_signatures(
    chart: dict[str, Any],
    grahas: dict[str, dict[str, Any]],
) -> list[dict[str, object]]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    rashi_indices = _classical_graha_rashi_indices(grahas)
    if len(rashi_indices) != len(CLASSICAL_GRAHAS):
        return []

    rows = []
    occupied_rashis = set(rashi_indices.values())
    bodies = list(CLASSICAL_GRAHAS)
    if occupied_rashis.issubset(MOVABLE_RASHIS):
        rows.append(_yoga_payload("rajju_nabhasa", "Rajju Nabhasa", bodies, "calculated_needs_citation", reference="Rashi"))
    if occupied_rashis.issubset(FIXED_RASHIS):
        rows.append(_yoga_payload("musala_nabhasa", "Musala Nabhasa", bodies, "calculated_needs_citation", reference="Rashi"))
    if occupied_rashis.issubset(DUAL_RASHIS):
        rows.append(_yoga_payload("nala_nabhasa", "Nala Nabhasa", bodies, "calculated_needs_citation", reference="Rashi"))

    if lagna_index is None:
        return rows

    houses_by_body = {
        body: _house_from(lagna_index, rashi_index)
        for body, rashi_index in rashi_indices.items()
    }
    occupied_houses = frozenset(houses_by_body.values())
    rows.extend(_dala_nabhasa_yogas(houses_by_body))
    rows.extend(_akriti_nabhasa_yogas(occupied_houses, bodies))
    rows.extend(_sankhya_nabhasa_yogas(occupied_houses, bodies))
    return rows


def _classical_graha_rashi_indices(grahas: dict[str, dict[str, Any]]) -> dict[str, int]:
    rows = {}
    for body in CLASSICAL_GRAHAS:
        rashi_index = _int_or_none((grahas.get(body) or {}).get("rashi_index"))
        if rashi_index is not None:
            rows[body] = rashi_index
    return rows


def _dala_nabhasa_yogas(houses_by_body: dict[str, int]) -> list[dict[str, object]]:
    rows = []
    benefic_houses = {house for body, house in houses_by_body.items() if body in NATURAL_BENEFICS}
    malefic_houses = {house for body, house in houses_by_body.items() if body in NATURAL_MALEFICS}
    if benefic_houses and benefic_houses.issubset(KENDRA_HOUSES) and not malefic_houses.intersection(KENDRA_HOUSES):
        rows.append(
            _yoga_payload(
                "mala_nabhasa",
                "Mala Nabhasa",
                sorted(NATURAL_BENEFICS),
                "calculated_needs_citation",
                reference="Lagna",
            )
        )
    if malefic_houses and malefic_houses.issubset(KENDRA_HOUSES) and not benefic_houses.intersection(KENDRA_HOUSES):
        rows.append(
            _yoga_payload(
                "sarpa_nabhasa",
                "Sarpa Nabhasa",
                sorted(NATURAL_MALEFICS),
                "calculated_needs_citation",
                reference="Lagna",
            )
        )
    rows.extend(_vajra_yava_nabhasa_yogas(houses_by_body))
    return rows


def _vajra_yava_nabhasa_yogas(houses_by_body: dict[str, int]) -> list[dict[str, object]]:
    benefic_houses = {house for body, house in houses_by_body.items() if body in NATURAL_BENEFICS}
    malefic_houses = {house for body, house in houses_by_body.items() if body in NATURAL_MALEFICS}
    rows = []
    if benefic_houses.issubset({1, 7}) and malefic_houses.issubset({4, 10}) and benefic_houses and malefic_houses:
        rows.append(
            _yoga_payload(
                "vajra_nabhasa",
                "Vajra Nabhasa",
                list(CLASSICAL_GRAHAS),
                "calculated_needs_citation",
                reference="Lagna",
            )
        )
    if malefic_houses.issubset({1, 7}) and benefic_houses.issubset({4, 10}) and benefic_houses and malefic_houses:
        rows.append(
            _yoga_payload(
                "yava_nabhasa",
                "Yava Nabhasa",
                list(CLASSICAL_GRAHAS),
                "calculated_needs_citation",
                reference="Lagna",
            )
        )
    return rows


def _akriti_nabhasa_yogas(occupied_houses: frozenset[int], bodies: list[str]) -> list[dict[str, object]]:
    rows = []
    for key, name, patterns in AKRITI_NABHASA_PATTERNS:
        if occupied_houses in patterns:
            rows.append(_yoga_payload(key, name, bodies, "calculated_needs_citation", reference="Lagna"))
    return rows


def _sankhya_nabhasa_yogas(occupied_houses: frozenset[int], bodies: list[str]) -> list[dict[str, object]]:
    yoga = SANKHYA_NABHASA_YOGAS.get(len(occupied_houses))
    if not yoga:
        return []
    key, name = yoga
    return [_yoga_payload(key, name, bodies, "calculated_needs_citation", reference="Lagna")]


def _additional_named_yogas(
    chart: dict[str, Any],
    grahas: dict[str, dict[str, Any]],
) -> list[dict[str, object]]:
    rows = []
    rows.extend(_grahana_yogas(grahas))
    rows.extend(_shakata_yoga(grahas))
    rows.extend(_mangala_dosha_yoga(chart, grahas))
    rows.extend(_pravrajya_yogas(grahas))
    rows.extend(_subha_asubha_vesi_yogas(grahas))
    rows.extend(_dusthana_exchange_yoga(chart, grahas))
    rows.extend(_dhana_learning_raja_yogas(chart, grahas))
    rows.extend(_remaining_review_gated_yogas(chart, grahas))
    return rows


def _grahana_yogas(grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    rows = []
    rahu_index = _int_or_none((grahas.get("Rahu") or {}).get("rashi_index"))
    ketu_index = _int_or_none((grahas.get("Ketu") or {}).get("rashi_index"))
    node_indices = {index for index in (rahu_index, ketu_index) if index is not None}
    bodies = []
    for luminary in ("Chandra", "Surya"):
        rashi_index = _int_or_none((grahas.get(luminary) or {}).get("rashi_index"))
        if rashi_index in node_indices:
            bodies.append(luminary)
    if bodies:
        node = "Rahu" if rahu_index in node_indices else "Ketu"
        rows.append(_yoga_payload("grahana", "Grahana", [*bodies, node], "calculated_needs_citation", reference="Rahu/Ketu"))
    return rows


def _shakata_yoga(grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    moon_index = _int_or_none((grahas.get("Chandra") or {}).get("rashi_index"))
    guru_index = _int_or_none((grahas.get("Guru") or {}).get("rashi_index"))
    if moon_index is None or guru_index is None:
        return []
    if _house_from(moon_index, guru_index) in DUSTHANA_HOUSES:
        return [_yoga_payload("shakata", "Shakata", ["Chandra", "Guru"], "calculated_needs_citation", reference="Chandra")]
    return []


def _mangala_dosha_yoga(chart: dict[str, Any], grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    mars_index = _int_or_none((grahas.get("Mangala") or {}).get("rashi_index"))
    if mars_index is None:
        return []
    references = [
        _int_or_none((chart.get("ascendant") or {}).get("rashi_index")),
        _int_or_none((grahas.get("Chandra") or {}).get("rashi_index")),
        _int_or_none((grahas.get("Shukra") or {}).get("rashi_index")),
    ]
    risk_houses = {1, 2, 4, 7, 8, 12}
    if any(reference is not None and _house_from(reference, mars_index) in risk_houses for reference in references):
        return [_yoga_payload("mangala_dosha", "Mangala Dosha", ["Mangala"], "calculated_needs_citation", reference="Lagna/Chandra/Shukra")]
    return []


def _pravrajya_yogas(grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    by_rashi: dict[int, list[str]] = {}
    for body in CLASSICAL_GRAHAS:
        rashi_index = _int_or_none((grahas.get(body) or {}).get("rashi_index"))
        if rashi_index is not None:
            by_rashi.setdefault(rashi_index, []).append(body)
    rows = []
    for bodies in by_rashi.values():
        if len(bodies) >= 4:
            rows.append(_yoga_payload("pravrajya", "Pravrajya", sorted(bodies), "calculated_needs_citation", reference="Rashi"))
            rows.append(_yoga_payload("sannyasa", "Sannyasa", sorted(bodies), "calculated_needs_citation", reference="Rashi"))
            break
    return rows


def _subha_asubha_vesi_yogas(grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    sun = grahas.get("Surya")
    sun_index = _int_or_none(sun.get("rashi_index") if sun else None)
    if sun_index is None:
        return []
    second = _planets_in_house_from(grahas, sun_index, 2)
    rows = []
    benefics = sorted(body for body in second if body in NATURAL_BENEFICS)
    malefics = sorted(body for body in second if body in NATURAL_MALEFICS)
    if benefics:
        rows.append(_yoga_payload("subha_vesi", "Subha Vesi", benefics, "calculated_needs_citation", reference="Surya"))
    if malefics:
        rows.append(_yoga_payload("asubha_vesi", "Asubha Vesi", malefics, "calculated_needs_citation", reference="Surya"))
    return rows


def _dusthana_exchange_yoga(chart: dict[str, Any], grahas: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    if lagna_index is None:
        return []
    dusthana_lords = {house: _house_lord(lagna_index, house) for house in DUSTHANA_HOUSES}
    for house_a, lord_a in dusthana_lords.items():
        index_a = _int_or_none((grahas.get(lord_a) or {}).get("rashi_index"))
        if index_a is None:
            continue
        for house_b, lord_b in dusthana_lords.items():
            if house_a >= house_b:
                continue
            index_b = _int_or_none((grahas.get(lord_b) or {}).get("rashi_index"))
            if index_b is None:
                continue
            if index_a == _house_rashi_index(lagna_index, house_b) and index_b == _house_rashi_index(lagna_index, house_a):
                return [
                    _yoga_payload(
                        "dusthana_lord_exchange_viparita",
                        "Dusthana Lord Exchange Viparita",
                        _unique_bodies([lord_a, lord_b]),
                        "calculated_needs_citation",
                        reference="Lagna",
                    )
                ]
    return []


def _dhana_learning_raja_yogas(
    chart: dict[str, Any],
    grahas: dict[str, dict[str, Any]],
) -> list[dict[str, object]]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    if lagna_index is None:
        return []
    rows = []
    lagna_lord = _house_lord(lagna_index, 1)
    lagna_lord_house = _house_of_body(grahas, lagna_index, lagna_lord)
    if lagna_lord_house in KENDRA_HOUSES | TRIKONA_HOUSES:
        rows.append(_yoga_payload("lagna_lord_kendra_trikona_raja", "Lagna Lord Kendra/Trikona Raja", [lagna_lord], "calculated_needs_citation", reference="Lagna"))

    ninth_lord = _house_lord(lagna_index, 9)
    if _is_strong_by_sign(grahas, ninth_lord) and _house_of_body(grahas, lagna_index, ninth_lord) in KENDRA_HOUSES | TRIKONA_HOUSES:
        rows.append(_yoga_payload("lakshmi", "Lakshmi", _unique_bodies([lagna_lord, ninth_lord]), "calculated_needs_citation", reference="Lagna"))
        rows.append(_yoga_payload("lakshmi_dhana", "Lakshmi Dhana", _unique_bodies([lagna_lord, ninth_lord]), "calculated_needs_citation", reference="Lagna"))

    wisdom_bodies = ["Budha", "Guru", "Shukra"]
    if all(_house_of_body(grahas, lagna_index, body) in {1, 2, 4, 5, 7, 9, 10} for body in wisdom_bodies):
        rows.append(_yoga_payload("saraswati", "Saraswati", wisdom_bodies, "calculated_needs_citation", reference="Lagna"))

    if _associated(grahas, "Guru", "Budha") or _associated(grahas, "Guru", "Shukra"):
        rows.append(_yoga_payload("kalanidhi", "Kalanidhi", ["Guru"], "calculated_needs_citation", reference="Lagna/Chandra"))

    benefic_upachaya = [
        body for body in NATURAL_BENEFICS if _house_of_body(grahas, lagna_index, body) in {3, 6, 10, 11}
    ]
    moon_index = _int_or_none((grahas.get("Chandra") or {}).get("rashi_index"))
    if moon_index is not None:
        benefic_upachaya.extend(
            body
            for body in NATURAL_BENEFICS
            if body not in benefic_upachaya and _house_of_body(grahas, moon_index, body) in {3, 6, 10, 11}
        )
    if benefic_upachaya:
        rows.append(_yoga_payload("vasumati", "Vasumati", sorted(benefic_upachaya), "calculated_needs_citation", reference="Lagna/Chandra"))

    if moon_index is not None:
        guru_index = _int_or_none((grahas.get("Guru") or {}).get("rashi_index"))
        if guru_index is not None and _house_from(moon_index, guru_index) in {1, 2, 4, 5, 7, 9, 10, 11}:
            rows.append(_yoga_payload("chandra_guru_dhana", "Chandra Guru Dhana", ["Chandra", "Guru"], "calculated_needs_citation", reference="Chandra"))

    eleventh_lord = _house_lord(lagna_index, 11)
    if _is_strong_by_sign(grahas, eleventh_lord) or _house_of_body(grahas, lagna_index, eleventh_lord) in {1, 2, 5, 9, 10, 11}:
        rows.append(_yoga_payload("labha_lord_strength", "Labha Lord Strength", [eleventh_lord], "calculated_needs_citation", reference="Lagna"))

    dhana_link_count = _dhana_link_count(grahas, lagna_index)
    if dhana_link_count >= 1:
        rows.append(_yoga_payload("dhana_lagna_lord_second_eleventh", "Dhana Lagna/2nd/11th Link", [lagna_lord, _house_lord(lagna_index, 2), eleventh_lord], "calculated_needs_citation", reference="Lagna"))
    if dhana_link_count >= 2:
        rows.append(_yoga_payload("dwi_dhana", "Dwi Dhana", [], "calculated_needs_citation", reference="Lagna"))
    if dhana_link_count >= 3:
        rows.append(_yoga_payload("bahu_dhana", "Bahu Dhana", [], "calculated_needs_citation", reference="Lagna"))
    return rows


def _house_of_body(grahas: dict[str, dict[str, Any]], reference_index: int, body: str) -> int | None:
    rashi_index = _int_or_none((grahas.get(body) or {}).get("rashi_index"))
    if rashi_index is None:
        return None
    return _house_from(reference_index, rashi_index)


def _is_strong_by_sign(grahas: dict[str, dict[str, Any]], body: str) -> bool:
    graha = grahas.get(body) or {}
    rashi = str(graha.get("rashi") or "")
    return rashi in OWN_SIGNS.get(body, set()) or rashi == EXALTATION_SIGNS.get(body)


def _dhana_link_count(grahas: dict[str, dict[str, Any]], lagna_index: int) -> int:
    pairs = [
        (_house_lord(lagna_index, 1), _house_lord(lagna_index, 2)),
        (_house_lord(lagna_index, 1), _house_lord(lagna_index, 11)),
        (_house_lord(lagna_index, 2), _house_lord(lagna_index, 11)),
        (_house_lord(lagna_index, 5), _house_lord(lagna_index, 9)),
    ]
    count = 0
    for first, second in pairs:
        if first == second or _associated(grahas, first, second):
            count += 1
    for house in (2, 5, 9, 11):
        lord = _house_lord(lagna_index, house)
        if _is_strong_by_sign(grahas, lord):
            count += 1
    if sum(1 for body in NATURAL_BENEFICS if _house_of_body(grahas, lagna_index, body) in {3, 6, 10, 11}) >= 2:
        count += 1
    return count


def _remaining_review_gated_yogas(
    chart: dict[str, Any],
    grahas: dict[str, dict[str, Any]],
) -> list[dict[str, object]]:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    if lagna_index is None:
        return []
    rows = []
    lagna_lord = _house_lord(lagna_index, 1)
    fourth_lord = _house_lord(lagna_index, 4)
    seventh_lord = _house_lord(lagna_index, 7)
    ninth_lord = _house_lord(lagna_index, 9)
    tenth_lord = _house_lord(lagna_index, 10)
    eleventh_lord = _house_lord(lagna_index, 11)
    benefic_kendra = [body for body in NATURAL_BENEFICS if _house_of_body(grahas, lagna_index, body) in KENDRA_HOUSES]
    benefic_chamara_houses = [
        body for body in NATURAL_BENEFICS if _house_of_body(grahas, lagna_index, body) in {7, 9, 10}
    ]

    if _is_strong_by_sign(grahas, seventh_lord) and _house_of_body(grahas, lagna_index, seventh_lord) in KENDRA_HOUSES:
        rows.append(_yoga_payload("sri_natha", "Sri Natha", [seventh_lord], "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, lagna_lord) and (_is_strong_by_sign(grahas, ninth_lord) or _is_strong_by_sign(grahas, tenth_lord)):
        rows.append(_yoga_payload("raja_sambandha", "Raja Sambandha", _unique_bodies([lagna_lord, ninth_lord, tenth_lord]), "calculated_needs_citation", reference="Lagna"))
        rows.append(_yoga_payload("maharaja", "Maharaja", _unique_bodies([lagna_lord, ninth_lord, tenth_lord]), "calculated_needs_citation", reference="Lagna"))
    amatya = _chara_karakas(grahas).get("AmK")
    if amatya and _house_of_body(grahas, lagna_index, amatya) in TRIKONA_HOUSES and not _has_yoga_key(rows, "raja_sambandha"):
        rows.append(_yoga_payload("raja_sambandha", "Raja Sambandha", [amatya], "calculated_needs_citation", reference="Amatya karaka"))
    if _is_strong_by_sign(grahas, lagna_lord) and benefic_kendra:
        rows.append(_yoga_payload("chamara", "Chamara", [lagna_lord, *sorted(benefic_kendra)], "calculated_needs_citation", reference="Lagna"))
        rows.append(_yoga_payload("mridanga", "Mridanga", [lagna_lord], "calculated_needs_citation", reference="Lagna"))
    if len(benefic_chamara_houses) >= 2 and not _has_yoga_key(rows, "chamara"):
        rows.append(_yoga_payload("chamara", "Chamara", sorted(benefic_chamara_houses), "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, fourth_lord) and _is_strong_by_sign(grahas, ninth_lord):
        rows.append(_yoga_payload("kahala", "Kahala", _unique_bodies([fourth_lord, ninth_lord]), "calculated_needs_citation", reference="Lagna"))
    if benefic_kendra and not _classical_bodies_in_houses(grahas, lagna_index, {6, 8}):
        rows.append(_yoga_payload("parvata", "Parvata", sorted(benefic_kendra), "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, eleventh_lord) and _is_strong_by_sign(grahas, lagna_lord):
        rows.append(_yoga_payload("indra", "Indra", [eleventh_lord], "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, fifth_lord := _house_lord(lagna_index, 5)) and _is_strong_by_sign(grahas, ninth_lord):
        rows.append(_yoga_payload("sankha", "Sankha", _unique_bodies([fifth_lord, ninth_lord]), "calculated_needs_citation", reference="Lagna"))
    rows.extend(_rare_named_review_yogas(chart, grahas, lagna_index))
    rows.extend(_jhora_yogada_yogas(chart, grahas, lagna_index))
    rows.extend(_risk_review_yogas(grahas, lagna_index))
    return rows


def _rare_named_review_yogas(
    chart: dict[str, Any],
    grahas: dict[str, dict[str, Any]],
    lagna_index: int,
) -> list[dict[str, object]]:
    rows = []
    lagna_lord = _house_lord(lagna_index, 1)
    ninth_lord = _house_lord(lagna_index, 9)
    eleventh_lord = _house_lord(lagna_index, 11)
    tenth_lord = _house_lord(lagna_index, 10)
    strong_kendra_kona = [
        body
        for body in CLASSICAL_GRAHAS
        if _is_strong_by_sign(grahas, body)
        and _house_of_body(grahas, lagna_index, body) in KENDRA_HOUSES | TRIKONA_HOUSES
    ]
    if _is_strong_by_sign(grahas, "Guru") and _is_strong_by_sign(grahas, "Shukra"):
        rows.append(_yoga_payload("brahma", "Brahma", ["Guru", "Shukra"], "calculated_needs_citation", reference="Lagna"))
    if (
        _body_in_kendra_from_body(grahas, "Guru", ninth_lord)
        and _body_in_kendra_from_body(grahas, "Shukra", eleventh_lord)
        and (
            _body_in_kendra_from_body(grahas, "Budha", lagna_lord)
            or _body_in_kendra_from_body(grahas, "Budha", tenth_lord)
        )
        and not _has_yoga_key(rows, "brahma")
    ):
        rows.append(_yoga_payload("brahma", "Brahma", ["Guru", "Shukra", "Budha"], "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, ninth_lord):
        rows.append(_yoga_payload("bhagya", "Bhagya", [ninth_lord], "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, "Budha") or _is_strong_by_sign(grahas, "Guru"):
        rows.append(_yoga_payload("vidyut", "Vidyut", [body for body in ("Budha", "Guru") if _is_strong_by_sign(grahas, body)], "calculated_needs_citation", reference="Lagna"))
    if eleventh_lord == "Shukra" and _is_strong_by_sign(grahas, "Shukra") and _body_in_kendra_from_body(grahas, "Shukra", lagna_lord) and not _has_yoga_key(rows, "vidyut"):
        rows.append(_yoga_payload("vidyut", "Vidyut", ["Shukra"], "calculated_needs_citation", reference="11th lord"))
    if len(strong_kendra_kona) >= 2 and not _has_yoga_key(rows, "mridanga"):
        rows.append(_yoga_payload("mridanga", "Mridanga", sorted(strong_kendra_kona), "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, lagna_lord) and _is_strong_by_sign(grahas, "Chandra"):
        rows.append(_yoga_payload("pushkala", "Pushkala", [lagna_lord, "Chandra"], "calculated_needs_citation", reference="Lagna/Chandra"))
    if _is_strong_by_sign(grahas, "Guru"):
        rows.append(_yoga_payload("vasishta", "Vasishta", ["Guru"], "calculated_needs_citation", reference="Lagna"))
        rows.append(_yoga_payload("garuda", "Garuda", ["Guru"], "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, lagna_lord):
        rows.append(_yoga_payload("parijata", "Parijata", [lagna_lord], "calculated_needs_citation", reference="Lagna"))
    if _node_afflicts_reference(grahas, lagna_index) or _node_afflicts_reference(grahas, _int_or_none((grahas.get("Chandra") or {}).get("rashi_index"))):
        rows.append(_yoga_payload("naga", "Naga", ["Rahu", "Ketu"], "calculated_needs_citation", reference="Rahu/Ketu"))
    if _is_kala_sarpa(grahas):
        rows.append(_yoga_payload("kala_sarpa_contested", "Kala Sarpa Contested", ["Rahu", "Ketu"], "calculated_needs_citation", reference="Rahu/Ketu"))
    if _birth_supports_maha_bhagya(chart, grahas, lagna_index):
        rows.append(_yoga_payload("maha_bhagya", "Maha Bhagya", ["Surya", "Chandra"], "calculated_needs_citation", reference="Lagna"))
    if all(_house_of_body(grahas, lagna_index, body) in MOVABLE_RASHIS for body in CLASSICAL_GRAHAS):
        rows.append(_yoga_payload("rajju_variant", "Rajju Variant", list(CLASSICAL_GRAHAS), "calculated_needs_citation", reference="Rashi"))
    if _is_strong_by_sign(grahas, "Shukra") or _is_strong_by_sign(grahas, "Chandra"):
        rows.append(_yoga_payload("go", "Go", [body for body in ("Chandra", "Shukra") if _is_strong_by_sign(grahas, body)], "calculated_needs_citation", reference="Lagna"))
    if _is_strong_by_sign(grahas, lagna_lord) and _is_strong_by_sign(grahas, ninth_lord):
        rows.append(_yoga_payload("adrogate_raja_research", "Adrogate Raja Research", _unique_bodies([lagna_lord, ninth_lord]), "calculated_needs_citation", reference="Lagna"))
    if _house_of_body(grahas, lagna_index, "Guru") in KENDRA_HOUSES | TRIKONA_HOUSES:
        rows.append(_yoga_payload("kesari_variant", "Kesari Variant", ["Guru"], "calculated_needs_citation", reference="Lagna/Chandra"))
    return rows


def _risk_review_yogas(grahas: dict[str, dict[str, Any]], lagna_index: int) -> list[dict[str, object]]:
    rows = []
    moon_index = _int_or_none((grahas.get("Chandra") or {}).get("rashi_index"))
    shani_index = _int_or_none((grahas.get("Shani") or {}).get("rashi_index"))
    if moon_index is not None and shani_index is not None and _house_from(moon_index, shani_index) in {1, 7}:
        rows.append(_yoga_payload("visha", "Visha", ["Chandra", "Shani"], "calculated_needs_citation", reference="Chandra"))
    if _body_in_dusthana_or_debilitated(grahas, lagna_index, _house_lord(lagna_index, 2)) and _body_in_dusthana_or_debilitated(grahas, lagna_index, _house_lord(lagna_index, 11)):
        rows.append(_yoga_payload("daridra", "Daridra", [_house_lord(lagna_index, 2), _house_lord(lagna_index, 11)], "calculated_needs_citation", reference="Lagna"))
    if _body_in_dusthana_or_debilitated(grahas, lagna_index, _house_lord(lagna_index, 1)) and moon_index is not None:
        rows.append(_yoga_payload("balarishta", "Balarishta", [_house_lord(lagna_index, 1), "Chandra"], "calculated_needs_citation", reference="Lagna/Chandra"))
    if any(row["key"] in {"balarishta", "daridra"} for row in rows) and any(_house_of_body(grahas, lagna_index, body) in KENDRA_HOUSES for body in NATURAL_BENEFICS):
        rows.append(_yoga_payload("arishta_bhanga", "Arishta Bhanga", sorted(NATURAL_BENEFICS), "calculated_needs_citation", reference="Lagna"))
    if _node_afflicts_reference(grahas, _house_rashi_index(lagna_index, 9)) or _node_afflicts_reference(grahas, _int_or_none((grahas.get("Surya") or {}).get("rashi_index"))):
        rows.append(_yoga_payload("pitru_dosha_research", "Pitru Dosha Research", ["Surya", "Rahu", "Ketu"], "calculated_needs_citation", reference="Surya/9th"))
    if _house_of_body(grahas, lagna_index, "Shani") in {9, 12} or _node_afflicts_reference(grahas, _int_or_none((grahas.get("Shani") or {}).get("rashi_index"))):
        rows.append(_yoga_payload("tapasvi", "Tapasvi", ["Shani"], "calculated_needs_citation", reference="Lagna"))
    if _body_in_dusthana_or_debilitated(grahas, lagna_index, _house_lord(lagna_index, 1)):
        rows.append(_yoga_payload("adhama", "Adhama", [_house_lord(lagna_index, 1)], "calculated_needs_citation", reference="Lagna"))
    return rows


def _jhora_yogada_yogas(
    chart: dict[str, Any],
    grahas: dict[str, dict[str, Any]],
    lagna_index: int,
) -> list[dict[str, object]]:
    point_indices = _special_point_indices(chart)
    rows = []
    for point_key, yoga_key, yoga_name in (
        ("ghati_lagna", "yogada_gl", "Yogada (GL)"),
        ("hora_lagna", "yogada_hl", "Yogada (HL)"),
    ):
        point_index = point_indices.get(point_key)
        if point_index is None:
            continue
        bodies = [
            body
            for body in VIMSOPAKA_BODIES
            if _associated_with_sign(grahas, body, lagna_index)
            and _associated_with_sign(grahas, body, point_index)
        ]
        if bodies:
            rows.append(_yoga_payload(yoga_key, yoga_name, bodies, "calculated_needs_citation", reference=point_key))
    return rows


def _special_point_indices(chart: dict[str, Any]) -> dict[str, int]:
    output: dict[str, int] = {}
    special = special_points(chart)
    vedic_points = ((special.get("vedic_points") or {}).get("items") or [])
    for item in vedic_points:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "")
        longitude = _float_or_none(item.get("longitude"))
        if key and longitude is not None:
            output[key] = int(normalize_degrees(longitude) // 30)
    return output


def _associated_with_sign(grahas: dict[str, dict[str, Any]], body: str, sign_index: int) -> bool:
    body_index = _int_or_none((grahas.get(body) or {}).get("rashi_index"))
    if body_index is None:
        return False
    return (
        body_index == sign_index
        or _body_owns_sign(body, sign_index)
        or _jaimini_rashi_aspect(body_index, sign_index)
    )


def _body_owns_sign(body: str, sign_index: int) -> bool:
    if RASHI_LORDS.get(sign_index % len(RASHIS)) == body:
        return True
    return sign_index % len(RASHIS) in NODE_CO_LORD_SIGNS.get(body, set())


def _jaimini_rashi_aspect(from_sign: int, to_sign: int) -> bool:
    from_sign %= len(RASHIS)
    to_sign %= len(RASHIS)
    if from_sign == to_sign:
        return True
    if from_sign in DUAL_RASHIS:
        return to_sign in DUAL_RASHIS
    if from_sign in MOVABLE_RASHIS:
        return to_sign in FIXED_RASHIS and to_sign != (from_sign + 1) % len(RASHIS)
    if from_sign in FIXED_RASHIS:
        return to_sign in MOVABLE_RASHIS and to_sign != (from_sign - 1) % len(RASHIS)
    return False


def _classical_bodies_in_houses(grahas: dict[str, dict[str, Any]], lagna_index: int, houses: set[int]) -> list[str]:
    return [body for body in CLASSICAL_GRAHAS if _house_of_body(grahas, lagna_index, body) in houses]


def _node_afflicts_reference(grahas: dict[str, dict[str, Any]], reference_index: int | None) -> bool:
    if reference_index is None:
        return False
    return any(_int_or_none((grahas.get(node) or {}).get("rashi_index")) == reference_index for node in ("Rahu", "Ketu"))


def _body_in_dusthana_or_debilitated(grahas: dict[str, dict[str, Any]], lagna_index: int, body: str) -> bool:
    graha = grahas.get(body) or {}
    rashi = str(graha.get("rashi") or "")
    return _house_of_body(grahas, lagna_index, body) in DUSTHANA_HOUSES or rashi == _debilitation_sign(body)


def _is_kala_sarpa(grahas: dict[str, dict[str, Any]]) -> bool:
    rahu = _int_or_none((grahas.get("Rahu") or {}).get("rashi_index"))
    ketu = _int_or_none((grahas.get("Ketu") or {}).get("rashi_index"))
    if rahu is None or ketu is None:
        return False
    indices = [_int_or_none((grahas.get(body) or {}).get("rashi_index")) for body in CLASSICAL_GRAHAS]
    if any(index is None for index in indices):
        return False
    forward_span = {(rahu + offset) % 12 for offset in range((ketu - rahu) % 12 + 1)}
    backward_span = {(ketu + offset) % 12 for offset in range((rahu - ketu) % 12 + 1)}
    return all(index in forward_span for index in indices if index is not None) or all(
        index in backward_span for index in indices if index is not None
    )


def _birth_supports_maha_bhagya(chart: dict[str, Any], grahas: dict[str, dict[str, Any]], lagna_index: int) -> bool:
    sun_house = _house_of_body(grahas, lagna_index, "Surya")
    moon_house = _house_of_body(grahas, lagna_index, "Chandra")
    return sun_house in KENDRA_HOUSES | TRIKONA_HOUSES and moon_house in KENDRA_HOUSES | TRIKONA_HOUSES


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


def _yoga_catalog_rows() -> list[dict[str, Any]]:
    try:
        from apps.interpretations.yoga_catalog import yoga_registry
    except ImportError:
        return []
    return yoga_registry()


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


def _argala_bodies_for_house(chart: dict[str, Any], reference_index: int, house: int) -> list[str]:
    return [
        str(graha.get("body"))
        for graha in chart.get("grahas", [])
        if _int_or_none(graha.get("rashi_index")) is not None
        and _house_from(reference_index, int(graha["rashi_index"])) == house
    ]


def _argala_pair_rows(
    chart: dict[str, Any],
    reference_index: int,
    pairs: list[tuple[int, int]],
    level: str,
) -> list[dict[str, object]]:
    rows = []
    for argala_house, obstruction_house in pairs:
        argala_bodies = _argala_bodies_for_house(chart, reference_index, argala_house)
        obstruction_bodies = _argala_bodies_for_house(chart, reference_index, obstruction_house)
        argala_count = len(argala_bodies)
        obstruction_count = len(obstruction_bodies)
        if argala_count == 0 and obstruction_count == 0:
            net_effect = "not_present"
        elif obstruction_count >= argala_count and obstruction_count > 0:
            net_effect = "obstructed"
        else:
            net_effect = "active"
        rows.append(
            {
                "level": level,
                "argala_house": argala_house,
                "obstruction_house": obstruction_house,
                "argala_bodies": argala_bodies,
                "obstruction_bodies": obstruction_bodies,
                "net_effect": net_effect,
            }
        )
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


def _special_points_status(
    lots: list[dict[str, object]],
    upagrahas: dict[str, object],
    vedic_points: dict[str, object],
) -> str:
    upagraha_status = str(upagrahas.get("status") or "")
    vedic_status = str(vedic_points.get("status") or "")
    if not lots and not upagrahas.get("items") and not vedic_points.get("items"):
        return "missing_inputs"
    if "missing" in upagraha_status or "invalid" in upagraha_status:
        return "partial_missing_upagraha_inputs"
    if "needs_jhora" in upagraha_status:
        return "calculated_with_source_review"
    if "single_jhora_fixture_matched" in upagraha_status or "single_jhora_fixture_matched" in vedic_status:
        return "calculated_single_jhora_fixture_matched_core_catalog"
    if "calculated" in upagraha_status or "calculated" in vedic_status or lots:
        return "calculated_with_source_review"
    return "source_review_required"


def _upagrahas(chart: dict[str, Any]) -> dict[str, object]:
    solar_items = _solar_upagrahas(chart)
    context = chart.get("upagraha_context")
    if isinstance(context, dict):
        segment = context.get("gulika")
        start_longitude = _body_longitude(context.get("gulika_start_ascendant"))
        midpoint_longitude = _body_longitude(context.get("gulika_midpoint_ascendant"))
        if midpoint_longitude is None:
            midpoint_longitude = _body_longitude(context.get("gulika_ascendant"))
        if not context.get("split_gulika_maandi") and isinstance(segment, dict) and midpoint_longitude is not None:
            item = _point_payload("gulika", "Gulika/Mandi", midpoint_longitude)
            item["local_time"] = str(segment.get("local_time") or "")
            item["period"] = str(segment.get("period") or "")
            item["segment"] = segment.get("segment")
            item["starts_at"] = segment.get("starts_at")
            item["ends_at"] = segment.get("ends_at")
            item["midpoint"] = segment.get("midpoint")
            item["metadata"] = {"anchor": "segment_midpoint"}
            item["calculation_note"] = (
                "Actual sunrise/sunset segment with Lagna at Gulika midpoint; use JHora profile to split Gulika and Maandi."
            )
            return {
                "status": "calculated_needs_jhora_split_profile",
                "method": "Gulika/Mandi uses actual sunrise/sunset period segmentation and midpoint Lagna.",
                "items": [item, *solar_items],
            }
        if isinstance(segment, dict) and (start_longitude is not None or midpoint_longitude is not None):
            items = []
            if start_longitude is not None:
                item = _point_payload("gulika", "Gulika", start_longitude)
                item["local_time"] = _time_from_iso(str(segment.get("starts_at") or ""))
                item["period"] = str(segment.get("period") or "")
                item["segment"] = segment.get("segment")
                item["starts_at"] = segment.get("starts_at")
                item["ends_at"] = segment.get("ends_at")
                item["midpoint"] = segment.get("midpoint")
                item["metadata"] = {"anchor": "segment_start"}
                item["calculation_note"] = (
                    "Actual sunrise/sunset Saturn segment with Lagna at segment start."
                )
                items.append(item)
            if midpoint_longitude is not None:
                item = _point_payload("maandi", "Maandi", midpoint_longitude)
                item["local_time"] = str(segment.get("local_time") or "")
                item["period"] = str(segment.get("period") or "")
                item["segment"] = segment.get("segment")
                item["starts_at"] = segment.get("starts_at")
                item["ends_at"] = segment.get("ends_at")
                item["midpoint"] = segment.get("midpoint")
                item["metadata"] = {"anchor": "segment_midpoint"}
                item["calculation_note"] = (
                    "Actual sunrise/sunset Saturn segment with Lagna at segment midpoint."
                )
                items.append(item)
            return {
                "status": "calculated_single_jhora_fixture_matched",
                "method": "Gulika uses Saturn-segment start; Maandi uses Saturn-segment midpoint; Sterlitamak JHora fixture matched these checked points.",
                "verified_fixture": "sterlitamak_1998_jhora_special_points",
                "items": [*items, *solar_items],
            }

    birth = chart.get("birth", {})
    raw_moment = birth.get("local_datetime") if isinstance(birth, dict) else None
    ascendant = _body_longitude(chart.get("ascendant"))
    if not isinstance(raw_moment, str):
        return {
            "status": "partial_missing_birth_time" if solar_items else "missing_birth_time",
            "items": solar_items,
            "method": "Needs local birth datetime for Gulika; solar upagrahas use Surya longitude.",
        }
    try:
        moment = datetime.fromisoformat(raw_moment)
    except ValueError:
        return {
            "status": "partial_invalid_birth_time" if solar_items else "invalid_birth_time",
            "items": solar_items,
            "method": "Needs ISO local birth datetime for Gulika; solar upagrahas use Surya longitude.",
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
        "method": (
            "Civil 06:00-18:00/18:00-06:00 Saturn segment approximation plus solar "
            "upagrahas; pending JHora audit."
        ),
        "items": [item, *solar_items],
    }


def _solar_upagrahas(chart: dict[str, Any]) -> list[dict[str, object]]:
    sun = _body_longitude(_graha_index(chart).get("Surya"))
    if sun is None:
        return []

    dhuma = normalize_degrees(sun + 133.33333333333334)
    vyatipata = normalize_degrees(360.0 - dhuma)
    parivesha = normalize_degrees(vyatipata + 180.0)
    indrachapa = normalize_degrees(360.0 - parivesha)
    upaketu = normalize_degrees(indrachapa + 16.666666666666668)
    return [
        _solar_upagraha_payload("dhuma", "Dhuma", dhuma),
        _solar_upagraha_payload("vyatipata", "Vyatipata", vyatipata),
        _solar_upagraha_payload("parivesha", "Parivesha", parivesha),
        _solar_upagraha_payload("indrachapa", "Indrachapa", indrachapa),
        _solar_upagraha_payload("upaketu", "Upaketu", upaketu),
    ]


def _solar_upagraha_payload(key: str, name: str, longitude: float) -> dict[str, object]:
    item = _point_payload(key, name, longitude)
    item["calculation_note"] = "Solar upagraha from Surya longitude."
    return item


def _vedic_points(chart: dict[str, Any]) -> dict[str, object]:
    items = []
    for point in (
        _indu_lagna(chart),
        _bhava_lagna(chart),
        _hora_lagna_point(chart),
        _ghati_lagna(chart),
    ):
        if point:
            items.append(point)
    return {
        "status": "calculated_single_jhora_fixture_matched" if items else "pending_source_mapping",
        "method": (
            "Indu/Dhana Lagna plus Bhava/Hora/Ghati Lagna calculations. "
            "Checked Sterlitamak JHora fixture matched implemented points; remaining JHora special points are not all implemented."
        ),
        "verified_fixture": "sterlitamak_1998_jhora_special_points" if items else "",
        "items": items,
    }


def _indu_lagna(chart: dict[str, Any]) -> dict[str, object] | None:
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    moon = _graha_index(chart).get("Chandra") or {}
    moon_index = _int_or_none(moon.get("rashi_index"))
    if lagna_index is None or moon_index is None:
        return None
    lagna_ninth_lord = _house_lord(lagna_index, 9)
    moon_ninth_lord = _house_lord(moon_index, 9)
    if lagna_ninth_lord not in INDU_KALAS or moon_ninth_lord not in INDU_KALAS:
        return None
    kala_sum = INDU_KALAS[lagna_ninth_lord] + INDU_KALAS[moon_ninth_lord]
    remainder = kala_sum % 12 or 12
    rashi_index = (moon_index + remainder - 1) % len(RASHIS)
    moon_longitude = _body_longitude(moon)
    sign_degree = normalize_degrees(moon_longitude) % 30.0 if moon_longitude is not None else 0.0
    longitude = rashi_index * 30.0 + sign_degree
    point = _point_payload("indu_lagna", "Indu/Dhana Lagna", longitude)
    point["metadata"] = {
        "lagna_ninth_lord": lagna_ninth_lord,
        "moon_ninth_lord": moon_ninth_lord,
        "kala_sum": kala_sum,
        "remainder": remainder,
        "sign_degree_source": "Chandra",
        "counted_from": "Chandra",
        "audit_status": "single_jhora_fixture_matched",
        "verified_fixture": "sterlitamak_1998_jhora_special_points",
    }
    return point


def _bhava_lagna(chart: dict[str, Any]) -> dict[str, object] | None:
    return _time_progressed_lagna(
        chart,
        "bhava_lagna",
        "Bhava Lagna",
        degrees_per_ghati=6.0,
        formula_note="Surya at sunrise plus 6 degrees per elapsed ghati from sunrise.",
    )


def _hora_lagna_point(chart: dict[str, Any]) -> dict[str, object] | None:
    return _time_progressed_lagna(
        chart,
        "hora_lagna",
        "Hora Lagna",
        degrees_per_ghati=12.0,
        formula_note="Surya at sunrise plus 12 degrees per elapsed ghati from sunrise.",
    )


def _ghati_lagna(chart: dict[str, Any]) -> dict[str, object] | None:
    return _time_progressed_lagna(
        chart,
        "ghati_lagna",
        "Ghati Lagna",
        degrees_per_ghati=30.0,
        formula_note="Surya at sunrise plus 30 degrees per elapsed ghati from sunrise.",
    )


def _time_progressed_lagna(
    chart: dict[str, Any],
    key: str,
    name: str,
    *,
    degrees_per_ghati: float,
    formula_note: str,
) -> dict[str, object] | None:
    moment = _birth_moment(chart)
    if moment is None:
        return None
    sunrise, _, _ = _solar_day_bounds(chart, moment)
    period_start = sunrise - timedelta(days=1) if moment < sunrise else sunrise
    elapsed_hours = max(0.0, (moment - period_start).total_seconds() / 3600.0)
    elapsed_ghatis = elapsed_hours * 2.5
    special_context = chart.get("special_lagna_context") if isinstance(chart.get("special_lagna_context"), dict) else {}
    base_longitude = _body_longitude(special_context.get("surya_at_sunrise") if isinstance(special_context, dict) else None)
    if base_longitude is None:
        base_longitude = _body_longitude(_graha_index(chart).get("Surya"))
    if base_longitude is None:
        return None
    point = _point_payload(key, name, base_longitude + elapsed_ghatis * degrees_per_ghati)
    point["metadata"] = {
        "base": "surya_at_sunrise",
        "base_longitude": round(base_longitude, 6),
        "elapsed_hours_from_sunrise": round(elapsed_hours, 6),
        "elapsed_ghatis_from_sunrise": round(elapsed_ghatis, 6),
        "degrees_per_ghati": degrees_per_ghati,
        "formula_note": formula_note,
        "audit_status": "single_jhora_fixture_matched",
        "verified_fixture": "sterlitamak_1998_jhora_special_points",
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


def _sthana_bala_full(body: str, graha: dict[str, Any], chart: dict[str, Any]) -> dict[str, object]:
    longitude = _body_longitude(graha)
    lagna_index = _int_or_none((chart.get("ascendant") or {}).get("rashi_index"))
    rashi_index = _int_or_none(graha.get("rashi_index"))
    uccha = _uccha_bala(body, longitude) if longitude is not None else 0.0
    saptavargaja, saptavargaja_details = _saptavargaja_bala(body, graha, chart)
    ojayugma, ojayugma_details = _ojayugma_bala(body, graha, chart)
    kendradi = _kendradi_bala(lagna_index, rashi_index)
    drekkana = _drekkana_bala(body, longitude)
    total = round(uccha + saptavargaja + ojayugma + kendradi + drekkana, 2)
    return {
        "uccha": uccha,
        "saptavargaja": saptavargaja,
        "saptavargaja_details": saptavargaja_details,
        "ojayugma": ojayugma,
        "ojayugma_details": ojayugma_details,
        "kendradi": kendradi,
        "drekkana": drekkana,
        "total": total,
        "unit": "virupa",
    }


def _saptavargaja_bala(
    body: str,
    graha: dict[str, Any],
    chart: dict[str, Any],
) -> tuple[float, list[dict[str, object]]]:
    total = 0.0
    details = []
    for code in SAPTAVARGA_CODES:
        placement = _varga_rashi(body, graha, chart, code)
        if placement is None:
            dignity, value = "missing", 0.0
            rashi = ""
        else:
            _, rashi = placement
            dignity, _ = _varga_dignity(body, rashi)
            value = STHANA_VARGA_DIGNITY_BALA.get(dignity, 0.0)
        total += value
        details.append({"varga": code, "rashi": rashi, "dignity": dignity, "virupa": value})
    return round(total, 2), details


def _ojayugma_bala(
    body: str,
    graha: dict[str, Any],
    chart: dict[str, Any],
) -> tuple[float, list[dict[str, object]]]:
    expected_odd = body not in FEMALE_BODIES
    total = 0.0
    details = []
    for code in ("D1", "D9"):
        placement = _varga_rashi(body, graha, chart, code)
        if placement is None:
            details.append({"varga": code, "rashi": "", "matches": False, "virupa": 0.0})
            continue
        rashi_index, rashi = placement
        matches = _is_odd_sign(rashi_index) == expected_odd
        value = 15.0 if matches else 0.0
        total += value
        details.append({"varga": code, "rashi": rashi, "matches": matches, "virupa": value})
    return round(total, 2), details


def _kendradi_bala(lagna_index: int | None, rashi_index: int | None) -> float:
    if lagna_index is None or rashi_index is None:
        return 0.0
    house = _house_from(lagna_index, rashi_index)
    if house in KENDRA_HOUSES:
        return 60.0
    if house in {2, 5, 8, 11}:
        return 30.0
    return 15.0


def _drekkana_bala(body: str, longitude: float | None) -> float:
    if longitude is None:
        return 0.0
    decan = floor((normalize_degrees(longitude) % 30.0) / 10.0) + 1
    if body in MALE_BODIES and decan == 1:
        return 15.0
    if body in FEMALE_BODIES and decan == 2:
        return 15.0
    if body in NEUTER_BODIES and decan == 3:
        return 15.0
    return 0.0


def _dig_bala_full(
    body: str,
    chart: dict[str, Any],
    longitude: float,
    lagna_index: int | None,
    rashi_index: int | None,
) -> dict[str, object]:
    target_house = DIG_BALA_HOUSES.get(body)
    if target_house is None:
        return {"exact": 0.0, "whole_sign_proxy": 0.0, "unit": "virupa"}
    nil_house = ((target_house + 5) % 12) + 1
    nil_cusp, cusp_source = _house_cusp_longitude(chart, lagna_index, nil_house)
    target_cusp, _ = _house_cusp_longitude(chart, lagna_index, target_house)
    if nil_cusp is None:
        exact = _dig_bala(body, lagna_index, rashi_index)
    else:
        distance = _angular_distance(longitude, nil_cusp)
        exact = round(min(60.0, distance / 3.0), 2)
    return {
        "exact": exact,
        "whole_sign_proxy": _dig_bala(body, lagna_index, rashi_index),
        "target_house": target_house,
        "target_cusp": target_cusp,
        "nil_house": nil_house,
        "nil_cusp": nil_cusp,
        "cusp_source": cusp_source,
        "unit": "virupa",
    }


def _kala_bala_full(
    body: str,
    chart: dict[str, Any],
    grahas: dict[str, dict[str, Any]],
) -> dict[str, object]:
    moment = _birth_moment(chart)
    if moment is None:
        return {
            "natonnata": 0.0,
            "paksha": 0.0,
            "tribhaga": 0.0,
            "abda_masa_vara_hora": {"value": 0.0, "components": {}, "lords": {}},
            "ayana": 0.0,
            "yuddha": {"value": 0.0, "wars": []},
            "total": 0.0,
            "unit": "virupa",
            "status": "missing_birth_time",
        }
    natonnata = _natonnata_bala(body, chart, moment)
    paksha = _paksha_bala(body, grahas)
    tribhaga = _tribhaga_bala(body, chart, moment)
    abda_masa_vara_hora = _abda_masa_vara_hora_bala(body, chart, moment)
    ayana = _ayana_bala(body, grahas.get(body))
    yuddha = _yuddha_bala(body, grahas)
    total = round(
        natonnata
        + paksha
        + tribhaga
        + float(abda_masa_vara_hora["value"])
        + ayana
        + float(yuddha["value"]),
        2,
    )
    return {
        "natonnata": natonnata,
        "paksha": paksha,
        "tribhaga": tribhaga,
        "abda_masa_vara_hora": abda_masa_vara_hora,
        "ayana": ayana,
        "yuddha": yuddha,
        "total": total,
        "unit": "virupa",
        "status": "calculated_with_solar_fallbacks",
    }


def _natonnata_bala(body: str, chart: dict[str, Any], moment: datetime) -> float:
    if body == "Budha":
        return 60.0
    minutes = _mean_local_minutes(chart, moment)
    distance_from_noon = abs(minutes - 720.0)
    if distance_from_noon > 720.0:
        distance_from_noon = 1440.0 - distance_from_noon
    day_bala = max(0.0, 60.0 * (1.0 - distance_from_noon / 720.0))
    night_bala = 60.0 - day_bala
    return round(day_bala if body in DAY_STRONG_BODIES else night_bala, 2)


def _paksha_bala(body: str, grahas: dict[str, dict[str, Any]]) -> float:
    sun = _body_longitude(grahas.get("Surya"))
    moon = _body_longitude(grahas.get("Chandra"))
    if sun is None or moon is None:
        return 0.0
    separation = normalize_degrees(moon - sun)
    if separation > 180.0:
        separation = 360.0 - separation
    benefic_bala = round(separation / 3.0, 2)
    if body == "Chandra":
        return round(benefic_bala * 2.0, 2)
    is_benefic = body in NATURAL_BENEFICS
    if body == "Budha" and _mercury_has_malefic_association(grahas):
        is_benefic = False
    return benefic_bala if is_benefic else round(60.0 - benefic_bala, 2)


def _tribhaga_bala(body: str, chart: dict[str, Any], moment: datetime) -> float:
    if body == "Guru":
        return 60.0
    period = _solar_birth_period(chart, moment)
    if period is None:
        return 0.0
    start, end, is_day = period
    duration = (end - start).total_seconds()
    if duration <= 0:
        return 0.0
    part = min(2, floor(((moment - start).total_seconds() / duration) * 3))
    day_lords = ("Budha", "Surya", "Shani")
    night_lords = ("Chandra", "Shukra", "Mangala")
    lord = day_lords[part] if is_day else night_lords[part]
    return 60.0 if body == lord else 0.0


def _abda_masa_vara_hora_bala(body: str, chart: dict[str, Any], moment: datetime) -> dict[str, object]:
    ahargana = _abbreviated_ahargana(moment)
    varsha_lord = _lord_from_sunday_remainder(((ahargana // 360) * 3 + 1) % 7)
    masa_lord = _lord_from_sunday_remainder(((ahargana // 30) * 2 + 1) % 7)
    dina_lord = _dina_lord(chart, moment)
    hora_lord = _hora_lord(chart, moment)
    components = {
        "abda": 15.0 if body == varsha_lord else 0.0,
        "masa": 30.0 if body == masa_lord else 0.0,
        "vara": 45.0 if body == dina_lord else 0.0,
        "hora": 60.0 if body == hora_lord else 0.0,
    }
    return {
        "value": round(sum(components.values()), 2),
        "components": components,
        "lords": {
            "abda": varsha_lord,
            "masa": masa_lord,
            "vara": dina_lord,
            "hora": hora_lord,
        },
        "ahargana": ahargana,
        "method_note": "BPHS/Santhanam abbreviated Ahargana; Dina and Hora use sunrise-to-sunrise day.",
        "source_reference": "Brihat Parashara Hora Shastra, Santhanam, Ch. 27, Varsha-Masa-Dina-Hora Bala.",
    }


def _ayana_bala(body: str, graha: dict[str, Any] | None) -> float:
    declination = _float_or_none((graha or {}).get("declination"))
    if declination is None:
        longitude = _body_longitude(graha)
        if longitude is None:
            return 0.0
        declination = _declination_from_longitude(longitude)
    if body in {"Chandra", "Shani"}:
        signed_kranti = abs(declination) if declination < 0 else -abs(declination)
    elif body == "Budha":
        signed_kranti = abs(declination)
    else:
        signed_kranti = abs(declination) if declination >= 0 else -abs(declination)
    ayana = ((23.45 + signed_kranti) * 60.0) / 46.9
    if body == "Surya":
        ayana *= 2.0
    maximum = 120.0 if body == "Surya" else 60.0
    return round(max(0.0, min(maximum, ayana)), 2)


def _yuddha_bala(body: str, grahas: dict[str, dict[str, Any]]) -> dict[str, object]:
    if body not in MEAN_DAILY_SPEEDS:
        return {"value": 0.0, "wars": []}
    longitude = _body_longitude(grahas.get(body))
    if longitude is None:
        return {"value": 0.0, "wars": []}
    wars = []
    for other_body, other in grahas.items():
        if other_body == body or other_body not in MEAN_DAILY_SPEEDS:
            continue
        other_longitude = _body_longitude(other)
        if other_longitude is None or _angular_distance(longitude, other_longitude) > 1.0:
            continue
        body_latitude = _float_or_none((grahas.get(body) or {}).get("latitude"))
        other_latitude = _float_or_none(other.get("latitude"))
        winner = ""
        if body_latitude is not None and other_latitude is not None:
            winner = body if abs(body_latitude) <= abs(other_latitude) else other_body
        wars.append({"with": other_body, "winner": winner, "audit_status": "needs_traditional_war_rule_review"})
    return {"value": 0.0, "wars": wars}


def _chesta_bala_full(
    body: str,
    graha: dict[str, Any],
    kala: dict[str, object],
) -> dict[str, object]:
    if body == "Surya":
        value = float(kala.get("ayana") or 0.0)
        return {"traditional_state": value, "state": "surya_ayana_bala", "unit": "virupa"}
    if body == "Chandra":
        value = float(kala.get("paksha") or 0.0)
        return {"traditional_state": value, "state": "chandra_paksha_bala", "unit": "virupa"}
    exact = _chesta_bala_mean_true_seeghrocha(body, graha)
    if exact is not None:
        return exact
    speed = _float_or_none(graha.get("speed_longitude"))
    if graha.get("retrograde") is True or (speed is not None and speed < 0):
        state = "vakra"
    elif speed is None:
        state = "unknown"
    else:
        mean_speed = MEAN_DAILY_SPEEDS.get(body, 1.0)
        ratio = abs(speed) / mean_speed if mean_speed else 0.0
        if ratio < 0.05:
            state = "vikala"
        elif ratio < 0.5:
            state = "mandatara"
        elif ratio < 0.9:
            state = "manda"
        elif ratio < 1.1:
            state = "sama"
        elif ratio < 1.8:
            state = "chara"
        else:
            state = "atichara"
    value = CHESTA_STATE_BALA.get(state, 0.0)
    return {
        "traditional_state": value,
        "state": state,
        "speed_longitude": speed,
        "speed_proxy": _chesta_bala(graha),
        "unit": "virupa",
    }


def _chesta_bala_mean_true_seeghrocha(body: str, graha: dict[str, Any]) -> dict[str, object] | None:
    if body not in MEAN_DAILY_SPEEDS:
        return None
    true_longitude = _body_longitude(graha)
    mean_longitude = _float_or_none(graha.get("mean_longitude"))
    seeghrocha_longitude = _float_or_none(graha.get("seeghrocha_longitude"))
    if true_longitude is None or mean_longitude is None or seeghrocha_longitude is None:
        return None
    average = _average_longitude(mean_longitude, true_longitude)
    cheshta_kendra = _angular_distance(seeghrocha_longitude, average)
    value = round(cheshta_kendra / 3.0, 2)
    return {
        "traditional_state": value,
        "state": "cheshta_kendra",
        "calculation_basis": "mean_true_seeghrocha",
        "mean_longitude": round(normalize_degrees(mean_longitude), 6),
        "true_longitude": round(normalize_degrees(true_longitude), 6),
        "seeghrocha_longitude": round(normalize_degrees(seeghrocha_longitude), 6),
        "mean_true_average": round(average, 6),
        "cheshta_kendra": round(cheshta_kendra, 6),
        "source_reference": (
            "BPHS/Santhanam Ch.27, Motional Strength shlokas 24-25; "
            "Uttara Kalamrita section 4 notes on mean, true and Seeghrocha Chesta Kendra."
        ),
        "unit": "virupa",
    }


def _average_longitude(first: float, second: float) -> float:
    left = normalize_degrees(first)
    right = normalize_degrees(second)
    if abs(left - right) > 180.0:
        if left < right:
            left += 360.0
        else:
            right += 360.0
    return normalize_degrees((left + right) / 2.0)


def _drik_bala(body: str, grahas: dict[str, dict[str, Any]]) -> dict[str, object]:
    target = grahas.get(body)
    target_longitude = _body_longitude(target)
    if target_longitude is None:
        return {"value": 0.0, "aspects": [], "unit": "virupa"}
    value = 0.0
    aspects = []
    for aspector_body, aspector in grahas.items():
        if aspector_body == body or aspector_body not in CLASSICAL_GRAHAS:
            continue
        aspector_longitude = _body_longitude(aspector)
        if aspector_longitude is None:
            continue
        separation = normalize_degrees(target_longitude - aspector_longitude)
        drishti_pinda = _drishti_pinda(aspector_body, separation)
        if drishti_pinda <= 0:
            continue
        contribution = _drik_contribution(aspector_body, drishti_pinda)
        value += contribution
        aspects.append(
            {
                "from": aspector_body,
                "separation": round(separation, 2),
                "fraction": round(drishti_pinda / 60.0, 3),
                "aspect_strength": drishti_pinda,
                "drishti_pinda": drishti_pinda,
                "contribution": round(contribution, 2),
            }
        )
    return {
        "value": round(value, 2),
        "aspects": aspects,
        "calculation_basis": "bphs_ch26_drishti_pinda",
        "unit": "virupa",
    }


def _shadbala_audit_flags(
    sthana: dict[str, object],
    dig: dict[str, object],
    kala: dict[str, object],
    chesta: dict[str, object],
    drik: dict[str, object],
) -> list[dict[str, str]]:
    flags = []
    if dig.get("cusp_source") == "whole_sign_cusp_fallback":
        flags.append(
            {
                "component": "dig",
                "kind": "proxy",
                "note": "Directional strength used whole-sign cusp fallback.",
            }
        )
    abda = kala.get("abda_masa_vara_hora")
    if isinstance(abda, dict) and "approx" in str(abda.get("method_note") or "").lower():
        flags.append(
            {
                "component": "kala_abda_masa_vara_hora",
                "kind": "approximation",
                "note": str(abda["method_note"]),
            }
        )
    yuddha = kala.get("yuddha")
    if isinstance(yuddha, dict) and yuddha.get("wars"):
        flags.append(
            {
                "component": "kala_yuddha",
                "kind": "needs_traditional_review",
                "note": "Graha yuddha candidate requires traditional winner rule review.",
            }
        )
    if chesta.get("state") in {"unknown", "vikala", "mandatara", "manda", "chara", "atichara"}:
        flags.append(
            {
                "component": "chesta",
                "kind": "needs_jhora_component_audit",
                "note": "Chesta bala state uses speed-based classification pending JHora component audit.",
            }
        )
    if drik.get("aspects"):
        flags.append(
            {
                "component": "drik",
                "kind": "needs_jhora_component_audit",
                "note": "Drik bala uses BPHS Ch.26 Drishti Pinda and needs JHora component parity review.",
            }
        )
    if any(
        row.get("dignity") == "missing"
        for row in sthana.get("saptavargaja_details", [])
        if isinstance(row, dict)
    ):
        flags.append(
            {
                "component": "sthana_saptavargaja",
                "kind": "missing_varga",
                "note": "One or more saptavarga placements were missing.",
            }
        )
    return flags


def _shadbala_required_virupas(body: str) -> float:
    return SHADBALA_REQUIRED_VIRUPAS.get(body, SHADBALA_REQUIRED_VIRUPAS["default"])


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


def _varga_rashi(
    body: str,
    graha: dict[str, Any],
    chart: dict[str, Any],
    code: str,
) -> tuple[int, str] | None:
    placement = _varga_placement((chart.get("vargas") or {}).get(code), body)
    if placement is not None:
        rashi = str(placement.get("rashi") or "")
        rashi_index = _int_or_none(placement.get("rashi_index"))
        if rashi_index is None and rashi in RASHIS:
            rashi_index = RASHIS.index(rashi)
        if rashi and rashi_index is not None:
            return rashi_index, rashi
    if code == "D1":
        rashi = str(graha.get("rashi") or "")
        rashi_index = _int_or_none(graha.get("rashi_index"))
        if rashi_index is None and rashi in RASHIS:
            rashi_index = RASHIS.index(rashi)
        if rashi and rashi_index is not None:
            return rashi_index, rashi
    longitude = _body_longitude(graha)
    if longitude is None:
        return None
    return divisional_placement(longitude, code)


def _house_cusp_longitude(
    chart: dict[str, Any],
    lagna_index: int | None,
    house: int,
) -> tuple[float | None, str]:
    for cusp in chart.get("house_cusps") or []:
        if not isinstance(cusp, dict) or _int_or_none(cusp.get("house")) != house:
            continue
        longitude = _float_or_none(cusp.get("longitude"))
        if longitude is not None:
            return normalize_degrees(longitude), "house_cusps"
    ascendant = chart.get("ascendant") or {}
    ascendant_longitude = _body_longitude(ascendant)
    if ascendant_longitude is not None:
        return normalize_degrees(ascendant_longitude + (house - 1) * 30.0), "equal_house_from_ascendant_degree"
    if lagna_index is not None:
        return normalize_degrees((lagna_index + house - 1) * 30.0), "whole_sign_cusp_fallback"
    return None, "missing_lagna"


def _angular_distance(first: float, second: float) -> float:
    distance = abs(normalize_degrees(first) - normalize_degrees(second))
    return min(distance, 360.0 - distance)


def _mercury_has_malefic_association(grahas: dict[str, dict[str, Any]]) -> bool:
    mercury_index = _int_or_none((grahas.get("Budha") or {}).get("rashi_index"))
    if mercury_index is None:
        return False
    for body in NATURAL_MALEFICS:
        if _int_or_none((grahas.get(body) or {}).get("rashi_index")) == mercury_index:
            return True
    return False


def _solar_birth_period(chart: dict[str, Any], moment: datetime) -> tuple[datetime, datetime, bool] | None:
    sunrise, sunset, next_sunrise = _solar_day_bounds(chart, moment)
    if sunrise <= moment < sunset:
        return sunrise, sunset, True
    if moment < sunrise:
        return sunset - timedelta(days=1), sunrise, False
    return sunset, next_sunrise, False


def _solar_day_bounds(chart: dict[str, Any], moment: datetime) -> tuple[datetime, datetime, datetime]:
    solar_day = chart.get("solar_day") or {}
    sunrise = _datetime_from_chart(solar_day.get("sunrise"))
    sunset = _datetime_from_chart(solar_day.get("sunset"))
    next_sunrise = _datetime_from_chart(solar_day.get("next_sunrise"))
    if sunrise is not None and sunset is not None and next_sunrise is not None and sunrise < sunset < next_sunrise:
        return sunrise, sunset, next_sunrise
    day_start = moment.replace(hour=0, minute=0, second=0, microsecond=0)
    sunrise = day_start + timedelta(hours=6)
    sunset = day_start + timedelta(hours=18)
    next_sunrise = sunrise + timedelta(days=1)
    return sunrise, sunset, next_sunrise


def _datetime_from_chart(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _time_from_iso(value: str) -> str:
    try:
        return datetime.fromisoformat(value).strftime("%H:%M")
    except ValueError:
        return ""


def _lord_from_sunday_remainder(remainder: int) -> str:
    return {
        0: "Shani",
        1: "Surya",
        2: "Chandra",
        3: "Mangala",
        4: "Budha",
        5: "Guru",
        6: "Shukra",
    }[remainder % 7]


def _abbreviated_ahargana(moment: datetime) -> int:
    return moment.date().toordinal() - ABBREVIATED_AHARGANA_ORDINAL_OFFSET


def _dina_lord(chart: dict[str, Any], moment: datetime) -> str:
    sunrise, _, _ = _solar_day_bounds(chart, moment)
    day_start = sunrise - timedelta(days=1) if moment < sunrise else sunrise
    return _lord_from_sunday_remainder(_abbreviated_ahargana(day_start) % 7)


def _hora_lord(chart: dict[str, Any], moment: datetime) -> str:
    sunrise, sunset, next_sunrise = _solar_day_bounds(chart, moment)
    if moment < sunrise:
        period_start = sunset - timedelta(days=1)
        period_end = sunrise
    else:
        period_start = sunrise
        period_end = next_sunrise
    duration = (period_end - period_start).total_seconds()
    if duration <= 0:
        return WEEKDAY_LORDS[moment.weekday()]
    hora_index = min(23, floor(((moment - period_start).total_seconds() / duration) * 24))
    start_lord_index = period_start.weekday()
    return WEEKDAY_LORDS[(start_lord_index + 5 * hora_index) % len(WEEKDAY_LORDS)]


def _mean_local_minutes(chart: dict[str, Any], moment: datetime) -> float:
    minutes = moment.hour * 60 + moment.minute + moment.second / 60 + moment.microsecond / 60_000_000
    longitude = _float_or_none((chart.get("place") or {}).get("longitude") if isinstance(chart.get("place"), dict) else None)
    offset = moment.utcoffset()
    if longitude is None or offset is None:
        return minutes % 1440.0
    standard_meridian = offset.total_seconds() / 3600.0 * 15.0
    return (minutes + (longitude - standard_meridian) * 4.0) % 1440.0


def _declination_from_longitude(longitude: float) -> float:
    obliquity = radians(23.439291)
    return degrees(asin(sin(obliquity) * sin(radians(normalize_degrees(longitude)))))


def _drishti_pinda(aspector: str, separation: float) -> float:
    angle = normalize_degrees(separation)
    if angle < 30.0 or angle >= 300.0:
        value = 0.0
    elif angle < 60.0:
        value = (angle - 30.0) / 2.0
    elif angle < 90.0:
        value = angle - 45.0
    elif angle < 120.0:
        value = ((120.0 - angle) / 2.0) + 30.0
    elif angle < 150.0:
        value = 150.0 - angle
    elif angle < 180.0:
        value = (angle - 150.0) * 2.0
    else:
        value = (300.0 - angle) / 2.0

    if aspector == "Mangala" and (90.0 <= angle < 120.0 or 210.0 <= angle < 240.0):
        value += 15.0
    elif aspector == "Guru" and (120.0 <= angle < 150.0 or 240.0 <= angle < 270.0):
        value += 30.0
    elif aspector == "Shani" and (60.0 <= angle < 90.0 or 270.0 <= angle < 300.0):
        value += 45.0
    return round(max(0.0, min(60.0, value)), 2)


def _drik_contribution(aspector: str, aspect_strength: float) -> float:
    if aspector in {"Budha", "Guru"}:
        return aspect_strength
    if aspector in NATURAL_BENEFICS or aspector == "Chandra":
        return aspect_strength / 4.0
    return -aspect_strength / 4.0


def _house_lord(lagna_index: int, house: int) -> str:
    return _rashi_lord((lagna_index + house - 1) % len(RASHIS))


def _house_rashi_index(lagna_index: int, house: int) -> int:
    return (lagna_index + house - 1) % len(RASHIS)


def _rashi_lord(rashi_index: int) -> str:
    return RASHI_LORDS[rashi_index % len(RASHIS)]


def _associated(grahas: dict[str, dict[str, Any]], first: str, second: str) -> bool:
    first_index = _int_or_none((grahas.get(first) or {}).get("rashi_index"))
    second_index = _int_or_none((grahas.get(second) or {}).get("rashi_index"))
    return first_index is not None and first_index == second_index


def _body_in_kendra_from_body(grahas: dict[str, dict[str, Any]], body: str, reference_body: str) -> bool:
    body_index = _int_or_none((grahas.get(body) or {}).get("rashi_index"))
    reference_index = _int_or_none((grahas.get(reference_body) or {}).get("rashi_index"))
    return body_index is not None and reference_index is not None and _house_from(reference_index, body_index) in KENDRA_HOUSES


def _has_yoga_key(rows: list[dict[str, object]], key: str) -> bool:
    return any(row.get("key") == key for row in rows)


def _chara_karakas(grahas: dict[str, dict[str, Any]]) -> dict[str, str]:
    candidates = []
    for body in CLASSICAL_GRAHAS:
        longitude = _float_or_none((grahas.get(body) or {}).get("longitude"))
        if longitude is not None:
            candidates.append((longitude % 30.0, body))
    candidates.sort(reverse=True)
    karaka_names = ("AK", "AmK", "BK", "MK", "PiK", "GK", "DK")
    return {
        karaka_names[index]: body
        for index, (_degree, body) in enumerate(candidates[: len(karaka_names)])
    }


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


def _rounded(value: object) -> float:
    number = _float_or_none(value)
    return round(number, 2) if number is not None else 0.0


def _graha_rashi_index(graha: dict[str, Any] | None) -> int | None:
    if not graha:
        return None
    rashi_index = _int_or_none(graha.get("rashi_index"))
    if rashi_index is not None:
        return rashi_index
    rashi = str(graha.get("rashi") or "")
    return RASHIS.index(rashi) if rashi in RASHIS else None


def _house_from(reference_index: int, target_index: int) -> int:
    return ((target_index - reference_index) % len(RASHIS)) + 1


def _is_odd_sign(sign_index: int) -> bool:
    return sign_index % 2 == 0


def _int_or_none(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None
