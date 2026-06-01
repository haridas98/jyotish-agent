from apps.interpretations.facts import build_chart_facts


def test_build_chart_facts_assigns_whole_sign_houses_to_grahas():
    facts = build_chart_facts(
        {
            "ascendant": {"body": "Lagna", "rashi": "Kanya", "rashi_index": 5},
            "grahas": [
                {
                    "body": "Chandra",
                    "rashi": "Vrishabha",
                    "rashi_index": 1,
                    "nakshatra": "Rohini",
                    "pada": 3,
                    "navamsa": "Mithuna",
                },
                {
                    "body": "Shukra",
                    "rashi": "Karka",
                    "rashi_index": 3,
                    "nakshatra": "Pushya",
                    "pada": 2,
                    "navamsa": "Kanya",
                },
            ],
            "dashas": {
                "vimshottari": {
                    "mahadashas": [
                        {
                            "lord": "Chandra",
                            "starts_at": "1990-08-15T10:24:00+05:30",
                            "ends_at": "1993-12-19T22:51:15+05:30",
                        }
                    ]
                }
            },
        }
    )

    assert facts["lagna"]["rashi"] == "Kanya"
    assert facts["grahas"]["Chandra"]["house"] == 9
    assert facts["grahas"]["Shukra"]["house"] == 11
    assert facts["placements"][0]["body"] == "Chandra"
    assert facts["vimshottari"]["birth_mahadasha_lord"] == "Chandra"


def test_build_chart_facts_handles_missing_lagna_without_house_claims():
    facts = build_chart_facts(
        {
            "ascendant": None,
            "grahas": [
                {
                    "body": "Chandra",
                    "rashi": "Vrishabha",
                    "rashi_index": 1,
                }
            ],
        }
    )

    assert facts["lagna"] is None
    assert facts["grahas"]["Chandra"]["house"] is None
