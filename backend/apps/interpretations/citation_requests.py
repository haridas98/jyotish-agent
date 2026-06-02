from __future__ import annotations

from typing import Any


def build_citation_requests(
    *,
    explanation_schedule: list[dict[str, Any]],
    detected_yoga_source_map: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_section_requests(explanation_schedule))
    rows.extend(_yoga_requests(detected_yoga_source_map))
    return rows


def _section_requests(explanation_schedule: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for section in explanation_schedule:
        key = str(section.get("key") or "")
        if not key:
            continue
        title = str(section.get("title_ru") or key)
        source_priority = _string_list(section.get("source_priority"))
        rows.append(
            {
                "kind": "section",
                "key": key,
                "title": title,
                "depends_on": _string_list(section.get("depends_on")),
                "source_priority": source_priority,
                "implementation_status": str(section.get("implementation_status") or ""),
                "required_for_public_text": True,
                "citation_coverage_status": "needs_approved_passage",
                "search_queries": _queries(title, source_priority),
            }
        )
    return rows


def _yoga_requests(detected_yoga_source_map: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for yoga in detected_yoga_source_map:
        key = str(yoga.get("key") or "")
        if not key:
            continue
        source_priority = _string_list(yoga.get("source_priority"))
        release_policy = str(yoga.get("public_release_policy") or "")
        is_blocked = release_policy == "block_public_interpretation"
        rows.append(
            {
                "kind": "detected_yoga",
                "key": key,
                "catalog_key": str(yoga.get("catalog_key") or key),
                "title": str(yoga.get("name") or key),
                "source_priority": source_priority,
                "source_mapping_status": str(yoga.get("source_mapping_status") or ""),
                "public_release_policy": release_policy,
                "required_for_public_text": True,
                "citation_coverage_status": (
                    "blocked_until_catalog_mapping" if is_blocked else "needs_approved_passage"
                ),
                "search_queries": [] if is_blocked else _queries(str(yoga.get("name") or key), source_priority),
            }
        )
    return rows


def _queries(title: str, source_priority: list[str]) -> list[str]:
    return [f"{title} {source}" for source in source_priority]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]
