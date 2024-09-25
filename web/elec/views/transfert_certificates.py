from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.excel import ExcelResponse
from elec.api.admin.transfer_certificates.transfer_certificates import (
    export_transfer_certificate_to_excel,
)
from elec.filters import TransfertCertificateFilter
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import (
    ElecTransferCertificateDetailsSerializer,
    ElecTransferCertificateSerializer,
)


class ActionMixin:
    @action(methods=["get"], detail=False)
    def export(self, request, *args, **kwargs):
        transfer_certificates = self.filter_queryset(self.get_queryset())
        file = export_transfer_certificate_to_excel(transfer_certificates)
        return ExcelResponse(file)

    @action(methods=["get"], detail=False)
    def filters(self, request, *args, **kwargs):
        query_params = request.GET.copy()
        filter = request.query_params.get("filter")
        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset())
        queryset = filterset.qs

        filters = {
            "year": "transfer_date__year",
            "transfer_date": "transfer_date",
            "cpo": "supplier__name",
            "operator": "client__name",
            "certificate_id": "certificate_id",
        }

        column = filters.get(filter)

        if not column:
            raise Exception(f"Filter '{filter}' does not exist for tickets")

        remaining_filter_values = queryset.values_list(column, flat=True).distinct()

        return Response(list(remaining_filter_values), status=status.HTTP_200_OK)


class TransfertCertificateViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, ActionMixin):
    serializer_class = ElecTransferCertificateSerializer
    queryset = ElecTransferCertificate.objects.select_related("supplier", "client")
    filterset_class = TransfertCertificateFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ElecTransferCertificateDetailsSerializer
        return super().get_serializer_class()
