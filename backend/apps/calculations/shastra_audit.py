from __future__ import annotations

from typing import Any

CALCULATION_SHASTRA_AUDIT: list[dict[str, Any]] = [
    {
        "key": "rashi_nakshatra_navamsa",
        "label": "Rashi, nakshatra, pada, navamsa",
        "source_priority": ["surya-siddhanta", "brhat-jataka", "jataka-parijata"],
        "source_basis": "Siddhanta coordinate math with classical rashi, nakshatra, pada and navamsa divisions.",
        "authority_status": "source_backed",
        "implementation_status": "calculated",
        "review_status": "research_only",
        "public_claim": "calculated_source_backed",
        "can_generate_client_interpretation": True,
    },
    {
        "key": "vargas_d2_d60",
        "label": "Shodasha vargas D2-D60",
        "source_priority": ["brhat-jataka", "hora-sara", "saravali", "brhat-parashara-hora-shastra"],
        "source_basis": "Classical divisional-chart rules; modern BPHS variants are used only when no older conflict is open.",
        "authority_status": "source_backed_with_bphs_caution",
        "implementation_status": "calculated_needs_text_rule_review",
        "review_status": "research_only",
        "public_claim": "calculated_not_interpretively_verified",
        "can_generate_client_interpretation": False,
    },
    {
        "key": "panchanga",
        "label": "Tithi, vara, yoga, karana",
        "source_priority": ["surya-siddhanta", "kalaprakasika", "muhurta-chintamani"],
        "source_basis": "Solar-lunar angle divisions and weekday rules used by standard panchanga and muhurta texts.",
        "authority_status": "source_backed",
        "implementation_status": "calculated_needs_fixture_audit",
        "review_status": "research_only",
        "public_claim": "calculated_source_backed",
        "can_generate_client_interpretation": True,
    },
    {
        "key": "vimshottari",
        "label": "Vimshottari dasha",
        "source_priority": ["jataka-parijata", "phaladipika", "laghu-parashari", "brhat-parashara-hora-shastra"],
        "source_basis": "Udu dasha from Moon nakshatra with 120-year cycle and classical planetary sequence.",
        "authority_status": "source_backed_with_bphs_caution",
        "implementation_status": "calculated_needs_text_rule_review",
        "review_status": "research_only",
        "public_claim": "calculated_not_interpretively_verified",
        "can_generate_client_interpretation": False,
    },
    {
        "key": "avasthas",
        "label": "Baladi avastha",
        "source_priority": ["phaladipika", "jataka-parijata", "brhat-parashara-hora-shastra"],
        "source_basis": "Degree-band avastha rules with odd/even sign direction.",
        "authority_status": "source_backed_with_bphs_caution",
        "implementation_status": "calculated_needs_text_rule_review",
        "review_status": "research_only",
        "public_claim": "calculated_not_interpretively_verified",
        "can_generate_client_interpretation": False,
    },
    {
        "key": "ashtakavarga",
        "label": "Bhinna and Sarva Ashtakavarga",
        "source_priority": ["brhat-jataka", "ashtakavarga-bv-raman", "jhora"],
        "source_basis": "Brhat Jataka chapter IX benefic-place rules with standard 337-bindu SAV total.",
        "authority_status": "source_backed",
        "implementation_status": "calculated_jhora_profile_diff_open",
        "review_status": "research_only",
        "public_claim": "source_backed_not_jhora_verified",
        "can_generate_client_interpretation": False,
        "blocker": "JHora and service witnesses still disagree on selected BAV cells; settings/profile audit remains open.",
    },
    {
        "key": "shadbala",
        "label": "Shadbala",
        "source_priority": ["graha-and-bhava-balas", "shadbala-rahasyam", "brhat-parashara-hora-shastra"],
        "source_basis": "Sixfold strength framework; current code implements only selected components.",
        "authority_status": "source_backed_with_bphs_caution",
        "implementation_status": "partial",
        "review_status": "research_only",
        "public_claim": "partial_do_not_interpret_as_full_shadbala",
        "can_generate_client_interpretation": False,
        "blocker": "Full sthana, dig, kala, chesta, naisargika and drik subcomponents need text and JHora parity audit.",
    },
    {
        "key": "vimshopaka",
        "label": "Vimshopaka bala",
        "source_priority": ["brhat-parashara-hora-shastra", "varga-tradition-review"],
        "source_basis": "Varga-weighted strength rules; weights vary by tradition and must be pinned before public use.",
        "authority_status": "needs_tradition_decision",
        "implementation_status": "temporary_proxy",
        "review_status": "research_only",
        "public_claim": "draft_proxy_do_not_interpret",
        "can_generate_client_interpretation": False,
        "blocker": "Replace own/exaltation proxy with a reviewed varga-weight table.",
    },
    {
        "key": "yogas",
        "label": "Detected yogas",
        "source_priority": ["brhat-jataka", "phaladipika", "jataka-parijata", "saravali", "sarvartha-cintamani"],
        "source_basis": "Named yoga conditions from older Jataka texts; rare yoga catalog is citation-gated.",
        "authority_status": "source_backed",
        "implementation_status": "partial_detection_needs_citations",
        "review_status": "research_only",
        "public_claim": "detected_conditions_not_full_prediction",
        "can_generate_client_interpretation": False,
        "blocker": "Each yoga needs exact verse mapping and cancellation/strength conditions before final interpretation.",
    },
    {
        "key": "argala",
        "label": "Argala",
        "source_priority": ["jaimini-sutra", "jaimini-commentarial-tradition"],
        "source_basis": "Jaimini argala and obstruction houses.",
        "authority_status": "source_backed_but_tradition_sensitive",
        "implementation_status": "partial",
        "review_status": "research_only",
        "public_claim": "structural_argala_only",
        "can_generate_client_interpretation": False,
    },
    {
        "key": "upagrahas",
        "label": "Gulika and upagrahas",
        "source_priority": ["kalaprakasika", "muhurta-chintamani", "jhora"],
        "source_basis": "Day/night segment methods for Gulika and related upagrahas.",
        "authority_status": "source_backed",
        "implementation_status": "partial_gulika_only",
        "review_status": "research_only",
        "public_claim": "gulika_calculated_upagrahas_partial",
        "can_generate_client_interpretation": False,
        "blocker": "Mandi, Yamakantaka and remaining upagrahas need selected tradition and fixture audit.",
    },
    {
        "key": "special_points",
        "label": "Indu lagna and special points",
        "source_priority": ["classical-point-source-review", "jhora"],
        "source_basis": "Indu lagna and special point formulas need exact source pinning before interpretation.",
        "authority_status": "needs_source_mapping",
        "implementation_status": "partial",
        "review_status": "research_only",
        "public_claim": "calculated_needs_source_audit",
        "can_generate_client_interpretation": False,
    },
    {
        "key": "transits",
        "label": "Gochar transits",
        "source_priority": ["gochar-phaladipika", "brhat-jataka", "jataka-parijata"],
        "source_basis": "Transit houses from Lagna/Moon with benefic and malefic movement rules.",
        "authority_status": "source_backed",
        "implementation_status": "baseline_api_ready",
        "review_status": "research_only",
        "public_claim": "api_ready_needs_prediction_rules",
        "can_generate_client_interpretation": False,
    },
    {
        "key": "compatibility",
        "label": "Compatibility",
        "source_priority": ["muhurta-chintamani", "vivaha-tradition-review", "teacher-review"],
        "source_basis": "Ashtakuta-style matching plus tradition review for Vaishnava marriage guidance.",
        "authority_status": "source_backed_but_pastoral_review_required",
        "implementation_status": "baseline_ashtakuta",
        "review_status": "research_only",
        "public_claim": "baseline_not_final_marriage_guidance",
        "can_generate_client_interpretation": False,
    },
    {
        "key": "muhurta",
        "label": "Muhurta",
        "source_priority": ["kalaprakasika", "muhurta-chintamani", "brhat-samhita"],
        "source_basis": "Electional rules from Kalaprakasika, Muhurta Chintamani and Brhat Samhita.",
        "authority_status": "source_backed",
        "implementation_status": "baseline_scoring",
        "review_status": "research_only",
        "public_claim": "baseline_not_final_election",
        "can_generate_client_interpretation": False,
    },
]

