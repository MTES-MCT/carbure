from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from biomethane.filters.provider_declaration import BiomethaneProviderDeclarationFilter
from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.permissions import CanAccessProviderApi
from biomethane.serializers.provider.declaration import BiomethaneProviderDeclarationSerializer
from biomethane.services.provider_declaration import get_provider_declarations


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Gas provider entity ID.",
            required=True,
        ),
    ]
)
class BiomethaneProviderDeclarationViewSet(GenericViewSet, ListModelMixin):
    """Validated annual declarations of the producers under contract with the gas provider."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [CanAccessProviderApi]
    serializer_class = BiomethaneProviderDeclarationSerializer
    filterset_class = BiomethaneProviderDeclarationFilter
    queryset = BiomethaneAnnualDeclaration.objects.none()

    def get_queryset(self):
        return get_provider_declarations(self.request.entity)
