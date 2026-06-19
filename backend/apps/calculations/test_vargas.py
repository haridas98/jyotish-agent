from apps.calculations.vargas import (
    VARGA_METHOD_REGISTRY,
    divisional_chart,
    divisional_placement,
    varga_boundary_cases,
    varga_first_last_cases,
    workbench_varga_codes,
)


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
    assert chart["D2"]["methodId"] == "varga.parashara_shodasha.v1"
    assert chart["D2"]["methodVersion"] == "1"
    assert chart["D2"]["calculationPreset"] == "parashara"


def test_varga_method_contract_changes_with_explicit_scheme():
    chart = divisional_chart({"Surya": 15.0}, codes=("D2",), scheme="jhora_uma_shambhu")

    assert chart["D2"]["methodId"] == "varga.jhora_uma_shambhu_hora.v1"
    assert chart["D2"]["methodVersion"] == "1"
    assert chart["D2"]["calculationPreset"] == "jhora_uma_shambhu"


def test_unknown_varga_scheme_is_rejected_not_silently_replaced():
    try:
        divisional_chart({"Surya": 15.0}, codes=("D2",), scheme="unknown_method")
    except ValueError as exc:
        assert "Unsupported varga scheme" in str(exc)
    else:
        raise AssertionError("unknown varga scheme must fail")


def test_varga_method_registry_marks_workbench_ready_scopes():
    assert workbench_varga_codes() == (
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
    )
    assert not VARGA_METHOD_REGISTRY["D30"].workbench_ready
    assert not VARGA_METHOD_REGISTRY["D60"].workbench_ready


def test_varga_first_last_generator_matches_divisional_placement():
    for code in ("D2", "D4", "D16", "D20", "D24"):
        cases = varga_first_last_cases(code)
        assert len(cases) == 12
        for case in cases:
            assert divisional_placement(case["start_longitude"], code) == case["expected_start"]
            assert divisional_placement(case["last_longitude"], code) == case["expected_last"]


def test_varga_boundary_generator_matches_divisional_placement():
    for code in ("D2", "D4", "D16", "D20", "D24"):
        cases = varga_boundary_cases(code)
        assert cases
        for case in cases:
            assert divisional_placement(case["before_longitude"], code) == case["expected_before"]
            assert divisional_placement(case["at_longitude"], code) == case["expected_at"]


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


def test_d9_navamsa_golden_first_and_last_parts_for_all_rashis():
    expected_starts = [
        (0, "Mesha"),
        (9, "Makara"),
        (6, "Tula"),
        (3, "Karka"),
        (0, "Mesha"),
        (9, "Makara"),
        (6, "Tula"),
        (3, "Karka"),
        (0, "Mesha"),
        (9, "Makara"),
        (6, "Tula"),
        (3, "Karka"),
    ]
    for sign_index, expected_start in enumerate(expected_starts):
        sign_start = sign_index * 30.0
        assert divisional_placement(sign_start, "D9") == expected_start
        expected_last_index = (expected_start[0] + 8) % 12
        expected_last = (expected_last_index, [
            "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
            "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
        ][expected_last_index])
        assert divisional_placement(sign_start + 29.999999, "D9") == expected_last


def test_d9_navamsa_golden_boundary_degrees_do_not_drift():
    one_navamsa = 30.0 / 9.0
    assert divisional_placement(one_navamsa - 0.000001, "D9") == (0, "Mesha")
    assert divisional_placement(one_navamsa, "D9") == (1, "Vrishabha")
    assert divisional_placement((2 * one_navamsa) - 0.000001, "D9") == (1, "Vrishabha")
    assert divisional_placement(2 * one_navamsa, "D9") == (2, "Mithuna")
    assert divisional_placement(30.0 - 0.000001, "D9") == (8, "Dhanu")
    assert divisional_placement(30.0, "D9") == (9, "Makara")


def test_d9_chart_snapshot_keeps_lagna_and_graha_order():
    chart = divisional_chart(
        {"Surya": 15.942392, "Chandra": 68.368149, "Mangala": 18.9547},
        ascendant_longitude=115.401188,
        codes=("D9",),
    )

    assert chart["D9"] == {
        "code": "D9",
        "name": "Navamsa",
        "method": "Parashara shodasha varga rules; D20 uses movable/fixed/dual starts and D27 uses elemental starts per JHora fixture audit.",
        "methodId": "varga.parashara_shodasha.v1",
        "methodVersion": "1",
        "calculationPreset": "parashara",
        "placements": [
            {"body": "Lagna", "rashi_index": 10, "rashi": "Kumbha"},
            {"body": "Surya", "rashi_index": 4, "rashi": "Simha"},
            {"body": "Chandra", "rashi_index": 8, "rashi": "Dhanu"},
            {"body": "Mangala", "rashi_index": 5, "rashi": "Kanya"},
        ],
    }


