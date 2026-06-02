import pytest
from rest_framework.test import APIClient

from apps.sources.citations import (
    combined_citation_search,
    local_approved_citation_search,
    local_research_corpus_search,
)
from apps.sources.coverage import source_coverage_matrix
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork, VLCitationLink


@pytest.mark.django_db
def test_local_approved_citation_search_falls_back_to_prabhupada_anchors():
    work = SourceWork.objects.create(
        slug="bhagavad-gita-as-it-is",
        title="Bhagavad-gita As It Is",
        source_class=SourceWork.SourceClass.CANONICAL_PRABHUPADA,
        review_status=ReviewStatus.APPROVED,
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="Bhagavad-gita 9.22",
        body="Krishna protects His devotee.",
        review_status=ReviewStatus.APPROVED,
    )
    VLCitationLink.objects.create(
        passage=passage,
        public_url="http://127.0.0.1:3100/bhagavad-gita/9/22",
    )

    results = local_approved_citation_search("Hare Krishna maha mantra", limit=1)

    assert results[0]["title"] == "Bhagavad-gita 9.22"
    assert results[0]["public_url"].endswith("/bhagavad-gita/9/22")


@pytest.mark.django_db
def test_combined_citation_search_uses_local_fallback_when_vl_is_empty():
    work = SourceWork.objects.create(
        slug="srimad-bhagavatam-prabhupada",
        title="Srimad-Bhagavatam",
        source_class=SourceWork.SourceClass.CANONICAL_PRABHUPADA,
        review_status=ReviewStatus.APPROVED,
    )
    SourcePassage.objects.create(
        work=work,
        reference="Srimad-Bhagavatam 1.2.6",
        body="Pure devotional service is supreme dharma.",
        review_status=ReviewStatus.APPROVED,
    )

    results = combined_citation_search("", "Krishna shelter", limit=1)

    assert results[0]["title"] == "Srimad-Bhagavatam 1.2.6"


@pytest.mark.django_db
def test_local_research_corpus_search_returns_private_chunks_without_public_citation_flag():
    work = SourceWork.objects.create(
        slug="phaladipika-private",
        title="Phaladipika",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"rights_status": "private_research_only_until_approved"},
    )
    SourcePassage.objects.create(
        work=work,
        reference="private full text chunk 0001",
        body="Gaja Kesari yoga research note from a private OCR chunk.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={
            "import_kind": "private_full_text_chunk",
            "public_quote_policy": "blocked_until_approved",
        },
    )

    results = local_research_corpus_search("Gaja Kesari", limit=2)

    assert results[0]["work_title"] == "Phaladipika"
    assert results[0]["review_status"] == ReviewStatus.RESEARCH_ONLY
    assert results[0]["is_public_citation"] is False
    assert results[0]["public_quote_policy"] == "blocked_until_approved"


@pytest.mark.django_db
def test_local_research_corpus_search_prioritizes_private_full_text_over_catalog():
    private_work = SourceWork.objects.create(
        slug="brhat-jataka-private",
        title="Brhat Jataka",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    catalog_work = SourceWork.objects.create(
        slug="yoga-catalog",
        title="Classical Yoga Research Catalog",
        source_class=SourceWork.SourceClass.RESEARCH_ONLY,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=catalog_work,
        reference="Yoga catalog: Gaja Kesari",
        body="Gaja Kesari yoga catalog anchor.",
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=private_work,
        reference="private full text chunk 0007",
        body="Gaja Kesari yoga full text source area.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "private_full_text_chunk"},
    )

    results = local_research_corpus_search("Gaja Kesari", limit=2)

    assert results[0]["work_title"] == "Brhat Jataka"


@pytest.mark.django_db
def test_research_search_api_returns_private_corpus_results():
    work = SourceWork.objects.create(
        slug="brhat-jataka-private",
        title="Brhat Jataka",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=work,
        reference="private full text chunk 0001",
        body="Lagna lord and yoga material for internal review.",
        review_status=ReviewStatus.RESEARCH_ONLY,
    )

    response = APIClient().get("/api/sources/research/search", {"q": "lagna yoga"})

    assert response.status_code == 200
    assert response.json()["items"][0]["work_title"] == "Brhat Jataka"


@pytest.mark.django_db
def test_research_search_api_rejects_invalid_limit():
    response = APIClient().get("/api/sources/research/search", {"q": "lagna", "limit": "many"})

    assert response.status_code == 400


@pytest.mark.django_db
def test_source_coverage_matrix_counts_private_chunks_and_missing_sources():
    private_work = SourceWork.objects.create(
        slug="brhat-jataka-aiyar-1905-private",
        title="Brhat Jataka",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=private_work,
        reference="private full text chunk 0001",
        body="Yoga source area.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "private_full_text_chunk"},
    )

    coverage = source_coverage_matrix(
        [
            {
                "key": "yogas",
                "label": "Yogas",
                "source_priority": ["brhat-jataka", "missing-source"],
            }
        ]
    )

    row = coverage["layers"][0]
    assert row["coverage_status"] == "private_text_loaded"
    assert row["sources"][0]["coverage_status"] == "private_full_text_available"
    assert row["sources"][0]["private_full_text_chunks"] == 1
    assert row["sources"][1]["coverage_status"] == "missing"
    assert row["needs_exact_mapping"] is True


@pytest.mark.django_db
def test_source_coverage_api_returns_matrix():
    SourceWork.objects.create(
        slug="phaladipika-subrahmanya-sastri-private",
        title="Phaladipika",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )

    response = APIClient().get("/api/sources/coverage")

    assert response.status_code == 200
    assert response.json()["summary"]["total_layers"] >= 1
