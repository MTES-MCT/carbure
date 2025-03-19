from django.contrib import admin

from tiruert.models import FossilFuel, FossilFuelCategory, Objective


@admin.register(FossilFuel)
class FossilFuelAdmin(admin.ModelAdmin):
    list_filter = ["fuel_category"]
    list_display = ["label", "fuel_category", "pci_litre", "masse_volumique"]


@admin.register(FossilFuelCategory)
class FossilFuelCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    pass
