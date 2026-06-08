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
