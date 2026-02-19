from datetime import date, timedelta

from django.core.management.base import BaseCommand

from tiruert.models import Operation
from tiruert.models.declaration_period import TiruertDeclarationPeriod


class Command(BaseCommand):
    help = """
    The next day of a declaration period's last day, update 'status' to CANCELED
    for all PENDING teneur operations of this closed period.

    Usage:
        python web/manage.py cancel_teneur_operations
    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)
        period_closed_yesterday = TiruertDeclarationPeriod.object.filter(end_date=yesterday).first()

        if period_closed_yesterday:
            pending_teneur_operations = Operation.objects.filter(
                type=Operation.TENEUR,
                status=Operation.PENDING,
                declaration_year=period_closed_yesterday.year,
            )
            count = pending_teneur_operations.count()
            pending_teneur_operations.update(status=Operation.CANCELED)

            self.stdout.write(
                self.style.SUCCESS(
                    f"{count} teneur operations have been canceled for declaration year {period_closed_yesterday.year}."
                )
            )
