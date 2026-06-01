from __future__ import annotations

from datetime import date, time, timedelta
from typing import Any

from .chart import build_birth_chart
from .constants import RASHIS
from .ephemeris import EphemerisProvider


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

    return {
        "status": "partial",
        "method": "Moon-based compatibility baseline; full ashtakuta/ISKCON review pending.",
        "moon": {
            "person_a": _compact_placement(moon_a),
            "person_b": _compact_placement(moon_b),
            "rashi_distance_a_to_b": _house_from(rashi_a, rashi_b),
            "rashi_distance_b_to_a": _house_from(rashi_b, rashi_a),
        },
        "kuta": {
            "tara": _tara_kuta(nak_a, nak_b),
        },
        "vaishnava_note": (
            "Совместимость не должна подменять садху-сангу, ответственность и совместное служение Кришне."
        ),
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
        "status": "partial",
        "method": "Daily panchanga scoring by tithi, vara, yoga, and karana; final muhurta requires task-specific review.",
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

    return {
        "date": day.isoformat(),
        "time": candidate_time.isoformat(timespec="minutes"),
        "score": max(0, min(100, score)),
        "panchanga": panchanga,
        "reasons": reasons,
    }


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
