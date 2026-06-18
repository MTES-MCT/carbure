from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.excel_importer import ExcelImporter, ExcelValidationError
from core.models import CarbureLot, Entity
from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.models import Operation
from tiruert.services.declaration_period import DeclarationPeriodService
from tiruert.services.operation import OperationService
from tiruert.services.operation_excel_template import get_tiruert_operator_queryset


class OperationExcelImportErrors:
    INVALID_OPERATION_TYPE = "INVALID_OPERATION_TYPE"
    INVALID_VOLUME = "INVALID_VOLUME"
    MISSING_CREDITED_ENTITY = "MISSING_CREDITED_ENTITY"


def _get_sector(biofuel) -> str:
    if biofuel.compatible_essence:
        return Operation.ESSENCE
    elif biofuel.compatible_diesel:
        return Operation.GAZOLE
    elif biofuel.code in SAF_BIOFUEL_TYPES:
        return Operation.CARBUREACTEUR
    return ""


@dataclass
class OperationGroup:
    operation_type: str
    customs_category: str
    biofuel_id: int
    biofuel_code: str
    sector: str
    credited_entity: Entity | None
    debited_entity: Entity
    row_numbers: list[int]
    lot_volumes: dict[int, float]


class OperationExcelRowSerializer(serializers.Serializer):
    lot_id = serializers.PrimaryKeyRelatedField(
        queryset=CarbureLot.objects.select_related("biofuel", "feedstock", "carbure_client", "carbure_supplier")
    )
    volume = serializers.FloatField()
    operation_type = serializers.CharField()
    credited_entity = serializers.PrimaryKeyRelatedField(
        queryset=get_tiruert_operator_queryset(), required=False, allow_null=True
    )

    def validate_volume(self, value):
        if value <= 0:
            raise serializers.ValidationError(_("La valeur du volume doit être supérieure à zéro."))
        return value

    def validate_operation_type(self, value):
        normalized = str(value or "").strip().upper()
        if normalized not in [Operation.TRANSFERT, Operation.TENEUR]:
            raise serializers.ValidationError(_("Le type d'opération doit être 'TRANSFERT' ou 'TENEUR'."))
        return normalized

    def validate(self, attrs):
        if attrs.get("operation_type") == Operation.TRANSFERT and not attrs.get("credited_entity"):
            raise serializers.ValidationError(
                {"credited_entity": _("Destinataire requis pour les opérations de type TRANSFERT.")}
            )
        return attrs


