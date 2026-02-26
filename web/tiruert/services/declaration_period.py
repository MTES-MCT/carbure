from datetime import date

from tiruert.models.declaration_period import TiruertDeclarationPeriod


class DeclarationPeriodService:
    @staticmethod
    def _get_current_declaration_period():
        """
        Determines the current declaration period based on the current date.

        Returns:
            TiruertDeclarationPeriod | None: The current declaration period, or None if not found.
        """
        today = date.today()
        return TiruertDeclarationPeriod.objects.filter(start_date__lte=today, end_date__gte=today).order_by("-year").first()

    @staticmethod
    def get_current_declaration_year():
        """
        Determines the current declaration year based on the current date.

        Returns:
            int | None: The current declaration year, or None if no period is configured.
        """
        period = DeclarationPeriodService._get_current_declaration_period()
        return period.year if period else None
