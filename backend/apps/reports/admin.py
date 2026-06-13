from django.contrib import admin

from .models import GeneratedAnalysisDraft, GeneratedAnalysisJob


@admin.register(GeneratedAnalysisDraft)
class GeneratedAnalysisDraftAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "review_status", "provider", "model", "created_at")
    list_filter = ("kind", "review_status", "provider")
    search_fields = ("kind", "model", "output_json")
    readonly_fields = ("created_at",)


@admin.register(GeneratedAnalysisJob)
class GeneratedAnalysisJobAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "status", "user", "analysis", "created_at", "completed_at")
    list_filter = ("kind", "status")
    search_fields = ("kind", "error", "user__username")
    readonly_fields = ("created_at", "updated_at", "started_at", "completed_at")
