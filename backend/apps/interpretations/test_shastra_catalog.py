import pytest
from django.core.management import CommandError, call_command

from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


def test_explanation_schedule_orders_full_chart_explanations():
    try:
        from apps.interpretations.shastra_catalog import explanation_schedule
    except ModuleNotFoundError:
        pytest.fail("shastra catalog is not implemented yet")

    schedule = explanation_schedule()
    keys = [section["key"] for section in schedule]

    assert keys[:4] == [
        "calculation_audit",
        "lagna_and_body",
        "graha_placements",
        "moon_mind_and_dasha_seed",
    ]
    assert "d1_d60_vargas" in keys
    assert "avasthas_shadbala_vimshopaka" in keys
    assert "ashtakavarga" in keys
    assert "yogas_argala_special_points" in keys
    assert "transits" in keys
    assert "compatibility" in keys
    assert "muhurta" in keys
    assert "vaishnava_remedies" in keys
    assert all(section["citation_policy"] == "required_for_public_text" for section in schedule)
    assert all(section["source_priority"] for section in schedule)


@pytest.mark.django_db
def test_seed_shastra_catalog_creates_idempotent_authority_sources_and_review_anchors():
    try:
        call_command("seed_shastra_catalog")
    except CommandError:
        pytest.fail("seed_shastra_catalog command is not implemented yet")

    first_counts = {
        "works": SourceWork.objects.count(),
        "passages": SourcePassage.objects.count(),
    }

    call_command("seed_shastra_catalog")

    assert {
        "works": SourceWork.objects.count(),
        "passages": SourcePassage.objects.count(),
    } == first_counts

    big_five = {
        "brhat-jataka",
        "jataka-parijata",
        "phaladipika",
        "saravali",
        "sarvartha-cintamani",
    }
    assert big_five.issubset(set(SourceWork.objects.values_list("slug", flat=True)))
    brhat_jataka = SourceWork.objects.get(slug="brhat-jataka")
    assert brhat_jataka.metadata["authority_tier"] == "primary_classic"
    assert "archive.org" in brhat_jataka.source_url
    assert brhat_jataka.metadata["access_policy"] == "public_domain_scan"
    assert SourceWork.objects.get(slug="phaladipika").metadata["access_policy"] == "copyright_review_required"
    assert SourceWork.objects.get(slug="brhat-parashara-hora-shastra").metadata["authority_note"] == "use_with_caution"

    passage = SourcePassage.objects.get(reference="Shyamasundara recommended reading list")
    assert passage.review_status == ReviewStatus.RESEARCH_ONLY
    assert passage.metadata["source_role"] == "bibliography_anchor"
