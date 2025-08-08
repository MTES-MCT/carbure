from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, mixins

from biomethane.filters import BiomethaneEntityConfigContractAmendmentFilter
from biomethane.models import BiomethaneEntityConfigAmendment
from biomethane.serializers import BiomethaneEntityConfigAmendmentAddSerializer, BiomethaneEntityConfigAmendmentSerializer
from core.models import Entity
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
class BiomethaneEntityConfigContractAmendmentViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = BiomethaneEntityConfigAmendment.objects.all()
    serializer_class = BiomethaneEntityConfigAmendmentSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    filterset_class = BiomethaneEntityConfigContractAmendmentFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneEntityConfigAmendmentAddSerializer
        return BiomethaneEntityConfigAmendmentSerializer

    def perform_create(self, serializer):
        serializer.save(contract_id=self.request.entity.id)
