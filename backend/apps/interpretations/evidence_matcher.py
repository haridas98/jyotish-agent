from __future__ import annotations

import re
from typing import Any

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.sources.models import ReviewStatus, SourcePassage

from .condition_matrix import shastra_condition_matrix
from .models import ShastraConditionEvidence
from .yoga_catalog import CATALOG_WORK_SLUG

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
        if not matches and str(condition.get("kind") or "") == "yoga_condition":
            matches = _yoga_catalog_anchor_matches(condition)
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
                        "matcher": (match.get("metadata") or {}).get("matcher", "lexical_condition_matcher_v1"),
                        "matched_terms": match["matched_terms"],
                        "condition_summary": str(condition.get("condition_summary") or ""),
                        "source_priority": condition.get("source_priority") or [],
                        **(match.get("metadata") or {}),
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


@transaction.atomic
def approve_shastra_condition_evidence(
    evidence_id: int,
    *,
    exact_reference: str,
    approved_excerpt: str,
    reviewer: str = "",
    notes: str = "",
) -> dict[str, Any]:
    exact_reference = exact_reference.strip()
    approved_excerpt = approved_excerpt.strip()
    if not exact_reference:
        raise ValueError("exact_reference is required")
    if not approved_excerpt:
        raise ValueError("approved_excerpt is required")

    evidence = (
        ShastraConditionEvidence.objects.select_for_update()
        .select_related("passage", "passage__work")
        .get(id=evidence_id)
    )
    passage = evidence.passage
    passage.reference = exact_reference
    passage.review_status = ReviewStatus.APPROVED
    passage.metadata = {
        **(passage.metadata if isinstance(passage.metadata, dict) else {}),
        "public_quote_policy": "approved_public_quote",
        "approved_excerpt": approved_excerpt,
        "approved_by": reviewer,
        "approved_at": timezone.now().isoformat(),
    }
    passage.save(update_fields=["reference", "review_status", "metadata", "updated_at"])

    evidence.inferred_reference = exact_reference
    evidence.reference_status = "approved"
    evidence.public_quote_policy = "approved_public_quote"
    evidence.review_status = ReviewStatus.APPROVED
    evidence.metadata = {
        **(evidence.metadata if isinstance(evidence.metadata, dict) else {}),
        "approved_reference": exact_reference,
        "approved_excerpt": approved_excerpt,
        "reviewer": reviewer,
        "review_notes": notes,
        "approved_at": timezone.now().isoformat(),
    }
    evidence.save(
        update_fields=[
            "inferred_reference",
            "reference_status",
            "public_quote_policy",
            "review_status",
            "metadata",
            "updated_at",
        ]
    )
    return _evidence_payload(evidence)


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
        approved_citations = [_approved_citation_payload(item) for item in evidence if _is_publicly_approved(item)]
        rows.append(
            {
                "condition_key": str(condition["key"]),
                "condition_kind": str(condition["kind"]),
                "condition_title": str(condition["title"]),
                "condition_summary": str(condition.get("condition_summary") or ""),
                "evidence_status": "matched" if evidence else "missing",
                "public_release_policy": _public_release_policy_for_condition(evidence),
                "approved_citations": approved_citations,
                "evidence": [_evidence_payload(item) for item in evidence],
            }
        )
    return {
        "schema_version": "jyotish-shastra-evidence-v1",
        "summary": {
            "conditions": len(rows),
            "conditions_with_evidence": sum(1 for row in rows if row["evidence_status"] == "matched"),
            "evidence_items": sum(len(row["evidence"]) for row in rows),
            "approved_conditions": sum(1 for row in rows if row["approved_citations"]),
            "approved_evidence_items": sum(len(row["approved_citations"]) for row in rows),
            "review_queue_items": sum(
                1
                for row in rows
                for item in row["evidence"]
                if item["review_status"] != ReviewStatus.APPROVED
                or item["reference_status"] != "approved"
                or item["public_quote_policy"] != "approved_public_quote"
            ),
        },
        "prompt_rules": [
            "do not quote research-only passages publicly; paraphrase only for internal draft analysis",
            "do not invent chapter or verse numbers; use inferred_reference only with reference_status",
            "every final interpretation must cite approved passages or remain draft",
            "reframe remedies through Krishna-bhakti, sadhu-sanga and Srila Prabhupada's guidance",
        ],
        "conditions": rows,
    }


