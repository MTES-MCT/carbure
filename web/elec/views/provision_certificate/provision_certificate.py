from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from elec.models import ElecProvisionCertificate
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer

from .mixins import BulkCreateMixin


class ElecProvisionCertificateViewSet(mixins.ListModelMixin, BulkCreateMixin, viewsets.GenericViewSet):
    queryset = ElecProvisionCertificate.objects.all()
    serializer_class = ElecProvisionCertificateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]
