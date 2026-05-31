from __future__ import annotations

from django.conf import settings
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.vl_integration.client import check_vl_database


class HealthView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "jyotish-agent",
                "debug": settings.DEBUG,
            }
        )


class DatabaseHealthView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            value = cursor.fetchone()[0]
        return Response({"status": "ok", "database": "connected", "check": value})


class VLHealthView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        result = check_vl_database(settings.VL_DATABASE_URL)
        status = 200 if result["status"] in {"ok", "not_configured"} else 503
        return Response(result, status=status)

