from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.conf import settings
from django.db import transaction
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.charts.services import ChartProfileInputError, create_birth_profile, profile_payload

from .settings_service import SettingsInputError, get_or_create_user_settings, settings_payload, update_user_settings


def _normalize_username(value: object) -> str:
    return str(value or "").strip().casefold()


def user_payload(user) -> dict[str, object]:
    return {
        "id": user.id,
        "username": user.get_username(),
        "email": user.email,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
    }


class RegisterView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        username = _normalize_username(request.data.get("username", ""))
        email = str(request.data.get("email") or "").strip().casefold()
        password = str(request.data.get("password") or "")

        if not username or not password:
            return Response({"error": "username and password are required"}, status=400)
        if len(password) < 10:
            return Response({"error": "password must be at least 10 characters"}, status=400)
        if get_user_model().objects.filter(username__iexact=username).exists():
            return Response({"error": "username already exists"}, status=409)

        try:
            with transaction.atomic():
                user = get_user_model().objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=True,
                )
                profile = _create_registration_self_profile(user, request.data)
        except IntegrityError:
            return Response({"error": "username already exists"}, status=409)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)

        login(request, user)
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        payload = {"user": user_payload(user), "status": "active"}
        if profile is not None:
            payload["profile"] = profile_payload(profile)
        return Response(payload, status=201)


class LoginView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        username = _normalize_username(request.data.get("username", ""))
        password = str(request.data.get("password") or "")
        canonical_username = _canonical_username_for_login(username)
        user = authenticate(request, username=canonical_username, password=password)
        if user is None:
            inactive = get_user_model().objects.filter(username__iexact=username, is_active=False).exists()
            if inactive:
                return Response({"error": "account pending approval"}, status=403)
            return Response({"error": "invalid credentials"}, status=401)

        login(request, user)
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return Response({"user": user_payload(user)})


def _canonical_username_for_login(username: str) -> str:
    existing = get_user_model().objects.filter(username__iexact=username).only("username").first()
    return existing.username if existing is not None else username


def _create_registration_self_profile(user, data) -> object | None:
    birth_date = str(data.get("birth_date") or "").strip()
    place_name = str(data.get("place_name") or "").strip()
    if not birth_date and not place_name:
        return None
    if not birth_date or not place_name:
        raise ChartProfileInputError("birth_date and place_name are required to create the first chart")

    birth_time = str(data.get("birth_time") or "").strip()
    return create_birth_profile(
        user,
        {
            "display_name": str(data.get("display_name") or "Моя карта").strip() or "Моя карта",
            "birth_date": birth_date,
            "birth_time": birth_time,
            "birth_time_accuracy": data.get("birth_time_accuracy") or ("exact" if birth_time else "unknown"),
            "place_name": place_name,
            "is_self_profile": True,
            "timezone": data.get("timezone"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        },
    )


class LogoutView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        logout(request)
        return Response({"status": "ok"})


class MeView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"user": None}, status=401)
        return Response({"user": user_payload(request.user)})


class UserSettingsView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)
        settings = get_or_create_user_settings(request.user)
        return Response(settings_payload(settings))

    def patch(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)
        try:
            settings = update_user_settings(request.user, request.data)
        except SettingsInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response(settings_payload(settings))


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return Response({"status": "ok"})
