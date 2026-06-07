from __future__ import annotations

from pathlib import Path
from typing import Any

import fitz

VISUAL_KEYWORDS = (
    "ashtakavarga",
    "ayana bala",
    "bala",
    "bhava",
    "chart",
    "chakra",
    "dasha",
    "diagram",
    "figure",
    "graph",
    "house",
    "rasi",
    "shadbala",
    "table",
    "varga",
    "vimshottari",
    "yoga",
)


def inventory_pdf_visuals(
    *,
    pdf_path: Path,
    output_dir: Path | None = None,
    render_top: int = 0,
    dpi: int = 144,
    max_text_chars: int = 600,
    top_limit: int = 30,
) -> dict[str, Any]:
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir) if output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    with fitz.open(pdf_path) as document:
        pages = [_page_payload(page, max_text_chars=max_text_chars) for page in document]
        top_pages = sorted(pages, key=lambda item: (-item["visual_score"], item["page_number"]))[
            : max(1, top_limit)
        ]
        rendered = _render_top_pages(
            document=document,
            top_pages=top_pages,
            output_dir=output_dir,
            render_top=max(0, render_top),
            dpi=max(36, dpi),
        )

    return {
        "schema_version": "jyotish-pdf-visual-inventory-v1",
        "pdf_path": str(pdf_path),
        "page_count": len(pages),
        "summary": {
            "image_pages_count": sum(1 for page in pages if page["image_count"] > 0),
            "drawing_pages_count": sum(1 for page in pages if page["drawing_count"] > 0),
            "rendered_pages": rendered,
        },
        "image_pages": [
            page["page_number"] for page in pages if page["image_count"] > 0
        ],
        "drawing_pages": [
            page["page_number"] for page in pages if page["drawing_count"] > 0
        ],
        "top_pages": top_pages,
    }


def _page_payload(page: fitz.Page, *, max_text_chars: int) -> dict[str, Any]:
    text = page.get_text("text") or ""
    drawings = page.get_drawings()
    line_count = _line_like_count(drawings)
    keyword_hits = _keyword_hits(text)
    image_count = len(page.get_images(full=True))
    drawing_count = len(drawings)
    text_blocks = len(page.get_text("blocks") or [])
    score = (
        image_count * 80
        + drawing_count * 3
        + line_count * 8
        + len(keyword_hits) * 18
        + min(text_blocks, 30)
    )
    return {
        "page_number": page.number + 1,
        "image_count": image_count,
        "drawing_count": drawing_count,
        "line_like_count": line_count,
        "text_block_count": text_blocks,
        "keyword_hits": keyword_hits,
        "visual_score": score,
        "text_sample": _compact_sample(text, max_text_chars=max_text_chars),
    }


def _line_like_count(drawings: list[dict[str, Any]]) -> int:
    count = 0
    for drawing in drawings:
        for item in drawing.get("items", []):
            operator = item[0] if item else ""
            if operator == "l":
                count += 1
            elif operator == "re":
                count += 4
            elif operator in {"c", "qu"}:
                count += 1
    return count


def _keyword_hits(text: str) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in VISUAL_KEYWORDS if keyword in lowered]


def _compact_sample(text: str, *, max_text_chars: int) -> str:
    sample = " ".join(text.split())
    return sample[: max(0, max_text_chars)]


def _render_top_pages(
    *,
    document: fitz.Document,
    top_pages: list[dict[str, Any]],
    output_dir: Path | None,
    render_top: int,
    dpi: int,
) -> int:
    if output_dir is None or render_top <= 0:
        return 0
    scale = dpi / 72
    matrix = fitz.Matrix(scale, scale)
    rendered = 0
    for page_payload in top_pages[:render_top]:
        page_number = int(page_payload["page_number"])
        path = output_dir / f"page-{page_number:04d}.png"
        pixmap = document[page_number - 1].get_pixmap(matrix=matrix, alpha=False)
        pixmap.save(path)
        page_payload["rendered_path"] = str(path)
        rendered += 1
    return rendered
