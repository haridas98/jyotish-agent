from __future__ import annotations

from django.db import models


class GeneratedAnalysisDraft(models.Model):
    kind = models.CharField(max_length=64)
    review_status = models.CharField(max_length=32, default="draft")
    source_policy = models.CharField(max_length=64, default="citation_first")
    provider = models.CharField(max_length=64, blank=True)
    model = models.CharField(max_length=128, blank=True)
    input_snapshot = models.JSONField(default=dict, blank=True)
    packet_snapshot = models.JSONField(default=dict, blank=True)
    output_json = models.JSONField(default=dict, blank=True)
    prompt_markdown = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["kind", "review_status"], name="reports_gen_kind_89d737_idx"),
            models.Index(fields=["created_at"], name="reports_gen_created_8d2ced_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.kind} {self.review_status} #{self.pk}"
