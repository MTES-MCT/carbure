from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.db.models import F, Q, QuerySet

from core.models import MatierePremiere
from tiruert.models import Operation, OperationDetail

EP2_CODE = "EP2"
EP2_CATEGORIES = [MatierePremiere.CONV, MatierePremiere.EP2AM]
EP2_EXCEPTION = Q(lot__feedstock__code=EP2_CODE, operation__customs_category__in=EP2_CATEGORIES)


class Command(BaseCommand):
    help = """
    Repair historical TIRUERT operations whose category differs from linked lot feedstocks.

    Mixed operations are cloned once per corrected category. Details are moved to
    the operation matching their lot feedstock category. Operations whose details
    all point to the same corrected category are updated in place.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply category repairs. Without this flag, the command only reports impacted operations.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        apply = options["apply"]

        operation_ids = self._get_mismatched_operation_ids()

        if not operation_ids:
            self.stdout.write(self.style.SUCCESS("No operations with feedstock category mismatches found."))
            return

        if not apply:
            mixed_count, updated_count, details_to_move_count = self._collect_stats(operation_ids)
            self.stdout.write(
                self.style.WARNING(
                    "Dry run. Use --apply to repair data: "
                    f"{mixed_count} mixed operation(s) would be split, "
                    f"{updated_count} operation(s) would be updated in place, "
                    f"{details_to_move_count} detail(s) would be moved."
                )
            )
            return

        with transaction.atomic():
            mixed_count = 0
            updated_count = 0
            moved_details_count = 0

            operations = Operation.objects.select_for_update().filter(id__in=operation_ids).order_by("id")

            for operation in operations:
                total_details_count = operation.details.count()
                mismatched_categories = self._get_mismatched_categories(operation)

                # Nothing to repair if all remaining details already match the operation category.
                if not mismatched_categories:
                    continue

                # If every detail points to the same corrected category, keep the operation
                # and only update its category to avoid creating an empty clone.
                if len(mismatched_categories) == 1:
                    category = mismatched_categories[0]
                    category_details = self._get_details_for_category(operation, category)

                    if category_details.count() == total_details_count:
                        operation.customs_category = category
                        operation.save(update_fields=["customs_category"])
                        updated_count += 1
                        continue

                # Mixed operation: create one clone per mismatched category and move only those mismatched details.
                # Details matching the original category are not selected by _get_mismatched_categories(),
                # so they remain unaffected, and linked to the original operation.
                for category in mismatched_categories:
                    category_details = self._get_details_for_category(operation, category)
                    category_operation = self._clone_operation_with_category(operation, category)
                    moved_details_count += category_details.update(operation=category_operation)
                    mixed_count += 1

                # If every detail was moved away, the original no longer represents any volume
                # and should not remain as an empty operation.
                if not OperationDetail.objects.filter(operation=operation).exists():
                    operation.delete()

        if mixed_count:
            self.stdout.write(self.style.SUCCESS(f"Split {mixed_count} mismatched category group(s)."))
        if updated_count:
            self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} operation(s) in place."))
        if moved_details_count:
            self.stdout.write(self.style.SUCCESS(f"Moved {moved_details_count} operation detail(s)."))

    @staticmethod
    def _get_mismatched_operation_ids() -> list[int]:
        return list(
            OperationDetail.objects.exclude(lot__feedstock__category=F("operation__customs_category"))
            .exclude(EP2_EXCEPTION)
            .values_list("operation_id", flat=True)
            .distinct()
        )

    @staticmethod
    def _collect_stats(operation_ids: list[int]) -> tuple[int, int, int]:
        mixed_count = 0
        updated_count = 0
        details_to_move_count = 0

        for operation in Operation.objects.filter(id__in=operation_ids).order_by("id"):
            total_details_count = operation.details.count()
            mismatched_categories = Command._get_mismatched_categories(operation)
            if not mismatched_categories:
                continue

            if len(mismatched_categories) == 1:
                category = mismatched_categories[0]
                category_details_count = Command._get_details_for_category(operation, category).count()
                if category_details_count == total_details_count:
                    updated_count += 1
                    continue

            for category in mismatched_categories:
                mixed_count += 1
                details_to_move_count += Command._get_details_for_category(operation, category).count()

        return mixed_count, updated_count, details_to_move_count

    @staticmethod
    def _get_mismatched_categories(operation: Operation) -> list[str]:
        categories = (
            operation.details.exclude(lot__feedstock__category=operation.customs_category)
            .exclude(EP2_EXCEPTION)
            .values_list("lot__feedstock__category", flat=True)
            .distinct()
            .order_by("lot__feedstock__category")
        )
        return list(categories)

    @staticmethod
    def _get_details_for_category(operation: Operation, category: str) -> QuerySet[OperationDetail]:
        return operation.details.filter(lot__feedstock__category=category)

    @staticmethod
    def _clone_operation_with_category(operation: Operation, category: str) -> Operation:
        category_operation = Operation.objects.create(
            type=operation.type,
            status=operation.status,
            customs_category=category,
            biofuel=operation.biofuel,
            credited_entity=operation.credited_entity,
            debited_entity=operation.debited_entity,
            from_depot=operation.from_depot,
            to_depot=operation.to_depot,
            export_country=operation.export_country,
            export_recipient=operation.export_recipient,
            declaration_year=operation.declaration_year,
            validation_date=operation.validation_date,
            renewable_energy_share=operation.renewable_energy_share,
            durability_period=operation.durability_period,
            objective_sector=operation.objective_sector,
        )
        Operation.objects.filter(id=category_operation.id).update(created_at=operation.created_at)
        category_operation.created_at = operation.created_at
        return category_operation
