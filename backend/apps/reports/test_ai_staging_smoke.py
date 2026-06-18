import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.test import override_settings

from apps.charts.models import BirthProfile, ChartCalculation, Place
from apps.reports.ai_real_provider import parse_provider_response


def provider_response_from_payload(provider_payload):
    item = provider_payload["items"][0]
    return {
        "schema_version": 1,
        "provider": "real",
        "report_type_id": provider_payload["report_type_id"],
        "report_recipe_id": provider_payload["report_recipe_id"],
        "theses": [
            {
                "id": f"real.thesis.01.{item['evidence_item_id']}",
                "title": "Validated staging thesis",
                "body": "A limited staging response based only on verified evidence.",
                "evidence_item_ids": [item["evidence_item_id"]],
                "citations": [{"evidence_item_id": item["evidence_item_id"], **item["citation_chains"][0]}],
                "confidence": "medium",
            }
        ],
    }


@pytest.mark.django_db
@override_settings(
    DEBUG=True,
    AI_REPORTS_ENABLED=True,
    AI_PROVIDER="real",
    AI_REAL_PROVIDER_ENABLED=True,
    AI_REPORTS_PUBLIC_UI=False,
    AI_REPORTS_STAGING_ONLY=True,
    AI_REAL_PROVIDER_API_KEY="test-key",
    AI_REAL_PROVIDER_MODEL="test-model",
)
def test_smoke_ai_staging_outputs_safe_receipt_and_cleans_temp_data(monkeypatch):
    from apps.reports import ai_real_provider

    captured_payloads = []

    def transport(url, payload, headers, timeout, max_response_bytes):
        captured_payloads.append(payload)
        return json.dumps(provider_response_from_payload(payload)).encode("utf-8")

    monkeypatch.setattr(ai_real_provider, "post_json_bytes", transport)

    stdout = StringIO()
    call_command("smoke_ai_staging", stdout=stdout)
    receipt = json.loads(stdout.getvalue())

    assert len(captured_payloads) == 1
    assert receipt["environment"] == "staging"
    assert receipt["providerAlias"] == "real"
    assert receipt["modelAlias"] == "test-model"
    assert receipt["status"] == "accepted"
    assert receipt["eligibleItemCount"] >= 2
    assert receipt["citationChainCount"] >= 2
    assert receipt["thesisCount"] == 1
    assert receipt["responseValidation"] == "passed"
    assert receipt["citationValidation"] == "passed"
    assert receipt["piiAudit"] == "passed"
    assert receipt["rawContentStored"] is False

    serialized_receipt = json.dumps(receipt, ensure_ascii=False)
    for forbidden in ["prompt", "rawPrompt", "rawResponse", "birth", "Private", "test-key"]:
        assert forbidden not in serialized_receipt

    assert not BirthProfile.objects.filter(display_name__startswith="ai-staging-smoke").exists()
    assert not Place.objects.filter(external_id__startswith="ai-staging-smoke").exists()
    assert not ChartCalculation.objects.filter(calculation_version="ai-staging-smoke").exists()


def test_parse_provider_response_accepts_responses_api_output_text_array():
    response = provider_response_from_payload(
        {
            "report_type_id": "personal_overview",
            "report_recipe_id": "personal_overview",
            "items": [
                {
                    "evidence_item_id": "entity.house.1",
                    "citation_chains": [
                        {
                            "rule_id": "rule",
                            "passage_id": "passage",
                            "source_id": "source",
                            "citation_label": "BPHS",
                        }
                    ],
                }
            ],
        }
    )
    raw = json.dumps(
        {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(response),
                        }
                    ],
                }
            ]
        }
    ).encode("utf-8")

    assert parse_provider_response(raw)["theses"][0]["evidence_item_ids"] == ["entity.house.1"]
