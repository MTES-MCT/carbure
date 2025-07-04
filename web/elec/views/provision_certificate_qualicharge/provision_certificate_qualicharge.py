from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from elec.filters.provision_certificate import ProvisionCertificateFilter
from elec.models import ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import ElecProvisionCertificateQualichargeSerializer

from .mixins import BulkCreateMixin, BulkUpdateMixin


class ElecProvisionCertificateQualichargeViewSet(
    mixins.ListModelMixin, mixins.UpdateModelMixin, BulkCreateMixin, BulkUpdateMixin, viewsets.GenericViewSet
):
    queryset = ElecProvisionCertificateQualicharge.objects.all()
    serializer_class = ElecProvisionCertificateQualichargeSerializer
    filterset_class = ProvisionCertificateFilter
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "post"]
