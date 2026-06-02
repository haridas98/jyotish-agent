from __future__ import annotations

import re
from typing import Any

from django.db import transaction

from .models import ReviewStatus, SourcePassage, SourceWork

PRIVATE_CHUNK_KIND = "private_full_text_chunk"
CANDIDATE_KIND = "candidate_shastra_passage"


@transaction.atomic
def segment_private_work(work_slug: str, max_chars: int = 1800) -> dict[str, int]:
    work = SourceWork.objects.get(slug=work_slug)
    chunks = list(
        SourcePassage.objects.filter(
            work=work,
            metadata__import_kind=PRIVATE_CHUNK_KIND,
        ).order_by("reference")
    )
    candidate_index = 0
    for chunk in chunks:
        for body in _candidate_units(chunk.body, max_chars=max(120, max_chars)):
            candidate_index += 1
            SourcePassage.objects.update_or_create(
                work=work,
                reference=f"candidate passage {candidate_index:04d}",
                language_code=work.language_code,
                defaults={
                    "body": body,
                    "review_status": ReviewStatus.RESEARCH_ONLY,
                    "metadata": {
                        "import_kind": CANDIDATE_KIND,
                        "source_reference": chunk.reference,
                        "candidate_index": candidate_index,
                        "exact_reference_status": "needs_review",
                        "rights_status": chunk.metadata.get(
                            "rights_status",
                            work.metadata.get("rights_status", "private_research_only_until_approved"),
                        ),
                        "public_quote_policy": "blocked_until_approved",
                    },
                },
            )
    return {"source_chunks": len(chunks), "candidate_passages": candidate_index}


@transaction.atomic
def segment_private_corpus(work_slug: str | None = None, max_chars: int = 1800) -> dict[str, Any]:
    works = _private_works(work_slug)
    results = [segment_private_work(work.slug, max_chars=max_chars) for work in works]
    return {
        "works": len(works),
        "source_chunks": sum(result["source_chunks"] for result in results),
        "candidate_passages": sum(result["candidate_passages"] for result in results),
    }


def _private_works(work_slug: str | None) -> list[SourceWork]:
    queryset = SourceWork.objects.filter(passages__metadata__import_kind=PRIVATE_CHUNK_KIND)
    if work_slug:
        queryset = queryset.filter(slug=work_slug)
    return list(queryset.distinct().order_by("slug"))


def _candidate_units(text: str, max_chars: int) -> list[str]:
    paragraphs = _presegment(text)
    units: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if _starts_new_unit(paragraph) and current:
            units.extend(_bounded_units(current, max_chars=max_chars))
            current = ""
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            units.extend(_bounded_units(current, max_chars=max_chars))
        units.extend(_bounded_units(paragraph, max_chars=max_chars))
        current = ""
    if current:
        units.extend(_bounded_units(current, max_chars=max_chars))
    return [unit for unit in units if unit.strip()]


def _presegment(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized = re.sub(r"(?im)(?=^\s*(?:sloka|śloka|stanza|verse)\s+\d+)", "\n\n", normalized)
    normalized = re.sub(r"(?im)(?=^---\s*page\s+\d+\s*---\s*$)", "\n\n", normalized)
    return [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]


def _starts_new_unit(paragraph: str) -> bool:
    return bool(
        re.match(
            r"(?is)^(?:---\s*page\s+\d+\s*---\s*)?(?:sloka|śloka|stanza|verse)\s+\d+",
            paragraph.strip(),
        )
    )


def _bounded_units(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    units: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence.strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            units.append(current)
        if len(sentence) > max_chars:
            units.extend(_hard_units(sentence, max_chars=max_chars))
            current = ""
        else:
            current = sentence.strip()
    if current:
        units.append(current)
    return units


def _hard_units(text: str, max_chars: int) -> list[str]:
    return [
        text[index : index + max_chars].strip()
        for index in range(0, len(text), max_chars)
        if text[index : index + max_chars].strip()
    ]
