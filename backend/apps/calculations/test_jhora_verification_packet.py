import json

from django.core.management import call_command


JHORA_EXPORT_SNIPPET = """
Natal Chart

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
"""


class PacketProvider:
    def planet_positions(self, moment, bodies, settings):
        from apps.calculations.ephemeris import BodyPosition
        from apps.calculations.primitives import zodiac_placement

        return {
            "Surya": BodyPosition("Surya", 118.009767, 0.0, 1.0, 1.0, zodiac_placement(118.009767)),
            "Chandra": BodyPosition("Chandra", 93.999064, 0.0, 1.0, 1.0, zodiac_placement(93.999064)),
        }

    def ascendant_position(self, moment, latitude, longitude, settings):
        from apps.calculations.ephemeris import BodyPosition
        from apps.calculations.primitives import zodiac_placement

        return BodyPosition("Lagna", 37.785167, None, None, None, zodiac_placement(37.785167))


def test_build_jhora_verification_packet_parses_export_without_marking_verified():
    from apps.calculations.jhora_verification_packet import build_jhora_verification_packet

    packet = build_jhora_verification_packet(
        {
            "birth_date": "1947-08-15",
            "birth_time": "00:00:01",
            "place_name": "Delhi",
            "timezone": "Asia/Kolkata",
            "latitude": 28.666667,
            "longitude": 77.216667,
            "calculation_model": "drik_siddhanta",
            "node_type": "mean",
            "ayanamsa": "lahiri",
        },
        packet_id="jhora-delhi-1947",
        jhora_export_text=JHORA_EXPORT_SNIPPET,
        screenshot_paths=[".tmp/jhora/main.png"],
        provider=PacketProvider(),
    )

    assert packet["schema_version"] == "jyotish-jhora-verification-packet-v1"
    assert packet["status"] == "jhora_export_parsed"
    assert packet["fixture"]["review_status"] == "draft"
    assert packet["fixture"]["jhora_metadata"]["profile_status"] == "unverified"
    assert packet["fixture"]["jhora_metadata"]["ayanamsa"] == "23-06-37.20"
    assert packet["fixture"]["expected"]["ascendant"]["rashi"] == "Vrishabha"
    assert packet["fixture"]["capture_files"]["screenshots"] == [".tmp/jhora/main.png"]
    assert packet["dual_calculation"]["status"] == "calculated_witness_mode"
    assert packet["parity_suite"]["case_count"] >= 20
    assert "modern_exact_timezone" in packet["parity_suite"]["groups"]


def test_build_jhora_verification_packet_command_writes_packet_files(monkeypatch, tmp_path):
    export_path = tmp_path / "jhora-export.txt"
    output_dir = tmp_path / "packet"
    export_path.write_text(JHORA_EXPORT_SNIPPET, encoding="utf-8")

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_jhora_verification_packet.build_jhora_verification_packet",
        lambda data, **kwargs: {
            "schema_version": "jyotish-jhora-verification-packet-v1",
            "id": kwargs["packet_id"],
            "status": "jhora_export_parsed",
            "fixture": {
                "id": kwargs["packet_id"],
                "review_status": "draft",
                "expected": {"ascendant": {"rashi": "Vrishabha"}},
                "jhora_metadata": {"version_required": kwargs["jhora_version"]},
            },
            "jyotish_agent_chart": {"birth": {"date": data["birth_date"]}},
            "dual_calculation": {"status": "calculated_witness_mode"},
            "jhora_capture_checklist": ["Capture settings"],
        },
    )

    call_command(
        "build_jhora_verification_packet",
        "--birth-date",
        "1998-04-30",
        "--birth-time",
        "13:45:00",
        "--place-name",
        "Sterlitamak",
        "--timezone",
        "Asia/Yekaterinburg",
        "--timezone-offset",
        "+06:00",
        "--latitude",
        "53.6304",
        "--longitude",
        "55.9502",
        "--jhora-export",
        str(export_path),
        "--output-dir",
        str(output_dir),
    )

    fixture = json.loads((output_dir / "fixture.json").read_text(encoding="utf-8"))
    assert fixture["review_status"] == "draft"
    assert fixture["expected"]["ascendant"]["rashi"] == "Vrishabha"
    assert (output_dir / "packet.json").exists()
    assert "Capture settings" in (output_dir / "jhora-capture-checklist.md").read_text(encoding="utf-8")


