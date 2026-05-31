from __future__ import annotations

from typing import Any, Callable

from apps.calculations.chart import build_birth_chart
from apps.calculations.ephemeris import EphemerisProvider
from apps.interpretations.vaishnava_policy import reframe_remedial_advice

CitationSearch = Callable[[str], list[dict[str, object]]]


def compose_birth_report(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
) -> dict[str, Any]:
    chart = build_birth_chart(data, provider=provider)
    citation_search = citation_search or (lambda query: [])
    guidance_citations = _citation_payloads(citation_search("Hare Krishna maha mantra Krishna shelter"))
    remedy = reframe_remedial_advice("Worship Shani on Saturday to pacify Saturn affliction.")

    sections = [
        _calculation_summary(chart),
        _panchanga_summary(chart),
        _dasha_summary(chart),
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
