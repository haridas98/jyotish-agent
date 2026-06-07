import io
import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.reports.draft_generation import DraftGenerationUnavailable


@override_settings(
    QWEN_MODEL="qwen-test",
    FREE_DEEPSEEK_MODEL="deepseek-test",
    NEMOTRON_MODEL="nemotron-test",
)
def test_smoke_ai_helpers_command_reports_qwen_deepseek_and_nemotron(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.qwen_generation.qwen_chat_completions_client",
        lambda: lambda prompt: json.dumps(
            {"language": "ru", "sections": [{"title": "Smoke", "body": "qwen ok", "citation_titles": []}]}
        ),
    )
    monkeypatch.setattr(
        "apps.reports.deepseek_generation.free_deepseek_chat_client",
        lambda: lambda prompt: json.dumps(
            {"language": "ru", "sections": [{"title": "Smoke", "body": "deepseek ok", "citation_titles": []}]}
        ),
    )
    monkeypatch.setattr(
        "apps.reports.nemotron_generation.nemotron_chat_completions_client",
        lambda: lambda prompt: json.dumps(
            {"language": "ru", "sections": [{"title": "Smoke", "body": "nemotron ok", "citation_titles": []}]}
        ),
    )

    stdout = io.StringIO()
    call_command("smoke_ai_helpers", "--providers", "qwen,free_deepseek,nemotron", stdout=stdout)

    payload = json.loads(stdout.getvalue())
    assert payload["status"] == "ok"
    assert payload["results"] == [
        {
            "status": "ok",
            "provider": "qwen",
            "model": "qwen-test",
            "section_count": 1,
            "message_excerpt": "qwen ok",
        },
        {
            "status": "ok",
            "provider": "free_deepseek",
            "model": "deepseek-test",
            "section_count": 1,
            "message_excerpt": "deepseek ok",
        },
        {
            "status": "ok",
            "provider": "nemotron",
            "model": "nemotron-test",
            "section_count": 1,
            "message_excerpt": "nemotron ok",
        },
    ]


@override_settings(QWEN_MODEL="qwen-test", FREE_DEEPSEEK_MODEL="deepseek-test")
def test_smoke_ai_helpers_command_can_continue_on_error(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.qwen_generation.qwen_chat_completions_client",
        lambda: lambda prompt: (_ for _ in ()).throw(DraftGenerationUnavailable("qwen down")),
    )
    monkeypatch.setattr(
        "apps.reports.deepseek_generation.free_deepseek_chat_client",
        lambda: lambda prompt: json.dumps(
            {"language": "ru", "sections": [{"title": "Smoke", "body": "deepseek ok", "citation_titles": []}]}
        ),
    )

    stdout = io.StringIO()
    call_command(
        "smoke_ai_helpers",
        "--providers",
        "qwen,free_deepseek",
        "--continue-on-error",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    assert payload["status"] == "failed"
    assert payload["results"][0] == {
        "status": "failed",
        "provider": "qwen",
        "model": "qwen-test",
        "error": "qwen down",
    }
    assert payload["results"][1]["status"] == "ok"


@override_settings(NEMOTRON_MODEL="nemotron-test")
def test_smoke_ai_helpers_command_accepts_nemotron(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.nemotron_generation.nemotron_chat_completions_client",
        lambda: lambda prompt: json.dumps(
            {"language": "ru", "sections": [{"title": "Smoke", "body": "nemotron ok", "citation_titles": []}]}
        ),
    )

    stdout = io.StringIO()
    call_command("smoke_ai_helpers", "--providers", "nemotron", stdout=stdout)

    payload = json.loads(stdout.getvalue())
    assert payload["status"] == "ok"
    assert payload["results"] == [
        {
            "status": "ok",
            "provider": "nemotron",
            "model": "nemotron-test",
            "section_count": 1,
            "message_excerpt": "nemotron ok",
        }
    ]


def test_smoke_ai_helpers_command_fails_on_unknown_provider():
    with pytest.raises(CommandError, match="Unknown AI helper provider"):
        call_command("smoke_ai_helpers", "--providers", "qwen,unknown")
