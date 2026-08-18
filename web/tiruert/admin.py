from django.contrib import admin
from django.db.models import IntegerField
from django.db.models.functions import Cast, Coalesce, Substr

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
    list_filter = ["year", "type", "fuel_category", "customs_category"]

    def target_(self, obj):
        if obj.target is not None:
            return f"{obj.target * 100:.2f} %"

    def penalty_(self, obj):
        if obj.penalty is not None:
            return f"{obj.penalty / 100} €"


class OperationYearFilter(admin.SimpleListFilter):
    """
    A computed filter to list operations by year in django admin
    """

    title = "Année"
    parameter_name = "year"

    def annotate_year(self, queryset):
        return queryset.annotate(
            year=Coalesce(
                "declaration_year",
                Cast(
                    Substr("durability_period", 1, 4),
                    output_field=IntegerField(),
                ),
            )
        )

    def lookups(self, request, model_admin):
        years = (
            self.annotate_year(model_admin.get_queryset(request))
            .exclude(year__isnull=True)
            .values_list("year", flat=True)
            .distinct()
            .order_by("year")
        )
        return [(year, year) for year in years]

    def queryset(self, request, queryset):
        if self.value():
            return self.annotate_year(queryset).filter(year=self.value())
        return queryset


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
    list_filter = ["type", "status", OperationYearFilter]
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
