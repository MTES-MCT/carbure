from datetime import date

from rest_framework import serializers

from tiruert.models.declaration_period import TiruertDeclarationPeriod


class DeclarationPeriodService:
    @staticmethod
    def _get_current_declaration_period():
        """
        Determines the current declaration period based on the current date.

        Returns:
            TiruertDeclarationPeriod: The current declaration period for the year.

        Raises:
            serializers.ValidationError: If no declaration period exists for the current year.
        """
        today = date.today()
        period = (
            TiruertDeclarationPeriod.objects.filter(start_date__lte=today, end_date__gte=today).order_by("-year").first()
        )

        if not period:
            raise serializers.ValidationError("No declaration period found for the current year.")

        return period

    @staticmethod
    def get_current_declaration_year():
        """
        Determines the current declaration year based on the current date.

        Returns:
            int: The current declaration year.

        Raises:
            serializers.ValidationError: If no declaration period exists for the current year.
        """
        period = DeclarationPeriodService._get_current_declaration_period()
        return period.year

    @staticmethod
    def is_declaration_period_open():
        """
        Check if we are currently in the declaration period.

        Returns:
            bool: True if current date is within the declaration period, False otherwise.

        Raises:
            serializers.ValidationError: If no declaration period exists for the current year.
        """
        period = DeclarationPeriodService._get_current_declaration_period()
        return period.is_open