def test_d10_dashamsa_golden_first_and_last_parts_for_all_rashis():
    rashi_names = [
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
    ]
    expected_starts = [
        (0, "Mesha"),
        (9, "Makara"),
        (2, "Mithuna"),
        (11, "Meena"),
        (4, "Simha"),
        (1, "Vrishabha"),
        (6, "Tula"),
        (3, "Karka"),
        (8, "Dhanu"),
        (5, "Kanya"),
        (10, "Kumbha"),
        (7, "Vrischika"),
    ]
    for sign_index, expected_start in enumerate(expected_starts):
        sign_start = sign_index * 30.0
        assert divisional_placement(sign_start, "D10") == expected_start
        expected_last_index = (expected_start[0] + 9) % 12
        assert divisional_placement(sign_start + 29.999999, "D10") == (expected_last_index, rashi_names[expected_last_index])


def test_d10_dashamsa_golden_boundary_degrees_do_not_drift():
    one_dashamsa = 30.0 / 10.0
    assert divisional_placement(one_dashamsa - 0.000001, "D10") == (0, "Mesha")
    assert divisional_placement(one_dashamsa, "D10") == (1, "Vrishabha")
    assert divisional_placement((2 * one_dashamsa) - 0.000001, "D10") == (1, "Vrishabha")
    assert divisional_placement(2 * one_dashamsa, "D10") == (2, "Mithuna")
    assert divisional_placement(30.0 - 0.000001, "D10") == (9, "Makara")
    assert divisional_placement(30.0, "D10") == (9, "Makara")


