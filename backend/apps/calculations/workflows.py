from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from .chart import build_birth_chart
from .constants import RASHIS
from .ephemeris import EphemerisProvider
from .primitives import normalize_degrees
from .solar import moment_hits_periods

VARNA_ORDER = {
    "Shudra": 1,
    "Vaishya": 2,
    "Kshatriya": 3,
    "Brahmana": 4,
}

VARNA_BY_ELEMENT = {
    0: "Kshatriya",
    1: "Vaishya",
    2: "Shudra",
    3: "Brahmana",
    4: "Kshatriya",
    5: "Vaishya",
    6: "Shudra",
    7: "Brahmana",
    8: "Kshatriya",
    9: "Vaishya",
    10: "Shudra",
    11: "Brahmana",
}

VASHYA_GROUPS = {
    0: "chatushpada",
    1: "chatushpada",
    2: "nara",
    3: "jala",
    4: "vana",
    5: "nara",
    6: "nara",
    7: "keeta",
    8: "chatushpada",
    9: "chatushpada",
    10: "nara",
    11: "jala",
}

NAKSHATRA_GANA = (
    "deva",
    "manushya",
    "rakshasa",
    "manushya",
    "deva",
    "manushya",
    "deva",
    "deva",
    "rakshasa",
    "rakshasa",
    "manushya",
    "manushya",
    "deva",
    "rakshasa",
    "deva",
    "rakshasa",
    "deva",
    "rakshasa",
    "rakshasa",
    "manushya",
    "manushya",
    "deva",
    "rakshasa",
    "rakshasa",
    "manushya",
    "manushya",
    "deva",
)

NAKSHATRA_YONI = (
    "horse",
    "elephant",
    "sheep",
    "serpent",
    "serpent",
    "dog",
    "cat",
    "sheep",
    "cat",
    "rat",
    "rat",
    "cow",
    "buffalo",
    "tiger",
    "buffalo",
    "tiger",
    "deer",
    "deer",
    "dog",
    "monkey",
    "mongoose",
    "monkey",
    "lion",
    "horse",
    "lion",
    "cow",
    "elephant",
)

NAKSHATRA_NADI = tuple("adi" if index % 3 == 0 else "madhya" if index % 3 == 1 else "antya" for index in range(27))

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

GRAHA_FRIENDS = {
    "Surya": {"Chandra", "Mangala", "Guru"},
    "Chandra": {"Surya", "Budha"},
    "Mangala": {"Surya", "Chandra", "Guru"},
    "Budha": {"Surya", "Shukra"},
    "Guru": {"Surya", "Chandra", "Mangala"},
    "Shukra": {"Budha", "Shani"},
    "Shani": {"Budha", "Shukra"},
}

GRAHA_ENEMIES = {
    "Surya": {"Shukra", "Shani"},
    "Chandra": set(),
    "Mangala": {"Budha"},
    "Budha": {"Chandra"},
    "Guru": {"Budha", "Shukra"},
    "Shukra": {"Surya", "Chandra"},
    "Shani": {"Surya", "Chandra", "Mangala"},
}

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

DEBILITATION_SIGNS = {
    "Surya": "Tula",
    "Chandra": "Vrischika",
    "Mangala": "Karka",
    "Budha": "Meena",
    "Guru": "Makara",
    "Shukra": "Kanya",
    "Shani": "Mesha",
}

KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DIFFICULT_RELATION_HOUSES = {6, 8, 12}

KUTA_LABELS = {
    "varna": "Varna",
    "vashya": "Vashya",
    "tara": "Tara",
    "yoni": "Yoni",
    "graha_maitri": "Graha Maitri",
    "gana": "Gana",
    "bhakoot": "Bhakoot",
    "nadi": "Nadi",
}

KUTA_ORDER = (
    "varna",
    "vashya",
    "tara",
    "yoni",
    "graha_maitri",
    "gana",
    "bhakoot",
    "nadi",
)

CALCULATION_SETTING_FIELDS = (
    "zodiac",
    "calculation_model",
    "siddhanta_model",
    "ayanamsa",
    "node_type",
    "ephemeris",
    "house_system",
    "bhava_system",
    "varga_scheme",
    "sunrise_source",
    "timezone_source",
    "shadbala_profile",
)

