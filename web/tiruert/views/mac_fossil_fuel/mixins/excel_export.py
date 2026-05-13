import time

import openpyxl
from django.db.models import Sum
from django.http import HttpResponse
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from openpyxl.utils import get_column_letter
from rest_framework.decorators import action


class ExcelExportActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Authorised entity ID.",
                required=True,
            ),
            OpenApiParameter(
                name="year",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Filter RFCs by year",
                required=True,
            ),
        ],
        examples=[
            OpenApiExample(
                "Example of export response.",
                value="mac_export.xlsx",
                request_only=False,
                response_only=True,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        ],
        responses={
            (200, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"): OpenApiTypes.STR,
        },
    )
    @action(detail=False, methods=["get"], url_path="export")
    def export_macfossilfuel_to_excel(self, request, *args, **kwargs):
        macs = self.filter_queryset(self.get_queryset())

        aggregated_macs = (
            macs.values(
                "operator__registration_id",
                "operator__name",
                "fuel__nomenclature",
                "year",
            )
            .annotate(volume=Sum("volume"))
            .order_by("year", "operator__name", "fuel__nomenclature")
        )

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "MAC Fossil Fuel Export"

        headers = [
            "SIREN",
            "Opérateur",
            "Carburant",
            "Volume (L)",
            "Année",
        ]
        for col_num, header in enumerate(headers, 1):
            sheet.cell(row=1, column=col_num, value=header)

        for row_num, mac in enumerate(aggregated_macs, 2):
            sheet.cell(row=row_num, column=1, value=mac["operator__registration_id"] or "")
            sheet.cell(row=row_num, column=2, value=mac["operator__name"] or "")
            sheet.cell(row=row_num, column=3, value=mac["fuel__nomenclature"] or "")
            sheet.cell(row=row_num, column=4, value=mac["volume"])
            sheet.cell(row=row_num, column=5, value=mac["year"])

        for col_num in range(1, len(headers) + 1):
            sheet.column_dimensions[get_column_letter(col_num)].width = 20

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        filename = f"mac_{request.entity}_{time.strftime('%Y-%m-%d_%H%M%S')}.xlsx"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        workbook.save(response)
        return response
