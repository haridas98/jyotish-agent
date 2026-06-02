import pytest

from apps.sources.citations import combined_citation_search, local_approved_citation_search
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
