from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from typing import Protocol

from .primitives import ZodiacPlacement, julian_day, normalize_degrees, zodiac_placement


class EphemerisUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class CalculationSettings:
    zodiac: str = "sidereal"
    ayanamsa: str = "lahiri"
    node_type: str = "true"
    ephemeris: str = "swiss"

    def __post_init__(self) -> None:
        if self.zodiac != "sidereal":
            raise ValueError("Only sidereal zodiac is supported in the MVP")
        if self.ayanamsa != "lahiri":
            raise ValueError("Only Lahiri ayanamsa is supported in the MVP")
        if self.node_type not in {"true", "mean"}:
            raise ValueError("node_type must be true or mean")
        if self.ephemeris not in {"swiss", "jpl"}:
            raise ValueError("ephemeris must be swiss or jpl")


@dataclass(frozen=True)
class BodyPosition:
    body: str
    longitude: float
    latitude: float | None
    distance_au: float | None
    speed_longitude: float | None
    placement: ZodiacPlacement


class EphemerisProvider(Protocol):
    def planet_positions(
        self,
        moment: datetime,
        bodies: list[str],
        settings: CalculationSettings,
    ) -> dict[str, BodyPosition]:
        raise NotImplementedError


class SwissEphemerisProvider:
    supported_bodies = {
        "Surya": "SUN",
        "Chandra": "MOON",
        "Mangala": "MARS",
        "Budha": "MERCURY",
        "Guru": "JUPITER",
        "Shukra": "VENUS",
        "Shani": "SATURN",
        "Rahu": "TRUE_NODE",
        "Ketu": "TRUE_NODE",
    }

    def planet_positions(
        self,
        moment: datetime,
        bodies: list[str],
        settings: CalculationSettings,
    ) -> dict[str, BodyPosition]:
        swe = self._load_swisseph()
        self._apply_settings(swe, settings)
        jd = julian_day(moment)
        flags = self._calculation_flags(swe, settings)
        output: dict[str, BodyPosition] = {}

        for body in bodies:
            if body == "Ketu":
                rahu = output.get("Rahu") or self._calculate_body(swe, jd, "Rahu", flags, settings)
                output["Ketu"] = BodyPosition(
                    body="Ketu",
                    longitude=normalize_degrees(rahu.longitude + 180.0),
                    latitude=-rahu.latitude if rahu.latitude is not None else None,
                    distance_au=rahu.distance_au,
                    speed_longitude=rahu.speed_longitude,
                    placement=zodiac_placement(rahu.longitude + 180.0),
                )
                continue

            output[body] = self._calculate_body(swe, jd, body, flags, settings)

        return output

    def ascendant_position(
        self,
        moment: datetime,
        latitude: float,
        longitude: float,
        settings: CalculationSettings,
    ) -> BodyPosition:
        swe = self._load_swisseph()
        self._apply_settings(swe, settings)
        jd = julian_day(moment)
        _cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"W", swe.FLG_SIDEREAL)
        ascendant_longitude = normalize_degrees(float(ascmc[0]))
        return BodyPosition(
            body="Lagna",
            longitude=ascendant_longitude,
            latitude=None,
            distance_au=None,
            speed_longitude=None,
            placement=zodiac_placement(ascendant_longitude),
        )

    def _load_swisseph(self):
        try:
            return import_module("swisseph")
        except ImportError as exc:
            raise EphemerisUnavailable(
                "Swiss Ephemeris provider requires optional dependency pyswisseph. "
                "Install with: python -m pip install -e \".[swisseph]\". "
                "Review AGPL/commercial licensing before public service use."
            ) from exc

    def _apply_settings(self, swe, settings: CalculationSettings) -> None:
        if settings.ayanamsa == "lahiri":
            swe.set_sid_mode(swe.SIDM_LAHIRI)
        ephemeris_path = os.getenv("SWISSEPH_EPHE_PATH")
        if ephemeris_path and hasattr(swe, "set_ephe_path"):
            swe.set_ephe_path(ephemeris_path)
        if settings.ephemeris == "jpl":
            jpl_file = os.getenv("SWISSEPH_JPL_FILE")
            if not jpl_file:
                raise EphemerisUnavailable(
                    "JPL ephemeris requires SWISSEPH_JPL_FILE in backend .env, "
                    "for example de441.eph on SWISSEPH_EPHE_PATH."
                )
            if hasattr(swe, "set_jpl_file"):
                swe.set_jpl_file(jpl_file)

    def _calculation_flags(self, swe, settings: CalculationSettings) -> int:
        ephemeris_flag = swe.FLG_JPLEPH if settings.ephemeris == "jpl" else swe.FLG_SWIEPH
        return ephemeris_flag | swe.FLG_SPEED | swe.FLG_SIDEREAL

    def _calculate_body(
        self,
        swe,
        jd: float,
        body: str,
        flags: int,
        settings: CalculationSettings,
    ) -> BodyPosition:
        if body not in self.supported_bodies:
            raise ValueError(f"Unsupported body: {body}")

        constant_name = self.supported_bodies[body]
        if body in {"Rahu", "Ketu"} and settings.node_type == "mean":
            constant_name = "MEAN_NODE"

        body_id = getattr(swe, constant_name)
        try:
            values, _retflags = swe.calc_ut(jd, body_id, flags)
        except Exception as exc:
            raise EphemerisUnavailable(f"{settings.ephemeris} ephemeris calculation failed: {exc}") from exc
        longitude = normalize_degrees(float(values[0]))
        latitude = float(values[1]) if len(values) > 1 else None
        distance_au = float(values[2]) if len(values) > 2 else None
        speed_longitude = float(values[3]) if len(values) > 3 else None

        return BodyPosition(
            body=body,
            longitude=longitude,
            latitude=latitude,
            distance_au=distance_au,
            speed_longitude=speed_longitude,
            placement=zodiac_placement(longitude),
        )
