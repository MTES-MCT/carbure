from django.contrib import admin

from producers.models import ProductionSiteInput, ProductionSiteOutput


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
