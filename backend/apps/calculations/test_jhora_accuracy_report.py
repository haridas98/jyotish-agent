import json

from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from apps.calculations.jhora_accuracy_report import load_jhora_accuracy_report


def test_load_jhora_accuracy_report_groups_failures(tmp_path):
    path = tmp_path / "accuracy-report.json"
    path.write_text(
        json.dumps(
            {
                "fixture_id": "sample",
                "passed": False,
                "longitude_comparisons": [
                    {"body": "Surya", "delta_arcseconds": 76.0, "signed_delta_arcseconds": -76.0, "passed": False},
                    {"body": "Rahu", "delta_arcseconds": 0.01, "signed_delta_arcseconds": -0.01, "passed": True},
                ],
                "exact_matches": {
                    "panchanga.tithi": False,
                    "jhora.ashtakavarga.Su.Mesha": True,
                    "jhora.shadbala.Sun.shadbala": False,
                },
                "missing_fields": ["jhora.vimsopaka.Rahu"],
                "diagnostics": {
                    "max_abs_delta_arcseconds": 76.0,
                    "median_abs_delta_arcseconds": 38.0,
                    "ayanamsa": {
                        "delta_arcseconds": 56.5,
                        "corrected_max_abs_delta_arcseconds": 20.0,
                    },
                    "jhora_layers": {
                        "ashtakavarga": {"checked": 12, "matched": 12, "failed": 0},
                        "shadbala": {"checked": 1, "matched": 0, "failed": 1, "max_abs_delta": 20.0},
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    report = load_jhora_accuracy_report(path)

    assert report["fixture_id"] == "sample"
    assert report["summary"]["longitude"]["ayanamsa_delta_arcseconds"] == 56.5
    assert report["summary"]["longitude"]["corrected_max_delta_arcseconds"] == 20.0
    assert report["summary"]["exact_groups"][0]["key"] == "ashtakavarga"
    assert report["summary"]["jhora_layers"]["shadbala"]["failed"] == 1


def test_load_jhora_accuracy_report_accepts_utf8_bom(tmp_path):
    path = tmp_path / "accuracy-report.json"
    payload = {
        "fixture_id": "bom-sample",
        "passed": True,
        "longitude_comparisons": [],
        "exact_matches": {},
        "missing_fields": [],
        "diagnostics": {},
    }
    path.write_text("\ufeff" + json.dumps(payload), encoding="utf-8")

    report = load_jhora_accuracy_report(path)

    assert report["fixture_id"] == "bom-sample"


def test_jhora_accuracy_report_api_reads_configured_report(settings, tmp_path):
    path = tmp_path / "accuracy-report.json"
    path.write_text(
        json.dumps(
            {
                "fixture_id": "api-sample",
                "passed": True,
                "longitude_comparisons": [],
                "exact_matches": {},
                "missing_fields": [],
                "diagnostics": {},
            }
        ),
        encoding="utf-8",
    )
    settings.JHORA_ACCURACY_REPORT_PATH = path

    response = APIClient().get(reverse("jhora-accuracy"))

    assert response.status_code == 200
    assert response.data["fixture_id"] == "api-sample"
    assert response.data["source_report"] == str(path)


def test_jhora_accuracy_report_api_caches_report_until_file_changes(settings, tmp_path, monkeypatch):
    cache.clear()
    path = tmp_path / "accuracy-report.json"
    path.write_text('{"fixture_id":"cached","passed":true}', encoding="utf-8")
    settings.JHORA_ACCURACY_REPORT_PATH = path
    calls = {"count": 0}

    def fake_loader(source_path):
        calls["count"] += 1
        return {"fixture_id": json.loads(path.read_text(encoding="utf-8"))["fixture_id"], "source_report": str(source_path)}

    monkeypatch.setattr("apps.calculations.views.load_jhora_accuracy_report", fake_loader)
    client = APIClient()

    first = client.get(reverse("jhora-accuracy"))
    second = client.get(reverse("jhora-accuracy"))
    path.write_text('{"fixture_id":"changed","passed":true,"extra":"mtime"}', encoding="utf-8")
    third = client.get(reverse("jhora-accuracy"))

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 200
    assert first.data["fixture_id"] == "cached"
    assert second.data["fixture_id"] == "cached"
    assert third.data["fixture_id"] == "changed"
    assert calls["count"] == 2
