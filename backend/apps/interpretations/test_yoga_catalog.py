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
            "amala_chandra",
        }.issubset(keys)
    assert sum(1 for yoga in yogas if yoga["rarity"] == "rare") >= 25
    assert all(yoga["citation_policy"] == "required_for_public_interpretation" for yoga in yogas)
    assert all(yoga["source_priority"] for yoga in yogas)
    assert all(yoga["vaishnava_guard"] for yoga in yogas)
    assert all(yoga.get("formula", {}).get("description") for yoga in yogas)
    assert all(yoga.get("formula", {}).get("status") for yoga in yogas)
    assert all(yoga.get("formula", {}).get("source_basis") for yoga in yogas)
    assert all(yoga.get("source_anchors") for yoga in yogas)
    gaja = next(yoga for yoga in yogas if yoga["key"] == "gaja_kesari")
    assert gaja["source_anchor_status"] == "exact_verse_verified"
    assert gaja["source_anchors"][0]["reference"] == "Chapter 36, Verses 3-4"
    assert gaja["formula"]["source_anchors"][0]["work_title"] == "Brhat Parashara Hora Shastra"
    ruchaka = next(yoga for yoga in yogas if yoga["key"] == "ruchaka_mahapurusha")
    assert ruchaka["source_anchor_status"] == "exact_verse_verified"
    assert ruchaka["source_anchors"][0]["condition_key"] == "ruchaka_mahapurusha"
    assert ruchaka["source_anchors"][0]["reference"] == "Chapter 75, Verses 1-2"
    sunapha = next(yoga for yoga in yogas if yoga["key"] == "sunapha")
    assert sunapha["source_anchor_status"] == "exact_verse_verified"
    assert sunapha["source_anchors"][0]["reference"] == "Chapter 37, Verses 7-10"
    veshi = next(yoga for yoga in yogas if yoga["key"] == "veshi")
    assert veshi["source_anchor_status"] == "exact_verse_verified"
    assert veshi["source_anchors"][0]["reference"] == "Chapter 38, Verses 1-4"
    viparita = next(yoga for yoga in yogas if yoga["key"] == "viparita_harsha")
    assert viparita["source_anchor_status"] == "curated_research_anchor"
    assert viparita["source_anchors"][0]["reference"] == "Chapter 6, Verses 57, 63, 65, and 69"
    pravrajya = next(yoga for yoga in yogas if yoga["key"] == "pravrajya")
    assert pravrajya["source_anchor_status"] == "exact_verse_verified"
    assert pravrajya["source_anchors"][0]["reference"] == "Chapter XV, Verses 1-4"
    exact_count = sum(1 for yoga in yogas if yoga["source_anchor_status"] == "exact_verse_verified")
    assert exact_count >= 50
    assert not [yoga["key"] for yoga in yogas if yoga["source_anchor_status"] == "curated_anchor_needs_review"]
    assert next(yoga for yoga in yogas if yoga["key"] == "chakra_nabhasa")["source_anchors"][0][
        "reference"
    ] == "Chapter 35, Verse 15"
    assert next(yoga for yoga in yogas if yoga["key"] == "saraswati")["source_anchors"][0][
        "reference"
    ] == "Chapter 6, Verses 26-27"
    assert next(yoga for yoga in yogas if yoga["key"] == "amala")["source_anchors"][0]["reference"] == (
        "Chapter 6, Verses 19-20"
    )
    assert not [
        yoga["key"]
        for yoga in yogas
        if yoga.get("formula", {}).get("status") == "formula_outline_needs_exact_rule"
    ]
    implemented = {yoga["key"]: yoga for yoga in yogas}
    assert implemented["grahana"]["detection_status"] == "signature_ready"
    assert implemented["dusthana_lord_exchange_viparita"]["detection_status"] == "signature_ready"
    assert implemented["asubha_vesi"]["detection_status"] == "signature_ready"


def test_yoga_catalog_overview_reports_formula_and_anchor_coverage():
    from apps.interpretations.yoga_catalog import yoga_catalog_overview

    overview = yoga_catalog_overview()

    assert overview["total_yogas"] >= 100
    assert overview["anchor_coverage"]["all_yogas_have_source_anchor"] is True
    assert overview["anchor_coverage"]["exact_verse_verified"] >= 70
    assert overview["formula_coverage"]["all_yogas_have_formula"] is True
    assert overview["formula_coverage"]["implemented_detection_count"] >= 50


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
    assert passage.metadata["source_anchor_status"] == "exact_verse_verified"
    assert passage.metadata["source_anchors"][0]["reference"] == "Chapter 36, Verses 3-4"
    ruchaka = passages.get(reference="Yoga catalog: Ruchaka Mahapurusha")
    assert ruchaka.metadata["source_anchors"][0]["condition_key"] == "ruchaka_mahapurusha"
    assert ruchaka.metadata["source_anchors"][0]["reference"] == "Chapter 75, Verses 1-2"