def test_d10_chart_snapshot_keeps_lagna_and_graha_order():
    chart = divisional_chart(
        {"Surya": 15.942392, "Chandra": 68.368149, "Mangala": 18.9547},
        ascendant_longitude=115.401188,
        codes=("D10",),
    )

    assert chart["D10"] == {
        "code": "D10",
        "name": "Dashamsa",
        "method": "Parashara shodasha varga rules; D20 uses movable/fixed/dual starts and D27 uses elemental starts per JHora fixture audit.",
        "methodId": "varga.parashara_shodasha.v1",
        "methodVersion": "1",
        "calculationPreset": "parashara",
        "placements": [
            {"body": "Lagna", "rashi_index": 7, "rashi": "Vrischika"},
            {"body": "Surya", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Chandra", "rashi_index": 4, "rashi": "Simha"},
            {"body": "Mangala", "rashi_index": 6, "rashi": "Tula"},
        ],
    }


def test_d12_dvadashamsha_golden_first_and_last_parts_for_all_rashis():
    rashi_names = [
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
    ]
    for sign_index, sign_name in enumerate(rashi_names):
        sign_start = sign_index * 30.0
        assert divisional_placement(sign_start, "D12") == (sign_index, sign_name)
        expected_last_index = (sign_index + 11) % 12
        assert divisional_placement(sign_start + 29.999999, "D12") == (expected_last_index, rashi_names[expected_last_index])


def test_d12_dvadashamsha_golden_boundary_degrees_do_not_drift():
    one_dvadashamsha = 30.0 / 12.0
    assert divisional_placement(one_dvadashamsha - 0.000001, "D12") == (0, "Mesha")
    assert divisional_placement(one_dvadashamsha, "D12") == (1, "Vrishabha")
    assert divisional_placement((2 * one_dvadashamsha) - 0.000001, "D12") == (1, "Vrishabha")
    assert divisional_placement(2 * one_dvadashamsha, "D12") == (2, "Mithuna")
    assert divisional_placement(30.0 - 0.000001, "D12") == (11, "Meena")
    assert divisional_placement(30.0, "D12") == (1, "Vrishabha")


def test_d12_chart_snapshot_keeps_lagna_and_graha_order():
    chart = divisional_chart(
        {"Surya": 15.942392, "Chandra": 68.368149, "Mangala": 18.9547},
        ascendant_longitude=115.401188,
        codes=("D12",),
    )

    assert chart["D12"] == {
        "code": "D12",
        "name": "Dvadashamsha",
        "method": "Parashara shodasha varga rules; D20 uses movable/fixed/dual starts and D27 uses elemental starts per JHora fixture audit.",
        "methodId": "varga.parashara_shodasha.v1",
        "methodVersion": "1",
        "calculationPreset": "parashara",
        "placements": [
            {"body": "Lagna", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Surya", "rashi_index": 6, "rashi": "Tula"},
            {"body": "Chandra", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Mangala", "rashi_index": 7, "rashi": "Vrischika"},
        ],
    }


def test_d3_drekkana_golden_first_and_last_parts_for_all_rashis():
    rashi_names = [
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
    ]
    for sign_index, sign_name in enumerate(rashi_names):
        sign_start = sign_index * 30.0
        assert divisional_placement(sign_start, "D3") == (sign_index, sign_name)
        expected_last_index = (sign_index + 8) % 12
        assert divisional_placement(sign_start + 29.999999, "D3") == (expected_last_index, rashi_names[expected_last_index])


def test_d3_drekkana_golden_boundary_degrees_do_not_drift():
    one_drekkana = 30.0 / 3.0
    assert divisional_placement(one_drekkana - 0.000001, "D3") == (0, "Mesha")
    assert divisional_placement(one_drekkana, "D3") == (4, "Simha")
    assert divisional_placement((2 * one_drekkana) - 0.000001, "D3") == (4, "Simha")
    assert divisional_placement(2 * one_drekkana, "D3") == (8, "Dhanu")
    assert divisional_placement(30.0 - 0.000001, "D3") == (8, "Dhanu")
    assert divisional_placement(30.0, "D3") == (1, "Vrishabha")


def test_d3_chart_snapshot_keeps_lagna_and_graha_order():
    chart = divisional_chart(
        {"Surya": 15.942392, "Chandra": 68.368149, "Mangala": 18.9547},
        ascendant_longitude=115.401188,
        codes=("D3",),
    )

    assert chart["D3"] == {
        "code": "D3",
        "name": "Drekkana",
        "method": "Parashara shodasha varga rules; D20 uses movable/fixed/dual starts and D27 uses elemental starts per JHora fixture audit.",
        "methodId": "varga.parashara_shodasha.v1",
        "methodVersion": "1",
        "calculationPreset": "parashara",
        "placements": [
            {"body": "Lagna", "rashi_index": 11, "rashi": "Meena"},
            {"body": "Surya", "rashi_index": 4, "rashi": "Simha"},
            {"body": "Chandra", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Mangala", "rashi_index": 4, "rashi": "Simha"},
        ],
    }


def test_d7_saptamsa_golden_first_and_last_parts_for_all_rashis():
    rashi_names = [
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
    ]
    expected_starts = [
        (0, "Mesha"),
        (7, "Vrischika"),
        (2, "Mithuna"),
        (9, "Makara"),
        (4, "Simha"),
        (11, "Meena"),
        (6, "Tula"),
        (1, "Vrishabha"),
        (8, "Dhanu"),
        (3, "Karka"),
        (10, "Kumbha"),
        (5, "Kanya"),
    ]
    for sign_index, expected_start in enumerate(expected_starts):
        sign_start = sign_index * 30.0
        assert divisional_placement(sign_start, "D7") == expected_start
        expected_last_index = (expected_start[0] + 6) % 12
        assert divisional_placement(sign_start + 29.999999, "D7") == (expected_last_index, rashi_names[expected_last_index])


def test_d7_saptamsa_golden_boundary_degrees_do_not_drift():
    one_saptamsa = 30.0 / 7.0
    assert divisional_placement(one_saptamsa - 0.000001, "D7") == (0, "Mesha")
    assert divisional_placement(one_saptamsa, "D7") == (1, "Vrishabha")
    assert divisional_placement((2 * one_saptamsa) - 0.000001, "D7") == (1, "Vrishabha")
    assert divisional_placement(2 * one_saptamsa, "D7") == (2, "Mithuna")
    assert divisional_placement(30.0 - 0.000001, "D7") == (6, "Tula")
    assert divisional_placement(30.0, "D7") == (7, "Vrischika")


def test_d7_chart_snapshot_keeps_lagna_and_graha_order():
    chart = divisional_chart(
        {"Surya": 15.942392, "Chandra": 68.368149, "Mangala": 18.9547},
        ascendant_longitude=115.401188,
        codes=("D7",),
    )

    assert chart["D7"] == {
        "code": "D7",
        "name": "Saptamsa",
        "method": "Parashara shodasha varga rules; D20 uses movable/fixed/dual starts and D27 uses elemental starts per JHora fixture audit.",
        "methodId": "varga.parashara_shodasha.v1",
        "methodVersion": "1",
        "calculationPreset": "parashara",
        "placements": [
            {"body": "Lagna", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Surya", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Chandra", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Mangala", "rashi_index": 4, "rashi": "Simha"},
        ],
    }
