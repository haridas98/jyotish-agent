import pytest

from apps.interpretations.models import ShastraConditionEvidence
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


@pytest.mark.django_db
def test_detected_yoga_source_map_marks_cataloged_yogas_as_research_only():
    try:
        from apps.interpretations.yoga_source_map import detected_yoga_source_map
    except ModuleNotFoundError:
        pytest.fail("detected yoga source map is not implemented yet")

    work = SourceWork.objects.create(
        slug="brhat-jataka-private",
        title="Brhat Jataka",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="candidate passage 0001",
        body="Gaja Kesari yoga candidate.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "candidate_shastra_passage"},
    )
    ShastraConditionEvidence.objects.create(
        condition_key="gaja_kesari",
        condition_kind="yoga_condition",
        condition_title="Gaja Kesari",
        passage=passage,
        score=10,
        reference_status="needs_review",
        public_quote_policy="blocked_until_approved",
    )

    chart = {
        "classical": {
            "yogas": {
                "items": [
                    {
                        "key": "gaja_kesari",
                        "name": "Gaja Kesari",
                        "bodies": ["Chandra", "Guru"],
                        "status": "calculated_needs_citation",
                        "reference": "Chandra",
                    },
                    {
                        "key": "amala_chandra",
                        "name": "Amala from Chandra",
                        "bodies": ["Budha"],
                        "status": "calculated_needs_citation",
                        "reference": "Chandra",
                    },
                    {
                        "key": "local_experimental_yoga",
                        "name": "Local Experimental Yoga",
                        "bodies": ["Surya"],
                        "status": "calculated_needs_citation",
                        "reference": "Lagna",
                    },
                ]
            }
        }
    }

    rows = detected_yoga_source_map(chart)

    gaja_kesari = rows[0]
    assert gaja_kesari["key"] == "gaja_kesari"
    assert gaja_kesari["catalog_key"] == "gaja_kesari"
    assert gaja_kesari["source_mapping_status"] == "mapped_research_only"
    assert gaja_kesari["review_status"] == "research_only"
    assert gaja_kesari["citation_policy"] == "required_for_public_interpretation"
    assert gaja_kesari["public_release_policy"] == "needs_approved_passage"
    assert gaja_kesari["detected_status"] == "calculated_needs_citation"
    assert gaja_kesari["source_link_count"] == 1
    assert gaja_kesari["evidence_status"] == "matched"
    assert gaja_kesari["approved_citation_count"] == 0
    assert gaja_kesari["bodies"] == ["Chandra", "Guru"]
    assert "Brhat Jataka" in gaja_kesari["source_priority"]
    assert "Krishna-centered" in gaja_kesari["public_explanation_outline"]
    assert gaja_kesari["formula"]["description"] == "Guru is in a kendra from Chandra."
    assert gaja_kesari["source_anchor_status"] == "exact_verse_verified"
    assert gaja_kesari["source_anchors"][0]["reference"] == "Chapter 36, Verses 3-4"
    assert gaja_kesari["explanation_plan"] == {
        "condition": "Guru is in a kendra from Chandra.",
        "primary_reference": {
            "work_title": "Brhat Parashara Hora Shastra",
            "reference": "Chapter 36, Verses 3-4",
            "reference_status": "exact_verse_verified",
            "source_url": "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-3/",
        },
        "source_summary": (
            "Defines Gaja Kesari and gives brilliance, wealth, intelligence, good qualities, "
            "and favor from rulers or authorities."
        ),
        "interpretation_hint": (
            "Read as protective intelligence/status potential; qualify by Jupiter strength, "
            "affliction, house lordship, and dasha."
        ),
        "gaudiya_guard": gaja_kesari["vaishnava_guard"],
        "client_text_sequence": [
            "condition",
            "shastra_reference",
            "chart_evidence",
            "qualified_interpretation",
            "gaudiya_guard",
        ],
        "citation_status": "exact_verse_verified",
    }

    amala_chandra = rows[1]
    assert amala_chandra["key"] == "amala_chandra"
    assert amala_chandra["catalog_key"] == "amala_chandra"
    assert amala_chandra["source_mapping_status"] == "mapped_research_only"
    assert amala_chandra["category"] == "rare_named_yoga"

    unknown = rows[2]
    assert unknown["key"] == "local_experimental_yoga"
    assert unknown["source_mapping_status"] == "missing_catalog_entry"
    assert unknown["public_release_policy"] == "block_public_interpretation"
    assert unknown["explanation_plan"]["citation_status"] == "missing_catalog_entry"
