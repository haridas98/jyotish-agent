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


def test_build_chart_facts_adds_detailed_position_analysis():
    facts = build_chart_facts(
        {
            "ascendant": {"body": "Lagna", "rashi": "Karka", "rashi_index": 3},
            "grahas": [
                {
                    "body": "Surya",
                    "longitude": 15.941111,
                    "speed_longitude": 1.0,
                    "rashi": "Mesha",
                    "rashi_index": 0,
                    "nakshatra": "Bharani",
                    "pada": 1,
                    "navamsa": "Simha",
                },
                {
                    "body": "Mangala",
                    "longitude": 18.954722,
                    "speed_longitude": 1.0,
                    "rashi": "Mesha",
                    "rashi_index": 0,
                    "nakshatra": "Bharani",
                    "pada": 2,
                    "navamsa": "Kanya",
                },
                {
                    "body": "Shani",
                    "longitude": 1.633889,
                    "speed_longitude": -0.02,
                    "rashi": "Mesha",
                    "rashi_index": 0,
                    "nakshatra": "Ashwini",
                    "pada": 1,
                    "navamsa": "Mesha",
                },
            ],
        }
    )

    rows = {row["body"]: row for row in facts["detailed_positions"]}

    assert rows["Surya"]["sign_degrees_dms"] == "15°56'28''"
    assert rows["Surya"]["dignity"] == "Экзальтация"
    assert rows["Surya"]["rashi_lord"] == "Mangala"
    assert rows["Surya"]["house"] == 10
    assert rows["Surya"]["ruled_houses"] == [2]
    assert rows["Surya"]["chara_karaka"] == "AmK"
    assert rows["Mangala"]["dignity"] == "Свой знак"
    assert rows["Mangala"]["ruled_houses"] == [10, 5]
    assert rows["Mangala"]["chara_karaka"] == "AK"
    assert rows["Shani"]["dignity"] == "Дебилитация"
    assert rows["Shani"]["retrograde"] is True


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
