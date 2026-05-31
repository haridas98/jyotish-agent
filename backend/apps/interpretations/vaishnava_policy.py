from __future__ import annotations

BLOCKED_REMEDY_TERMS = {
    "shani",
    "saturn",
    "surya",
    "chandra",
    "mangala",
    "budha",
    "guru",
    "shukra",
    "rahu",
    "ketu",
    "demigod",
    "graha",
}

KRISHNA_CENTERED_REMEDY = (
    "For a public ISKCON-aligned report, remedial guidance must be framed as taking shelter "
    "of Krishna: chant the Hare Krishna maha-mantra, study Bhagavad-gita and "
    "Srimad-Bhagavatam, serve Vaishnavas, and offer any vrata, charity, or worship only as "
    "service connected to Krishna and guru-parampara."
)


def reframe_remedial_advice(classical_advice: str) -> dict[str, object]:
    normalized = classical_advice.lower()
    blocked_terms = sorted(term for term in BLOCKED_REMEDY_TERMS if term in normalized)
    if not blocked_terms:
        return {
            "blocked_original": False,
            "blocked_terms": [],
            "public_advice": classical_advice,
        }

    return {
        "blocked_original": True,
        "blocked_terms": blocked_terms,
        "public_advice": KRISHNA_CENTERED_REMEDY,
    }
