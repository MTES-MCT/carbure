from django.contrib import admin

from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput


class ProductionSiteAdmin(admin.ModelAdmin):
    list_display = ("name", "producer", "country", "date_mise_en_service", "ges_option", "gps_coordinates")
    search_fields = ("name", "producer__name", "country__name", "ges_option")
    list_filter = ("producer", "country", "ges_option", "eligible_dc")


admin.site.register(ProductionSite, ProductionSiteAdmin)


class ProductionSiteInputAdmin(admin.ModelAdmin):
    list_display = ("production_site", "matiere_premiere")
    search_fields = ("production_site__name", "matiere_premiere__name", "matiere_premiere__code")
    list_filter = ("matiere_premiere",)


admin.site.register(ProductionSiteInput, ProductionSiteInputAdmin)


class ProductionSiteOutputAdmin(admin.ModelAdmin):
    list_display = (
        "production_site",
        "biocarburant",
    )
    search_fields = ("production_site__name", "biocarburant__code", "biocarburant__name")
    list_filter = ("biocarburant",)


admin.site.register(ProductionSiteOutput, ProductionSiteOutputAdmin)
