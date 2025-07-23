from datetime import date

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from core.models import Entity
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer


class ExcelExportActionMixin:
    @extend_schema(
        request=None,
        responses={200: {"type": "string", "format": "binary", "description": "Excel file download"}},
        operation_id="export_transfer_certificates_excel",
    )
    @action(detail=False, methods=["GET"], url_path="export")
    def export_to_excel(self, request, *args, **kwargs):
        transfers = self.filter_queryset(self.get_queryset())

        today = date.today()
        file = "carbure_elec_transfer_certificate_%s.xlsx" % (today.strftime("%Y%m%d_%H%M"))

        columns = [
            {"label": "certificate_id", "value": "certificate_id"},
            {"label": "status", "value": "status"},
            {"label": "supplier", "value": "supplier.name"},
            {"label": "client", "value": "client.name"},
            {"label": "transfer_date", "value": "transfer_date"},
            {"label": "energy_amount", "value": "energy_amount"},
        ]

        if request.entity.entity_type != Entity.CPO:
            columns.insert(5, {"label": "consumption_date", "value": "consumption_date"})

        excel_file = export_to_excel(
            file,
            [
                {
                    "label": "tickets",
                    "rows": ElecTransferCertificateSerializer(transfers, many=True).data,
                    "columns": columns,
                }
            ],
        )

        return ExcelResponse(excel_file)
