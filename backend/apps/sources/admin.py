from django.contrib import admin

from .models import SourcePassage, SourceWork, VLCitationLink


@admin.register(SourceWork)
class SourceWorkAdmin(admin.ModelAdmin):
    list_display = ("title", "source_class", "author", "review_status")
    list_filter = ("source_class", "review_status", "language_code")
    search_fields = ("title", "author", "slug")


@admin.register(SourcePassage)
class SourcePassageAdmin(admin.ModelAdmin):
    list_display = ("work", "reference", "language_code", "review_status")
    list_filter = ("review_status", "language_code")
    search_fields = ("work__title", "reference", "body")


admin.site.register(VLCitationLink)

