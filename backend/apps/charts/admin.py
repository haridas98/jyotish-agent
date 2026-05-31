from django.contrib import admin

from .models import BirthProfile, ChartCalculation, DashaPeriod, Place, PlanetPosition, VargaPlacement


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "country_code", "latitude", "longitude", "timezone_name")
    search_fields = ("name", "external_id", "timezone_name")


@admin.register(BirthProfile)
class BirthProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "birth_date", "birth_time", "birth_time_accuracy")
    list_filter = ("birth_time_accuracy", "timezone_name")
    search_fields = ("display_name", "user__email", "user__username")


@admin.register(ChartCalculation)
class ChartCalculationAdmin(admin.ModelAdmin):
    list_display = ("profile", "calculation_version", "ayanamsa", "house_system", "status")
    list_filter = ("status", "ayanamsa", "house_system", "calculation_version")


admin.site.register(PlanetPosition)
admin.site.register(VargaPlacement)
admin.site.register(DashaPeriod)

