from django.test import TestCase

from core.models import Entity
from core.tests_utils import setup_current_user
from doublecount.factories import DoubleCountingApplicationFactory
from doublecount.models import DoubleCountingApplication
from transactions.models import ProductionSite


class ApplicationUpdateStatusTest(TestCase):
    """Integration test for PATCH endpoint on status field"""

    fixtures = [
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.admin = Entity.objects.filter(entity_type=Entity.ADMIN).first()
        cls.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).first()
        cls.production_site = ProductionSite.objects.first()

    def setUp(self):
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "TEST", [(self.admin, "ADMIN")], True)

        # Create pending application for each test
        self.application = DoubleCountingApplicationFactory.create(
            production_site=self.production_site,
            certificate_id="CERT-001",
            status=DoubleCountingApplication.PENDING,
        )

    def test_patch_status_integration(self):
        """Test that PATCH endpoint correctly updates application status through full stack"""
        response = self.client.patch(
            f"/api/double-counting/applications/{self.application.id}/",
            {"status": DoubleCountingApplication.WAITING_FOR_DECISION},
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.admin.id}",
        )

        self.assertEqual(response.status_code, 200)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, DoubleCountingApplication.WAITING_FOR_DECISION)
