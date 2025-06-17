# pyright: strict

from django.db.models import Sum
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from web.core.pagination import MetadataPageNumberPagination

from core.models import Entity, ExternalAdminRights
from core.permissions import AdminRightsFactory, UserRightsFactory
from elec.filters.provision_certificates import ProvisionCertificateFilter
from elec.models import ElecProvisionCertificate
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer

from .mixins import ActionMixin

HasCpoUserRights = UserRightsFactory(entity_type=[Entity.CPO])
HasElecAdminRights = AdminRightsFactory(allow_external=[ExternalAdminRights.ELEC])


class ProvisionCertificatePagination(MetadataPageNumberPagination):
    aggregate_fields = {
        "available_energy": Sum("remaining_energy_amount"),
    }


class ProvisionCertificateViewSet(ActionMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[ElecProvisionCertificate]):
    queryset = ElecProvisionCertificate.objects.none()
    serializer_class = ElecProvisionCertificateSerializer
    filterset_class = ProvisionCertificateFilter
    pagination_class = ProvisionCertificatePagination
    lookup_field = "id"

    permission_classes = [IsAuthenticated & (HasCpoUserRights | HasElecAdminRights)]

    def get_queryset(self):
        queryset = ElecProvisionCertificate.objects.all()

        entity = self.request.entity
        if entity.entity_type == Entity.CPO:
            queryset = ElecProvisionCertificate.objects.filter(cpo=entity)

        return queryset.select_related("cpo")
