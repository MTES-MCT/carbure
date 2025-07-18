from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_simplejwt.authentication import JWTAuthentication

from elec.filters import ProvisionCertificateQualichargeFilter
from elec.models import ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import ElecProvisionCertificateQualichargeSerializer

from .mixins import BulkCreateMixin, BulkUpdateMixin


class ElecProvisionCertificateQualichargeViewSet(
    mixins.ListModelMixin, BulkCreateMixin, BulkUpdateMixin, viewsets.GenericViewSet
):
    queryset = ElecProvisionCertificateQualicharge.objects.all()
    serializer_class = ElecProvisionCertificateQualichargeSerializer
    filterset_class = ProvisionCertificateQualichargeFilter
    http_method_names = ["get", "post"]

    def initialize_request(self, request, *args, **kwargs):
        if request.method == "POST" and request.path.endswith("bulk-create/"):  # Not found better way to check this
            self.authentication_classes = [JWTAuthentication]
            self.permission_classes = [HasAPIKey & IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().initialize_request(request, *args, **kwargs)
