from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.models import Entity
from core.permissions import HasAdminRights, HasUserRights
from doublecount.filters import AgreementFilter
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
        return DoubleCountingRegistration.objects.all().select_related(
            "production_site", "production_site__created_by", "application"
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
