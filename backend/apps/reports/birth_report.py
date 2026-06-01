from __future__ import annotations

from typing import Any, Callable

from apps.calculations.chart import build_birth_chart
from apps.calculations.ephemeris import EphemerisProvider
from apps.interpretations.facts import build_chart_facts
from apps.interpretations.vaishnava_policy import reframe_remedial_advice

CitationSearch = Callable[[str], list[dict[str, object]]]
InterpretationProvider = Callable[[dict[str, Any]], list[dict[str, Any]]]


def compose_birth_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    interpretation_provider: InterpretationProvider | None = None,
) -> dict[str, Any]:
    chart = build_birth_chart(data, provider=provider)
    chart_facts = build_chart_facts(chart)
    citation_search = citation_search or (lambda query: [])
    interpretation_provider = interpretation_provider or (lambda chart: [])
    guidance_citations = _citation_payloads(citation_search("Hare Krishna maha mantra Krishna shelter"))
    remedy = reframe_remedial_advice("Worship Shani on Saturday to pacify Saturn affliction.")

    sections = [
        _calculation_summary(chart),
        _panchanga_summary(chart),
        _dasha_summary(chart),
        *interpretation_provider(chart),
        {
            "key": "devotional_guidance",
            "title": "Devotional Guidance",
            "body": str(remedy["public_advice"]),
            "review_status": "draft" if guidance_citations else "needs_citation",
            "calculation_only": False,
            "citations": guidance_citations,
            "policy": {
                "blocked_original": remedy["blocked_original"],
                "blocked_terms": remedy["blocked_terms"],
            },
        },
    ]

    return {
        "chart": chart,
        "report": {
            "review_status": _report_status(sections),
            "calculation_version": chart["calculation_version"],
            "source_policy": "citation_first",
            "chart_facts": chart_facts,
            "person_summary": _person_summary(chart, chart_facts),
            "sections": sections,
        },
    }


def _calculation_summary(chart: dict[str, Any]) -> dict[str, Any]:
    ascendant = chart.get("ascendant") or {}
    grahas = chart.get("grahas", [])
    return {
        "key": "calculation_summary",
        "title": "Calculation Summary",
        "body": (
            f"Birth data resolved to {chart['place']['label']} at {chart['birth']['local_datetime']}. "
            f"Lagna is {ascendant.get('rashi', 'pending')}; {len(grahas)} grahas were calculated."
        ),
        "review_status": "calculation_only",
        "calculation_only": True,
        "citations": [],
        "facts": {
            "lagna": ascendant.get("rashi"),
            "graha_count": len(grahas),
        },
    }


def _panchanga_summary(chart: dict[str, Any]) -> dict[str, Any]:
    panchanga = chart.get("panchanga", {})
    tithi = panchanga.get("tithi", {})
    vara = panchanga.get("vara", {})
    yoga = panchanga.get("yoga", {})
    karana = panchanga.get("karana", {})
    return {
        "key": "panchanga",
        "title": "Panchanga",
        "body": (
            f"Tithi: {tithi.get('paksha', 'pending')} {tithi.get('name', 'pending')}; "
            f"vara: {vara.get('name', 'pending')}; yoga: {yoga.get('name', 'pending')}; "
            f"karana: {karana.get('name', 'pending')}."
        ),
        "review_status": "calculation_only",
        "calculation_only": True,
        "citations": [],
    }


def _dasha_summary(chart: dict[str, Any]) -> dict[str, Any]:
    periods = chart.get("dashas", {}).get("vimshottari", {}).get("mahadashas", [])
    first = periods[0] if periods else {}
    return {
        "key": "vimshottari",
        "title": "Vimshottari",
        "body": (
            f"Birth mahadasha starts with {first.get('lord', 'pending')}. "
            "This MVP dasha layer remains draft until JHora parity is verified."
        ),
        "review_status": "calculation_only",
        "calculation_only": True,
        "citations": [],
        "facts": {"first_lord": first.get("lord")},
    }


def _person_summary(chart: dict[str, Any], chart_facts: dict[str, Any]) -> dict[str, Any]:
    return {
        "birth_context": _birth_context(chart),
        "core_factors": _core_factors(chart, chart_facts),
        "graha_houses": _graha_house_rows(chart_facts),
        "panchanga": _panchanga_rows(chart),
        "dasha": _dasha_facts(chart, chart_facts),
    }


