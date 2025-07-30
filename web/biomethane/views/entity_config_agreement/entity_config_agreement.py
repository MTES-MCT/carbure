from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneEntityConfigAgreement
from biomethane.serializers.entity_config_agreement.add import BiomethaneEntityConfigAgreementAddSerializer
from biomethane.serializers.entity_config_agreement.list import BiomethaneEntityConfigAgreementSerializer
from biomethane.views.entity_config_agreement.mixins import BiomethaneEntityConfigAgreementMixin
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
class BiomethaneEntityConfigAgreementViewSet(
    ListModelMixin, CreateModelMixin, GenericViewSet, BiomethaneEntityConfigAgreementMixin
):
    queryset = BiomethaneEntityConfigAgreement.objects.none()
    serializer_class = BiomethaneEntityConfigAgreementSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    http_method_names = ["get", "post", "patch"]

    def get_permissions(self):
        if self.action in [
            "create",
        ]:
            return [IsAuthenticated(), HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return super().get_permissions()

    def get_queryset(self):
        return BiomethaneEntityConfigAgreement.objects.filter(entity=self.request.entity).prefetch_related("amendments")

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneEntityConfigAgreementAddSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        try:
            agreement = BiomethaneEntityConfigAgreement.objects.get(entity=request.entity)
            data = BiomethaneEntityConfigAgreementSerializer(agreement).data
            return Response(data)
        except BiomethaneEntityConfigAgreement.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        operation_id="create_biomethane_entity_config_agreement",
        description="Create a new agreement.",
        request=BiomethaneEntityConfigAgreementAddSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneEntityConfigAgreementAddSerializer, description="The newly created agreement."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid input data."),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = BiomethaneEntityConfigAgreementAddSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        validated_data["entity"] = request.entity

        BiomethaneEntityConfigAgreement.objects.create(**validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
