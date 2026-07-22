from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from types import SimpleNamespace

from django.db import transaction
from rest_framework import serializers

from core.excel_importer import ExcelImporter, ExcelValidationError
from core.models import CarbureLot, Entity
from core.models.feedstock import Biocarburant
from tiruert.models import Operation
from tiruert.serializers.operation import OperationExcelRowSerializer, OperationImportResponseSerializer
from tiruert.services.declaration_period import DeclarationPeriodService
from tiruert.services.operation import OperationService
from tiruert.services.operation_excel_template import get_tiruert_operator_queryset


class OperationExcelImportErrors:
    INVALID_OPERATION_TYPE = "INVALID_OPERATION_TYPE"
    INVALID_VOLUME = "INVALID_VOLUME"
    MISSING_CREDITED_ENTITY = "MISSING_CREDITED_ENTITY"


# Columns added to the export template for display purposes only (not expected by the row serializer).
DISPLAY_ONLY_COLUMNS = ["credited_entity_name", "available_volume", "emission_rate_per_mj", "biofuel", "customs_category"]

EXCEL_IMPORT_CONFIG = {"header_row": 1}

# Row numbering starts at 3: row 1 is the header, row 2 the hidden technical keys.
FIRST_DATA_ROW_NUMBER = 3


def _get_sector(biofuel: Biocarburant) -> str:
    return OperationService.define_sector(biofuel)


def _default_status(operation_type: str) -> str:
    default_status = {
        Operation.TENEUR: Operation.PENDING,
        Operation.TRANSFERT: Operation.DRAFT,
    }
    return default_status.get(operation_type, Operation.DRAFT)


@dataclass
class OperationGroup:
    operation_type: str
    customs_category: str
    biofuel_id: int
    biofuel_code: str
    biofuel: Biocarburant
    sector: str
    credited_entity: Entity | None
    debited_entity: Entity
    row_numbers: list[int]
    first_row_by_lot: dict[int, int]
    lot_volumes: dict[int, float]


