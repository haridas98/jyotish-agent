import pytest


def test_parse_jhd_text_extracts_birth_input_and_jhora_metadata():
    try:
        from apps.calculations.jhora_import import parse_jhd_text
    except ModuleNotFoundError:
        pytest.fail("JHora .jhd import helper is not implemented yet")

    parsed = parse_jhd_text(
        "\n".join(
            [
                "8",
                "15",
                "1947",
                "0.000167",
                "-5.300000",
                "-77.130000",
                "28.400000",
                "0.000000",
                "-5.500000",
                "-5.500000",
                "0",
                "105",
                "Delhi",
                "India",
            ]
        ),
        source_name="India.jhd",
    )

    assert parsed["source_name"] == "India.jhd"
    assert parsed["birth_date"] == "1947-08-15"
    assert parsed["birth_time"] == "00:00:01"
    assert parsed["place_name"] == "Delhi"
    assert parsed["country"] == "India"
    assert parsed["latitude"] == pytest.approx(28.666667)
    assert parsed["longitude"] == pytest.approx(77.216667)
    assert parsed["jhora_time_compact"] == "0.000167"
    assert parsed["jhora_time_decimal_hours"] == pytest.approx(1 / 3600)
    assert parsed["jhora_timezone_offset_hours"] == pytest.approx(5.5)
    assert parsed["timezone"] == "Asia/Kolkata"


def test_jhd_to_accuracy_fixture_keeps_expected_empty_until_manual_jhora_export():
    from apps.calculations.jhora_import import jhd_to_accuracy_fixture

    fixture = jhd_to_accuracy_fixture(
        "10\n2\n1869\n7.200000\n-4.392667\n-69.490000\n21.370000\n",
        source_name="Mahatma Gandhi.jhd",
    )

    assert fixture["id"] == "jhora-input-mahatma-gandhi"
    assert fixture["source"] == "jhora_sample_jhd"
    assert fixture["review_status"] == "draft"
    assert fixture["input"]["birth_date"] == "1869-10-02"
    assert fixture["input"]["birth_time"] == "07:20:00"
    assert fixture["input"]["place_name"] == "Mahatma Gandhi"
    assert fixture["input"]["latitude"] == pytest.approx(21.616667)
    assert fixture["input"]["longitude"] == pytest.approx(69.816667)
    assert fixture["jhora_metadata"]["version_required"] == "8.0"
    assert fixture["expected"] == {}


def test_jhd_to_accuracy_fixture_uses_source_name_when_place_line_is_unknown_or_numeric():
    from apps.calculations.jhora_import import jhd_to_accuracy_fixture

    unknown_place = jhd_to_accuracy_fixture(
        "10\n2\n1869\n7.200000\n-4.392667\n-69.490000\n21.370000\n0\n0\n0\n0\n0\nUnknown\nUnknown\n",
        source_name="Mahatma Gandhi.jhd",
    )
    numeric_place = jhd_to_accuracy_fixture(
        "8\n8\n1912\n19.3800\n-5.30\n-77.35\n12.59\n0.9\n112.9\n53.6\n141\n133\n222.9\n122\n",
        source_name="Prof. B. V. Raman.jhd",
    )

    assert unknown_place["id"] == "jhora-input-mahatma-gandhi"
    assert unknown_place["input"]["place_name"] == "Mahatma Gandhi"
    assert numeric_place["id"] == "jhora-input-prof-b-v-raman"
    assert numeric_place["input"]["place_name"] == "Prof. B. V. Raman"