_REQUIRED_FIELDS = {
    "key",
    "label",
    "source_priority",
    "source_basis",
    "authority_status",
    "implementation_status",
    "review_status",
    "public_claim",
    "can_generate_client_interpretation",
}


def validate_shastra_audit(items: list[dict[str, Any]] | None = None) -> list[str]:
    rows = items or CALCULATION_SHASTRA_AUDIT
    problems: list[str] = []
    seen: set[str] = set()

    for row in rows:
        key = str(row.get("key") or "<missing>")
        missing = sorted(field for field in _REQUIRED_FIELDS if field not in row)
        if missing:
            problems.append(f"{key}: missing {', '.join(missing)}")
        if key in seen:
            problems.append(f"{key}: duplicate key")
        seen.add(key)
        if not row.get("source_priority"):
            problems.append(f"{key}: source_priority is empty")
        if not str(row.get("source_basis") or "").strip():
            problems.append(f"{key}: source_basis is empty")
        if row.get("authority_status") == "source_backed" and row.get("review_status") not in {
            "research_only",
            "reviewed",
            "approved",
        }:
            problems.append(f"{key}: source-backed row has invalid review_status")
        if row.get("can_generate_client_interpretation") and row.get("review_status") not in {
            "research_only",
            "reviewed",
            "approved",
        }:
            problems.append(f"{key}: client interpretation requires review_status")
        if row.get("public_claim") == "verified" and row.get("review_status") != "approved":
            problems.append(f"{key}: verified claim requires approved review")

    return problems


def shastra_audit_payload() -> dict[str, Any]:
    if problems := validate_shastra_audit():
        raise ValueError("; ".join(problems))

    items = [dict(item) for item in CALCULATION_SHASTRA_AUDIT]
    return {
        "policy": "shastra_first_black_box_second",
        "authority_order": [
            "older shastra and reviewed parampara instruction",
            "astronomical ephemeris and timezone audit",
            "JHora and external services as black-box witnesses",
            "internal regression fixtures",
        ],
        "bphs_policy": (
            "Modern BPHS is useful but not accepted blindly where older sources or "
            "Shyamasundara Dasa's authenticity cautions create a conflict."
        ),
        "summary": {
            "total": len(items),
            "source_backed": sum(1 for item in items if str(item["authority_status"]).startswith("source_backed")),
            "client_interpretation_allowed": sum(
                1 for item in items if item["can_generate_client_interpretation"]
            ),
            "partial_or_audit": sum(1 for item in items if _is_partial_or_audit(item)),
            "needs_text_rule_review": sum(
                1 for item in items if "needs_text_rule_review" in str(item["implementation_status"])
            ),
        },
        "items": items,
        "items_by_key": {item["key"]: item for item in items},
    }


def _is_partial_or_audit(item: dict[str, Any]) -> bool:
    status = str(item["implementation_status"])
    return any(marker in status for marker in ("partial", "temporary", "needs", "diff_open", "baseline"))
