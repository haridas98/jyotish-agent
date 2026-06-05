from __future__ import annotations

from typing import Any

from django.db.models import Count

from .models import ReviewStatus, SourcePassage, SourceWork


def source_inventory_payload(*, limit: int = 300) -> dict[str, Any]:
    works = (
        SourceWork.objects.annotate(passage_count=Count("passages"))
        .order_by("source_class", "title", "id")[: max(1, limit)]
    )
    total_works = SourceWork.objects.count()
    total_passages = SourcePassage.objects.count()
    research_works = SourceWork.objects.filter(review_status=ReviewStatus.RESEARCH_ONLY).count()
    research_passages = SourcePassage.objects.filter(review_status=ReviewStatus.RESEARCH_ONLY).count()
    return {
        "schema_version": "jyotish-source-inventory-v1",
        "summary": {
            "total_works": total_works,
            "total_passages": total_passages,
            "research_only_works": research_works,
            "research_only_passages": research_passages,
            "returned_works": len(works),
            "search_scope": "all_imported_source_passages",
        },
        "works": [_work_payload(work) for work in works],
    }


def work_passages_payload(work_slug: str, *, limit: int = 25, offset: int = 0) -> dict[str, Any]:
    work = SourceWork.objects.annotate(passage_count=Count("passages")).get(slug=work_slug)
    safe_limit = min(max(1, limit), 100)
    safe_offset = max(0, offset)
    passages = (
        SourcePassage.objects.filter(work=work)
        .order_by("id")[safe_offset : safe_offset + safe_limit]
    )
    return {
        "work": _work_payload(work),
        "limit": safe_limit,
        "offset": safe_offset,
        "items": [_passage_payload(passage) for passage in passages],
    }


def _work_payload(work: SourceWork) -> dict[str, Any]:
    metadata = work.metadata if isinstance(work.metadata, dict) else {}
    return {
        "id": work.id,
        "slug": work.slug,
        "title": work.title,
        "source_class": work.source_class,
        "author": work.author,
        "edition": work.edition,
        "language_code": work.language_code,
        "source_url": work.source_url,
        "review_status": work.review_status,
        "passage_count": getattr(work, "passage_count", None),
        "rights_status": metadata.get("rights_status") or "",
        "public_quote_policy": metadata.get("public_quote_policy") or "",
    }


def _passage_payload(passage: SourcePassage) -> dict[str, Any]:
    metadata = passage.metadata if isinstance(passage.metadata, dict) else {}
    return {
        "id": passage.id,
        "reference": passage.reference,
        "body": passage.body,
        "language_code": passage.language_code,
        "review_status": passage.review_status,
        "rights_status": metadata.get("rights_status") or "",
        "public_quote_policy": metadata.get("public_quote_policy") or "",
        "metadata": {
            key: value
            for key, value in metadata.items()
            if key in {"import_kind", "chunk_index", "chunk_count", "candidate_index"}
        },
    }
