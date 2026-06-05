from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from apps.sources.models import ReviewStatus, SourceWork

CATALOG_WORK_SLUG = "classical-yoga-research-catalog"

BASE_SOURCE_PRIORITY = ["Brhat Jataka", "Phaladipika", "Jataka Parijata", "Saravali"]
NABHASA_SOURCE_PRIORITY = ["Brhat Jataka", "BPHS with caution", "Saravali"]
RAJA_SOURCE_PRIORITY = ["Phaladipika", "Jataka Parijata", "Sarvartha Cintamani"]
VAISHNAVA_GUARD = (
    "Explain as karma and service context only; no fatalistic promise, no independent "
    "graha or demigod worship, and no public claim without citations."
)
FORMULA_SOURCE_BASIS = "working classical formula; exact chapter/verse citation required before public prediction"
FORMULA_BY_KEY = {
    "gaja_kesari": "Guru is in a kendra from Chandra.",
    "budha_aditya": "Surya and Budha occupy the same rashi; dignity and combustion need review.",
    "chandra_mangala": "Chandra and Mangala occupy the same rashi.",
    "sunapha": "One or more classical planets occupy the 2nd from Chandra.",
    "anapha": "One or more classical planets occupy the 12th from Chandra.",
    "durudhara": "One or more classical planets occupy both the 2nd and 12th from Chandra.",
    "kemadruma": "No qualifying classical planets occupy the 2nd or 12th from Chandra.",
    "veshi": "One or more classical planets occupy the 2nd from Surya.",
    "voshi": "One or more classical planets occupy the 12th from Surya.",
    "ubhayachari": "One or more classical planets occupy both the 2nd and 12th from Surya.",
    "dharma_karmadhipati_raja": "The 9th lord and 10th lord are associated by conjunction or mutual aspect.",
    "kendra_trikona_raja": "A kendra lord and trikona lord are associated by conjunction or mutual aspect.",
    "second_lord_eleventh_lord_link": "The 2nd lord and 11th lord are associated by conjunction or mutual aspect.",
    "viparita_harsha": "The 6th lord is placed in another dusthana.",
    "viparita_sarala": "The 8th lord is placed in another dusthana.",
    "viparita_vimala": "The 12th lord is placed in another dusthana.",
    "neecha_bhanga_raja": "A debilitated graha receives cancellation through its debility sign lord in kendra from Lagna or Chandra.",
    "amala": "A natural benefic occupies the 10th from Lagna.",
    "amala_chandra": "A natural benefic occupies the 10th from Chandra.",
    "yogada_gl": "A graha is associated with both Lagna and Ghati Lagna by conjunction, ownership, or Jaimini rashi aspect.",
    "yogada_hl": "A graha is associated with both Lagna and Hora Lagna by conjunction, ownership, or Jaimini rashi aspect.",
}
CURATED_YOGA_SOURCE_ANCHORS: dict[str, list[dict[str, Any]]] = {
    "gaja_kesari": [
        {
            "condition_key": "gaja_kesari",
            "work_slug": "bphs-enjoylearning-sanskrit",
            "work_title": "Brhat Parashara Hora Shastra",
            "edition": "Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
            "source_url": "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-3/",
            "secondary_urls": [
                "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-4/",
                "https://archive.org/stream/brihatparasarahorashastrabyr.santhanam/Brihat%20Par%C4%81%C5%9Bara%20Hor%C4%81%20%C5%9Ah%C4%81stra%20By%20R.%20Santhanam_djvu.txt",
            ],
            "reference": "Chapter 36, Verses 3-4",
            "reference_status": "exact_verse_verified",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "condition_formula": (
                "Jupiter is in a kendra from Lagna or Moon, supported by benefic influence, "
                "and not weakened by debility, combustion, or enemy sign."
            ),
            "source_summary": (
                "Defines Gaja Kesari and gives brilliance, wealth, intelligence, good qualities, "
                "and favor from rulers or authorities."
            ),
            "interpretation_hint": (
                "Read as protective intelligence/status potential; qualify by Jupiter strength, "
                "affliction, house lordship, and dasha."
            ),
        }
    ],
    "kemadruma": [
        {
            "condition_key": "kemadruma",
            "work_slug": "bphs-enjoylearning-sanskrit",
            "work_title": "Brhat Parashara Hora Shastra",
            "edition": "Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
            "source_url": "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-37/verse-11/",
            "secondary_urls": [
                "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-37/verse-12/",
                "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english/d/doc1501766.html",
            ],
            "reference": "Chapter 37, Verses 11-12; Brihat Jataka 13.6 corroboration",
            "reference_status": "exact_verse_verified",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "condition_formula": (
                "No qualifying planet except the Sun occupies the 2nd or 12th from Moon; "
                "check cancellation by angular planets from Lagna before interpretation."
            ),
            "source_summary": (
                "Defines Kemadruma around the Moon and warns of poverty, distress, and weak learning "
                "when the condition is not cancelled."
            ),
            "interpretation_hint": (
                "Do not present fatalistically; emphasize cancellation, benefic support, dasha context, "
                "and Krishna-centered remedy framing."
            ),
        }
    ],
    "budha_aditya": [
        {
            "condition_key": "budha_aditya",
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira, Chapter XIV double planetary yogas",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english/d/doc1501770.html",
            "secondary_urls": [
                "https://chestofbooks.com/new-age/astrology/Brihat-Jataka/Chapter-XIV-On-Double-Planetary-Yogas.html"
            ],
            "reference": "Chapter 14, Verse 1",
            "reference_status": "condition_equivalent_exact_verse_name_not_printed",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "condition_formula": "Sun and Mercury occupy the same rashi.",
            "source_summary": (
                "Gives the Sun-Mercury conjunction results of skill, intelligence, fame, and comfort; "
                "the verse gives the condition but not the later popular name."
            ),
            "interpretation_hint": (
                "Treat the name as traditional shorthand; judge combustion, Mercury strength, house, "
                "and dignity before positive claims."
            ),
        }
    ],
    "neecha_bhanga_raja": [
        {
            "condition_key": "neecha_bhanga_raja",
            "work_slug": "phaladeepika",
            "work_title": "Phaladeepika",
            "edition": "Mantreswara; source text requires local passage review",
            "source_url": "https://www.jyotishvidya.com/HTMLobj-9415/Mantreswara_s__Phaladeeplka_.pdf",
            "secondary_urls": [],
            "reference": "Chapter 7, Verses 26-30",
            "reference_status": "exact_reference_pending_local_text_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "condition_formula": (
                "A debilitated planet receives cancellation through classical kendra, dispositor, "
                "aspect, or exaltation-related conditions."
            ),
            "source_summary": (
                "Lists debilitation-cancellation conditions and connects a strong cancellation with "
                "raja-yoga type rise."
            ),
            "interpretation_hint": (
                "Separate technical cancellation from strong Neecha Bhanga Raja Yoga; require strength, "
                "timing, and repeated support before promising rise."
            ),
        }
    ],
    "dharma_karmadhipati_raja": [
        {
            "condition_key": "dharma_karmadhipati_raja",
            "work_slug": "bphs-enjoylearning-sanskrit",
            "work_title": "Brhat Parashara Hora Shastra",
            "edition": "Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
            "source_url": "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-41/verse-28/",
            "secondary_urls": [
                "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-18/",
                "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-24/verse-106/",
                "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-24/verse-117/",
            ],
            "reference": "Chapter 41, Verse 28; Chapter 36, Verse 18; Chapter 24, Verses 106 and 117",
            "reference_status": "exact_verses_for_underlying_rule_name_varies",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "condition_formula": (
                "The 9th lord and 10th lord are associated by conjunction, exchange, placement, "
                "or the broader kendra-trikona lord sambandha rule."
            ),
            "source_summary": (
                "BPHS states that connection between kendra and trikona lords gives raja yoga, "
                "and gives specific 9th/10th lord placements or conjunctions as authority indicators."
            ),
            "interpretation_hint": (
                "Translate classical kingship into modern responsibility, visibility, institutional support, "
                "and dharmic use of work."
            ),
        }
    ],
    "kendra_trikona_raja": [
        {
            "condition_key": "kendra_trikona_raja",
            "work_slug": "bphs-enjoylearning-sanskrit",
            "work_title": "Brhat Parashara Hora Shastra",
            "edition": "Enjoy Learning Sanskrit Sanskrit/English",
            "source_url": "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-41/verse-28/",
            "secondary_urls": [],
            "reference": "Chapter 41, Verse 28",
            "reference_status": "exact_verse_verified",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "condition_formula": "A kendra lord and trikona lord are connected by sambandha.",
            "source_summary": "States that connection between lords of kendra and trikona houses gives raja yoga.",
            "interpretation_hint": "Judge the associated lords by dignity, house, affliction, and dasha before conclusions.",
        }
    ],
}
GROUP_YOGA_SOURCE_ANCHORS: dict[str, list[dict[str, Any]]] = {
    "panca_mahapurusha": [
        {
            "work_slug": "bphs-santhanam-ocr",
            "work_title": "Brhat Parashara Hora Shastra",
            "edition": "R. Santhanam OCR; Sanskrit/translation review required",
            "source_url": "https://archive.org/stream/brihatparasarahorashastrabyr.santhanam/Brihat%20Par%C4%81%C5%9Bara%20Hor%C4%81%20%C5%9Ah%C4%81stra%20By%20R.%20Santhanam_djvu.txt",
            "secondary_urls": [
                "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english"
            ],
            "reference": "Panch Mahapurusha Yoga sections; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": (
                "Classical sources group Ruchaka, Bhadra, Hamsa, Malavya, and Shasha as great-person "
                "yogas formed by strong planets in kendras."
            ),
            "interpretation_hint": (
                "Use only after checking the qualifying planet is in a kendra and in own or exaltation sign; "
                "judge combustion, aspects, varga strength, and dasha."
            ),
        }
    ],
    "lunar_yoga": [
        {
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira, Moon yogas chapter",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english/d/doc1501766.html",
            "secondary_urls": [
                "https://archive.org/stream/brihatparasarahorashastrabyr.santhanam/Brihat%20Par%C4%81%C5%9Bara%20Hor%C4%81%20%C5%9Ah%C4%81stra%20By%20R.%20Santhanam_djvu.txt"
            ],
            "reference": "Chapter 13, Moon yogas",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": (
                "Moon-centered yogas are judged from planets in the 2nd, 12th, both sides, or absence "
                "around the Moon, with cancellation and strength checks."
            ),
            "interpretation_hint": (
                "Read as mental support, social support, resources, and isolation patterns; always check "
                "cancellations and benefic relief."
            ),
        }
    ],
    "solar_yoga": [
        {
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira, double planetary and solar yoga material",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english/d/doc1501770.html",
            "secondary_urls": [],
            "reference": "Chapter 14 and related solar yoga sections; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": (
                "Solar yogas are read from planets adjacent to or joined the Sun, with benefic/malefic "
                "quality and combustion review."
            ),
            "interpretation_hint": (
                "Translate into public conduct, confidence, visibility, and initiative; do not ignore "
                "combustion or dignity."
            ),
        }
    ],
    "raja_yoga": [
        {
            "work_slug": "bphs-enjoylearning-sanskrit",
            "work_title": "Brhat Parashara Hora Shastra",
            "edition": "Enjoy Learning Sanskrit Sanskrit/English",
            "source_url": "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-41/verse-28/",
            "secondary_urls": [
                "https://www.jyotishvidya.com/HTMLobj-9415/Mantreswara_s__Phaladeeplka_.pdf"
            ],
            "reference": "Chapter 41, Raja Yoga principles; exact yoga-specific verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": (
                "Raja-yoga material centers on kendra and trikona lord connections, strength, and repeated "
                "support for authority or rise."
            ),
            "interpretation_hint": (
                "Translate kingship language into responsibility, leadership, institutional support, and "
                "dharma-aligned work."
            ),
        }
    ],
    "viparita_raja_yoga": [
        {
            "work_slug": "phaladeepika",
            "work_title": "Phaladeepika",
            "edition": "Mantreswara; source text requires local passage review",
            "source_url": "https://www.jyotishvidya.com/HTMLobj-9415/Mantreswara_s__Phaladeeplka_.pdf",
            "secondary_urls": [],
            "reference": "Viparita Raja Yoga material; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": (
                "Viparita patterns use dusthana lords in dusthanas to show improvement through difficulty, "
                "after checking actual strength and affliction."
            ),
            "interpretation_hint": (
                "Do not glorify suffering; read as resilience and recovery when the dusthana condition is exact."
            ),
        }
    ],
    "dhana_yoga": [
        {
            "work_slug": "phaladeepika",
            "work_title": "Phaladeepika",
            "edition": "Mantreswara; compare with Saravali/Sarvartha Cintamani",
            "source_url": "https://www.jyotishvidya.com/HTMLobj-9415/Mantreswara_s__Phaladeeplka_.pdf",
            "secondary_urls": [],
            "reference": "Dhana Yoga material; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": (
                "Wealth yogas depend on connections among Lagna, 2nd, 5th, 9th, 10th, and 11th factors, "
                "benefic strength, and repetition."
            ),
            "interpretation_hint": (
                "Frame as resource capacity and stewardship, not financial guarantee or investment advice."
            ),
        }
    ],
    "arishta_and_bhanga": [
        {
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira; compare with Phaladeepika",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
            "secondary_urls": [
                "https://www.jyotishvidya.com/HTMLobj-9415/Mantreswara_s__Phaladeeplka_.pdf"
            ],
            "reference": "Arishta and bhanga sections; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": (
                "Difficult yogas and their cancellations must be read together, especially for affliction, "
                "relief, strength, and timing."
            ),
            "interpretation_hint": (
                "Keep language careful and non-fatalistic; emphasize cancellation, remedial responsibility, "
                "and Vaishnava shelter."
            ),
        }
    ],
    "nabhasa_ashraya": [
        {
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira, Nabhasa Yogas",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
            "secondary_urls": [],
            "reference": "Nabhasa Yoga chapter; Ashraya group; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": "Ashraya Nabhasa yogas classify the sky pattern by sign modality concentration.",
            "interpretation_hint": "Use as broad temperament/background pattern, not as a standalone prediction.",
        }
    ],
    "nabhasa_dala": [
        {
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira, Nabhasa Yogas",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
            "secondary_urls": [],
            "reference": "Nabhasa Yoga chapter; Dala group; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": "Dala Nabhasa yogas classify benefic or malefic occupation of kendras.",
            "interpretation_hint": "Read with benefic/malefic balance and strength; do not overstate by pattern alone.",
        }
    ],
    "nabhasa_akriti": [
        {
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira, Nabhasa Yogas",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
            "secondary_urls": [],
            "reference": "Nabhasa Yoga chapter; Akriti group; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": "Akriti Nabhasa yogas classify planetary distribution by recognizable house patterns.",
            "interpretation_hint": "Use for structural life pattern only after checking all seven grahas and house scheme.",
        }
    ],
    "nabhasa_sankhya": [
        {
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira, Nabhasa Yogas",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
            "secondary_urls": [],
            "reference": "Nabhasa Yoga chapter; Sankhya group; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": "Sankhya Nabhasa yogas classify charts by the number of occupied houses.",
            "interpretation_hint": "Use as a broad distribution signature; check if a more specific Nabhasa yoga overrides it.",
        }
    ],
    "sannyasa_and_tapas": [
        {
            "work_slug": "brihat-jataka-varahamihira",
            "work_title": "Brihat Jataka",
            "edition": "Varahamihira; compare with BPHS and Phaladeepika",
            "source_url": "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
            "secondary_urls": [
                "https://archive.org/stream/brihatparasarahorashastrabyr.santhanam/Brihat%20Par%C4%81%C5%9Bara%20Hor%C4%81%20%C5%9Ah%C4%81stra%20By%20R.%20Santhanam_djvu.txt"
            ],
            "reference": "Pravrajya/Sannyasa material; exact verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": (
                "Renunciation yogas are judged from clustered planets, the strongest planet, and spiritual "
                "houses or austerity indicators."
            ),
            "interpretation_hint": (
                "In Gaudiya framing, interpret as capacity for sadhana, detachment, discipline, and service "
                "under guru-sadhu-shastra."
            ),
        }
    ],
    "rare_named_yoga": [
        {
            "work_slug": "phaladeepika",
            "work_title": "Phaladeepika",
            "edition": "Mantreswara; compare with Jataka Parijata and Saravali",
            "source_url": "https://www.jyotishvidya.com/HTMLobj-9415/Mantreswara_s__Phaladeeplka_.pdf",
            "secondary_urls": [],
            "reference": "Named yoga material; exact yoga-specific verse pending",
            "reference_status": "category_topic_anchor_needs_rule_review",
            "public_quote_policy": "paraphrase_until_passage_approved",
            "source_summary": "Rare named yogas need yoga-by-yoga textual confirmation before strong claims.",
            "interpretation_hint": "Use as a research lead only until the exact verse and condition are approved.",
        }
    ],
}


