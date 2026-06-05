from apps.calculations.vargas import divisional_chart, divisional_placement


def test_parashara_shodasha_varga_codes_are_generated():
    chart = divisional_chart(
        {"Surya": 15.0, "Chandra": 47.0},
        ascendant_longitude=90.0,
    )

    assert set(chart) == {
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
    }
    assert chart["D9"]["placements"][0] == {"body": "Lagna", "rashi_index": 3, "rashi": "Karka"}


def test_varga_core_parashara_rules():
    assert divisional_placement(15.0, "D1") == (0, "Mesha")
    assert divisional_placement(14.0, "D2") == (4, "Simha")
    assert divisional_placement(20.0, "D3") == (8, "Dhanu")
    assert divisional_placement(8.0, "D4") == (3, "Karka")
    assert divisional_placement(29.0, "D7") == (6, "Tula")
    assert divisional_placement(30.0, "D9") == (9, "Makara")
    assert divisional_placement(27.0, "D10") == (9, "Makara")
    assert divisional_placement(17.0, "D12") == (6, "Tula")
    assert divisional_placement(2.0, "D30") == (0, "Mesha")
    assert divisional_placement(7.0, "D30") == (10, "Kumbha")
    assert divisional_placement(1.0, "D60") == (2, "Mithuna")


def test_even_sign_d30_reverses_trimsamsa_sequence():
    assert divisional_placement(31.0, "D30") == (1, "Vrishabha")
    assert divisional_placement(37.0, "D30") == (5, "Kanya")
    assert divisional_placement(45.0, "D30") == (11, "Meena")


def test_jhora_uma_shambhu_hora_uses_two_cycles_and_even_sign_reversal():
    assert divisional_placement(14.0, "D2", scheme="jhora_uma_shambhu") == (0, "Mesha")
    assert divisional_placement(16.0, "D2", scheme="jhora_uma_shambhu") == (1, "Vrishabha")
    assert divisional_placement(31.0, "D2", scheme="jhora_uma_shambhu") == (3, "Karka")
    assert divisional_placement(46.0, "D2", scheme="jhora_uma_shambhu") == (2, "Mithuna")

    assert divisional_placement(15.96, "D2", scheme="jhora_uma_shambhu") == (1, "Vrishabha")
    assert divisional_placement(133.59, "D2", scheme="jhora_uma_shambhu") == (8, "Dhanu")


def test_d20_uses_jhora_parashara_movable_fixed_dual_starts():
    assert divisional_placement(325.573663, "D20") == (1, "Vrishabha")
    assert divisional_placement(68.368149, "D20") == (9, "Makara")
    assert divisional_placement(133.574927, "D20") == (5, "Kanya")


def test_d27_uses_elemental_fire_earth_air_water_starts():
    assert divisional_placement(115.401188, "D27") == (7, "Vrischika")
    assert divisional_placement(133.574927, "D27") == (0, "Mesha")
    assert divisional_placement(349.859617, "D27") == (2, "Mithuna")
