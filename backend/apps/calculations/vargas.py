from __future__ import annotations

from dataclasses import dataclass
from math import floor

from .constants import RASHIS

@dataclass(frozen=True)
class VargaMethod:
    code: str
    name: str
    divisions: int
    workbench_ready: bool = False
    method_id: str = "varga.parashara_shodasha.v1"
    method_version: str = "1"
    non_uniform: bool = False
    source_anchor: str = ""
    expert_only: bool = False
    time_accuracy_required: str = ""
    category: str = "main"


VARGA_METHOD_REGISTRY = {
    "D1": VargaMethod("D1", "Rashi", 1, True),
    "D2": VargaMethod("D2", "Hora", 2, True),
    "D3": VargaMethod("D3", "Drekkana", 3, True, category="family"),
    "D4": VargaMethod("D4", "Chaturthamsha", 4, True),
    "D7": VargaMethod("D7", "Saptamsa", 7, True, category="family"),
    "D9": VargaMethod("D9", "Navamsa", 9, True, category="family"),
    "D10": VargaMethod("D10", "Dashamsa", 10, True, category="professional"),
    "D12": VargaMethod("D12", "Dvadashamsha", 12, True, category="family"),
    "D16": VargaMethod("D16", "Shodashamsha", 16, True),
    "D20": VargaMethod("D20", "Vimshamsha", 20, True, category="spiritual"),
    "D24": VargaMethod("D24", "Siddhamsha", 24, True, category="spiritual"),
    "D27": VargaMethod("D27", "Bhamsha", 27),
    "D30": VargaMethod(
        "D30",
        "Trimsamsha",
        30,
        workbench_ready=True,
        method_id="varga.d30.parashara_unequal.v1",
        non_uniform=True,
        source_anchor="BPHS 6.27-28",
        expert_only=True,
        category="expert",
    ),
    "D40": VargaMethod("D40", "Khavedamsha", 40),
    "D45": VargaMethod("D45", "Akshavedamsha", 45),
    "D60": VargaMethod(
        "D60",
        "Shashtyamsha",
        60,
        workbench_ready=True,
        method_id="varga.d60.parashara_shashtyamsha.v1",
        source_anchor="JHora Sterlitamak 1998 D60 parity; BPHS Shashtyamsha source review pending",
        expert_only=True,
        time_accuracy_required="exact",
        category="expert",
    ),
}

SHODASHA_VARGA_CODES = tuple(VARGA_METHOD_REGISTRY)
VARGA_NAMES = {code: method.name for code, method in VARGA_METHOD_REGISTRY.items()}


def workbench_varga_codes() -> tuple[str, ...]:
    return tuple(code for code, method in VARGA_METHOD_REGISTRY.items() if method.workbench_ready)


def workbench_expert_varga_codes() -> tuple[str, ...]:
    return tuple(code for code, method in VARGA_METHOD_REGISTRY.items() if method.workbench_ready and method.expert_only)


def varga_first_last_cases(code: str) -> list[dict[str, object]]:
    _require_varga_method(code)
    cases = []
    for sign_index in range(12):
        start_longitude = sign_index * 30.0
        last_longitude = start_longitude + 29.999999
        cases.append(
            {
                "sign_index": sign_index,
                "start_longitude": start_longitude,
                "last_longitude": last_longitude,
                "expected_start": divisional_placement(start_longitude, code),
                "expected_last": divisional_placement(last_longitude, code),
            }
        )
    return cases


def varga_boundary_cases(code: str) -> list[dict[str, object]]:
    method = _require_varga_method(code)
    if code == "D30":
        return _d30_boundary_cases()
    if method.divisions <= 1:
        return []
    span = 30.0 / method.divisions
    cases = []
    for boundary in range(1, method.divisions):
        at_longitude = boundary * span
        before_longitude = at_longitude - 0.000001
        cases.append(
            {
                "boundary": boundary,
                "before_longitude": before_longitude,
                "at_longitude": at_longitude,
                "expected_before": divisional_placement(before_longitude, code),
                "expected_at": divisional_placement(at_longitude, code),
            }
        )
    return cases

