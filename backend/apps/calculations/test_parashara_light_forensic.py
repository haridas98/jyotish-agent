import json

from django.core.management import call_command


def test_build_parashara_light_forensic_dump_compares_pl_witness_to_swiss(tmp_path):
    from apps.calculations.parashara_light_forensic import build_parashara_light_forensic_dump

    packet_path = tmp_path / "packet.json"
    manual_values_path = tmp_path / "manual-values.json"
    packet_path.write_text(
        json.dumps(
            {
                "jyotish_agent_chart": {
                    "birth": {"utc_datetime": "1998-04-30T07:45:00+00:00"},
                    "settings": {"ayanamsa": "lahiri"},
                    "grahas": [
                        {"body": "Surya", "longitude": 15.0},
                        {"body": "Chandra", "longitude": 20.0},
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    manual_values_path.write_text(
        json.dumps(
            [
                {"body": "Surya", "witness": {"rashi": "Mesha", "longitude_dms": "15:10:00"}},
                {"body": "Chandra", "witness": {"rashi": "Mesha", "longitude_dms": "20:00:00"}},
            ]
        ),
        encoding="utf-8",
    )

    report = build_parashara_light_forensic_dump(
        packet_path,
        manual_values_path,
        swiss_longitude_provider=lambda chart: {
            "Surya": {"sidereal": 15.0, "tropical": 38.0},
            "Chandra": {"sidereal": 20.0, "tropical": 43.0},
        },
    )

    assert report["summary"]["engine_swiss_max_abs_arcsec"] == 0
    assert report["summary"]["pl_diff_count"] == 1
    assert report["summary"]["conclusion"] == "engine_matches_swiss_pl_profile_diff_open"
    assert report["rows"][0]["body"] == "Surya"
    assert report["rows"][0]["pl_minus_engine_arcsec"] == 600.0
    assert report["rows"][1]["status"] == "matched"


def test_build_parashara_light_forensic_dump_rejects_uniform_offset_and_time_shift(tmp_path):
    from apps.calculations.parashara_light_forensic import build_parashara_light_forensic_dump

    packet_path = tmp_path / "packet.json"
    manual_values_path = tmp_path / "manual-values.json"
    packet_path.write_text(
        json.dumps(
            {
                "jyotish_agent_chart": {
                    "birth": {"utc_datetime": "1998-04-30T07:45:00+00:00"},
                    "settings": {"ayanamsa": "lahiri"},
                    "grahas": [
                        {"body": "Surya", "longitude": 10.0},
                        {"body": "Chandra", "longitude": 20.0},
                        {"body": "Budha", "longitude": 30.0},
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    manual_values_path.write_text(
        json.dumps(
            [
                {"body": "Surya", "witness": {"rashi": "Mesha", "longitude_dms": "10:06:40"}},
                {"body": "Chandra", "witness": {"rashi": "Mesha", "longitude_dms": "20:00:00"}},
                {"body": "Budha", "witness": {"rashi": "Vrishabha", "longitude_dms": "00:10:00"}},
            ]
        ),
        encoding="utf-8",
    )

    report = build_parashara_light_forensic_dump(
        packet_path,
        manual_values_path,
        swiss_longitude_provider=lambda chart: {
            "Surya": {"sidereal": 10.0, "tropical": 33.0, "sidereal_speed": 1.0},
            "Chandra": {"sidereal": 20.0, "tropical": 43.0, "sidereal_speed": 13.0},
            "Budha": {"sidereal": 30.0, "tropical": 53.0, "sidereal_speed": 0.5},
        },
    )

    diagnostics = report["diagnostics"]
    assert diagnostics["uniform_offset"]["status"] == "rejected"
    assert diagnostics["uniform_offset"]["max_residual_arcsec"] > 60
    assert diagnostics["time_shift"]["status"] == "rejected"
    assert diagnostics["time_shift"]["max_residual_arcsec"] > 60
    assert diagnostics["next_action"] == "capture_parashara_light_profile_settings"


def test_build_parashara_light_forensic_dump_command_writes_json(monkeypatch, tmp_path):
    packet_path = tmp_path / "packet.json"
    manual_values_path = tmp_path / "manual-values.json"
    output_path = tmp_path / "forensic.json"
    packet_path.write_text("{}", encoding="utf-8")
    manual_values_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_parashara_light_forensic_dump.build_parashara_light_forensic_dump",
        lambda packet, manual_values: {
            "source": "parashara_light_forensic_dump",
            "source_packet": str(packet),
            "manual_witness_source": str(manual_values),
            "summary": {"conclusion": "matched"},
            "rows": [],
        },
    )

    call_command(
        "build_parashara_light_forensic_dump",
        "--packet",
        str(packet_path),
        "--manual-witness-values",
        str(manual_values_path),
        "--output",
        str(output_path),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["source"] == "parashara_light_forensic_dump"
    assert payload["source_packet"] == str(packet_path)
