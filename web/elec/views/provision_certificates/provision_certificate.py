from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from core.utils import CustomPageNumberPagination
from elec.filters.provision_certificates import ProvisionCertificateFilter
from elec.models import ElecProvisionCertificate
from elec.permissions import HasCpoRights, HasCpoWriteRights, HasElecAdminRights
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer

from .mixins import ActionMixin


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
class ProvisionCertificateViewSet(ActionMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[ElecProvisionCertificate]):
    queryset = ElecProvisionCertificate.objects.all()
    serializer_class = ElecProvisionCertificateSerializer
    filterset_class = ProvisionCertificateFilter
    pagination_class = CustomPageNumberPagination
    permission_classes = [HasCpoRights | HasElecAdminRights]
    lookup_field = "id"
    search_fields = ["cpo__name", "operating_unit"]

    def get_permissions(self):
        if self.action == "transfer":
            return [HasCpoWriteRights()]
        if self.action == "import_certificates":
            return [HasElecAdminRights()]

        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()

        entity = self.request.entity
        if entity.entity_type == Entity.CPO:
            queryset = ElecProvisionCertificate.objects.filter(cpo=entity)

        return queryset.select_related("cpo").order_by("id")