MUHURTA_PURPOSE_RULES = {
    "general": {
        "label": "General",
        "supporting_tithis": {"Dvitiya", "Tritiya", "Panchami", "Dashami", "Ekadashi", "Dvadashi", "Trayodashi"},
        "caution_tithis": {"Chaturthi", "Navami", "Chaturdashi", "Amavasya"},
        "supporting_nakshatras": set(),
        "caution_nakshatras": set(),
        "supporting_yogas": {"Shubha", "Siddha", "Sukarma", "Dhruva", "Brahma", "Indra"},
        "caution_yogas": {"Vyatipata", "Vaidhriti", "Parigha", "Ganda", "Atiganda", "Vajra"},
    },
    "marriage": {
        "label": "Marriage",
        "supporting_tithis": {"Dvitiya", "Tritiya", "Panchami", "Saptami", "Dashami", "Trayodashi"},
        "caution_tithis": {"Chaturthi", "Navami", "Chaturdashi", "Amavasya"},
        "supporting_nakshatras": {
            "Rohini",
            "Mrigashira",
            "Magha",
            "Uttara Phalguni",
            "Hasta",
            "Swati",
            "Anuradha",
            "Mula",
            "Uttara Ashadha",
            "Uttara Bhadrapada",
            "Revati",
        },
        "caution_nakshatras": {"Ardra", "Ashlesha", "Jyeshtha"},
        "supporting_yogas": {"Shubha", "Siddha", "Sukarma", "Dhruva", "Brahma", "Indra"},
        "caution_yogas": {"Vyatipata", "Vaidhriti", "Parigha", "Ganda", "Atiganda", "Vajra"},
    },
    "travel": {
        "label": "Travel",
        "supporting_tithis": {"Dvitiya", "Tritiya", "Panchami", "Saptami", "Dashami", "Ekadashi", "Trayodashi"},
        "caution_tithis": {"Chaturthi", "Navami", "Chaturdashi", "Amavasya"},
        "supporting_nakshatras": {
            "Ashwini",
            "Punarvasu",
            "Pushya",
            "Hasta",
            "Anuradha",
            "Shravana",
            "Dhanishta",
            "Revati",
        },
        "caution_nakshatras": {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula"},
        "supporting_yogas": {"Siddha", "Sukarma", "Dhruva", "Brahma", "Indra"},
        "caution_yogas": {"Vyatipata", "Vaidhriti", "Parigha", "Ganda", "Atiganda", "Vajra"},
    },
    "study": {
        "label": "Study",
        "supporting_tithis": {"Dvitiya", "Tritiya", "Panchami", "Dashami", "Ekadashi"},
        "caution_tithis": {"Chaturthi", "Navami", "Chaturdashi", "Amavasya"},
        "supporting_nakshatras": {
            "Rohini",
            "Mrigashira",
            "Punarvasu",
            "Pushya",
            "Hasta",
            "Swati",
            "Anuradha",
            "Shravana",
            "Revati",
        },
        "caution_nakshatras": {"Ardra", "Ashlesha", "Jyeshtha", "Mula"},
        "supporting_yogas": {"Shubha", "Siddha", "Sukarma", "Brahma", "Indra"},
        "caution_yogas": {"Vyatipata", "Vaidhriti", "Parigha", "Ganda", "Atiganda", "Vajra"},
    },
}


def build_transit_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    natal = build_birth_chart(data, provider=provider)
    transit_input = _as_of_input(data)
    transit_chart = build_birth_chart(transit_input, provider=provider)
    natal_lagna_index = _rashi_index(natal.get("ascendant"))
    natal_moon = _graha(natal, "Chandra")
    natal_moon_index = _rashi_index(natal_moon)

    return {
        "status": "calculated",
        "method": "Transit grahas calculated for as-of datetime and compared to natal Lagna/Moon by whole-sign houses.",
        "interpretation_plan": _workflow_interpretation_plan(
            "transits",
            source_anchors=["gochara", "brhat-jataka", "jataka-parijata", "teacher-review"],
            required_factors=[
                "house_from_lagna",
                "house_from_moon",
                "transit_graha_strength",
                "natal_promise",
                "running_dasha",
            ],
            client_text_sequence=[
                "current_transit_facts",
                "moon_and_lagna_context",
                "natal_promise_filter",
                "dasha_timing",
                "gaudiya_guard",
            ],
        ),
        "as_of": {
            "date": transit_input["birth_date"],
            "time": transit_input["birth_time"],
            "timezone": transit_chart["birth"]["timezone"],
            "local_datetime": transit_chart["birth"]["local_datetime"],
        },
        "natal": {
            "lagna": _compact_placement(natal.get("ascendant")),
            "moon": _compact_placement(natal_moon),
        },
        "transits": [
            {
                "body": graha.get("body"),
                "longitude": graha.get("longitude"),
                "rashi": graha.get("rashi"),
                "nakshatra": graha.get("nakshatra"),
                "pada": graha.get("pada"),
                "house_from_lagna": _house_from(natal_lagna_index, _rashi_index(graha)),
                "house_from_moon": _house_from(natal_moon_index, _rashi_index(graha)),
            }
            for graha in transit_chart.get("grahas", [])
        ],
    }


def build_compatibility_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    person_a = build_birth_chart(_required_mapping(data, "person_a"), provider=provider)
    person_b = build_birth_chart(_required_mapping(data, "person_b"), provider=provider)
    relationship_context = _compatibility_relationship_context(data)
    moon_a = _graha(person_a, "Chandra")
    moon_b = _graha(person_b, "Chandra")
    nak_a = _int_or_none(moon_a.get("nakshatra_index") if moon_a else None)
    nak_b = _int_or_none(moon_b.get("nakshatra_index") if moon_b else None)
    rashi_a = _rashi_index(moon_a)
    rashi_b = _rashi_index(moon_b)
    kuta = {
        "varna": _varna_kuta(rashi_a, rashi_b),
        "vashya": _vashya_kuta(rashi_a, rashi_b),
        "tara": _tara_kuta(nak_a, nak_b),
        "yoni": _yoni_kuta(nak_a, nak_b),
        "graha_maitri": _graha_maitri_kuta(rashi_a, rashi_b),
        "gana": _gana_kuta(nak_a, nak_b),
        "bhakoot": _bhakoot_kuta(rashi_a, rashi_b),
        "nadi": _nadi_kuta(nak_a, nak_b),
    }
    total_score = round(sum(float(item["score"]) for item in kuta.values()), 2)
    max_score = round(sum(float(item["max_score"]) for item in kuta.values()), 2)
    kuta_rows = _kuta_rows(kuta)
    vaishnava_note = "Совместимость не должна подменять садху-сангу, ответственность и совместное служение Кришне."
    analysis = _compatibility_chart_analysis(person_a, person_b, total_score, max_score, kuta_rows)

    return {
        "status": "calculated_needs_tradition_review",
        "method": (
            "Ashtakuta from Moon rashi/nakshatra plus multi-factor chart analysis: "
            "Lagna, Moon, seventh house, Shukra/Mangala, Guru/Shukra and dasha context."
        ),
        "coverage": {
            "system": "ashtakuta_plus_chart_analysis",
            "calculated_kutas": len(kuta_rows),
            "total_kutas": len(KUTA_ORDER),
            "calculated_perspectives": len(analysis["perspectives"]),
            "status": "multi_factor_needs_shastra_citation_review",
        },
        "score": {
            "total": total_score,
            "max": max_score,
            "percent": round(total_score / max_score * 100, 2) if max_score else 0,
        },
        "moon": {
            "person_a": _compact_placement(moon_a),
            "person_b": _compact_placement(moon_b),
            "rashi_distance_a_to_b": _house_from(rashi_a, rashi_b),
            "rashi_distance_b_to_a": _house_from(rashi_b, rashi_a),
        },
        "kuta": kuta,
        "kuta_rows": kuta_rows,
        "analysis": analysis,
        "relationship_context": relationship_context,
        "interpretation_plan": _workflow_interpretation_plan(
            "compatibility",
            source_anchors=[
                "muhurta-chintamani",
                "jataka-parijata",
                "brhat-jataka",
                "teacher-review",
            ],
            required_factors=[
                "ashtakuta",
                "lagna_lagna",
                "moon_mind",
                "seventh_house",
                "shukra_mangala",
                "guru_shukra",
                "dasha_context",
                *relationship_context["required_factors"],
            ],
            client_text_sequence=[
                "two_chart_facts",
                "ashtakuta_score",
                "relationship_house_analysis",
                "support_and_caution_factors",
                "practical_guidance",
                "gaudiya_guard",
            ],
        ),
        "assessment": _compatibility_assessment(total_score, max_score, kuta_rows, vaishnava_note),
        "vaishnava_note": vaishnava_note,
    }


def _compatibility_relationship_context(data: dict[str, Any]) -> dict[str, Any]:
    raw = data.get("relationship_context")
    if not isinstance(raw, dict):
        raw = {}
    role = str(raw.get("role") or "partner").strip() or "partner"
    label = str(raw.get("label") or role).strip() or role
    focus_houses = [
        int(item)
        for item in raw.get("focus_houses", [])
        if isinstance(item, int) or (isinstance(item, str) and item.isdigit())
    ]
    focus_vargas = [
        str(item).strip()
        for item in raw.get("focus_vargas", [])
        if str(item).strip()
    ]
    required_factors = [f"relationship_role:{role}"]
    required_factors.extend(f"house_{house}" for house in focus_houses)
    required_factors.extend(f"varga_{code.lower()}" for code in focus_vargas)
    return {
        "role": role,
        "label": label,
        "focus_houses": focus_houses,
        "focus_vargas": focus_vargas,
        "prompt_hint": str(raw.get("prompt_hint") or "").strip(),
        "relationship_id": raw.get("relationship_id"),
        "link_status": raw.get("link_status"),
        "profile_id": raw.get("profile_id"),
        "related_profile_id": raw.get("related_profile_id"),
        "profile_label": raw.get("profile_label"),
        "related_profile_label": raw.get("related_profile_label"),
        "consent_policy": str(raw.get("consent_policy") or "").strip(),
        "required_factors": required_factors,
    }


def build_muhurta_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    start_date = _required_date(data, "start_date")
    end_date = _required_date(data, "end_date")
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")
    candidate_time = _optional_time(data, "time", default=time(9, 0))
    purpose = _muhurta_purpose(data)

    candidates = []
    day = start_date
    while day <= end_date:
        chart = build_birth_chart(
            {
                "birth_date": day.isoformat(),
                "birth_time": candidate_time.isoformat(timespec="minutes"),
                "place_name": data.get("place_name", ""),
                "timezone": data.get("timezone", ""),
                "latitude": data.get("latitude", ""),
                "longitude": data.get("longitude", ""),
                **_calculation_settings_input(data),
            },
            provider=provider,
        )
        candidates.append(_muhurta_candidate(day, candidate_time, chart, purpose=purpose))
        day += timedelta(days=1)

    candidates.sort(key=lambda item: (-item["score"], item["date"], item["time"]))
    return {
        "status": "calculated_needs_task_review",
        "method": (
            "Daily panchanga scoring with purpose profile and sunrise-based Rahu/Yamaganda/Gulika avoidance; "
            "final muhurta requires task-specific review."
        ),
        "purpose": purpose,
        "purpose_profile": MUHURTA_PURPOSE_RULES[purpose]["label"],
        "interpretation_plan": _workflow_interpretation_plan(
            "muhurta",
            source_anchors=["muhurta-chintamani", "kalaprakashika", "teacher-review"],
            required_factors=[
                "panchanga",
                "purpose_profile",
                "rahu_yamaganda_gulika_avoidance",
                "lagna_strength",
                "task_context",
            ],
            client_text_sequence=[
                "candidate_window",
                "panchanga_support",
                "blocked_periods",
                "purpose_fit",
                "gaudiya_guard",
            ],
        ),
        "candidates": candidates,
        "vaishnava_note": "Даже благоприятное время используем для служения Кришне, а не как замену преданию.",
    }


def build_tithi_pravesha_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    target_year = _required_int(data, "target_year", minimum=1, maximum=9999)
    search_days = _required_int(data, "search_days", default=45, minimum=1, maximum=120)
    natal = build_birth_chart(data, provider=provider)
    target_angle = _solar_lunar_angle(natal)
    if target_angle is None:
        raise ValueError("natal Surya and Chandra are required")

    center = _target_year_birth_date(natal["birth"]["date"], target_year)
    return_base = _return_place_input(data)
    found = _find_tithi_pravesha_moment(
        target_angle,
        center,
        search_days,
        return_base,
        data,
        provider=provider,
    )
    return_chart = build_birth_chart(
        {
            **return_base,
            "birth_date": found["moment"].date().isoformat(),
            "birth_time": found["moment"].time().replace(microsecond=0).isoformat(timespec="seconds"),
            **_calculation_settings_input(data),
        },
        provider=provider,
    )
    return_angle = _solar_lunar_angle(return_chart) or 0.0

    return {
        "status": "calculated_needs_jhora_audit",
        "method": "Annual same solar-lunar angle return near the birth date; interpretation remains Tajaka/source gated.",
        "target_year": target_year,
        "interpretation_plan": _workflow_interpretation_plan(
            "tithi_pravesha",
            source_anchors=["tajaka", "tithi-pravesha-tradition", "teacher-review"],
            required_factors=[
                "natal_tithi_angle",
                "annual_chart",
                "annual_lagna",
                "annual_moon",
                "annual_panchanga",
            ],
            client_text_sequence=[
                "return_moment",
                "annual_chart_facts",
                "tajaka_context",
                "timing_cautions",
                "gaudiya_guard",
            ],
        ),
        "search": {
            "center_date": center.isoformat(),
            "search_days": search_days,
            "step_hours": found["step_hours"],
            "tolerance_degrees": 0.01,
        },
        "natal": {
            "birth": natal["birth"],
            "tithi": natal.get("panchanga", {}).get("tithi"),
            "solar_lunar_angle": round(target_angle, 6),
            "sun": _compact_placement(_graha(natal, "Surya")),
            "moon": _compact_placement(_graha(natal, "Chandra")),
        },
        "return": {
            "date": return_chart["birth"]["date"],
            "time": return_chart["birth"]["time"],
            "timezone": return_chart["birth"]["timezone"],
            "local_datetime": return_chart["birth"]["local_datetime"],
            "solar_lunar_angle": round(return_angle, 6),
            "delta_degrees": round(_angle_distance(return_angle, target_angle), 6),
            "iterations": found["iterations"],
            "chart": return_chart,
        },
        "annual_context": {
            "lagna": _compact_placement(return_chart.get("ascendant")),
            "sun": _compact_placement(_graha(return_chart, "Surya")),
            "moon": _compact_placement(_graha(return_chart, "Chandra")),
            "panchanga": return_chart.get("panchanga", {}),
            "tajaka": _tajaka_baseline(natal, return_chart, target_year),
        },
        "audit": {
            "review_status": "research_only",
            "source_anchors": ["jhora", "tajaka-tradition-review", "teacher-review"],
            "public_interpretation_status": "blocked_until_jhora_and_shastra_review",
        },
    }


def build_tajaka_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    annual = build_tithi_pravesha_report(data, provider=provider)
    annual_chart = annual["return"]["chart"]
    return {
        "status": "baseline_calculated_needs_full_tajaka_audit",
        "method": "Tajaka shell from Tithi Pravesha annual chart with Muntha and annual chart anchors.",
        "tithi_pravesha": annual,
        "interpretation_plan": _workflow_interpretation_plan(
            "tajaka",
            source_anchors=["tajaka-neelakanthi", "tithi-pravesha-tradition", "teacher-review"],
            required_factors=[
                "annual_chart",
                "muntha",
                "muntha_lord",
                "annual_lagna",
                "sahams",
                "annual_dashas",
            ],
            client_text_sequence=[
                "annual_chart_anchor",
                "muntha_focus",
                "annual_house_themes",
                "timing_sequence",
                "gaudiya_guard",
            ],
        ),
        "tajaka": {
            "status": "baseline_only",
            "muntha": annual["annual_context"]["tajaka"].get("muntha"),
            "annual_lagna": annual["annual_context"]["lagna"],
            "annual_moon": annual["annual_context"]["moon"],
            "annual_sun": annual["annual_context"]["sun"],
            "panchanga": annual["annual_context"]["panchanga"],
            "open_items": ["tajaka_yogas", "muntha_lord_strength", "sahams", "annual_dashas"],
        },
        "audit": {
            "review_status": "research_only",
            "public_interpretation_status": "blocked_until_tajaka_text_and_jhora_review",
            "chart_id": annual_chart.get("birth", {}).get("local_datetime"),
        },
    }


def build_prashna_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    chart = build_birth_chart(_event_chart_input(data, date_field="question_date", time_field="question_time"), provider=provider)
    lagna_index = _rashi_index(chart.get("ascendant"))
    moon = _graha(chart, "Chandra")
    moon_index = _rashi_index(moon)
    lagna_lord = RASHI_LORDS.get(lagna_index) if lagna_index is not None else None
    return {
        "status": "baseline_calculated_needs_prashna_tradition_review",
        "method": "Horary chart at question time with Lagna/Moon/panchanga anchors; final Prashna rules are citation-gated.",
        "interpretation_plan": _workflow_interpretation_plan(
            "prashna",
            source_anchors=["prashna-marga", "daivajna-vallabha", "teacher-review"],
            required_factors=[
                "question_lagna",
                "lagna_lord",
                "moon",
                "seventh_house",
                "panchanga",
            ],
            client_text_sequence=[
                "question_context",
                "horary_lagna",
                "moon_and_significators",
                "answer_limits",
                "gaudiya_guard",
            ],
        ),
        "question": {
            "text": str(data.get("question") or "").strip(),
            "asked_at": chart["birth"],
            "place": chart["place"],
        },
        "chart": chart,
        "indicators": {
            "lagna": _compact_placement(chart.get("ascendant")),
            "lagna_lord": lagna_lord,
            "lagna_lord_placement": _compact_placement(_graha(chart, lagna_lord)) if lagna_lord else _compact_placement(None),
            "moon": _compact_placement(moon),
            "moon_house_from_lagna": _house_from(lagna_index, moon_index),
            "seventh_house_rashi": RASHIS[(lagna_index + 6) % len(RASHIS)] if lagna_index is not None else None,
            "panchanga": chart.get("panchanga", {}),
        },
        "audit": {
            "review_status": "research_only",
            "source_anchors": ["prashna-marga", "jhora", "teacher-review"],
            "public_interpretation_status": "blocked_until_prashna_text_review",
        },
    }


def build_mundane_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    chart = build_birth_chart(_event_chart_input(data, date_field="event_date", time_field="event_time"), provider=provider)
    lagna_index = _rashi_index(chart.get("ascendant"))
    slow_planets = []
    for body in ("Guru", "Shani", "Rahu", "Ketu"):
        graha = _graha(chart, body)
        slow_planets.append(
            {
                "body": body,
                "placement": _compact_placement(graha),
                "house_from_lagna": _house_from(lagna_index, _rashi_index(graha)),
            }
        )
    return {
        "status": "baseline_event_chart_needs_mundane_rules_review",
        "method": "Mundane/event chart shell for event time and place; national/event prediction rules are not final.",
        "interpretation_plan": _workflow_interpretation_plan(
            "mundane",
            source_anchors=["brhat-samhita", "mundane-tradition", "teacher-review"],
            required_factors=[
                "event_lagna",
                "sun",
                "moon",
                "slow_planets",
                "fourth_house",
                "tenth_house",
            ],
            client_text_sequence=[
                "event_context",
                "chart_angles",
                "slow_planet_pressure",
                "public_scope_limits",
                "gaudiya_guard",
            ],
        ),
        "event": {
            "type": str(data.get("event_type") or "general").strip().lower(),
            "description": str(data.get("description") or "").strip(),
            "occurred_at": chart["birth"],
            "place": chart["place"],
        },
        "chart": chart,
        "indicators": {
            "lagna": _compact_placement(chart.get("ascendant")),
            "sun": _compact_placement(_graha(chart, "Surya")),
            "moon": _compact_placement(_graha(chart, "Chandra")),
            "tenth_house_rashi": RASHIS[(lagna_index + 9) % len(RASHIS)] if lagna_index is not None else None,
            "fourth_house_rashi": RASHIS[(lagna_index + 3) % len(RASHIS)] if lagna_index is not None else None,
            "slow_planets": slow_planets,
            "panchanga": chart.get("panchanga", {}),
        },
        "audit": {
            "review_status": "research_only",
            "source_anchors": ["brhat-samhita", "jhora", "teacher-review"],
            "public_interpretation_status": "blocked_until_mundane_text_review",
        },
    }


def _as_of_input(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "birth_date": str(data.get("as_of_date") or data.get("birth_date") or "").strip(),
        "birth_time": str(data.get("as_of_time") or "09:00").strip(),
        "place_name": str(data.get("transit_place_name") or data.get("place_name") or "").strip(),
        "timezone": str(data.get("transit_timezone") or data.get("timezone") or "").strip(),
        "latitude": data.get("transit_latitude", data.get("latitude", "")),
        "longitude": data.get("transit_longitude", data.get("longitude", "")),
        **_calculation_settings_input(data),
    }


def _event_chart_input(data: dict[str, Any], *, date_field: str, time_field: str) -> dict[str, Any]:
    event_date = str(data.get(date_field) or data.get("birth_date") or "").strip()
    event_time = str(data.get(time_field) or data.get("birth_time") or "").strip()
    return {
        "birth_date": event_date,
        "birth_time": event_time,
        "place_name": str(data.get("place_name") or "").strip(),
        "timezone": str(data.get("timezone") or "").strip(),
        "latitude": data.get("latitude", ""),
        "longitude": data.get("longitude", ""),
        **_calculation_settings_input(data),
    }


def _calculation_settings_input(data: dict[str, Any]) -> dict[str, Any]:
    return {
        field: data[field]
        for field in CALCULATION_SETTING_FIELDS
        if data.get(field) not in {None, ""}
    }


def _workflow_interpretation_plan(
    kind: str,
    *,
    source_anchors: list[str],
    required_factors: list[str],
    client_text_sequence: list[str],
) -> dict[str, Any]:
    return {
        "kind": kind,
        "source_anchors": source_anchors,
        "required_factors": required_factors,
        "client_text_sequence": client_text_sequence,
        "gaudiya_guard": (
            "Use calculations as context for responsible Krishna-centered service; "
            "do not prescribe independent graha or demigod worship."
        ),
        "citation_rule": "condition_or_factor -> shastra_reference -> qualified_interpretation",
    }


def _return_place_input(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "place_name": str(data.get("return_place_name") or data.get("place_name") or "").strip(),
        "timezone": str(data.get("return_timezone") or data.get("timezone") or "").strip(),
        "latitude": data.get("return_latitude", data.get("latitude", "")),
        "longitude": data.get("return_longitude", data.get("longitude", "")),
    }


def _target_year_birth_date(raw_birth_date: str, target_year: int) -> date:
    birth_date = date.fromisoformat(raw_birth_date)
    try:
        return birth_date.replace(year=target_year)
    except ValueError:
        return date(target_year, 2, 28)


def _solar_lunar_angle(chart: dict[str, Any]) -> float | None:
    sun = _graha(chart, "Surya")
    moon = _graha(chart, "Chandra")
    if not isinstance(sun, dict) or not isinstance(moon, dict):
        return None
    sun_longitude = _float_or_none(sun.get("longitude"))
    moon_longitude = _float_or_none(moon.get("longitude"))
    if sun_longitude is None or moon_longitude is None:
        return None
    return normalize_degrees(moon_longitude - sun_longitude)


def _signed_angle_delta(angle: float, target: float) -> float:
    return (normalize_degrees(angle) - normalize_degrees(target) + 180.0) % 360.0 - 180.0


def _angle_distance(angle: float, target: float) -> float:
    return abs(_signed_angle_delta(angle, target))


def _tajaka_baseline(natal: dict[str, Any], return_chart: dict[str, Any], target_year: int) -> dict[str, Any]:
    natal_lagna = natal.get("ascendant") or {}
    return_lagna = return_chart.get("ascendant") or {}
    natal_lagna_index = _int_or_none(natal_lagna.get("rashi_index"))
    return_lagna_index = _int_or_none(return_lagna.get("rashi_index"))
    if natal_lagna_index is None or return_lagna_index is None:
        return {
            "status": "missing_lagna",
            "method": "Muntha requires natal and annual lagna.",
        }
    birth_date = date.fromisoformat(str(natal["birth"]["date"]))
    completed_years = max(0, target_year - birth_date.year)
    muntha_index = (natal_lagna_index + completed_years) % len(RASHIS)
    return {
        "status": "baseline_calculated_needs_tajaka_review",
        "method": "Muntha progresses one sign per completed year from natal lagna.",
        "completed_years": completed_years,
        "muntha": {
            "rashi_index": muntha_index,
            "rashi": RASHIS[muntha_index],
            "house_from_annual_lagna": ((muntha_index - return_lagna_index) % len(RASHIS)) + 1,
        },
    }


def _find_tithi_pravesha_moment(
    target_angle: float,
    center: date,
    search_days: int,
    return_base: dict[str, Any],
    data: dict[str, Any],
    *,
    provider: EphemerisProvider | None,
) -> dict[str, Any]:
    start = datetime.combine(center - timedelta(days=search_days), time(0, 0))
    end = datetime.combine(center + timedelta(days=search_days), time(23, 59))
    step = timedelta(hours=6)
    previous_moment: datetime | None = None
    previous_delta: float | None = None
    best: tuple[float, datetime] | None = None
    crossings: list[tuple[datetime, datetime]] = []
    moment = start
    while moment <= end:
        delta = _tithi_angle_delta(moment, target_angle, return_base, data, provider=provider)
        distance = abs(delta)
        if best is None or distance < best[0]:
            best = (distance, moment)
        if previous_moment is not None and previous_delta is not None and (delta == 0 or delta * previous_delta < 0):
            crossings.append((previous_moment, moment))
        previous_moment = moment
        previous_delta = delta
        moment += step
    if not crossings:
        if best is None:
            raise ValueError("No Tithi Pravesha candidate found")
        return {"moment": best[1], "iterations": 0, "step_hours": 6}

    center_dt = datetime.combine(center, time(12, 0))
    left, right = min(crossings, key=lambda pair: abs((pair[0] + (pair[1] - pair[0]) / 2 - center_dt).total_seconds()))
    iterations = 0
    left_delta = _tithi_angle_delta(left, target_angle, return_base, data, provider=provider)
    for _ in range(24):
        iterations += 1
        mid = left + (right - left) / 2
        mid_delta = _tithi_angle_delta(mid, target_angle, return_base, data, provider=provider)
        if abs(mid_delta) <= 0.01:
            return {"moment": mid.replace(microsecond=0), "iterations": iterations, "step_hours": 6}
        if left_delta * mid_delta <= 0:
            right = mid
        else:
            left = mid
            left_delta = mid_delta
    return {"moment": (left + (right - left) / 2).replace(microsecond=0), "iterations": iterations, "step_hours": 6}


def _tithi_angle_delta(
    moment: datetime,
    target_angle: float,
    return_base: dict[str, Any],
    data: dict[str, Any],
    *,
    provider: EphemerisProvider | None,
) -> float:
    chart = build_birth_chart(
        {
            **return_base,
            "birth_date": moment.date().isoformat(),
            "birth_time": moment.time().replace(microsecond=0).isoformat(timespec="seconds"),
            **_calculation_settings_input(data),
        },
        provider=provider,
    )
    angle = _solar_lunar_angle(chart)
    if angle is None:
        raise ValueError("candidate Surya and Chandra are required")
    return _signed_angle_delta(angle, target_angle)


def _muhurta_candidate(day: date, candidate_time: time, chart: dict[str, Any], *, purpose: str) -> dict[str, Any]:
    panchanga = chart.get("panchanga", {})
    score = 50
    reasons = []
    purpose_adjustments = []
    purpose_rules = MUHURTA_PURPOSE_RULES[purpose]
    day_periods = _day_periods(chart)
    blocked_periods = _blocked_periods(chart, day_periods)
    tithi_name = panchanga.get("tithi", {}).get("name")
    nakshatra_name = panchanga.get("nakshatra", {}).get("name")
    yoga_name = panchanga.get("yoga", {}).get("name")
    karana_name = panchanga.get("karana", {}).get("name")

    if tithi_name in purpose_rules["supporting_tithis"]:
        score += 20
        purpose_adjustments.append({"field": "tithi", "name": tithi_name, "delta": 20, "status": "supporting"})
        reasons.append(f"Поддерживающий титхи: {tithi_name}")
    if tithi_name in {"Ekadashi", "Dvadashi"}:
        score += 10
        purpose_adjustments.append({"field": "tithi", "name": tithi_name, "delta": 10, "status": "vaishnava_priority"})
        reasons.append(f"Вайшнавский приоритет: {tithi_name}")
    if tithi_name in purpose_rules["caution_tithis"]:
        score -= 20
        purpose_adjustments.append({"field": "tithi", "name": tithi_name, "delta": -20, "status": "caution"})
        reasons.append(f"Осторожно с титхи: {tithi_name}")
    if nakshatra_name in purpose_rules["supporting_nakshatras"]:
        score += 12
        reasons.append(f"Supporting nakshatra for {purpose}: {nakshatra_name}")
        purpose_adjustments.append({"field": "nakshatra", "name": nakshatra_name, "delta": 12, "status": "supporting"})
    if nakshatra_name in purpose_rules["caution_nakshatras"]:
        score -= 12
        reasons.append(f"Caution nakshatra for {purpose}: {nakshatra_name}")
        purpose_adjustments.append({"field": "nakshatra", "name": nakshatra_name, "delta": -12, "status": "caution"})
    if yoga_name in purpose_rules["supporting_yogas"]:
        score += 10
        purpose_adjustments.append({"field": "yoga", "name": yoga_name, "delta": 10, "status": "supporting"})
        reasons.append(f"Поддерживающая йога: {yoga_name}")
    if yoga_name in purpose_rules["caution_yogas"]:
        score -= 10
        purpose_adjustments.append({"field": "yoga", "name": yoga_name, "delta": -10, "status": "caution"})
        reasons.append(f"Осторожно с йогой: {yoga_name}")
    if karana_name == "Vishti":
        score -= 15
        reasons.append("Vishti karana")
    for period in blocked_periods:
        if period.get("key") == "rahu_kalam":
            score -= 15
            reasons.append(f"Избегать Rahu Kalam: {_period_time_range(period)}")
        elif period.get("key") == "yamaganda":
            score -= 10
            reasons.append(f"Избегать Yamaganda: {_period_time_range(period)}")
        elif period.get("key") == "gulika_kala":
            score -= 5
            reasons.append(f"Осторожно Gulika Kala: {_period_time_range(period)}")

    return {
        "date": day.isoformat(),
        "time": candidate_time.isoformat(timespec="minutes"),
        "score": max(0, min(100, score)),
        "purpose": purpose,
        "purpose_profile": purpose_rules["label"],
        "purpose_adjustments": purpose_adjustments,
        "panchanga": panchanga,
        "day_periods": day_periods,
        "blocked_periods": blocked_periods,
        "reasons": reasons,
    }


def _muhurta_purpose(data: dict[str, Any]) -> str:
    raw = str(data.get("purpose") or data.get("task_type") or "general").strip().lower().replace("-", "_")
    aliases = {
        "marriage": "marriage",
        "vivaha": "marriage",
        "wedding": "marriage",
        "travel": "travel",
        "journey": "travel",
        "study": "study",
        "education": "study",
        "learning": "study",
        "general": "general",
    }
    return aliases.get(raw, "general")


def _kuta_rows(kuta: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for key in KUTA_ORDER:
        item = kuta[key]
        rows.append(
            {
                "key": key,
                "name": KUTA_LABELS[key],
                "score": item["score"],
                "max_score": item["max_score"],
                "status": item["status"],
                "details": _kuta_details(item),
            }
        )
    return rows


def _compatibility_assessment(
    total_score: float,
    max_score: float,
    kuta_rows: list[dict[str, object]],
    note: str,
) -> dict[str, object]:
    percent = total_score / max_score * 100 if max_score else 0
    caution_count = sum(1 for row in kuta_rows if float(row["score"]) == 0 and float(row["max_score"]) > 0)
    if percent >= 65 and caution_count <= 1:
        level = "supportive"
    elif percent >= 50:
        level = "mixed"
    else:
        level = "caution"
    return {
        "level": level,
        "caution_count": caution_count,
        "note": note,
    }


def _compatibility_chart_analysis(
    person_a: dict[str, Any],
    person_b: dict[str, Any],
    ashtakuta_score: float,
    ashtakuta_max: float,
    kuta_rows: list[dict[str, object]],
) -> dict[str, object]:
    summaries = {
        "person_a": _compatibility_chart_summary(person_a),
        "person_b": _compatibility_chart_summary(person_b),
    }
    perspectives = [
        _ashtakuta_perspective(ashtakuta_score, ashtakuta_max, kuta_rows),
        _lagna_lagna_perspective(summaries),
        _moon_mind_perspective(person_a, person_b),
        _seventh_house_perspective(summaries),
        _shukra_mangala_perspective(person_a, person_b),
        _guru_shukra_perspective(person_a, person_b),
        _dasha_context_perspective(person_a, person_b),
    ]
    return {
        "status": "calculated_needs_shastra_citation_review",
        "review_status": "research_only",
        "source_policy": "ashtakuta_is_one_layer_not_final_verdict",
        "source_anchors": [
            "muhurta-chintamani",
            "jataka-parijata",
            "brhat-jataka",
            "teacher-review",
        ],
        "chart_summaries": summaries,
        "perspectives": perspectives,
        "support_factors": [
            item for row in perspectives if row["status"] == "supportive" for item in row["findings"]
        ],
        "caution_factors": [
            item for row in perspectives if row["status"] == "caution" for item in row["findings"]
        ],
        "vaishnava_guard": "final_guidance_requires_sadhu_guru_shastra_review",
    }


def _compatibility_chart_summary(chart: dict[str, Any]) -> dict[str, object]:
    lagna = chart.get("ascendant")
    lagna_index = _rashi_index(lagna)
    moon = _graha(chart, "Chandra")
    seventh_index = (lagna_index + 6) % 12 if lagna_index is not None else None
    seventh_lord = RASHI_LORDS[seventh_index] if seventh_index is not None else None
    seventh_lord_graha = _graha(chart, seventh_lord) if seventh_lord else None
    seventh_lord_index = _rashi_index(seventh_lord_graha)
    relationship_bodies = {
        body: _relationship_graha_summary(chart, body)
        for body in ("Chandra", "Shukra", "Mangala", "Guru", "Shani")
    }
    return {
        "lagna": _compact_placement(lagna if isinstance(lagna, dict) else None),
        "moon": _compact_placement(moon),
        "seventh_house": {
            "rashi": RASHIS[seventh_index] if seventh_index is not None else None,
            "rashi_index": seventh_index,
            "lord": seventh_lord,
            "planets": _planets_in_house(chart, lagna_index, 7),
        },
        "seventh_lord": {
            "body": seventh_lord,
            "rashi": seventh_lord_graha.get("rashi") if isinstance(seventh_lord_graha, dict) else None,
            "house": _house_from(lagna_index, seventh_lord_index),
            "dignity": _graha_dignity(seventh_lord, seventh_lord_graha),
        },
        "relationship_grahas": relationship_bodies,
        "birth_dasha_lord": _birth_dasha_lord(chart),
    }


def _relationship_graha_summary(chart: dict[str, Any], body: str) -> dict[str, object]:
    graha = _graha(chart, body)
    lagna_index = _rashi_index(chart.get("ascendant"))
    rashi_index = _rashi_index(graha)
    return {
        "body": body,
        "rashi": graha.get("rashi") if isinstance(graha, dict) else None,
        "rashi_index": rashi_index,
        "house": _house_from(lagna_index, rashi_index),
        "nakshatra": graha.get("nakshatra") if isinstance(graha, dict) else None,
        "dignity": _graha_dignity(body, graha),
    }


def _ashtakuta_perspective(
    score: float,
    max_score: float,
    kuta_rows: list[dict[str, object]],
) -> dict[str, object]:
    percent = score / max_score * 100 if max_score else 0.0
    status = "supportive" if percent >= 65 else "mixed" if percent >= 50 else "caution"
    zero_rows = [row["name"] for row in kuta_rows if float(row["score"]) == 0 and float(row["max_score"]) > 0]
    return _perspective(
        "ashtakuta",
        "Ashtakuta baseline",
        round(score, 2),
        max_score,
        status,
        [
            f"Ashtakuta score {round(score, 2)}/{max_score} ({round(percent, 2)}%).",
            f"Zero-score kutas: {', '.join(str(row) for row in zero_rows) if zero_rows else 'none'}.",
        ],
        "Classical kuta matching from Moon rashi and nakshatra; not a standalone marriage verdict.",
    )


def _lagna_lagna_perspective(summaries: dict[str, dict[str, object]]) -> dict[str, object]:
    lagna_a = (summaries["person_a"]["lagna"] or {}).get("rashi_index")
    lagna_b = (summaries["person_b"]["lagna"] or {}).get("rashi_index")
    distance_a = _house_from(_int_or_none(lagna_a), _int_or_none(lagna_b))
    distance_b = _house_from(_int_or_none(lagna_b), _int_or_none(lagna_a))
    score, status = _relation_score(distance_a, distance_b, max_score=12.0)
    return _perspective(
        "lagna_lagna",
        "Lagna and life direction",
        score,
        12.0,
        status,
        [f"Lagna distance A→B {distance_a}; B→A {distance_b}."],
        "Lagna comparison checks shared life direction and practical household rhythm.",
    )


def _moon_mind_perspective(person_a: dict[str, Any], person_b: dict[str, Any]) -> dict[str, object]:
    moon_a = _graha(person_a, "Chandra")
    moon_b = _graha(person_b, "Chandra")
    distance_a = _house_from(_rashi_index(moon_a), _rashi_index(moon_b))
    distance_b = _house_from(_rashi_index(moon_b), _rashi_index(moon_a))
    score, status = _relation_score(distance_a, distance_b, max_score=12.0)
    return _perspective(
        "moon_mind",
        "Moon and emotional rhythm",
        score,
        12.0,
        status,
        [
            f"Moon distance A→B {distance_a}; B→A {distance_b}.",
            f"Moon nakshatras: {moon_a.get('nakshatra') if moon_a else None} / {moon_b.get('nakshatra') if moon_b else None}.",
        ],
        "Moon comparison reviews manas, daily emotional response and domestic comfort.",
    )


def _seventh_house_perspective(summaries: dict[str, dict[str, object]]) -> dict[str, object]:
    findings = []
    score = 0.0
    for key in ("person_a", "person_b"):
        seventh = summaries[key]["seventh_house"]
        seventh_lord = summaries[key]["seventh_lord"]
        house = _int_or_none(seventh_lord.get("house") if isinstance(seventh_lord, dict) else None)
        lord = seventh_lord.get("body") if isinstance(seventh_lord, dict) else None
        findings.append(f"{key} seventh house {seventh.get('rashi')} lord {lord}.")
        findings.append(f"{key} seventh lord {lord} in house {house}.")
        score += _seventh_lord_score(house)
        planets = seventh.get("planets") if isinstance(seventh, dict) else []
        if planets:
            findings.append(f"{key} planets in seventh: {', '.join(str(item) for item in planets)}.")
    status = "supportive" if score >= 9 else "mixed" if score >= 6 else "caution"
    return _perspective(
        "seventh_house",
        "Seventh house and marriage capacity",
        round(score, 2),
        12.0,
        status,
        findings,
        "The seventh house, its lord and occupants are checked in both natal charts.",
    )


def _shukra_mangala_perspective(person_a: dict[str, Any], person_b: dict[str, Any]) -> dict[str, object]:
    shukra_a = _graha(person_a, "Shukra")
    mangala_a = _graha(person_a, "Mangala")
    shukra_b = _graha(person_b, "Shukra")
    mangala_b = _graha(person_b, "Mangala")
    distance_a = _house_from(_rashi_index(shukra_a), _rashi_index(mangala_b))
    distance_b = _house_from(_rashi_index(shukra_b), _rashi_index(mangala_a))
    score, status = _relation_score(distance_a, distance_b, max_score=10.0)
    return _perspective(
        "shukra_mangala",
        "Shukra and Mangala chemistry",
        score,
        10.0,
        status,
        [
            f"A Shukra to B Mangala distance {distance_a}.",
            f"B Shukra to A Mangala distance {distance_b}.",
        ],
        "Shukra/Mangala comparison is a secondary attraction and friction indicator.",
    )


def _guru_shukra_perspective(person_a: dict[str, Any], person_b: dict[str, Any]) -> dict[str, object]:
    findings = []
    score = 0.0
    for key, chart in (("person_a", person_a), ("person_b", person_b)):
        for body in ("Guru", "Shukra"):
            graha = _graha(chart, body)
            dignity = _graha_dignity(body, graha)
            findings.append(f"{key} {body} dignity {dignity}.")
            score += _dignity_score(dignity)
    status = "supportive" if score >= 7 else "mixed" if score >= 4 else "caution"
    return _perspective(
        "guru_shukra",
        "Guru, Shukra and dharmic household values",
        round(score, 2),
        10.0,
        status,
        findings,
        "Guru and Shukra are reviewed for dharma, counsel, affection and household values.",
    )


def _dasha_context_perspective(person_a: dict[str, Any], person_b: dict[str, Any]) -> dict[str, object]:
    lord_a = _birth_dasha_lord(person_a)
    lord_b = _birth_dasha_lord(person_b)
    status = "context" if lord_a and lord_b else "missing"
    return _perspective(
        "dasha_context",
        "Dasha context",
        0.0,
        0.0,
        status,
        [f"Birth mahadasha lords: {lord_a} / {lord_b}."],
        "Dasha timing must be interpreted separately and should not override chart compatibility.",
    )


def _perspective(
    key: str,
    title: str,
    score: float,
    max_score: float,
    status: str,
    findings: list[str],
    source_basis: str,
) -> dict[str, object]:
    return {
        "key": key,
        "title": title,
        "score": score,
        "max_score": max_score,
        "status": status,
        "findings": findings,
        "source_basis": source_basis,
        "review_status": "research_only",
    }


def _kuta_details(item: dict[str, object]) -> str:
    person_a = item.get("person_a")
    person_b = item.get("person_b")
    if person_a is not None and person_b is not None:
        return f"{person_a} / {person_b}"
    a_to_b = item.get("a_to_b_count") or item.get("distance_a_to_b")
    b_to_a = item.get("b_to_a_count") or item.get("distance_b_to_a")
    if a_to_b is not None and b_to_a is not None:
        return f"{a_to_b} / {b_to_a}"
    return str(item.get("status") or "")


def _relation_score(
    distance_a: int | None,
    distance_b: int | None,
    *,
    max_score: float,
) -> tuple[float, str]:
    if distance_a is None or distance_b is None:
        return 0.0, "missing"
    pair = {distance_a, distance_b}
    if pair & DIFFICULT_RELATION_HOUSES:
        return round(max_score * 0.25, 2), "caution"
    if pair <= (KENDRA_HOUSES | TRIKONA_HOUSES | {11}):
        return max_score, "supportive"
    return round(max_score * 0.55, 2), "mixed"


def _seventh_lord_score(house: int | None) -> float:
    if house is None:
        return 0.0
    if house in KENDRA_HOUSES or house in TRIKONA_HOUSES:
        return 6.0
    if house in DIFFICULT_RELATION_HOUSES:
        return 2.0
    return 4.0


def _planets_in_house(
    chart: dict[str, Any],
    lagna_index: int | None,
    house: int,
) -> list[str]:
    if lagna_index is None:
        return []
    return [
        str(graha.get("body"))
        for graha in chart.get("grahas", [])
        if isinstance(graha, dict) and _house_from(lagna_index, _rashi_index(graha)) == house
    ]


def _graha_dignity(body: str | None, graha: dict[str, Any] | None) -> str:
    if not body or not isinstance(graha, dict):
        return "missing"
    rashi = str(graha.get("rashi") or "")
    if rashi == EXALTATION_SIGNS.get(body):
        return "exaltation"
    if rashi in OWN_SIGNS.get(body, set()):
        return "own"
    if rashi == DEBILITATION_SIGNS.get(body):
        return "debilitation"
    try:
        lord = RASHI_LORDS[RASHIS.index(rashi)]
    except ValueError:
        return "unknown"
    if lord in GRAHA_FRIENDS.get(body, set()):
        return "friend"
    if lord in GRAHA_ENEMIES.get(body, set()):
        return "enemy"
    return "neutral"


def _dignity_score(dignity: str) -> float:
    return {
        "exaltation": 2.5,
        "own": 2.2,
        "friend": 1.8,
        "neutral": 1.2,
        "enemy": 0.6,
        "debilitation": 0.0,
    }.get(dignity, 0.0)


def _birth_dasha_lord(chart: dict[str, Any]) -> str | None:
    periods = ((chart.get("dashas") or {}).get("vimshottari") or {}).get("mahadashas")
    if isinstance(periods, list) and periods and isinstance(periods[0], dict):
        lord = periods[0].get("lord")
        return str(lord) if lord else None
    return None


def _day_periods(chart: dict[str, Any]) -> list[dict[str, Any]]:
    solar = chart.get("solar_day")
    if not isinstance(solar, dict):
        return []
    periods = solar.get("day_periods")
    return [period for period in periods if isinstance(period, dict)] if isinstance(periods, list) else []


def _blocked_periods(chart: dict[str, Any], day_periods: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_moment = (chart.get("birth") or {}).get("local_datetime")
    if not isinstance(raw_moment, str):
        return []
    try:
        moment = datetime.fromisoformat(raw_moment)
    except ValueError:
        return []
    return moment_hits_periods(moment, day_periods)


def _period_time_range(period: dict[str, Any]) -> str:
    starts_at = _time_label(period.get("starts_at"))
    ends_at = _time_label(period.get("ends_at"))
    return f"{starts_at}-{ends_at}"


def _time_label(value: object) -> str:
    if not isinstance(value, str):
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%H:%M")
    except ValueError:
        return ""


def _tara_kuta(nak_a: int | None, nak_b: int | None) -> dict[str, object]:
    if nak_a is None or nak_b is None:
        return {"score": 0.0, "max_score": 3.0, "status": "missing_moon_nakshatra"}
    a_to_b = ((nak_b - nak_a) % 27) + 1
    b_to_a = ((nak_a - nak_b) % 27) + 1
    favorable = [_tara_favorable(a_to_b), _tara_favorable(b_to_a)]
    return {
        "score": 1.5 * sum(1 for item in favorable if item),
        "max_score": 3.0,
        "a_to_b_count": a_to_b,
        "b_to_a_count": b_to_a,
        "status": "calculated",
    }


def _varna_kuta(rashi_a: int | None, rashi_b: int | None) -> dict[str, object]:
    if rashi_a is None or rashi_b is None:
        return _missing_kuta(1.0)
    varna_a = VARNA_BY_ELEMENT[rashi_a]
    varna_b = VARNA_BY_ELEMENT[rashi_b]
    return {
        "score": 1.0 if VARNA_ORDER[varna_a] >= VARNA_ORDER[varna_b] else 0.0,
        "max_score": 1.0,
        "person_a": varna_a,
        "person_b": varna_b,
        "status": "calculated",
    }


def _vashya_kuta(rashi_a: int | None, rashi_b: int | None) -> dict[str, object]:
    if rashi_a is None or rashi_b is None:
        return _missing_kuta(2.0)
    group_a = VASHYA_GROUPS[rashi_a]
    group_b = VASHYA_GROUPS[rashi_b]
    score = 2.0 if group_a == group_b else 1.0 if {group_a, group_b} & {"nara", "chatushpada"} else 0.5
    return {
        "score": score,
        "max_score": 2.0,
        "person_a": group_a,
        "person_b": group_b,
        "status": "calculated",
    }


def _yoni_kuta(nak_a: int | None, nak_b: int | None) -> dict[str, object]:
    if nak_a is None or nak_b is None:
        return _missing_kuta(4.0)
    yoni_a = NAKSHATRA_YONI[nak_a]
    yoni_b = NAKSHATRA_YONI[nak_b]
    score = 4.0 if yoni_a == yoni_b else 2.0
    return {
        "score": score,
        "max_score": 4.0,
        "person_a": yoni_a,
        "person_b": yoni_b,
        "status": "calculated",
    }


def _graha_maitri_kuta(rashi_a: int | None, rashi_b: int | None) -> dict[str, object]:
    if rashi_a is None or rashi_b is None:
        return _missing_kuta(5.0)
    lord_a = RASHI_LORDS[rashi_a]
    lord_b = RASHI_LORDS[rashi_b]
    if lord_a == lord_b:
        score = 5.0
    elif lord_b in GRAHA_FRIENDS[lord_a] and lord_a in GRAHA_FRIENDS[lord_b]:
        score = 5.0
    elif lord_b in GRAHA_ENEMIES[lord_a] or lord_a in GRAHA_ENEMIES[lord_b]:
        score = 0.0
    else:
        score = 3.0
    return {
        "score": score,
        "max_score": 5.0,
        "person_a": lord_a,
        "person_b": lord_b,
        "status": "calculated",
    }


def _gana_kuta(nak_a: int | None, nak_b: int | None) -> dict[str, object]:
    if nak_a is None or nak_b is None:
        return _missing_kuta(6.0)
    gana_a = NAKSHATRA_GANA[nak_a]
    gana_b = NAKSHATRA_GANA[nak_b]
    if gana_a == gana_b:
        score = 6.0
    elif {gana_a, gana_b} == {"deva", "manushya"}:
        score = 5.0
    elif {gana_a, gana_b} == {"manushya", "rakshasa"}:
        score = 1.0
    else:
        score = 0.0
    return {
        "score": score,
        "max_score": 6.0,
        "person_a": gana_a,
        "person_b": gana_b,
        "status": "calculated",
    }


def _bhakoot_kuta(rashi_a: int | None, rashi_b: int | None) -> dict[str, object]:
    if rashi_a is None or rashi_b is None:
        return _missing_kuta(7.0)
    distance_a = _house_from(rashi_a, rashi_b)
    distance_b = _house_from(rashi_b, rashi_a)
    adverse = {frozenset({2, 12}), frozenset({5, 9}), frozenset({6, 8})}
    score = 0.0 if frozenset({distance_a, distance_b}) in adverse else 7.0
    return {
        "score": score,
        "max_score": 7.0,
        "distance_a_to_b": distance_a,
        "distance_b_to_a": distance_b,
        "status": "calculated",
    }


def _nadi_kuta(nak_a: int | None, nak_b: int | None) -> dict[str, object]:
    if nak_a is None or nak_b is None:
        return _missing_kuta(8.0)
    nadi_a = NAKSHATRA_NADI[nak_a]
    nadi_b = NAKSHATRA_NADI[nak_b]
    return {
        "score": 0.0 if nadi_a == nadi_b else 8.0,
        "max_score": 8.0,
        "person_a": nadi_a,
        "person_b": nadi_b,
        "status": "calculated",
    }


def _missing_kuta(max_score: float) -> dict[str, object]:
    return {"score": 0.0, "max_score": max_score, "status": "missing_moon_data"}


def _tara_favorable(count: int) -> bool:
    return count % 9 not in {3, 5, 7}


def _compact_placement(item: dict[str, Any] | None) -> dict[str, object | None]:
    if not isinstance(item, dict):
        return {"rashi": None, "nakshatra": None, "pada": None}
    return {
        "rashi": item.get("rashi"),
        "rashi_index": item.get("rashi_index"),
        "nakshatra": item.get("nakshatra"),
        "nakshatra_index": item.get("nakshatra_index"),
        "pada": item.get("pada"),
    }


def _graha(chart: dict[str, Any], body: str) -> dict[str, Any] | None:
    return next(
        (graha for graha in chart.get("grahas", []) if isinstance(graha, dict) and graha.get("body") == body),
        None,
    )


def _rashi_index(item: dict[str, Any] | None) -> int | None:
    if not isinstance(item, dict):
        return None
    raw = item.get("rashi_index")
    if isinstance(raw, int):
        return raw
    rashi = item.get("rashi")
    if isinstance(rashi, str) and rashi in RASHIS:
        return RASHIS.index(rashi)
    return None


def _house_from(reference_index: int | None, target_index: int | None) -> int | None:
    if reference_index is None or target_index is None:
        return None
    return ((target_index - reference_index) % 12) + 1


def _required_mapping(data: dict[str, Any], field: str) -> dict[str, Any]:
    value = data.get(field)
    if not isinstance(value, dict):
        raise ValueError(f"{field} is required")
    return value


def _required_date(data: dict[str, Any], field: str) -> date:
    value = str(data.get(field) or "").strip()
    if not value:
        raise ValueError(f"{field} is required")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be YYYY-MM-DD") from exc


def _optional_time(data: dict[str, Any], field: str, default: time) -> time:
    value = str(data.get(field) or "").strip()
    if not value:
        return default
    try:
        return time.fromisoformat(value).replace(second=0, microsecond=0)
    except ValueError as exc:
        raise ValueError(f"{field} must be HH:MM") from exc


def _required_int(
    data: dict[str, Any],
    field: str,
    *,
    default: int | None = None,
    minimum: int,
    maximum: int,
) -> int:
    raw = data.get(field, default)
    if raw in {None, ""}:
        raise ValueError(f"{field} is required")
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if value < minimum or value > maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return value


def _int_or_none(value: object) -> int | None:
    return value if isinstance(value, int) else None


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
