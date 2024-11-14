from django.contrib import admin, messages

from entity.services import enable_depot
from transactions.models import EntitySite, Site

from .models import YearConfig


@admin.register(YearConfig)
class YearConfigAdmin(admin.ModelAdmin):
    list_display = ("year", "locked")


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "customs_id",
        "get_owner",
        "site_type",
        "city",
        "country",
        "date_mise_en_service",
        "ges_option",
        "gps_coordinates",
        "private",
        "is_enabled",
    )
    search_fields = ("name", "city", "country__name", "ges_option", "customs_id")
    list_filter = ("country", "ges_option", "eligible_dc", "site_type")
    actions = ["enable_site"]

    def enable_site(self, request, queryset):
        for site in queryset:
            response = enable_depot.enable_depot(site, request)
            messages.add_message(request, messages.SUCCESS, response)

    enable_site.short_description = "Valider les sites sélectionnés"

    def get_owner(self, obj):
        entity_sites = EntitySite.objects.filter(site=obj)
        return [entity_site.entity.name for entity_site in entity_sites]

    get_owner.short_description = "Owners"


class DepotAdmin(admin.ModelAdmin):
    list_filter = ("depot_type",)
    readonly_fields = ("is_enabled",)
    actions = ["enable_depot"]

    def enable_depot(self, request, queryset):
        for depot in queryset:
            response = enable_depot.enable_depot(depot, request)
            messages.add_message(request, messages.SUCCESS, response)

    enable_depot.short_description = "Valider les dépôts sélectionnés"
