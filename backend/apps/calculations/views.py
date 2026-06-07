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
from .witness_summary import build_witness_summary
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
        manual_witness_values_path = getattr(settings, "PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH", "")
        try:
            return Response(
                load_parashara_light_packet_report(
                    path,
                    manual_witness_values_path=manual_witness_values_path,
                )
            )
        except FileNotFoundError:
            return Response({"error": "Parashara Light verification packet is not captured yet"}, status=404)


class WitnessSummaryView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        jhora_path = getattr(settings, "JHORA_ACCURACY_REPORT_PATH", "")
        if not jhora_path:
            jhora_path = settings.ROOT_DIR / ".tmp" / "jhora" / "sterlitamak-1998" / "accuracy-report.json"
        pl_packet_path = getattr(settings, "PARASHARA_LIGHT_PACKET_PATH", "")
        if not pl_packet_path:
            pl_packet_path = settings.ROOT_DIR / ".tmp" / "pl7" / "haridas-verification-packet" / "packet.json"
        return Response(
            build_witness_summary(
                jhora_report_path=jhora_path,
                jhora_witness_case_path=getattr(settings, "JHORA_WITNESS_CASE_PATH", ""),
                witness_review_batch_index_path=getattr(settings, "WITNESS_REVIEW_BATCH_INDEX_PATH", ""),
                witness_capture_queue_path=getattr(settings, "WITNESS_CAPTURE_QUEUE_PATH", ""),
                parashara_light_packet_path=pl_packet_path,
                parashara_light_manual_values_path=getattr(settings, "PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH", ""),
                parashara_light_profile_report_path=getattr(settings, "PARASHARA_LIGHT_PROFILE_REPORT_PATH", ""),
                parashara_light_forensic_report_path=getattr(settings, "PARASHARA_LIGHT_FORENSIC_REPORT_PATH", ""),
                parashara_light_settings_evidence_path=getattr(settings, "PARASHARA_LIGHT_SETTINGS_EVIDENCE_PATH", ""),
                parashara_light_visible_settings_capture_path=getattr(
                    settings,
                    "PARASHARA_LIGHT_VISIBLE_SETTINGS_CAPTURE_PATH",
                    "",
                ),
                parashara_light_calculation_options_report_path=getattr(
                    settings,
                    "PARASHARA_LIGHT_CALCULATION_OPTIONS_REPORT_PATH",
                    "",
                ),
                parashara_light_settings_aware_forensic_path=getattr(
                    settings,
                    "PARASHARA_LIGHT_SETTINGS_AWARE_FORENSIC_PATH",
                    "",
                ),
                parashara_light_preferences_inventory_path=getattr(
                    settings,
                    "PARASHARA_LIGHT_PREFERENCES_INVENTORY_PATH",
                    "",
                ),
                parashara_light_hidden_option_store_path=getattr(
                    settings,
                    "PARASHARA_LIGHT_HIDDEN_OPTION_STORE_PATH",
                    "",
                ),
                parashara_light_option_store_diff_path=getattr(
                    settings,
                    "PARASHARA_LIGHT_OPTION_STORE_DIFF_PATH",
                    "",
                ),
                parashara_light_internal_settings_audit_path=getattr(
                    settings,
                    "PARASHARA_LIGHT_INTERNAL_SETTINGS_AUDIT_PATH",
                    "",
                ),
            )
        )


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
