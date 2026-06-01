from __future__ import annotations

from math import floor

from .constants import RASHIS

SHODASHA_VARGA_CODES = (
    "D1",
    "D2",
    "D3",
    "D4",
    "D7",
    "D9",
    "D10",
    "D12",
    "D16",
    "D20",
    "D24",
    "D27",
    "D30",
    "D40",
    "D45",
    "D60",
)

VARGA_NAMES = {
    "D1": "Rashi",
    "D2": "Hora",
    "D3": "Drekkana",
    "D4": "Chaturthamsha",
    "D7": "Saptamsa",
    "D9": "Navamsa",
    "D10": "Dashamsa",
    "D12": "Dvadashamsha",
    "D16": "Shodashamsha",
    "D20": "Vimshamsha",
    "D24": "Siddhamsha",
    "D27": "Bhamsha",
    "D30": "Trimsamsha",
    "D40": "Khavedamsha",
    "D45": "Akshavedamsha",
    "D60": "Shashtyamsha",
}


def divisional_chart(
    longitudes: dict[str, float],
    ascendant_longitude: float | None = None,
    codes: tuple[str, ...] = SHODASHA_VARGA_CODES,
) -> dict[str, dict[str, object]]:
    charts = {}
    for code in codes:
        placements = []
        if ascendant_longitude is not None:
            placements.append(_placement("Lagna", ascendant_longitude, code))
        placements.extend(_placement(body, longitude, code) for body, longitude in longitudes.items())
        charts[code] = {
            "code": code,
            "name": VARGA_NAMES[code],
            "method": "Parashara shodasha varga rules; D16/D20/D24/D27/D40/D45 use standard cyclic starts pending JHora fixture audit",
            "placements": placements,
        }
    return charts


def divisional_placement(longitude: float, code: str) -> tuple[int, str]:
    normalized = longitude % 360.0
    sign_index = min(11, floor(normalized / 30.0))
    sign_degrees = normalized % 30.0

    if code == "D1":
        index = sign_index
    elif code == "D2":
        index = _hora(sign_index, sign_degrees)
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
        index = _cyclic_from_start(_elemental_start(sign_index), sign_degrees, 20)
    elif code == "D24":
        index = _cyclic_from_start(_odd_even_start(sign_index, odd_start=4, even_start=3), sign_degrees, 24)
    elif code == "D27":
        index = _cyclic_from_start(_elemental_start(sign_index), sign_degrees, 27)
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


def _placement(body: str, longitude: float, code: str) -> dict[str, object]:
    rashi_index, rashi = divisional_placement(longitude, code)
    return {"body": body, "rashi_index": rashi_index, "rashi": rashi}


def _hora(sign_index: int, sign_degrees: float) -> int:
    first_half = sign_degrees < 15.0
    if _is_odd_sign(sign_index):
        return 4 if first_half else 3
    return 3 if first_half else 4


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


def _odd_even_start(sign_index: int, odd_start: int, even_start: int) -> int:
    return odd_start if _is_odd_sign(sign_index) else even_start
