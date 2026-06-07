import json

import pytest
from django.core.management import call_command

from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


@pytest.mark.django_db
def test_review_private_corpus_ocr_with_ai_outputs_two_provider_reviews(tmp_path, monkeypatch):
    import apps.sources.management.commands.review_private_corpus_ocr_with_ai as command_module

    work = SourceWork.objects.create(
        slug="ocr-review-work",
        title="OCR Review Work",
        source_class=SourceWork.SourceClass.RESEARCH_ONLY,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=work,
        reference="private full text chunk 0001",
        body="Lagna   is  strong when OCR breaks words li ke this.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "private_full_text_chunk"},
    )
    output = tmp_path / "ocr-review.json"

    def fake_runner(provider):
        return lambda prompt: json.dumps(
            {
                "normalized_text": f"{provider}: Lagna is strong when OCR breaks words like this.",
                "detected_script": "latin",
                "ocr_issues": ["broken spacing"],
                "confidence": 0.9,
            }
        )

    monkeypatch.setattr(command_module, "_provider_runner", fake_runner)

    call_command(
        "review_private_corpus_ocr_with_ai",
        "--work-slug",
        "ocr-review-work",
        "--providers",
        "qwen,free_deepseek",
        "--output",
        str(output),
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"] == {"selected": 1, "reviewed": 1, "failed": 0}
    item = payload["items"][0]
    assert item["reference"] == "private full text chunk 0001"
    assert [review["provider"] for review in item["reviews"]] == ["qwen", "free_deepseek"]
    assert item["cross_check"]["provider_count"] == 2
    assert item["cross_check"]["both_succeeded"] is True


@pytest.mark.django_db
def test_review_private_corpus_ocr_with_ai_does_not_modify_source_passage(tmp_path, monkeypatch):
    import apps.sources.management.commands.review_private_corpus_ocr_with_ai as command_module

    work = SourceWork.objects.create(
        slug="ocr-review-source-preserved",
        title="OCR Review Source Preserved",
        source_class=SourceWork.SourceClass.RESEARCH_ONLY,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="private full text chunk 0001",
        body="Original OCR text.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "private_full_text_chunk"},
    )

    monkeypatch.setattr(
        command_module,
        "_provider_runner",
        lambda provider: lambda prompt: json.dumps(
            {"normalized_text": "Corrected text.", "ocr_issues": [], "confidence": 1.0}
        ),
    )

    call_command(
        "review_private_corpus_ocr_with_ai",
        "--work-slug",
        "ocr-review-source-preserved",
        "--providers",
        "qwen",
        "--output",
        str(tmp_path / "review.json"),
    )

    passage.refresh_from_db()
    assert passage.body == "Original OCR text."


@pytest.mark.django_db
def test_review_private_corpus_ocr_with_ai_adds_internet_witness_context(tmp_path, monkeypatch):
    import apps.sources.management.commands.review_private_corpus_ocr_with_ai as command_module

    work = SourceWork.objects.create(
        slug="bphs-witness-review",
        title="Brihat Parashara Hora Shastra",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=work,
        reference="private full text chunk 0001",
        body="Chapter 1. The Creation\nOCR line with bad Sanskrit.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "private_full_text_chunk"},
    )
    witness_root = tmp_path / "witnesses"
    sanskrit_dir = witness_root / "sanskritdocuments" / "bphs"
    parashara_dir = witness_root / "parashara_net"
    sanskrit_dir.mkdir(parents=True)
    parashara_dir.mkdir(parents=True)
    (sanskrit_dir / "par0110.itx").write_text(
        "\\section{sR^iShTikramakathanAdhyAyaH || 1||}\n"
        "athaikadA munishreShThaM trikalaj~naM parAsharam |\n"
        "\\section{athAvatArakathanAdhyAyaH || 2||}\n"
        "chapter two text",
        encoding="utf-8",
    )
    (parashara_dir / "chapter01.html").write_text(
        "<html><body><h2>Chapter 1</h2><p>Internet witness chapter one.</p></body></html>",
        encoding="utf-8",
    )
    prompts = []

    def fake_runner(provider):
        def run(prompt):
            prompts.append(prompt)
            return json.dumps(
                {
                    "normalized_text": "normalized",
                    "detected_script": "mixed",
                    "ocr_issues": [],
                    "confidence": 0.8,
                    "witness_usage": "used chapter 1 witness",
                }
            )

        return run

    monkeypatch.setattr(command_module, "_provider_runner", fake_runner)
    output = tmp_path / "review.json"

    call_command(
        "review_private_corpus_ocr_with_ai",
        "--work-slug",
        "bphs-witness-review",
        "--providers",
        "qwen",
        "--witness-root",
        str(witness_root),
        "--output",
        str(output),
    )

    assert "INTERNET WITNESS CONTEXT" in prompts[0]
    assert "athaikadA munishreShThaM" in prompts[0]
    assert "Internet witness chapter one" in prompts[0]
    payload = json.loads(output.read_text(encoding="utf-8"))
    item = payload["items"][0]
    assert item["internet_witness"]["chapters"] == [1]
    assert item["reviews"][0]["witness_usage"] == "used chapter 1 witness"
