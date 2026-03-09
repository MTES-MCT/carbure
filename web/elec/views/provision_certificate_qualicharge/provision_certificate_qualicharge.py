from drf_spectacular.utils import OpenApiParameter, PolymorphicProxySerializer, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Entity
from core.pagination import MetadataPageNumberPagination
from elec.filters import ProvisionCertificateQualichargeFilter
from elec.models import ElecProvisionCertificateQualicharge
from elec.permissions import HasCpoRights, HasElecAdminRights
from elec.serializers.elec_provision_certificate_qualicharge import (
    ElecProvisionCertificateQualichargeGroupedSerializer,
    ElecProvisionCertificateQualichargeSerializer,
)

from .mixins import ActionMixin


class ElecProvisionCertificateQualichargePagination(MetadataPageNumberPagination):
    aggregate_fields = {"total_quantity": 0, "total_quantity_renewable": 0}

    def get_extra_metadata(self):
        metadata = {"total_quantity": 0, "total_quantity_renewable": 0}

        for qualichargeData in self.queryset:
            # Handle both model instances and dict
            if isinstance(qualichargeData, dict):
                renewable_energy = qualichargeData.get("renewable_energy", 0)
                energy = qualichargeData.get("energy_amount", 0)
            else:
                renewable_energy = qualichargeData.renewable_energy
                energy = qualichargeData.energy_amount

            metadata["total_quantity"] += energy
            metadata["total_quantity_renewable"] += renewable_energy
        return metadata


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
@extend_schema_view(
    list=extend_schema(
        responses={
            status.HTTP_200_OK: PolymorphicProxySerializer(
                many=True,
                component_name="ElecProvisionCertificateQualichargeResponse",
                serializers=[
                    ElecProvisionCertificateQualichargeGroupedSerializer,
                    ElecProvisionCertificateQualichargeSerializer,
                ],
                resource_type_field_name=None,
            )
        },
    )
)
class ElecProvisionCertificateQualichargeViewSet(ListModelMixin, RetrieveModelMixin, ActionMixin, GenericViewSet):
    queryset = ElecProvisionCertificateQualicharge.objects.all()
    serializer_class = ElecProvisionCertificateQualichargeSerializer
    filterset_class = ProvisionCertificateQualichargeFilter
    http_method_names = ["get", "post"]
    pagination_class = ElecProvisionCertificateQualichargePagination

    def get_serializer_class(self):
        if "group_by" in self.request.query_params:
            return ElecProvisionCertificateQualichargeGroupedSerializer
        return self.serializer_class

    def paginate_queryset(self, queryset):
        if "group_by" in self.request.query_params:
            return None
        return super().paginate_queryset(queryset)

    def initialize_request(self, request, *args, **kwargs):
        if request.method == "POST" and request.path.endswith("bulk-create/"):  # Not found better way to check this
            self.authentication_classes = [JWTAuthentication]
            self.permission_classes = [HasAPIKey & IsAuthenticated]
        else:
            self.permission_classes = [HasCpoRights | HasElecAdminRights]

        return super().initialize_request(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        entity = self.request.entity

        if entity.entity_type == Entity.CPO:
            queryset = ElecProvisionCertificateQualicharge.objects.filter(cpo=entity)

        return queryset.select_related("cpo").filter(cpo__isnull=False).order_by("id")
