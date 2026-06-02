import json

import pytest
from django.core.management import call_command

from apps.sources.models import ReviewStatus, SourcePassage, SourceWork
from apps.sources.segmentation import segment_private_work


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


@pytest.mark.django_db
def test_import_private_corpus_accepts_itrans_itx_files(tmp_path):
    text_path = tmp_path / "phaladipika.itx"
    text_path.write_text(
        "% Text title : phaladIpikA\n\\engtitle{.. phaladIpikA ..}\nrAshi bheda shuklAmbaradharaM devam\n",
        encoding="utf-8",
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "works": [
                    {
                        "slug": "phaladipika-sanskrit-itx-test",
                        "title": "Phaladipika Sanskrit ITX test",
                        "author": "Mantreswara",
                        "edition": "SanskritDocuments ITRANS test",
                        "language_code": "sa-ITRANS",
                        "source_url": "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/phaladIpika.itx",
                        "local_path": str(text_path),
                        "rights_status": "personal_study_research_only",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    call_command("import_private_corpus", str(manifest_path), "--chunk-chars", "500")

    work = SourceWork.objects.get(slug="phaladipika-sanskrit-itx-test")
    passage = SourcePassage.objects.get(work=work)
    assert work.language_code == "sa-ITRANS"
    assert passage.body.startswith("% Text title : phaladIpikA")
    assert passage.metadata["rights_status"] == "personal_study_research_only"


@pytest.mark.django_db
def test_import_private_corpus_accepts_utf8_sig_manifest(tmp_path):
    text_path = tmp_path / "brihajjataka.itx"
    text_path.write_text("% Text title : bRihajjAtakam\nlagna yoga\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "works": [
                    {
                        "slug": "brhat-jataka-sanskrit-bom-test",
                        "title": "Brhat Jataka Sanskrit BOM test",
                        "language_code": "sa-ITRANS",
                        "local_path": str(text_path),
                    }
                ]
            }
        ),
        encoding="utf-8-sig",
    )

    call_command("import_private_corpus", str(manifest_path))

    assert SourceWork.objects.filter(slug="brhat-jataka-sanskrit-bom-test").exists()


@pytest.mark.django_db
def test_segment_private_work_creates_review_only_candidate_passages():
    work = SourceWork.objects.create(
        slug="brhat-jataka-private-test",
        title="Brhat Jataka private test",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=work,
        reference="private full text chunk 0001",
        body=(
            "--- page 1 ---\n"
            "Sloka 1. Lagna source condition for yoga testing.\n\n"
            "Sloka 2. Chandra source condition for dasha testing.\n\n"
            "--- page 2 ---\n"
            "Stanza 3. Shani source condition for strength testing."
        ),
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "private_full_text_chunk"},
    )

    counts = segment_private_work(work.slug, max_chars=70)
    segment_private_work(work.slug, max_chars=70)

    candidates = SourcePassage.objects.filter(
        work=work,
        metadata__import_kind="candidate_shastra_passage",
    ).order_by("reference")
    assert counts["candidate_passages"] >= 3
    assert candidates.count() == counts["candidate_passages"]
    assert candidates[0].review_status == ReviewStatus.RESEARCH_ONLY
    assert candidates[0].metadata["exact_reference_status"] == "needs_review"
    assert candidates[0].metadata["public_quote_policy"] == "blocked_until_approved"
    assert candidates[0].metadata["source_reference"] == "private full text chunk 0001"
