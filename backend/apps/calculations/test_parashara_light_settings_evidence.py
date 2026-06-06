import json

from django.core.management import call_command


def test_build_parashara_light_settings_evidence_hashes_private_artifacts_without_parsing(tmp_path):
    from apps.calculations.parashara_light_settings_evidence import build_parashara_light_settings_evidence

    chart_xml = tmp_path / "Haridas.xml"
    chart_xml.write_text(
        """<?xml version="1.0" encoding="UTF-16"?><BirthData>
 <BirthInfo><FirstName>Haridas</FirstName><Longitude>-55.9666667</Longitude><Latitude>53.6166667</Latitude><TimeZone>-5</TimeZone><DST>1</DST></BirthInfo>
</BirthData>""",
        encoding="utf-16",
    )
    options_dir = tmp_path / "GeoVisionOptions"
    options_dir.mkdir()
    (options_dir / "popts1.dat").write_bytes(b"\x00binary proprietary ayanamsa Lahiri text must stay hidden")
    (options_dir / "history.bin").write_bytes(b"\x01\x02history")
    pl7_dir = tmp_path / "PL7"
    (pl7_dir / "Bin").mkdir(parents=True)
    (pl7_dir / "Bin" / "paths.txt").write_text("charts=C:\\GeoVision\\GeoVisionCharts", encoding="utf-8")
    (pl7_dir / "Temp").mkdir()
    (pl7_dir / "Temp" / "20501.e31").write_bytes(b"\x00opaque session ayanamsa Lahiri")

    report = build_parashara_light_settings_evidence(
        chart_xml=chart_xml,
        options_dir=options_dir,
        pl7_dir=pl7_dir,
    )

    assert report["source"] == "parashara_light_settings_evidence"
    assert report["artifact_policy"] == "private_audit_only_do_not_commit"
    assert report["proprietary_binary_policy"] == "hash_only_do_not_parse"
    assert report["birth_profile"]["subject"]["first_name"] == "Haridas"
    option_entry = next(item for item in report["options_manifest"] if item["relative_path"] == "popts1.dat")
    assert option_entry["sha256"]
    assert option_entry["classification"] == "proprietary_option_hash_only"
    assert "content_preview" not in option_entry
    text_entry = next(item for item in report["text_artifacts"] if item["relative_path"] == "Bin/paths.txt")
    assert "GeoVisionCharts" in text_entry["content_preview"]
    session_entry = next(item for item in report["session_token_manifest"] if item["relative_path"] == "Temp/20501.e31")
    assert session_entry["classification"] == "opaque_session_token_hash_only"
    assert "content_preview" not in session_entry
    assert report["next_action"] == "capture_visible_pl_profile_settings"


def test_build_parashara_light_settings_evidence_command_writes_json(monkeypatch, tmp_path):
    output_path = tmp_path / "settings-evidence.json"
    chart_xml = tmp_path / "Haridas.xml"
    chart_xml.write_text("<BirthData />", encoding="utf-16")
    options_dir = tmp_path / "GeoVisionOptions"
    options_dir.mkdir()
    pl7_dir = tmp_path / "PL7"
    pl7_dir.mkdir()

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_parashara_light_settings_evidence.build_parashara_light_settings_evidence",
        lambda chart_xml, options_dir, pl7_dir, **kwargs: {
            "source": "parashara_light_settings_evidence",
            "chart_xml": str(chart_xml),
            "options_dir": str(options_dir),
            "pl7_dir": str(pl7_dir),
        },
    )

    call_command(
        "build_parashara_light_settings_evidence",
        "--chart-xml",
        str(chart_xml),
        "--options-dir",
        str(options_dir),
        "--pl7-dir",
        str(pl7_dir),
        "--output",
        str(output_path),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["source"] == "parashara_light_settings_evidence"
    assert payload["chart_xml"] == str(chart_xml)
