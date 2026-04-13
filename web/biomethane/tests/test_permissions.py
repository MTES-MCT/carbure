from django.test import TestCase

from biomethane.permissions import (
    CanAccessContract,
    CanAccessInjection,
    HasBiomethaneProducerRights,
    HasBiomethaneProducerWriteRights,
    HasDrealRights,
    ReadAccessBiomethane,
    get_biomethane_permissions,
)
from biomethane.views import (
    BiomethaneAnnualDeclarationViewSet,
    BiomethaneContractAmendmentViewSet,
    BiomethaneContractViewSet,
    BiomethaneDigestateSpreadingViewSet,
    BiomethaneDigestateStorageViewSet,
    BiomethaneDigestateViewSet,
    BiomethaneEnergyMonthlyReportViewSet,
    BiomethaneEnergyViewSet,
    BiomethaneInjectionSiteViewSet,
    BiomethaneProducersViewSet,
    BiomethaneProductionUnitViewSet,
    BiomethaneSupplyInputViewSet,
    BiomethaneSupplyPlanViewSet,
)
from biomethane.views.admin.annual_declaration import BiomethaneAdminAnnualDeclarationViewSet
from core.models import Entity, UserRights
from core.tests_utils import PermissionTestMixin


class BiomethanePermissionsMixinTests(TestCase, PermissionTestMixin):
    def test_write_actions_initialization(self):
        """Test that write_actions throws an error if it is not a list"""
        with self.assertRaises(ValueError):
            get_biomethane_permissions("upsert", "upsert")

    def test_get_permissions_with_write_action(self):
        """Test that get_permissions returns the correct permission for a write action"""
        permissions = get_biomethane_permissions(["upsert", "validate"], "upsert")
        self.assertEqual(permissions[0].role, [UserRights.ADMIN, UserRights.RW])
        self.assertEqual(permissions[0].entity_type, [Entity.BIOMETHANE_PRODUCER])

    def test_get_permissions_with_read_action(self):
        """Test that get_permissions returns the correct permission for a read action"""
        permissions = get_biomethane_permissions(["upsert", "validate"], "retrieve")
        self.assertPermissionsEqual(permissions, [ReadAccessBiomethane()])

    def test_can_access_contract_permissions(self):
        """Test that contract access excludes ADEME rights"""
        self.assertPermissionsEqual([CanAccessContract()], [(HasBiomethaneProducerRights | HasDrealRights)()])


class BiomethanePermissions(TestCase, PermissionTestMixin):
    def test_contract_permissions(self):
        """Test BiomethaneContractViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneContractViewSet,
            [
                (["retrieve"], [CanAccessContract()]),
                (["watched_fields"], [ReadAccessBiomethane()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_energy_permissions(self):
        """Test BiomethaneEnergyViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneEnergyViewSet,
            [
                (["retrieve", "get_optional_fields"], [ReadAccessBiomethane()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_production_unit_permissions(self):
        """Test BiomethaneProductionUnitViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneProductionUnitViewSet,
            [
                (["retrieve", "watched_fields"], [ReadAccessBiomethane()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_contract_amendment_permissions(self):
        """Test BiomethaneContractAmendmentViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneContractAmendmentViewSet,
            [
                (["list", "retrieve"], [ReadAccessBiomethane()]),
                (["create"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_digestate_permissions(self):
        """Test BiomethaneDigestateViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneDigestateViewSet,
            [
                (["retrieve", "get_optional_fields"], [ReadAccessBiomethane()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_injection_site_permissions(self):
        """Test BiomethaneInjectionSiteViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneInjectionSiteViewSet,
            [
                (["retrieve"], [CanAccessInjection()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_annual_declaration_permissions(self):
        """Test BiomethaneAnnualDeclarationViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneAnnualDeclarationViewSet,
            [
                (["retrieve", "get_years"], [ReadAccessBiomethane()]),
                (["validate_annual_declaration"], [HasBiomethaneProducerWriteRights()]),
                (["create"], [HasDrealRights()]),
                (["partial_update"], [(HasBiomethaneProducerWriteRights | HasDrealRights)()]),
            ],
        )

    def test_supply_plan_permissions(self):
        """Test BiomethaneSupplyPlanViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneSupplyPlanViewSet,
            [
                (["get_years"], [ReadAccessBiomethane()]),
                (["import_supply_plan_from_excel"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_supply_input_permissions(self):
        """Test BiomethaneSupplyInputViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneSupplyInputViewSet,
            [
                (["retrieve", "list", "export_supply_plan_to_excel", "filters"], [ReadAccessBiomethane()]),
                (["create", "destroy", "update"], [HasBiomethaneProducerWriteRights()]),
                (["partial_update"], [(HasBiomethaneProducerWriteRights | HasDrealRights)()]),
            ],
        )

    def test_digestate_spreading_permissions(self):
        """Test BiomethaneDigestateSpreadingViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneDigestateSpreadingViewSet,
            [
                (["create", "destroy"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_energy_monthly_report_permissions(self):
        """Test BiomethaneEnergyMonthlyReportViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneEnergyMonthlyReportViewSet,
            [
                (["list"], [ReadAccessBiomethane()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_digestate_storage_permissions(self):
        """Test BiomethaneDigestateStorageViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneDigestateStorageViewSet,
            [
                (["list", "retrieve"], [ReadAccessBiomethane()]),
                (["create", "destroy", "update"], [HasBiomethaneProducerWriteRights()]),
                (["partial_update"], [(HasBiomethaneProducerWriteRights | HasDrealRights)()]),
            ],
        )

    def test_producers_permissions(self):
        """Test BiomethaneProducersViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneProducersViewSet,
            [
                (["list"], [HasDrealRights()]),
            ],
        )

    def test_annual_declaration_admin_permissions(self):
        """Test BiomethaneAdminAnnualDeclarationViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneAdminAnnualDeclarationViewSet,
            [
                (["list", "filters"], [HasDrealRights()]),
            ],
        )