def _d30_boundary_cases() -> list[dict[str, object]]:
    cases = []
    for sign_index in range(12):
        boundaries = (
            (5.0, 10.0, 18.0, 25.0)
            if _is_odd_sign(sign_index)
            else (5.0, 12.0, 20.0, 25.0)
        )
        sign_start = sign_index * 30.0
        for boundary_degree in boundaries:
            at_longitude = sign_start + boundary_degree
            before_longitude = at_longitude - 0.000001
            cases.append(
                {
                    "sign_index": sign_index,
                    "boundary_degree": boundary_degree,
                    "before_longitude": before_longitude,
                    "at_longitude": at_longitude,
                    "expected_before": divisional_placement(before_longitude, "D30"),
                    "expected_at": divisional_placement(at_longitude, "D30"),
                }
            )
    return cases

def _require_varga_method(code: str) -> VargaMethod:
    try:
        return VARGA_METHOD_REGISTRY[code]
    except KeyError as exc:
        raise ValueError(f"Unsupported varga code: {code}") from exc

def divisional_chart(
    longitudes: dict[str, float],
    ascendant_longitude: float | None = None,
    codes: tuple[str, ...] = SHODASHA_VARGA_CODES,
    scheme: str = "parashara",
    birth_time_accuracy: str = "exact",
) -> dict[str, dict[str, object]]:
    charts = {}
    for code in codes:
        if varga_accuracy_contract(code, birth_time_accuracy)["status"] == "blocked":
            continue
        placements = []
        if ascendant_longitude is not None:
            placements.append(_placement("Lagna", ascendant_longitude, code, scheme))
        placements.extend(_placement(body, longitude, code, scheme) for body, longitude in longitudes.items())
        charts[code] = {
            "code": code,
            "name": VARGA_NAMES[code],
            "method": _method_note(code, scheme),
            "methodId": _method_id(code, scheme),
            "methodVersion": _method_version(code, scheme),
            "calculationPreset": _normalize_scheme(scheme),
            "placements": placements,
        }
    return charts


def varga_accuracy_contract(code: str, birth_time_accuracy: str) -> dict[str, str]:
    method = _require_varga_method(code)
    actual = str(birth_time_accuracy or "unknown").strip().lower()
    required = method.time_accuracy_required
    status = "blocked" if required and actual != required else "usable"
    return {
        "scopeId": code,
        "status": status,
        "requiredBirthTimeAccuracy": required or "any",
        "actualBirthTimeAccuracy": actual,
        "reason": f"{code.lower()}_requires_{required}_birth_time" if required else "no_time_accuracy_restriction",
    }


def divisional_placement(longitude: float, code: str, scheme: str = "parashara") -> tuple[int, str]:
    normalized = longitude % 360.0
    sign_index = min(11, floor(normalized / 30.0))
    sign_degrees = normalized % 30.0
    scheme = _normalize_scheme(scheme)

    if code == "D1":
        index = sign_index
    elif code == "D2":
        index = _uma_shambhu_hora(sign_index, sign_degrees) if scheme == "jhora_uma_shambhu" else _hora(sign_index, sign_degrees)
    elif code == "D3":
        index = _cyclic_from_sign(sign_index, sign_degrees, 3, start_offset=0, step=4)
    elif code == "D4":
        index = _cyclic_from_sign(sign_index, sign_degrees, 4, start_offset=0, step=3)
    elif code == "D7":
        start = sign_index if _is_odd_sign(sign_index) else sign_index + 6
        index = _cyclic_from_start(start, sign_degrees, 7)
    elif code == "D9":
        index = _navamsa(sign_index, sign_degrees)
    elif code == "D10":
        start = sign_index if _is_odd_sign(sign_index) else sign_index + 8
        index = _cyclic_from_start(start, sign_degrees, 10)
    elif code == "D12":
        index = _cyclic_from_start(sign_index, sign_degrees, 12)
    elif code == "D16":
        index = _cyclic_from_start(_elemental_start(sign_index), sign_degrees, 16)
    elif code == "D20":
        index = _cyclic_from_start(_vimshamsha_start(sign_index), sign_degrees, 20)
    elif code == "D24":
        index = _cyclic_from_start(_odd_even_start(sign_index, odd_start=4, even_start=3), sign_degrees, 24)
    elif code == "D27":
        index = _cyclic_from_start(_bhamsha_start(sign_index), sign_degrees, 27)
    elif code == "D30":
        index = _trimsamsha(sign_index, sign_degrees)
    elif code == "D40":
        index = _cyclic_from_start(_odd_even_start(sign_index, odd_start=0, even_start=6), sign_degrees, 40)
    elif code == "D45":
        index = _cyclic_from_start(_elemental_start(sign_index), sign_degrees, 45)
    elif code == "D60":
        index = _cyclic_from_start(sign_index, sign_degrees, 60)
    else:
        raise ValueError(f"Unsupported varga code: {code}")

    index %= 12
    return index, RASHIS[index]


