from django.contrib import admin, messages

from entity.services import enable_depot
from transactions.models import Airport, Depot, EntitySite, ProductionSite, Site

from .models import YearConfig


@admin.register(YearConfig)
class YearConfigAdmin(admin.ModelAdmin):
    list_display = ("year", "locked")


class EntitySiteInline(admin.TabularInline):
    model = EntitySite
    extra = 0
    fields = ("entity",)

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_owner",
        "site_type",
        "city",
        "country",
        "gps_coordinates",
        "private",
        "is_enabled",
    )
    search_fields = ("name", "city", "country__name")
    list_filter = ("site_type", "country")
    actions = ["enable_site"]
    inlines = [EntitySiteInline]

    def enable_site(self, request, queryset):
        for site in queryset:
            response = enable_depot.enable_depot(site, request)
            messages.add_message(request, messages.SUCCESS, response)

    enable_site.short_description = "Valider les sites sélectionnés"

    def get_owner(self, obj):
        entity_sites = EntitySite.objects.filter(site=obj)
        return [entity_site.entity.name for entity_site in entity_sites]

    get_owner.short_description = "Owners"


@admin.register(Depot)
class DepotAdmin(SiteAdmin):
    list_display = (
        "name",
        "customs_id",
        "get_owner",
        "site_type",
        "city",
        "country",
        "gps_coordinates",
        "private",
        "is_enabled",
    )
    search_fields = ("name", "city", "country__name", "customs_id")
    list_filter = ("site_type", "country")


@admin.register(ProductionSite)
class ProductionSiteAdmin(SiteAdmin):
    list_display = (
        "name",
        "get_owner",
        "city",
        "country",
        "date_mise_en_service",
        "ges_option",
        "eligible_dc",
        "gps_coordinates",
        "private",
        "is_enabled",
    )
    search_fields = ("name", "city", "country__name", "ges_option")
    list_filter = ("country", "ges_option", "eligible_dc")


@admin.register(Airport)
class AirportAdmin(SiteAdmin):
    list_display = (
        "name",
        "icao_code",
        "get_owner",
        "city",
        "country",
        "is_ue_airport",
        "gps_coordinates",
        "private",
        "is_enabled",
    )
    search_fields = ("name", "city", "country__name", "icao_code")
    list_filter = ("country", "is_ue_airport")
