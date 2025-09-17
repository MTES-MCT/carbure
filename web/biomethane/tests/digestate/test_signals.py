from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.factories.digestate import BiomethaneDigestateFactory
from biomethane.factories.production_unit import BiomethaneProductionUnitFactory
from biomethane.models.biomethane_contract import BiomethaneContract
from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.models.biomethane_production_unit import BiomethaneProductionUnit
from core.models import Entity


class BiomethaneDigestateSignalTests(TestCase):
    def setUp(self):
        """Initial setup for signal tests."""
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        # Create production unit with spreading valorization
        self.production_unit = BiomethaneProductionUnitFactory.create(
            producer=self.producer_entity,
            digestate_valorization_methods=[BiomethaneProductionUnit.SPREADING, BiomethaneProductionUnit.COMPOSTING],
            has_digestate_phase_separation=True,
        )

        self.buyer_entity = Entity.objects.create(
            name="Test Buyer",
            entity_type=Entity.OPERATOR,
        )

    def test_clear_phase_separation_fields_when_disabled(self):
        """Test phase separation fields are cleared when phase separation is disabled."""
        # Create digestate with phase separation data
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            solid_digestate_tonnage=500.0,
            liquid_digestate_quantity=1000.0,
        )

        # Disable phase separation
        self.production_unit.has_digestate_phase_separation = False
        self.production_unit.save()

        # Reload digestate and verify phase separation fields are cleared
        digestate.refresh_from_db()
        self.assertIsNone(digestate.solid_digestate_tonnage)
        self.assertIsNone(digestate.liquid_digestate_quantity)

    def test_clear_raw_digestate_fields_when_enabled(self):
        """Test raw digestate fields are cleared when phase separation is enabled."""
        # Create digestate with raw digestate data
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            raw_digestate_tonnage_produced=800.0,
            raw_digestate_dry_matter_rate=20.0,
        )

        # Update production unit to enable phase separation
        self.production_unit.has_digestate_phase_separation = True
        self.production_unit.save()

        # Reload digestate and verify raw digestate fields are cleared
        digestate.refresh_from_db()
        self.assertIsNone(digestate.raw_digestate_tonnage_produced)
        self.assertIsNone(digestate.raw_digestate_dry_matter_rate)

    def test_clear_spreading_fields_when_not_in_valorization_methods(self):
        """Test spreading fields are cleared when spreading is not in valorization methods."""
        # Create digestate with spreading data
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            average_spreading_valorization_distance=50.0,
        )

        # Update production unit to remove spreading from valorization methods
        self.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.COMPOSTING]
        self.production_unit.save()

        # Reload digestate and verify spreading field is cleared
        digestate.refresh_from_db()
        self.assertIsNone(digestate.average_spreading_valorization_distance)

    def test_clear_composting_fields_when_not_in_valorization_methods(self):
        """Test composting fields are cleared when composting is not in valorization methods."""
        # Create digestate with composting data
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            composting_locations=[BiomethaneDigestate.ON_SITE, BiomethaneDigestate.EXTERNAL_PLATFORM],
            on_site_composted_digestate_volume=300.0,
            external_platform_name="Test Platform",
            external_platform_digestate_volume=200.0,
            external_platform_department="75",
            external_platform_municipality="Paris",
        )

        # Update production unit to remove composting from valorization methods
        self.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.production_unit.save()

        # Reload digestate and verify composting fields are cleared
        digestate.refresh_from_db()
        self.assertEqual(digestate.composting_locations, [])
        self.assertIsNone(digestate.on_site_composted_digestate_volume)
        self.assertIsNone(digestate.external_platform_name)
        self.assertIsNone(digestate.external_platform_digestate_volume)
        self.assertIsNone(digestate.external_platform_department)
        self.assertIsNone(digestate.external_platform_municipality)

    def test_clear_on_site_composting_field_when_location_removed(self):
        """Test on-site composting field is cleared when location is removed."""
        # Create digestate with both composting locations
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            composting_locations=[BiomethaneDigestate.ON_SITE, BiomethaneDigestate.EXTERNAL_PLATFORM],
            on_site_composted_digestate_volume=300.0,
            external_platform_name="Test Platform",
            external_platform_digestate_volume=200.0,
            external_platform_department="75",
            external_platform_municipality="Paris",
        )

        # Update digestate to only have external platform
        digestate.composting_locations = [BiomethaneDigestate.EXTERNAL_PLATFORM]
        digestate.save()

        # Reload and verify only on-site field is cleared
        digestate.refresh_from_db()
        self.assertIsNone(digestate.on_site_composted_digestate_volume)
        # External platform fields should remain
        self.assertEqual(digestate.external_platform_name, "Test Platform")
        self.assertEqual(digestate.external_platform_digestate_volume, 200.0)

    def test_clear_external_platform_fields_when_location_removed(self):
        """Test external platform fields are cleared when location is removed."""
        # Create digestate with both composting locations
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            composting_locations=[BiomethaneDigestate.ON_SITE, BiomethaneDigestate.EXTERNAL_PLATFORM],
            on_site_composted_digestate_volume=300.0,
            external_platform_name="Test Platform",
            external_platform_digestate_volume=200.0,
            external_platform_department="75",
            external_platform_municipality="Paris",
        )

        # Update digestate to only have on-site
        digestate.composting_locations = [BiomethaneDigestate.ON_SITE]
        digestate.save()

        # Reload and verify only external platform fields are cleared
        digestate.refresh_from_db()
        self.assertEqual(digestate.on_site_composted_digestate_volume, 300.0)
        # External platform fields should be cleared
        self.assertIsNone(digestate.external_platform_name)
        self.assertIsNone(digestate.external_platform_digestate_volume)
        self.assertIsNone(digestate.external_platform_department)
        self.assertIsNone(digestate.external_platform_municipality)

    def test_clear_incineration_fields_when_not_in_valorization_methods(self):
        """Test incineration fields are cleared when incineration is not in valorization methods."""
        # Create digestate with incineration data
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            annual_eliminated_volume=100.0,
            incinerator_landfill_center_name="Test Center",
            wwtp_materials_to_incineration=50.0,
        )

        # Update production unit to not include incineration (it's not in default valorization methods)
        self.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.production_unit.save()

        # Reload digestate and verify incineration fields are cleared
        digestate.refresh_from_db()
        self.assertIsNone(digestate.annual_eliminated_volume)
        self.assertIsNone(digestate.incinerator_landfill_center_name)
        self.assertIsNone(digestate.wwtp_materials_to_incineration)

    def test_clear_wwtp_materials_when_contract_not_category_2(self):
        """Test WWTP materials field is cleared when contract is not installation category 2."""
        # Create digestate with WWTP materials data
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            wwtp_materials_to_incineration=75.0,
        )

        # Create contract with category different from 2
        contract = BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
        )

        # Save contract to trigger signal
        contract.save()

        # Reload digestate and verify WWTP materials field is cleared
        digestate.refresh_from_db()
        self.assertIsNone(digestate.wwtp_materials_to_incineration)

    def test_clear_sale_fields_when_not_in_spreading_management_methods(self):
        """Test sale fields are cleared when sale is not in spreading management methods."""
        # Create digestate with sale data
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            sold_volume=200.0,
            acquiring_companies="Company A, Company B",
        )

        # Update production unit to not include sale in spreading management methods
        self.production_unit.spreading_management_methods = [BiomethaneProductionUnit.DIRECT_SPREADING]
        self.production_unit.save()

        # Reload digestate and verify sale fields are cleared
        digestate.refresh_from_db()
        self.assertIsNone(digestate.sold_volume)
        self.assertIsNone(digestate.acquiring_companies)
