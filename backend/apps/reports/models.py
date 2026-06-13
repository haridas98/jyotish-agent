from __future__ import annotations

from django.conf import settings
from django.db import models


class GeneratedAnalysisDraft(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_analysis_drafts",
    )
    parent_analysis = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_records",
    )
    kind = models.CharField(max_length=64)
    review_status = models.CharField(max_length=32, default="draft")
    source_policy = models.CharField(max_length=64, default="citation_first")
    provider = models.CharField(max_length=64, blank=True)
    model = models.CharField(max_length=128, blank=True)
    input_snapshot = models.JSONField(default=dict, blank=True)
    packet_snapshot = models.JSONField(default=dict, blank=True)
    output_json = models.JSONField(default=dict, blank=True)
    engine_label = models.CharField(max_length=160, blank=True)
    first_section_title = models.CharField(max_length=240, blank=True)
    excerpt = models.TextField(blank=True)
    section_count = models.PositiveIntegerField(default=0)
    prompt_markdown = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "kind", "created_at"], name="reports_gen_user_kind_idx"),
            models.Index(fields=["parent_analysis", "user", "created_at"], name="reports_gen_parent_chat_idx"),
            models.Index(fields=["kind", "review_status"], name="reports_gen_kind_89d737_idx"),
            models.Index(fields=["created_at"], name="reports_gen_created_8d2ced_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.kind} {self.review_status} #{self.pk}"

    def save(self, *args, **kwargs):
        self.refresh_preview_fields()
        super().save(*args, **kwargs)

    def refresh_preview_fields(self) -> None:
        output = self.output_json if isinstance(self.output_json, dict) else {}
        sections = output.get("sections") if isinstance(output.get("sections"), list) else []
        first_section = sections[0] if sections and isinstance(sections[0], dict) else {}

        self.engine_label = str(output.get("engine_label") or "")[:160]
        self.section_count = len(sections)
        self.first_section_title = str(first_section.get("title") or "")[:240]

        if first_section:
            self.excerpt = str(first_section.get("body") or "")[:720]
        elif self.kind.endswith("_chat"):
            self.excerpt = str(output.get("answer") or "")[:720]
        else:
            self.excerpt = ""
