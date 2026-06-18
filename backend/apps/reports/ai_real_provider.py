from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from typing import Any

from django.conf import settings

from .ai_gateway import AiGatewayInputError, AiGatewayProviderError, AiProviderTimeout


class InsufficientVerifiedEvidence(AiGatewayInputError):
    pass


def citation_count(request: dict[str, Any]) -> int:
    return sum(len(item.get("citation_chains") or []) for item in request.get("items") or [])


def enforce_minimum_coverage(request: dict[str, Any]) -> None:
    min_items = int(getattr(settings, "AI_REPORT_GATEWAY_MIN_ELIGIBLE_ITEMS", 2))
    min_citations = int(getattr(settings, "AI_REPORT_GATEWAY_MIN_CITATION_CHAINS", 2))
    if len(request.get("items") or []) < min_items or citation_count(request) < min_citations:
        raise InsufficientVerifiedEvidence("insufficient_verified_evidence")


def build_provider_payload(ai_report_request: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "task": "jyotish_report_response",
        "report_type_id": ai_report_request["report_type_id"],
        "report_recipe_id": ai_report_request["report_recipe_id"],
        "language": ai_report_request["language"],
        "audience": ai_report_request["audience"],
        "subject": "subject",
        "instructions": [
            "Use only the provided evidence items.",
            "Do not infer from excluded summary.",
            "Do not add rules from model memory.",
            "Every thesis must cite at least one evidence item.",
            "Every thesis must use an allowed citation chain.",
            "If evidence is insufficient, state limitations.",
            "Return only JSON matching AiReportResponse schema.",
            "Do not give medical, legal, or financial guarantees.",
            "Do not claim events are inevitable.",
            "Do not label a person as bad, dangerous, doomed, or equivalent.",
        ],
        "items": [
            {
                "evidence_item_id": item["evidence_item_id"],
                "label": item["label"],
                "kind": item["kind"],
                "factor_id": item["factor_id"],
                "citation_chains": item["citation_chains"],
            }
            for item in ai_report_request.get("items", [])
        ],
        "coverage_summary": ai_report_request["excluded_summary"],
        "limits": {
            "max_theses": int(getattr(settings, "AI_REPORT_GATEWAY_MAX_THESES", 8)),
            "max_thesis_chars": int(getattr(settings, "AI_REPORT_GATEWAY_MAX_THESIS_CHARS", 900)),
        },
    }


def build_provider_http_body(provider_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": getattr(settings, "AI_REAL_PROVIDER_MODEL", "gpt-5.2"),
        "input": json.dumps(provider_payload, ensure_ascii=False, sort_keys=True),
    }


def post_json_bytes(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: int,
    max_response_bytes: int,
) -> bytes:
    body = json.dumps(build_provider_http_body(payload), ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read(max_response_bytes + 1)
    except socket.timeout as exc:
        raise AiProviderTimeout("provider timeout") from exc
    except urllib.error.URLError as exc:
        raise AiGatewayProviderError("provider network error") from exc
    if len(data) > max_response_bytes:
        raise AiGatewayProviderError("provider response too large")
    return data


def parse_provider_response(raw: bytes) -> dict[str, Any]:
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AiGatewayProviderError("provider response is not valid JSON") from exc

    if isinstance(data, dict) and data.get("schema_version") == 1 and "theses" in data:
        return data

    output_text = data.get("output_text") if isinstance(data, dict) else None
    if isinstance(output_text, str):
        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise AiGatewayProviderError("provider output_text is not valid JSON") from exc
        if isinstance(parsed, dict):
            return parsed

    choices = data.get("choices") if isinstance(data, dict) else None
    if isinstance(choices, list) and choices:
        content = choices[0].get("message", {}).get("content")
        if isinstance(content, str):
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as exc:
                raise AiGatewayProviderError("provider message content is not valid JSON") from exc
            if isinstance(parsed, dict):
                return parsed

    raise AiGatewayProviderError("provider response does not contain AiReportResponse JSON")


class RealAiProvider:
    provider_id = "real"

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        api_key = str(getattr(settings, "AI_REAL_PROVIDER_API_KEY", "") or "").strip()
        if not api_key:
            raise AiGatewayProviderError("real provider api key is not configured")
        enforce_minimum_coverage(request)
        provider_payload = build_provider_payload(request)
        raw = post_json_bytes(
            str(getattr(settings, "AI_REAL_PROVIDER_URL", "")).strip(),
            provider_payload,
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            int(getattr(settings, "AI_REPORT_GATEWAY_TIMEOUT_SECONDS", 15)),
            int(getattr(settings, "AI_REPORT_GATEWAY_MAX_RESPONSE_BYTES", 65536)),
        )
        response = parse_provider_response(raw)
        response["provider"] = "real"
        return response