def shastra_source_trace_payload(
    *,
    condition_keys: list[str] | None = None,
    limit_per_condition: int = 3,
) -> dict[str, Any]:
    conditions = _selected_conditions(condition_keys)
    traces = []
    for condition in conditions:
        evidence_rows = (
            ShastraConditionEvidence.objects.select_related("passage", "passage__work")
            .filter(condition_key=str(condition["key"]))
            .order_by("-score", "id")[: max(1, limit_per_condition)]
        )
        for evidence in evidence_rows:
            traces.append(_source_trace_payload(condition, evidence))
    return {
        "schema_version": "jyotish-shastra-source-traces-v1",
        "summary": {
            "conditions": len(conditions),
            "traces": len(traces),
            "approved_traces": sum(1 for trace in traces if trace["source_status"] == "approved"),
            "research_only_traces": sum(1 for trace in traces if trace["source_status"] != "approved"),
        },
        "rules": [
            "Use trace rows as condition-to-source scaffolding.",
            "Do not present inferred references as final public citations.",
            "Private analysis may paraphrase research-only fragments with status shown.",
            "Final public quotes require approved source traces.",
        ],
        "traces": traces,
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


def _yoga_catalog_anchor_matches(condition: dict[str, Any]) -> list[dict[str, Any]]:
    passage = SourcePassage.objects.select_related("work").filter(
        work__slug=CATALOG_WORK_SLUG,
        metadata__yoga_key=str(condition.get("key") or ""),
    ).first()
    if passage is None:
        return []
    source_anchors = _source_anchors_for_condition(condition, passage)
    primary_anchor = source_anchors[0] if source_anchors else {}
    matcher = "curated_yoga_source_anchor_v1" if primary_anchor else "yoga_catalog_anchor_v1"
    return [
        {
            "passage": passage,
            "score": 5 if primary_anchor else 1,
            "matched_terms": [],
            "inferred_reference": str(primary_anchor.get("reference") or passage.reference),
            "reference_status": str(
                primary_anchor.get("reference_status") or "research_anchor_needs_exact_source"
            ),
            "public_quote_policy": str(
                primary_anchor.get("public_quote_policy") or "blocked_until_approved"
            ),
            "metadata": {
                "matcher": matcher,
                "exact_source_required": not bool(primary_anchor),
                "source_priority": condition.get("source_priority") or [],
                "source_anchor": primary_anchor,
                "source_anchors": source_anchors,
            },
        }
    ]


def _source_anchors_for_condition(condition: dict[str, Any], passage: SourcePassage) -> list[dict[str, Any]]:
    anchors = condition.get("source_anchors")
    if not anchors and isinstance(condition.get("formula"), dict):
        anchors = condition["formula"].get("source_anchors")
    if not anchors and isinstance(passage.metadata, dict):
        anchors = passage.metadata.get("source_anchors")
    if not isinstance(anchors, list):
        return []
    return [dict(anchor) for anchor in anchors if isinstance(anchor, dict)]


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


def _public_release_policy_for_condition(evidence: list[ShastraConditionEvidence]) -> str:
    if any(_is_publicly_approved(item) for item in evidence):
        return "approved"
    if evidence:
        return "needs_human_review"
    return "needs_approved_passage"


def _is_publicly_approved(evidence: ShastraConditionEvidence) -> bool:
    return (
        evidence.review_status == ReviewStatus.APPROVED
        and evidence.reference_status == "approved"
        and evidence.public_quote_policy == "approved_public_quote"
        and evidence.passage.review_status == ReviewStatus.APPROVED
    )


def _approved_citation_payload(evidence: ShastraConditionEvidence) -> dict[str, Any]:
    passage = evidence.passage
    metadata = evidence.metadata if isinstance(evidence.metadata, dict) else {}
    return {
        "condition_key": evidence.condition_key,
        "condition_title": evidence.condition_title,
        "work_slug": passage.work.slug,
        "work_title": passage.work.title,
        "source_url": passage.work.source_url,
        "passage_id": passage.id,
        "evidence_id": evidence.id,
        "reference": metadata.get("approved_reference") or evidence.inferred_reference or passage.reference,
        "excerpt": metadata.get("approved_excerpt") or passage.body[:600],
        "reviewer": metadata.get("reviewer") or "",
        "review_status": evidence.review_status,
        "public_quote_policy": evidence.public_quote_policy,
    }


def _source_trace_payload(condition: dict[str, Any], evidence: ShastraConditionEvidence) -> dict[str, Any]:
    passage = evidence.passage
    metadata = evidence.metadata if isinstance(evidence.metadata, dict) else {}
    source_anchor = metadata.get("source_anchor") if isinstance(metadata.get("source_anchor"), dict) else {}
    reference = (
        metadata.get("approved_reference")
        or evidence.inferred_reference
        or source_anchor.get("reference")
        or passage.reference
    )
    chapter, verse = _chapter_verse(reference)
    source_status = _trace_source_status(evidence)
    condition_summary = str(
        metadata.get("condition_summary")
        or condition.get("condition_summary")
        or "Interpret only after checking the exact condition and source context."
    )
    return {
        "condition_key": evidence.condition_key,
        "condition_kind": evidence.condition_kind,
        "condition_title": evidence.condition_title,
        "trigger": {
            "kind": _trigger_kind(evidence.condition_kind),
            "chart_path": _chart_path_for_condition(evidence.condition_kind, evidence.condition_key),
        },
        "source": {
            "work_slug": source_anchor.get("work_slug") or passage.work.slug,
            "work_title": source_anchor.get("work_title") or passage.work.title,
            "source_url": source_anchor.get("source_url") or passage.work.source_url,
            "edition": source_anchor.get("edition") or "",
            "passage_id": passage.id,
            "catalog_passage_id": passage.id if source_anchor else None,
            "passage_reference": passage.reference,
            "reference": reference,
            "chapter": chapter,
            "verse": verse,
            "reference_status": evidence.reference_status,
            "review_status": evidence.review_status,
            "public_quote_policy": evidence.public_quote_policy,
            "source_anchor": source_anchor,
            "fragment": str(source_anchor.get("source_summary") or passage.body)[:900],
        },
        "interpretation_hint": str(source_anchor.get("interpretation_hint") or condition_summary),
        "source_status": source_status,
    }


def _trace_source_status(evidence: ShastraConditionEvidence) -> str:
    if _is_publicly_approved(evidence):
        return "approved"
    if evidence.reference_status.startswith("inferred"):
        return "inferred_needs_review"
    if evidence.reference_status.startswith("research_anchor"):
        return "research_anchor_needs_exact_source"
    if evidence.reference_status.startswith("category_topic_anchor"):
        return "curated_category_anchor_needs_rule_review"
    if evidence.reference_status.startswith("exact_") or evidence.reference_status.startswith("condition_equivalent"):
        return "curated_research_anchor"
    if (
        "topic_anchor" in evidence.reference_status
        or "name_mismatch" in evidence.reference_status
        or "protective_metaphor" in evidence.reference_status
        or "detector_review" in evidence.reference_status
    ):
        return "curated_research_anchor"
    return str(evidence.review_status or ReviewStatus.RESEARCH_ONLY)


def _trigger_kind(condition_kind: str) -> str:
    if condition_kind == "yoga_condition":
        return "yoga"
    if "avastha" in condition_kind:
        return "avastha"
    if condition_kind == "calculation_layer":
        return "calculation_layer"
    return "condition"


def _chart_path_for_condition(condition_kind: str, condition_key: str) -> str:
    if condition_kind == "yoga_condition":
        return f"classical.yogas.items[key={condition_key}]"
    if "avastha" in condition_key or "avastha" in condition_kind:
        return "classical.avasthas"
    if condition_key in {"shadbala", "ashtakavarga", "argala", "upagrahas", "special_points"}:
        return f"classical.{condition_key}"
    return f"condition_matrix.{condition_key}"


def _chapter_verse(reference: str) -> tuple[str, str]:
    chapter = _first_match(
        reference,
        [
            r"\bAdhyaya\s+([IVXLCDM]+|\d+)\b",
            r"\bChapter\s+([IVXLCDM]+|\d+)\b",
        ],
    )
    verse = _first_match(
        reference,
        [
            r"\bSloka\s+(\d+[A-Za-z]?)\b",
            r"\bStanza\s+(\d+[A-Za-z]?)\b",
            r"\bVerse\s+(\d+[A-Za-z]?)\b",
        ],
    )
    return chapter, verse


def _evidence_payload(evidence: ShastraConditionEvidence) -> dict[str, Any]:
    passage = evidence.passage
    metadata = evidence.metadata if isinstance(evidence.metadata, dict) else {}
    return {
        "id": evidence.id,
        "condition_key": evidence.condition_key,
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
        "approved_reference": metadata.get("approved_reference") or "",
        "approved_excerpt": metadata.get("approved_excerpt") or "",
        "reviewer": metadata.get("reviewer") or "",
        "source_anchor": metadata.get("source_anchor") or {},
        "source_anchors": metadata.get("source_anchors") or [],
        "snippet": passage.body[:1200],
        "matched_terms": evidence.metadata.get("matched_terms", []),
    }