class OperationExcelImportService:
    @staticmethod
    def _parse_rows(file) -> list[dict]:
        """Parse the uploaded Excel file, keeping only rows with a requested volume."""
        parsed_data = ExcelImporter.parse(file, **EXCEL_IMPORT_CONFIG)

        rows = []
        for row in parsed_data:
            if row.get("volume") in (None, ""):
                continue

            for column in DISPLAY_ONLY_COLUMNS:
                row.pop(column, None)

            rows.append(row)

        return rows

    @staticmethod
    def _extract_ids(rows: list[dict], field: str) -> set[int]:
        """
        Collect the distinct valid int ids for a field across rows (invalid values are ignored here;
        they get reported as validation errors later on).
        """
        ids = set()
        for row in rows:
            value = row.get(field)
            if value in (None, ""):
                continue
            try:
                ids.add(int(value))
            except (TypeError, ValueError):
                continue
        return ids

    @staticmethod
    def _build_lookup_caches(rows: list[dict]) -> dict:
        """
        Pre-fetch lots and credited entities referenced in the rows, to avoid one DB query
        per row when the row serializer resolves `lot_id`/`credited_entity` (many=True).
        """
        lot_ids = OperationExcelImportService._extract_ids(rows, "lot_id")
        entity_ids = OperationExcelImportService._extract_ids(rows, "credited_entity")

        lot_cache = {lot.id: lot for lot in CarbureLot.objects.filter(id__in=lot_ids).select_related("biofuel", "feedstock")}
        credited_entity_cache = {entity.id: entity for entity in get_tiruert_operator_queryset().filter(id__in=entity_ids)}

        return {"lot_cache": lot_cache, "credited_entity_cache": credited_entity_cache}

    @staticmethod
    def _group_key(row: dict) -> tuple:
        lot = row["lot_id"]
        credited_entity = row["credited_entity"]
        return (
            row["operation_type"],
            lot.feedstock.category,
            lot.biofuel_id,
            credited_entity.id if credited_entity else None,
        )

    @staticmethod
    def _build_group_from_rows(key: tuple, rows: list[dict], debited_entity: Entity) -> OperationGroup:
        operation_type, customs_category, biofuel_id, _ = key
        first_row = rows[0]
        first_lot = first_row["lot_id"]

        lot_volumes: dict[int, float] = defaultdict(float)
        first_row_by_lot: dict[int, int] = {}
        row_numbers = []

        # If there are multiple rows for the same lot id, sum their volumes and keep track of row numbers.
        for row in rows:
            lot_id = row["lot_id"].id
            row_number = row["row_number"]

            lot_volumes[lot_id] += row["volume"]
            row_numbers.append(row_number)
            first_row_by_lot.setdefault(lot_id, row_number)

        return OperationGroup(
            operation_type=operation_type,
            customs_category=customs_category,
            biofuel_id=biofuel_id,
            biofuel_code=first_lot.biofuel.code,
            biofuel=first_lot.biofuel,
            sector=_get_sector(first_lot.biofuel),
            credited_entity=first_row["credited_entity"],
            debited_entity=debited_entity,
            row_numbers=row_numbers,
            first_row_by_lot=first_row_by_lot,
            lot_volumes=dict(lot_volumes),
        )

    @staticmethod
    def _build_groups(validated_rows: list[dict], debited_entity: Entity) -> list[OperationGroup]:
        """Group validated rows by operation_type, customs_category, biofuel and credited_entity."""
        grouped: dict[tuple, list[dict]] = defaultdict(list)

        for row_number, row in enumerate(validated_rows, start=FIRST_DATA_ROW_NUMBER):
            key = OperationExcelImportService._group_key(row)
            grouped[key].append({"row_number": row_number, **row})

        return [
            OperationExcelImportService._build_group_from_rows(key, rows, debited_entity) for key, rows in grouped.items()
        ]

    @staticmethod
    def _rows_for_error(group: OperationGroup, exc: serializers.ValidationError) -> list[int]:
        """Return the row numbers a validation error should be attached to.

        Lot-level errors (formatted as '<lot_id>: ...') are attached only to the first row
        of the offending lot. Any other error is attached to every row of the group.
        """
        lot_errors = exc.detail.get("lot_id") if isinstance(exc.detail, dict) else None
        if not lot_errors:
            return group.row_numbers

        if not isinstance(lot_errors, list):
            lot_errors = [lot_errors]

        targeted_rows = set()
        for error in lot_errors:
            prefix = str(error).split(":", 1)[0].strip()
            if prefix.isdigit():
                row_number = group.first_row_by_lot.get(int(prefix))
                if row_number is not None:
                    targeted_rows.add(row_number)

        return sorted(targeted_rows) if targeted_rows else group.row_numbers

    @staticmethod
    def _validate_group(group: OperationGroup, biofuel: Biocarburant, declaration_year) -> list[dict]:
        """Run business checks for a single group. Returns a list of {row, errors} dicts."""
        selected_lots = [{"id": lot_id, "volume": volume} for lot_id, volume in group.lot_volumes.items()]
        data = {
            "debited_entity": group.debited_entity,
            "biofuel": biofuel,
            "customs_category": group.customs_category,
            "type": group.operation_type,
        }
        request = SimpleNamespace(entity=group.debited_entity, GET={})

        try:
            OperationService.perform_checks_before_create(
                request=request,
                entity_id=group.debited_entity.id,
                selected_lots=selected_lots,
                data=data,
                unit="l",
                declaration_year=declaration_year,
            )
        except serializers.ValidationError as exc:
            rows = OperationExcelImportService._rows_for_error(group, exc)
            return [{"row": row_number, "errors": exc.detail} for row_number in rows]

        return []

    @staticmethod
    def _validate_groups(groups: list[OperationGroup], total_rows: int, declaration_year: int | None) -> None:
        errors = []
        for group in groups:
            if not group.lot_volumes:
                continue

            errors.extend(OperationExcelImportService._validate_group(group, group.biofuel, declaration_year))

        if errors:
            raise ExcelValidationError(errors, total_rows)

    @staticmethod
    def _build_operation_data(group: OperationGroup, declaration_year: int) -> dict:
        return {
            "type": group.operation_type,
            "status": _default_status(group.operation_type),
            "customs_category": group.customs_category,
            "biofuel_id": group.biofuel_id,
            "credited_entity": group.credited_entity,
            "debited_entity": group.debited_entity,
            "renewable_energy_share": 1,
            "declaration_year": declaration_year,
        }

    @staticmethod
    def _create_operation_for_group(
        group: OperationGroup, declaration_year: int, emissions_by_lot: dict[int, float]
    ) -> Operation:
        operation_data = OperationExcelImportService._build_operation_data(group, declaration_year)
        details_data = OperationService.build_details_data(group.lot_volumes, emissions_by_lot)
        return OperationService.create_operation_with_details(operation_data, details_data)

    @staticmethod
    def _create_operations(groups: list[OperationGroup], declaration_year: int | None) -> list[Operation]:
        # Fetch emission rates for all lots across all groups in a single query rather than one query per group.
        all_lot_ids = [lot_id for group in groups for lot_id in group.lot_volumes]
        emissions_by_lot = OperationService.get_emission_rates_by_lot(all_lot_ids)

        with transaction.atomic():
            return [
                OperationExcelImportService._create_operation_for_group(group, declaration_year, emissions_by_lot)
                for group in groups
            ]

    @staticmethod
    def _group_to_dict(group: OperationGroup, operation: Operation | None = None) -> dict:
        return {
            "operation_id": operation.id if operation else None,
            "status": operation.status if operation else _default_status(group.operation_type),
            "type": group.operation_type,
            "sector": group.sector,
            "customs_category": group.customs_category,
            "biofuel": group.biofuel_code,
            "debited_entity": {"id": group.debited_entity.id, "name": group.debited_entity.name},
            "credited_entity": (
                {"id": group.credited_entity.id, "name": group.credited_entity.name} if group.credited_entity else None
            ),
            "lot_count": len(group.lot_volumes),
            "total_volume": round(sum(group.lot_volumes.values()), 4),
            "rows": group.row_numbers,
        }

    @staticmethod
    def _map_operations_by_group_key(operations: list[Operation]) -> dict[tuple, Operation]:
        return {(op.type, op.customs_category, op.biofuel_id, op.credited_entity_id): op for op in operations}

    @staticmethod
    def _build_groups_data(groups: list[OperationGroup], operations: list[Operation] | None) -> list[dict]:
        operation_by_key = OperationExcelImportService._map_operations_by_group_key(operations) if operations else {}

        groups_data = []
        for group in groups:
            key = (
                group.operation_type,
                group.customs_category,
                group.biofuel_id,
                group.credited_entity.id if group.credited_entity else None,
            )
            groups_data.append(OperationExcelImportService._group_to_dict(group, operation_by_key.get(key)))

        return groups_data

    @staticmethod
    def execute(file, mode: str, debited_entity: Entity) -> dict:
        data = OperationExcelImportService._parse_rows(file)

        row_serializer = OperationExcelRowSerializer(
            data=data, many=True, context=OperationExcelImportService._build_lookup_caches(data)
        )
        ExcelImporter.validate_retrieved_data(row_serializer, EXCEL_IMPORT_CONFIG, len(data))

        groups = OperationExcelImportService._build_groups(row_serializer.validated_data, debited_entity)
        declaration_year = DeclarationPeriodService.get_current_declaration_year()
        OperationExcelImportService._validate_groups(groups, len(data), declaration_year)

        operations = OperationExcelImportService._create_operations(groups, declaration_year) if mode == "create" else None
        groups_data = OperationExcelImportService._build_groups_data(groups, operations)

        return OperationImportResponseSerializer({"mode": mode, "operations": groups_data}).data
