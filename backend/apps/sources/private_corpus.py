from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.db import transaction

from .models import ReviewStatus, SourcePassage, SourceWork

DEFAULT_CHUNK_CHARS = 8000
SUPPORTED_PRIVATE_CORPUS_SUFFIXES = {".txt", ".md", ".itx"}


@transaction.atomic
def import_private_corpus_manifest(manifest_path: Path, chunk_chars: int = DEFAULT_CHUNK_CHARS) -> dict[str, int]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    works = _list(manifest, "works")
    imported_passages = 0
    for item in works:
        imported_passages += _import_work(item, base_dir=manifest_path.parent, chunk_chars=chunk_chars)
    return {"works": len(works), "passages": imported_passages}


def _import_work(item: dict[str, Any], base_dir: Path, chunk_chars: int) -> int:
    local_path = _local_path(item, base_dir)
    text = _normalize_text(local_path.read_text(encoding=str(item.get("encoding") or "utf-8")))
    slug = _required_str(item, "slug")
    rights_status = str(item.get("rights_status") or "private_research_only_until_approved")
    work, _created = SourceWork.objects.update_or_create(
        slug=slug,
        defaults={
            "title": _required_str(item, "title"),
            "source_class": _choice(item.get("source_class", SourceWork.SourceClass.JYOTISH_SHASTRA), SourceWork.SourceClass.values),
            "author": str(item.get("author") or ""),
            "edition": str(item.get("edition") or ""),
            "language_code": str(item.get("language_code") or "en"),
            "source_url": str(item.get("source_url") or ""),
            "review_status": ReviewStatus.RESEARCH_ONLY,
            "metadata": {
                **(item.get("metadata") if isinstance(item.get("metadata"), dict) else {}),
                "import_kind": "private_full_text",
                "rights_status": rights_status,
                "public_quote_policy": "blocked_until_approved",
                "local_path": str(local_path),
            },
        },
    )
    chunks = _chunk_text(text, max_chars=max(500, chunk_chars))
    for index, chunk in enumerate(chunks, start=1):
        SourcePassage.objects.update_or_create(
            work=work,
            reference=f"private full text chunk {index:04d}",
            language_code=work.language_code,
            defaults={
                "body": chunk,
                "review_status": ReviewStatus.RESEARCH_ONLY,
                "metadata": {
                    "import_kind": "private_full_text_chunk",
                    "chunk_index": index,
                    "chunk_count": len(chunks),
                    "rights_status": rights_status,
                    "public_quote_policy": "blocked_until_approved",
                },
            },
        )
    return len(chunks)


def _local_path(item: dict[str, Any], base_dir: Path) -> Path:
    raw_path = Path(_required_str(item, "local_path"))
    path = raw_path if raw_path.is_absolute() else base_dir / raw_path
    if not path.exists():
        raise FileNotFoundError(f"Private corpus file does not exist: {path}")
    if path.suffix.lower() not in SUPPORTED_PRIVATE_CORPUS_SUFFIXES:
        raise ValueError("Private corpus importer currently supports .txt, .md and .itx files")
    return path


def _chunk_text(text: str, max_chars: int) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_hard_chunks(paragraph, max_chars))
            continue
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = paragraph
    if current:
        chunks.append(current)
    return chunks or [text.strip()]


def _hard_chunks(text: str, max_chars: int) -> list[str]:
    return [text[index : index + max_chars].strip() for index in range(0, len(text), max_chars) if text[index : index + max_chars].strip()]


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


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
