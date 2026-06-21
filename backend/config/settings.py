from __future__ import annotations

import os
import importlib.util
from pathlib import Path
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

load_dotenv(ROOT_DIR / ".env")
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def private_app_auth_default(debug: bool) -> bool:
    return not debug


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
PRIVATE_APP_REQUIRE_AUTH = env_bool("PRIVATE_APP_REQUIRE_AUTH", private_app_auth_default(DEBUG))
ENABLE_DEV_LOGIN = env_bool("ENABLE_DEV_LOGIN", False)
DEV_LOGIN_TOKEN = os.getenv("DEV_LOGIN_TOKEN", "").strip()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.accounts",
    "apps.places",
    "apps.health",
    "apps.calculations",
    "apps.charts",
    "apps.sources",
    "apps.interpretations",
    "apps.reports",
    "apps.vl_integration",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


def database_from_url(url: str | None) -> dict[str, object]:
    if not url:
        postgres_db = os.getenv("POSTGRES_DB")
        postgres_user = os.getenv("POSTGRES_USER")
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        postgres_host = os.getenv("POSTGRES_HOST", "127.0.0.1")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        if postgres_db and postgres_user and postgres_password:
            return {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": postgres_db,
                "USER": postgres_user,
                "PASSWORD": postgres_password,
                "HOST": postgres_host,
                "PORT": postgres_port,
            }
        if not DEBUG:
            raise ImproperlyConfigured("DATABASE_URL or POSTGRES_DB/POSTGRES_USER/POSTGRES_PASSWORD is required when DJANGO_DEBUG=false")
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }

    parsed = urlparse(url)
    if parsed.scheme == "sqlite":
        if not DEBUG and not env_bool("ALLOW_PRODUCTION_SQLITE", False):
            raise ImproperlyConfigured(
                "SQLite is disabled when DJANGO_DEBUG=false. Use PostgreSQL DATABASE_URL, "
                "or set ALLOW_PRODUCTION_SQLITE=true only for emergency rollback."
            )
        sqlite_path = parsed.path
        if sqlite_path.startswith("//"):
            sqlite_path = sqlite_path[1:]
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_path,
        }

    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError(f"Unsupported DATABASE_URL scheme: {parsed.scheme}")

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username or "",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or 5432),
    }


DATABASES = {
    "default": database_from_url(os.getenv("DATABASE_URL")),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if env_bool("DJANGO_SECURE_PROXY_SSL_HEADER", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", not DEBUG)
SESSION_COOKIE_AGE = int(os.getenv("DJANGO_SESSION_COOKIE_AGE", "2592000"))
SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool("DJANGO_SESSION_EXPIRE_AT_BROWSER_CLOSE", False)
SESSION_SAVE_EVERY_REQUEST = env_bool("DJANGO_SESSION_SAVE_EVERY_REQUEST", False)
SESSION_COOKIE_SAMESITE = os.getenv("DJANGO_SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")

CORS_ALLOWED_ORIGINS = env_list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    "http://127.0.0.1:3130,http://localhost:3130",
)
CORS_ALLOW_CREDENTIALS = env_bool("DJANGO_CORS_ALLOW_CREDENTIALS", True)
CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://127.0.0.1:3130,http://localhost:3130",
)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

REDIS_URL = os.getenv("REDIS_URL", "")
DJANGO_REDIS_AVAILABLE = importlib.util.find_spec("django_redis") is not None
if REDIS_URL and DJANGO_REDIS_AVAILABLE:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "TIMEOUT": int(os.getenv("DJANGO_CACHE_TIMEOUT_SECONDS", "600")),
        }
    }
else:
    if REDIS_URL and not DEBUG:
        raise ImproperlyConfigured("django-redis must be installed when REDIS_URL is set in production")
    CACHES = {
        "default": {
            "BACKEND": os.getenv("DJANGO_CACHE_BACKEND", "django.core.cache.backends.locmem.LocMemCache"),
            "LOCATION": os.getenv("DJANGO_CACHE_LOCATION", "jyotish-agent-cache"),
            "TIMEOUT": int(os.getenv("DJANGO_CACHE_TIMEOUT_SECONDS", "600")),
        }
    }
