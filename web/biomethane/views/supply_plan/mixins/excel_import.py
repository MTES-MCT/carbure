from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.serializers import BiomethaneSupplyInputCreateSerializer, BiomethaneUploadExcelSerializer
from core.excel_importer import ExcelImporter, ExcelValidationError


class ExcelImportActionMixin:
    # @extend_schema(
    # )
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

            valid_instances = ExcelImporter.validate_retrieved_data(
                data,
                serializer_class=BiomethaneSupplyInputCreateSerializer,
                config=config,
            )

            # If all validations passed, save all instances
            for serializer in valid_instances:
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
