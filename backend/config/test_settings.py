from config import settings as project_settings
from config.settings import database_from_url, private_app_auth_default


def test_private_app_auth_is_enabled_by_default_in_production():
    assert private_app_auth_default(debug=False) is True


def test_private_app_auth_can_stay_relaxed_by_default_in_development():
    assert private_app_auth_default(debug=True) is False


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
