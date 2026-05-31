from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import APIView


def user_payload(user) -> dict[str, object]:
    return {
        "id": user.id,
        "username": user.get_username(),
        "email": user.email,
    }


class RegisterView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        email = str(request.data.get("email", "")).strip()
        password = str(request.data.get("password", ""))

        if not username or not password:
            return Response({"error": "username and password are required"}, status=400)
        if len(password) < 10:
            return Response({"error": "password must be at least 10 characters"}, status=400)

        try:
            user = get_user_model().objects.create_user(
                username=username,
                email=email,
                password=password,
            )
        except IntegrityError:
            return Response({"error": "username already exists"}, status=409)

        login(request, user)
        return Response({"user": user_payload(user)}, status=201)


class LoginView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        password = str(request.data.get("password", ""))
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"error": "invalid credentials"}, status=401)

        login(request, user)
        return Response({"user": user_payload(user)})


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

