from django.contrib import admin

from biomethane.models import (
    BiomethaneAnnualDeclaration,
    BiomethaneContract,
    BiomethaneContractAmendment,
    BiomethaneDeclarationPeriod,
    BiomethaneDigestate,
    BiomethaneDigestateSpreading,
    BiomethaneDigestateStorage,
    BiomethaneEnergy,
    BiomethaneEnergyMonthlyReport,
    BiomethaneInjectionSite,
    BiomethaneProductionUnit,
    BiomethaneSupplyInput,
    BiomethaneSupplyPlan,
)


@admin.register(BiomethaneContract)
class BiomethaneContractAdmin(admin.ModelAdmin):
    list_display = ("id", "producer", "buyer", "tariff_reference", "signature_date", "effective_date")
    list_filter = ("tariff_reference",)
    search_fields = ("buyer__name", "producer__name", "producer__pk")


@admin.register(BiomethaneContractAmendment)
class BiomethaneContractAmendmentAdmin(admin.ModelAdmin):
    list_display = ("id", "contract__producer__name", "signature_date", "effective_date")
    search_fields = ("contract__buyer__name", "contract__producer__name", "producer__pk")


@admin.register(BiomethaneInjectionSite)
class BiomethaneInjectionSiteAdmin(admin.ModelAdmin):
    list_display = ("id", "producer", "unique_identification_number", "network_type", "is_shared_injection_site")
    list_filter = ("network_type", "is_shared_injection_site")
    search_fields = ("unique_identification_number", "producer__name", "meter_number", "producer__pk")


@admin.register(BiomethaneProductionUnit)
class BiomethaneProductionUnitAdmin(admin.ModelAdmin):
    list_display = ("id", "producer", "department", "unit_name", "siret_number", "unit_type")
    list_filter = ("unit_type", "department")
    search_fields = ("unit_name", "siret_number", "producer__name", "producer__pk")


@admin.register(BiomethaneDigestateStorage)
class BiomethaneDigestateStorageAdmin(admin.ModelAdmin):
    list_display = ("id", "producer__name", "type", "capacity", "has_cover", "has_biogas_recovery")
    list_filter = ("has_cover", "has_biogas_recovery")
    search_fields = ("producer__name", "producer__pk")


@admin.register(BiomethaneDigestate)
class BiomethaneDigestateAdmin(admin.ModelAdmin):
    list_display = ("id", "producer", "year", "raw_digestate_tonnage_produced")
    list_filter = ("year",)
    search_fields = ("producer__name", "producer__pk")


@admin.register(BiomethaneDigestateSpreading)
class BiomethaneDigestateSpreadingAdmin(admin.ModelAdmin):
    list_display = ("id", "digestate__producer__name", "spreading_department", "spread_quantity")
    list_filter = ("spreading_department",)
    search_fields = ("digestate__producer__name", "digestate__producer__pk")


@admin.register(BiomethaneEnergy)
class BiomethaneEnergyAdmin(admin.ModelAdmin):
    list_display = ("id", "producer", "year", "injected_biomethane_gwh_pcs_per_year")
    list_filter = ("year",)
    search_fields = ("producer__name", "producer__pk")


@admin.register(BiomethaneEnergyMonthlyReport)
class BiomethaneEnergyMonthlyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "energy__producer__name", "energy__year", "month", "injected_volume_nm3")
    list_filter = ("energy__year",)
    search_fields = ("energy__producer__name", "energy__producer__pk")


@admin.register(BiomethaneSupplyPlan)
class BiomethaneSupplyPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "producer", "year")
    list_filter = ("year",)
    search_fields = ("producer__name", "producer__pk")


@admin.register(BiomethaneSupplyInput)
class BiomethaneSupplyInputAdmin(admin.ModelAdmin):
    list_display = ("id", "supply_plan__producer__name", "supply_plan__year", "input_type", "input_category", "volume")
    list_filter = ("supply_plan__year", "source", "crop_type")
    search_fields = ("supply_plan__producer__name", "input_type", "supply_plan__producer__pk")


@admin.register(BiomethaneAnnualDeclaration)
class BiomethaneAnnualDeclarationAdmin(admin.ModelAdmin):
    list_display = ("id", "producer", "year", "status")
    list_filter = ("status", "year")
    search_fields = ("producer__name", "producer__pk")


@admin.register(BiomethaneDeclarationPeriod)
class BiomethaneDeclarationPeriodAdmin(admin.ModelAdmin):
    list_display = ("year", "start_date", "end_date")
    search_fields = ("year",)
