from datetime import date, timedelta

from django.core.management.base import BaseCommand

from tiruert.models.declaration_period import TiruertDeclarationPeriod
from tiruert.models.operation import Operation


class Command(BaseCommand):
    help = """
    Set selected operations status to EXPIRED the next day of a declaration period's last day.
    This command should be run every day.

    Usage:
        python web/manage.py set_operations_expired
    """

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)
        period_closed_yesterday = TiruertDeclarationPeriod.objects.filter(end_date=yesterday).first()

        if period_closed_yesterday:
            types = [
                Operation.INCORPORATION,
                Operation.MAC_BIO,
                Operation.LIVRAISON_DIRECTE,
            ]
            period = period_closed_yesterday.year - 1

            operations_to_update = Operation.objects.filter(
                type__in=types,
                durability_period__startswith=str(period),
            )
            count = operations_to_update.count()
            operations_to_update.update(status=Operation.EXPIRED)

            self.stdout.write(
                self.style.SUCCESS(
                    f"{count} operations have been set to EXPIRED for declaration year {period_closed_yesterday.year}."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("No declaration period closed yesterday. No operations updated."))
