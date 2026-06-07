from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from indic_transliteration import sanscript


@dataclass(frozen=True)
class SanskritChapter:
    chapter: int
    source_file: str
    title_itrans: str
    body_itrans: str
    title_devanagari: str
    body_devanagari: str


def assemble_bphs_with_sanskrit(
    *,
    english_path: Path,
    sanskrit_root: Path,
    output_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    english = english_path.read_text(encoding="utf-8")
    chapters = load_bphs_sanskrit_chapters(sanskrit_root)
    merged, inserted = merge_sanskrit_into_english(english, chapters)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(merged, encoding="utf-8")
    payload = {
        "schema_version": "jyotish-bphs-sanskrit-merged-v1",
        "status": "complete" if len(inserted) == len(chapters) else "partial",
        "english_source": str(english_path),
        "sanskrit_root": str(sanskrit_root),
        "output": str(output_path),
        "chapters_loaded": len(chapters),
        "chapters_inserted": len(inserted),
        "missing_insertions": [chapter for chapter in sorted(chapters) if chapter not in inserted],
        "generated_at": datetime.now(UTC).isoformat(),
    }
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_bphs_sanskrit_chapters(root: Path) -> dict[int, SanskritChapter]:
    base = root / "sanskritdocuments" / "bphs"
    if not base.exists():
        base = root
    chapters: dict[int, SanskritChapter] = {}
    for path in sorted(base.glob("par*.itx")):
        chapters.update(_split_itx_file(path))
    return chapters


def merge_sanskrit_into_english(
    english: str,
    chapters: dict[int, SanskritChapter],
) -> tuple[str, set[int]]:
    lines = english.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    output: list[str] = []
    inserted: set[int] = set()
    for line in lines:
        chapter = _chapter_heading(line)
        if chapter and chapter in chapters and chapter not in inserted:
            output.extend(_sanskrit_block(chapters[chapter]))
            inserted.add(chapter)
        output.append(line)
    return "\n".join(output).strip() + "\n", inserted


def _split_itx_file(path: Path) -> dict[int, SanskritChapter]:
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = _chapter_markers(text)
    chapters: dict[int, SanskritChapter] = {}
    for index, match in enumerate(matches):
        chapter = int(match["chapter"])
        start = int(match["body_start"])
        end = int(matches[index + 1]["start"]) if index + 1 < len(matches) else len(text)
        title = _clean_itrans(str(match["title"]))
        body = _clean_itrans(text[start:end])
        chapters[chapter] = SanskritChapter(
            chapter=chapter,
            source_file=path.name,
            title_itrans=title,
            body_itrans=body,
            title_devanagari=_to_devanagari(title),
            body_devanagari=_to_devanagari(body),
        )
    return chapters


def _chapter_markers(text: str) -> list[dict[str, int | str]]:
    markers: list[dict[str, int | str]] = []
    for match in re.finditer(r"\\section\{(?P<title>[^{}]*\|\|\s*(?P<chapter>\d+)\s*\|\|)\}", text):
        markers.append(
            {
                "start": match.start(),
                "body_start": match.end(),
                "title": match.group("title"),
                "chapter": int(match.group("chapter")),
            }
        )
    plain_title = re.compile(
        r"(?im)^\s*(?P<title>(?:atha\s+)?[^\n|\\]*(?:adhyAya|AdhyAya|adyAya|AdyAya)[Hh]?[^\n|]*\|\|\s*(?P<chapter>\d+)\s*\|\|)\s*$"
    )
    for match in plain_title.finditer(text):
        markers.append(
            {
                "start": match.start(),
                "body_start": match.end(),
                "title": match.group("title"),
                "chapter": int(match.group("chapter")),
            }
        )
    return sorted(markers, key=lambda item: int(item["start"]))


def _clean_itrans(text: str) -> str:
    text = re.sub(r"(?m)^%.*$", "", text)
    text = re.sub(r"\\(?:begin|end)\{[^{}]+\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+(?:\[[^\]]+\])?(?:\{[^{}]*\})?", "", text)
    text = text.replace("##", "")
    text = text.replace("\\_", "_")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _to_devanagari(text: str) -> str:
    return sanscript.transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)


def _chapter_heading(line: str) -> int | None:
    match = re.match(r"^\s*Chapter\s+(\d+)(?:[\.:]\s+\S+|\s*$)", line)
    if not match:
        return None
    chapter = int(match.group(1))
    return chapter if 1 <= chapter <= 120 else None


def _sanskrit_block(chapter: SanskritChapter) -> list[str]:
    return [
        "",
        f"=== Sanskrit Witness Chapter {chapter.chapter} ===",
        f"Source: SanskritDocuments {chapter.source_file}",
        "",
        "[Devanagari]",
        chapter.title_devanagari,
        "",
        chapter.body_devanagari,
        "",
        "[ITRANS]",
        chapter.title_itrans,
        "",
        chapter.body_itrans,
        "",
        f"=== English Translation / Notes Chapter {chapter.chapter} ===",
        "",
    ]
