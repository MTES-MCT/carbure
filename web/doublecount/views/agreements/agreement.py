from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.models import Entity
from doublecount.filters import AgreementFilter
from doublecount.models import DoubleCountingProduction, DoubleCountingSourcing
from doublecount.permissions import HasDoubleCountingAdminRights, HasProducerRights
from doublecount.views.agreements.mixins import ActionMixin


class AgreementViewSet(ActionMixin, GenericViewSet):
    queryset = DoubleCountingRegistration.objects.all()
    serializer_class = DoubleCountingRegistrationDetailsSerializer
    pagination_class = None
    lookup_field = "id"
    filterset_class = AgreementFilter
    permission_classes = [HasProducerRights | HasDoubleCountingAdminRights]

    def get_permissions(self):
        if self.action == "agreements_public_list":
            return [IsAuthenticated()]
        elif self.action in ["agreement_admin", "export"]:
            return [HasDoubleCountingAdminRights()]

        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        entity = self.request.entity

        if entity.entity_type == Entity.PRODUCER:
            queryset = queryset.filter(production_site__created_by=entity)

        if self.action == "retrieve":
            queryset = queryset.select_related(
                "application",
                "application__producer",
                "application__production_site__created_by",
                "application__production_site",
                "application__production_site__country",
            ).prefetch_related(
                # For application sourcing with their related data
                Prefetch(
                    "application__sourcing",
                    queryset=DoubleCountingSourcing.objects.select_related(
                        "feedstock", "origin_country", "supply_country", "transit_country"
                    ),
                ),
                # For application production with their related data
                Prefetch(
                    "application__production",
                    queryset=DoubleCountingProduction.objects.select_related("biofuel", "feedstock"),
                ),
                # For application documents
                "application__documents",
                "application__production_site__productionsiteinput_set",
                "application__production_site__productionsiteoutput_set",
            )

        return queryset.select_related(
            "production_site",
            "production_site__created_by",
        )
