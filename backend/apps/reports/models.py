from __future__ import annotations

from django.conf import settings
from django.apps import apps
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class GeneratedAnalysisProfileLink(models.Model):
    analysis = models.ForeignKey(
        GeneratedAnalysisDraft,
        on_delete=models.CASCADE,
        related_name="profile_links",
    )
    profile = models.ForeignKey(
        "charts.BirthProfile",
        on_delete=models.CASCADE,
        related_name="analysis_links",
    )
    role = models.CharField(max_length=32, default="primary")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["analysis", "profile", "role"], name="unique_analysis_profile_role"),
        ]
        indexes = [
            models.Index(fields=["profile", "analysis"], name="reports_profile_analysis_idx"),
            models.Index(fields=["analysis", "role"], name="reports_analysis_role_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.analysis_id}:{self.profile_id}:{self.role}"


def analysis_profile_links_from_snapshot(snapshot: object) -> list[tuple[int, str]]:
    if not isinstance(snapshot, dict):
        return []
    links: list[tuple[int, str]] = []

    def add(value: object, role: str) -> None:
        try:
            profile_id = int(str(value))
        except (TypeError, ValueError):
            return
        if profile_id <= 0:
            return
        item = (profile_id, role)
        if item not in links:
            links.append(item)

    add(snapshot.get("profile_id"), "primary")
    for key in ("person_a", "person_b"):
        person = snapshot.get(key)
        if isinstance(person, dict):
            add(person.get("profile_id"), key)
    related_ids = snapshot.get("related_profile_ids")
    if isinstance(related_ids, list):
        for related_id in related_ids:
            add(related_id, "related")
    related_context = snapshot.get("related_profile_context")
    if isinstance(related_context, list):
        for item in related_context:
            profile = item.get("profile") if isinstance(item, dict) else None
            if isinstance(profile, dict):
                add(profile.get("id"), "related")
    return links


def refresh_generated_analysis_profile_links(analysis: GeneratedAnalysisDraft) -> None:
    BirthProfile = apps.get_model("charts", "BirthProfile")
    links = analysis_profile_links_from_snapshot(analysis.input_snapshot)
    profile_ids = {profile_id for profile_id, _role in links}
    existing_profile_ids = set(BirthProfile.objects.filter(id__in=profile_ids).values_list("id", flat=True))
    GeneratedAnalysisProfileLink.objects.filter(analysis=analysis).delete()
    GeneratedAnalysisProfileLink.objects.bulk_create(
        [
            GeneratedAnalysisProfileLink(analysis=analysis, profile_id=profile_id, role=role)
            for profile_id, role in links
            if profile_id in existing_profile_ids
        ],
        ignore_conflicts=True,
    )


@receiver(post_save, sender=GeneratedAnalysisDraft)
def sync_generated_analysis_profile_links(sender, instance: GeneratedAnalysisDraft, **kwargs) -> None:
    refresh_generated_analysis_profile_links(instance)
