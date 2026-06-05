from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from typing import Protocol

from .primitives import ZodiacPlacement, julian_day, normalize_degrees, zodiac_placement


class EphemerisUnavailable(RuntimeError):
    pass


CHESHTA_ORBITAL_BODY_CONSTANTS = {
    "Mangala": "MARS",
    "Budha": "MERCURY",
    "Guru": "JUPITER",
    "Shukra": "VENUS",
    "Shani": "SATURN",
}
CHESHTA_OUTER_BODIES = {"Mangala", "Guru", "Shani"}
CHESHTA_INNER_BODIES = {"Budha", "Shukra"}


@dataclass(frozen=True)
class CalculationSettings:
    zodiac: str = "sidereal"
    calculation_model: str = "drik_siddhanta"
    ayanamsa: str = "lahiri"
    node_type: str = "true"
    ephemeris: str = "swiss"
    house_system: str = "whole_sign"
    bhava_system: str = "whole_sign"
    varga_scheme: str = "parashara"
    sunrise_source: str = "noaa"
    timezone_source: str = "iana"
    shadbala_profile: str = "bphs_classical"

    def __post_init__(self) -> None:
        if self.zodiac != "sidereal":
            raise ValueError("Only sidereal zodiac is supported in the MVP")
        if self.calculation_model == "surya_siddhanta":
            raise ValueError("surya_siddhanta calculation model is tracked but is not implemented yet")
        if self.calculation_model != "drik_siddhanta":
            raise ValueError("calculation_model must be drik_siddhanta")
        if self.ayanamsa != "lahiri":
            raise ValueError("Only Lahiri ayanamsa is supported in the MVP")
        if self.node_type not in {"true", "mean"}:
            raise ValueError("node_type must be true or mean")
        if self.ephemeris not in {"swiss", "jpl"}:
            raise ValueError("ephemeris must be swiss or jpl")
        if self.house_system != "whole_sign":
            raise ValueError("house_system must be whole_sign")
        if self.bhava_system != "whole_sign":
            raise ValueError("bhava_system must be whole_sign")
        if self.varga_scheme not in {"parashara", "jhora_uma_shambhu"}:
            raise ValueError("varga_scheme must be parashara or jhora_uma_shambhu")
        if self.sunrise_source not in {"noaa", "swiss_center_no_refraction"}:
            raise ValueError("sunrise_source must be noaa or swiss_center_no_refraction")
        if self.timezone_source not in {"iana", "fixed_offset", "manual_offset", "user_supplied_or_jhora_ui"}:
            raise ValueError("timezone_source must be iana, fixed_offset, manual_offset, or user_supplied_or_jhora_ui")
        if self.shadbala_profile != "bphs_classical":
            raise ValueError("shadbala_profile must be bphs_classical")


@dataclass(frozen=True)
class BodyPosition:
    body: str
    longitude: float
    latitude: float | None
    distance_au: float | None
    speed_longitude: float | None
    placement: ZodiacPlacement
    mean_longitude: float | None = None
    seeghrocha_longitude: float | None = None
    declination: float | None = None
    ephemeris_engine: str | None = None
    ephemeris_flags: int | None = None


