from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.calculations.witness_parity_roadmap import build_witness_parity_roadmap
from apps.calculations.witness_summary import build_witness_summary


class Command(BaseCommand):
    help = "Build a safe witness parity roadmap launch ledger from the witness summary payload."

    def add_arguments(self, parser):
        parser.add_argument("--out", default="")
        parser.add_argument("--fail-if-review", action="store_true")
        parser.add_argument("--fail-if-waiting", action="store_true")

    def handle(self, *args, **options):
        roadmap = build_witness_parity_roadmap(_build_summary_from_settings())
        encoded = json.dumps(roadmap, ensure_ascii=False, indent=2)
        out = str(options.get("out") or "").strip()
        if out:
            output_path = Path(out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        else:
            self.stdout.write(encoded)

        totals = roadmap["totals"]
        if options.get("fail_if_review") and totals["review_count"]:
            raise CommandError(f"parity roadmap has {totals['review_count']} review domains")
        if options.get("fail_if_waiting") and totals["waiting_count"]:
            raise CommandError(f"parity roadmap has {totals['waiting_count']} waiting domains")


def _build_summary_from_settings():
    return build_witness_summary(
        jhora_report_path=_setting_path("JHORA_ACCURACY_REPORT_PATH", ".tmp/jhora/sterlitamak-1998/accuracy-report.json"),
        jhora_witness_case_path=_setting_path("JHORA_WITNESS_CASE_PATH"),
        witness_review_batch_index_path=_setting_path("WITNESS_REVIEW_BATCH_INDEX_PATH"),
        witness_capture_queue_path=_setting_path("WITNESS_CAPTURE_QUEUE_PATH"),
        witness_core_parity_report_path=_setting_path("WITNESS_CORE_PARITY_REPORT_PATH"),
        witness_varga_parity_report_path=_setting_path("WITNESS_VARGA_PARITY_REPORT_PATH"),
        witness_dasha_parity_report_path=_setting_path("WITNESS_DASHA_PARITY_REPORT_PATH"),
        witness_panchanga_parity_report_path=_setting_path("WITNESS_PANCHANGA_PARITY_REPORT_PATH"),
        witness_ashtakavarga_parity_report_path=_setting_path("WITNESS_ASHTAKAVARGA_PARITY_REPORT_PATH"),
        witness_strengths_parity_report_path=_setting_path("WITNESS_STRENGTHS_PARITY_REPORT_PATH"),
        witness_yoga_parity_report_path=_setting_path("WITNESS_YOGA_PARITY_REPORT_PATH"),
        witness_special_points_parity_report_path=_setting_path("WITNESS_SPECIAL_POINTS_PARITY_REPORT_PATH"),
        witness_argala_parity_report_path=_setting_path("WITNESS_ARGALA_PARITY_REPORT_PATH"),
        witness_avastha_parity_report_path=_setting_path("WITNESS_AVASTHA_PARITY_REPORT_PATH"),
        witness_drishti_parity_report_path=_setting_path("WITNESS_DRISHTI_PARITY_REPORT_PATH"),
        witness_transit_coordinate_parity_report_path=_setting_path("WITNESS_TRANSIT_COORDINATE_PARITY_REPORT_PATH"),
        witness_compatibility_parity_report_path=_setting_path("WITNESS_COMPATIBILITY_PARITY_REPORT_PATH"),
        witness_muhurta_parity_report_path=_setting_path("WITNESS_MUHURTA_PARITY_REPORT_PATH"),
        witness_tithi_pravesha_parity_report_path=_setting_path("WITNESS_TITHI_PRAVESHA_PARITY_REPORT_PATH"),
        witness_tajaka_parity_report_path=_setting_path("WITNESS_TAJAKA_PARITY_REPORT_PATH"),
        witness_prashna_parity_report_path=_setting_path("WITNESS_PRASHNA_PARITY_REPORT_PATH"),
        witness_jaimini_karaka_parity_report_path=_setting_path("WITNESS_JAIMINI_KARAKA_PARITY_REPORT_PATH"),
        witness_jaimini_varga_parity_report_path=_setting_path("WITNESS_JAIMINI_VARGA_PARITY_REPORT_PATH"),
        parashara_light_packet_path=_setting_path(
            "PARASHARA_LIGHT_PACKET_PATH",
            ".tmp/pl7/haridas-verification-packet/packet.json",
        ),
        parashara_light_manual_values_path=_setting_path("PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH"),
        parashara_light_profile_report_path=_setting_path("PARASHARA_LIGHT_PROFILE_REPORT_PATH"),
        parashara_light_forensic_report_path=_setting_path("PARASHARA_LIGHT_FORENSIC_REPORT_PATH"),
        parashara_light_settings_evidence_path=_setting_path("PARASHARA_LIGHT_SETTINGS_EVIDENCE_PATH"),
        parashara_light_visible_settings_capture_path=_setting_path("PARASHARA_LIGHT_VISIBLE_SETTINGS_CAPTURE_PATH"),
        parashara_light_calculation_options_report_path=_setting_path("PARASHARA_LIGHT_CALCULATION_OPTIONS_REPORT_PATH"),
        parashara_light_settings_aware_forensic_path=_setting_path("PARASHARA_LIGHT_SETTINGS_AWARE_FORENSIC_PATH"),
        parashara_light_preferences_inventory_path=_setting_path("PARASHARA_LIGHT_PREFERENCES_INVENTORY_PATH"),
        parashara_light_hidden_option_store_path=_setting_path("PARASHARA_LIGHT_HIDDEN_OPTION_STORE_PATH"),
        parashara_light_option_store_diff_path=_setting_path("PARASHARA_LIGHT_OPTION_STORE_DIFF_PATH"),
        parashara_light_internal_settings_audit_path=_setting_path("PARASHARA_LIGHT_INTERNAL_SETTINGS_AUDIT_PATH"),
    )


def _setting_path(name: str, fallback: str = ""):
    value = getattr(settings, name, "")
    if value:
        return value
    return settings.ROOT_DIR / fallback if fallback else ""
