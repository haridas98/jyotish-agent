from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable

from django.core.management.base import BaseCommand, CommandError

from apps.reports.deepseek_generation import free_deepseek_chat_client
from apps.reports.qwen_generation import qwen_chat_completions_client
from apps.sources.models import SourcePassage, SourceWork

ProviderRunner = Callable[[str], str | dict[str, Any]]


class Command(BaseCommand):
    help = "Ask Qwen/Deepseek to review private OCR chunks without modifying source passages."

    def add_arguments(self, parser):
        parser.add_argument("--work-slug", required=True)
        parser.add_argument("--output", required=True)
        parser.add_argument("--providers", default="qwen,free_deepseek")
        parser.add_argument("--limit", type=int, default=1)
        parser.add_argument("--offset", type=int, default=0)
        parser.add_argument("--max-chars", type=int, default=3500)

    def handle(self, *args, **options):
        payload = review_private_corpus_ocr_with_ai(
            work_slug=str(options["work_slug"]),
            providers=_provider_keys(str(options["providers"])),
            limit=max(1, int(options["limit"])),
            offset=max(0, int(options["offset"])),
            max_chars=max(500, int(options["max_chars"])),
        )
        output = Path(options["output"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(json.dumps({"status": payload["status"], "summary": payload["summary"], "output": str(output)}, ensure_ascii=False))


def review_private_corpus_ocr_with_ai(
    *,
    work_slug: str,
    providers: list[str],
    limit: int,
    offset: int = 0,
    max_chars: int = 3500,
) -> dict[str, Any]:
    try:
        work = SourceWork.objects.get(slug=work_slug)
    except SourceWork.DoesNotExist as exc:
        raise CommandError(f"Source work not found: {work_slug}") from exc

    passages = _source_chunks(work, limit=limit, offset=offset)
    items = [_review_passage(work, passage, providers=providers, max_chars=max_chars) for passage in passages]
    failed = sum(1 for item in items if any(review["status"] == "failed" for review in item["reviews"]))
    return {
        "schema_version": "jyotish-private-corpus-ocr-ai-review-v1",
        "status": "ok" if failed == 0 else "partial",
        "work": {
            "slug": work.slug,
            "title": work.title,
            "language_code": work.language_code,
            "review_status": work.review_status,
        },
        "summary": {"selected": len(passages), "reviewed": len(items), "failed": failed},
        "items": items,
    }


def _source_chunks(work: SourceWork, *, limit: int, offset: int) -> list[SourcePassage]:
    source_chunks = [
        passage
        for passage in SourcePassage.objects.filter(work=work).order_by("reference", "id")
        if passage.metadata.get("import_kind") == "private_full_text_chunk"
    ]
    return source_chunks[offset : offset + limit]


def _review_passage(
    work: SourceWork,
    passage: SourcePassage,
    *,
    providers: list[str],
    max_chars: int,
) -> dict[str, Any]:
    text = passage.body[:max_chars]
    reviews = [_review_with_provider(provider, work, passage, text) for provider in providers]
    return {
        "passage_id": passage.id,
        "reference": passage.reference,
        "source_chars": len(passage.body),
        "reviewed_chars": len(text),
        "source_metadata": {
            "language_code": passage.language_code,
            "review_status": passage.review_status,
            "rights_status": passage.metadata.get("rights_status") or work.metadata.get("rights_status") or "",
        },
        "reviews": reviews,
        "cross_check": _cross_check(reviews),
    }


def _review_with_provider(provider: str, work: SourceWork, passage: SourcePassage, text: str) -> dict[str, Any]:
    prompt = _ocr_review_prompt(provider, work, passage, text)
    try:
        raw = _provider_runner(provider)(prompt)
        payload = _parse_provider_payload(raw)
        return {
            "status": "ok",
            "provider": provider,
            "normalized_text": str(payload.get("normalized_text") or ""),
            "detected_script": str(payload.get("detected_script") or ""),
            "ocr_issues": [str(item) for item in payload.get("ocr_issues", []) if str(item).strip()],
            "confidence": _float_or_none(payload.get("confidence")),
        }
    except Exception as exc:  # noqa: BLE001 - AI review should keep per-provider failures.
        return {"status": "failed", "provider": provider, "error": str(exc)}


def _ocr_review_prompt(provider: str, work: SourceWork, passage: SourcePassage, text: str) -> str:
    return (
        f"You are {provider}, an OCR reviewer inside jyotish-agent.\n"
        "Task: normalize the OCR text for private research only. Preserve meaning and order. Do not add missing doctrine.\n"
        "If text is unclear, keep the closest reading and mark the issue in ocr_issues. Do not translate unless the source already mixes languages.\n"
        "Return valid JSON only with keys: normalized_text, detected_script, ocr_issues, confidence.\n\n"
        f"Work: {work.title}\n"
        f"Reference: {passage.reference}\n"
        f"Language code: {passage.language_code}\n\n"
        "OCR TEXT:\n"
        "```text\n"
        f"{text}\n"
        "```"
    )


def _provider_runner(provider: str) -> ProviderRunner:
    if provider == "qwen":
        return qwen_chat_completions_client()
    if provider == "free_deepseek":
        return free_deepseek_chat_client()
    raise CommandError(f"Unknown OCR review provider: {provider}")


def _provider_keys(value: str) -> list[str]:
    providers = [item.strip() for item in value.split(",") if item.strip()]
    if not providers:
        raise CommandError("At least one provider is required")
    unknown = [provider for provider in providers if provider not in {"qwen", "free_deepseek"}]
    if unknown:
        raise CommandError(f"Unknown OCR review provider(s): {', '.join(unknown)}")
    return providers


def _parse_provider_payload(raw: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    text = str(raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.removeprefix("json").strip()
    return json.loads(text)


def _cross_check(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [review for review in reviews if review["status"] == "ok"]
    normalized = [str(review.get("normalized_text") or "") for review in successful]
    similarity = None
    if len(normalized) >= 2:
        similarity = round(SequenceMatcher(None, normalized[0], normalized[1]).ratio(), 4)
    return {
        "provider_count": len(reviews),
        "successful_count": len(successful),
        "both_succeeded": len(successful) == len(reviews) and len(reviews) >= 2,
        "first_two_similarity": similarity,
        "needs_human_review": len(successful) != len(reviews) or (similarity is not None and similarity < 0.92),
    }


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
