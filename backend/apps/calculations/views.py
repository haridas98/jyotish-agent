from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from apps.accounts.permissions import PrivateAppAccess

from .chart import ChartInputError, build_birth_chart
from .dual_calculation import build_dual_calculation_report
from .ephemeris import EphemerisUnavailable, SwissEphemerisProvider
from .jhora_accuracy_report import load_jhora_accuracy_report
from .parashara_light_packet_report import load_parashara_light_packet_report
from .primitives import zodiac_placement
from .workflows import (
    build_compatibility_report,
    build_muhurta_report,
    build_mundane_report,
    build_prashna_report,
    build_tajaka_report,
    build_tithi_pravesha_report,
    build_transit_report,
)


class ZodiacPlacementView(APIView):
    permission_classes = [PrivateAppAccess]

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
    permission_classes = [PrivateAppAccess]

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


class JHoraAccuracyReportView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        path = getattr(settings, "JHORA_ACCURACY_REPORT_PATH", "")
        if not path:
            path = settings.ROOT_DIR / ".tmp" / "jhora" / "sterlitamak-1998" / "accuracy-report.json"
        try:
            return Response(load_jhora_accuracy_report(path))
        except FileNotFoundError:
            return Response({"error": "JHora accuracy report is not captured yet"}, status=404)


class ParasharaLightPacketReportView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        path = getattr(settings, "PARASHARA_LIGHT_PACKET_PATH", "")
        if not path:
            path = settings.ROOT_DIR / ".tmp" / "pl7" / "haridas-verification-packet" / "packet.json"
        try:
            return Response(load_parashara_light_packet_report(path))
        except FileNotFoundError:
            return Response({"error": "Parashara Light verification packet is not captured yet"}, status=404)


class BirthChartView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_birth_chart(request.data))
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class DualCalculationView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_dual_calculation_report(request.data))
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class TransitView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_transit_report(request.data))
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class CompatibilityView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_compatibility_report(request.data))
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class MuhurtaView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_muhurta_report(request.data))
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class TithiPraveshaView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_tithi_pravesha_report(request.data))
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class TajakaView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_tajaka_report(request.data))
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class PrashnaView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_prashna_report(request.data))
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class MundaneView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(build_mundane_report(request.data))
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)
