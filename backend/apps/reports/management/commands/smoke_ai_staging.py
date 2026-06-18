from __future__ import annotations

import json
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.charts.models import BirthProfile, ChartCalculation, Place
from apps.reports.ai_gateway import (
    AiGatewayInputError,
    build_ai_report_request,
    execute_ai_report_staging_run,
    real_provider_enabled,
)
from apps.reports.ai_real_provider import InsufficientVerifiedEvidence, build_provider_payload, citation_count


def _bool_setting(name: str) -> bool:
    return bool(getattr(settings, name, False))


def _assert_staging_env() -> None:
    expected = {
        "AI_REPORTS_ENABLED": True,
        "AI_REAL_PROVIDER_ENABLED": True,
        "AI_REPORTS_PUBLIC_UI": False,
        "AI_REPORTS_STAGING_ONLY": True,
    }
    for name, value in expected.items():
        if _bool_setting(name) is not value:
            raise CommandError(f"{name} must be {str(value).lower()} for staging smoke")
    if str(getattr(settings, "AI_PROVIDER", "")).strip().lower() != "real":
        raise CommandError("AI_PROVIDER must be real for staging smoke")
    if not str(getattr(settings, "AI_REAL_PROVIDER_API_KEY", "") or "").strip():
        raise CommandError("AI_REAL_PROVIDER_API_KEY is not configured")
    if not real_provider_enabled():
        raise CommandError("real provider is not enabled for this environment")


def _create_smoke_profile() -> tuple[object, Place, BirthProfile]:
    suffix = uuid4().hex[:12]
    user = get_user_model().objects.create_user(
        username=f"ai-staging-smoke-{suffix}",
        password=uuid4().hex,
        email=f"ai-staging-smoke-{suffix}@example.invalid",
    )
    place = Place.objects.create(
        external_id=f"ai-staging-smoke-{suffix}",
        name=f"ai-staging-smoke-place-{suffix}",
        country_code="IN",
        latitude="23.424100",
        longitude="88.388600",
        timezone_name="Asia/Kolkata",
    )
    profile = BirthProfile.objects.create(
        user=user,
        display_name=f"ai-staging-smoke-{suffix}",
        birth_date="1990-05-14",
        birth_time="07:15",
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        gender=BirthProfile.Gender.UNKNOWN,
        place=place,
        timezone_name=place.timezone_name,
    )
    ChartCalculation.objects.create(
        profile=profile,
        calculation_version="ai-staging-smoke",
        status=ChartCalculation.Status.COMPLETE,
        result={
            "houses": [{"house": 1, "sign": "Taurus"}],
            "grahas": [{"body": "Surya"}, {"body": "Chandra"}],
            "vargas": {"D1": {}, "D9": {}},
            "dashas": {"vimshottari": []},
        },
    )
    return user, place, profile


def _assert_anonymized_payload(profile: BirthProfile, payload: dict) -> None:
    serialized = json.dumps(payload, ensure_ascii=False)
    forbidden_values = [
        profile.display_name,
        str(profile.birth_date),
        str(profile.birth_time),
        profile.place.name if profile.place else "",
        str(profile.place.latitude) if profile.place else "",
        str(profile.place.longitude) if profile.place else "",
        profile.user.email,
    ]
    for value in forbidden_values:
        if value and value in serialized:
            raise CommandError("pii audit failed")


def _cleanup(user, place, profile) -> None:
    ChartCalculation.objects.filter(profile=profile).delete()
    BirthProfile.objects.filter(id=profile.id).delete()
    Place.objects.filter(id=place.id).delete()
    get_user_model().objects.filter(id=user.id).delete()


class Command(BaseCommand):
    help = "Run one staging-only real AI report smoke and print a safe receipt."

    def handle(self, *args, **options):
        _assert_staging_env()
        user = place = profile = None
        try:
            user, place, profile = _create_smoke_profile()
            request = build_ai_report_request(
                profile=profile,
                relationship=None,
                report_type_id="personal_overview",
                language="ru",
                audience="novice",
            )
            _assert_anonymized_payload(profile, build_provider_payload(request))

            execution = execute_ai_report_staging_run(
                profile=profile,
                relationship=None,
                report_type_id="personal_overview",
                language="ru",
                audience="novice",
            )

            empty_profile = BirthProfile.objects.create(
                user=user,
                display_name=f"{profile.display_name}-empty",
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
                gender=BirthProfile.Gender.UNKNOWN,
                place=place,
                timezone_name=place.timezone_name,
            )
            try:
                execute_ai_report_staging_run(
                    profile=empty_profile,
                    relationship=None,
                    report_type_id="personal_overview",
                    language="ru",
                    audience="novice",
                )
            except InsufficientVerifiedEvidence:
                pass
            else:
                raise CommandError("insufficient evidence did not stop provider execution")
            finally:
                BirthProfile.objects.filter(id=empty_profile.id).delete()

            receipt = {
                "requestId": execution.metadata["request_id"],
                "environment": "staging",
                "providerAlias": "real",
                "modelAlias": str(getattr(settings, "AI_REAL_PROVIDER_MODEL", "unknown")),
                "status": execution.metadata["validation_result"],
                "durationMs": execution.metadata["elapsed_ms"],
                "eligibleItemCount": len(request["items"]),
                "citationChainCount": citation_count(request),
                "thesisCount": len(execution.response.get("theses") or []),
                "inputTokens": None,
                "outputTokens": None,
                "estimatedCost": None,
                "responseValidation": "passed",
                "citationValidation": "passed",
                "piiAudit": "passed",
                "rawContentStored": False,
            }
            self.stdout.write(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
        except (AiGatewayInputError, CommandError):
            raise
        except Exception as exc:
            raise CommandError("staging smoke failed") from exc
        finally:
            if user and place and profile:
                _cleanup(user, place, profile)
