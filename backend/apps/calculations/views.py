from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

from .chart import ChartInputError, build_birth_chart
from .ephemeris import EphemerisUnavailable, SwissEphemerisProvider
from .primitives import zodiac_placement


class ZodiacPlacementView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        raw_longitude = request.query_params.get("longitude")
        if raw_longitude is None:
            return Response({"error": "longitude query parameter is required"}, status=400)

        try:
            longitude = float(raw_longitude)
        except ValueError:
            return Response({"error": "longitude must be a number"}, status=400)

        placement = zodiac_placement(longitude)
        return Response(
            {
                "longitude": placement.longitude,
                "rashi": {
                    "index": placement.rashi_index,
                    "name": placement.rashi,
                },
                "nakshatra": {
                    "index": placement.nakshatra_index,
                    "name": placement.nakshatra,
                    "pada": placement.pada,
                },
                "navamsa": {
                    "index": placement.navamsa_index,
                    "name": placement.navamsa,
                },
            }
        )


class EphemerisStatusView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        provider = SwissEphemerisProvider()
        try:
            provider._load_swisseph()
        except EphemerisUnavailable as exc:
            return Response(
                {
                    "provider": "swiss",
                    "available": False,
                    "detail": str(exc),
                }
            )

        return Response(
            {
                "provider": "swiss",
                "available": True,
                "detail": "Swiss Ephemeris Python bindings are importable",
            }
        )


class BirthChartView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        try:
            return Response(build_birth_chart(request.data))
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)
