import json

from django.core.management import call_command


def test_parse_parashara_light_birth_xml_preserves_raw_and_candidate_normalization(tmp_path):
    from apps.calculations.parashara_light_profile import build_parashara_light_profile_report

    xml_path = tmp_path / "Haridas.xml"
    packet_path = tmp_path / "packet.json"
    xml_path.write_text(
        """<?xml version="1.0" encoding="UTF-16"?><BirthData>
 <BirthInfo><FirstName>Haridas</FirstName>
  <BirthDate>2450934.0729167</BirthDate>
  <Longitude>-55.9666667</Longitude>
  <Latitude>53.6166667</Latitude>
  <TimeZone>-5.0000000</TimeZone>
  <DST>1.0000000</DST>
  <City>Sterlitamak</City>
  <State>RUSSIA (General)</State>
  <Country>Russia</Country>
 </BirthInfo>
</BirthData>""",
        encoding="utf-16",
    )
    packet_path.write_text(
        json.dumps(
            {
                "fixture": {
                    "input": {
                        "longitude": 55.9502,
                        "latitude": 53.6304,
                        "timezone_offset": "+06:00",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    report = build_parashara_light_profile_report(xml_path, packet_path=packet_path)

    assert report["subject"]["first_name"] == "Haridas"
    assert report["raw_birth_info"]["longitude"] == -55.9666667
    assert report["candidate_normalization"]["longitude_east_candidate"] == 55.9666667
    assert report["candidate_normalization"]["timezone_offset_hours_candidate"] == 6.0
    assert report["packet_comparison"]["longitude_delta_degrees"] == 0.016467
    assert "PL_LONGITUDE_EAST_NEGATIVE_CONVENTION" in report["data_quality_flags"]
    assert "PL_TIMEZONE_EAST_NEGATIVE_WITH_DST_CONVENTION" in report["data_quality_flags"]


def test_build_parashara_light_profile_report_command_writes_json(monkeypatch, tmp_path):
    xml_path = tmp_path / "Haridas.xml"
    output_path = tmp_path / "profile-report.json"
    xml_path.write_text("<BirthData />", encoding="utf-16")

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_parashara_light_profile_report.build_parashara_light_profile_report",
        lambda birth_xml, packet_path=None: {
            "source": "parashara_light_birth_xml_profile",
            "source_xml": str(birth_xml),
            "packet_source": str(packet_path) if packet_path else "",
        },
    )

    call_command(
        "build_parashara_light_profile_report",
        "--birth-xml",
        str(xml_path),
        "--output",
        str(output_path),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["source"] == "parashara_light_birth_xml_profile"
    assert payload["source_xml"] == str(xml_path)
