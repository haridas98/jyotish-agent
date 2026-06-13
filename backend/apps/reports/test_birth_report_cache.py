from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient


@override_settings(BIRTH_REPORT_CACHE_SECONDS=300)
def test_birth_report_reuses_cached_payload(monkeypatch):
    cache.clear()
    calls = {"count": 0}

    def fake_compose_birth_report(data, **kwargs):
        calls["count"] += 1
        return {
            "chart": {"birth": {"date": data["birth_date"]}, "grahas": []},
            "report": {"sections": []},
        }

    monkeypatch.setattr("apps.reports.views.compose_birth_report", fake_compose_birth_report)
    payload = {
        "birth_date": "1998-04-30",
        "birth_time": "13:45",
        "place_name": "Sterlitamak",
        "timezone": "Asia/Yekaterinburg",
    }
    client = APIClient()

    first = client.post("/api/reports/birth-chart", payload, format="json")
    second = client.post("/api/reports/birth-chart", payload, format="json")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.headers["X-Jyotish-Cache"] == "miss"
    assert second.headers["X-Jyotish-Cache"] == "hit"
    assert calls["count"] == 1
