from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_simplejwt.authentication import JWTAuthentication
from web.core.pagination import MetadataPageNumberPagination

from elec.filters import ProvisionCertificateQualichargeFilter
from elec.models import ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import ElecProvisionCertificateQualichargeSerializer

from .mixins import ActionMixin


class ElecProvisionCertificateQualichargePagination(MetadataPageNumberPagination):
    aggregate_fields = {"total_quantity": 0}

    def get_extra_metadata(self):
        metadata = {"total_quantity": 0}

        for qualichargeData in self.queryset:
            metadata["total_quantity"] += qualichargeData.energy_amount
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
class ElecProvisionCertificateQualichargeViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, ActionMixin, viewsets.GenericViewSet
):
    queryset = ElecProvisionCertificateQualicharge.objects.all()
    serializer_class = ElecProvisionCertificateQualichargeSerializer
    filterset_class = ProvisionCertificateQualichargeFilter
    http_method_names = ["get", "post"]
    pagination_class = ElecProvisionCertificateQualichargePagination

    def initialize_request(self, request, *args, **kwargs):
        if request.method == "POST" and request.path.endswith("bulk-create/"):  # Not found better way to check this
            self.authentication_classes = [JWTAuthentication]
            self.permission_classes = [HasAPIKey & IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().initialize_request(request, *args, **kwargs)
