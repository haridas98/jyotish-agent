def test_build_citation_requests_creates_section_and_yoga_search_tasks():
    try:
        from apps.interpretations.citation_requests import build_citation_requests
    except ModuleNotFoundError:
        import pytest

        pytest.fail("citation request builder is not implemented yet")

    requests = build_citation_requests(
        explanation_schedule=[
            {
                "key": "lagna_and_body",
                "title_ru": "Lagna",
                "depends_on": ["ascendant"],
                "source_priority": ["Brhat Jataka", "Prabhupada"],
                "implementation_status": "seeded_foundation",
            }
        ],
        detected_yoga_source_map=[
            {
                "key": "gaja_kesari",
                "catalog_key": "gaja_kesari",
                "name": "Gaja Kesari",
                "source_priority": ["Brhat Jataka", "Phaladipika"],
                "public_release_policy": "needs_approved_passage",
                "source_mapping_status": "mapped_research_only",
            },
            {
                "key": "local_experimental_yoga",
                "name": "Local Experimental Yoga",
                "public_release_policy": "block_public_interpretation",
                "source_mapping_status": "missing_catalog_entry",
            },
        ],
    )

    section = requests[0]
    assert section["kind"] == "section"
    assert section["key"] == "lagna_and_body"
    assert section["required_for_public_text"] is True
    assert section["citation_coverage_status"] == "needs_approved_passage"
    assert section["search_queries"][0] == "Lagna Brhat Jataka"

    yoga = requests[1]
    assert yoga["kind"] == "detected_yoga"
    assert yoga["key"] == "gaja_kesari"
    assert yoga["catalog_key"] == "gaja_kesari"
    assert yoga["source_priority"] == ["Brhat Jataka", "Phaladipika"]
    assert yoga["search_queries"] == ["Gaja Kesari Brhat Jataka", "Gaja Kesari Phaladipika"]
    assert yoga["citation_coverage_status"] == "needs_approved_passage"

    blocked = requests[2]
    assert blocked["key"] == "local_experimental_yoga"
    assert blocked["citation_coverage_status"] == "blocked_until_catalog_mapping"
    assert blocked["search_queries"] == []
