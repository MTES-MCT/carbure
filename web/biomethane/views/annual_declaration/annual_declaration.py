from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters import BiomethaneAnnualDeclarationFilter
from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers import BiomethaneAnnualDeclarationSerializer
from biomethane.utils import get_declaration_period
from biomethane.views.mixins import YearsActionMixin

from .mixins import ValidateActionMixin


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
class BiomethaneAnnualDeclarationViewSet(GenericViewSet, ValidateActionMixin, YearsActionMixin):
    queryset = BiomethaneAnnualDeclaration.objects.all()
    serializer_class = BiomethaneAnnualDeclarationSerializer
    filterset_class = BiomethaneAnnualDeclarationFilter
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["partial_update", "validate_annual_declaration"], self.action)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_queryset(self):
        if self.action == "get_years":
            return super().get_queryset()

        year = get_declaration_period()
        return self.queryset.filter(year=year)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneAnnualDeclarationSerializer,
                description="Declaration details for the entity",
            ),
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneAnnualDeclarationSerializer,
                description="Declaration created for the entity",
            ),
        },
        description="Retrieve the declaration. Returns a single declaration object.",
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve the declaration for the current entity and current period or create it if it does not exist."""
        try:
            declaration = self.filter_queryset(self.get_queryset()).get()
            status_code = status.HTTP_200_OK
        except BiomethaneAnnualDeclaration.DoesNotExist:
            serializer = self.get_serializer(data={})
            serializer.is_valid(raise_exception=True)
            declaration = serializer.save()
            status_code = status.HTTP_201_CREATED

        data = self.get_serializer(declaration, many=False).data
        return Response(data, status=status_code)

    def partial_update(self, request, *args, **kwargs):
        try:
            declaration = self.filter_queryset(self.get_queryset()).get()
            serializer = self.get_serializer(declaration, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except BiomethaneAnnualDeclaration.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
