from apps.calculations import vargas as varga_module
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
        "D30",
    )
    assert VARGA_METHOD_REGISTRY["D30"].workbench_ready
    assert VARGA_METHOD_REGISTRY["D30"].expert_only
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


def test_d30_method_registry_is_non_uniform_and_source_anchored():
    method = VARGA_METHOD_REGISTRY["D30"]

    assert method.method_id == "varga.d30.parashara_unequal.v1"
    assert method.method_version == "1"
    assert method.non_uniform is True
    assert method.source_anchor == "BPHS 6.27-28"
    assert method.workbench_ready is True
    assert method.expert_only is True


def test_d30_chart_contract_uses_parashara_unequal_method():
    chart = divisional_chart({"Surya": 5.0}, ascendant_longitude=4.999999, codes=("D30",))

    assert chart["D30"]["methodId"] == "varga.d30.parashara_unequal.v1"
    assert chart["D30"]["methodVersion"] == "1"
    assert chart["D30"]["calculationPreset"] == "parashara"


def test_d30_uses_unequal_boundaries_with_start_inclusive_end_exclusive_policy():
    odd_cases = [
        (0.0, (0, "Mesha")),
        (4.999999, (0, "Mesha")),
        (5.0, (10, "Kumbha")),
        (9.999999, (10, "Kumbha")),
        (10.0, (8, "Dhanu")),
        (17.999999, (8, "Dhanu")),
        (18.0, (2, "Mithuna")),
        (24.999999, (2, "Mithuna")),
        (25.0, (6, "Tula")),
        (29.999999, (6, "Tula")),
        (30.0, (1, "Vrishabha")),
    ]
    for longitude, expected in odd_cases:
        assert divisional_placement(longitude, "D30") == expected

    even_cases = [
        (30.0, (1, "Vrishabha")),
        (34.999999, (1, "Vrishabha")),
        (35.0, (5, "Kanya")),
        (41.999999, (5, "Kanya")),
        (42.0, (11, "Meena")),
        (49.999999, (11, "Meena")),
        (50.0, (9, "Makara")),
        (54.999999, (9, "Makara")),
        (55.0, (7, "Vrischika")),
        (59.999999, (7, "Vrischika")),
        (60.0, (0, "Mesha")),
    ]
    for longitude, expected in even_cases:
        assert divisional_placement(longitude, "D30") == expected


def test_d30_boundary_cases_are_not_generated_as_equal_thirtieths():
    cases = varga_boundary_cases("D30")
    first_two_signs = [(case["sign_index"], case["boundary_degree"]) for case in cases[:8]]

    assert first_two_signs == [
        (0, 5.0),
        (0, 10.0),
        (0, 18.0),
        (0, 25.0),
        (1, 5.0),
        (1, 12.0),
        (1, 20.0),
        (1, 25.0),
    ]
    assert len(cases) == 48


