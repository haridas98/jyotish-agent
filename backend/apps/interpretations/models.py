from __future__ import annotations

from django.db import models

from apps.sources.models import ReviewStatus, SourcePassage


class InterpretationRule(models.Model):
    slug = models.SlugField(max_length=180, unique=True)
    title = models.CharField(max_length=255)
    condition = models.JSONField(default=dict)
    priority = models.PositiveIntegerField(default=100)
    passages = models.ManyToManyField(SourcePassage, blank=True)
    review_status = models.CharField(
        max_length=32,
        choices=ReviewStatus.choices,
        default=ReviewStatus.DRAFT,
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "slug"]
        indexes = [models.Index(fields=["review_status", "priority"])]

    def __str__(self) -> str:
        return self.title


class InterpretationBlock(models.Model):
    rule = models.ForeignKey(
        InterpretationRule,
        on_delete=models.CASCADE,
        related_name="blocks",
        null=True,
        blank=True,
    )
    section = models.CharField(max_length=128)
    title = models.CharField(max_length=255)
    body = models.TextField()
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
        indexes = [
            models.Index(fields=["section", "language_code"]),
            models.Index(fields=["review_status"]),
        ]


class RemedyPolicy(models.Model):
    slug = models.SlugField(max_length=180, unique=True)
    classical_trigger = models.CharField(max_length=255)
    blocked_advice = models.TextField(blank=True)
    vaishnava_reframe = models.TextField()
    passages = models.ManyToManyField(SourcePassage, blank=True)
    review_status = models.CharField(
        max_length=32,
        choices=ReviewStatus.choices,
        default=ReviewStatus.DRAFT,
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "remedy policies"
        indexes = [models.Index(fields=["review_status"])]

    def __str__(self) -> str:
        return self.slug

