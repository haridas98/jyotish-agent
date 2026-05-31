from __future__ import annotations

from typing import Any

from django.db.models import Prefetch

from apps.sources.models import ReviewStatus, SourcePassage

from .models import InterpretationBlock, InterpretationRule


def public_interpretation_sections_for_chart(chart: dict[str, Any]) -> list[dict[str, Any]]:
    rules = (
        InterpretationRule.objects.filter(review_status=ReviewStatus.APPROVED)
        .prefetch_related(
            Prefetch(
                "blocks",
                queryset=InterpretationBlock.objects.filter(
                    review_status=ReviewStatus.APPROVED
                ).order_by("id"),
            ),
            "passages__work",
            "passages__vl_links",
        )
        .order_by("priority", "slug")
    )
    sections: list[dict[str, Any]] = []
    for rule in rules:
        if not _matches_condition(rule.condition, chart):
            continue
        citations = _approved_citations(rule)
        if not citations:
            continue
        for block in rule.blocks.all():
            sections.append(
                {
                    "key": f"interpretation:{rule.slug}",
                    "title": block.title,
                    "body": block.body,
                    "review_status": ReviewStatus.APPROVED,
                    "calculation_only": False,
                    "citations": citations,
                    "rule": {
                        "slug": rule.slug,
                        "section": block.section,
                        "priority": rule.priority,
                    },
                }
            )
    return sections


def _matches_condition(condition: dict[str, Any], chart: dict[str, Any]) -> bool:
    if not condition:
        return False
    clauses = condition.get("all")
    if isinstance(clauses, list):
        return all(_matches_clause(clause, chart) for clause in clauses)
    return _matches_clause(condition, chart)


def _matches_clause(clause: Any, chart: dict[str, Any]) -> bool:
    if not isinstance(clause, dict):
        return False

    path = clause.get("path")
    if isinstance(path, str) and "equals" in clause:
        return _value_at_path(chart, path) == clause["equals"]

    collection = clause.get("collection")
    where = clause.get("where")
    if isinstance(collection, str) and isinstance(where, dict):
        items = chart.get(collection)
        if not isinstance(items, list):
            return False
        return any(
            isinstance(item, dict)
            and all(item.get(field) == expected for field, expected in where.items())
            for item in items
        )

    return False


def _value_at_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _approved_citations(rule: InterpretationRule) -> list[dict[str, object]]:
    return [
        _citation_payload(passage)
        for passage in rule.passages.all()
        if passage.review_status == ReviewStatus.APPROVED
        and passage.work.review_status == ReviewStatus.APPROVED
    ]


def _citation_payload(passage: SourcePassage) -> dict[str, object]:
    public_url = ""
    for link in passage.vl_links.all():
        if link.public_url:
            public_url = link.public_url
            break
    return {
        "title": passage.reference,
        "work_title": passage.work.title,
        "snippet": passage.body[:600],
        "public_url": public_url or passage.work.source_url,
    }
