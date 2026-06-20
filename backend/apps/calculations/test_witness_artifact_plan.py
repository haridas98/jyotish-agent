from pathlib import Path


def test_witness_artifact_plan_uses_deterministic_batch_queue_paths(tmp_path):
    from apps.calculations.witness_artifact_plan import build_witness_artifact_plan

    case_id = "sterlitamak-1998-04-30-1345"

    direct = build_witness_artifact_plan(
        case_id=case_id,
        jhora_root=tmp_path / "jhora" / "batch-queue",
        pl_root=tmp_path / "pl7" / "batch-queue",
        review_output_root=tmp_path / "review",
    )
    nested = build_witness_artifact_plan(
        case_id=case_id,
        jhora_root=tmp_path / "jhora",
        pl_root=tmp_path / "pl7",
        review_output_root=tmp_path / "review",
    )

    assert direct["schema_version"] == "jyotish-witness-artifact-plan-v1"
    assert direct["jhora"]["packet_dir"] == str(tmp_path / "jhora" / "batch-queue" / case_id)
    assert nested["jhora"]["packet_dir"] == direct["jhora"]["packet_dir"]
    assert nested["parashara_light"]["packet_dir"] == str(tmp_path / "pl7" / "batch-queue" / case_id)
    assert nested["review"]["packet_path"] == str(Path(tmp_path / "review" / f"{case_id}.md"))


def test_witness_artifact_plan_marks_existing_and_missing_files(tmp_path):
    from apps.calculations.witness_artifact_plan import build_witness_artifact_plan

    case_id = "sterlitamak-1998-04-30-1345"
    case_dir = tmp_path / "jhora" / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    (case_dir / "packet.json").write_text("{}", encoding="utf-8")
    (case_dir / "fixture.json").write_text("{}", encoding="utf-8")

    plan = build_witness_artifact_plan(case_id=case_id, jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    checks = {item["name"]: item for item in plan["jhora"]["checks"]}

    assert checks["packet_json"]["exists"] is True
    assert checks["fixture_json"]["exists"] is True
    assert checks["complete_calculations_text"]["exists"] is False
    assert checks["complete_calculations_text"]["required_for_review"] is True
    assert "jhora_complete_calculations_text" in plan["jhora"]["missing_required_evidence_groups"]
    assert "manual_witness_values" in plan["parashara_light"]["missing_required_evidence_groups"]


def test_witness_artifact_plan_empty_screenshots_dir_is_still_missing(tmp_path):
    from apps.calculations.witness_artifact_plan import build_witness_artifact_plan

    case_id = "case-a"
    (tmp_path / "jhora" / "batch-queue" / case_id / "screenshots").mkdir(parents=True)
    (tmp_path / "pl7" / "batch-queue" / case_id / "screenshots").mkdir(parents=True)

    plan = build_witness_artifact_plan(case_id=case_id, jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    jhora_screenshots = next(item for item in plan["jhora"]["checks"] if item["name"] == "screenshots")
    pl_screenshots = next(item for item in plan["parashara_light"]["checks"] if item["name"] == "screenshots")

    assert jhora_screenshots["exists"] is False
    assert jhora_screenshots["files"] == []
    assert pl_screenshots["exists"] is False
    assert pl_screenshots["files"] == []
    assert "jhora_screenshots" in plan["jhora"]["missing_required_evidence_groups"]
    assert "pl_screenshots" in plan["parashara_light"]["missing_required_evidence_groups"]


def test_witness_artifact_plan_screenshots_require_allowed_image_files(tmp_path):
    from apps.calculations.witness_artifact_plan import build_witness_artifact_plan

    case_id = "case-a"
    jhora_screens = tmp_path / "jhora" / "batch-queue" / case_id / "screenshots"
    pl_screens = tmp_path / "pl7" / "batch-queue" / case_id / "screenshots"
    jhora_screens.mkdir(parents=True)
    pl_screens.mkdir(parents=True)
    (jhora_screens / "screen.png").write_bytes(b"png")
    (jhora_screens / "notes.txt").write_text("ignored", encoding="utf-8")
    (pl_screens / "screen.webp").write_bytes(b"webp")

    plan = build_witness_artifact_plan(case_id=case_id, jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    jhora_screenshots = next(item for item in plan["jhora"]["checks"] if item["name"] == "screenshots")
    pl_screenshots = next(item for item in plan["parashara_light"]["checks"] if item["name"] == "screenshots")

    assert jhora_screenshots["exists"] is True
    assert jhora_screenshots["files"] == [str(jhora_screens / "screen.png")]
    assert pl_screenshots["exists"] is True
    assert pl_screenshots["files"] == [str(pl_screens / "screen.webp")]
    assert "jhora_screenshots" not in plan["jhora"]["missing_required_evidence_groups"]
    assert "pl_screenshots" not in plan["parashara_light"]["missing_required_evidence_groups"]
