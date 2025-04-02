import logging

from django.db import transaction

from user.models import InactiveUser

logger = logging.getLogger(__name__)


class UserAnonymizationService:
    """
    Service managing the anonymization of inactive users.
    """

    @classmethod
    @transaction.atomic
    def process_inactive_users(cls):
        """
        Processes all inactive users according to defined rules:
        - Deactivate accounts inactive for more than 18 months
        - Anonymize accounts inactive for more than 3 years

        Returns a tuple with the number of users deactivated and anonymized.
        """
        # First anonymize GDPR accounts (3+ years)
        count_anonymized = InactiveUser.anonymize_gdpr_accounts()
        logger.info(f"{count_anonymized} users anonymized for GDPR compliance")

        # Then deactivate security accounts (18+ months to 3 years)
        count_deactivated = InactiveUser.deactivate_security_accounts()
        logger.info(f"{count_deactivated} users deactivated for security reasons")

        return count_deactivated, count_anonymized
