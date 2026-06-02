import pytest
from django.core.management import CommandError, call_command

from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


def test_yoga_registry_starts_broad_rare_yoga_catalog():
    try:
        from apps.interpretations.yoga_catalog import yoga_registry
    except ModuleNotFoundError:
        pytest.fail("yoga catalog is not implemented yet")

    yogas = yoga_registry()
    keys = {yoga["key"] for yoga in yogas}

    assert len(yogas) >= 90
    assert {
        "gaja_kesari",
        "budha_aditya",
        "ruchaka_mahapurusha",
        "dharma_karmadhipati_raja",
        "viparita_harsha",
        "shakata_nabhasa",
        "gola_nabhasa",
        "pravrajya",
        "tapasvi",
        "kala_sarpa_contested",
    }.issubset(keys)
    assert sum(1 for yoga in yogas if yoga["rarity"] == "rare") >= 25
    assert all(yoga["citation_policy"] == "required_for_public_interpretation" for yoga in yogas)
    assert all(yoga["source_priority"] for yoga in yogas)
    assert all(yoga["vaishnava_guard"] for yoga in yogas)


@pytest.mark.django_db
def test_seed_yoga_catalog_creates_idempotent_research_only_passages():
    try:
        from apps.interpretations.yoga_catalog import yoga_registry
    except ModuleNotFoundError:
        pytest.fail("yoga catalog is not implemented yet")

    try:
        call_command("seed_yoga_catalog")
    except CommandError:
        pytest.fail("seed_yoga_catalog command is not implemented yet")

    first_counts = {
        "works": SourceWork.objects.count(),
        "passages": SourcePassage.objects.count(),
    }

    call_command("seed_yoga_catalog")

    assert {
        "works": SourceWork.objects.count(),
        "passages": SourcePassage.objects.count(),
    } == first_counts

    work = SourceWork.objects.get(slug="classical-yoga-research-catalog")
    assert work.review_status == ReviewStatus.RESEARCH_ONLY
    assert work.metadata["source_role"] == "yoga_catalog_index"

    yoga_count = len(yoga_registry())
    passages = SourcePassage.objects.filter(work=work)
    assert passages.count() == yoga_count
    passage = passages.get(reference="Yoga catalog: Gaja Kesari")
    assert passage.review_status == ReviewStatus.RESEARCH_ONLY
    assert passage.metadata["yoga_key"] == "gaja_kesari"
    assert passage.metadata["public_quote_status"] == "summary_anchor_only"