def _birth_context(chart: dict[str, Any]) -> list[dict[str, object]]:
    birth = chart.get("birth", {})
    place = chart.get("place", {})
    settings = chart.get("settings", {})
    return [
        {"label": "Birth", "value": birth.get("local_datetime", "")},
        {"label": "Place", "value": place.get("label") or place.get("name", "")},
        {"label": "Ayanamsa", "value": settings.get("ayanamsa", "")},
        {"label": "Ephemeris", "value": settings.get("ephemeris", "")},
    ]


def _core_factors(chart: dict[str, Any], chart_facts: dict[str, Any]) -> list[dict[str, object]]:
    factors = []
    lagna = chart_facts.get("lagna")
    if isinstance(lagna, dict):
        factors.append(
            {
                "label": "Lagna",
                "value": lagna.get("rashi", ""),
                "detail": _placement_detail(lagna),
            }
        )
    grahas = chart_facts.get("grahas", {})
    if isinstance(grahas, dict):
        for label, body in [("Moon", "Chandra"), ("Sun", "Surya")]:
            placement = grahas.get(body)
            if isinstance(placement, dict):
                factors.append(
                    {
                        "label": label,
                        "value": _rashi_house_value(placement),
                        "detail": _placement_detail(placement),
                    }
                )
    return factors


def _graha_house_rows(chart_facts: dict[str, Any]) -> list[dict[str, object]]:
    placements = chart_facts.get("placements", [])
    if not isinstance(placements, list):
        return []
    return [
        {
            "body": placement.get("body"),
            "rashi": placement.get("rashi"),
            "house": placement.get("house"),
            "nakshatra": placement.get("nakshatra"),
            "pada": placement.get("pada"),
            "navamsa": placement.get("navamsa"),
        }
        for placement in placements
        if isinstance(placement, dict)
    ]


def _panchanga_rows(chart: dict[str, Any]) -> list[dict[str, object]]:
    panchanga = chart.get("panchanga", {})
    rows = []
    tithi = panchanga.get("tithi", {})
    if tithi:
        rows.append({"label": "Tithi", "value": f"{tithi.get('paksha', '')} {tithi.get('name', '')}".strip()})
    for key, label in [("vara", "Vara"), ("yoga", "Yoga"), ("karana", "Karana")]:
        item = panchanga.get(key, {})
        if item:
            rows.append({"label": label, "value": item.get("name", "")})
    return rows


def _dasha_facts(chart: dict[str, Any], chart_facts: dict[str, Any]) -> dict[str, object]:
    periods = chart.get("dashas", {}).get("vimshottari", {}).get("mahadashas", [])
    first = periods[0] if periods else {}
    vimshottari = chart_facts.get("vimshottari", {})
    return {
        "birth_mahadasha_lord": vimshottari.get("birth_mahadasha_lord")
        if isinstance(vimshottari, dict)
        else None,
        "starts_at": first.get("starts_at") if isinstance(first, dict) else None,
        "ends_at": first.get("ends_at") if isinstance(first, dict) else None,
    }


def _rashi_house_value(placement: dict[str, object]) -> str:
    rashi = str(placement.get("rashi") or "")
    house = placement.get("house")
    if isinstance(house, int):
        return f"{rashi}, house {house}"
    return rashi


def _placement_detail(placement: dict[str, object]) -> str:
    pieces = []
    nakshatra = placement.get("nakshatra")
    pada = placement.get("pada")
    if nakshatra:
        pieces.append(f"{nakshatra} pada {pada}" if pada else str(nakshatra))
    navamsa = placement.get("navamsa")
    if navamsa:
        pieces.append(f"D9 {navamsa}")
    return "; ".join(pieces)


def _citation_payloads(results: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "title": result.get("title") or result.get("work_title") or "",
            "work_title": result.get("work_title") or "",
            "snippet": result.get("body") or "",
            "public_url": result.get("public_url") or "",
        }
        for result in results[:3]
    ]


def _report_status(sections: list[dict[str, Any]]) -> str:
    if any(section["review_status"] == "needs_citation" for section in sections):
        return "needs_citation"
    return "draft"
