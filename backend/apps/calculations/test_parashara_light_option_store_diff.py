import json

from django.core.management import call_command


def _snapshot(label, files):
    return {
        "source": "parashara_light_option_store_hash_snapshot",
        "label": label,
        "visible_setting": "System.ShowStatusBar",
        "files": files,
    }


def test_option_store_diff_identifies_changed_and_restored_candidate(tmp_path):
    from apps.calculations.parashara_light_option_store_diff import (
        build_parashara_light_option_store_diff_report,
    )

    before_path = tmp_path / "before.json"
    changed_path = tmp_path / "changed.json"
    restored_path = tmp_path / "restored.json"
    before_path.write_text(
        json.dumps(
            _snapshot(
                "before",
                [
                    {"relative_path": "popts1.dat", "bytes": 200, "sha256": "a" * 64},
                    {"relative_path": "OP2000.L1", "bytes": 1260, "sha256": "b" * 64},
                ],
            )
        ),
        encoding="utf-8",
    )
    changed_path.write_text(
        json.dumps(
            _snapshot(
                "after_toggle",
                [
                    {"relative_path": "popts1.dat", "bytes": 200, "sha256": "c" * 64},
                    {"relative_path": "OP2000.L1", "bytes": 1260, "sha256": "b" * 64},
                ],
            )
        ),
        encoding="utf-8",
    )
    restored_path.write_text(
        json.dumps(
            _snapshot(
                "after_restore",
                [
                    {"relative_path": "popts1.dat", "bytes": 200, "sha256": "a" * 64},
                    {"relative_path": "OP2000.L1", "bytes": 1260, "sha256": "b" * 64},
                ],
            )
        ),
        encoding="utf-8",
    )

    report = build_parashara_light_option_store_diff_report(
        before_snapshot_path=before_path,
        changed_snapshot_path=changed_path,
        restored_snapshot_path=restored_path,
    )

    assert report["source"] == "parashara_light_option_store_diff"
    assert report["status"] == "option_store_diff_captured"
    assert report["proprietary_binary_policy"] == "hash_only_do_not_parse"
    assert report["visible_setting"] == "System.ShowStatusBar"
    assert report["restore_verified"] is True
    assert report["changed_candidates_count"] == 1
    assert report["changed_candidates"][0]["relative_path"] == "popts1.dat"
    assert report["changed_candidates"][0]["restored_to_before"] is True
    assert report["primary_candidate"] == "popts1.dat"
    assert report["next_action"] == "inspect_pl_native_export_or_ephemeris_mode"
    assert "content_preview" not in report["changed_candidates"][0]


def test_option_store_diff_reports_no_hash_change(tmp_path):
    from apps.calculations.parashara_light_option_store_diff import (
        build_parashara_light_option_store_diff_report,
    )

    files = [{"relative_path": "popts1.dat", "bytes": 200, "sha256": "a" * 64}]
    before_path = tmp_path / "before.json"
    changed_path = tmp_path / "changed.json"
    restored_path = tmp_path / "restored.json"
    before_path.write_text(json.dumps(_snapshot("before", files)), encoding="utf-8")
    changed_path.write_text(json.dumps(_snapshot("after_toggle", files)), encoding="utf-8")
    restored_path.write_text(json.dumps(_snapshot("after_restore", files)), encoding="utf-8")

    report = build_parashara_light_option_store_diff_report(
        before_snapshot_path=before_path,
        changed_snapshot_path=changed_path,
        restored_snapshot_path=restored_path,
    )

    assert report["status"] == "no_option_store_hash_change_detected"
    assert report["restore_verified"] is True
    assert report["changed_candidates_count"] == 0
    assert report["next_action"] == "try_another_visible_setting_or_capture_native_export"


def test_option_store_diff_command_writes_json(monkeypatch, tmp_path):
    output_path = tmp_path / "report.json"

    def fake_build(**kwargs):
        assert kwargs["before_snapshot_path"] == tmp_path / "before.json"
        assert kwargs["changed_snapshot_path"] == tmp_path / "changed.json"
        assert kwargs["restored_snapshot_path"] == tmp_path / "restored.json"
        return {"source": "parashara_light_option_store_diff", "status": "option_store_diff_captured"}

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_parashara_light_option_store_diff."
        "build_parashara_light_option_store_diff_report",
        fake_build,
    )

    call_command(
        "build_parashara_light_option_store_diff",
        "--before-snapshot",
        str(tmp_path / "before.json"),
        "--changed-snapshot",
        str(tmp_path / "changed.json"),
        "--restored-snapshot",
        str(tmp_path / "restored.json"),
        "--output",
        str(output_path),
    )

    assert json.loads(output_path.read_text(encoding="utf-8"))["status"] == "option_store_diff_captured"
