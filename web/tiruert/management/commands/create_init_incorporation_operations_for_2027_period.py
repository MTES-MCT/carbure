import io
from collections import defaultdict

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Sum

from core import private_storage
from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from core.utils import truncate
from tiruert.models import Operation
from tiruert.services.operation import OperationService

DEFAULT_S3_PATH = "reliquats-2026/import_reliquat_operations.xlsx"


class Command(BaseCommand):
    help = "Create INCORPORATION operations from an Excel file stored on S3"

    def add_arguments(self, parser):
        parser.add_argument("--s3-path", default=DEFAULT_S3_PATH)

    def handle(self, *args, **options):
        s3_path = options.get("s3_path", DEFAULT_S3_PATH)
        rows = self._read_rows(s3_path)

        if not rows:
            raise CommandError("No rows found in the Excel file")

        self._validate_rows(rows)
        self._create_operations(rows)

        self.stdout.write(self.style.SUCCESS(f"Created {len(rows)} INCORPORATION operations"))

    def _read_rows(self, s3_path):
        with private_storage.open(s3_path, "rb") as handle:
            excel_bytes = handle.read()

        dataframe = pd.read_excel(io.BytesIO(excel_bytes))
        return dataframe.to_dict(orient="records")

    def _validate_rows(self, rows):
        errors = []
        seen_tuples = set()
        available_volumes = {}

        for line_number, row in enumerate(rows, start=2):
            entity_id = row.get("entity_id")
            biofuel_code = row.get("biofuel_code")
            customs_category = row.get("customs_category")
            volume = row.get("volume")

            if not entity_id:
                errors.append(f"Ligne {line_number}: entity_id is required")
                continue

            entity = Entity.objects.filter(pk=entity_id).first()
            if entity is None:
                errors.append(f"Ligne {line_number}: entity_id '{entity_id}' does not exist")
                continue

            if not biofuel_code:
                errors.append(f"Ligne {line_number}: biofuel_code is required")
                continue

            biofuel = Biocarburant.objects.filter(code=biofuel_code).first()
            if biofuel is None:
                errors.append(f"Ligne {line_number}: biofuel_code '{biofuel_code}' does not exist")
                continue

            if not customs_category:
                errors.append(f"Ligne {line_number}: customs_category is required")
                continue

            if customs_category not in dict(MatierePremiere.MP_CATEGORIES):
                errors.append(f"Ligne {line_number}: customs_category '{customs_category}' does not exist")
                continue

            if volume is None or volume == "":
                errors.append(f"Ligne {line_number}: volume is required")
                continue

            try:
                volume = float(volume)
            except (TypeError, ValueError):
                errors.append(f"Ligne {line_number}: volume '{volume}' is invalid")
                continue

            if volume <= 0:
                errors.append(f"Ligne {line_number}: volume must be strictly positive")
                continue

            tuple_key = (entity.id, biofuel.id, customs_category)
            if tuple_key in seen_tuples:
                errors.append(
                    f"Ligne {line_number}: duplicate tuple (entity_id={entity.id}, biofuel_code={biofuel.code}, customs_category={customs_category})"  # noqa: E501
                )
                continue

            seen_tuples.add(tuple_key)

            available_volumes[tuple_key] = self._get_available_volume(entity, biofuel, customs_category)
            available_volume = available_volumes[tuple_key]

            if volume > available_volume:
                errors.append(f"Ligne {line_number}: requested volume {volume} exceeds available volume {available_volume}")

        if errors:
            raise CommandError("\n".join(errors))

    def _get_lots(self, entity, biofuel, customs_category):
        return CarbureLot.objects.filter(
            carbure_client=entity,
            biofuel=biofuel,
            feedstock__category=customs_category,
            year=2026,
        ).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.REJECTED])

    def _get_available_volume(self, entity, biofuel, customs_category):
        lots = self._get_lots(entity, biofuel, customs_category)
        return float(lots.aggregate(total_volume=Sum("volume"))["total_volume"] or 0.0)

    def _create_operations(self, rows):
        with transaction.atomic():
            for row in rows:
                entity_id = row.get("entity_id")
                biofuel_code = row.get("biofuel_code")
                customs_category = row.get("customs_category")
                entity = Entity.objects.get(pk=entity_id)
                biofuel = Biocarburant.objects.get(code=biofuel_code)
                self._create_operations_for_entity(entity, biofuel, customs_category, row)

    def _create_operations_for_entity(self, entity, biofuel, customs_category, row):
        lots = list(self._get_lots(entity, biofuel, customs_category).order_by("volume", "id"))

        if not lots:
            return

        total_lot_volume = sum(lot.volume for lot in lots)
        if total_lot_volume <= 0:
            return

        grouped_lots = defaultdict(list)
        for lot in lots:
            grouped_lots[lot.ghg_total].append(lot)

        operation_volume = float(row.get("volume", 0))
        ratio = self._calculate_ratio(operation_volume, total_lot_volume)

        operation_data = {
            "type": Operation.INCORPORATION,
            "status": Operation.ACCEPTED,
            "credited_entity": entity,
            "debited_entity": None,
            "customs_category": customs_category,
            "biofuel": biofuel,
            "declaration_year": 2027,
        }

        details_data = []
        for group_lots in grouped_lots.values():
            group_total_volume = sum(lot.volume for lot in group_lots)
            volume_to_keep = ratio * group_total_volume
            lot_volumes = self._calculate_lot_volumes(group_lots, volume_to_keep)

            emissions_by_lot = {lot.id: lot.ghg_total for lot in group_lots}
            details_data.extend(OperationService.build_details_data(lot_volumes, emissions_by_lot))

        self._adjust_details_data_to_target(details_data, operation_volume)

        lots_taken_count = sum(1 for detail in details_data if detail["volume"] > 0)
        self.stdout.write(
            self.style.SUCCESS(
                "Import row for entity=%s biofuel=%s customs_category=%s: total_lots_volume=%s total_lots=%s kept_volume=%s ratio=%s lots_taken=%s"  # noqa: E501
                % (
                    entity.id,
                    biofuel.code,
                    customs_category,
                    total_lot_volume,
                    len(lots),
                    sum(detail["volume"] for detail in details_data),
                    ratio,
                    lots_taken_count,
                )
            )
        )

        OperationService.create_operation_with_details(operation_data, details_data)

    def _calculate_ratio(self, requested_volume, total_lot_volume):
        if total_lot_volume <= 0:
            return 0.0

        return requested_volume / total_lot_volume

    def _calculate_lot_volumes(self, lots, volume_to_keep):
        """Calculate the volume to keep for each lot, filling them in order until the target volume is reached."""
        if not lots:
            return {}

        remaining_to_keep = volume_to_keep
        lot_volumes = {}

        for lot in lots:
            if remaining_to_keep <= 0:
                continue

            lot_volume = min(lot.volume, remaining_to_keep)
            lot_volumes[lot.id] = truncate(lot_volume, 2)
            remaining_to_keep -= lot_volume

        return lot_volumes

    def _adjust_details_data_to_target(self, details_data, target_volume):
        """Adjust the last non-zero detail volume so the total matches the target volume."""
        total_kept_volume = sum(detail["volume"] for detail in details_data)
        if total_kept_volume >= target_volume:
            return

        difference = round(target_volume - total_kept_volume, 2)
        for detail in reversed(details_data):
            if detail["volume"] > 0:
                detail["volume"] += difference
                break
