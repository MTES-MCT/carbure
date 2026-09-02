from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.excel_importer import ExcelImporter, ExcelValidationError
from core.import_export_template import DATA_START_ROW, get_data_start_row
from traceability.serializers.action import ActionExcelUploadSerializer
from traceability.services.action_excel import parse_action_import_file


class ExcelImportActionMixinErrors:
    INVALID_FILE = "INVALID_FILE"
    EMPTY_FILE = "EMPTY_FILE"


class ExcelImportActionMixin:
    @extend_schema(
        operation_id="import_actions_from_excel",
        description="Create actions from an Excel import template.",
        request=ActionExcelUploadSerializer,
        responses={201: {"type": "object"}, 400: {"type": "object"}},
    )
    @action(detail=False, methods=["post"], url_path="import")
    def import_actions(self, request, *args, **kwargs):
        file_serializer = ActionExcelUploadSerializer(data=request.data)
        if not file_serializer.is_valid():
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = parse_action_import_file(file_serializer.validated_data["file"], request.handler)
        except Exception:
            return Response(
                {"error": ExcelImportActionMixinErrors.INVALID_FILE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not rows:
            return Response(
                {"error": ExcelImportActionMixinErrors.EMPTY_FILE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = request.handler.excel_import_serializer_class(
            data=rows, many=True, context=self.get_serializer_context()
        )
        try:
            serializer = ExcelImporter.validate_retrieved_data(
                serializer,
                config={"header_row": get_data_start_row(request.handler.excel_columns) - DATA_START_ROW},
                nb_rows=len(rows),
            )
        except ExcelValidationError as exc:
            return Response(
                {
                    "validation_errors": exc.validation_errors,
                    "total_errors": len(exc.validation_errors),
                    "total_rows_processed": exc.total_rows_processed,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            serializer.save()

        return Response({"rows_imported": len(rows)}, status=status.HTTP_201_CREATED)
