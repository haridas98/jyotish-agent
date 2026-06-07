import json

import fitz
from django.core.management import call_command

from apps.sources.pdf_visual_inventory import inventory_pdf_visuals


def _sample_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Chapter 1. Plain prose without visual layout.")

    table_page = doc.new_page()
    table_page.insert_text((72, 72), "Table: Ashtakavarga chart values")
    left, top, cell = 72, 100, 42
    for index in range(4):
        x = left + index * cell
        y = top + index * cell
        table_page.draw_line((x, top), (x, top + 3 * cell))
        table_page.draw_line((left, y), (left + 3 * cell, y))

    doc.save(path)
    doc.close()


def test_inventory_pdf_visuals_scores_and_renders_table_page(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    output_dir = tmp_path / "visuals"
    _sample_pdf(pdf_path)

    payload = inventory_pdf_visuals(
        pdf_path=pdf_path,
        output_dir=output_dir,
        render_top=1,
        dpi=72,
    )

    assert payload["schema_version"] == "jyotish-pdf-visual-inventory-v1"
    assert payload["page_count"] == 2
    assert payload["top_pages"][0]["page_number"] == 2
    assert "table" in payload["top_pages"][0]["keyword_hits"]
    assert (output_dir / "page-0002.png").exists()


def test_inventory_pdf_visuals_command_writes_manifest(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    output_dir = tmp_path / "visuals"
    manifest_path = tmp_path / "manifest.json"
    _sample_pdf(pdf_path)

    call_command(
        "inventory_pdf_visuals",
        "--pdf",
        str(pdf_path),
        "--output-dir",
        str(output_dir),
        "--json-output",
        str(manifest_path),
        "--render-top",
        "0",
    )

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["page_count"] == 2
    assert payload["top_pages"][0]["page_number"] == 2
    assert payload["summary"]["rendered_pages"] == 0
