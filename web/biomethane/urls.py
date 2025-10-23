from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    BiomethaneAnnualDeclarationViewSet,
    BiomethaneContractAmendmentViewSet,
    BiomethaneContractViewSet,
    BiomethaneDigestateSpreadingViewSet,
    BiomethaneDigestateStorageViewSet,
    BiomethaneDigestateViewSet,
    BiomethaneEnergyMonthlyReportViewSet,
    BiomethaneEnergyViewSet,
    BiomethaneInjectionSiteViewSet,
    BiomethaneProductionUnitViewSet,
    BiomethaneSupplyInputViewSet,
    BiomethaneSupplyPlanViewSet,
    download_template,
)

router = SimpleRouter()
router.register(
    "contract/amendments",
    BiomethaneContractAmendmentViewSet,
    basename="biomethane-contract-amendment",
)
router.register(
    "digestate-storage",
    BiomethaneDigestateStorageViewSet,
    basename="biomethane-digestate-storage",
)
router.register(
    "digestate/spreading",
    BiomethaneDigestateSpreadingViewSet,
    basename="biomethane-digestate-spreading",
)
router.register(
    "supply-input",
    BiomethaneSupplyInputViewSet,
    basename="biomethane-supply-input",
)
router.register(
    "contract",
    BiomethaneContractViewSet,
    basename="biomethane-contract",
)
router.register(
    "production-unit",
    BiomethaneProductionUnitViewSet,
    basename="biomethane-production-unit",
)

contract_viewset = BiomethaneContractViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

injection_site_viewset = BiomethaneInjectionSiteViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

production_unit_viewset = BiomethaneProductionUnitViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

digestate_viewset = BiomethaneDigestateViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

digestate_optional_fields_viewset = BiomethaneDigestateViewSet.as_view(
    {
        "get": "get_optional_fields",
    }
)


energy_viewset = BiomethaneEnergyViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

energy_monthly_report_viewset = BiomethaneEnergyMonthlyReportViewSet.as_view(
    {
        "put": "upsert",
        "get": "list",
    }
)

energy_optional_fields_viewset = BiomethaneEnergyViewSet.as_view(
    {
        "get": "get_optional_fields",
    }
)

supply_plan_years_viewset = BiomethaneSupplyPlanViewSet.as_view(
    {
        "get": "get_years",
    }
)

supply_plan_import_excel_viewset = BiomethaneSupplyPlanViewSet.as_view(
    {
        "post": "import_supply_plan_from_excel",
    }
)

supply_plan_export_to_excel_viewset = BiomethaneSupplyInputViewSet.as_view(
    {
        "get": "export_supply_plan_to_excel",
    }
)

annual_declaration_viewset = BiomethaneAnnualDeclarationViewSet.as_view(
    {
        "get": "retrieve",
        "patch": "partial_update",
    }
)

annual_declaration_validate_viewset = BiomethaneAnnualDeclarationViewSet.as_view(
    {
        "post": "validate_annual_declaration",
    }
)

annual_declaration_years_viewset = BiomethaneAnnualDeclarationViewSet.as_view(
    {
        "get": "get_years",
    }
)

urlpatterns = [
    path("contract/", contract_viewset, name="biomethane-contract"),
    path("injection-site/", injection_site_viewset, name="biomethane-injection-site"),
    path("production-unit/", production_unit_viewset, name="biomethane-production-unit"),
    path("digestate/", digestate_viewset, name="biomethane-digestate"),
    path("digestate/optional-fields/", digestate_optional_fields_viewset, name="biomethane-digestate-optional-fields"),
    path("energy/", energy_viewset, name="biomethane-energy"),
    path("energy/monthly-reports/", energy_monthly_report_viewset, name="biomethane-energy-monthly-report"),
    path("energy/optional-fields/", energy_optional_fields_viewset, name="biomethane-energy-optional-fields"),
    path("supply-plan/years/", supply_plan_years_viewset, name="biomethane-supply-plan-years"),
    path("supply-plan/import/", supply_plan_import_excel_viewset, name="biomethane-supply-plan-import-excel"),
    path("supply-plan/export/", supply_plan_export_to_excel_viewset, name="biomethane-supply-plan-export-excel"),
    path("supply-plan/download-template/", download_template, name="biomethane-supply-plan-dl-template"),
    path("annual-declaration/", annual_declaration_viewset, name="biomethane-annual-declaration"),
    path("annual-declaration/validate/", annual_declaration_validate_viewset, name="biomethane-annual-declaration-validate"),
    path("annual-declaration/years/", annual_declaration_years_viewset, name="biomethane-annual-declaration-years"),
    *router.urls,
]
