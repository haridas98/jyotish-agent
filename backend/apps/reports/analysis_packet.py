from __future__ import annotations

import json
from typing import Any

from apps.calculations.chart import build_birth_chart
from apps.calculations.ephemeris import EphemerisProvider
from apps.calculations.workflows import build_compatibility_report
from apps.interpretations.citation_requests import build_citation_requests
from apps.interpretations.shastra_catalog import explanation_schedule
from apps.interpretations.yoga_catalog import yoga_catalog_overview
from apps.interpretations.yoga_source_map import detected_yoga_source_map

from .birth_report import CitationSearch, InterpretationProvider, compose_birth_report

SCHEMA_VERSION = "jyotish-analysis-packet-v1"
COMPATIBILITY_SCHEMA_VERSION = "jyotish-compatibility-analysis-packet-v1"
ResearchSearch = CitationSearch


def build_analysis_packet(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: ResearchSearch | None = None,
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
    schedule = explanation_schedule()
    yoga_source_map = detected_yoga_source_map(chart)
    citation_requests = build_citation_requests(
        explanation_schedule=schedule,
        detected_yoga_source_map=yoga_source_map,
    )
    research_context = _research_context(citation_requests, research_search)

    packet = {
        "schema_version": SCHEMA_VERSION,
        "status": _packet_status(report, citations),
        "generator_policy": _generator_policy(),
        "citation_requests": citation_requests,
        "context": {
            "birth": chart.get("birth", {}),
            "place": chart.get("place", {}),
            "settings": chart.get("settings", {}),
            "chart": chart,
            "explanation_schedule": schedule,
            "yoga_catalog_overview": yoga_catalog_overview(),
            "detected_yoga_source_map": yoga_source_map,
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
        "research_context": research_context,
    }
    packet["prompt_markdown"] = render_analysis_prompt(packet)
    return packet


def build_compatibility_analysis_packet(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: ResearchSearch | None = None,
) -> dict[str, Any]:
    citation_search = citation_search or (lambda query: [])
    person_a_input = _required_mapping(data, "person_a")
    person_b_input = _required_mapping(data, "person_b")
    person_a_chart = build_birth_chart(person_a_input, provider=provider)
    person_b_chart = build_birth_chart(person_b_input, provider=provider)
    compatibility = build_compatibility_report(data, provider=provider)
    citation_requests = _compatibility_citation_requests(compatibility)
    citations = _citation_payloads_from_results(
        citation_search(_compatibility_seed_query(compatibility))
    )
    research_context = _research_context(citation_requests, research_search)

    packet = {
        "schema_version": COMPATIBILITY_SCHEMA_VERSION,
        "status": "needs_citation_review",
        "generator_policy": _compatibility_generator_policy(),
        "citation_requests": citation_requests,
        "context": {
            "person_a": {
                "input": person_a_input,
                "chart": person_a_chart,
            },
            "person_b": {
                "input": person_b_input,
                "chart": person_b_chart,
            },
            "compatibility": compatibility,
            "source_review_status": "exact_shastra_citations_required_before_public_marriage_guidance",
        },
        "report": {
            "review_status": "needs_citation_review",
            "source_policy": "citation_first",
            "calculation_version": person_a_chart.get("calculation_version", ""),
        },
        "citations": citations,
        "research_context": research_context,
    }
    packet["prompt_markdown"] = render_compatibility_analysis_prompt(packet)
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
        f"{_translation_review_rules()}"
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


def render_compatibility_analysis_prompt(packet: dict[str, Any]) -> str:
    packet_for_prompt = {key: value for key, value in packet.items() if key != "prompt_markdown"}
    return (
        "Ты готовишь черновик русскоязычного jyotish-разбора совместимости для Gaudiya Vaishnava сервиса.\n\n"
        "Правила:\n"
        "- сравни обе карты с разных ракурсов, а не только по аштакуте;\n"
        "- используй расчеты как технические факты, не как фатальный приговор;\n"
        "- не выдумывай шастра-цитаты, номера глав, стихов или ссылки;\n"
        "- используй только citations из пакета;\n"
        "- если цитат не хватает, явно пометь место как needing citation review;\n"
        "- не советуй independent demigod worship;\n"
        "- любые remedial выводы формулируй через прибежище у Кришны, садхану, служение вайшнавам и наставления Шрилы Прабхупады;\n"
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
        f"{_translation_review_rules()}"
        "COMPATIBILITY ANALYSIS PACKET JSON:\n"
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
            "public_quotation_from_unreviewed_translation",
            "citation_titles_from_research_context",
            "fatalistic_guarantees",
            "medical_legal_financial_directives",
        ],
        "required_behaviors": [
            "cite_only_packet_citations",
            "compare_multiple_translation_variants",
            "cite_exact_edition_translator_and_reference",
            "flag_translation_conflicts",
            "mark_unverified_claims_for_review",
            "keep_remedies_krishna_centered",
            "preserve_calculation_uncertainty",
        ],
    }


def _translation_review_rules() -> str:
    return (
        "- compare_multiple_translation_variants: when source variants are present, compare them before final wording;\n"
        "- cite_exact_edition_translator_and_reference: every shastra quote must name work, chapter/verse if known, edition and translator;\n"
        "- flag_translation_conflicts: if translations disagree, say it is a translation/edition issue and keep the conclusion draft;\n"
        "- do not quote copyright_review_required or private_research_only passages in public text until approved.\n"
        "- research_context is private evidence only; do not copy it into citation_titles.\n"
    )


def _research_context(
    citation_requests: list[dict[str, Any]],
    research_search: ResearchSearch | None,
) -> dict[str, Any]:
    if research_search is None:
        return {
            "status": "not_configured",
            "items": [],
            "public_quote_policy": "not_public_citations",
        }
    items: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for query in _research_queries(citation_requests):
        for raw_item in research_search(query):
            item = dict(raw_item)
            item["is_public_citation"] = False
            item.setdefault("public_quote_policy", "blocked_until_approved")
            key = (str(item.get("work_title") or ""), str(item.get("title") or ""))
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
            if len(items) >= 12:
                return _research_context_payload(items)
    return _research_context_payload(items)


def _research_context_payload(items: list[dict[str, object]]) -> dict[str, Any]:
    return {
        "status": "private_research_not_public_citation",
        "items": items,
        "public_quote_policy": "not_public_citations_until_passage_approved",
    }


def _research_queries(citation_requests: list[dict[str, Any]]) -> list[str]:
    queries: list[str] = []
    for request in citation_requests:
        search_queries = request.get("search_queries", [])
        if isinstance(search_queries, list):
            queries.extend(str(query) for query in search_queries if str(query).strip())
        elif request.get("title"):
            queries.append(str(request["title"]))
        if len(queries) >= 8:
            break
    return queries


def _compatibility_generator_policy() -> dict[str, Any]:
    policy = _generator_policy()
    policy["required_behaviors"] = [
        "compare_both_charts_from_multiple_angles",
        *policy["required_behaviors"],
        "keep_final_marriage_guidance_under_human_review",
    ]
    policy["forbidden_outputs"] = [
        *policy["forbidden_outputs"],
        "final_marriage_verdict_without_human_review",
        "ashtakuta_only_verdict",
    ]
    return policy


def _packet_status(report: dict[str, Any], citations: list[dict[str, object]]) -> str:
    if report.get("review_status") == "needs_citation" or not citations:
        return "needs_citation_review"
    return "ready_for_generation"


def _compatibility_citation_requests(compatibility: dict[str, Any]) -> list[dict[str, Any]]:
    analysis = compatibility.get("analysis", {})
    source_anchors = _string_list(analysis.get("source_anchors"))
    perspectives = analysis.get("perspectives", [])
    if not isinstance(perspectives, list):
        return []
    rows = []
    for perspective in perspectives:
        if not isinstance(perspective, dict):
            continue
        key = str(perspective.get("key") or "")
        title = str(perspective.get("title") or key)
        basis = str(perspective.get("source_basis") or "")
        rows.append(
            {
                "kind": "compatibility_perspective",
                "key": key,
                "title": title,
                "source_basis": basis,
                "source_priority": source_anchors,
                "required_for_public_text": True,
                "citation_coverage_status": "needs_approved_passage",
                "search_queries": [
                    query
                    for source in source_anchors
                    for query in (f"{title} {source}", f"{basis} {source}")
                    if query.strip()
                ],
            }
        )
    return rows


def _compatibility_seed_query(compatibility: dict[str, Any]) -> str:
    analysis = compatibility.get("analysis", {})
    anchors = " ".join(_string_list(analysis.get("source_anchors")))
    return f"vivaha compatibility ashtakuta lagna moon seventh house {anchors}".strip()


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


def _citation_payloads_from_results(results: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "title": str(result.get("title") or result.get("work_title") or ""),
            "work_title": str(result.get("work_title") or ""),
            "snippet": str(result.get("snippet") or result.get("body") or ""),
            "public_url": str(result.get("public_url") or ""),
        }
        for result in results[:5]
        if result.get("title") or result.get("work_title")
    ]


def _required_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]
