from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TRANSIT_COORDINATE_SNAPSHOT_SCHEMA = "transit-coordinate-snapshot.v1"
TRANSIT_COORDINATE_METHOD_ID = "transit.coordinates.swiss_lahiri.v1"
TRANSIT_COORDINATE_METHOD_VERSION = "1"


def transit_coordinate_snapshot(chart: dict[str, Any]) -> dict[str, Any]:
    settings = chart.get("settings") if isinstance(chart.get("settings"), dict) else {}
    birth = chart.get("birth") if isinstance(chart.get("birth"), dict) else {}
    place = chart.get("place") if isinstance(chart.get("place"), dict) else {}
    ascendant = chart.get("ascendant") if isinstance(chart.get("ascendant"), dict) else None
    grahas = chart.get("grahas") if isinstance(chart.get("grahas"), list) else []
    return {
        "schemaVersion": TRANSIT_COORDINATE_SNAPSHOT_SCHEMA,
        "methodId": TRANSIT_COORDINATE_METHOD_ID,
        "methodVersion": TRANSIT_COORDINATE_METHOD_VERSION,
        "calculationPreset": str(settings.get("calculation_model") or "drik_siddhanta"),
        "ayanamshaId": str(settings.get("ayanamsa") or "lahiri"),
        "nodeType": str(settings.get("node_type") or "true"),
        "timezone": birth.get("timezone"),
        "localDateTime": birth.get("local_datetime"),
        "utcDateTime": birth.get("utc_datetime"),
        "location": {
            "latitude": _round_float(place.get("latitude")),
            "longitude": _round_float(place.get("longitude")),
        },
        "lagna": _placement_snapshot(ascendant) if ascendant else None,
        "grahas": [_placement_snapshot(item) for item in grahas if isinstance(item, dict)],
    }


def _placement_snapshot(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "body": item.get("body"),
        "longitude": _round_float(item.get("longitude")),
        "rashi": item.get("rashi"),
        "rashiIndex": item.get("rashi_index"),
        "nakshatra": item.get("nakshatra"),
        "nakshatraIndex": item.get("nakshatra_index"),
        "pada": item.get("pada"),
    }


def _round_float(value: Any) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def transit_coordinate_golden_metadata() -> dict[str, Any]:
    fixture_path = Path(__file__).parent / "fixtures" / "transit_coordinate_golden_v1.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    cases = payload.get("cases") if isinstance(payload.get("cases"), list) else []
    return {
        "schemaVersion": str(payload.get("schemaVersion") or "transit-coordinate-golden.v1"),
        "caseCount": len(cases),
        "caseIds": [str(case.get("id")) for case in cases if isinstance(case, dict)],
        "utcMoments": [
            str(case.get("expected", {}).get("utcDateTime"))
            for case in cases
            if isinstance(case, dict) and isinstance(case.get("expected"), dict)
        ],
        "timezoneIds": [
            str(case.get("expected", {}).get("timezone"))
            for case in cases
            if isinstance(case, dict) and isinstance(case.get("expected"), dict)
        ],
        "independentOfBuildBirthChart": True,
        "generator": str(payload.get("generator") or "direct provider fixture"),
    }
