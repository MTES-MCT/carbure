from django.test import TestCase

from biomethane.factories import BiomethaneDigestateFactory
from biomethane.factories.energy import BiomethaneEnergyFactory
from biomethane.models import BiomethaneAnnualDeclaration, BiomethaneDigestate
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.utils import get_declaration_period
from core.models import Entity


class BiomethaneAnnualDeclarationServiceTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.current_year = get_declaration_period()

    def test_get_missing_fields_both_models_exist(self):
        """Test get_missing_fields structure when both digestate and energy exist"""
        BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            year=self.current_year,
        )

        BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=self.current_year,
        )

        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        missing_fields = BiomethaneAnnualDeclarationService.get_missing_fields(declaration)

        self.assertIsInstance(missing_fields, dict)
        self.assertIn("digestate_missing_fields", missing_fields)
        self.assertIn("energy_missing_fields", missing_fields)
        self.assertIsInstance(missing_fields["digestate_missing_fields"], list)
        self.assertIsInstance(missing_fields["energy_missing_fields"], list)

    def test_get_missing_fields_both_not_exist(self):
        """Test get_missing_fields when neither digestate nor energy exist"""
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        missing_fields = BiomethaneAnnualDeclarationService.get_missing_fields(declaration)

        self.assertIsNone(missing_fields["digestate_missing_fields"])
        self.assertIsNone(missing_fields["energy_missing_fields"])

    def test_get_required_fields_with_valid_model(self):
        """Test get_required_fields returns all field names for a model"""
        # Test with BiomethaneDigestate model
        fields = BiomethaneAnnualDeclarationService.get_required_fields(BiomethaneDigestate)

        # Assert we get a list of field names
        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) > 0)

        # Check some known fields are present
        self.assertIn("producer", fields)
        self.assertIn("year", fields)
        self.assertIn("raw_digestate_tonnage_produced", fields)

    def test_is_declaration_complete_with_incomplete_data(self):
        """Test is_declaration_complete returns False when required fields are missing"""
        missing_fields = {
            "digestate_missing_fields": ["xxx"],
            "energy_missing_fields": ["yyy"],
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
        """Test is_declaration_complete returns False when no digestate/energy exist"""
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
