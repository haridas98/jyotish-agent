from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management import call_command


BATCH_ARTIFACTS = {
    "core": {
        "command": "build_witness_core_parity_report",
        "path": ".tmp/witness-review/core-parity-report.json",
        "schema": "jyotish-core-parity-report-v1",
    },
    "varga": {
        "command": "build_witness_varga_parity_report",
        "path": ".tmp/witness-review/varga-parity-report.json",
        "schema": "jyotish-varga-parity-report-v1",
    },
    "dasha": {
        "command": "build_witness_dasha_parity_report",
        "path": ".tmp/witness-review/dasha-parity-report.json",
        "schema": "jyotish-dasha-parity-report-v1",
    },
    "panchanga": {
        "command": "build_witness_panchanga_parity_report",
        "path": ".tmp/witness-review/panchanga-parity-report.json",
        "schema": "jyotish-panchanga-parity-report-v1",
    },
    "ashtakavarga": {
        "command": "build_witness_ashtakavarga_parity_report",
        "path": ".tmp/witness-review/ashtakavarga-parity-report.json",
        "schema": "jyotish-ashtakavarga-parity-report-v1",
    },
    "special_points": {
        "command": "build_witness_special_points_parity_report",
        "path": ".tmp/witness-review/special-points-parity-report.json",
        "schema": "jyotish-special-points-parity-report-v1",
    },
    "argala": {
        "command": "build_witness_argala_parity_report",
        "path": ".tmp/witness-review/argala-parity-report.json",
        "schema": "jyotish-argala-parity-report-v1",
    },
    "avastha": {
        "command": "build_witness_avastha_parity_report",
        "path": ".tmp/witness-review/avastha-parity-report.json",
        "schema": "jyotish-avastha-parity-report-v1",
    },
    "drishti": {
        "command": "build_witness_drishti_parity_report",
        "path": ".tmp/witness-review/drishti-parity-report.json",
        "schema": "jyotish-drishti-parity-report-v1",
    },
    "transit_coordinates": {
        "command": "build_witness_transit_coordinates_parity_report",
        "path": ".tmp/witness-review/transit-coordinate-parity-report.json",
        "schema": "jyotish-transit-coordinate-parity-report-v1",
    },
    "compatibility": {
        "command": "build_witness_compatibility_parity_report",
        "path": ".tmp/witness-review/compatibility-parity-report.json",
        "schema": "jyotish-compatibility-parity-report-v1",
    },
    "muhurta": {
        "command": "build_witness_muhurta_parity_report",
        "path": ".tmp/witness-review/muhurta-parity-report.json",
        "schema": "jyotish-muhurta-parity-report-v1",
    },
    "tithi_pravesha": {
        "command": "build_witness_tithi_pravesha_parity_report",
        "path": ".tmp/witness-review/tithi-pravesha-parity-report.json",
        "schema": "jyotish-tithi-pravesha-parity-report-v1",
    },
    "tajaka": {
        "command": "build_witness_tajaka_parity_report",
        "path": ".tmp/witness-review/tajaka-parity-report.json",
        "schema": "jyotish-tajaka-parity-report-v1",
    },
    "prashna": {
        "command": "build_witness_prashna_parity_report",
        "path": ".tmp/witness-review/prashna-parity-report.json",
        "schema": "jyotish-prashna-parity-report-v1",
    },
    "strengths": {
        "command": "build_witness_strengths_parity_report",
        "path": ".tmp/witness-review/strengths-parity-report.json",
        "schema": "jyotish-strengths-parity-report-v1",
    },
    "yoga": {
        "command": "build_witness_yoga_parity_report",
        "path": ".tmp/witness-review/yoga-parity-report.json",
        "schema": "jyotish-yoga-parity-report-v1",
    },
    "jaimini_karaka": {
        "command": "build_witness_jaimini_karaka_parity_report",
        "path": ".tmp/witness-review/jaimini-karaka-parity-report.json",
        "schema": "jyotish-jaimini-karaka-parity-report-v1",
    },
    "jaimini_varga": {
        "command": "build_witness_jaimini_varga_parity_report",
        "path": ".tmp/witness-review/jaimini-varga-parity-report.json",
        "schema": "jyotish-jaimini-varga-parity-report-v1",
    },
}

FORBIDDEN_KEYS = {
    "source_report",
    "field_results",
    "expected",
    "actual",
    "sources_present",
}
FORBIDDEN_TEXT = [
    "source_report",
    "field_results",
    "expected",
    "actual",
    "sources_present",
    "seal_witness_case",
    "--ack-diff-open",
    "authority",
    "authoritative",
    "c:/users",
    "c:\\users",
    "c:/projects",
    "c:\\projects",
    ".env",
]
SUMMARY_NUMERIC_FIELDS = [
    "case_count",
    "comparable_count",
    "passed_count",
    "failed_count",
    "missing_witness_count",
    "not_reviewed_count",
    "not_comparable_count",
    "target_reviewed_count",
]
_REMOVED = object()


def test_p39_committed_artifacts_parse_have_schema_and_safe_summaries():
    for name, spec in BATCH_ARTIFACTS.items():
        report = _read_committed_artifact(spec["path"])

        assert report["schema_version"] == spec["schema"], name
        assert isinstance(report.get("summary"), dict), name
        for field in SUMMARY_NUMERIC_FIELDS:
            assert isinstance(report["summary"].get(field), int), f"{name}.{field}"
        assert isinstance(report["summary"].get("target_met"), bool), f"{name}.target_met"


def test_p39_committed_artifacts_strip_forbidden_keys_and_private_markers():
    for name, spec in BATCH_ARTIFACTS.items():
        report = _read_committed_artifact(spec["path"])

        assert not _contains_forbidden_key(report), name
        serialized = json.dumps(report, ensure_ascii=False).lower()
        assert [marker for marker in FORBIDDEN_TEXT if marker in serialized] == [], name


def test_p39_committed_artifacts_match_sanitized_second_generation(tmp_path):
    for name, spec in BATCH_ARTIFACTS.items():
        temp_output = tmp_path / f"{name}-parity-report.json"
        call_command(spec["command"], output=str(temp_output), markdown_output="")

        committed = _normalize_for_batch_comparison(_read_committed_artifact(spec["path"]))
        regenerated = _normalize_for_batch_comparison(json.loads(temp_output.read_text(encoding="utf-8")))
        assert committed == regenerated, name


def _read_committed_artifact(path: str) -> dict[str, Any]:
    report_path = Path(settings.ROOT_DIR) / path
    return json.loads(report_path.read_text(encoding="utf-8"))


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(key in FORBIDDEN_KEYS or _contains_forbidden_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _normalize_for_batch_comparison(report: dict[str, Any]) -> dict[str, Any]:
    normalized = _strip_raw_diagnostic_fields(report)
    metadata = normalized.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("generated_at", None)
        metadata.pop("jhora_root", None)
        metadata.pop("pl_root", None)
    return normalized


def _strip_raw_diagnostic_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): cleaned
            for key, item in value.items()
            if str(key) not in FORBIDDEN_KEYS and not _has_forbidden_text(str(key))
            for cleaned in [_strip_raw_diagnostic_fields(item)]
            if cleaned is not _REMOVED
        }
    if isinstance(value, list):
        cleaned_items = [_strip_raw_diagnostic_fields(item) for item in value]
        return [item for item in cleaned_items if item is not _REMOVED]
    if isinstance(value, str) and _has_forbidden_text(value):
        return _REMOVED
    return value


def _has_forbidden_text(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in FORBIDDEN_TEXT)
