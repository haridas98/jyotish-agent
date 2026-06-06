import json


def test_hidden_option_store_candidates_are_hash_only(tmp_path):
    from apps.calculations.parashara_light_hidden_option_store import (
        build_parashara_light_hidden_option_store_report,
    )

    settings_evidence_path = tmp_path / "settings-evidence.json"
    settings_evidence_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_settings_evidence",
                "proprietary_binary_policy": "hash_only_do_not_parse",
                "options_manifest": [
                    {
                        "relative_path": "popts1.dat",
                        "bytes": 200,
                        "modified_at": "2026-06-05T21:33:32+00:00",
                        "sha256": "a" * 64,
                    },
                    {
                        "relative_path": "OP2000.L1",
                        "bytes": 1260,
                        "modified_at": "2026-06-05T21:33:32+00:00",
                        "sha256": "b" * 64,
                    },
                    {
                        "relative_path": "TRANSOP.D1",
                        "bytes": 344,
                        "modified_at": "2005-09-20T08:18:08+00:00",
                        "sha256": "c" * 64,
                    },
                    {
                        "relative_path": "COLOR0.DAT",
                        "bytes": 1471,
                        "modified_at": "2026-06-05T21:33:32+00:00",
                        "sha256": "d" * 64,
                    },
                ],
                "session_token_manifest": [
                    {
                        "relative_path": "Temp/20501.e31",
                        "bytes": 512,
                        "modified_at": "2026-06-05T21:40:00+00:00",
                        "sha256": "e" * 64,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = build_parashara_light_hidden_option_store_report(
        settings_evidence_path=settings_evidence_path,
    )

    assert report["source"] == "parashara_light_hidden_option_store"
    assert report["status"] == "hidden_option_store_candidates_identified"
    assert report["proprietary_binary_policy"] == "hash_only_do_not_parse"
    assert report["primary_candidate"]["relative_path"] == "popts1.dat"
    assert report["candidate_counts"]["option_store_candidates"] == 3
    assert report["candidate_counts"]["session_token_candidates"] == 1
    assert report["next_action"] == "diff_option_store_before_after_visible_setting_change"
    assert "content_preview" not in report["option_store_candidates"][0]
