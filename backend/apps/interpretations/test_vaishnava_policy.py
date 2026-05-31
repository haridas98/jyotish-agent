from apps.interpretations.vaishnava_policy import reframe_remedial_advice


def test_reframe_remedial_advice_blocks_independent_graha_worship():
    result = reframe_remedial_advice("Worship Shani on Saturday to remove Saturn affliction.")

    assert result["blocked_original"] is True
    assert "shani" in result["blocked_terms"]
    assert "Krishna" in result["public_advice"]
    assert "Hare Krishna" in result["public_advice"]
    assert "Worship Shani" not in result["public_advice"]


def test_reframe_remedial_advice_keeps_devotional_advice_public():
    result = reframe_remedial_advice("Chant Hare Krishna and study Bhagavad-gita daily.")

    assert result["blocked_original"] is False
    assert result["blocked_terms"] == []
    assert result["public_advice"] == "Chant Hare Krishna and study Bhagavad-gita daily."