def test_d30_chart_snapshot_keeps_lagna_and_nine_grahas_order():
    chart = divisional_chart(
        {
            "Surya": 5.0,
            "Chandra": 10.0,
            "Mangala": 18.0,
            "Budha": 25.0,
            "Guru": 34.999999,
            "Shukra": 35.0,
            "Shani": 42.0,
            "Rahu": 50.0,
            "Ketu": 55.0,
        },
        ascendant_longitude=4.999999,
        codes=("D30",),
    )

    assert {"scopeId": "D30", **chart["D30"]} == {
        "scopeId": "D30",
        "code": "D30",
        "name": "Trimsamsha",
        "method": "BPHS 6.27-28 Parashara unequal Trimsamsha segments.",
        "methodId": "varga.d30.parashara_unequal.v1",
        "methodVersion": "1",
        "calculationPreset": "parashara",
        "placements": [
            {"body": "Lagna", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Surya", "rashi_index": 10, "rashi": "Kumbha"},
            {"body": "Chandra", "rashi_index": 8, "rashi": "Dhanu"},
            {"body": "Mangala", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Budha", "rashi_index": 6, "rashi": "Tula"},
            {"body": "Guru", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Shukra", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Shani", "rashi_index": 11, "rashi": "Meena"},
            {"body": "Rahu", "rashi_index": 9, "rashi": "Makara"},
            {"body": "Ketu", "rashi_index": 7, "rashi": "Vrischika"},
        ],
    }

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

def test_d60_method_registry_is_time_sensitive_and_hidden_from_workbench():
    method = VARGA_METHOD_REGISTRY["D60"]

    assert method.method_id == "varga.d60.parashara_shashtyamsha.v1"
    assert method.method_version == "1"
    assert method.source_anchor == "JHora Sterlitamak 1998 D60 parity; BPHS Shashtyamsha source review pending"
    assert method.time_accuracy_required == "exact"
    assert method.workbench_ready is False
    assert "D60" not in workbench_varga_codes()


def test_d60_boundary_policy_half_degree_start_inclusive_end_exclusive():
    cases = [
        (0.0, (0, "Mesha")),
        (0.499999, (0, "Mesha")),
        (0.5, (1, "Vrishabha")),
        (1.0, (2, "Mithuna")),
        (29.999999, (11, "Meena")),
        (30.0, (1, "Vrishabha")),
        (30.499999, (1, "Vrishabha")),
        (30.5, (2, "Mithuna")),
        (359.999999, (10, "Kumbha")),
    ]
    for longitude, expected in cases:
        assert divisional_placement(longitude, "D60") == expected


def test_d60_boundary_cases_cover_half_degree_segments_without_ui_exposure():
    cases = varga_boundary_cases("D60")

    assert cases[0] == {
        "boundary": 1,
        "before_longitude": 0.499999,
        "at_longitude": 0.5,
        "expected_before": (0, "Mesha"),
        "expected_at": (1, "Vrishabha"),
    }
    assert len(cases) == 59


def test_d60_chart_snapshot_keeps_lagna_and_nine_grahas_order():
    chart = divisional_chart(
        {
            "Surya": 0.5,
            "Chandra": 1.0,
            "Mangala": 1.5,
            "Budha": 2.0,
            "Guru": 2.5,
            "Shukra": 3.0,
            "Shani": 3.5,
            "Rahu": 4.0,
            "Ketu": 4.5,
        },
        ascendant_longitude=0.0,
        codes=("D60",),
        birth_time_accuracy="exact",
    )

    assert {"scopeId": "D60", **chart["D60"]} == {
        "scopeId": "D60",
        "code": "D60",
        "name": "Shashtyamsha",
        "method": "Parashara Shashtyamsha: 60 equal half-degree divisions; JHora Sterlitamak parity locked.",
        "methodId": "varga.d60.parashara_shashtyamsha.v1",
        "methodVersion": "1",
        "calculationPreset": "parashara",
        "placements": [
            {"body": "Lagna", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Surya", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Chandra", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Mangala", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Budha", "rashi_index": 4, "rashi": "Simha"},
            {"body": "Guru", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Shukra", "rashi_index": 6, "rashi": "Tula"},
            {"body": "Shani", "rashi_index": 7, "rashi": "Vrischika"},
            {"body": "Rahu", "rashi_index": 8, "rashi": "Dhanu"},
            {"body": "Ketu", "rashi_index": 9, "rashi": "Makara"},
        ],
    }


def test_d60_accuracy_contract_blocks_inexact_birth_time():
    assert varga_module.varga_accuracy_contract("D60", "exact") == {
        "scopeId": "D60",
        "status": "usable",
        "requiredBirthTimeAccuracy": "exact",
        "actualBirthTimeAccuracy": "exact",
        "reason": "d60_requires_exact_birth_time",
    }
    assert varga_module.varga_accuracy_contract("D60", "approximate") == {
        "scopeId": "D60",
        "status": "blocked",
        "requiredBirthTimeAccuracy": "exact",
        "actualBirthTimeAccuracy": "approximate",
        "reason": "d60_requires_exact_birth_time",
    }
    assert divisional_chart({"Surya": 0.5}, ascendant_longitude=0.0, codes=("D60",), birth_time_accuracy="approximate") == {}
    assert divisional_chart({"Surya": 0.5}, ascendant_longitude=0.0, codes=("D60",), birth_time_accuracy="unknown") == {}
