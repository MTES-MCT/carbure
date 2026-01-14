from unittest import mock

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity
from core.tests_utils import setup_current_user


class ValidateAnnualDeclarationAPITests(TestCase):
    def setUp(self):
        """Initial setup for API tests."""
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

        self.validate_url = reverse("biomethane-annual-declaration-validate")
        self.base_params = {"entity_id": self.producer_entity.id}

    @mock.patch(
        "biomethane.services.annual_declaration.BiomethaneAnnualDeclarationService.is_declaration_complete",
        return_value=True,
    )
    def test_validate_digestate_endpoint_success(self, mock_is_complete):
        """Test successful validation via API endpoint."""
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=BiomethaneAnnualDeclarationService.get_current_declaration_year(),
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.post(self.validate_url, query_params=self.base_params)

        mock_is_complete.assert_called_once_with(declaration)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify declaration status was updated
        declaration.refresh_from_db()
        self.assertEqual(declaration.status, BiomethaneAnnualDeclaration.DECLARED)

    @mock.patch(
        "biomethane.services.annual_declaration.BiomethaneAnnualDeclarationService.is_declaration_complete",
        return_value=False,
    )
    def test_validate_digestate_endpoint_incomplete(self, mock_is_complete):
        """Test validation when declaration is incomplete."""
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_entity,
            year=BiomethaneAnnualDeclarationService.get_current_declaration_year(),
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.post(self.validate_url, query_params=self.base_params)

        mock_is_complete.assert_called_once_with(declaration)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify declaration status was not updated
        declaration.refresh_from_db()
        self.assertEqual(declaration.status, BiomethaneAnnualDeclaration.IN_PROGRESS)

    def test_validate_digestate_endpoint_not_found(self):
        """Test validation when declaration doesn't exist."""
        response = self.client.post(self.validate_url, query_params=self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
