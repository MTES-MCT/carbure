from django.test import TestCase

from core.models import Entity
from core.tests_utils import FiltersActionTestMixin, setup_current_user
from doublecount.factories import DoubleCountingApplicationFactory
from doublecount.models import DoubleCountingApplication
from doublecount.views.applications.application import ApplicationViewSet
from transactions.models import ProductionSite


class ApplicationFiltersTest(TestCase, FiltersActionTestMixin):
    """Test FiltersActionFactory endpoint for double-counting applications"""

    fixtures = [
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # Get production sites from fixtures
        cls.production_site1 = ProductionSite.objects.first()
        cls.production_site2 = (
            ProductionSite.objects.all()[1] if ProductionSite.objects.count() > 1 else cls.production_site1
        )

        # Create test applications with different statuses and certificate IDs
        DoubleCountingApplicationFactory.create(
            production_site=cls.production_site1,
            certificate_id="CERT-001",
            status=DoubleCountingApplication.ACCEPTED,
        )

        DoubleCountingApplicationFactory.create(
            production_site=cls.production_site2,
            certificate_id="CERT-002",
            status=DoubleCountingApplication.REJECTED,
        )

        DoubleCountingApplicationFactory.create(
            production_site=cls.production_site1,
            certificate_id="CERT-003",
            status=DoubleCountingApplication.PENDING,
        )

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN).first()
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "TEST", [(self.admin, "ADMIN")], True)

    def test_filter_certificate_id(self):
        """Test certificate_id filter returns all certificate IDs"""
        self.assertFilterOptions(
            ApplicationViewSet,
            "certificate_id",
            ["CERT-001", "CERT-002", "CERT-003"],
            entity=self.admin,
        )

    def test_filter_production_sites(self):
        """Test production_sites filter returns unique production site names"""
        site_names = sorted([self.production_site1.name, self.production_site2.name])
        expected = list(dict.fromkeys(site_names))  # Remove duplicates while preserving order

        self.assertFilterOptions(
            ApplicationViewSet,
            "production_sites",
            expected,
            entity=self.admin,
        )

    def test_filter_status_values(self):
        """Test status_values filter returns actual model status values"""
        status_values = sorted(
            [
                DoubleCountingApplication.ACCEPTED,
                DoubleCountingApplication.REJECTED,
                DoubleCountingApplication.PENDING,
            ]
        )

        self.assertFilterOptions(
            ApplicationViewSet,
            "status_values",
            status_values,
            entity=self.admin,
        )

    def test_filter_with_status_rejected(self):
        """Verify that status='rejected' custom filter value works correctly"""
        # Using status=rejected should only show CERT-002
        self.assertFilterOptions(
            ApplicationViewSet,
            "certificate_id",
            ["CERT-002"],
            params={"status": "rejected"},
            entity=self.admin,
        )

    def test_filter_with_status_pending(self):
        """Verify that status='pending' custom filter value works correctly"""
        # Using status=pending should only show CERT-003
        self.assertFilterOptions(
            ApplicationViewSet,
            "certificate_id",
            ["CERT-003"],
            params={"status": "pending"},
            entity=self.admin,
        )

    def test_filter_producers(self):
        """Test producers filter returns unique producer entity names"""
        producer_names = sorted(
            {
                self.production_site1.created_by.name,
                self.production_site2.created_by.name,
            }
        )

        self.assertFilterOptions(
            ApplicationViewSet,
            "producers",
            producer_names,
            entity=self.admin,
        )
