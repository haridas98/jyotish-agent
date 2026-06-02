from django.contrib import admin

from .models import InterpretationBlock, InterpretationRule, RemedyPolicy, ShastraConditionEvidence


@admin.register(InterpretationRule)
class InterpretationRuleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "priority", "review_status")
    list_filter = ("review_status",)
    search_fields = ("title", "slug")
    filter_horizontal = ("passages",)


@admin.register(InterpretationBlock)
class InterpretationBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "language_code", "review_status")
    list_filter = ("section", "language_code", "review_status")
    search_fields = ("title", "body")


@admin.register(RemedyPolicy)
class RemedyPolicyAdmin(admin.ModelAdmin):
    list_display = ("slug", "classical_trigger", "review_status")
    list_filter = ("review_status",)
    search_fields = ("slug", "classical_trigger", "vaishnava_reframe")
    filter_horizontal = ("passages",)


@admin.register(ShastraConditionEvidence)
class ShastraConditionEvidenceAdmin(admin.ModelAdmin):
    list_display = (
        "condition_key",
        "condition_kind",
        "condition_title",
        "score",
        "reference_status",
        "review_status",
    )
    list_filter = ("condition_kind", "reference_status", "review_status")
    search_fields = ("condition_key", "condition_title", "passage__reference", "passage__body")
