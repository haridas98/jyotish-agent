def test_detected_yoga_source_map_marks_cataloged_yogas_as_research_only():
    try:
        from apps.interpretations.yoga_source_map import detected_yoga_source_map
    except ModuleNotFoundError:
        import pytest

        pytest.fail("detected yoga source map is not implemented yet")

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
    assert gaja_kesari["bodies"] == ["Chandra", "Guru"]
    assert "Brhat Jataka" in gaja_kesari["source_priority"]
    assert "Krishna-centered" in gaja_kesari["public_explanation_outline"]

    amala_chandra = rows[1]
    assert amala_chandra["key"] == "amala_chandra"
    assert amala_chandra["catalog_key"] == "amala"
    assert amala_chandra["source_mapping_status"] == "mapped_research_only"
    assert amala_chandra["category"] == "rare_named_yoga"

    unknown = rows[2]
    assert unknown["key"] == "local_experimental_yoga"
    assert unknown["source_mapping_status"] == "missing_catalog_entry"
    assert unknown["public_release_policy"] == "block_public_interpretation"
