from __future__ import annotations

import re
from typing import Any

from django.db import transaction
from django.db.models import Q

from apps.sources.models import ReviewStatus, SourcePassage

from .condition_matrix import shastra_condition_matrix
from .models import ShastraConditionEvidence

CANDIDATE_KINDS = {"candidate_shastra_passage", "private_full_text_chunk"}
STOPWORDS = {
    "and",
    "the",
    "with",
    "from",
    "source",
    "condition",
    "conditions",
    "yoga",
    "yogas",
    "raja",
    "nabhasa",
    "birth",
    "planet",
    "planets",
    "house",
    "houses",
}


@transaction.atomic
def build_shastra_evidence(
    *,
    condition_keys: list[str] | None = None,
    limit_per_condition: int = 5,
    min_score: int = 10,
) -> dict[str, Any]:
    conditions = _selected_conditions(condition_keys)
    processed = 0
    created_or_updated = 0
    for condition in conditions:
        processed += 1
        matches = _ranked_matches(condition, limit=max(1, limit_per_condition), min_score=min_score)
        for match in matches:
            _evidence, _created = ShastraConditionEvidence.objects.update_or_create(
                condition_key=str(condition["key"]),
                passage=match["passage"],
                defaults={
                    "condition_kind": str(condition["kind"]),
                    "condition_title": str(condition["title"]),
                    "score": int(match["score"]),
                    "inferred_reference": str(match["inferred_reference"]),
                    "reference_status": str(match["reference_status"]),
                    "public_quote_policy": str(match["public_quote_policy"]),
                    "review_status": ReviewStatus.RESEARCH_ONLY,
                    "metadata": {
                        "matcher": "lexical_condition_matcher_v1",
                        "matched_terms": match["matched_terms"],
                        "condition_summary": str(condition.get("condition_summary") or ""),
                        "source_priority": condition.get("source_priority") or [],
                    },
                },
            )
            created_or_updated += 1
    return {
        "schema_version": "jyotish-shastra-evidence-build-v1",
        "summary": {
            "conditions_processed": processed,
            "evidence_created_or_updated": created_or_updated,
            "limit_per_condition": limit_per_condition,
            "min_score": min_score,
        },
    }


def shastra_evidence_payload(
    *,
    condition_keys: list[str] | None = None,
    limit_per_condition: int = 5,
) -> dict[str, Any]:
    conditions = _selected_conditions(condition_keys)
    rows = []
    for condition in conditions:
        evidence = list(
            ShastraConditionEvidence.objects.select_related("passage", "passage__work")
            .filter(condition_key=str(condition["key"]))
            .order_by("-score", "id")[:limit_per_condition]
        )
        rows.append(
            {
                "condition_key": str(condition["key"]),
                "condition_kind": str(condition["kind"]),
                "condition_title": str(condition["title"]),
                "condition_summary": str(condition.get("condition_summary") or ""),
                "evidence_status": "matched" if evidence else "missing",
                "public_release_policy": (
                    "needs_human_review" if any(item.reference_status != "approved" for item in evidence) else "approved"
                ),
                "evidence": [_evidence_payload(item) for item in evidence],
            }
        )
    return {
        "schema_version": "jyotish-shastra-evidence-v1",
        "summary": {
            "conditions": len(rows),
            "conditions_with_evidence": sum(1 for row in rows if row["evidence_status"] == "matched"),
            "evidence_items": sum(len(row["evidence"]) for row in rows),
        },
        "prompt_rules": [
            "do not quote research-only passages publicly; paraphrase only for internal draft analysis",
            "do not invent chapter or verse numbers; use inferred_reference only with reference_status",
            "every final interpretation must cite approved passages or remain draft",
            "reframe remedies through Krishna-bhakti, sadhu-sanga and Srila Prabhupada's guidance",
        ],
        "conditions": rows,
    }


def _selected_conditions(condition_keys: list[str] | None) -> list[dict[str, Any]]:
    wanted = {str(key) for key in condition_keys or [] if str(key).strip()}
    conditions = shastra_condition_matrix()["conditions"]
    if not wanted:
        return conditions
    return [condition for condition in conditions if str(condition["key"]) in wanted]


def _ranked_matches(condition: dict[str, Any], *, limit: int, min_score: int) -> list[dict[str, Any]]:
    terms = _condition_terms(condition)
    if not terms:
        return []
    passages = _candidate_passages(terms)
    matches = []
    for passage in passages:
        score, matched_terms = _score(condition, passage, terms)
        if score < min_score:
            continue
        inferred_reference = _infer_reference(passage.body)
        matches.append(
            {
                "passage": passage,
                "score": score,
                "matched_terms": matched_terms,
                "inferred_reference": inferred_reference,
                "reference_status": "inferred_needs_review" if inferred_reference else "needs_review",
                "public_quote_policy": _public_quote_policy(passage),
            }
        )
    return sorted(matches, key=lambda item: (-int(item["score"]), item["passage"].id))[:limit]


