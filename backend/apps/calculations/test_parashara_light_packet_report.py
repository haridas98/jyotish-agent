import json

from django.urls import reverse
from rest_framework.test import APIClient


def test_load_parashara_light_packet_report_summarizes_packet(tmp_path):
    from apps.calculations.parashara_light_packet_report import load_parashara_light_packet_report

    path = tmp_path / "packet.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-parashara-light-verification-packet-v1",
                "id": "pl7-haridas-1998",
                "status": "pl_ui_state_captured",
                "fixture": {
                    "review_status": "draft",
                    "pl_metadata": {
                        "version_required": "7.0.1",
                        "window_title": "Parashara's Light 7.0.1 - [Haridas]",
                        "control_count": 26,
                        "screenshot_blank": False,
                        "capture_status": "ui_state_captured",
                    },
                    "capture_files": {
                        "ui_state": ".tmp/pl7/haridas-ui-state.json",
                        "screenshots": [".tmp/pl7/haridas-ui-state.png"],
                        "fingerprints": {
                            "ui_state": {"sha256": "abc", "bytes": 100},
                            "screenshots": [{"sha256": "def", "bytes": 200}],
                        },
                    },
                },
                "pl_capture_checklist": ["Capture PL settings", "Review visible values"],
                "jyotish_agent_chart": {"ascendant": {"rashi": "Karka"}},
            }
        ),
        encoding="utf-8",
    )

    report = load_parashara_light_packet_report(path)

    assert report["id"] == "pl7-haridas-1998"
    assert report["summary"]["review_status"] == "draft"
    assert report["summary"]["window_title"].startswith("Parashara's Light")
    assert report["summary"]["screenshot_blank"] is False
    assert report["summary"]["screenshots_count"] == 1
    assert report["summary"]["fingerprints"]["ui_state"]["sha256"] == "abc"
    assert report["summary"]["jyotish_agent_lagna"] == "Karka"
    assert report["checklist_count"] == 2
    assert report["source_packet"] == str(path)


def test_parashara_light_packet_report_api_reads_configured_packet(settings, tmp_path):
    path = tmp_path / "packet.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-parashara-light-verification-packet-v1",
                "id": "pl7-api",
                "status": "pl_ui_state_captured",
                "fixture": {
                    "review_status": "draft",
                    "pl_metadata": {"window_title": "Parashara's Light", "screenshot_blank": False},
                    "capture_files": {"screenshots": []},
                },
                "pl_capture_checklist": [],
                "jyotish_agent_chart": {},
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_PACKET_PATH = path

    response = APIClient().get(reverse("parashara-light-packet"))

    assert response.status_code == 200
    assert response.data["id"] == "pl7-api"
    assert response.data["summary"]["review_status"] == "draft"


def test_parashara_light_packet_report_api_returns_404_when_missing(settings, tmp_path):
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing.json"

    response = APIClient().get(reverse("parashara-light-packet"))

    assert response.status_code == 404
