from django.http import JsonResponse
from django.middleware.gzip import GZipMiddleware
from django.test import RequestFactory

from config import settings as project_settings
from config.settings import database_from_url, private_app_auth_default


def test_private_app_auth_is_enabled_by_default_in_production():
    assert private_app_auth_default(debug=False) is True


def test_private_app_auth_can_stay_relaxed_by_default_in_development():
    assert private_app_auth_default(debug=True) is False


def test_codex_generation_queue_is_enabled_by_default():
    assert project_settings.CODEX_GENERATION_QUEUE_ENABLED is True


def test_gzip_middleware_is_enabled_for_large_json_responses():
    assert "django.middleware.gzip.GZipMiddleware" in project_settings.MIDDLEWARE


def test_gzip_middleware_compresses_large_json_responses():
    middleware = GZipMiddleware(lambda _request: JsonResponse({"payload": "x" * 5000}))
    request = RequestFactory().get("/api/large-json", HTTP_ACCEPT_ENCODING="gzip")

    response = middleware(request)

    assert response["Content-Encoding"] == "gzip"
    assert int(response["Content-Length"]) < 5000


def test_database_from_url_accepts_postgres_env_fallback(monkeypatch):
    monkeypatch.setattr(project_settings, "DEBUG", False)
    monkeypatch.setenv("POSTGRES_DB", "jyotish_agent")
    monkeypatch.setenv("POSTGRES_USER", "jyotish")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_PORT", "5433")

    config = database_from_url(None)

    assert config["ENGINE"] == "django.db.backends.postgresql"
    assert config["NAME"] == "jyotish_agent"
    assert config["USER"] == "jyotish"
    assert config["HOST"] == "db"
    assert config["PORT"] == "5433"


def test_database_from_url_accepts_sqlite_url():
    config = database_from_url("sqlite:////srv/jyotish-agent/app/backend/db.sqlite3")

    assert config["ENGINE"] == "django.db.backends.sqlite3"
    assert config["NAME"] == "/srv/jyotish-agent/app/backend/db.sqlite3"
