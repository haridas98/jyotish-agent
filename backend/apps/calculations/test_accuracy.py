from apps.calculations.accuracy import angular_delta_arcseconds, compare_longitude


def test_angular_delta_uses_shortest_wraparound_path():
    assert angular_delta_arcseconds(359.999, 0.001) == 7.2


def test_compare_longitude_marks_pass_when_within_tolerance():
    result = compare_longitude(
        body="Surya",
        expected_degrees=30.0,
        actual_degrees=30.0001,
        tolerance_arcseconds=0.5,
    )

    assert result.passed is True
    assert result.delta_arcseconds == 0.36


def test_compare_longitude_marks_fail_when_outside_tolerance():
    result = compare_longitude(
        body="Chandra",
        expected_degrees=120.0,
        actual_degrees=120.01,
        tolerance_arcseconds=10,
    )

    assert result.passed is False
    assert result.delta_arcseconds == 36
