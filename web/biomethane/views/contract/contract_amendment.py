from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import GenericViewSet, mixins

from biomethane.filters import BiomethaneContractAmendmentFilter
from biomethane.models import BiomethaneContractAmendment
from biomethane.serializers import BiomethaneContractAmendmentAddSerializer, BiomethaneContractAmendmentSerializer
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
class BiomethaneContractAmendmentViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = BiomethaneContractAmendment.objects.all()
    serializer_class = BiomethaneContractAmendmentSerializer
    permission_classes = [HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    filterset_class = BiomethaneContractAmendmentFilter

    def get_permissions(self):
        if self.action in [
            "create",
        ]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneContractAmendmentAddSerializer
        return BiomethaneContractAmendmentSerializer