def _candidate_passages(terms: list[str]):
    query = Q()
    for term in terms[:10]:
        query |= Q(reference__icontains=term)
        query |= Q(body__icontains=term)
        query |= Q(work__title__icontains=term)
    return (
        SourcePassage.objects.select_related("work")
        .filter(
            query,
            review_status__in=[ReviewStatus.RESEARCH_ONLY, ReviewStatus.APPROVED],
        )
        .filter(Q(metadata__import_kind__in=sorted(CANDIDATE_KINDS)) | Q(review_status=ReviewStatus.APPROVED))
        .order_by("id")[:250]
    )


def _score(condition: dict[str, Any], passage: SourcePassage, terms: list[str]) -> tuple[int, list[str]]:
    text = _normalize(f"{passage.reference} {passage.body} {passage.work.title}")
    title = _normalize(str(condition.get("title") or ""))
    source_priority = [str(source) for source in condition.get("source_priority") or []]
    score = 0
    matched_terms = []
    if title and title in text:
        score += 25
    title_terms = _tokens(title)
    if title_terms and all(term in text for term in title_terms):
        score += 12
    for term in terms:
        if term in text:
            matched_terms.append(term)
            score += 8 if term in title_terms else 3
    if _source_matches(passage, source_priority):
        score += 8
    if re.search(r"\b(?:sloka|stanza|verse|chapter|adhyaya)\b", passage.body, flags=re.IGNORECASE):
        score += 4
    if passage.metadata.get("import_kind") == "candidate_shastra_passage":
        score += 2
    return score, sorted(set(matched_terms))


def _condition_terms(condition: dict[str, Any]) -> list[str]:
    raw = " ".join(
        [
            str(condition.get("key") or "").replace("_", " "),
            str(condition.get("title") or ""),
            str(condition.get("condition_summary") or ""),
        ]
    )
    terms = []
    for term in _tokens(raw):
        if term in STOPWORDS or len(term) < 3:
            continue
        terms.append(term)
    return sorted(set(terms), key=lambda value: (-len(value), value))[:16]


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", _normalize(value))


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower())


def _source_matches(passage: SourcePassage, source_priority: list[str]) -> bool:
    haystack = _normalize(f"{passage.work.slug} {passage.work.title}")
    return any(_source_key(source) in haystack for source in source_priority)


def _source_key(source: str) -> str:
    normalized = _normalize(source.replace("-", " "))
    aliases = {
        "phaladeepika": "phaladipika",
        "gochar phaladeepika": "phaladipika",
        "bp hs with caution": "brhat parashara",
        "bphs with caution": "brhat parashara",
    }
    return aliases.get(normalized, normalized)


def _infer_reference(text: str) -> str:
    chapter = _first_match(
        text,
        [
            r"\bAdhyaya\s+([IVXLCDM]+|\d+)\b",
            r"\bChapter\s+([IVXLCDM]+|\d+)\b",
        ],
    )
    verse = _first_match(
        text,
        [
            r"\bSloka\s+(\d+[A-Za-z]?)\b",
            r"\bStanza\s+(\d+[A-Za-z]?)\b",
            r"\bVerse\s+(\d+[A-Za-z]?)\b",
        ],
    )
    parts = []
    if chapter:
        parts.append(chapter)
    if verse:
        parts.append(verse)
    return ", ".join(parts)


def _first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            label = pattern.split("\\b")[1].split("\\s+")[0]
            return f"{label.title()} {match.group(1)}"
    return ""


def _public_quote_policy(passage: SourcePassage) -> str:
    return str(
        passage.metadata.get("public_quote_policy")
        or passage.work.metadata.get("public_quote_policy")
        or "blocked_until_approved"
    )


def _evidence_payload(evidence: ShastraConditionEvidence) -> dict[str, Any]:
    passage = evidence.passage
    return {
        "id": evidence.id,
        "score": evidence.score,
        "work_slug": passage.work.slug,
        "work_title": passage.work.title,
        "source_url": passage.work.source_url,
        "passage_id": passage.id,
        "passage_reference": passage.reference,
        "inferred_reference": evidence.inferred_reference,
        "reference_status": evidence.reference_status,
        "review_status": evidence.review_status,
        "public_quote_policy": evidence.public_quote_policy,
        "snippet": passage.body[:1200],
        "matched_terms": evidence.metadata.get("matched_terms", []),
    }
