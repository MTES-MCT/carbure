from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models.biomethane_annual_declaration import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.views.annual_declaration.annual_declaration import BiomethaneAnnualDeclarationViewSet
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

        self.current_year = BiomethaneAnnualDeclarationService.get_declaration_period()
        self.annual_declaration_url = reverse("biomethane-annual-declaration")
        self.base_params = {"entity_id": self.producer_entity.id}

    @patch("biomethane.views.annual_declaration.annual_declaration.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that the write actions are correctly defined"""
        viewset = BiomethaneAnnualDeclarationViewSet()
        viewset.action = "retrieve"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with(
            ["partial_update", "validate_annual_declaration"], "retrieve"
        )

    def test_retrieve_creates_declaration_if_not_exists(self):
        """Test that retrieve creates a new declaration if it doesn't exist"""
        response = self.client.get(self.annual_declaration_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["year"], self.current_year)
        self.assertEqual(response.data["status"], BiomethaneAnnualDeclaration.IN_PROGRESS)
        self.assertIn("missing_fields", response.data)
        self.assertIn("digestate_missing_fields", response.data["missing_fields"])
        self.assertIn("energy_missing_fields", response.data["missing_fields"])
        self.assertIn("is_complete", response.data)

        # Verify that the declaration was created in the database
        declaration = BiomethaneAnnualDeclaration.objects.get(producer=self.producer_entity, year=self.current_year)
        self.assertEqual(declaration.status, BiomethaneAnnualDeclaration.IN_PROGRESS)

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
