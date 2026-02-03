from datetime import date
from unittest.mock import patch

from django.test import TestCase

from biomethane.factories import BiomethaneDigestateFactory, BiomethaneProductionUnitFactory
from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.factories.energy import BiomethaneEnergyFactory
from biomethane.factories.supply_plan import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.models import BiomethaneAnnualDeclaration, BiomethaneDigestate
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity


class BiomethaneAnnualDeclarationServiceTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()

    @patch("biomethane.services.annual_declaration.date")
    def test_get_declaration_period(self, mock_date):
        """Test get_current_declaration_year returns previous year based on current date"""
        # Test that get_current_declaration_year always returns previous year
        mock_date.today.return_value = date(2026, 1, 1)
        result = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        self.assertEqual(result, 2025)

        mock_date.today.return_value = date(2026, 12, 31)
        result = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        self.assertEqual(result, 2025)

    def test_is_declaration_period_open_with_period_exists(self):
        """Test is_declaration_period_open when BiomethaneDeclarationPeriod exists"""
        from biomethane.models import BiomethaneDeclarationPeriod

        # Create a declaration period for 2025
        BiomethaneDeclarationPeriod.objects.create(
            year=2025,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )

        # Test when we're in the period - need to mock date in both service and model
        with (
            patch("biomethane.services.annual_declaration.date") as mock_date_service,
            patch("biomethane.models.biomethane_declaration_period.date") as mock_date_model,
        ):
            mock_date_service.today.return_value = date(2026, 2, 15)
            mock_date_model.today.return_value = date(2026, 2, 15)
            result = BiomethaneAnnualDeclarationService.is_declaration_period_open()
            self.assertTrue(result)

        # Test when we're after the period
        with (
            patch("biomethane.services.annual_declaration.date") as mock_date_service,
            patch("biomethane.models.biomethane_declaration_period.date") as mock_date_model,
        ):
            mock_date_service.today.return_value = date(2026, 5, 15)
            mock_date_model.today.return_value = date(2026, 5, 15)
            result = BiomethaneAnnualDeclarationService.is_declaration_period_open()
            self.assertFalse(result)

    def test_is_declaration_period_open_without_period(self):
        """Test is_declaration_period_open when BiomethaneDeclarationPeriod doesn't exist"""
        result = BiomethaneAnnualDeclarationService.is_declaration_period_open()
        self.assertFalse(result)

    def test_get_missing_fields_both_models_exist(self):
        """Test get_missing_fields structure when digestate, energy and supply_plan exist"""
        BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            year=self.current_year,
        )

        BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=self.current_year,
        )

        supply_plan = BiomethaneSupplyPlanFactory.create(
            producer=self.producer_entity,
            year=self.current_year,
        )
        BiomethaneSupplyInputFactory.create(supply_plan=supply_plan)

        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        missing_fields = BiomethaneAnnualDeclarationService.get_missing_fields(declaration)

        self.assertIsInstance(missing_fields, dict)
        self.assertIn("digestate_missing_fields", missing_fields)
        self.assertIn("energy_missing_fields", missing_fields)
        self.assertIn("supply_plan_valid", missing_fields)
        self.assertIsInstance(missing_fields["digestate_missing_fields"], list)
        self.assertIsInstance(missing_fields["energy_missing_fields"], list)
        self.assertTrue(missing_fields["supply_plan_valid"])

    def test_get_missing_fields_both_not_exist(self):
        """Test get_missing_fields when neither digestate, energy nor supply_plan exist"""
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        missing_fields = BiomethaneAnnualDeclarationService.get_missing_fields(declaration)

        self.assertIsNone(missing_fields["digestate_missing_fields"])
        self.assertIsNone(missing_fields["energy_missing_fields"])
        self.assertFalse(missing_fields["supply_plan_valid"])

    def test_get_required_fields_with_valid_model(self):
        """Test get_required_fields returns all field names for a model"""
        # Test with BiomethaneDigestate model
        fields = BiomethaneAnnualDeclarationService.get_all_fields(BiomethaneDigestate)

        # Assert we get a list of field names
        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) > 0)

        # Check some known fields are present
        self.assertIn("producer", fields)
        self.assertIn("year", fields)
        self.assertIn("raw_digestate_tonnage_produced", fields)

    def test_get_missing_fields_supply_plan_without_inputs(self):
        """Test get_missing_fields when supply_plan exists but has no inputs"""
        BiomethaneSupplyPlanFactory.create(
            producer=self.producer_entity,
            year=self.current_year,
        )

        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        missing_fields = BiomethaneAnnualDeclarationService.get_missing_fields(declaration)

        self.assertFalse(missing_fields["supply_plan_valid"])

    def test_is_declaration_complete_with_incomplete_data(self):
        """Test is_declaration_complete returns False when required fields are missing"""
        missing_fields = {
            "digestate_missing_fields": ["xxx"],
            "energy_missing_fields": ["yyy"],
            "supply_plan_valid": False,
        }

        # Create declaration
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        is_complete = BiomethaneAnnualDeclarationService.is_declaration_complete(declaration, missing_fields)

        self.assertFalse(is_complete)

    def test_is_declaration_complete_with_no_data(self):
        """Test is_declaration_complete returns False when no digestate/energy/supply plan exist"""
        # Create declaration without digestate and energy
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        is_complete = BiomethaneAnnualDeclarationService.is_declaration_complete(declaration)

        self.assertFalse(is_complete)

    def test_is_declaration_complete_with_complete_data(self):
        """Test is_declaration_complete returns True when all required fields are filled"""
        missing_fields = {
            "digestate_missing_fields": [],
            "energy_missing_fields": [],
            "supply_plan_valid": True,
        }

        # Create declaration
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        is_complete = BiomethaneAnnualDeclarationService.is_declaration_complete(declaration, missing_fields)

        self.assertTrue(is_complete)

    def test_is_declaration_editable_in_progress_status(self):
        """Test is_declaration_editable returns True for IN_PROGRESS declarations"""
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        is_editable = BiomethaneAnnualDeclarationService.is_declaration_editable(self.producer_entity, self.current_year)

        self.assertTrue(is_editable)

    def test_is_declaration_editable_declared_status(self):
        """Test is_declaration_editable returns False for DECLARED status"""
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        is_editable = BiomethaneAnnualDeclarationService.is_declaration_editable(self.producer_entity, self.current_year)

        self.assertFalse(is_editable)

    def test_is_declaration_editable_not_exists(self):
        """Test is_declaration_editable returns True when declaration doesn't exist"""
        is_editable = BiomethaneAnnualDeclarationService.is_declaration_editable(self.producer_entity, self.current_year)

        # Assert it's editable (can create new)
        self.assertTrue(is_editable)

    def test_get_watched_fields_structure(self):
        """Test get_watched_fields returns correct structure"""
        watched_fields = BiomethaneAnnualDeclarationService.get_watched_fields()

        self.assertIsInstance(watched_fields, dict)
        self.assertIn("production_unit", watched_fields)
        self.assertIn("contract", watched_fields)
        self.assertIsInstance(watched_fields["production_unit"], list)
        self.assertIsInstance(watched_fields["contract"], list)

        # Verify some known watched fields
        self.assertIn("installed_meters", watched_fields["production_unit"])
        self.assertIn("tariff_reference", watched_fields["contract"])

    def test_has_watched_field_changed_production_unit(self):
        """Test has_watched_field_changed detects production unit field changes"""
        production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)

        # Test with watched field
        changed_fields = ["installed_meters", "name"]
        result = BiomethaneAnnualDeclarationService.has_watched_field_changed(production_unit, changed_fields)
        self.assertTrue(result)

        # Test with non-watched field only
        changed_fields = ["name", "description"]
        result = BiomethaneAnnualDeclarationService.has_watched_field_changed(production_unit, changed_fields)
        self.assertFalse(result)

    def test_has_watched_field_changed_contract(self):
        """Test has_watched_field_changed detects contract field changes"""
        contract = BiomethaneContractFactory.create(producer=self.producer_entity)

        # Test with watched field
        changed_fields = ["tariff_reference", "status"]
        result = BiomethaneAnnualDeclarationService.has_watched_field_changed(contract, changed_fields)
        self.assertTrue(result)

        # Test with non-watched field only
        changed_fields = ["status", "notes"]
        result = BiomethaneAnnualDeclarationService.has_watched_field_changed(contract, changed_fields)
        self.assertFalse(result)

    def test_reset_annual_declaration_status(self):
        """Test reset_annual_declaration_status updates status to IN_PROGRESS"""
        # Create declaration with DECLARED status
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        # Reset status
        BiomethaneAnnualDeclarationService.reset_annual_declaration_status(self.producer_entity)

        # Verify status was reset
        declaration.refresh_from_db()
        self.assertEqual(declaration.status, BiomethaneAnnualDeclaration.IN_PROGRESS)

    def test_reset_annual_declaration_status_no_declaration(self):
        """Test reset_annual_declaration_status handles missing declaration gracefully"""
        # Verify no declaration exists initially
        self.assertEqual(BiomethaneAnnualDeclaration.objects.filter(producer=self.producer_entity).count(), 0)

        # Should not raise exception when declaration doesn't exist
        BiomethaneAnnualDeclarationService.reset_annual_declaration_status(self.producer_entity)

        # Verify no declaration was created
        self.assertEqual(BiomethaneAnnualDeclaration.objects.filter(producer=self.producer_entity).count(), 0)

    @patch("biomethane.services.annual_declaration.date")
    def test_get_declaration_status_in_progress_current_year(self, mock_date):
        """Test get_declaration_status returns IN_PROGRESS for current year declaration"""
        mock_date.today.return_value = date(2026, 5, 15)

        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=2026,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        status = BiomethaneAnnualDeclarationService.get_declaration_status(declaration)
        self.assertEqual(status, BiomethaneAnnualDeclaration.IN_PROGRESS)

    @patch("biomethane.services.annual_declaration.date")
    def test_get_declaration_status_declared(self, mock_date):
        """Test get_declaration_status returns DECLARED for declared declaration"""
        mock_date.today.return_value = date(2026, 5, 15)

        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=2025,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        status = BiomethaneAnnualDeclarationService.get_declaration_status(declaration)
        self.assertEqual(status, BiomethaneAnnualDeclaration.DECLARED)

    @patch("biomethane.services.annual_declaration.date")
    def test_get_declaration_status_overdue_previous_year(self, mock_date):
        """Test get_declaration_status returns OVERDUE for old year IN_PROGRESS declaration"""
        # Current date in April 2026, so current declaration year is 2025 (year - 1)
        mock_date.today.return_value = date(2026, 4, 15)

        # Declaration for 2024 (< 2025) still IN_PROGRESS should be OVERDUE
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=2024,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        status = BiomethaneAnnualDeclarationService.get_declaration_status(declaration)
        self.assertEqual(status, BiomethaneAnnualDeclaration.OVERDUE)

    @patch("biomethane.services.annual_declaration.date")
    def test_get_declaration_status_in_progress_current_declaration_year(self, mock_date):
        """Test get_declaration_status returns IN_PROGRESS for current declaration year"""
        # In January 2026, current declaration year is 2025 (year - 1)
        mock_date.today.return_value = date(2026, 1, 15)

        # Declaration for 2025 (current declaration year) should be IN_PROGRESS
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=2025,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        status = BiomethaneAnnualDeclarationService.get_declaration_status(declaration)
        self.assertEqual(status, BiomethaneAnnualDeclaration.IN_PROGRESS)
