from django.contrib import admin

from .models import GeneratedAnalysisDraft


@admin.register(GeneratedAnalysisDraft)
class GeneratedAnalysisDraftAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "review_status", "provider", "model", "created_at")
    list_filter = ("kind", "review_status", "provider")
    search_fields = ("kind", "model", "output_json")
    readonly_fields = ("created_at",)
