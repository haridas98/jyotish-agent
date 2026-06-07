from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from html import unescape
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
        parser.add_argument("--passage-kind", default="private_full_text_chunk")
        parser.add_argument("--witness-root", default="")
        parser.add_argument("--max-witness-chars", type=int, default=3500)
        parser.add_argument("--provider-workers", type=int, default=1)

    def handle(self, *args, **options):
        payload = review_private_corpus_ocr_with_ai(
            work_slug=str(options["work_slug"]),
            providers=_provider_keys(str(options["providers"])),
            limit=max(1, int(options["limit"])),
            offset=max(0, int(options["offset"])),
            max_chars=max(500, int(options["max_chars"])),
            passage_kind=str(options["passage_kind"]),
            witness_root=Path(options["witness_root"]) if str(options["witness_root"]).strip() else None,
            max_witness_chars=max(500, int(options["max_witness_chars"])),
            provider_workers=max(1, int(options["provider_workers"])),
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
    passage_kind: str = "private_full_text_chunk",
    witness_root: Path | None = None,
    max_witness_chars: int = 3500,
    provider_workers: int = 1,
) -> dict[str, Any]:
    try:
        work = SourceWork.objects.get(slug=work_slug)
    except SourceWork.DoesNotExist as exc:
        raise CommandError(f"Source work not found: {work_slug}") from exc

    chunks = _source_chunks(work, passage_kind=passage_kind)
    passages = chunks[offset : offset + limit]
    witness_contexts = _witness_contexts(
        chunks=chunks,
        offset=offset,
        count=len(passages),
        witness_root=witness_root,
        max_witness_chars=max_witness_chars,
    )
    items = [
        _review_passage(
            work,
            passage,
            providers=providers,
            max_chars=max_chars,
            witness_context=witness_contexts[index],
            provider_workers=provider_workers,
        )
        for index, passage in enumerate(passages)
    ]
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


def _source_chunks(work: SourceWork, *, passage_kind: str) -> list[SourcePassage]:
    return [
        passage
        for passage in SourcePassage.objects.filter(work=work).order_by("reference", "id")
        if passage.metadata.get("import_kind") == passage_kind
    ]


def _review_passage(
    work: SourceWork,
    passage: SourcePassage,
    *,
    providers: list[str],
    max_chars: int,
    witness_context: dict[str, Any],
    provider_workers: int,
) -> dict[str, Any]:
    text = passage.body[:max_chars]
    with ThreadPoolExecutor(max_workers=max(1, min(len(providers), provider_workers))) as executor:
        reviews = list(
            executor.map(
                lambda provider: _review_with_provider(
                    provider,
                    work,
                    passage,
                    text,
                    witness_context=witness_context,
                ),
                providers,
            )
        )
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
        "internet_witness": {
            "chapters": witness_context.get("chapters", []),
            "sources": witness_context.get("sources", []),
        },
        "reviews": reviews,
        "cross_check": _cross_check(reviews),
    }


def _review_with_provider(
    provider: str,
    work: SourceWork,
    passage: SourcePassage,
    text: str,
    *,
    witness_context: dict[str, Any],
) -> dict[str, Any]:
    prompt = _ocr_review_prompt(provider, work, passage, text, witness_context=witness_context)
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
            "witness_usage": str(payload.get("witness_usage") or ""),
        }
    except Exception as exc:  # noqa: BLE001 - AI review should keep per-provider failures.
        return {"status": "failed", "provider": provider, "error": str(exc)}


def _ocr_review_prompt(
    provider: str,
    work: SourceWork,
    passage: SourcePassage,
    text: str,
    *,
    witness_context: dict[str, Any],
) -> str:
    witness_text = str(witness_context.get("text") or "").strip()
    witness_block = ""
    if witness_text:
        witness_block = (
            "\nINTERNET WITNESS CONTEXT:\n"
            "Use this only when a line clearly matches the OCR text. If a Sanskrit shloka matches, prefer the witness reading for that shloka and note it in witness_usage.\n"
            "Do not import unrelated witness text into normalized_text.\n"
            "```text\n"
            f"{witness_text}\n"
            "```\n"
        )
    return (
        f"You are {provider}, an OCR reviewer inside jyotish-agent.\n"
        "Task: normalize the OCR text for private research only. Preserve meaning and order. Do not add missing doctrine.\n"
        "If text is unclear, keep the closest reading and mark the issue in ocr_issues. Do not translate unless the source already mixes languages.\n"
        "Return valid JSON only with keys: normalized_text, detected_script, ocr_issues, confidence, witness_usage.\n\n"
        f"Work: {work.title}\n"
        f"Reference: {passage.reference}\n"
        f"Language code: {passage.language_code}\n\n"
        "OCR TEXT:\n"
        "```text\n"
        f"{text}\n"
        "```\n"
        f"{witness_block}"
    )


