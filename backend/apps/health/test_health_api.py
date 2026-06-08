import pytest
from django.urls import reverse
from rest_framework.test import APIClient


def test_health_api_reports_deploy_commit_from_file(settings, tmp_path):
    settings.ROOT_DIR = tmp_path
    (tmp_path / ".deploy-commit").write_text("101d432\n", encoding="utf-8")

    response = APIClient().get(reverse("health"))

    assert response.status_code == 200
    assert response.data["status"] == "ok"
    assert response.data["deploy_commit"] == "101d432"


def test_health_api_reports_deploy_commit_from_env(settings, monkeypatch, tmp_path):
    settings.ROOT_DIR = tmp_path
    monkeypatch.setenv("JYOTISH_DEPLOY_COMMIT", "env-commit")

    response = APIClient().get(reverse("health"))

    assert response.status_code == 200
    assert response.data["deploy_commit"] == "env-commit"


@pytest.mark.django_db
def test_database_health_api_runs_select_one():
    response = APIClient().get(reverse("health-db"))

    assert response.status_code == 200
    assert response.data == {"status": "ok", "database": "connected", "check": 1}


def test_vl_health_api_reports_not_configured(settings):
    settings.VL_DATABASE_URL = ""

    response = APIClient().get(reverse("health-vl"))

    assert response.status_code == 200
    assert response.data["status"] == "not_configured"
    assert response.data["database"] == "vl"


def test_vl_health_api_reports_error_as_unavailable(monkeypatch):
    monkeypatch.setattr(
        "apps.health.views.check_vl_database",
        lambda database_url: {"status": "error", "database": "vl", "detail": "connection refused"},
    )

    response = APIClient().get(reverse("health-vl"))

    assert response.status_code == 503
    assert response.data == {"status": "error", "database": "vl", "detail": "connection refused"}
