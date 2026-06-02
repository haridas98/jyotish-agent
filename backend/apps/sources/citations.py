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


def local_research_corpus_search(query: str, limit: int = 5) -> list[dict[str, object]]:
    passages = (
        SourcePassage.objects.select_related("work")
        .filter(
            review_status=ReviewStatus.RESEARCH_ONLY,
            work__review_status=ReviewStatus.RESEARCH_ONLY,
        )
        .order_by("id")
    )
    private_chunks = passages.filter(metadata__import_kind="private_full_text_chunk")
    matched = list(_matching_passages(private_chunks, query)[:limit])
    if len(matched) < limit:
        private_ids = [passage.id for passage in matched]
        other_passages = passages.exclude(id__in=private_ids)
        matched.extend(list(_matching_passages(other_passages, query)[: limit - len(matched)]))
    return [_research_payload(passage) for passage in matched]


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


def _research_payload(passage: SourcePassage) -> dict[str, object]:
    metadata = passage.metadata if isinstance(passage.metadata, dict) else {}
    work_metadata = passage.work.metadata if isinstance(passage.work.metadata, dict) else {}
    return {
        "title": passage.reference,
        "work_title": passage.work.title,
        "body": passage.body[:1200],
        "source_url": passage.work.source_url,
        "review_status": passage.review_status,
        "work_review_status": passage.work.review_status,
        "rights_status": metadata.get("rights_status") or work_metadata.get("rights_status") or "",
        "public_quote_policy": metadata.get("public_quote_policy") or "blocked_until_approved",
        "is_public_citation": False,
    }
