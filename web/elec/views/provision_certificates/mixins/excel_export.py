from datetime import date

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer


class ExcelExportActionMixin:
    @extend_schema(
        request=None,
        responses={200: {"type": "string", "format": "binary", "description": "Excel file download"}},
        operation_id="export_provision_certificates_excel",
    )
    @action(detail=False, methods=["GET"], url_path="export")
    def export_to_excel(self, request, *args, **kwargs):
        provisions = self.filter_queryset(self.get_queryset())

        today = date.today()
        file = "carbure_elec_provision_certificate_%s.xlsx" % (today.strftime("%Y%m%d_%H%M"))

        excel_file = export_to_excel(
            file,
            [
                {
                    "label": "tickets",
                    "rows": ElecProvisionCertificateSerializer(provisions, many=True).data,
                    "columns": [
                        {"label": "id", "value": "id"},
                        {"label": "quarter", "value": "quarter"},
                        {"label": "year", "value": "year"},
                        {"label": "cpo", "value": "cpo.name"},
                        {"label": "operating_unit", "value": "operating_unit"},
                        {"label": "source", "value": "source"},
                        {"label": "energy_amount", "value": "energy_amount"},
                        {"label": "remaining_energy_amount", "value": "remaining_energy_amount"},
                    ],
                }
            ],
        )

        return ExcelResponse(excel_file)
