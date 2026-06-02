from __future__ import annotations

from django.db.models import Q

from apps.sources.models import ReviewStatus, SourcePassage, SourceWork
from apps.vl_integration.client import search_vl_documents


def combined_citation_search(
    database_url: str,
    query: str,
    limit: int = 3,
    public_base_url: str = "",
) -> list[dict[str, object]]:
    try:
        vl_results = search_vl_documents(
            database_url,
            query,
            limit=limit,
            public_base_url=public_base_url,
        )
    except Exception:
        vl_results = []
    return vl_results or local_approved_citation_search(query, limit=limit)


def local_approved_citation_search(query: str, limit: int = 3) -> list[dict[str, object]]:
    passages = (
        SourcePassage.objects.select_related("work")
        .prefetch_related("vl_links")
        .filter(
            review_status=ReviewStatus.APPROVED,
            work__review_status=ReviewStatus.APPROVED,
        )
    )
    matched = list(_matching_passages(passages, query)[:limit])
    fallback = passages.filter(
        work__source_class__in=[
            SourceWork.SourceClass.CANONICAL_PRABHUPADA,
            SourceWork.SourceClass.CANONICAL_GAUDIYA,
        ]
    )
    selected = matched or list(fallback.order_by("id")[:limit])
    return [_citation_payload(passage) for passage in selected]


def _matching_passages(passages, query: str):
    terms = [term.strip() for term in query.split() if len(term.strip()) >= 3][:6]
    if not terms:
        return passages.none()

    condition = Q()
    for term in terms:
        condition |= Q(reference__icontains=term)
        condition |= Q(body__icontains=term)
        condition |= Q(work__title__icontains=term)
    return passages.filter(condition).order_by("id")


def _citation_payload(passage: SourcePassage) -> dict[str, object]:
    public_url = ""
    for link in passage.vl_links.all():
        if link.public_url:
            public_url = link.public_url
            break
    return {
        "title": passage.reference,
        "work_title": passage.work.title,
        "body": passage.body[:600],
        "public_url": public_url or passage.work.source_url,
    }
