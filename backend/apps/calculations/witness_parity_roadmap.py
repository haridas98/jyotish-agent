from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "witness-parity-roadmap.v1"

PARITY_ROADMAP_DOMAINS: tuple[tuple[str, str], ...] = (
    ("witness_core_parity", "Core parity"),
    ("witness_varga_parity", "Varga parity"),
    ("witness_dasha_parity", "Dasha parity"),
    ("witness_panchanga_parity", "Panchanga parity"),
    ("witness_ashtakavarga_parity", "Ashtakavarga parity"),
    ("witness_strengths_parity", "Strengths parity"),
    ("witness_yoga_parity", "Yoga parity"),
    ("witness_special_points_parity", "Special points parity"),
    ("witness_argala_parity", "Argala parity"),
    ("witness_avastha_parity", "Avastha parity"),
    ("witness_drishti_parity", "Drishti parity"),
    ("witness_transit_coordinate_parity", "Transit coordinate parity"),
    ("witness_compatibility_parity", "Compatibility parity"),
    ("witness_muhurta_parity", "Muhurta parity"),
    ("witness_tithi_pravesha_parity", "Tithi Pravesha parity"),
    ("witness_tajaka_parity", "Tajaka parity"),
    ("witness_prashna_parity", "Prashna parity"),
    ("witness_jaimini_karaka_parity", "Jaimini karaka parity"),
    ("witness_jaimini_varga_parity", "Jaimini varga parity"),
)


def build_witness_parity_roadmap(summary: dict[str, Any]) -> dict[str, Any]:
    domains = [_domain_row(summary, key, label) for key, label in PARITY_ROADMAP_DOMAINS]
    return {
        "schema_version": SCHEMA_VERSION,
        "domains": domains,
        "totals": {
            "integrated_count": len(domains),
            "ready_count": sum(1 for row in domains if row["state"] == "ready"),
            "review_count": sum(1 for row in domains if row["state"] == "review"),
            "waiting_count": sum(1 for row in domains if row["state"] == "waiting"),
        },
    }


def _domain_row(summary: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    payload = summary.get(key)
    if not isinstance(payload, dict) or not payload.get("available"):
        return {
            "key": key,
            "label": label,
            "state": "waiting",
            "passed_count": 0,
            "target_reviewed_count": 0,
            "failed_count": 0,
            "blocker_count": 0,
            "skipped_count": 0,
            "readiness_gap_count": 0,
            "next_action": "collect report",
        }

    counts = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    passed_count = _safe_int(counts.get("passed_count"))
    target_reviewed_count = _safe_int(counts.get("target_reviewed_count"))
    failed_count = _safe_int(counts.get("failed_count"))
    blocker_count = (
        _safe_int(counts.get("missing_witness_count"))
        + _safe_int(counts.get("not_reviewed_count"))
        + _safe_int(counts.get("not_comparable_count"))
    )
    target_met = bool(payload.get("target_met") or counts.get("target_met"))
    state = "ready" if target_met and failed_count == 0 and blocker_count == 0 else "review"
    return {
        "key": key,
        "label": label,
        "state": state,
        "passed_count": passed_count,
        "target_reviewed_count": target_reviewed_count,
        "failed_count": failed_count,
        "blocker_count": blocker_count,
        "skipped_count": _skipped_count(payload),
        "readiness_gap_count": _readiness_gap_count(payload),
        "next_action": "ready for demo" if state == "ready" else "review witness rows",
    }


def _skipped_count(payload: dict[str, Any]) -> int:
    total = 0
    for key, value in payload.items():
        if key == "summary" or not key.endswith("_summary") or not isinstance(value, dict):
            continue
        for row in value.values():
            if isinstance(row, dict):
                total += _safe_int(row.get("skipped"))
    return total


def _readiness_gap_count(payload: dict[str, Any]) -> int:
    readiness = payload.get("readiness_summary")
    if not isinstance(readiness, dict):
        return 0
    total = 0
    for row in readiness.values():
        if isinstance(row, dict):
            total += _safe_int(row.get("actual_missing"))
    return total


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