class EphemerisProvider(Protocol):
    def planet_positions(
        self,
        moment: datetime,
        bodies: list[str],
        settings: CalculationSettings,
    ) -> dict[str, BodyPosition]:
        raise NotImplementedError

    def ayanamsa_degrees(self, moment: datetime, settings: CalculationSettings) -> float | None:
        raise NotImplementedError

    def house_cusps(
        self,
        moment: datetime,
        latitude: float,
        longitude: float,
        settings: CalculationSettings,
    ) -> list[dict[str, float | int | str]]:
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
                    mean_longitude=(
                        normalize_degrees(rahu.mean_longitude + 180.0)
                        if rahu.mean_longitude is not None
                        else None
                    ),
                    declination=-rahu.declination if rahu.declination is not None else None,
                    ephemeris_engine=rahu.ephemeris_engine,
                    ephemeris_flags=rahu.ephemeris_flags,
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

    def house_cusps(
        self,
        moment: datetime,
        latitude: float,
        longitude: float,
        settings: CalculationSettings,
    ) -> list[dict[str, float | int | str]]:
        swe = self._load_swisseph()
        self._apply_settings(swe, settings)
        jd = julian_day(moment)
        cusps, _ascmc = swe.houses_ex(jd, latitude, longitude, b"W", swe.FLG_SIDEREAL)
        output = []
        for index, longitude_value in enumerate(cusps[:12], start=1):
            placement = zodiac_placement(float(longitude_value))
            output.append(
                {
                    "house": index,
                    "longitude": normalize_degrees(float(longitude_value)),
                    "rashi": placement.rashi,
                    "rashi_index": placement.rashi_index,
                }
            )
        return output

    def ayanamsa_degrees(self, moment: datetime, settings: CalculationSettings) -> float:
        swe = self._load_swisseph()
        self._apply_settings(swe, settings)
        return round(float(swe.get_ayanamsa_ut(julian_day(moment))), 9)

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
            values, retflags = swe.calc_ut(jd, body_id, flags)
        except Exception as exc:
            raise EphemerisUnavailable(f"{settings.ephemeris} ephemeris calculation failed: {exc}") from exc
        longitude = normalize_degrees(float(values[0]))
        latitude = float(values[1]) if len(values) > 1 else None
        distance_au = float(values[2]) if len(values) > 2 else None
        speed_longitude = float(values[3]) if len(values) > 3 else None
        declination = self._equatorial_declination(swe, jd, body_id, settings)
        chesta_longitudes = self._chesta_orbital_longitudes(swe, jd, body, settings)

        return BodyPosition(
            body=body,
            longitude=longitude,
            latitude=latitude,
            distance_au=distance_au,
            speed_longitude=speed_longitude,
            placement=zodiac_placement(longitude),
            mean_longitude=chesta_longitudes[0] if chesta_longitudes else None,
            seeghrocha_longitude=chesta_longitudes[1] if chesta_longitudes else None,
            declination=declination,
            ephemeris_engine=_ephemeris_engine(swe, int(retflags)),
            ephemeris_flags=int(retflags),
        )

    def _equatorial_declination(self, swe, jd: float, body_id: int, settings: CalculationSettings) -> float | None:
        if not hasattr(swe, "FLG_EQUATORIAL"):
            return None
        ephemeris_flag = swe.FLG_JPLEPH if settings.ephemeris == "jpl" else swe.FLG_SWIEPH
        flags = ephemeris_flag | swe.FLG_SPEED | swe.FLG_EQUATORIAL
        try:
            values, _retflags = swe.calc_ut(jd, body_id, flags)
        except Exception:
            return None
        return float(values[1]) if len(values) > 1 else None

    def _chesta_orbital_longitudes(
        self,
        swe,
        jd_ut: float,
        body: str,
        settings: CalculationSettings,
    ) -> tuple[float, float] | None:
        if body not in CHESHTA_ORBITAL_BODY_CONSTANTS:
            return None
        planet_constant = getattr(swe, CHESHTA_ORBITAL_BODY_CONSTANTS[body], None)
        earth_constant = getattr(swe, "EARTH", None)
        if planet_constant is None or earth_constant is None or not hasattr(swe, "get_orbital_elements"):
            return None
        flags = self._orbital_element_flags(swe, settings)
        ayanamsa = float(swe.get_ayanamsa_ut(jd_ut))
        try:
            earth_mean = self._orbital_mean_longitude_tropical(swe, jd_ut, earth_constant, flags)
            sun_mean = normalize_degrees(earth_mean + 180.0 - ayanamsa)
            planet_mean = normalize_degrees(
                self._orbital_mean_longitude_tropical(swe, jd_ut, planet_constant, flags) - ayanamsa
            )
        except Exception:
            return None
        if body in CHESHTA_OUTER_BODIES:
            return planet_mean, sun_mean
        if body in CHESHTA_INNER_BODIES:
            return sun_mean, planet_mean
        return None

    def _orbital_element_flags(self, swe, settings: CalculationSettings) -> int:
        ephemeris_flag = swe.FLG_JPLEPH if settings.ephemeris == "jpl" else swe.FLG_SWIEPH
        return ephemeris_flag | getattr(swe, "FLG_HELCTR", 0)

    def _orbital_mean_longitude_tropical(self, swe, jd_ut: float, body_id: int, flags: int) -> float:
        jd_et = jd_ut + float(swe.deltat(jd_ut)) if hasattr(swe, "deltat") else jd_ut
        elements = swe.get_orbital_elements(jd_et, body_id, flags)
        return normalize_degrees(float(elements[9]))


def _ephemeris_engine(swe, retflags: int) -> str:
    if retflags & getattr(swe, "FLG_JPLEPH", 0):
        return "jpl"
    if retflags & getattr(swe, "FLG_SWIEPH", 0):
        return "swiss"
    if retflags & getattr(swe, "FLG_MOSEPH", 0):
        return "moshier"
    return "unknown"