class OperationExcelImportService:
    @staticmethod
    def _build_groups(validated_rows: list[dict], total_rows: int, debited_entity: Entity) -> list[OperationGroup]:
        grouped: dict[tuple, list[dict]] = defaultdict(list)

        # Group rows by operation_type, customs_category, biofuel_id, and credited_entity_id
        for row_number, row in enumerate(validated_rows, start=3):
            lot = row["lot_id"]
            credited_entity = row["credited_entity"]
            key = (
                row["operation_type"],
                lot.feedstock.category,
                lot.biofuel_id,
                credited_entity.id if credited_entity else None,
            )
            grouped[key].append({"row_number": row_number, **row})

        groups = []
        for key, rows in grouped.items():
            operation_type, customs_category, biofuel_id, _ = key
            first_row = rows[0]
            first_lot = first_row["lot_id"]
            lot_volumes: dict[int, float] = defaultdict(float)
            row_numbers = []

            # If there are multiple rows for the same lot id, sum their volumes and keep track of row numbers
            for row in rows:
                lot_volumes[row["lot_id"].id] += row["volume"]
                row_numbers.append(row["row_number"])

            groups.append(
                OperationGroup(
                    operation_type=operation_type,
                    customs_category=customs_category,
                    biofuel_id=biofuel_id,
                    biofuel_code=first_lot.biofuel.code,
                    sector=_get_sector(first_lot.biofuel),
                    credited_entity=first_row["credited_entity"],
                    debited_entity=debited_entity,
                    row_numbers=row_numbers,
                    lot_volumes=dict(lot_volumes),
                )
            )

        return groups

    @staticmethod
    def _validate_groups(groups: list[OperationGroup], total_rows: int) -> None:
        first_lot_ids = [list(group.lot_volumes.keys())[0] for group in groups if group.lot_volumes]
        lot_biofuels = {
            lot.id: lot.biofuel for lot in CarbureLot.objects.filter(id__in=first_lot_ids).select_related("biofuel")
        }

        errors = []
        for group in groups:
            first_lot_id = list(group.lot_volumes.keys())[0]
            biofuel = lot_biofuels.get(first_lot_id)
            if biofuel is None:
                continue

            selected_lots = [{"id": lot_id, "volume": volume} for lot_id, volume in group.lot_volumes.items()]
            data = {
                "debited_entity": group.debited_entity,
                "biofuel": biofuel,
                "customs_category": group.customs_category,
                "type": group.operation_type,
            }

            try:
                OperationService.check_volumes(selected_lots, data, "l")
            except serializers.ValidationError as exc:
                for row_number in group.row_numbers:
                    errors.append({"row": row_number, "errors": exc.detail})

        if errors:
            raise ExcelValidationError(errors, total_rows)

    @staticmethod
    def _serialize_group(group: OperationGroup, operation: Operation | None = None) -> dict:
        return {
            "operation_id": operation.id if operation else None,
            "status": operation.status if operation else Operation.DRAFT,
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
    def _create_operations(groups: list[OperationGroup]) -> list[Operation]:
        created_operations = []
        year = DeclarationPeriodService.get_current_declaration_year()
        with transaction.atomic():
            for group in groups:
                operation_data = {
                    "type": group.operation_type,
                    "status": Operation.DRAFT,
                    "customs_category": group.customs_category,
                    "biofuel_id": group.biofuel_id,
                    "credited_entity": group.credited_entity,
                    "debited_entity": group.debited_entity,
                    "renewable_energy_share": 1,
                    "declaration_year": year,
                }

                lots = CarbureLot.objects.filter(id__in=group.lot_volumes.keys()).values("id", "ghg_total")
                ghg_by_lot = {lot["id"]: lot["ghg_total"] for lot in lots}

                details_data = OperationService.build_details_data(group.lot_volumes, ghg_by_lot)

                operation = OperationService.create_operation_with_details(operation_data, details_data)
                created_operations.append(operation)

        return created_operations

    @staticmethod
    def execute(file, mode: str, debited_entity_id: int) -> dict:
        config = {"header_row": 1}

        data = ExcelImporter.parse(file, **config)
        for row in data:
            row.pop("credited_entity_name", None)

        row_serializer = OperationExcelRowSerializer(data=data, many=True)
        ExcelImporter.validate_retrieved_data(row_serializer, config, len(data))

        debited_entity = Entity.objects.filter(id=debited_entity_id).first()
        if debited_entity is None:
            raise serializers.ValidationError({"entity_id": "Invalid entity_id"})

        groups = OperationExcelImportService._build_groups(row_serializer.validated_data, len(data), debited_entity)
        OperationExcelImportService._validate_groups(groups, len(data))

        if mode == "create":
            operations = OperationExcelImportService._create_operations(groups)
            operation_by_key = {
                (op.type, op.customs_category, op.biofuel_id, op.credited_entity_id): op for op in operations
            }

            result = []
            for group in groups:
                key = (
                    group.operation_type,
                    group.customs_category,
                    group.biofuel_id,
                    group.credited_entity.id if group.credited_entity else None,
                )
                result.append(OperationExcelImportService._serialize_group(group, operation_by_key.get(key)))

            return {"mode": mode, "operations": result}

        return {
            "mode": mode,
            "operations": [OperationExcelImportService._serialize_group(group) for group in groups],
        }
