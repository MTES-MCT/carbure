from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import GenericViewSet, mixins

from biomethane.filters import BiomethaneContractAmendmentFilter
from biomethane.models import BiomethaneContractAmendment
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers import BiomethaneContractAmendmentAddSerializer, BiomethaneContractAmendmentSerializer


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
    queryset = BiomethaneContractAmendment.objects.all().order_by("pk")
    serializer_class = BiomethaneContractAmendmentSerializer
    filterset_class = BiomethaneContractAmendmentFilter

    def get_permissions(self):
        return get_biomethane_permissions(["create"], self.action)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneContractAmendmentAddSerializer
        return BiomethaneContractAmendmentSerializer
