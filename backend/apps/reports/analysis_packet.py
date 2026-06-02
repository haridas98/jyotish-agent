from __future__ import annotations

import json
from typing import Any

from apps.calculations.ephemeris import EphemerisProvider
from apps.interpretations.shastra_catalog import explanation_schedule

from .birth_report import CitationSearch, InterpretationProvider, compose_birth_report

SCHEMA_VERSION = "jyotish-analysis-packet-v1"


def build_analysis_packet(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    interpretation_provider: InterpretationProvider | None = None,
) -> dict[str, Any]:
    composed = compose_birth_report(
        data,
        provider=provider,
        citation_search=citation_search,
        interpretation_provider=interpretation_provider,
    )
    chart = composed["chart"]
    report = composed["report"]
    citations = _dedupe_citations(report.get("sections", []))

    packet = {
        "schema_version": SCHEMA_VERSION,
        "status": _packet_status(report, citations),
        "generator_policy": _generator_policy(),
        "context": {
            "birth": chart.get("birth", {}),
            "place": chart.get("place", {}),
            "settings": chart.get("settings", {}),
            "chart": chart,
            "explanation_schedule": explanation_schedule(),
            "chart_facts": report.get("chart_facts", {}),
            "person_summary": report.get("person_summary", {}),
            "sections": report.get("sections", []),
        },
        "report": {
            "review_status": report.get("review_status", "draft"),
            "source_policy": report.get("source_policy", "citation_first"),
            "calculation_version": report.get("calculation_version", ""),
        },
        "citations": citations,
    }
    packet["prompt_markdown"] = render_analysis_prompt(packet)
    return packet


def render_analysis_prompt(packet: dict[str, Any]) -> str:
    packet_for_prompt = {key: value for key, value in packet.items() if key != "prompt_markdown"}
    return (
        "Ты готовишь черновик русскоязычного джйотиш-разбора для Gaudiya Vaishnava сервиса.\n\n"
        "Правила:\n"
        "- не выдумывай цитаты, источники, номера стихов или ссылки;\n"
        "- используй только citations из пакета;\n"
        "- расчеты считай техническими фактами, а не фатальными гарантиями;\n"
        "- не советуй independent demigod worship;\n"
        "- если классический remedy требует поклонения грахе или полубогу, переформулируй через "
        "прибежище у Кришны, садхану, служение вайшнавам и наставления Шрилы Прабхупады;\n"
        "- оставляй review_status=draft, пока человек не проверит текст.\n\n"
        "OUTPUT JSON schema:\n"
        "{\n"
        '  "review_status": "draft",\n'
        '  "language": "ru",\n'
        '  "sections": [\n'
        "    {\n"
        '      "title": "string",\n'
        '      "body": "string",\n'
        '      "citation_titles": ["string"],\n'
        '      "review_notes": ["string"]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "ANALYSIS PACKET JSON:\n"
        "```json\n"
        f"{json.dumps(packet_for_prompt, ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def _generator_policy() -> dict[str, Any]:
    return {
        "language": "ru",
        "output_format": "json",
        "source_policy": "citation_first",
        "forbidden_outputs": [
            "independent_demigod_worship",
            "uncited_scriptural_claims",
            "fatalistic_guarantees",
            "medical_legal_financial_directives",
        ],
        "required_behaviors": [
            "cite_only_packet_citations",
            "mark_unverified_claims_for_review",
            "keep_remedies_krishna_centered",
            "preserve_calculation_uncertainty",
        ],
    }


def _packet_status(report: dict[str, Any], citations: list[dict[str, object]]) -> str:
    if report.get("review_status") == "needs_citation" or not citations:
        return "needs_citation_review"
    return "ready_for_generation"


def _dedupe_citations(sections: list[dict[str, Any]]) -> list[dict[str, object]]:
    citations: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for section in sections:
        for citation in section.get("citations", []):
            if not isinstance(citation, dict):
                continue
            title = str(citation.get("title") or "").strip()
            public_url = str(citation.get("public_url") or "").strip()
            key = (title, public_url)
            if not title or key in seen:
                continue
            seen.add(key)
            citations.append(
                {
                    "title": title,
                    "work_title": str(citation.get("work_title") or ""),
                    "snippet": str(citation.get("snippet") or citation.get("body") or ""),
                    "public_url": public_url,
                }
            )
    return citations
