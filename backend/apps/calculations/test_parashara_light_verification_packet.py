import json

from django.core.management import call_command


class PacketProvider:
    def planet_positions(self, moment, bodies, settings):
        from apps.calculations.ephemeris import BodyPosition
        from apps.calculations.primitives import zodiac_placement

        return {
            "Surya": BodyPosition("Surya", 15.0, 0.0, 1.0, 1.0, zodiac_placement(15.0)),
            "Chandra": BodyPosition("Chandra", 68.0, 0.0, 1.0, 1.0, zodiac_placement(68.0)),
        }

    def ascendant_position(self, moment, latitude, longitude, settings):
        from apps.calculations.ephemeris import BodyPosition
        from apps.calculations.primitives import zodiac_placement

        return BodyPosition("Lagna", 115.0, None, None, None, zodiac_placement(115.0))


def test_build_parashara_light_verification_packet_keeps_pl_witness_draft():
    from apps.calculations.parashara_light_verification_packet import (
        build_parashara_light_verification_packet,
    )

    packet = build_parashara_light_verification_packet(
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45:00",
            "place_name": "Sterlitamak",
            "timezone": "Asia/Yekaterinburg",
            "timezone_offset": "+06:00",
            "latitude": 53.6304,
            "longitude": 55.9502,
            "calculation_model": "drik_siddhanta",
            "ayanamsa": "lahiri",
            "node_type": "true",
            "house_system": "whole_sign",
            "bhava_system": "whole_sign",
            "varga_scheme": "parashara",
            "timezone_source": "iana",
        },
        packet_id="pl7-sterlitamak-1998",
        pl_ui_state={
            "source": "parashara_light_ui_state",
            "backend": "uia",
            "window_title": "Parashara's Light 7.0.1 - [Haridas]",
            "captured_at": "2026-06-06T19:17:31Z",
            "control_count": 26,
            "artifact_policy": "private_audit_only_do_not_commit",
            "screenshot": "..\\.tmp\\pl7\\haridas-ui-state.png",
            "screenshot_blank": False,
            "class_summary": [{"control_type": "Pane", "class_name": "QWidget", "count": 20}],
        },
        pl_ui_state_path=".tmp/pl7/haridas-ui-state.json",
        screenshot_paths=[".tmp/pl7/haridas-ui-state.png"],
        manual_witness_values=[
            {"source": "pl7", "body": "Lagna", "rashi": "Karka", "house": 1},
            {"source": "pl7", "body": "Surya", "rashi": "Mesha", "house": 10},
        ],
        provider=PacketProvider(),
    )

    assert packet["schema_version"] == "jyotish-parashara-light-verification-packet-v1"
    assert packet["status"] == "pl_ui_state_captured"
    assert packet["fixture"]["review_status"] == "draft"
    assert packet["fixture"]["pl_metadata"]["profile_status"] == "unverified"
    assert packet["fixture"]["pl_metadata"]["window_title"].startswith("Parashara's Light")
    assert packet["fixture"]["pl_metadata"]["screenshot_blank"] is False
    assert packet["fixture"]["capture_files"]["screenshots"] == [".tmp/pl7/haridas-ui-state.png"]
    assert packet["fixture"]["pl_expected"]["ui_state"]["artifact_policy"] == "private_audit_only_do_not_commit"
    assert packet["fixture"]["manual_witness_values"][0]["body"] == "Lagna"
    assert packet["fixture"]["manual_witness_values"][1]["house"] == 10
    assert packet["jyotish_agent_chart"]["ascendant"]["rashi"] == "Karka"
    assert "PL settings" in packet["pl_capture_checklist"][-1]


