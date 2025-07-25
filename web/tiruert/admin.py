from django.contrib import admin

from tiruert.models import (
    FossilFuel,
    FossilFuelCategory,
    FossilFuelCategoryConsiderationRate,
    MacFossilFuel,
    Objective,
    Operation,
)
from tiruert.models.elec_operation import ElecOperation

from .admin_actions import perform_bulk_operations_validation


@admin.register(FossilFuel)
class FossilFuelAdmin(admin.ModelAdmin):
    list_filter = ["fuel_category"]
    list_display = ["label", "fuel_category", "pci_litre", "masse_volumique"]


@admin.register(FossilFuelCategory)
class FossilFuelCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(FossilFuelCategoryConsiderationRate)
class FossilFuelCategoryConsiderationRateAdmin(admin.ModelAdmin):
    list_display = ["category_fuel", "year", "consideration_rate_"]
    search_fields = ["category_fuel__name"]
    list_filter = ["year", "category_fuel"]
    ordering = ["-year"]

    def consideration_rate_(self, obj):
        if obj.consideration_rate is not None:
            return f"{obj.consideration_rate * 100:.2f} %"


@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = [
        "type",
        "fuel_category",
        "customs_category",
        "year",
        "target_",
        "target_type",
        "penalty_",
    ]

    def target_(self, obj):
        if obj.target is not None:
            return f"{obj.target * 100:.2f} %"

    def penalty_(self, obj):
        if obj.penalty is not None:
            return f"{obj.penalty / 100} €"


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


@admin.register(ElecOperation)
class ElecOperationAdmin(admin.ModelAdmin):
    list_display = [
        "type",
        "status",
        "credited_entity",
        "debited_entity",
        "created_at",
    ]
    search_fields = ["credited_entity__name", "debited_entity__name", "credited_entity__id", "debited_entity__id"]
    list_filter = ["type", "status"]


@admin.register(MacFossilFuel)
class MacFossilFuelAdmin(admin.ModelAdmin):
    list_display = ["fuel", "operator", "volume", "period", "year", "depot"]
    list_filter = ["year", "operator__name"]
    search_fields = ["operator__name"]
