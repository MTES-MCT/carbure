from datetime import date, timedelta

from django.core.management.base import BaseCommand

from tiruert.models.declaration_period import TiruertDeclarationPeriod
from tiruert.services.declaration_period import DeclarationPeriodService
from tiruert.services.yearly_balance import YearlyBalanceService


class Command(BaseCommand):
    help = """
    Create YEARLY_BALANCE operations taking a snapshot of every entity balance
    (one operation per biofuel / customs_category) when a declaration year is closed.

    These operations are informative only: they are returned by the /operation/ endpoint
    but are never taken into account in balance or total volume computations.

    This command should be run every day (the snapshot is only created the day
    after a declaration period end date).

    Usage:
        python web/manage.py create_yearly_balance_operations
    """

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)
        period_closed_yesterday = TiruertDeclarationPeriod.objects.filter(end_date=yesterday).first()

        if not period_closed_yesterday:
            self.stdout.write(self.style.SUCCESS("No declaration period closed yesterday. No snapshot created."))
            return

        year = DeclarationPeriodService.get_current_declaration_year()
        declaration_end_date = period_closed_yesterday.end_date

        if YearlyBalanceService.snapshot_exists(year):
            self.stdout.write(self.style.WARNING(f"YEARLY_BALANCE operations already exist for year {year}. Skipping."))
            return

        self.stdout.write(f"Creating YEARLY_BALANCE operations for declaration year {year}...")

        operations_created = YearlyBalanceService.create_snapshot(year, declaration_end_date)

        self.stdout.write(self.style.SUCCESS(f"Created {operations_created} YEARLY_BALANCE operations for year {year}."))
