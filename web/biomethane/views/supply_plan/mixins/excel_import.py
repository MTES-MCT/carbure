from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.serializers import BiomethaneSupplyInputCreateFromExcelSerializer, BiomethaneUploadExcelSerializer
from core.excel_importer import ExcelImporter, ExcelValidationError


class ExcelImportActionMixin:
    @extend_schema(
        operation_id="import_supply_plan_from_excel",
        description=("Upload and process an Excel file to create supply plan entries. "),
        request=BiomethaneUploadExcelSerializer,
        responses={201: {"type": "object"}, 400: {"type": "object"}},
        examples=[
            OpenApiExample(
                "Example of successful import response.",
                value={"rows_imported": 25},
                request_only=False,
                response_only=True,
                status_codes=[201],
            ),
            OpenApiExample(
                "Example of validation error response.",
                value={
                    "validation_errors": [
                        {"row": 3, "errors": {"volume": ["This field is required."]}},
                        {"row": 5, "errors": {"input_type": ["Invalid input type."]}},
                    ],
                    "total_errors": 2,
                    "total_rows_processed": 10,
                },
                request_only=False,
                response_only=True,
                status_codes=[400],
            ),
            OpenApiExample(
                "Example of file error response.",
                value={"file": "The file is too large (maximum 10MB)"},
                request_only=False,
                response_only=True,
                status_codes=[400],
            ),
        ],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="import",
    )
    def import_supply_plan_from_excel(self, request, *args, **kwargs):
        file_serializer = BiomethaneUploadExcelSerializer(data=request.data)
        if not file_serializer.is_valid():
            return Response(file_serializer.errors, status=400)

        file = file_serializer.validated_data["file"]

        config = {
            "header_row": 1,
            "sheet_name": "Plan d'approvisionnement",
        }

        try:
            data = ExcelImporter.parse(file, **config)

            serializer = BiomethaneSupplyInputCreateFromExcelSerializer(
                data=data, many=True, context=self.get_serializer_context()
            )

            serializer = ExcelImporter.validate_retrieved_data(
                serializer=serializer,
                config=config,
            )

            # If all validations passed, save all instances using bulk save
            serializer.save()

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
            return Response({"file": str(e)}, status=400)

        return Response({"rows_imported": len(data)}, status=201)
