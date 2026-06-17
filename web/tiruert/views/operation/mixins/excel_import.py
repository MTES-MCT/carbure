from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.serializers.operation import OperationExcelImportRequestSerializer
from tiruert.services.operation_excel_import import OperationExcelImportService


class ExcelImportActionMixin:
    @extend_schema(
        operation_id="import_operations_from_excel",
        description="Validate or create TIRUERT operations from an Excel file",
        request=OperationExcelImportRequestSerializer,
    )
    @action(detail=False, methods=["post"], url_path="import")
    def import_operations_from_excel(self, request, *args, **kwargs):
        from core.excel_importer import ExcelValidationError

        file_serializer = OperationExcelImportRequestSerializer(data=request.data)
        if not file_serializer.is_valid():
            return Response(file_serializer.errors, status=400)

        file = file_serializer.validated_data["file"]
        mode = file_serializer.validated_data["mode"]
        entity_id = request.entity.id

        try:
            result = OperationExcelImportService.execute(file, mode, entity_id)
        except ExcelValidationError as e:
            return Response(
                {
                    "validation_errors": e.validation_errors,
                    "total_errors": len(e.validation_errors),
                    "total_rows_processed": e.total_rows_processed,
                },
                status=400,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response(result, status=status.HTTP_200_OK)