def test_jhora_parity_suite_manifest_has_required_case_mix():
    from apps.calculations.jhora_parity_suite import jhora_parity_suite_manifest

    manifest = jhora_parity_suite_manifest()

    assert manifest["schema_version"] == "jyotish-jhora-parity-suite-v1"
    assert manifest["case_count"] >= 20
    assert manifest["groups"]["modern_exact_timezone"]["count"] >= 4
    assert manifest["groups"]["dst_sensitive"]["count"] >= 4
    assert manifest["groups"]["boundary_sensitive"]["count"] >= 4
    assert manifest["groups"]["historical"]["count"] >= 4
    assert manifest["capture_policy"]["required_artifacts"] == [
        "jhora_complete_calculations_text",
        "settings_screenshots",
        "main_chart_screenshots",
        "strength_tables",
    ]


def test_build_jhora_witness_batch_packets_command_writes_selected_cases(monkeypatch, tmp_path):
    output_root = tmp_path / "batch"
    captured = []

    def fake_build(data, **kwargs):
        captured.append((data, kwargs))
        return {
            "schema_version": "jyotish-jhora-verification-packet-v1",
            "id": kwargs["packet_id"],
            "status": "capture_pending",
            "fixture": {
                "id": kwargs["packet_id"],
                "review_status": "draft",
                "jhora_metadata": {"version_required": kwargs["jhora_version"]},
            },
            "jyotish_agent_chart": {"birth": {"date": data["birth_date"]}},
            "dual_calculation": {"status": "calculated_witness_mode"},
            "jhora_capture_checklist": ["Capture settings"],
        }

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_jhora_witness_batch_packets.build_jhora_verification_packet",
        fake_build,
    )

    call_command(
        "build_jhora_witness_batch_packets",
        "--case-id",
        "sterlitamak-1998-04-30-1345",
        "--output-root",
        str(output_root),
    )

    assert captured[0][0]["birth_date"] == "1998-04-30"
    assert captured[0][0]["ayanamsa"] == "lahiri"
    assert (output_root / "sterlitamak-1998-04-30-1345" / "packet.json").exists()
    fixture = json.loads(
        (output_root / "sterlitamak-1998-04-30-1345" / "fixture.json").read_text(encoding="utf-8")
    )
    assert fixture["review_status"] == "draft"


def test_build_jhora_witness_batch_packets_uses_existing_complete_export(monkeypatch, tmp_path):
    output_root = tmp_path / "batch"
    case_dir = output_root / "sterlitamak-1998-04-30-1345"
    case_dir.mkdir(parents=True)
    export_path = case_dir / "jhora-complete-calculations.txt"
    export_path.write_text(JHORA_EXPORT_SNIPPET, encoding="utf-8")
    captured = []

    def fake_build(data, **kwargs):
        captured.append((data, kwargs))
        return {
            "schema_version": "jyotish-jhora-verification-packet-v1",
            "id": kwargs["packet_id"],
            "status": "jhora_export_parsed",
            "fixture": {
                "id": kwargs["packet_id"],
                "review_status": "draft",
                "capture_files": {"complete_calculations_text": kwargs["jhora_export_path"]},
                "jhora_metadata": {"capture_status": "export_parsed"},
            },
            "jyotish_agent_chart": {"birth": {"date": data["birth_date"]}},
            "dual_calculation": {"status": "calculated_witness_mode"},
            "jhora_capture_checklist": ["Capture settings"],
        }

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_jhora_witness_batch_packets.build_jhora_verification_packet",
        fake_build,
    )

    call_command(
        "build_jhora_witness_batch_packets",
        "--case-id",
        "sterlitamak-1998-04-30-1345",
        "--output-root",
        str(output_root),
    )

    assert captured[0][1]["jhora_export_text"] == JHORA_EXPORT_SNIPPET
    assert captured[0][1]["jhora_export_path"] == str(export_path)
    packet = json.loads((case_dir / "packet.json").read_text(encoding="utf-8"))
    assert packet["status"] == "jhora_export_parsed"


