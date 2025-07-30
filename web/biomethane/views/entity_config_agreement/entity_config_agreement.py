from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneEntityConfigAgreement
from biomethane.serializers.entity_config_agreement import BiomethaneEntityConfigAgreementSerializer
from core.models import Entity, UserRights
from core.permissions import HasUserRights


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
class BiomethaneEntityConfigAgreementViewSet(ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = BiomethaneEntityConfigAgreementSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    # permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch"]

    def get_permissions(self):
        if self.action in [
            "create",
        ]:
            return [IsAuthenticated(), HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return super().get_permissions()

    def get_queryset(self):
        queryset = BiomethaneEntityConfigAgreement.objects.all()

        return queryset.filter(entity=self.request.entity).prefetch_related("amendments")

    def list(self, request, *args, **kwargs):
        try:
            agreement = BiomethaneEntityConfigAgreement.objects.get(entity=request.entity)
            data = BiomethaneEntityConfigAgreementSerializer(agreement).data
            return Response(data)
        except BiomethaneEntityConfigAgreement.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