def _witness_contexts(
    *,
    chunks: list[SourcePassage],
    offset: int,
    count: int,
    witness_root: Path | None,
    max_witness_chars: int,
) -> list[dict[str, Any]]:
    if not witness_root:
        return [_empty_witness_context() for _ in range(count)]
    index = _BphsWitnessIndex(witness_root)
    contexts: list[dict[str, Any]] = []
    current_chapter: int | None = None
    end = offset + count
    for position, chunk in enumerate(chunks[:end]):
        found = _chapters_in_text(chunk.body)
        if found:
            current_chapter = found[-1]
        if position >= offset:
            chapters = found or ([current_chapter] if current_chapter else [])
            contexts.append(index.context_for(chapters, max_chars=max_witness_chars))
    return contexts


def _empty_witness_context() -> dict[str, Any]:
    return {"chapters": [], "sources": [], "text": ""}


def _chapters_in_text(text: str) -> list[int]:
    chapters: list[int] = []
    for match in re.finditer(r"(?im)^\s*Chapter\s+(\d+)\b", text):
        chapter = int(match.group(1))
        if 1 <= chapter <= 120 and chapter not in chapters:
            chapters.append(chapter)
    return chapters


class _BphsWitnessIndex:
    def __init__(self, root: Path):
        self.root = root
        self.sanskrit_by_chapter = self._load_sanskritdocuments()
        self.parashara_net_by_chapter = self._load_parashara_net()

    def context_for(self, chapters: list[int], *, max_chars: int) -> dict[str, Any]:
        normalized = [chapter for chapter in chapters if chapter > 0]
        if not normalized:
            return _empty_witness_context()
        sections: list[str] = []
        sources: list[str] = []
        per_source_chars = max(300, max_chars // max(1, len(normalized) * 2))
        for chapter in normalized:
            sanskrit = self.sanskrit_by_chapter.get(chapter, "")
            if sanskrit:
                sections.append(f"[SanskritDocuments BPHS chapter {chapter}]\n{_trim(sanskrit, per_source_chars)}")
                sources.append(f"https://sanskritdocuments.org/doc_z_misc_sociology_astrology/{_sanskrit_file_for_chapter(chapter)}")
            parashara = self.parashara_net_by_chapter.get(chapter, "")
            if parashara:
                sections.append(f"[parashara.net BPHS chapter {chapter}]\n{_trim(parashara, per_source_chars)}")
                sources.append(f"https://parashara.net/index.php?page=chapter{chapter}")
        return {"chapters": normalized, "sources": sorted(set(sources)), "text": "\n\n".join(sections)}

    def _load_sanskritdocuments(self) -> dict[int, str]:
        base = self.root / "sanskritdocuments" / "bphs"
        if not base.exists():
            base = self.root
        chapters: dict[int, str] = {}
        for path in sorted(base.glob("par*.itx")):
            text = path.read_text(encoding="utf-8", errors="replace")
            chapters.update(_split_sanskritdocuments_chapters(text))
        return chapters

    def _load_parashara_net(self) -> dict[int, str]:
        base = self.root / "parashara_net"
        if not base.exists():
            return {}
        chapters: dict[int, str] = {}
        for path in sorted(base.glob("chapter*.html")):
            match = re.search(r"chapter(\d+)\.html$", path.name)
            if not match:
                continue
            chapters[int(match.group(1))] = _html_to_text(path.read_text(encoding="utf-8", errors="replace"))
        return chapters


def _split_sanskritdocuments_chapters(text: str) -> dict[int, str]:
    matches = list(re.finditer(r"\\section\{[^{}]*\|\|\s*(\d+)\s*\|\|\}", text))
    chapters: dict[int, str] = {}
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chapters[int(match.group(1))] = text[start:end].strip()
    return chapters


def _html_to_text(text: str) -> str:
    text = re.sub(r"(?is)<script\b.*?</script>", " ", text)
    text = re.sub(r"(?is)<style\b.*?</style>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p|</h[1-6]|</div|</li", "\n<", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    return text.strip()


def _sanskrit_file_for_chapter(chapter: int) -> str:
    ranges = [
        (1, 10, "par0110.itx"),
        (11, 20, "par1120.itx"),
        (21, 30, "par2130.itx"),
        (31, 40, "par3140.itx"),
        (41, 45, "par4145.itx"),
        (46, 50, "par4650.itx"),
        (51, 60, "par5160.itx"),
        (61, 70, "par6170.itx"),
        (71, 80, "par7180.itx"),
        (81, 90, "par8190.itx"),
        (91, 97, "par9197.itx"),
    ]
    for start, end, filename in ranges:
        if start <= chapter <= end:
            return filename
    return "par0110.itx"


def _trim(text: str, max_chars: int) -> str:
    text = text.strip()
    return text if len(text) <= max_chars else f"{text[:max_chars].rstrip()}\n...[trimmed]"


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