BIRTH_REPORT_CACHE_SECONDS = int(os.getenv("BIRTH_REPORT_CACHE_SECONDS", "3600"))
CURRENT_DAY_REPORT_CACHE_SECONDS = int(os.getenv("CURRENT_DAY_REPORT_CACHE_SECONDS", "1800"))
CODEX_ANALYSIS_LOCK_SECONDS = int(os.getenv("CODEX_ANALYSIS_LOCK_SECONDS", "900"))
CODEX_CHAT_LOCK_SECONDS = int(os.getenv("CODEX_CHAT_LOCK_SECONDS", "300"))
CODEX_MAX_RUNNING_GENERATIONS_PER_USER = int(os.getenv("CODEX_MAX_RUNNING_GENERATIONS_PER_USER", "1"))
CODEX_RUNNING_GENERATION_STALE_SECONDS = int(os.getenv("CODEX_RUNNING_GENERATION_STALE_SECONDS", "1800"))
CODEX_GENERATION_QUEUE_ENABLED = env_bool("CODEX_GENERATION_QUEUE_ENABLED", True)

VL_DATABASE_URL = os.getenv("VL_DATABASE_URL", "")
VL_PUBLIC_BASE_URL = os.getenv("VL_PUBLIC_BASE_URL", "http://127.0.0.1:3001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")
CODEX_ANALYSIS_PROVIDER = os.getenv("CODEX_ANALYSIS_PROVIDER", "codex_cli").strip().lower()
AI_REPORTS_ENABLED = env_bool("AI_REPORTS_ENABLED", False)
AI_PROVIDER = os.getenv("AI_PROVIDER", "disabled").strip().lower()
AI_REAL_PROVIDER_ENABLED = env_bool("AI_REAL_PROVIDER_ENABLED", False)
AI_REPORTS_PUBLIC_UI = env_bool("AI_REPORTS_PUBLIC_UI", False)
AI_REPORTS_STAGING_ONLY = env_bool("AI_REPORTS_STAGING_ONLY", True)
AI_REPORTS_ALLOW_PRODUCTION_REAL = env_bool("AI_REPORTS_ALLOW_PRODUCTION_REAL", False)
AI_REAL_PROVIDER_API_KEY = os.getenv("AI_REAL_PROVIDER_API_KEY", os.getenv("OPENAI_API_KEY", ""))
AI_REAL_PROVIDER_URL = os.getenv("AI_REAL_PROVIDER_URL", "https://api.openai.com/v1/responses")
AI_REAL_PROVIDER_MODEL = os.getenv("AI_REAL_PROVIDER_MODEL", os.getenv("OPENAI_MODEL", "gpt-5.2"))
AI_REPORT_GATEWAY_TIMEOUT_SECONDS = int(os.getenv("AI_REPORT_GATEWAY_TIMEOUT_SECONDS", "15"))
AI_REPORT_GATEWAY_RATE_LIMIT_PER_MINUTE = int(os.getenv("AI_REPORT_GATEWAY_RATE_LIMIT_PER_MINUTE", "6"))
AI_REPORT_GATEWAY_MAX_REQUEST_BYTES = int(os.getenv("AI_REPORT_GATEWAY_MAX_REQUEST_BYTES", "2048"))
AI_REPORT_GATEWAY_MAX_RESPONSE_BYTES = int(os.getenv("AI_REPORT_GATEWAY_MAX_RESPONSE_BYTES", "65536"))
AI_REPORT_GATEWAY_MIN_ELIGIBLE_ITEMS = int(os.getenv("AI_REPORT_GATEWAY_MIN_ELIGIBLE_ITEMS", "2"))
AI_REPORT_GATEWAY_MIN_CITATION_CHAINS = int(os.getenv("AI_REPORT_GATEWAY_MIN_CITATION_CHAINS", "2"))
AI_REPORT_GATEWAY_MAX_THESES = int(os.getenv("AI_REPORT_GATEWAY_MAX_THESES", "8"))
AI_REPORT_GATEWAY_MAX_THESIS_CHARS = int(os.getenv("AI_REPORT_GATEWAY_MAX_THESIS_CHARS", "900"))
JHORA_ACCURACY_REPORT_PATH = os.getenv(
    "JHORA_ACCURACY_REPORT_PATH",
    str(ROOT_DIR / ".tmp" / "jhora" / "sterlitamak-1998" / "accuracy-report.json"),
)
JHORA_WITNESS_CASE_PATH = os.getenv(
    "JHORA_WITNESS_CASE_PATH",
    str(ROOT_DIR / ".tmp" / "jhora" / "batch-queue" / "sterlitamak-1998-04-30-1345"),
)
WITNESS_REVIEW_BATCH_INDEX_PATH = os.getenv(
    "WITNESS_REVIEW_BATCH_INDEX_PATH",
    str(ROOT_DIR / ".tmp" / "witness-review" / "_index.json"),
)
WITNESS_CAPTURE_QUEUE_PATH = os.getenv(
    "WITNESS_CAPTURE_QUEUE_PATH",
    str(ROOT_DIR / ".tmp" / "witness-review" / "capture-queue.json"),
)
WITNESS_CORE_PARITY_REPORT_PATH = os.getenv(
    "WITNESS_CORE_PARITY_REPORT_PATH",
    str(ROOT_DIR / ".tmp" / "witness-review" / "core-parity-report.json"),
)
WITNESS_VARGA_PARITY_REPORT_PATH = os.getenv(
    "WITNESS_VARGA_PARITY_REPORT_PATH",
    str(ROOT_DIR / ".tmp" / "witness-review" / "varga-parity-report.json"),
)
PARASHARA_LIGHT_PACKET_PATH = os.getenv(
    "PARASHARA_LIGHT_PACKET_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-verification-packet" / "packet.json"),
)
PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = os.getenv(
    "PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-manual-values-template.json"),
)
PARASHARA_LIGHT_PROFILE_REPORT_PATH = os.getenv(
    "PARASHARA_LIGHT_PROFILE_REPORT_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-profile-report.json"),
)
PARASHARA_LIGHT_FORENSIC_REPORT_PATH = os.getenv(
    "PARASHARA_LIGHT_FORENSIC_REPORT_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-swiss-forensic-dump.json"),
)
PARASHARA_LIGHT_SETTINGS_EVIDENCE_PATH = os.getenv(
    "PARASHARA_LIGHT_SETTINGS_EVIDENCE_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-settings-evidence.json"),
)
PARASHARA_LIGHT_VISIBLE_SETTINGS_CAPTURE_PATH = os.getenv(
    "PARASHARA_LIGHT_VISIBLE_SETTINGS_CAPTURE_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-visible-settings-capture.json"),
)
PARASHARA_LIGHT_CALCULATION_OPTIONS_REPORT_PATH = os.getenv(
    "PARASHARA_LIGHT_CALCULATION_OPTIONS_REPORT_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-calculation-options-report.json"),
)
PARASHARA_LIGHT_SETTINGS_AWARE_FORENSIC_PATH = os.getenv(
    "PARASHARA_LIGHT_SETTINGS_AWARE_FORENSIC_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-settings-aware-forensic.json"),
)
PARASHARA_LIGHT_PREFERENCES_INVENTORY_PATH = os.getenv(
    "PARASHARA_LIGHT_PREFERENCES_INVENTORY_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-preferences-inventory.json"),
)
PARASHARA_LIGHT_HIDDEN_OPTION_STORE_PATH = os.getenv(
    "PARASHARA_LIGHT_HIDDEN_OPTION_STORE_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-hidden-option-store.json"),
)
PARASHARA_LIGHT_OPTION_STORE_DIFF_PATH = os.getenv(
    "PARASHARA_LIGHT_OPTION_STORE_DIFF_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-option-store-diff.json"),
)
PARASHARA_LIGHT_INTERNAL_SETTINGS_AUDIT_PATH = os.getenv(
    "PARASHARA_LIGHT_INTERNAL_SETTINGS_AUDIT_PATH",
    str(ROOT_DIR / ".tmp" / "pl7" / "haridas-pl-internal-settings-audit.json"),
)
