from apps.calculations.jhora_parity_suite import (
    assess_review_batch_coverage,
    jhora_parity_suite_manifest,
)


def test_jhora_parity_suite_manifest_exposes_p2_review_batch_contract():
    manifest = jhora_parity_suite_manifest()

    contract = manifest["review_batch_contract"]

    assert manifest["case_count"] >= 20
    assert contract["target_reviewed_count"] == 20
    assert contract["suite_case_count"] == manifest["case_count"]
    assert contract["coverage_target_met"] is True
    assert contract["missing_required_groups"] == []
    assert contract["missing_required_focus"] == []
    for group in ["dst_sensitive", "historical", "boundary_sensitive", "modern_exact_timezone"]:
        assert contract["group_counts"][group] >= 1
    for focus in ["timezone_dst", "historical_timezone", "panchanga", "vargas", "dashas", "lagna", "sunrise"]:
        assert contract["focus_counts"][focus] >= 1


def test_review_batch_coverage_contract_reports_missing_group_and_focus():
    contract = assess_review_batch_coverage(
        [
            {
                "id": "one",
                "group": "dst_sensitive",
                "focus": ["timezone_dst"],
            }
        ]
    )

    assert contract["coverage_target_met"] is False
    assert "historical" in contract["missing_required_groups"]
    assert "panchanga" in contract["missing_required_focus"]
    assert contract["suite_case_count"] == 1
