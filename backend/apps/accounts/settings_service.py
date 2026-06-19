from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractBaseUser

from apps.calculations.vargas import workbench_varga_codes

from .models import UserJyotishSettings


class SettingsInputError(ValueError):
    pass


DEFAULT_CALCULATION_SETTINGS: dict[str, Any] = {
    "ayanamsa": "lahiri",
    "zodiacType": "sidereal",
    "houseSystem": "whole_sign",
    "nodeType": "mean",
    "calculationProfile": "gaudiya_default",
    "divisionalChartsEnabled": ["D1", "D9"],
    "defaultDivisionalChart": "D1",
    "timezoneMode": "birth_place_timezone",
}

DEFAULT_DISPLAY_SETTINGS: dict[str, Any] = {
    "chartStyle": "north_indian",
    "language": "ru",
    "terminologyMode": "mixed",
    "degreeFormat": "dms",
    "showSanskritNames": True,
    "showTransliteration": True,
    "themeMode": "system",
}

ALLOWED_VALUES = {
    "calculation": {
        "ayanamsa": {"lahiri", "raman", "krishnamurti", "yukteshwar"},
        "zodiacType": {"sidereal"},
        "houseSystem": {"whole_sign", "sripati", "equal"},
        "nodeType": {"mean", "true"},
        "calculationProfile": {"default", "bphs_research", "gaudiya_default"},
        "defaultDivisionalChart": set(workbench_varga_codes()),
        "timezoneMode": {"birth_place_timezone"},
    },
    "display": {
        "chartStyle": {"north_indian", "south_indian"},
        "language": {"ru", "en"},
        "terminologyMode": {"russian", "sanskrit", "mixed"},
        "degreeFormat": {"dms", "decimal"},
        "themeMode": {"system", "light", "dark"},
    },
}

ALLOWED_DIVISIONAL_CHARTS = set(workbench_varga_codes())


def settings_payload(settings: UserJyotishSettings) -> dict[str, Any]:
    return {
        "id": settings.id,
        "userId": settings.user_id,
        "calculation": normalize_calculation_settings(settings.calculation),
        "display": normalize_display_settings(settings.display),
        "createdAt": settings.created_at.isoformat(),
        "updatedAt": settings.updated_at.isoformat(),
    }


def get_or_create_user_settings(user: AbstractBaseUser) -> UserJyotishSettings:
    settings, _created = UserJyotishSettings.objects.get_or_create(
        user=user,
        defaults={
            "calculation": DEFAULT_CALCULATION_SETTINGS.copy(),
            "display": DEFAULT_DISPLAY_SETTINGS.copy(),
        },
    )
    changed = False
    calculation = normalize_calculation_settings(settings.calculation)
    display = normalize_display_settings(settings.display)
    if settings.calculation != calculation:
        settings.calculation = calculation
        changed = True
    if settings.display != display:
        settings.display = display
        changed = True
    if changed:
        settings.save(update_fields=["calculation", "display", "updated_at"])
    return settings


def update_user_settings(user: AbstractBaseUser, data: dict[str, Any]) -> UserJyotishSettings:
    settings = get_or_create_user_settings(user)
    changed_fields: list[str] = []

    if "calculation" in data:
        settings.calculation = normalize_calculation_settings(data.get("calculation") or {})
        changed_fields.append("calculation")
    if "display" in data:
        settings.display = normalize_display_settings(data.get("display") or {})
        changed_fields.append("display")

    if changed_fields:
        settings.save(update_fields=[*changed_fields, "updated_at"])
    return settings


def normalize_calculation_settings(raw: object) -> dict[str, Any]:
    values = _merge_dict(DEFAULT_CALCULATION_SETTINGS, raw)
    for key, allowed in ALLOWED_VALUES["calculation"].items():
        _validate_choice("calculation", key, values.get(key), allowed)
    charts = values.get("divisionalChartsEnabled")
    if not isinstance(charts, list):
        raise SettingsInputError("calculation.divisionalChartsEnabled must be a list")
    normalized_charts = [str(chart).strip().upper() for chart in charts]
    if not normalized_charts:
        raise SettingsInputError("calculation.divisionalChartsEnabled must not be empty")
    unknown = [chart for chart in normalized_charts if chart not in ALLOWED_DIVISIONAL_CHARTS]
    if unknown:
        raise SettingsInputError("calculation.divisionalChartsEnabled contains unknown chart")
    if values["defaultDivisionalChart"] not in normalized_charts:
        raise SettingsInputError("calculation.defaultDivisionalChart must be enabled")
    values["divisionalChartsEnabled"] = normalized_charts
    return values


def normalize_display_settings(raw: object) -> dict[str, Any]:
    values = _merge_dict(DEFAULT_DISPLAY_SETTINGS, raw)
    for key, allowed in ALLOWED_VALUES["display"].items():
        _validate_choice("display", key, values.get(key), allowed)
    values["showSanskritNames"] = _validate_bool("display", "showSanskritNames", values.get("showSanskritNames"))
    values["showTransliteration"] = _validate_bool("display", "showTransliteration", values.get("showTransliteration"))
    return values


def _merge_dict(defaults: dict[str, Any], raw: object) -> dict[str, Any]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise SettingsInputError("settings section must be an object")
    return {**defaults, **raw}


def _validate_choice(section: str, key: str, value: object, allowed: set[str]) -> None:
    if value not in allowed:
        raise SettingsInputError(f"{section}.{key} is invalid")


def _validate_bool(section: str, key: str, value: object) -> bool:
    if not isinstance(value, bool):
        raise SettingsInputError(f"{section}.{key} must be boolean")
    return value