def test_build_parashara_light_verification_packet_command_writes_packet_files(monkeypatch, tmp_path):
    ui_state_path = tmp_path / "pl-ui-state.json"
    manual_values_path = tmp_path / "manual-values.json"
    output_dir = tmp_path / "packet"
    ui_state_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_ui_state",
                "window_title": "Parashara's Light 7.0.1",
                "control_count": 26,
                "screenshot_blank": False,
            }
        ),
        encoding="utf-8",
    )
    manual_values_path.write_text(
        json.dumps([{"source": "pl7", "body": "Lagna", "rashi": "Karka"}]),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_parashara_light_verification_packet.build_parashara_light_verification_packet",
        lambda data, **kwargs: {
            "schema_version": "jyotish-parashara-light-verification-packet-v1",
            "id": kwargs["packet_id"],
            "status": "pl_ui_state_captured",
            "fixture": {
                "id": kwargs["packet_id"],
                "review_status": "draft",
                "pl_metadata": {"version_required": kwargs["pl_version"]},
                "manual_witness_values": kwargs["manual_witness_values"],
            },
            "jyotish_agent_chart": {"birth": {"date": data["birth_date"]}},
            "pl_capture_checklist": ["Capture PL settings"],
        },
    )

    call_command(
        "build_parashara_light_verification_packet",
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
        "--pl-ui-state",
        str(ui_state_path),
        "--screenshot",
        ".tmp/pl7/haridas-ui-state.png",
        "--manual-witness-values",
        str(manual_values_path),
        "--output-dir",
        str(output_dir),
    )

    fixture = json.loads((output_dir / "fixture.json").read_text(encoding="utf-8"))
    assert fixture["review_status"] == "draft"
    assert fixture["manual_witness_values"] == [{"source": "pl7", "body": "Lagna", "rashi": "Karka"}]
    assert (output_dir / "packet.json").exists()
    assert "Capture PL settings" in (output_dir / "pl-capture-checklist.md").read_text(encoding="utf-8")


def test_parashara_light_verification_packet_records_capture_file_fingerprints(tmp_path):
    from apps.calculations.parashara_light_verification_packet import (
        build_parashara_light_verification_packet,
    )

    ui_state = tmp_path / "ui-state.json"
    screenshot = tmp_path / "screen.png"
    ui_state.write_text('{"source":"parashara_light_ui_state"}', encoding="utf-8")
    screenshot.write_bytes(b"png")

    packet = build_parashara_light_verification_packet(
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45:00",
            "place_name": "Sterlitamak",
            "timezone": "Asia/Yekaterinburg",
            "latitude": 53.6304,
            "longitude": 55.9502,
        },
        pl_ui_state={"source": "parashara_light_ui_state"},
        pl_ui_state_path=str(ui_state),
        screenshot_paths=[str(screenshot)],
        provider=PacketProvider(),
    )

    fingerprints = packet["fixture"]["capture_files"]["fingerprints"]
    assert fingerprints["ui_state"]["sha256"]
    assert fingerprints["ui_state"]["bytes"] == len('{"source":"parashara_light_ui_state"}')
    assert fingerprints["screenshots"][0]["sha256"]
    assert fingerprints["screenshots"][0]["bytes"] == 3


def test_build_manual_witness_template_command_reads_packet_chart(tmp_path):
    packet_path = tmp_path / "packet.json"
    output_path = tmp_path / "manual-values-template.json"
    packet_path.write_text(
        json.dumps(
            {
                "jyotish_agent_chart": {
                    "ascendant": {
                        "body": "Lagna",
                        "longitude": 115.414369,
                        "rashi": "Karka",
                        "rashi_index": 3,
                        "nakshatra": "Ashlesha",
                        "pada": 3,
                    },
                    "grahas": [
                        {
                            "body": "Surya",
                            "longitude": 15.942392,
                            "rashi": "Mesha",
                            "rashi_index": 0,
                            "nakshatra": "Bharani",
                            "pada": 1,
                        }
                    ],
                    "houses": [
                        {"house": 1, "rashi": "Karka", "rashi_index": 3},
                        {"house": 10, "rashi": "Mesha", "rashi_index": 0},
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    call_command(
        "build_manual_witness_template",
        "--packet",
        str(packet_path),
        "--source",
        "pl7",
        "--output",
        str(output_path),
    )

    template = json.loads(output_path.read_text(encoding="utf-8"))
    assert template[0]["source"] == "pl7"
    assert template[0]["body"] == "Lagna"
    assert template[0]["witness"]["status"] == "pending"
    assert template[0]["calculated_reference"]["rashi"] == "Karka"
    assert template[1]["body"] == "Surya"
    assert template[1]["calculated_reference"]["house"] == 10
