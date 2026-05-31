from __future__ import annotations

from django.db import models


class ReviewStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    RESEARCH_ONLY = "research_only", "Research only"
    APPROVED = "approved", "Approved"
    BLOCKED = "blocked", "Blocked"


class SourceWork(models.Model):
    class SourceClass(models.TextChoices):
        CANONICAL_PRABHUPADA = "canonical_prabhupada", "Canonical Prabhupada"
        CANONICAL_GAUDIYA = "canonical_gaudiya", "Canonical Gaudiya"
        JYOTISH_SHASTRA = "jyotish_shastra", "Jyotish shastra"
        TEACHER_REFERENCE = "teacher_reference", "Teacher reference"
        RESEARCH_ONLY = "research_only", "Research only"

    slug = models.SlugField(max_length=160, unique=True)
    title = models.CharField(max_length=255)
    source_class = models.CharField(max_length=64, choices=SourceClass.choices)
    author = models.CharField(max_length=255, blank=True)
    edition = models.CharField(max_length=255, blank=True)
    language_code = models.CharField(max_length=16, default="en")
    source_url = models.URLField(blank=True)
    review_status = models.CharField(
        max_length=32,
        choices=ReviewStatus.choices,
        default=ReviewStatus.DRAFT,
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class SourcePassage(models.Model):
    work = models.ForeignKey(SourceWork, on_delete=models.CASCADE, related_name="passages")
    reference = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    language_code = models.CharField(max_length=16, default="en")
    review_status = models.CharField(
        max_length=32,
        choices=ReviewStatus.choices,
        default=ReviewStatus.DRAFT,
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("work", "reference", "language_code")]
        indexes = [
            models.Index(fields=["review_status"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self) -> str:
        return f"{self.work}: {self.reference}"


class VLCitationLink(models.Model):
    passage = models.ForeignKey(
        SourcePassage,
        on_delete=models.CASCADE,
        related_name="vl_links",
        null=True,
        blank=True,
    )
    vl_work_id = models.BigIntegerField(null=True, blank=True)
    vl_text_unit_id = models.BigIntegerField(null=True, blank=True)
    vl_text_id = models.BigIntegerField(null=True, blank=True)
    public_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["vl_work_id"]),
            models.Index(fields=["vl_text_unit_id"]),
            models.Index(fields=["vl_text_id"]),
        ]

