from django.contrib import admin

from tiruert.models import FossilFuel, FossilFuelCategory, Objective, Operation

from .admin_actions import perform_bulk_operations_validation


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


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = [
        "type",
        "status",
        "customs_category",
        "biofuel",
        "credited_entity",
        "debited_entity",
        "created_at",
        "validation_date",
    ]
    search_fields = ["credited_entity__name", "debited_entity__name", "credited_entity__id", "debited_entity__id"]
    list_filter = ["type", "status"]
    actions = [perform_bulk_operations_validation]
