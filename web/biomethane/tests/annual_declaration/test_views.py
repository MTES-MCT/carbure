from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models.biomethane_annual_declaration import BiomethaneAnnualDeclaration
from biomethane.models.biomethane_declaration_period import BiomethaneDeclarationPeriod
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity
from core.tests_utils import setup_current_user


class BiomethaneAnnualDeclarationViewSetTests(TestCase):
    def setUp(self):
        """Initial setup for tests"""
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.producer_entity, "RW")],
        )

        self.current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        self.annual_declaration_url = reverse("biomethane-annual-declaration")
        self.base_params = {"entity_id": self.producer_entity.id}

        # Create an open declaration period for the current year
        BiomethaneDeclarationPeriod.objects.create(
            year=self.current_year,
            start_date="2026-01-01",
            end_date="2026-03-31",
        )

    def test_retrieve_creates_declaration_if_not_exists(self):
        """Test that retrieve creates a new declaration if it doesn't exist"""
        # Mock date to ensure we're within the declaration period
        with (
            patch("biomethane.services.annual_declaration.date") as mock_date_service,
            patch("biomethane.models.biomethane_declaration_period.date") as mock_date_model,
        ):
            mock_date_service.today.return_value = date(2026, 2, 15)
            mock_date_model.today.return_value = date(2026, 2, 15)

            response = self.client.get(self.annual_declaration_url, self.base_params)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data["year"], self.current_year)
            self.assertEqual(response.data["status"], BiomethaneAnnualDeclaration.IN_PROGRESS)
            self.assertTrue(response.data["is_open"])
            self.assertIn("missing_fields", response.data)
            self.assertIn("digestate_missing_fields", response.data["missing_fields"])
            self.assertIn("energy_missing_fields", response.data["missing_fields"])
            self.assertIn("is_complete", response.data)

            # Verify that the declaration was created in the database
            declaration = BiomethaneAnnualDeclaration.objects.get(producer=self.producer_entity, year=self.current_year)
            self.assertEqual(declaration.status, BiomethaneAnnualDeclaration.IN_PROGRESS)
            self.assertTrue(declaration.is_open)

    def test_retrieve_returns_existing_declaration(self):
        """Test successful retrieval of an existing declaration"""
        # Create an existing declaration
        _declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.get(self.annual_declaration_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["year"], self.current_year)
        self.assertEqual(response.data["status"], BiomethaneAnnualDeclaration.IN_PROGRESS)
        self.assertIn("missing_fields", response.data)
        self.assertIn("digestate_missing_fields", response.data["missing_fields"])
        self.assertIn("energy_missing_fields", response.data["missing_fields"])
        self.assertIn("is_complete", response.data)

    def test_partial_update_to_in_progress_success(self):
        """Test successful partial update of declaration status to IN_PROGRESS"""
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        update_data = {"status": BiomethaneAnnualDeclaration.IN_PROGRESS}

        response = self.client.patch(
            self.annual_declaration_url,
            update_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], BiomethaneAnnualDeclaration.IN_PROGRESS)

        declaration.refresh_from_db()
        self.assertEqual(declaration.status, BiomethaneAnnualDeclaration.IN_PROGRESS)

    def test_partial_update_already_in_progress(self):
        """Test partial update when declaration is already IN_PROGRESS"""
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        update_data = {"status": BiomethaneAnnualDeclaration.IN_PROGRESS}

        response = self.client.patch(
            self.annual_declaration_url,
            update_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], BiomethaneAnnualDeclaration.IN_PROGRESS)

    def test_partial_update_to_declared_forbidden(self):
        """Test that partial update to DECLARED status is forbidden"""
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        update_data = {"status": BiomethaneAnnualDeclaration.DECLARED}

        response = self.client.patch(
            self.annual_declaration_url,
            update_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

        declaration.refresh_from_db()
        self.assertEqual(declaration.status, BiomethaneAnnualDeclaration.DECLARED)

    def test_partial_update_declaration_not_found(self):
        """Test 404 return when trying to update a non-existing declaration"""
        update_data = {"status": BiomethaneAnnualDeclaration.IN_PROGRESS}

        response = self.client.patch(
            self.annual_declaration_url,
            update_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_filters_by_current_year(self):
        """Test that retrieve only returns declaration for current year"""
        # Create declarations for different years
        _old_declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year - 1,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        _current_declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.get(self.annual_declaration_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["year"], self.current_year)
        self.assertNotEqual(response.data["year"], self.current_year - 1)

    def test_retrieve_closed_declaration_period_returns_404(self):
        """Test that retrieve returns 404 when declaration period is closed"""
        # Remove the open declaration period
        BiomethaneDeclarationPeriod.objects.filter(year=self.current_year).delete()

        response = self.client.get(self.annual_declaration_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_declaration_is_open_field_default_value(self):
        """Test that is_open field has default value of True when creating a declaration"""
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        self.assertTrue(declaration.is_open)
