from django.db.models import Sum
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from core.pagination import MetadataPageNumberPagination
from elec.filters.transfer_certificates import TransferCertificateFilter
from elec.models import ElecTransferCertificate
from elec.permissions import HasCpoUserRights, HasElecAdminRights
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer

from .mixins import ActionMixin


class TransferCertificatePagination(MetadataPageNumberPagination):
    aggregate_fields = {
        "transferred_energy": Sum("energy_amount"),
    }


class TransferCertificateViewSet(ActionMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[ElecTransferCertificate]):
    queryset = ElecTransferCertificate.objects.none()
    serializer_class = ElecTransferCertificateSerializer
    filterset_class = TransferCertificateFilter
    pagination_class = TransferCertificatePagination
    permission_classes = [IsAuthenticated & (HasCpoUserRights | HasElecAdminRights)]
    lookup_field = "id"
    search_fields = ["supplier__name", "client__name", "certificate_id"]

    def get_queryset(self):
        queryset = ElecTransferCertificate.objects.all()

        entity = self.request.entity
        if entity.entity_type == Entity.CPO:
            queryset = ElecTransferCertificate.objects.filter(supplier=entity)

        return queryset.select_related("supplier", "client")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