def _install_shared_curated_anchor(
    keys: list[str],
    *,
    work_slug: str,
    work_title: str,
    edition: str,
    source_url: str,
    secondary_urls: list[str] | None,
    reference: str,
    reference_status: str,
    source_summary: str,
    interpretation_hint: str,
) -> None:
    for key in keys:
        mahapurusha_formulas = globals().get("MAHAPURUSHA_FORMULAS", {})
        working_formulas = globals().get("WORKING_FORMULAS_NEED_SOURCE_REVIEW", {})
        formula = (
            FORMULA_BY_KEY.get(key)
            or mahapurusha_formulas.get(key)
            or working_formulas.get(key)
            or "See the per-yoga formula.description in the catalog."
        )
        CURATED_YOGA_SOURCE_ANCHORS.setdefault(key, []).append(
            {
                "condition_key": key,
                "work_slug": work_slug,
                "work_title": work_title,
                "edition": edition,
                "source_url": source_url,
                "secondary_urls": secondary_urls or [],
                "reference": reference,
                "reference_status": reference_status,
                "public_quote_policy": "paraphrase_until_passage_approved",
                "condition_formula": formula,
                "source_summary": source_summary,
                "interpretation_hint": interpretation_hint,
            }
        )


_install_shared_curated_anchor(
    [
        "ruchaka_mahapurusha",
        "bhadra_mahapurusha",
        "hamsa_mahapurusha",
        "malavya_mahapurusha",
        "shasha_mahapurusha",
    ],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-75/verse-1/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-75/verse-2/",
    ],
    reference="Chapter 75, Verses 1-2",
    reference_status="exact_verse_verified",
    source_summary=(
        "Mars, Mercury, Jupiter, Venus, and Saturn form the five Mahapurusha yogas when strong "
        "in own or exaltation signs and in kendras."
    ),
    interpretation_hint=(
        "Judge the named yoga by the qualifying planet, kendra placement, dignity, combustion, "
        "affliction, varga strength, and active dasha."
    ),
)
_install_shared_curated_anchor(
    ["sunapha", "anapha", "durudhara"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-37/verse-7/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-37/verse-8/",
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-37/verse-9/",
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-37/verse-10/",
    ],
    reference="Chapter 37, Verses 7-10",
    reference_status="exact_verse_verified",
    source_summary=(
        "Non-Sun planets in the 2nd, 12th, or both sides from the Moon form Sunapha, Anapha, "
        "and Durudhara with status, wealth, and comfort themes."
    ),
    interpretation_hint=(
        "Read as social and mental support around the Moon; qualify by benefic or malefic planets, "
        "Moon strength, and cancellation."
    ),
)
_install_shared_curated_anchor(
    ["veshi", "voshi", "ubhayachari"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 38, Verses 1-4",
    reference_status="exact_verse_verified",
    source_summary=(
        "Excluding the Moon, planets in the 2nd, 12th, or both sides from the Sun form Vesi, "
        "Vosi, and Ubhayachari; benefics and malefics alter the result."
    ),
    interpretation_hint=(
        "Read as public conduct and visibility around the Sun; check planet quality, combustion, dignity, "
        "and house context."
    ),
)
_install_shared_curated_anchor(
    ["viparita_harsha", "viparita_sarala", "viparita_vimala"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[
        "https://www.jyotishvidya.com/HTMLobj-9415/Mantreswara_s__Phaladeeplka_.pdf",
    ],
    reference="Chapter 6, Verses 57, 63, 65, and 69",
    reference_status="exact_name_verses_viparita_label_topic",
    source_summary=(
        "Harsha, Sarala, and Vimala are described through 6th, 8th, and 12th lord patterns, "
        "showing recovery, independence, and overcoming difficulty."
    ),
    interpretation_hint=(
        "Read as resilience through difficult houses only when the exact dusthana-lord condition is met; "
        "avoid glorifying suffering."
    ),
)
_install_shared_curated_anchor(
    ["pravrajya", "sannyasa"],
    work_slug="brihat-jataka-chestofbooks",
    work_title="Brihat Jataka",
    edition="Chestofbooks English web text; verify Sanskrit before public quotation",
    source_url="https://chestofbooks.com/new-age/astrology/Brihat-Jataka/Chapter-XV-On-Ascetio-Yogas.html",
    secondary_urls=[],
    reference="Chapter XV, Verses 1-4",
    reference_status="exact_verse_verified",
    source_summary=(
        "Four or more powerful planets in one sign indicate ascetic life, with the strongest planet "
        "showing the order or type."
    ),
    interpretation_hint=(
        "In Gaudiya framing, read as detachment and capacity for disciplined sadhana under guru, "
        "sadhu, and shastra, not automatic social renunciation."
    ),
)
_install_shared_curated_anchor(
    ["shakata"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 14 and 17",
    reference_status="exact_verse_verified",
    source_summary=(
        "Moon in the 6th, 8th, or 12th from Jupiter forms Shakata, with cancellation when Moon is "
        "in a kendra from Lagna; results fluctuate."
    ),
    interpretation_hint=(
        "Check cancellation and dasha before interpretation; read as fluctuating support or fortune, "
        "not permanent loss."
    ),
)
_install_shared_curated_anchor(
    ["chandra_mangala"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621590.html",
    secondary_urls=[],
    reference="Chapter 18, Verse 2",
    reference_status="condition_equivalent_exact_verse_name_not_printed",
    source_summary=(
        "Moon-Mars conjunction is treated as a two-planet result with trade, rough goods, and maternal "
        "tension themes; the popular yoga name is a later shorthand."
    ),
    interpretation_hint=(
        "Judge emotional drive, enterprise, and conflict themes by house, dignity, benefic influence, "
        "and Moon strength."
    ),
)
_install_shared_curated_anchor(
    ["vasumati"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 19-20",
    reference_status="exact_verse_verified",
    source_summary=(
        "Benefics in upachaya houses from Lagna or Moon form Vasumati and indicate abundant resources."
    ),
    interpretation_hint=(
        "Frame as resource capacity and stewardship; still check benefic strength, house ownership, and dasha."
    ),
)
_install_shared_curated_anchor(
    ["second_lord_eleventh_lord_link"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-14/verse-4/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-14/verse-5/",
    ],
    reference="Chapter 14, Verses 4-5",
    reference_status="exact_verse_verified",
    source_summary=(
        "A link between the 2nd and 11th lords by exchange or union in kendra/trikona gives wealth acquisition."
    ),
    interpretation_hint=(
        "Read as earning and resource support, not financial advice; qualify by strength, affliction, and timing."
    ),
)
_install_shared_curated_anchor(
    ["tapasvi"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621599.html",
    secondary_urls=[],
    reference="Chapter 27, Verse 6",
    reference_status="exact_verse_verified",
    source_summary=(
        "A weak Moon aspected by the Lagna lord is described as giving a distressed ascetic or tapasvi pattern."
    ),
    interpretation_hint=(
        "Translate into austerity, endurance, and need for devotional support; avoid romanticizing distress."
    ),
)
_install_shared_curated_anchor(
    ["rajju_nabhasa", "musala_nabhasa", "nala_nabhasa"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 35, Verse 7",
    reference_status="exact_verse_verified",
    source_summary=(
        "Rajju, Musala, and Nala are formed when all grahas occupy movable, fixed, or dual signs."
    ),
    interpretation_hint=(
        "Read as a broad modality pattern after checking all seven classical grahas and override rules."
    ),
)
_install_shared_curated_anchor(
    ["mala_nabhasa", "sarpa_nabhasa"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 35, Verse 8",
    reference_status="exact_verse_verified",
    source_summary=(
        "Mala and Sarpa are formed by benefics or malefics occupying three kendras."
    ),
    interpretation_hint=(
        "Read through benefic/malefic balance and strength; do not overstate the pattern alone."
    ),
)
_install_shared_curated_anchor(
    [
        "gada_nabhasa",
        "shakata_nabhasa",
        "vihaga_nabhasa",
        "shringataka_nabhasa",
        "hala_nabhasa",
        "vajra_nabhasa",
        "yava_nabhasa",
    ],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 35, Verses 9-11",
    reference_status="exact_verse_verified",
    source_summary=(
        "Gada, Shakata, Vihaga, Shringataka, Hala, Vajra, and Yava are defined by specific all-graha "
        "kendra and trinal house patterns."
    ),
    interpretation_hint=(
        "Use the exact house-pattern test and keep it as structural background unless repeated by stronger factors."
    ),
)
_install_shared_curated_anchor(
    ["kamala_nabhasa", "vapi_nabhasa"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 35, Verse 12",
    reference_status="exact_verse_verified",
    source_summary=(
        "Kamala is formed by all grahas in the four kendras; Vapi by all grahas in apoklima or panaphara houses."
    ),
    interpretation_hint=(
        "Read as chart-wide distribution; verify house scheme and all seven classical grahas."
    ),
)
_install_shared_curated_anchor(
    ["yupa_nabhasa", "ishu_nabhasa", "shakti_nabhasa", "danda_nabhasa"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 35, Verse 13",
    reference_status="exact_verse_verified",
    source_summary=(
        "Yupa, Shara/Ishu, Shakti, and Danda are formed when all seven grahas occupy four consecutive houses "
        "starting from Lagna, 4th, 7th, or 10th."
    ),
    interpretation_hint=(
        "Use as a whole-chart directional pattern; confirm the four-house span exactly."
    ),
)
_install_shared_curated_anchor(
    [
        "nauka_nabhasa",
        "kuta_nabhasa",
        "chhatra_nabhasa",
        "chapa_nabhasa",
        "ardha_chandra_nabhasa",
    ],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 35, Verse 14",
    reference_status="exact_verse_verified",
    source_summary=(
        "Nauka, Kuta, Chhatra, Chapa, and the Saravali-quoted Ardha Chandra are formed by continuous "
        "seven-house distributions from specified starts."
    ),
    interpretation_hint=(
        "Verify seven continuous occupied houses and whether a more specific Nabhasa rule overrides the pattern."
    ),
)
_install_shared_curated_anchor(
    ["chakra_nabhasa", "samudra_nabhasa"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 35, Verse 15",
    reference_status="exact_verse_verified",
    source_summary=(
        "Chakra and Samudra are formed by all grahas occupying six alternate signs from Lagna or 2nd house."
    ),
    interpretation_hint=(
        "Read as a broad distribution signature; validate alternating sign pattern exactly."
    ),
)
_install_shared_curated_anchor(
    [
        "gola_nabhasa",
        "yuga_nabhasa",
        "shula_nabhasa",
        "kedara_nabhasa",
        "pasha_nabhasa",
        "dama_nabhasa",
        "vina_nabhasa_variant",
    ],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments English text; compare with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    secondary_urls=[],
    reference="Chapter 35, Verses 16-17",
    reference_status="exact_verse_verified",
    source_summary=(
        "Sankhya Nabhasa yogas are formed by all grahas occupying one through seven rashis, producing "
        "Gola, Yuga, Shula, Kedara, Pasha, Dama, and Veena."
    ),
    interpretation_hint=(
        "Use only when earlier Nabhasa categories do not override; count occupied rashis deterministically."
    ),
)
_install_shared_curated_anchor(
    ["amala", "amala_chandra", "pushkala"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 19-20",
    reference_status="exact_verse_verified",
    source_summary=(
        "Amala is formed by benefics in the 10th from Lagna or Moon and is described with wealth, fame, "
        "prudence, and prosperity."
    ),
    interpretation_hint=(
        "Read as clean public karma and reputation support; qualify by the benefic's strength and 10th-house context."
    ),
)
_install_shared_curated_anchor(
    ["lakshmi"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 21 and 24",
    reference_status="exact_verse_verified",
    source_summary=(
        "Lakshmi Yoga is formed by the 9th lord and Venus strong in own or exaltation signs in a kendra or trikona."
    ),
    interpretation_hint=(
        "Use a Krishna-centered wealth and stewardship framing; do not recommend separate goddess worship."
    ),
)
_install_shared_curated_anchor(
    ["saraswati"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 26-27",
    reference_status="exact_verse_verified",
    source_summary=(
        "Saraswati Yoga is formed by Venus, Jupiter, and Mercury in kendra, trikona, or 2nd house, with strong Jupiter."
    ),
    interpretation_hint=(
        "Read as learning, expression, writing, and refined intelligence; qualify by dignity and affliction."
    ),
)
_install_shared_curated_anchor(
    ["sri_natha"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 28 and 30",
    reference_status="exact_verse_verified",
    source_summary=(
        "Srinatha Yoga is formed by Venus, the 9th lord, and Mercury similarly placed in strength."
    ),
    interpretation_hint=(
        "The source has Vaishnava language; interpret through devotion to Narayana/Krishna and practical character."
    ),
)
_install_shared_curated_anchor(
    ["brahma"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 28 and 31",
    reference_status="condition_equivalent_exact_verse_name_varies",
    source_summary=(
        "Virinchi/Brahma-type yoga is connected with Jupiter, the 5th lord, and Saturn in strong kendra/trikona conditions."
    ),
    interpretation_hint=(
        "Read as scriptural learning, restraint, and teaching capacity; verify name equivalence before public wording."
    ),
)
_install_shared_curated_anchor(
    ["kahala", "parvata"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 35-36",
    reference_status="exact_verse_verified",
    source_summary=(
        "Kahala and Parvata are defined through the dispositor chain of the Lagna lord and strong kendra/trikona dignity."
    ),
    interpretation_hint=(
        "Read as stability, capacity, and public respect only after verifying the dispositor chain exactly."
    ),
)
_install_shared_curated_anchor(
    ["sankha", "dharma_karmadhipati_raja"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 37-38",
    reference_status="exact_verse_verified",
    source_summary=(
        "The 9th and 10th lords joined in an auspicious bhava give Raja Yoga; kendra and trikona lord union gives Sankha."
    ),
    interpretation_hint=(
        "Translate kingly language into responsibility, dharmic work, and institutional support."
    ),
)
_install_shared_curated_anchor(
    ["maha_bhagya", "kesari_variant"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 14-18",
    reference_status="exact_verse_verified",
    source_summary=(
        "This section defines Mahabhagya, Kesari, Shakata, and Adhama/Sama/Varishtha Moon-Sun conditions."
    ),
    interpretation_hint=(
        "Use the exact luminary condition before naming the yoga; qualify by gender/day-night rules where applicable."
    ),
)
_install_shared_curated_anchor(
    ["adhama"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[
        "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/phaladIpika.itx",
    ],
    reference="Chapter 6, Verses 14 and 18",
    reference_status="exact_name_formula_mismatch",
    source_summary=(
        "Adhama/Sama/Varishtha are Moon-from-Sun positional yogas, not a generic weak-Lagna rule."
    ),
    interpretation_hint=(
        "Treat the current local detector as needing formula correction before public Adhama Yoga wording."
    ),
)
_install_shared_curated_anchor(
    ["daridra"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verse 68",
    reference_status="exact_verse_verified",
    source_summary=(
        "Daridra Yoga is listed among the twelve bhava-lord difficulty yogas and described with debt, poverty, and dependence themes."
    ),
    interpretation_hint=(
        "Use non-fatalistic language; emphasize counter-yogas, dasha context, service, and disciplined stewardship."
    ),
)
_install_shared_curated_anchor(
    ["bhagya"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verse 53",
    reference_status="exact_verse_verified",
    source_summary=(
        "Bhagya Yoga is described with lasting wealth, righteous conduct, and honoring sacred duties."
    ),
    interpretation_hint=(
        "Read as dharmic fortune and support, not entitlement; judge 9th-house strength and dasha."
    ),
)
_install_shared_curated_anchor(
    ["parijata"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verse 55",
    reference_status="exact_verse_verified",
    source_summary=(
        "Parijata Yoga is described with auspicious celebrations, rulership, accumulated wealth, family, learning, and auspicious work."
    ),
    interpretation_hint=(
        "Use as a prosperity/support indicator only after verifying the exact Parijata condition in the chart."
    ),
)
_install_shared_curated_anchor(
    ["subha_vesi", "asubha_vesi"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[
        "https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.html",
    ],
    reference="Chapter 6, Verse 13; BPHS Chapter 38, Verses 1-4",
    reference_status="exact_verse_verified",
    source_summary=(
        "Benefic and malefic variants of Vesi-type yogas take results from the benefic or malefic nature of the planet."
    ),
    interpretation_hint=(
        "Judge the planet's natural quality, combustion, dignity, and house before interpreting conduct and public expression."
    ),
)
_install_shared_curated_anchor(
    ["lagna_lord_kendra_trikona_raja"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-40/verse-15/",
    secondary_urls=[],
    reference="Chapter 40, Verse 15",
    reference_status="topic_anchor_for_lagna_lord_raja_principle",
    source_summary=(
        "Lagna or Atmakaraka connected with the 5th lord in kendra or trikona gives kingly or ministerial result."
    ),
    interpretation_hint=(
        "Use as a lagna-lord raja-yoga support only when the chart condition matches; detector is broader."
    ),
)
_install_shared_curated_anchor(
    ["raja_sambandha"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-41/verse-28/",
    secondary_urls=[],
    reference="Chapter 41, Verse 28",
    reference_status="exact_principle_verified",
    source_summary=(
        "Kendra lord and trikona lord sambandha is stated as a raja-yoga principle."
    ),
    interpretation_hint=(
        "Use for the general sambandha principle; specify the exact planets, houses, strength, and dasha."
    ),
)
_install_shared_curated_anchor(
    ["maharaja"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-39/verse-7/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-39/verse-6/",
    ],
    reference="Chapter 39, Verses 6-7",
    reference_status="exact_name_detector_partial",
    source_summary=(
        "Maharaja Yoga is tied to strong Lagna/5th or Atmakaraka/Putrakaraka patterns with benefic support."
    ),
    interpretation_hint=(
        "Do not equate every local maharaja detector hit with the exact BPHS rule; show the matched subcondition."
    ),
)
_install_shared_curated_anchor(
    ["kalanidhi"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-31/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-32/",
    ],
    reference="Chapter 36, Verses 31-32",
    reference_status="exact_name_detector_partial",
    source_summary=(
        "Kalanidhi Yoga is defined through Jupiter in the 2nd or 5th with Mercury and Venus influence."
    ),
    interpretation_hint=(
        "Read as refined learning, culture, and resource support; verify the Jupiter-Mercury-Venus condition exactly."
    ),
)
_install_shared_curated_anchor(
    ["bheri"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-15/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-16/",
    ],
    reference="Chapter 36, Verses 15-16",
    reference_status="exact_verse_verified",
    source_summary=(
        "Bheri Yoga is defined through strong 9th lord and specified Venus, Jupiter, and Lagna-lord/kendra patterns."
    ),
    interpretation_hint=(
        "Use only when the exact multi-factor rule is met; read as support, dignity, and organized capability."
    ),
)
_install_shared_curated_anchor(
    ["chamara"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-11/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-12/",
    ],
    reference="Chapter 36, Verses 11-12",
    reference_status="exact_name_detector_partial",
    source_summary=(
        "Chamara Yoga is formed by exalted Lagna lord in kendra aspected by Jupiter, or by two benefics "
        "in Lagna, 7th, 9th, or 10th."
    ),
    interpretation_hint=(
        "Check the exact alternative rule; read as dignity and respected bearing, not automatic rank."
    ),
)
_install_shared_curated_anchor(
    ["dhana_from_arudha"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-29/verse-30/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-29/verse-31/",
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-29/verse-32/",
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-39/verse-29/",
    ],
    reference="Chapter 29, Verses 30-32; Chapter 39, Verses 29-31",
    reference_status="exact_topic_verified",
    source_summary=(
        "Benefic influence on the 2nd from Arudha and Venus/benefic links to Arudha gain points support wealth results."
    ),
    interpretation_hint=(
        "Use as Arudha-specific dhana evidence; keep it separate from ordinary 2nd/11th house wealth rules."
    ),
)
_install_shared_curated_anchor(
    ["chandra_guru_dhana"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-37/verse-2/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-3/",
    ],
    reference="Chapter 37, Verse 2; Chapter 36, Verses 3-4",
    reference_status="partial_exact_topic_anchor",
    source_summary=(
        "Moon with Jupiter influence is tied to wealth and happiness themes; Gaja Kesari gives a stronger Moon-Jupiter anchor."
    ),
    interpretation_hint=(
        "Use as Moon-Jupiter wealth support only after judging whether the exact Gaja Kesari or another rule applies."
    ),
)
_install_shared_curated_anchor(
    ["labha_lord_strength"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-40/verse-12/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-40/verse-2/",
    ],
    reference="Chapter 40, Verses 2 and 12",
    reference_status="topic_anchor_needs_detector_review",
    source_summary=(
        "The 11th house and its lord are treated as gain factors when strong and free from severe malefic influence."
    ),
    interpretation_hint=(
        "Use as gain-house support; do not make a wealth claim without 2nd/11th/trikona repetition and dasha."
    ),
)
_install_shared_curated_anchor(
    ["lakshmi_dhana"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Phaladeepika",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-27/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-36/verse-28/",
        "https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    ],
    reference="BPHS Chapter 36, Verses 27-28; Phaladeepika Chapter 6, Verses 21 and 24",
    reference_status="exact_name_topic_for_local_dhana_variant",
    source_summary=(
        "Lakshmi Yoga anchors strong 9th-lord, Lagna, and wealth/status themes; local Lakshmi-Dhana is a broader variant."
    ),
    interpretation_hint=(
        "Keep public wording as a Lakshmi/Dhana variant unless the exact BPHS or Phaladeepika rule is matched."
    ),
)
_install_shared_curated_anchor(
    ["dusthana_lord_exchange_viparita"],
    work_slug="phaladeepika-wisdomlib",
    work_title="Phaladeepika",
    edition="Wisdomlib text/translation; OCR unproofread, verify against PDF",
    source_url="https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation/d/doc1621578.html",
    secondary_urls=[],
    reference="Chapter 6, Verses 32-34",
    reference_status="condition_equivalent_exact_verses",
    source_summary=(
        "Phaladeepika classifies house-lord exchanges into Dainya, Khala, and Maha patterns, including dusthana-based exchanges."
    ),
    interpretation_hint=(
        "Use this as exchange-yoga evidence, then separately verify whether the local Viparita interpretation is justified."
    ),
)
_install_shared_curated_anchor(
    ["dhana_lagna_lord_second_eleventh", "dwi_dhana", "bahu_dhana", "indra"],
    work_slug="bphs-enjoylearning-sanskrit",
    work_title="Brhat Parashara Hora Shastra",
    edition="Enjoy Learning Sanskrit Sanskrit/English; compare with Santhanam OCR",
    source_url="https://enjoylearningsanskrit.com/scriptures/parashara/chapter-41/",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-41/verse-7/",
    ],
    reference="Chapter 41, Verses 1-17",
    reference_status="topic_anchor_for_composite_dhana_rules",
    source_summary=(
        "BPHS gives a dedicated wealth-combinations chapter with repeated links among wealth, gain, and auspicious lords."
    ),
    interpretation_hint=(
        "Use as chapter-level support for internal counted dhana links; exact public claim needs the matched verse."
    ),
)
_install_shared_curated_anchor(
    ["balarishta", "arishta_bhanga"],
    work_slug="brihat-jataka-chestofbooks",
    work_title="Brihat Jataka",
    edition="Chidambaram Aiyar English web text; verify Sanskrit before public quotation",
    source_url="https://chestofbooks.com/new-age/astrology/Brihat-Jataka/Chapter-VI-On-Balarishta-Or-Early-Death.html",
    secondary_urls=[
        "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
    ],
    reference="Chapter VI, Balarishta and cancellation material",
    reference_status="chapter_topic_anchor_needs_sloka_review",
    source_summary=(
        "Brihat Jataka Chapter VI gives early-life arishta combinations and also cancellation/mitigation material."
    ),
    interpretation_hint=(
        "Never present as a prediction of death; use only for technical audit, cancellation checks, and careful non-fatalistic wording."
    ),
)
_install_shared_curated_anchor(
    ["balarishta"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par0110.itx",
    secondary_urls=[
        "https://chestofbooks.com/new-age/astrology/Brihat-Jataka/Chapter-VI-On-Balarishta-Or-Early-Death.html",
    ],
    reference="Chapter 9, Verses 1-23",
    reference_status="exact_category_verified",
    source_summary=(
        "BPHS treats childhood arishta before ayurdaya, using Moon, Lagna, and severe malefic affliction conditions."
    ),
    interpretation_hint=(
        "Use only as technical early-life risk audit and always check arishta-bhanga; never present as a death prediction."
    ),
)
_install_shared_curated_anchor(
    ["arishta_bhanga"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par0110.itx",
    secondary_urls=[],
    reference="Chapter 10, Verses 1-9",
    reference_status="exact_verse_verified",
    source_summary=(
        "Strong benefics in kendras, strong Jupiter or Lagna lord, and benefic protection cancel arishta."
    ),
    interpretation_hint=(
        "Present cancellation and protective factors before any difficult arishta interpretation."
    ),
)
_install_shared_curated_anchor(
    ["grahana"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par0110.itx",
    secondary_urls=[],
    reference="Chapter 9, Verse 7",
    reference_status="exact_topic_verified",
    source_summary=(
        "Rahu joined Sun or Moon at an eclipse with malefic Lagna influence is treated as severe arishta."
    ),
    interpretation_hint=(
        "Use as eclipse-affliction evidence, not as a blanket rule for every Sun/Moon-node conjunction."
    ),
)
_install_shared_curated_anchor(
    ["mangala_dosha"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par7180.itx",
    secondary_urls=[],
    reference="Chapter 80, Verses 47-49",
    reference_status="exact_core_verified",
    source_summary=(
        "Mars in Lagna, 12th, 4th, 7th, or 8th without benefic relief harms spouse; mutual affliction can cancel."
    ),
    interpretation_hint=(
        "Use as core Mangala Dosha only; Moon/Venus-based expansions and compatibility balancing need separate review."
    ),
)
_install_shared_curated_anchor(
    ["pitru_dosha_research"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par8190.itx",
    secondary_urls=[],
    reference="Chapter 83, Verses 20-33",
    reference_status="topic_anchor_name_differs_pitri_shapa",
    source_summary=(
        "The source discusses pitri-shapa through Sun, 9th, and lineage indicators with malefic links."
    ),
    interpretation_hint=(
        "Call this pitri-shapa lineage-affliction evidence, not a finalized modern Pitru Dosha rule."
    ),
)
_install_shared_curated_anchor(
    ["kala_sarpa_contested"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par8190.itx",
    secondary_urls=[],
    reference="Chapter 83, Verses 9-19",
    reference_status="no_exact_kala_sarpa_rule_found_serpent_curse_topic",
    source_summary=(
        "Serpent-curse and Rahu-naga material exists, but the all-planets-between-nodes Kala Sarpa rule was not found here."
    ),
    interpretation_hint=(
        "Keep Kala Sarpa contested and research-gated; do not present it as BPHS-confirmed."
    ),
)
_install_shared_curated_anchor(
    ["visha"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par7180.itx",
    secondary_urls=[],
    reference="Chapter 80, Verses 43-46",
    reference_status="name_mismatch_topic_anchor",
    source_summary=(
        "The source has visha/vishakhya wording in female horoscopy, not the later Shani-Chandra Vish Yoga."
    ),
    interpretation_hint=(
        "Keep the local Shani-Chandra Visha rule under review until an exact classical anchor is found."
    ),
)
_install_shared_curated_anchor(
    ["mridanga"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par3140.itx",
    secondary_urls=[],
    reference="Chapter 36, Verse 17",
    reference_status="exact_verse_verified",
    source_summary=(
        "Strong Lagna lord with planets in kendras, trikonas, own, or exaltation contexts gives Mridanga/Mrigaanga Yoga."
    ),
    interpretation_hint=(
        "Read as structural support and capability only after exact Lagna-lord strength is verified."
    ),
)
_install_shared_curated_anchor(
    ["naga"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par8190.itx",
    secondary_urls=[],
    reference="Chapter 83, Verses 9-19",
    reference_status="topic_anchor_name_differs_sarpa_shapa",
    source_summary=(
        "Sarpa-shapa material uses Rahu, Mars, and 5th/child indicators; it is not an exact Naga Yoga match."
    ),
    interpretation_hint=(
        "Use as serpent-affliction context only; remedies must be Krishna-centered, not independent naga worship."
    ),
)
_install_shared_curated_anchor(
    ["garuda"],
    work_slug="jataka-parijata-sanskritdocuments",
    work_title="Jataka Parijata",
    edition="SanskritDocuments ITX; verify before public quotation",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/jAtakapArijAtaH.itx",
    secondary_urls=[],
    reference="Chapter 4, Verse 81",
    reference_status="protective_metaphor_topic_anchor",
    source_summary=(
        "A strong benefic Moon cancels arishta like Garuda destroys poison; this is protective metaphor, not exact Garuda Yoga."
    ),
    interpretation_hint=(
        "Use only as protective-cancellation imagery; do not name a chart pattern Garuda Yoga without exact rule."
    ),
)
_install_shared_curated_anchor(
    ["go"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par3140.itx",
    secondary_urls=[],
    reference="Chapter 36, Verses 38-39",
    reference_status="no_exact_go_yoga_gopura_topic",
    source_summary=(
        "Gopura dignity results were found, not an exact Go Yoga matching the catalog rule."
    ),
    interpretation_hint=(
        "Keep Go Yoga as research-gated until the exact named rule is found."
    ),
)
_install_shared_curated_anchor(
    ["vidyut"],
    work_slug="classical-yoga-research-catalog",
    work_title="Classical Yoga Research Catalog",
    edition="Search note from BPHS/BJ/Phaladeepika/Jataka Parijata/Saravali pass",
    source_url="",
    secondary_urls=[],
    reference="No exact public classical anchor found in current pass",
    reference_status="no_exact_anchor_found",
    source_summary=(
        "No exact Vidyut Yoga anchor was found in the checked public classics."
    ),
    interpretation_hint=(
        "Keep Vidyut Yoga blocked from public interpretation until a verse is found."
    ),
)
_install_shared_curated_anchor(
    ["adrogate_raja_research"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par3140.itx",
    secondary_urls=[],
    reference="Chapter 39, Verses 33-39",
    reference_status="no_exact_name_raja_topic_anchor",
    source_summary=(
        "No adrogate term was found; nearest support is raja-yoga through Lagna, 5th, 9th, and 10th lord relations."
    ),
    interpretation_hint=(
        "Keep this as a research placeholder and do not expose the name publicly."
    ),
)
_install_shared_curated_anchor(
    ["rajju_variant"],
    work_slug="bphs-sanskritdocuments",
    work_title="Brhat Parashara Hora Shastra",
    edition="SanskritDocuments ITX; verify with Sanskrit/OCR",
    source_url="https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par3140.itx",
    secondary_urls=[
        "https://enjoylearningsanskrit.com/scriptures/parashara/chapter-35/verse-7/",
    ],
    reference="Chapter 35, Verses 3, 7, and 18",
    reference_status="exact_verse_verified",
    source_summary=(
        "Rajju Nabhasa is all planets in movable signs, with effects given later in the Nabhasa chapter."
    ),
    interpretation_hint=(
        "Use as a Rajju/Nabhasa variant only if all classical grahas are in movable signs."
    ),
)
_install_shared_curated_anchor(
    ["vasishta"],
    work_slug="classical-yoga-research-catalog",
    work_title="Classical Yoga Research Catalog",
    edition="Search note from BPHS/BJ/Phaladeepika/Jataka Parijata/Saravali pass",
    source_url="",
    secondary_urls=[],
    reference="No exact public classical anchor found in current pass",
    reference_status="no_exact_anchor_found",
    source_summary=(
        "No exact Vasishta Yoga matching the Guru/Budha/benefic wisdom rule was found in the checked public classics."
    ),
    interpretation_hint=(
        "Keep Vasishta Yoga research-gated until an exact rule is found."
    ),
)
NABHASA_FORMULAS = {
    "rajju_nabhasa": "All seven classical grahas are in movable rashis.",
    "musala_nabhasa": "All seven classical grahas are in fixed rashis.",
    "nala_nabhasa": "All seven classical grahas are in dual rashis.",
    "mala_nabhasa": "Natural benefics occupy kendras from Lagna while malefic interference is absent or secondary.",
    "sarpa_nabhasa": "Natural malefics occupy kendras from Lagna while benefic support is absent or secondary.",
    "gada_nabhasa": "All seven classical grahas are confined to two adjacent kendras.",
    "shakata_nabhasa": "All seven classical grahas are confined to Lagna and the 7th house.",
    "vihaga_nabhasa": "All seven classical grahas are confined to the 4th and 10th houses.",
    "shringataka_nabhasa": "All seven classical grahas are confined to the trines 1, 5, and 9.",
    "hala_nabhasa": "All seven classical grahas are confined to one Hala triad: 2/6/10, 3/7/11, or 4/8/12.",
    "vajra_nabhasa": "Benefics occupy Lagna/7th while malefics occupy 4th/10th.",
    "yava_nabhasa": "Malefics occupy Lagna/7th while benefics occupy 4th/10th.",
    "kamala_nabhasa": "All seven classical grahas are confined to the four kendras.",
    "vapi_nabhasa": "All seven classical grahas are confined to panaphara or apoklima houses.",
    "yupa_nabhasa": "All seven classical grahas are confined to houses 1, 2, 3, and 4.",
    "ishu_nabhasa": "All seven classical grahas are confined to houses 4, 5, 6, and 7.",
    "shakti_nabhasa": "All seven classical grahas are confined to houses 7, 8, 9, and 10.",
    "danda_nabhasa": "All seven classical grahas are confined to houses 10, 11, 12, and 1.",
    "nauka_nabhasa": "All seven classical grahas are confined to houses 1 through 7.",
    "kuta_nabhasa": "All seven classical grahas are confined to houses 4 through 10.",
    "chhatra_nabhasa": "All seven classical grahas are confined to houses 7 through 12 and 1.",
    "chapa_nabhasa": "All seven classical grahas are confined to houses 10 through 12 and 1 through 4.",
    "ardha_chandra_nabhasa": "All seven classical grahas are distributed across any seven consecutive houses.",
    "chakra_nabhasa": "All seven classical grahas are confined to odd houses 1, 3, 5, 7, 9, and 11.",
    "samudra_nabhasa": "All seven classical grahas are confined to even houses 2, 4, 6, 8, 10, and 12.",
    "gola_nabhasa": "All seven classical grahas occupy one house.",
    "yuga_nabhasa": "All seven classical grahas occupy two houses.",
    "shula_nabhasa": "All seven classical grahas occupy three houses.",
    "kedara_nabhasa": "All seven classical grahas occupy four houses.",
    "pasha_nabhasa": "All seven classical grahas occupy five houses.",
    "dama_nabhasa": "All seven classical grahas occupy six houses.",
    "vina_nabhasa_variant": "All seven classical grahas occupy seven houses.",
}
MAHAPURUSHA_FORMULAS = {
    "ruchaka_mahapurusha": "Mangala is in a kendra from Lagna in own or exaltation rashi.",
    "bhadra_mahapurusha": "Budha is in a kendra from Lagna in own or exaltation rashi.",
    "hamsa_mahapurusha": "Guru is in a kendra from Lagna in own or exaltation rashi.",
    "malavya_mahapurusha": "Shukra is in a kendra from Lagna in own or exaltation rashi.",
    "shasha_mahapurusha": "Shani is in a kendra from Lagna in own or exaltation rashi.",
}
WORKING_FORMULAS_NEED_SOURCE_REVIEW = {
    "lagna_lord_kendra_trikona_raja": "Lagna lord is strongly placed in a kendra or trikona and associated with a trinal or angular lord.",
    "raja_sambandha": "A sambandha exists between lords of kendras/trikonas or between a strong lagna lord and authority-giving houses.",
    "maharaja": "Multiple strong raja-yoga lords, especially 9th/10th or kendra/trikona lords, are associated and unafflicted.",
    "sri_natha": "The 7th lord, 10th lord, or lagna lord gains strength in exaltation/own sign and links to a kendra or trikona.",
    "lakshmi": "The 9th lord is strong and associated with the lagna lord or placed in a kendra/trikona with benefic support.",
    "saraswati": "Budha, Guru, and Shukra are strong and connected to kendras/trikonas or the 2nd/5th houses of learning.",
    "kalanidhi": "Guru is connected with Budha or Shukra and occupies/supports the 2nd or 5th from Lagna or Chandra.",
    "bheri": "Strong lagna, 9th, 10th, and benefic support combine through kendras/trikonas.",
    "chamara": "Lagna lord is exalted or strong in a kendra and benefics support Lagna or the 7th/10th.",
    "kahala": "The 4th lord and 9th/10th factors are strong and connected with Lagna or kendras.",
    "parvata": "Benefics occupy kendras while the 6th and 8th houses are empty or their lords are weak/contained.",
    "sankha": "Strong 5th and 6th lords or Lagna/10th support combine with benefic kendra/trikona strength.",
    "dusthana_lord_exchange_viparita": "Two dusthana lords exchange signs, especially among the 6th, 8th, and 12th houses.",
    "dhana_lagna_lord_second_eleventh": "Lagna lord, 2nd lord, and 11th lord connect by placement, conjunction, or mutual aspect.",
    "dwi_dhana": "Two independent dhana links connect wealth houses/lords, especially 2nd, 5th, 9th, and 11th.",
    "bahu_dhana": "Several dhana links repeat through wealth houses, benefics, and strong lords.",
    "vasumati": "Natural benefics occupy upachaya houses from Lagna or Chandra.",
    "indra": "Strong Lagna/11th factors and benefic support create repeated prosperity and status links.",
    "chandra_guru_dhana": "Chandra and Guru form a wealth-supporting relation through kendra, 2nd, 5th, 9th, or 11th links.",
    "dhana_from_arudha": "Arudha Lagna or its 2nd/11th receives benefic occupation, aspect, or strong lordship support.",
    "labha_lord_strength": "The 11th lord is strong by dignity, house placement, or association with wealth/trine lords.",
    "lakshmi_dhana": "The 9th lord, lagna lord, and wealth houses connect with benefic strength.",
    "balarishta": "Childhood-risk indicators arise from severe affliction to Lagna, Chandra, and their lords without benefic protection.",
    "arishta_bhanga": "Arishta indicators are cancelled by strong benefics, strong Lagna lord, or protective kendra/trikona influence.",
    "daridra": "Wealth houses/lords are afflicted or connected to dusthanas without compensating dhana support.",
    "grahana": "Surya or Chandra is closely joined Rahu or Ketu, with strength judged by sign, house, and benefic support.",
    "shakata": "Guru is in the 6th, 8th, or 12th from Chandra, with cancellation checked by kendra strength.",
    "mangala_dosha": "Mangala occupies classical marriage-risk houses from Lagna, Chandra, or Shukra, with cancellations reviewed.",
    "pitru_dosha_research": "Surya, 9th house, 9th lord, or ancestral indicators are strongly afflicted by malefics or nodes.",
    "kala_sarpa_contested": "All classical grahas lie between Rahu and Ketu; contested tradition requires separate review.",
    "visha": "Shani and Chandra are closely associated or mutually afflict each other, especially without benefic relief.",
    "pravrajya": "Four or more classical grahas gather in one sign/house, with the strongest graha shaping renunciation type.",
    "sannyasa": "Renunciation indicators repeat through strong 9th/12th houses, Saturn/Ketu influence, and clustered grahas.",
    "tapasvi": "Shani, Ketu, Lagna, 9th, or 12th factors show strong austerity links with reduced worldly attachment.",
    "brahma": "Guru, Shukra, and Budha or lords of key trines/kendras form a strong wisdom and protection pattern.",
    "maha_bhagya": "Birth conditions and luminaries align with classical gender/day-night/sign strength rules.",
    "bhagya": "The 9th house/lord and Guru receive strength and benefic association from Lagna or Chandra.",
    "mridanga": "Lagna lord or a strong graha occupies exaltation/own sign and receives kendra/trikona support.",
    "naga": "Nodal or serpentine indicators strongly influence Lagna, Chandra, or key houses; tradition review required.",
    "garuda": "Strong benefic/protective factors counter nodal or malefic affliction and support dharma houses.",
    "go": "Benefic strength connects Lagna, 4th, 9th, or wealth houses, indicating support and nourishment themes.",
    "vidyut": "Sharp benefic/intellectual links, especially Budha/Guru/Shukra with kendras/trikonas, indicate brilliance.",
    "pushkala": "Lagna lord and Chandra receive benefic support while wealth/status houses are strengthened.",
    "adhama": "Lagna, Chandra, or key lords are weak and afflicted without benefic correction.",
    "subha_vesi": "A natural benefic occupies the 2nd from Surya.",
    "asubha_vesi": "A natural malefic occupies the 2nd from Surya.",
    "adrogate_raja_research": "A rare authority-yoga variant requiring exact textual rule review before interpretation.",
    "kesari_variant": "Guru forms a protective kendra or strong relation with Chandra or Lagna.",
    "rajju_variant": "Grahas concentrate in movable signs or a Rajju-like Nabhasa pattern variant.",
    "parijata": "The dispositor chain of Lagna lord or key house lord becomes progressively strong by dignity and placement.",
    "vasishta": "Guru/Budha/benefic wisdom factors strongly influence Lagna, 5th, 9th, or Chandra.",
}
IMPLEMENTED_DETECTION_KEYS = {
    "dharma_karmadhipati_raja",
    "kendra_trikona_raja",
    "second_lord_eleventh_lord_link",
    "viparita_harsha",
    "viparita_sarala",
    "viparita_vimala",
    "dusthana_lord_exchange_viparita",
    "neecha_bhanga_raja",
    "amala",
    "amala_chandra",
    "grahana",
    "shakata",
    "mangala_dosha",
    "pravrajya",
    "sannyasa",
    "subha_vesi",
    "asubha_vesi",
    "lagna_lord_kendra_trikona_raja",
    "lakshmi",
    "lakshmi_dhana",
    "saraswati",
    "kalanidhi",
    "vasumati",
    "chandra_guru_dhana",
    "labha_lord_strength",
    "dhana_lagna_lord_second_eleventh",
    "dwi_dhana",
    "bahu_dhana",
    "raja_sambandha",
    "maharaja",
    "sri_natha",
    "bheri",
    "chamara",
    "kahala",
    "parvata",
    "sankha",
    "indra",
    "dhana_from_arudha",
    "balarishta",
    "arishta_bhanga",
    "daridra",
    "pitru_dosha_research",
    "kala_sarpa_contested",
    "visha",
    "tapasvi",
    "brahma",
    "maha_bhagya",
    "bhagya",
    "mridanga",
    "naga",
    "garuda",
    "go",
    "vidyut",
    "yogada_gl",
    "yogada_hl",
    "pushkala",
    "adhama",
    "adrogate_raja_research",
    "kesari_variant",
    "rajju_variant",
    "parijata",
    "vasishta",
}


def yoga_registry() -> list[dict[str, Any]]:
    yogas: list[dict[str, Any]] = []
    yogas.extend(
        _many(
            "panca_mahapurusha",
            "uncommon",
            ["Brhat Jataka", "BPHS with caution", "Phaladipika"],
            [
                ("ruchaka_mahapurusha", "Ruchaka Mahapurusha"),
                ("bhadra_mahapurusha", "Bhadra Mahapurusha"),
                ("hamsa_mahapurusha", "Hamsa Mahapurusha"),
                ("malavya_mahapurusha", "Malavya Mahapurusha"),
                ("shasha_mahapurusha", "Shasha Mahapurusha"),
            ],
            "Kendra strength of a qualifying graha in own or exaltation sign.",
            "signature_ready",
        )
    )
    yogas.extend(
        _many(
            "lunar_yoga",
            "common",
            ["Brhat Jataka", "Phaladipika"],
            [
                ("sunapha", "Sunapha"),
                ("anapha", "Anapha"),
                ("durudhara", "Durudhara"),
                ("kemadruma", "Kemadruma"),
                ("gaja_kesari", "Gaja Kesari"),
                ("chandra_mangala", "Chandra Mangala"),
            ],
            "Moon-centered combinations; strength and cancellation require full audit.",
            "partial_signature_ready",
        )
    )
    yogas.extend(
        _many(
            "solar_yoga",
            "common",
            ["Brhat Jataka", "Phaladipika"],
            [
                ("veshi", "Veshi"),
                ("voshi", "Voshi"),
                ("ubhayachari", "Ubhayachari"),
                ("budha_aditya", "Budha Aditya"),
            ],
            "Sun-centered combinations; combustion and dignity must be reviewed.",
            "partial_signature_ready",
        )
    )
    yogas.extend(
        _many(
            "raja_yoga",
            "uncommon",
            RAJA_SOURCE_PRIORITY,
            [
                ("dharma_karmadhipati_raja", "Dharma Karmadhipati Raja"),
                ("kendra_trikona_raja", "Kendra Trikona Raja"),
                ("lagna_lord_kendra_trikona_raja", "Lagna Lord Kendra/Trikona Raja"),
                ("raja_sambandha", "Raja Sambandha"),
                ("maharaja", "Maharaja"),
                ("sri_natha", "Sri Natha"),
                ("lakshmi", "Lakshmi"),
                ("saraswati", "Saraswati"),
                ("kalanidhi", "Kalanidhi"),
                ("bheri", "Bheri"),
                ("chamara", "Chamara"),
                ("kahala", "Kahala"),
                ("parvata", "Parvata"),
                ("sankha", "Sankha"),
            ],
            "Authority, support, learning, and rise combinations; public claims need exact rule.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "viparita_raja_yoga",
            "rare",
            RAJA_SOURCE_PRIORITY,
            [
                ("viparita_harsha", "Harsha Viparita Raja"),
                ("viparita_sarala", "Sarala Viparita Raja"),
                ("viparita_vimala", "Vimala Viparita Raja"),
                ("dusthana_lord_exchange_viparita", "Dusthana Lord Exchange Viparita"),
            ],
            "Difficult-house lordship patterns; interpret with humility and lived context.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "dhana_yoga",
            "uncommon",
            ["Phaladipika", "Saravali", "Sarvartha Cintamani"],
            [
                ("dhana_lagna_lord_second_eleventh", "Dhana Lagna/2nd/11th Link"),
                ("dwi_dhana", "Dwi Dhana"),
                ("bahu_dhana", "Bahu Dhana"),
                ("vasumati", "Vasumati"),
                ("indra", "Indra"),
                ("chandra_guru_dhana", "Chandra Guru Dhana"),
                ("dhana_from_arudha", "Dhana from Arudha"),
                ("labha_lord_strength", "Labha Lord Strength"),
                ("second_lord_eleventh_lord_link", "Second/Eleventh Lord Link"),
                ("lakshmi_dhana", "Lakshmi Dhana"),
            ],
            "Resource combinations; no financial advice or guarantee.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "arishta_and_bhanga",
            "uncommon",
            ["Brhat Jataka", "Phaladipika", "Jataka Parijata"],
            [
                ("balarishta", "Balarishta"),
                ("arishta_bhanga", "Arishta Bhanga"),
                ("daridra", "Daridra"),
                ("grahana", "Grahana"),
                ("shakata", "Shakata"),
                ("neecha_bhanga_raja", "Neecha Bhanga Raja"),
                ("mangala_dosha", "Mangala Dosha"),
                ("pitru_dosha_research", "Pitru Dosha Research"),
                ("kala_sarpa_contested", "Kala Sarpa Contested"),
                ("visha", "Visha"),
            ],
            "Difficult combinations; must be softened through Vaishnava remedy policy.",
            "catalog_only",
        )
    )
    yogas.extend(_nabhasa_yogas())
    yogas.extend(
        _many(
            "sannyasa_and_tapas",
            "rare",
            ["Brhat Jataka", "Phaladipika", "Prasna Marga"],
            [
                ("pravrajya", "Pravrajya"),
                ("sannyasa", "Sannyasa"),
                ("tapasvi", "Tapasvi"),
                ("brahma", "Brahma"),
                ("maha_bhagya", "Maha Bhagya"),
                ("bhagya", "Bhagya"),
            ],
            "Renunciation and austerity indications; align with guru, sadhu, and shastra.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "rare_named_yoga",
            "rare",
            BASE_SOURCE_PRIORITY,
            [
                ("mridanga", "Mridanga"),
                ("naga", "Naga"),
                ("garuda", "Garuda"),
                ("go", "Go"),
                ("vidyut", "Vidyut"),
                ("yogada_gl", "Yogada (GL)"),
                ("yogada_hl", "Yogada (HL)"),
                ("pushkala", "Pushkala"),
                ("amala", "Amala"),
                ("amala_chandra", "Amala from Chandra"),
                ("adhama", "Adhama"),
                ("subha_vesi", "Subha Vesi"),
                ("asubha_vesi", "Asubha Vesi"),
                ("adrogate_raja_research", "Adrogate Raja Research"),
                ("kesari_variant", "Kesari Variant"),
                ("rajju_variant", "Rajju Variant"),
                ("parijata", "Parijata"),
                ("vasishta", "Vasishta"),
            ],
            "Named rare yoga family; each requires exact textual mapping before publication.",
            "catalog_only",
        )
    )
    return [_with_common_policy(yoga, index) for index, yoga in enumerate(yogas, start=1)]


def yoga_catalog_overview() -> dict[str, Any]:
    yogas = yoga_registry()
    categories = Counter(str(yoga["category"]) for yoga in yogas)
    anchor_statuses = Counter(str(yoga.get("source_anchor_status") or "") for yoga in yogas)
    formula_statuses = Counter(str((yoga.get("formula") or {}).get("status") or "") for yoga in yogas)
    implemented_detection_count = sum(
        1
        for yoga in yogas
        if str(yoga.get("detection_status") or "") in {"signature_ready", "partial_signature_ready"}
    )
    return {
        "status": "research_catalog_started",
        "total_yogas": len(yogas),
        "rare_yogas": sum(1 for yoga in yogas if yoga["rarity"] == "rare"),
        "categories": dict(sorted(categories.items())),
        "anchor_coverage": {
            "all_yogas_have_source_anchor": all(bool(yoga.get("source_anchors")) for yoga in yogas),
            "exact_verse_verified": anchor_statuses.get("exact_verse_verified", 0),
            "statuses": dict(sorted(anchor_statuses.items())),
        },
        "formula_coverage": {
            "all_yogas_have_formula": all(bool((yoga.get("formula") or {}).get("description")) for yoga in yogas),
            "implemented_detection_count": implemented_detection_count,
            "statuses": dict(sorted(formula_statuses.items())),
        },
        "citation_policy": "required_for_public_interpretation",
        "public_release_policy": "catalog entries are research-only until source passages are approved",
    }


def yoga_catalog_import_payload() -> dict[str, Any]:
    return {
        "works": [
            {
                "slug": CATALOG_WORK_SLUG,
                "title": "Classical Yoga Research Catalog",
                "source_class": SourceWork.SourceClass.RESEARCH_ONLY,
                "review_status": ReviewStatus.RESEARCH_ONLY,
                "metadata": {
                    "seed": "yoga_catalog",
                    "source_role": "yoga_catalog_index",
                    "public_quote_status": "summary_anchor_only",
                },
            }
        ],
        "passages": [_passage_for_yoga(yoga) for yoga in yoga_registry()],
        "rules": [],
    }


def _nabhasa_yogas() -> list[dict[str, Any]]:
    yogas: list[dict[str, Any]] = []
    yogas.extend(
        _many(
            "nabhasa_ashraya",
            "rare",
            NABHASA_SOURCE_PRIORITY,
            [
                ("rajju_nabhasa", "Rajju Nabhasa"),
                ("musala_nabhasa", "Musala Nabhasa"),
                ("nala_nabhasa", "Nala Nabhasa"),
            ],
            "Nabhasa Ashraya sky-pattern family.",
            "signature_ready",
        )
    )
    yogas.extend(
        _many(
            "nabhasa_dala",
            "rare",
            NABHASA_SOURCE_PRIORITY,
            [
                ("mala_nabhasa", "Mala Nabhasa"),
                ("sarpa_nabhasa", "Sarpa Nabhasa"),
            ],
            "Nabhasa Dala sky-pattern family.",
            "signature_ready",
        )
    )
    yogas.extend(
        _many(
            "nabhasa_akriti",
            "rare",
            NABHASA_SOURCE_PRIORITY,
            [
                ("gada_nabhasa", "Gada Nabhasa"),
                ("shakata_nabhasa", "Shakata Nabhasa"),
                ("vihaga_nabhasa", "Vihaga Nabhasa"),
                ("shringataka_nabhasa", "Shringataka Nabhasa"),
                ("hala_nabhasa", "Hala Nabhasa"),
                ("vajra_nabhasa", "Vajra Nabhasa"),
                ("yava_nabhasa", "Yava Nabhasa"),
                ("kamala_nabhasa", "Kamala Nabhasa"),
                ("vapi_nabhasa", "Vapi Nabhasa"),
                ("yupa_nabhasa", "Yupa Nabhasa"),
                ("ishu_nabhasa", "Ishu/Shara Nabhasa"),
                ("shakti_nabhasa", "Shakti Nabhasa"),
                ("danda_nabhasa", "Danda Nabhasa"),
                ("nauka_nabhasa", "Nauka Nabhasa"),
                ("kuta_nabhasa", "Kuta Nabhasa"),
                ("chhatra_nabhasa", "Chhatra Nabhasa"),
                ("chapa_nabhasa", "Chapa/Dhanusha Nabhasa"),
                ("ardha_chandra_nabhasa", "Ardha Chandra Nabhasa"),
                ("chakra_nabhasa", "Chakra Nabhasa"),
                ("samudra_nabhasa", "Samudra Nabhasa"),
            ],
            "Nabhasa Akriti sky-pattern family.",
            "signature_ready",
        )
    )
    yogas.extend(
        _many(
            "nabhasa_sankhya",
            "rare",
            NABHASA_SOURCE_PRIORITY,
            [
                ("gola_nabhasa", "Gola Nabhasa"),
                ("yuga_nabhasa", "Yuga Nabhasa"),
                ("shula_nabhasa", "Shula Nabhasa"),
                ("kedara_nabhasa", "Kedara Nabhasa"),
                ("pasha_nabhasa", "Pasha Nabhasa"),
                ("dama_nabhasa", "Dama/Damini Nabhasa"),
                ("vina_nabhasa_variant", "Vina Nabhasa Variant"),
            ],
            "Nabhasa Sankhya sky-pattern family; variant names require source audit.",
            "signature_ready",
        )
    )
    return yogas


def _many(
    category: str,
    rarity: str,
    source_priority: list[str],
    pairs: list[tuple[str, str]],
    definition_scope: str,
    detection_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "key": key,
            "name": name,
            "category": category,
            "rarity": rarity,
            "source_priority": source_priority,
            "definition_scope": definition_scope,
            "detection_status": detection_status,
        }
        for key, name in pairs
    ]


def _with_common_policy(yoga: dict[str, Any], order: int) -> dict[str, Any]:
    item = deepcopy(yoga)
    item["order"] = order
    if str(item.get("key") or "") in IMPLEMENTED_DETECTION_KEYS:
        item["detection_status"] = "signature_ready"
    item["formula"] = _formula_for_yoga(item)
    item["source_anchors"] = list(item["formula"].get("source_anchors") or [])
    item["source_anchor_status"] = str(item["formula"].get("anchor_status") or "missing_curated_anchor")
    item["citation_policy"] = "required_for_public_interpretation"
    item["review_status"] = ReviewStatus.RESEARCH_ONLY
    item["vaishnava_guard"] = VAISHNAVA_GUARD
    item["public_explanation_outline"] = (
        "Name the yoga only as a researched classical indicator, explain the required "
        "formation, cite approved shastra passages, and frame practical guidance through "
        "Krishna-centered responsibility and service."
    )
    return item


def _formula_for_yoga(yoga: dict[str, Any]) -> dict[str, Any]:
    key = str(yoga.get("key") or "")
    formula = (
        FORMULA_BY_KEY.get(key)
        or NABHASA_FORMULAS.get(key)
        or MAHAPURUSHA_FORMULAS.get(key)
        or WORKING_FORMULAS_NEED_SOURCE_REVIEW.get(key)
        or str(yoga.get("definition_scope") or "")
    )
    detection_status = str(yoga.get("detection_status") or "")
    if detection_status in {"signature_ready", "partial_signature_ready"}:
        status = "implemented_working_formula"
    elif key in WORKING_FORMULAS_NEED_SOURCE_REVIEW or formula != str(yoga.get("definition_scope") or ""):
        status = "working_formula_needs_source_review"
    else:
        status = "formula_outline_needs_exact_rule"
    source_anchors = curated_yoga_source_anchors(
        key,
        category=str(yoga.get("category") or ""),
        formula=formula,
    )
    return {
        "description": formula,
        "status": status,
        "source_basis": FORMULA_SOURCE_BASIS,
        "source_anchors": source_anchors,
        "anchor_status": _source_anchor_status(source_anchors),
    }


def curated_yoga_source_anchors(
    key: str,
    *,
    category: str = "",
    formula: str = "",
) -> list[dict[str, Any]]:
    specific = deepcopy(CURATED_YOGA_SOURCE_ANCHORS.get(str(key) or "", []))
    anchors = specific or deepcopy(GROUP_YOGA_SOURCE_ANCHORS.get(str(category) or "", []))
    for anchor in anchors:
        anchor["condition_key"] = str(key)
        if formula and (
            not anchor.get("condition_formula")
            or str(anchor.get("condition_formula")).startswith("See the per-yoga")
        ):
            anchor["condition_formula"] = formula
    anchors.sort(key=_source_anchor_priority)
    return anchors


def _source_anchor_priority(anchor: dict[str, Any]) -> int:
    status = str(anchor.get("reference_status") or "")
    if status == "exact_verse_verified":
        return 0
    if status.startswith("exact_") or status.startswith("condition_equivalent") or "exact" in status:
        return 1
    if "mismatch" in status:
        return 3
    if "no_exact" in status or "not_found" in status:
        return 4
    return 2


def _source_anchor_status(anchors: list[dict[str, Any]]) -> str:
    if not anchors:
        return "missing_curated_anchor"
    statuses = {str(anchor.get("reference_status") or "") for anchor in anchors}
    if statuses == {"exact_verse_verified"}:
        return "exact_verse_verified"
    if any("exact" in status for status in statuses):
        return "curated_research_anchor"
    if any(
        "topic_anchor" in status
        or "name_mismatch" in status
        or "protective_metaphor" in status
        or "detector_review" in status
        for status in statuses
    ):
        return "curated_research_anchor"
    return "curated_anchor_needs_review"


def _passage_for_yoga(yoga: dict[str, Any]) -> dict[str, Any]:
    return {
        "work_slug": CATALOG_WORK_SLUG,
        "reference": f"Yoga catalog: {yoga['name']}",
        "body": (
            f"{yoga['name']} ({yoga['category']}): {yoga['definition_scope']} "
            "This is a research-only catalog anchor, not a public shastra quotation."
        ),
        "language_code": "en",
        "review_status": ReviewStatus.RESEARCH_ONLY,
        "metadata": {
            "seed": "yoga_catalog",
            "source_role": "yoga_research_anchor",
            "public_quote_status": "summary_anchor_only",
            "yoga_key": yoga["key"],
            "category": yoga["category"],
            "rarity": yoga["rarity"],
            "source_priority": yoga["source_priority"],
            "detection_status": yoga["detection_status"],
            "citation_policy": yoga["citation_policy"],
            "vaishnava_guard": yoga["vaishnava_guard"],
            "formula": yoga["formula"],
            "source_anchors": yoga.get("source_anchors") or [],
            "source_anchor_status": yoga.get("source_anchor_status") or "missing_curated_anchor",
        },
    }
