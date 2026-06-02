from __future__ import annotations

import re
from typing import Any

from apps.calculations.shastra_audit import CALCULATION_SHASTRA_AUDIT

from .models import ReviewStatus, SourcePassage, SourceWork

ALIASES = {
    "bphs-with-caution": "brhat-parashara-hora-shastra",
    "bp-hs-with-caution": "brhat-parashara-hora-shastra",
    "brhat-parashara-hora-sastra": "brhat-parashara-hora-shastra",
    "parasara-hora-sastra": "brhat-parashara-hora-shastra",
    "phaladeepika": "phaladipika",
    "gochar-phaladeepika": "phaladipika",
    "gochar-phaladipika": "phaladipika",
    "jhora": "jhora",
    "teacher-review": "teacher-review",
    "varga-tradition-review": "varga-tradition-review",
    "vivaha-tradition-review": "vivaha-tradition-review",
}


def source_coverage_matrix(targets: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    source_cache: dict[str, dict[str, Any]] = {}
    layers = [_layer_coverage(item, source_cache=source_cache) for item in (targets or CALCULATION_SHASTRA_AUDIT)]
    return {
        "schema_version": "jyotish-source-coverage-v1",
        "summary": {
            "total_layers": len(layers),
            "layers_with_private_text": sum(
                1 for layer in layers if layer["coverage_status"] == "private_text_loaded"
            ),
            "layers_with_approved_passages": sum(
                1 for layer in layers if layer["coverage_status"] == "approved_passages_ready"
            ),
            "layers_needing_exact_mapping": sum(1 for layer in layers if layer["needs_exact_mapping"]),
            "missing_sources": sum(
                1
                for layer in layers
                for source in layer["sources"]
                if source["coverage_status"] == "missing"
            ),
        },
        "layers": layers,
    }


def _layer_coverage(item: dict[str, Any], *, source_cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sources = [_cached_source_coverage(source_key, source_cache) for source_key in item.get("source_priority", [])]
    approved_count = sum(int(source["approved_passages"]) for source in sources)
    private_count = sum(int(source["private_full_text_chunks"]) for source in sources)
    research_count = sum(int(source["research_passages"]) for source in sources)
    coverage_status = _layer_status(approved_count, private_count, research_count, sources)
    return {
        "key": str(item.get("key") or ""),
        "label": str(item.get("label") or item.get("title_ru") or item.get("key") or ""),
        "source_basis": str(item.get("source_basis") or ""),
        "implementation_status": str(item.get("implementation_status") or ""),
        "public_claim": str(item.get("public_claim") or ""),
        "coverage_status": coverage_status,
        "needs_exact_mapping": approved_count == 0,
        "sources": sources,
    }


def _cached_source_coverage(source_key: object, source_cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    raw_key = str(source_key or "").strip()
    if raw_key not in source_cache:
        source_cache[raw_key] = _source_coverage(raw_key)
    return source_cache[raw_key]


def _source_coverage(source_key: object) -> dict[str, Any]:
    raw_key = str(source_key or "").strip()
    normalized = ALIASES.get(_slug(raw_key), _slug(raw_key))
    if normalized in {"", "jhora", "teacher-review", "varga-tradition-review", "vivaha-tradition-review"}:
        return _missing_payload(raw_key, normalized)
    works = list(_matching_works(normalized))
    if not works:
        return _missing_payload(raw_key, normalized)
    passages = SourcePassage.objects.filter(work__in=works)
    approved = passages.filter(review_status=ReviewStatus.APPROVED).count()
    research = passages.filter(review_status=ReviewStatus.RESEARCH_ONLY).count()
    private_chunks = passages.filter(metadata__import_kind="private_full_text_chunk").count()
    return {
        "source_key": raw_key,
        "normalized_key": normalized,
        "coverage_status": _source_status(approved, private_chunks, research, works),
        "works": [
            {
                "slug": work.slug,
                "title": work.title,
                "review_status": work.review_status,
                "source_url": work.source_url,
            }
            for work in works
        ],
        "approved_passages": approved,
        "research_passages": research,
        "private_full_text_chunks": private_chunks,
    }


def _matching_works(normalized: str):
    exact = SourceWork.objects.filter(slug=normalized)
    prefixed = SourceWork.objects.filter(slug__startswith=f"{normalized}-")
    title_matches = SourceWork.objects.filter(title__icontains=normalized.replace("-", " "))
    return (exact | prefixed | title_matches).distinct().order_by("slug")


def _source_status(
    approved: int,
    private_chunks: int,
    research: int,
    works: list[SourceWork],
) -> str:
    if approved:
        return "approved_passages_available"
    if private_chunks:
        return "private_full_text_available"
    if research:
        return "research_passages_available"
    if works:
        return "source_work_registered"
    return "missing"


def _layer_status(
    approved_count: int,
    private_count: int,
    research_count: int,
    sources: list[dict[str, Any]],
) -> str:
    if approved_count:
        return "approved_passages_ready"
    if private_count:
        return "private_text_loaded"
    if research_count:
        return "research_only_available"
    if any(source["coverage_status"] == "source_work_registered" for source in sources):
        return "source_anchor_only"
    return "missing_sources"


def _missing_payload(raw_key: str, normalized: str) -> dict[str, Any]:
    return {
        "source_key": raw_key,
        "normalized_key": normalized,
        "coverage_status": "missing",
        "works": [],
        "approved_passages": 0,
        "research_passages": 0,
        "private_full_text_chunks": 0,
    }


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
