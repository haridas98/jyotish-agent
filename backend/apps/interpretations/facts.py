from __future__ import annotations

from typing import Any

from apps.calculations.constants import RASHIS

RASHI_LORDS = {
    "Mesha": "Mangala",
    "Vrishabha": "Shukra",
    "Mithuna": "Budha",
    "Karka": "Chandra",
    "Simha": "Surya",
    "Kanya": "Budha",
    "Tula": "Shukra",
    "Vrischika": "Mangala",
    "Dhanu": "Guru",
    "Makara": "Shani",
    "Kumbha": "Shani",
    "Meena": "Guru",
}

OWN_SIGNS = {
    "Surya": ("Simha",),
    "Chandra": ("Karka",),
    "Mangala": ("Mesha", "Vrischika"),
    "Budha": ("Mithuna", "Kanya"),
    "Guru": ("Dhanu", "Meena"),
    "Shukra": ("Vrishabha", "Tula"),
    "Shani": ("Makara", "Kumbha"),
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

CHARA_KARAKAS = ["AK", "AmK", "BK", "MK", "PiK", "GK", "DK"]
CHARA_KARAKA_BODIES = {"Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani"}


def build_chart_facts(chart: dict[str, Any]) -> dict[str, Any]:
    ascendant = chart.get("ascendant")
    lagna_index = _rashi_index(ascendant)
    placements = [_graha_fact(graha, lagna_index) for graha in chart.get("grahas", [])]
    grahas = {
        placement["body"]: placement
        for placement in placements
        if isinstance(placement.get("body"), str) and placement["body"]
    }
    return {
        "lagna": _lagna_fact(ascendant) if isinstance(ascendant, dict) else None,
        "grahas": grahas,
        "placements": placements,
        "detailed_positions": _detailed_positions(chart.get("grahas", []), lagna_index),
        "vimshottari": _vimshottari_facts(chart),
    }


def _lagna_fact(ascendant: dict[str, Any]) -> dict[str, Any]:
    return {
        "rashi": ascendant.get("rashi"),
        "rashi_index": _rashi_index(ascendant),
        "nakshatra": ascendant.get("nakshatra"),
        "pada": ascendant.get("pada"),
        "navamsa": ascendant.get("navamsa"),
    }


def _graha_fact(graha: dict[str, Any], lagna_index: int | None) -> dict[str, Any]:
    rashi_idx = _rashi_index(graha)
    return {
        "body": graha.get("body"),
        "rashi": graha.get("rashi"),
        "rashi_index": rashi_idx,
        "house": _whole_sign_house(lagna_index, rashi_idx),
        "nakshatra": graha.get("nakshatra"),
        "pada": graha.get("pada"),
        "navamsa": graha.get("navamsa"),
    }


def _whole_sign_house(lagna_index: int | None, rashi_idx: int | None) -> int | None:
    if lagna_index is None or rashi_idx is None:
        return None
    return ((rashi_idx - lagna_index) % 12) + 1


def _rashi_index(item: Any) -> int | None:
    if not isinstance(item, dict):
        return None
    raw_index = item.get("rashi_index")
    if isinstance(raw_index, int) and 0 <= raw_index <= 11:
        return raw_index
    rashi = item.get("rashi")
    if isinstance(rashi, str) and rashi in RASHIS:
        return RASHIS.index(rashi)
    return None


def _vimshottari_facts(chart: dict[str, Any]) -> dict[str, Any]:
    periods = chart.get("dashas", {}).get("vimshottari", {}).get("mahadashas", [])
    first = periods[0] if periods else {}
    return {
        "birth_mahadasha_lord": first.get("lord") if isinstance(first, dict) else None,
    }


def _detailed_positions(grahas: list[dict[str, Any]], lagna_index: int | None) -> list[dict[str, Any]]:
    chara_karakas = _chara_karakas(grahas)
    rows = []
    for graha in grahas:
        body = graha.get("body")
        rashi = str(graha.get("rashi") or "")
        rashi_idx = _rashi_index(graha)
        longitude = _float_or_none(graha.get("longitude"))
        rows.append(
            {
                "body": body,
                "chara_karaka": chara_karakas.get(body),
                "longitude": longitude,
                "sign_degrees_dms": _sign_degrees_dms(longitude),
                "rashi": rashi,
                "rashi_lord": RASHI_LORDS.get(rashi),
                "navamsa": graha.get("navamsa"),
                "nakshatra": graha.get("nakshatra"),
                "pada": graha.get("pada"),
                "house": _whole_sign_house(lagna_index, rashi_idx),
                "ruled_houses": _ruled_houses(str(body or ""), lagna_index),
                "dignity": _dignity(str(body or ""), rashi),
                "retrograde": _is_retrograde(graha),
            }
        )
    return rows


def _chara_karakas(grahas: list[dict[str, Any]]) -> dict[str, str]:
    candidates = []
    for graha in grahas:
        body = graha.get("body")
        longitude = _float_or_none(graha.get("longitude"))
        if body not in CHARA_KARAKA_BODIES or longitude is None:
            continue
        candidates.append((longitude % 30.0, body))
    candidates.sort(reverse=True)
    return {
        body: CHARA_KARAKAS[index]
        for index, (_degree, body) in enumerate(candidates[: len(CHARA_KARAKAS)])
    }


def _sign_degrees_dms(longitude: float | None) -> str:
    if longitude is None:
        return ""
    total_seconds = round((longitude % 30.0) * 3600)
    degrees, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{degrees}°{minutes:02d}'{seconds:02d}''"


def _ruled_houses(body: str, lagna_index: int | None) -> list[int]:
    if lagna_index is None:
        return []
    houses = []
    for rashi in OWN_SIGNS.get(body, set()):
        rashi_idx = RASHIS.index(rashi)
        house = _whole_sign_house(lagna_index, rashi_idx)
        if house:
            houses.append(house)
    return houses


def _dignity(body: str, rashi: str) -> str:
    if EXALTATION_SIGNS.get(body) == rashi:
        return "Экзальтация"
    if DEBILITATION_SIGNS.get(body) == rashi:
        return "Дебилитация"
    if rashi in OWN_SIGNS.get(body, ()):
        return "Свой знак"
    return "Обычное"


def _is_retrograde(graha: dict[str, Any]) -> bool:
    body = graha.get("body")
    if body in {"Rahu", "Ketu"}:
        return True
    speed = _float_or_none(graha.get("speed_longitude"))
    return bool(speed is not None and speed < 0)


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
