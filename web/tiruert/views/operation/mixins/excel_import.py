from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.excel import ExcelResponse
from tiruert.serializers.operation import OperationExcelImportRequestSerializer, OperationImportResponseSerializer
from tiruert.services.declaration_period import DeclarationPeriodService
from tiruert.services.operation_excel_import import OperationExcelImportService
from tiruert.services.operation_excel_template import create_operation_import_template


class ExcelImportActionMixin:
    @extend_schema(
        operation_id="download_operations_import_template",
        description="Download the TIRUERT operation import template",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="Fichier Excel généré",
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="import/template")
    def download_import_template(self, request, *args, **kwargs):
        file = create_operation_import_template(request.entity.id)
        return ExcelResponse(file)

    @extend_schema(
        operation_id="import_operations_from_excel",
        description="Validate or create TIRUERT operations from an Excel file",
        request=OperationExcelImportRequestSerializer,
        responses=OperationImportResponseSerializer,
    )
    @action(detail=False, methods=["post"], url_path="import")
    def import_operations_from_excel(self, request, *args, **kwargs):
        from core.excel_importer import ExcelValidationError

        if not DeclarationPeriodService.get_current_declaration_year():
            return Response(
                {"error": "La période de déclaration n'est pas ouverte."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_serializer = OperationExcelImportRequestSerializer(data=request.data)
        if not file_serializer.is_valid():
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = file_serializer.validated_data["file"]
        mode = file_serializer.validated_data["mode"]
        entity = request.entity

        try:
            result = OperationExcelImportService.execute(file, mode, entity)
        except ExcelValidationError as e:
            return Response(
                {
                    "validation_errors": e.validation_errors,
                    "total_errors": len(e.validation_errors),
                    "total_rows_processed": e.total_rows_processed,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)
