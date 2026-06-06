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


def test_manual_witness_values_compare_against_chart_fields():
    from apps.calculations.manual_witness_comparison import compare_manual_witness_values

    chart = {
        "ascendant": {
            "body": "Lagna",
            "longitude": 115.414369,
            "rashi": "Karka",
            "rashi_index": 3,
            "nakshatra": "Ashlesha",
            "pada": 3,
        },
        "grahas": [
            {
                "body": "Surya",
                "longitude": 15.942392,
                "rashi": "Mesha",
                "rashi_index": 0,
                "nakshatra": "Bharani",
                "pada": 1,
            },
            {
                "body": "Chandra",
                "longitude": 68.368275,
                "rashi": "Mithuna",
                "rashi_index": 2,
                "nakshatra": "Ardra",
                "pada": 1,
            },
        ],
        "houses": [
            {"house": 1, "rashi": "Karka", "rashi_index": 3},
            {"house": 10, "rashi": "Mesha", "rashi_index": 0},
        ],
    }
    witness_values = [
        {
            "source": "pl7",
            "body": "Lagna",
            "longitude": 115.4144,
            "rashi": "Karka",
            "nakshatra": "Ashlesha",
            "pada": 3,
            "house": 1,
        },
        {
            "source": "pl7",
            "body": "Surya",
            "rashi": "Mesha",
            "nakshatra": "Bharani",
            "pada": 1,
            "house": 10,
        },
        {
            "source": "pl7",
            "body": "Chandra",
            "rashi": "Karka",
            "nakshatra": "Ardra",
            "pada": 1,
        },
    ]

    report = compare_manual_witness_values(chart, witness_values)

    assert report["status"] == "diff_open"
    assert report["summary"]["manual_values_count"] == 3
    assert report["summary"]["failed_count"] == 1
    assert report["summary"]["missing_count"] == 0
    assert report["diffs"] == [
        {
            "source": "pl7",
            "body": "Chandra",
            "field": "rashi",
            "witness": "Karka",
            "calculated": "Mithuna",
            "passed": False,
        }
    ]


def test_packet_report_includes_manual_witness_comparison(tmp_path):
    from apps.calculations.parashara_light_packet_report import load_parashara_light_packet_report

    path = tmp_path / "packet.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-parashara-light-verification-packet-v1",
                "id": "pl7-manual-values",
                "status": "pl_ui_state_captured",
                "fixture": {
                    "review_status": "draft",
                    "pl_metadata": {},
                    "capture_files": {"screenshots": []},
                    "manual_witness_values": [
                        {"source": "pl7", "body": "Lagna", "rashi": "Karka", "house": 1},
                        {"source": "pl7", "body": "Surya", "rashi": "Vrishabha"},
                    ],
                },
                "pl_capture_checklist": [],
                "jyotish_agent_chart": {
                    "ascendant": {"body": "Lagna", "rashi": "Karka", "rashi_index": 3},
                    "grahas": [{"body": "Surya", "rashi": "Mesha", "rashi_index": 0}],
                    "houses": [{"house": 1, "rashi": "Karka", "rashi_index": 3}],
                },
            }
        ),
        encoding="utf-8",
    )

    report = load_parashara_light_packet_report(path)

    assert report["manual_witness_comparison"]["status"] == "diff_open"
    assert report["manual_witness_comparison"]["summary"]["manual_values_count"] == 2
    assert report["manual_witness_comparison"]["summary"]["failed_count"] == 1
    assert report["manual_witness_comparison"]["diffs"][0]["body"] == "Surya"


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
