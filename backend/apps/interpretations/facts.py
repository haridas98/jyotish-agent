from __future__ import annotations

from typing import Any

from apps.calculations.constants import RASHIS


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
