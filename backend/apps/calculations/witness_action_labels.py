from __future__ import annotations


ACTION_LABELS = {
    "set_review_status_jhora_verified_after_manual_review": "Run review preflight",
    "add_reviewer_and_reviewed_at": "Add reviewer after manual review",
    "mark_jhora_witness_reviewed": "Mark JHora reviewed after ACK",
    "mark_jhora_witness_reviewed_with_ack_diff_open": "Mark JHora reviewed after diff ACK",
    "mark_parashara_light_witness_reviewed": "Mark PL reviewed after ACK",
    "attach_jhora_screenshots": "Attach JHora screenshots",
    "capture_jhora_witness_batch_exports_or_attach_jhora_complete_calculations": "Capture JHora complete export",
    "capture_jhora_expected_values_or_complete_calculations": "Capture JHora expected values",
    "record_jhora_settings_and_timezone_dst_evidence": "Record JHora settings and DST evidence",
    "attach_pl_screenshots": "Attach PL screenshots",
    "capture_parashara_light_ui_state_or_attach_ui_state": "Capture PL UI state",
    "fill_pl_manual_witness_values": "Fill PL manual witness values",
    "record_pl_settings_and_timezone_dst_evidence": "Record PL settings and DST evidence",
    "attach_pl_witness_packet_or_manual_values": "Attach PL witness values",
    "build_jhora_witness_batch_packets": "Build JHora witness packet",
    "capture_jhora_witness_batch_exports": "Capture JHora witness export",
    "build_parashara_light_witness_batch_packets": "Build PL witness packet",
}


def suggested_action_label(action: str) -> str:
    action = str(action or "")
    return ACTION_LABELS.get(action, action.replace("_", " ")) if action else ""


def suggested_action_labels(actions: list[str]) -> list[str]:
    return [suggested_action_label(action) for action in actions]
