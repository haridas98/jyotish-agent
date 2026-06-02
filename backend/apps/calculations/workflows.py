from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from .chart import build_birth_chart
from .constants import RASHIS
from .ephemeris import EphemerisProvider
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
        "assessment": _compatibility_assessment(total_score, max_score, kuta_rows, vaishnava_note),
        "vaishnava_note": vaishnava_note,
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
            },
            provider=provider,
        )
        candidates.append(_muhurta_candidate(day, candidate_time, chart))
        day += timedelta(days=1)

    candidates.sort(key=lambda item: (-item["score"], item["date"], item["time"]))
    return {
        "status": "calculated_needs_task_review",
        "method": "Daily panchanga scoring with sunrise-based Rahu/Yamaganda/Gulika avoidance; final muhurta requires task-specific review.",
        "candidates": candidates,
        "vaishnava_note": "Даже благоприятное время используем для служения Кришне, а не как замену преданию.",
    }


def _as_of_input(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "birth_date": str(data.get("as_of_date") or data.get("birth_date") or "").strip(),
        "birth_time": str(data.get("as_of_time") or "09:00").strip(),
        "place_name": str(data.get("transit_place_name") or data.get("place_name") or "").strip(),
        "timezone": str(data.get("transit_timezone") or data.get("timezone") or "").strip(),
        "latitude": data.get("transit_latitude", data.get("latitude", "")),
        "longitude": data.get("transit_longitude", data.get("longitude", "")),
    }


def _muhurta_candidate(day: date, candidate_time: time, chart: dict[str, Any]) -> dict[str, Any]:
    panchanga = chart.get("panchanga", {})
    score = 50
    reasons = []
    day_periods = _day_periods(chart)
    blocked_periods = _blocked_periods(chart, day_periods)
    tithi_name = panchanga.get("tithi", {}).get("name")
    yoga_name = panchanga.get("yoga", {}).get("name")
    karana_name = panchanga.get("karana", {}).get("name")

    if tithi_name in {"Ekadashi", "Dvadashi", "Trayodashi", "Dvitiya", "Tritiya", "Panchami", "Dashami"}:
        score += 20
        reasons.append(f"Поддерживающий титхи: {tithi_name}")
    if tithi_name in {"Ekadashi", "Dvadashi"}:
        score += 10
        reasons.append(f"Вайшнавский приоритет: {tithi_name}")
    if tithi_name in {"Chaturthi", "Navami", "Chaturdashi", "Amavasya"}:
        score -= 20
        reasons.append(f"Осторожно с титхи: {tithi_name}")
    if yoga_name in {"Shubha", "Siddha", "Sukarma", "Dhruva", "Brahma", "Indra"}:
        score += 10
        reasons.append(f"Поддерживающая йога: {yoga_name}")
    if yoga_name in {"Vyatipata", "Vaidhriti", "Parigha", "Ganda", "Atiganda", "Vajra"}:
        score -= 10
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
        "panchanga": panchanga,
        "day_periods": day_periods,
        "blocked_periods": blocked_periods,
        "reasons": reasons,
    }


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


def _int_or_none(value: object) -> int | None:
    return value if isinstance(value, int) else None
