from django.test import TestCase

from doublecount.factories import DoubleCountingApplicationFactory
from doublecount.models import DoubleCountingApplication
from doublecount.serializers import DoubleCountingApplicationUpdateSerializer


class DoubleCountingApplicationUpdateSerializerTest(TestCase):
    """Unit tests for DoubleCountingApplicationUpdateSerializer"""

    fixtures = [
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    def test_validate_status_accepts_authorized_status(self):
        """Test that authorised status values are accepted"""
        application = DoubleCountingApplicationFactory.create(status=DoubleCountingApplication.PENDING)

        for status in DoubleCountingApplicationUpdateSerializer.AUTHORIZED_STATUS_VALUES:
            serializer = DoubleCountingApplicationUpdateSerializer(instance=application, data={"status": status})
            self.assertTrue(serializer.is_valid(), f"Status {status} should be valid")

    def test_validate_status_rejects_accepted(self):
        """Test that ACCEPTED status is rejected"""
        application = DoubleCountingApplicationFactory.create(status=DoubleCountingApplication.PENDING)
        serializer = DoubleCountingApplicationUpdateSerializer(
            instance=application, data={"status": DoubleCountingApplication.ACCEPTED}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)

    def test_validate_status_rejects_rejected(self):
        """Test that REJECTED status is rejected"""
        application = DoubleCountingApplicationFactory.create(status=DoubleCountingApplication.PENDING)
        serializer = DoubleCountingApplicationUpdateSerializer(
            instance=application, data={"status": DoubleCountingApplication.REJECTED}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)

    def test_validate_status_rejects_update_from_accepted(self):
        """Test that applications with ACCEPTED status cannot be updated"""
        application = DoubleCountingApplicationFactory.create(status=DoubleCountingApplication.ACCEPTED)
        serializer = DoubleCountingApplicationUpdateSerializer(
            instance=application, data={"status": DoubleCountingApplication.PENDING}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
        self.assertIn("statut actuel", str(serializer.errors["status"][0]))

    def test_validate_status_rejects_update_from_rejected(self):
        """Test that applications with REJECTED status cannot be updated"""
        application = DoubleCountingApplicationFactory.create(status=DoubleCountingApplication.REJECTED)
        serializer = DoubleCountingApplicationUpdateSerializer(
            instance=application, data={"status": DoubleCountingApplication.PENDING}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
        self.assertIn("statut actuel", str(serializer.errors["status"][0]))

    def test_validate_status_allows_update_from_inprogress(self):
        """Test that applications with INPROGRESS status can be updated"""
        application = DoubleCountingApplicationFactory.create(status=DoubleCountingApplication.INPROGRESS)
        serializer = DoubleCountingApplicationUpdateSerializer(
            instance=application, data={"status": DoubleCountingApplication.WAITING_FOR_DECISION}
        )

        self.assertTrue(serializer.is_valid())

    def test_validate_status_allows_update_from_waiting_for_decision(self):
        """Test that applications with WAITING_FOR_DECISION status can be updated"""
        application = DoubleCountingApplicationFactory.create(status=DoubleCountingApplication.WAITING_FOR_DECISION)
        serializer = DoubleCountingApplicationUpdateSerializer(
            instance=application, data={"status": DoubleCountingApplication.INPROGRESS}
        )

        self.assertTrue(serializer.is_valid())

    def test_validate_status_rejects_invalid_status(self):
        """Test that invalid status values are rejected"""
        application = DoubleCountingApplicationFactory.create(status=DoubleCountingApplication.PENDING)
        serializer = DoubleCountingApplicationUpdateSerializer(instance=application, data={"status": "INVALID_STATUS"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