def _placement(body: str, longitude: float, code: str, scheme: str) -> dict[str, object]:
    rashi_index, rashi = divisional_placement(longitude, code, scheme)
    return {"body": body, "rashi_index": rashi_index, "rashi": rashi}


def _normalize_scheme(scheme: str) -> str:
    value = str(scheme or "parashara").strip().lower()
    if value == "parashara":
        return "parashara"
    if value in {"jhora", "jhora_v8", "jhora_uma_shambhu"}:
        return "jhora_uma_shambhu"
    raise ValueError(f"Unsupported varga scheme: {scheme}")


def _method_id(code: str, scheme: str) -> str:
    if code == "D2" and _normalize_scheme(scheme) == "jhora_uma_shambhu":
        return "varga.jhora_uma_shambhu_hora.v1"
    return _require_varga_method(code).method_id


def _method_version(code: str, scheme: str) -> str:
    return _require_varga_method(code).method_version


def _method_note(code: str, scheme: str) -> str:
    if code == "D30":
        return "BPHS 6.27-28 Parashara unequal Trimsamsha segments."
    if code == "D60":
        return "Parashara Shashtyamsha: 60 equal half-degree divisions; JHora Sterlitamak parity locked."
    if code == "D2" and _normalize_scheme(scheme) == "jhora_uma_shambhu":
        return "JHora D-2 (US): Uma-Shambhu Hora with two zodiac cycles and reversed even-sign halves."
    return "Parashara shodasha varga rules; D20 uses movable/fixed/dual starts and D27 uses elemental starts per JHora fixture audit."


def _hora(sign_index: int, sign_degrees: float) -> int:
    first_half = sign_degrees < 15.0
    if _is_odd_sign(sign_index):
        return 4 if first_half else 3
    return 3 if first_half else 4


def _uma_shambhu_hora(sign_index: int, sign_degrees: float) -> int:
    first_half = sign_degrees < 15.0
    if _is_odd_sign(sign_index):
        base = ((sign_index // 2) % 3) * 4
        return base if first_half else base + 1
    base = (((sign_index - 1) // 2) % 3) * 4 + 3
    return base if first_half else base - 1


def _navamsa(sign_index: int, sign_degrees: float) -> int:
    if sign_index in {0, 3, 6, 9}:
        start = sign_index
    elif sign_index in {1, 4, 7, 10}:
        start = sign_index + 8
    else:
        start = sign_index + 4
    return _cyclic_from_start(start, sign_degrees, 9)


def _trimsamsha(sign_index: int, sign_degrees: float) -> int:
    if _is_odd_sign(sign_index):
        spans = ((5, 0), (10, 10), (18, 8), (25, 2), (30, 6))
    else:
        spans = ((5, 1), (12, 5), (20, 11), (25, 9), (30, 7))
    for end_degree, rashi_index in spans:
        if sign_degrees < end_degree:
            return rashi_index
    return spans[-1][1]


def _cyclic_from_sign(
    sign_index: int,
    sign_degrees: float,
    division: int,
    start_offset: int,
    step: int,
) -> int:
    part = _part_index(sign_degrees, division)
    return sign_index + start_offset + (part * step)


def _cyclic_from_start(start_index: int, sign_degrees: float, division: int) -> int:
    return start_index + _part_index(sign_degrees, division)


def _part_index(sign_degrees: float, division: int) -> int:
    return min(division - 1, floor(sign_degrees / (30.0 / division)))


def _is_odd_sign(sign_index: int) -> bool:
    return sign_index % 2 == 0


def _elemental_start(sign_index: int) -> int:
    if sign_index in {0, 3, 6, 9}:
        return 0
    if sign_index in {1, 4, 7, 10}:
        return 4
    return 8


def _vimshamsha_start(sign_index: int) -> int:
    if sign_index in {0, 3, 6, 9}:
        return 0
    if sign_index in {1, 4, 7, 10}:
        return 8
    return 4


def _bhamsha_start(sign_index: int) -> int:
    if sign_index in {0, 4, 8}:
        return 0
    if sign_index in {1, 5, 9}:
        return 3
    if sign_index in {2, 6, 10}:
        return 6
    return 9


def _odd_even_start(sign_index: int, odd_start: int, even_start: int) -> int:
    return odd_start if _is_odd_sign(sign_index) else even_start
