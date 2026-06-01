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
    "Для публичного отчёта в духе ИСККОН рекомендации должны быть сформулированы как "
    "прибежище у Кришны: повторять маха-мантру Харе Кришна, изучать Бхагавад-гиту и "
    "Шримад-Бхагаватам, служить вайшнавам, а любые vrata, пожертвования или поклонение "
    "предлагать только как служение Кришне и гуру-парампаре."
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
