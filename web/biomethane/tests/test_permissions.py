from django.test import TestCase

from biomethane.permissions import (
    HasBiomethaneProducerWriteRights,
    HasDrealOrProducerRights,
    HasDrealRights,
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
from core.models import Entity, ExternalAdminRights, UserRights
from core.tests_utils import PermissionTestMixin


class BiomethanePermissionsMixinTests(TestCase):
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
        self.assertEqual(permissions[0].op1.role, None)
        self.assertEqual(permissions[0].op1.entity_type, [Entity.BIOMETHANE_PRODUCER])
        self.assertEqual(permissions[0].op2.allow_external, [ExternalAdminRights.DREAL])
        self.assertEqual(permissions[0].op2.allow_role, None)


class BiomethanePermissions(TestCase, PermissionTestMixin):
    def test_contract_permissions(self):
        """Test BiomethaneContractViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneContractViewSet,
            [
                (["retrieve", "watched_fields"], [HasDrealOrProducerRights()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_energy_permissions(self):
        """Test BiomethaneEnergyViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneEnergyViewSet,
            [
                (["retrieve", "get_optional_fields"], [HasDrealOrProducerRights()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_production_unit_permissions(self):
        """Test BiomethaneProductionUnitViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneProductionUnitViewSet,
            [
                (["retrieve", "watched_fields"], [HasDrealOrProducerRights()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_contract_amendment_permissions(self):
        """Test BiomethaneContractAmendmentViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneContractAmendmentViewSet,
            [
                (["list", "retrieve"], [HasDrealOrProducerRights()]),
                (["create"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_digestate_permissions(self):
        """Test BiomethaneDigestateViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneDigestateViewSet,
            [
                (["retrieve", "get_optional_fields"], [HasDrealOrProducerRights()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_injection_site_permissions(self):
        """Test BiomethaneInjectionSiteViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneInjectionSiteViewSet,
            [
                (["retrieve"], [HasDrealOrProducerRights()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_annual_declaration_permissions(self):
        """Test BiomethaneAnnualDeclarationViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneAnnualDeclarationViewSet,
            [
                (["retrieve", "get_years"], [HasDrealOrProducerRights()]),
                (["partial_update", "validate_annual_declaration"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_supply_plan_permissions(self):
        """Test BiomethaneSupplyPlanViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneSupplyPlanViewSet,
            [
                (["get_years"], [HasDrealOrProducerRights()]),
                (["import_supply_plan_from_excel"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_supply_input_permissions(self):
        """Test BiomethaneSupplyInputViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneSupplyInputViewSet,
            [
                (["retrieve", "list", "export_supply_plan_to_excel", "filters"], [HasDrealOrProducerRights()]),
                (["create", "update", "partial_update"], [HasBiomethaneProducerWriteRights()]),
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
                (["list"], [HasDrealOrProducerRights()]),
                (["upsert"], [HasBiomethaneProducerWriteRights()]),
            ],
        )

    def test_digestate_storage_permissions(self):
        """Test BiomethaneDigestateStorageViewSet permissions"""
        self.assertViewPermissions(
            BiomethaneDigestateStorageViewSet,
            [
                (["list", "retrieve"], [HasDrealOrProducerRights()]),
                (["create", "destroy", "partial_update", "update"], [HasBiomethaneProducerWriteRights()]),
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
