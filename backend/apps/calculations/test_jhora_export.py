import pytest


JHORA_EXPORT_SNIPPET = """
Natal Chart

Date:          August 15, 1947
Time:          0:00:01
Time Zone:     5:30:00 (East of GMT)
Place:         77 E 13' 00", 28 N 40' 00"
               Delhi, India

Tithi:         Krishna Trayodasi (Ju) (0.09% left)
Vedic Weekday: Thursday (Ju)
Nakshatra:     Pushyami (Sa) (95.01% left)
Yoga:          Siddhi (Ma) (9.93% left)
Karana:        Vanija (Ve) (0.18% left)

Ayanamsa:      23-06-37.20

Body                    Longitude        Nakshatra Pada Rasi Navamsa

Lagna                    7 Ta 47' 06.60" Krit      4    Ta   Pi
Sun - AK                28 Cn 00' 35.16" Asre      4    Cn   Pi
Moon - DK                3 Cn 59' 56.63" Push      1    Cn   Le
Mars - GK                7 Ge 28' 43.15" Ardr      1    Ge   Sg
Maandi                   1 Cn 34' 16.57" Puna      4    Cn   Cn
Gulika                  21 Ge 13' 14.11" Puna      1    Ge   Ar
Hora Lagna              13 Sc 00' 35.05" Anu       3    Sc   Li

Ashtakavarga of Rasi Chart:

      Ar  Ta  Ge  Cn  Le  Vi  Li  Sc  Sg  Cp  Aq  Pi
As   6   4*  4   5   4   4   6   3   4   1   4   4
Su   6   4   4   4*  4   3   3   1   4   4   5   6

Planet  Shadbala In rupas % Strength IshtaPhala KashtaPhala

Sun     343.31   5.72     114.44     32.12      24.74
Moon    443.61   7.39     123.23     17.82      32.52

Vimsopaka Dasa Varga (10) Shodasa Varga (16) Sapta Varga (7) Shad Varga (6)

Sun       12.10  (60.50%) 12.93  (64.63%)    12.43  (62.13%) 14.40  (72.00%)
Moon      16.13  (80.63%) 14.38  (71.88%)    16.43  (82.13%) 15.10  (75.50%)
Rahu      9.50   (47.50%) 7.95   (39.75%)    11.68  (58.38%) 9.80   (49.00%)
Ketu      15.08  (75.38%) 14.90  (74.50%)    14.75  (73.75%) 16.15  (80.75%)

Vimsottari Dasa ():

Sat  Sat 1946-09-02  Merc 1949-09-05  Ket 1952-05-12
"""


def test_parse_jhora_complete_calculations_extracts_expected_values():
    try:
        from apps.calculations.jhora_export import parse_jhora_complete_calculations
    except ModuleNotFoundError:
        pytest.fail("JHora complete-calculations parser is not implemented yet")

    parsed = parse_jhora_complete_calculations(JHORA_EXPORT_SNIPPET)

    assert parsed["metadata"]["ayanamsa"] == "23-06-37.20"
    assert parsed["metadata"]["ayanamsa_degrees"] == pytest.approx(23.110333)
    assert parsed["expected"]["ascendant"]["rashi"] == "Vrishabha"
    assert parsed["expected"]["ascendant"]["longitude"] == pytest.approx(37.785167)
    assert parsed["expected"]["grahas"]["Surya"]["rashi"] == "Karka"
    assert parsed["expected"]["grahas"]["Surya"]["longitude"] == pytest.approx(118.009767)
    assert parsed["expected"]["grahas"]["Surya"]["nakshatra"] == "Ashlesha"
    assert parsed["expected"]["grahas"]["Surya"]["pada"] == 4
    assert parsed["expected"]["grahas"]["Chandra"]["rashi"] == "Karka"
    assert parsed["expected"]["panchanga"]["tithi"] == "Krishna Trayodasi"
    assert parsed["jhora_expected"]["ashtakavarga"]["Su"]["Karka"] == 4
    assert parsed["jhora_expected"]["shadbala"]["Sun"]["rupas"] == pytest.approx(5.72)
    assert parsed["jhora_expected"]["special_points"]["Gulika"]["rashi"] == "Mithuna"
    assert parsed["jhora_expected"]["special_points"]["Hora Lagna"]["longitude"] == pytest.approx(223.009736)
    assert parsed["jhora_expected"]["vimsopaka"]["Sun"]["dasa_varga"]["score"] == pytest.approx(12.10)
    assert parsed["jhora_expected"]["vimsopaka"]["Moon"]["shodasa_varga"]["percent"] == pytest.approx(71.88)
    assert parsed["jhora_expected"]["vimsopaka"]["Rahu"]["sapta_varga"]["score"] == pytest.approx(11.68)
    assert parsed["jhora_expected"]["vimsopaka"]["Ketu"]["shad_varga"]["percent"] == pytest.approx(80.75)
    assert parsed["jhora_expected"]["vimshottari_raw"][0].startswith("Sat  Sat 1946-09-02")


def test_parse_jhora_complete_calculations_extracts_ascii_varga_charts():
    from apps.calculations.jhora_export import parse_jhora_complete_calculations

    text = """
Natal Chart

+-----------------------------------------------+
|Ve         |Sa         |Su   Ma    |           |
|           |           |           |           |
|           |           |           |           |
|           |           |           |           |
|           |           |           |           |
|-----------+-----------------------+-----------|
|Me   GL    |                       |HL         |
|           |                       |           |
|           |                       |           |
|           |                       |           |
|           |                       |           |
|-----------|     Chaturthamsa      |-----------|
|Ju         |          D-4          |Mo   AL    |
|           |                       |           |
|           |                       |           |
|           |                       |           |
|           |                       |           |
|-----------+-----------------------+-----------|
|Ra   Ke    |Md         |As         |Gk         |
|           |           |           |           |
|           |           |           |           |
|           |           |           |           |
|           |           |           |           |
+-----------------------------------------------+
"""

    parsed = parse_jhora_complete_calculations(text)
    d4 = parsed["expected"]["vargas"]["D4"]

    assert d4["Surya"]["rashi"] == "Vrishabha"
    assert d4["Mangala"]["rashi_index"] == 1
    assert d4["Shukra"]["rashi"] == "Meena"
    assert d4["Chandra"]["rashi"] == "Simha"
    assert d4["Lagna"]["rashi"] == "Tula"
    assert d4["Rahu"]["rashi"] == "Dhanu"
    assert d4["Ketu"]["rashi"] == "Dhanu"
