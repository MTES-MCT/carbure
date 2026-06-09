from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count

from tiruert.models import Operation
from tiruert.models.declaration_period import TiruertDeclarationPeriod


class Command(BaseCommand):
    help = """
    The next day of a declaration period's last day, update 'status' to CANCELED
    for all PENDING teneur operations of this closed period.
    This command should be run every day.

    Usage:
        python web/manage.py cancel_closed_period_operations
    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)
        period_closed_yesterday = TiruertDeclarationPeriod.objects.filter(end_date=yesterday).first()

        if period_closed_yesterday:
            pending_or_draft_operations = Operation.objects.filter(
                type__in=Operation.API_DELETABLE_TYPES,
                status__in=[Operation.PENDING, Operation.DRAFT],
                declaration_year=period_closed_yesterday.year,
            )

            operation_counts_by_type = {
                row["type"]: row["count"]
                for row in pending_or_draft_operations.values("type").annotate(count=Count("id")).order_by("type")
            }

            count = sum(operation_counts_by_type.values())

            pending_or_draft_operations.update(status=Operation.CANCELED)

            self.stdout.write(
                self.style.SUCCESS(
                    f"{count} operations have been canceled for declaration year {period_closed_yesterday.year}."
                )
            )

            for operation_type, operation_count in operation_counts_by_type.items():
                self.stdout.write(self.style.SUCCESS(f"- {operation_type}: {operation_count} operation(s) canceled"))
        else:
            self.stdout.write(self.style.SUCCESS("No declaration period closed yesterday. No operations canceled."))
