from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneEntityConfigAgreement
from biomethane.serializers.entity_config_agreement.retrieve import BiomethaneEntityConfigAgreementSerializer
from biomethane.views.entity_config_agreement.mixins import BiomethaneEntityConfigAgreementMixin
from core.models import Entity, UserRights
from core.permissions import HasUserRights


class BiomethaneEntityConfigAgreementViewSet(GenericViewSet, BiomethaneEntityConfigAgreementMixin):
    queryset = BiomethaneEntityConfigAgreement.objects.none()
    serializer_class = BiomethaneEntityConfigAgreementSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]

    def get_permissions(self):
        if self.action in [
            "create_agreement",
            "patch_agreement",
        ]:
            return [IsAuthenticated(), HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return super().get_permissions()

    def get_queryset(self):
        return BiomethaneEntityConfigAgreement.objects.filter(entity=self.request.entity).prefetch_related("amendments")
