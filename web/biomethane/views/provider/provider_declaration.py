from django.conf import settings
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from biomethane.filters.provider_declaration import BiomethaneProviderDeclarationFilter
from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.permissions import CanAccessProviderApi, CanAccessProviderModule
from biomethane.serializers.provider.declaration import BiomethaneProviderDeclarationSerializer
from biomethane.services.provider_declaration import get_provider_declarations


@extend_schema(
    auth=[{"jwtAuth": [], "apiKeyAuth": []}, {"cookieAuth": []}],
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Gas provider entity ID.",
            required=True,
        ),
    ],
)
class BiomethaneProviderDeclarationViewSet(GenericViewSet, ListModelMixin):
    """Annual declarations (any status) of the producers under contract with the gas provider."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [CanAccessProviderApi]
    serializer_class = BiomethaneProviderDeclarationSerializer
    filterset_class = BiomethaneProviderDeclarationFilter
    search_fields = None
    queryset = BiomethaneAnnualDeclaration.objects.none()

    def initialize_request(self, request, *args, **kwargs):
        # Without API key, the call comes from the frontend (session + OTP) instead of the provider's API client
        if settings.API_KEY_CUSTOM_HEADER not in request.META:
            self.authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
            self.permission_classes = [CanAccessProviderModule]

        return super().initialize_request(request, *args, **kwargs)

    def get_queryset(self):
        return get_provider_declarations(self.request.entity)
