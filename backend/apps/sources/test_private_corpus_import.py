import json

import pytest
from django.core.management import call_command

from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


@pytest.mark.django_db
def test_import_private_corpus_chunks_local_books_as_research_only(tmp_path):
    text_path = tmp_path / "phaladipika.txt"
    text_path.write_text("Chapter 1\n" + ("A private research paragraph.\n" * 80), encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "works": [
                    {
                        "slug": "phaladipika-private-test",
                        "title": "Phaladipika private test",
                        "author": "Mantreswara",
                        "edition": "V. Subrahmanya Sastri test OCR",
                        "language_code": "en",
                        "source_url": "https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation",
                        "local_path": str(text_path),
                        "rights_status": "private_research_only_until_approved",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    call_command("import_private_corpus", str(manifest_path), "--chunk-chars", "500")
    call_command("import_private_corpus", str(manifest_path), "--chunk-chars", "500")

    work = SourceWork.objects.get(slug="phaladipika-private-test")
    assert work.review_status == ReviewStatus.RESEARCH_ONLY
    assert work.metadata["import_kind"] == "private_full_text"
    assert work.metadata["rights_status"] == "private_research_only_until_approved"
    assert work.metadata["public_quote_policy"] == "blocked_until_approved"

    passages = SourcePassage.objects.filter(work=work).order_by("reference")
    assert passages.count() > 1
    assert all(passage.review_status == ReviewStatus.RESEARCH_ONLY for passage in passages)
    assert all(passage.metadata["import_kind"] == "private_full_text_chunk" for passage in passages)
