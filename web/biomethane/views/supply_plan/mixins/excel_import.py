from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.serializers import BiomethaneSupplyInputCreateSerializer, BiomethaneUploadExcelSerializer
from core.excel_importer import ExcelImporter


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

        try:
            config = {
                "header_row": 1,
                "sheet_name": "Plan d'approvisionnement",
            }
            data = ExcelImporter.parse(file, **config)

            # Collect all validation errors by row
            validation_errors = []
            valid_instances = []

            for row_index, row in enumerate(data, start=1):
                input_serializer = BiomethaneSupplyInputCreateSerializer(data=row)

                if input_serializer.is_valid():
                    valid_instances.append(input_serializer)
                else:
                    # Add row number to errors
                    excel_row_number = row_index + config["header_row"] + 1
                    validation_errors.append(
                        {
                            "row": excel_row_number,
                            "errors": input_serializer.errors,
                        }
                    )

            # If there are validation errors, return them all
            if validation_errors:
                return Response(
                    {
                        "validation_errors": validation_errors,
                        "total_errors": len(validation_errors),
                        "total_rows_processed": len(data),
                    },
                    status=400,
                )

            # If all validations passed, save all instances
            for serializer in valid_instances:
                serializer.save()

        except Exception as e:
            return Response({"file": str(e)}, status=400)

        return Response({"rows_imported": len(data)}, status=201)
