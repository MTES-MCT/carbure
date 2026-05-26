from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user


class ExportAnnualDeclarationViewTests(TestCase):
    def setUp(self):
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
        self.url = reverse("biomethane-annual-export")
        self.base_params = {"entity_id": self.producer_entity.id, "year": 2025}

    def test_missing_year_returns_400(self):
        """year param is required — omitting it returns a 400 with an error message."""
        response = self.client.get(self.url, {"entity_id": self.producer_entity.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "year parameter is required")

    def test_unknown_producer_id_returns_404(self):
        """A producer_id that does not exist returns a 404 with an error message."""
        response = self.client.get(self.url, {**self.base_params, "producer_id": 999999})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "producer not found")

    def test_response_content_type_is_excel_and_attachment(self):
        """Successful export returns application/vnd.ms-excel content type and Content-Disposition attachment header."""
        response = self.client.get(self.url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/vnd.ms-excel")
        self.assertTrue(response["Content-Disposition"].startswith("attachment"))
