from django.db.models import Prefetch
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.models import Entity
from core.permissions import HasAdminRights, HasUserRights
from doublecount.filters import AgreementFilter
from doublecount.models import DoubleCountingProduction, DoubleCountingSourcing
from doublecount.views.agreements.mixins import ActionMixin


class AgreementViewSet(ActionMixin, GenericViewSet):
    queryset = applications = DoubleCountingRegistration.objects.all()
    serializer_class = DoubleCountingRegistrationDetailsSerializer
    pagination_class = None
    lookup_field = "id"
    filterset_class = AgreementFilter
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.PRODUCER, Entity.ADMIN]),
    )

    def get_queryset(self):
        queryset = super().get_queryset()

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

    def get_permissions(self):
        # TODO fix permissions if needed
        if self.action == "list":
            return [IsAuthenticated(), HasUserRights(None, [Entity.PRODUCER, Entity.ADMIN])]
        if self.action == "agreements_public_list":
            return [AllowAny()]
        if self.action in ["agreements_admin", "export"]:
            return [HasAdminRights()]

        return super().get_permissions()
