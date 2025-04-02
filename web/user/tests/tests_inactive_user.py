from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from user.models import InactiveUser

User = get_user_model()


class InactiveUserModelTest(TestCase):
    def setUp(self):
        # Recently active user
        self.active_user = User.objects.create_user(name="Active User", email="active@example.com", is_active=True)
        self.active_user.last_login = timezone.now()
        self.active_user.save()

        # User inactive for 20 months (security risk)
        self.security_user = User.objects.create_user(
            name="Security Risk User", email="security@example.com", is_active=True
        )
        self.security_user.last_login = timezone.now() - timedelta(days=20 * 30)
        self.security_user.save()

        # User inactive for 4 years (GDPR compliance)
        self.gdpr_user = User.objects.create_user(name="GDPR User", email="gdpr@example.com", is_active=True)
        self.gdpr_user.last_login = timezone.now() - timedelta(days=4 * 365)
        self.gdpr_user.save()

    def test_security_manager(self):
        # Test the security manager
        security_users = InactiveUser.security.all()
        assert security_users.count() == 2
        assert self.security_user.id in security_users.values_list("id", flat=True)
        assert self.gdpr_user.id in security_users.values_list("id", flat=True)

        # Test users to deactivate (18+ months but not 3+ years)
        to_deactivate = InactiveUser.security.to_deactivate()
        assert to_deactivate.count() == 1
        assert self.security_user.id in to_deactivate.values_list("id", flat=True)

    def test_gdpr_manager(self):
        # Test the GDPR manager
        gdpr_users = InactiveUser.gdpr.all()
        assert gdpr_users.count() == 1
        assert self.gdpr_user.id in gdpr_users.values_list("id", flat=True)

    def test_deactivate_security_accounts(self):
        # Test the method to deactivate security accounts
        count = InactiveUser.deactivate_security_accounts()
        assert count == 1

        self.security_user.refresh_from_db()
        assert not self.security_user.is_active
        assert self.security_user.email == "security@example.com"  # Email unchanged

        # GDPR users should not be affected by this method
        self.gdpr_user.refresh_from_db()
        assert self.gdpr_user.is_active

    def test_anonymize_gdpr_accounts(self):
        # Test the method to anonymize GDPR accounts
        count = InactiveUser.anonymize_gdpr_accounts()
        assert count == 1

        self.gdpr_user.refresh_from_db()
        assert not self.gdpr_user.is_active
        assert self.gdpr_user.email == f"anonymized_{self.gdpr_user.id}@anonymized.carbure"
        assert self.gdpr_user.name == "Anonymized User"

        # Security users should not be affected by this method
        self.security_user.refresh_from_db()
        assert self.security_user.is_active
        assert self.security_user.email == "security@example.com"
