from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Manager, Q
from django.utils import timezone

User = get_user_model()


class SecurityInactiveUserManager(Manager):
    """
    Manager handling users inactive for security purposes (18+ months).
    """

    def get_queryset(self):
        eighteen_months_ago = timezone.now() - timedelta(days=18 * 30)
        return super().get_queryset().filter(Q(last_login__lt=eighteen_months_ago) & Q(is_active=True))

    def to_deactivate(self):
        """
        Returns users that should be deactivated but not anonymized.
        Excludes users that should be anonymized (3+ years).
        """
        three_years_ago = timezone.now() - timedelta(days=3 * 365)
        return self.get_queryset().exclude(last_login__lt=three_years_ago)


class GDPRInactiveUserManager(Manager):
    """
    Manager handling users inactive for GDPR purposes (3+ years).
    """

    def get_queryset(self):
        three_years_ago = timezone.now() - timedelta(days=3 * 365)
        return (
            super()
            .get_queryset()
            .filter(
                Q(last_login__lt=three_years_ago) & Q(is_active=True)
                | (~Q(email__contains="@anonymized.carbure") & Q(last_login__lt=three_years_ago))
            )
        )


class DisabledManager(Manager):
    """
    Manager that raises an exception when used, to prevent using the default manager.
    """

    def get_queryset(self):
        raise NotImplementedError(
            "Default manager is disabled. Please use specialized managers: " "InactiveUser.security or InactiveUser.gdpr"
        )


class InactiveUser(User):
    """
    Proxy model for managing inactive users with specialized managers.

    This model provides:
    - A 'security' manager for users inactive for 18+ months (security risk)
    - A 'gdpr' manager for users inactive for 3+ years (data privacy compliance)
    - Helper methods to process these inactive users

    The default manager is disabled to encourage use of specialized managers.
    """

    # Replace default manager
    objects = DisabledManager()
    security = SecurityInactiveUserManager()
    gdpr = GDPRInactiveUserManager()

    class Meta:
        proxy = True

    @classmethod
    def deactivate_security_accounts(cls):
        """
        Deactivates accounts that are inactive for security reasons (18+ months)
        but don't need to be anonymized yet.

        Returns count of deactivated users.
        """
        count = 0
        for user in cls.security.to_deactivate():
            if user.is_active:
                user.is_active = False
                user.save(update_fields=["is_active"])
                count += 1
        return count

    @classmethod
    def anonymize_gdpr_accounts(cls):
        """
        Anonymizes accounts that are inactive for GDPR compliance (3+ years).

        Returns count of anonymized users.
        """
        count = 0

        for user in cls.gdpr.all():
            sanitized_values = {
                "email": f"anonymized_{user.id}@anonymized.carbure",
                "name": "Anonymized User",
                "is_active": False,
            }
            if user.is_active or not user.email.endswith("@anonymized.carbure"):
                user.update(**sanitized_values)
                user.save(update_fields=sanitized_values.keys())
                count += 1
        return count
