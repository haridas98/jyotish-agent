from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.sources.models import ReviewStatus, SourcePassage, SourceWork, VLCitationLink

from .models import InterpretationBlock, InterpretationRule


@transaction.atomic
def import_interpretation_catalog(catalog: dict[str, Any]) -> dict[str, int]:
    works = _import_works(_list(catalog, "works"))
    passages = _import_passages(_list(catalog, "passages"), works)
    rules = _import_rules(_list(catalog, "rules"), passages)
    return {
        "works": len(works),
        "passages": len(passages),
        "rules": rules,
        "blocks": InterpretationBlock.objects.filter(
            rule__slug__in=[str(item.get("slug")) for item in _list(catalog, "rules")]
        ).count(),
    }


def _import_works(items: list[dict[str, Any]]) -> dict[str, SourceWork]:
    works = {}
    for item in items:
        slug = _required_str(item, "slug")
        source_class = _choice(item.get("source_class", SourceWork.SourceClass.RESEARCH_ONLY), SourceWork.SourceClass.values)
        review_status = _choice(item.get("review_status", ReviewStatus.DRAFT), ReviewStatus.values)
        work, _created = SourceWork.objects.update_or_create(
            slug=slug,
            defaults={
                "title": _required_str(item, "title"),
                "source_class": source_class,
                "author": str(item.get("author") or ""),
                "edition": str(item.get("edition") or ""),
                "language_code": str(item.get("language_code") or "en"),
                "source_url": str(item.get("source_url") or ""),
                "review_status": review_status,
                "metadata": item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
            },
        )
        works[slug] = work
    return works


def _import_passages(
    items: list[dict[str, Any]],
    works: dict[str, SourceWork],
) -> dict[tuple[str, str, str], SourcePassage]:
    passages = {}
    for item in items:
        work_slug = _required_str(item, "work_slug")
        work = works.get(work_slug) or SourceWork.objects.filter(slug=work_slug).first()
        if work is None:
            raise ValueError(f"Unknown work_slug: {work_slug}")
        reference = _required_str(item, "reference")
        language_code = str(item.get("language_code") or "en")
        passage, _created = SourcePassage.objects.update_or_create(
            work=work,
            reference=reference,
            language_code=language_code,
            defaults={
                "body": str(item.get("body") or ""),
                "review_status": _choice(item.get("review_status", ReviewStatus.DRAFT), ReviewStatus.values),
                "metadata": item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
            },
        )
        public_url = str(item.get("public_url") or "")
        if public_url:
            VLCitationLink.objects.get_or_create(
                passage=passage,
                public_url=public_url,
                defaults={"metadata": item.get("link_metadata") if isinstance(item.get("link_metadata"), dict) else {}},
            )
        passages[(work_slug, reference, language_code)] = passage
    return passages


def _import_rules(
    items: list[dict[str, Any]],
    passages: dict[tuple[str, str, str], SourcePassage],
) -> int:
    for item in items:
        slug = _required_str(item, "slug")
        rule, _created = InterpretationRule.objects.update_or_create(
            slug=slug,
            defaults={
                "title": _required_str(item, "title"),
                "condition": item.get("condition") if isinstance(item.get("condition"), dict) else {},
                "priority": int(item.get("priority") or 100),
                "review_status": _choice(item.get("review_status", ReviewStatus.DRAFT), ReviewStatus.values),
                "metadata": item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
            },
        )
        rule.passages.set([_passage_for_ref(ref, passages) for ref in _list(item, "passage_refs")])
        for block in _list(item, "blocks"):
            InterpretationBlock.objects.update_or_create(
                rule=rule,
                section=_required_str(block, "section"),
                title=_required_str(block, "title"),
                defaults={
                    "body": _required_str(block, "body"),
                    "language_code": str(block.get("language_code") or "ru"),
                    "review_status": _choice(block.get("review_status", ReviewStatus.DRAFT), ReviewStatus.values),
                    "metadata": block.get("metadata") if isinstance(block.get("metadata"), dict) else {},
                },
            )
    return len(items)


def _passage_for_ref(ref: dict[str, Any], passages: dict[tuple[str, str, str], SourcePassage]) -> SourcePassage:
    work_slug = _required_str(ref, "work_slug")
    reference = _required_str(ref, "reference")
    language_code = str(ref.get("language_code") or "en")
    key = (work_slug, reference, language_code)
    passage = passages.get(key)
    if passage is None:
        passage = SourcePassage.objects.filter(
            work__slug=work_slug,
            reference=reference,
            language_code=language_code,
        ).first()
    if passage is None:
        raise ValueError(f"Unknown passage reference: {work_slug} / {reference} / {language_code}")
    return passage


def _list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return [item for item in value if isinstance(item, dict)]


def _required_str(data: dict[str, Any], key: str) -> str:
    value = str(data.get(key) or "").strip()
    if not value:
        raise ValueError(f"{key} is required")
    return value


def _choice(value: object, allowed: list[str]) -> str:
    normalized = str(value or "").strip()
    if normalized not in allowed:
        raise ValueError(f"Unsupported choice: {normalized}")
    return normalized