def test_build_jhora_witness_batch_packets_uses_existing_ui_table_dump(monkeypatch, tmp_path):
    output_root = tmp_path / "batch"
    case_dir = output_root / "sterlitamak-1998-04-30-1345"
    case_dir.mkdir(parents=True)
    ui_path = case_dir / "jhora-ui-tables.json"
    ui_payload = {
        "source": "jhora_win32_listviews",
        "tables": [{"index": 4, "row_count": 7}],
        "identified": {"shadbala_totals": {"rows": [["Sun", "682.72"]]}},
    }
    ui_path.write_text(json.dumps(ui_payload), encoding="utf-8")
    captured = []

    def fake_build(data, **kwargs):
        captured.append((data, kwargs))
        return {
            "schema_version": "jyotish-jhora-verification-packet-v1",
            "id": kwargs["packet_id"],
            "status": "capture_pending",
            "fixture": {
                "id": kwargs["packet_id"],
                "review_status": "draft",
                "capture_files": {"ui_table_dump": kwargs["jhora_ui_table_dump_path"]},
                "jhora_metadata": {"capture_status": "export_pending"},
                "jhora_expected": {"ui_tables": kwargs["jhora_ui_table_dump"]},
            },
            "jyotish_agent_chart": {"birth": {"date": data["birth_date"]}},
            "dual_calculation": {"status": "calculated_witness_mode"},
            "jhora_capture_checklist": ["Capture settings"],
        }

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_jhora_witness_batch_packets.build_jhora_verification_packet",
        fake_build,
    )

    call_command(
        "build_jhora_witness_batch_packets",
        "--case-id",
        "sterlitamak-1998-04-30-1345",
        "--output-root",
        str(output_root),
    )

    assert captured[0][1]["jhora_ui_table_dump"] == ui_payload
    assert captured[0][1]["jhora_ui_table_dump_path"] == str(ui_path)
    fixture = json.loads((case_dir / "fixture.json").read_text(encoding="utf-8"))
    assert fixture["jhora_expected"]["ui_tables"]["identified"]["shadbala_totals"]


def test_build_jhora_witness_batch_packets_uses_existing_screenshots(monkeypatch, tmp_path):
    output_root = tmp_path / "batch"
    case_dir = output_root / "sterlitamak-1998-04-30-1345"
    screenshot_dir = case_dir / "screenshots"
    screenshot_dir.mkdir(parents=True)
    first = screenshot_dir / "Снимок экрана 2026-06-07 131214.png"
    second = screenshot_dir / "menu expanded.jpg"
    first.write_bytes(b"png")
    second.write_bytes(b"jpg")
    captured = []

    def fake_build(data, **kwargs):
        captured.append((data, kwargs))
        return {
            "schema_version": "jyotish-jhora-verification-packet-v1",
            "id": kwargs["packet_id"],
            "status": "capture_pending",
            "fixture": {
                "id": kwargs["packet_id"],
                "review_status": "draft",
                "capture_files": {"screenshots": kwargs["screenshot_paths"]},
                "jhora_metadata": {"capture_status": "export_pending"},
            },
            "jyotish_agent_chart": {"birth": {"date": data["birth_date"]}},
            "dual_calculation": {"status": "calculated_witness_mode"},
            "jhora_capture_checklist": ["Capture settings"],
        }

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_jhora_witness_batch_packets.build_jhora_verification_packet",
        fake_build,
    )

    call_command(
        "build_jhora_witness_batch_packets",
        "--case-id",
        "sterlitamak-1998-04-30-1345",
        "--output-root",
        str(output_root),
    )

    assert captured[0][1]["screenshot_paths"] == [str(second), str(first)]
    fixture = json.loads((case_dir / "fixture.json").read_text(encoding="utf-8"))
    assert fixture["capture_files"]["screenshots"] == [str(second), str(first)]
