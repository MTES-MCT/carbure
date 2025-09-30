from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories.digestate import BiomethaneDigestateFactory
from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.utils import get_declaration_period
from core.models import Entity
from core.tests_utils import setup_current_user


class ValidateDigestateAPITests(TestCase):
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

        self.validate_url = reverse("biomethane-digestate-validate")
        self.base_params = {"entity_id": self.producer_entity.id}

    def test_validate_digestate_endpoint_success(self):
        """Test successful validation via API endpoint."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            year=get_declaration_period(),
        )

        response = self.client.post(self.validate_url, query_params=self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify digestate status was updated
        digestate.refresh_from_db()
        self.assertEqual(digestate.status, BiomethaneDigestate.VALIDATED)

    def test_validate_digestate_endpoint_not_found(self):
        """Test validation when digestate doesn't exist."""
        response = self.client.post(self.validate_url, query_params=self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
