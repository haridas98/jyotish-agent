import json

from django.urls import reverse
from rest_framework.test import APIClient


def test_witness_summary_api_combines_jhora_and_parashara_light(settings, tmp_path):
    jhora_path = tmp_path / "jhora-accuracy.json"
    jhora_path.write_text(
        json.dumps(
            {
                "fixture_id": "sterlitamak-1998",
                "passed": False,
                "longitude_comparisons": [
                    {"body": "Surya", "delta_arcseconds": 42.0, "signed_delta_arcseconds": -42.0, "passed": False}
                ],
                "exact_matches": {"jhora.vimshopaka.Sun": True, "jhora.shadbala.Sun": False},
                "missing_fields": [],
                "diagnostics": {"jhora_layers": {"shadbala": {"checked": 1, "matched": 0, "failed": 1}}},
            }
        ),
        encoding="utf-8",
    )
    pl_packet_path = tmp_path / "pl-packet.json"
    pl_packet_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-parashara-light-verification-packet-v1",
                "id": "pl7-haridas",
                "status": "pl_ui_state_captured",
                "fixture": {
                    "review_status": "draft",
                    "pl_metadata": {"capture_status": "ui_state_captured"},
                    "capture_files": {"screenshots": []},
                    "manual_witness_values": [{"source": "pl7", "body": "Surya", "rashi": "Vrishabha"}],
                },
                "pl_capture_checklist": [],
                "jyotish_agent_chart": {
                    "grahas": [{"body": "Surya", "rashi": "Mesha", "rashi_index": 0}],
                    "houses": [{"house": 10, "rashi": "Mesha", "rashi_index": 0}],
                },
            }
        ),
        encoding="utf-8",
    )
    settings.JHORA_ACCURACY_REPORT_PATH = jhora_path
    settings.PARASHARA_LIGHT_PACKET_PATH = pl_packet_path
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    profile_report_path = tmp_path / "pl-profile.json"
    profile_report_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_birth_xml_profile",
                "source_xml": "C:\\GeoVision\\GeoVisionCharts\\Haridas.xml",
                "candidate_normalization": {
                    "longitude_east_candidate": 55.9666667,
                    "timezone_offset_hours_candidate": 6.0,
                },
                "packet_comparison": {
                    "longitude_delta_degrees": 0.016467,
                    "latitude_delta_degrees": -0.013733,
                    "timezone_delta_hours": 0.0,
                },
                "data_quality_flags": [
                    "PL_LONGITUDE_EAST_NEGATIVE_CONVENTION",
                    "PL_PACKET_COORDINATE_VARIANCE",
                ],
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_PROFILE_REPORT_PATH = profile_report_path

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    assert response.data["overall_status"] == "diff_open"
    assert response.data["jhora"]["available"] is True
    assert response.data["jhora"]["status"] == "diff_open"
    assert response.data["jhora"]["failed_checks"] == 2
    assert response.data["parashara_light"]["available"] is True
    assert response.data["parashara_light"]["status"] == "diff_open"
    assert response.data["parashara_light"]["manual_failed_count"] == 1
    profile = response.data["parashara_light"]["profile"]
    assert profile["available"] is True
    assert profile["status"] == "loaded"
    assert profile["authoritative"] is False
    assert profile["packet_comparison"]["longitude_delta_degrees"] == 0.016467
    assert "PL_PACKET_COORDINATE_VARIANCE" in profile["data_quality_flags"]
    assert response.data["open_items"][0]["source"] == "jhora"
    assert response.data["open_items"][1]["source"] == "parashara_light"


def test_witness_summary_api_reports_missing_sources(settings, tmp_path):
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    settings.PARASHARA_LIGHT_PROFILE_REPORT_PATH = tmp_path / "missing-pl-profile.json"

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    assert response.data["overall_status"] == "missing_witnesses"
    assert response.data["jhora"]["available"] is False
    assert response.data["parashara_light"]["available"] is False
    assert response.data["parashara_light"]["profile"]["available"] is False


def test_witness_summary_api_reports_pl_profile_load_error(settings, tmp_path):
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    profile_path = tmp_path / "broken-pl-profile.json"
    profile_path.write_text("{broken", encoding="utf-8")
    settings.PARASHARA_LIGHT_PROFILE_REPORT_PATH = profile_path

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    profile = response.data["parashara_light"]["profile"]
    assert profile["available"] is False
    assert profile["status"] == "load_error"
    assert profile["authoritative"] is False
    assert profile["source_report"] == str(profile_path)
