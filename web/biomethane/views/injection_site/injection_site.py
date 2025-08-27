from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneInjectionSite
from biomethane.serializers import BiomethaneInjectionSiteInputSerializer, BiomethaneInjectionSiteSerializer
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
class BiomethaneInjectionSiteViewSet(
    GenericViewSet,
):
    queryset = BiomethaneInjectionSite.objects.all()
    serializer_class = BiomethaneInjectionSiteSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "injection_site_put":
            return BiomethaneInjectionSiteInputSerializer
        return BiomethaneInjectionSiteSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneInjectionSiteSerializer,
                description="Injection site details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Injection site not found for this entity."),
        },
        description="Retrieve the injection site for the current entity. Returns a single object.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            injection_site = BiomethaneInjectionSite.objects.get(entity=request.entity)
            data = self.get_serializer(injection_site, many=False).data
            return Response(data)
        except BiomethaneInjectionSite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneInjectionSiteSerializer,
            ),
        },
        request=BiomethaneInjectionSiteInputSerializer,
    )
    def upsert(self, request, *args, **kwargs):
        """Create or update injection site using upsert logic."""
        serializer_context = self.get_serializer_context()
        try:
            # Try to get existing injection site
            injection_site = BiomethaneInjectionSite.objects.get(entity=request.entity)
            # Update existing injection site
            serializer = BiomethaneInjectionSiteInputSerializer(
                injection_site, data=request.data, partial=True, context=serializer_context
            )
            if serializer.is_valid():
                serializer.save()
                response_data = BiomethaneInjectionSiteSerializer(injection_site, context=serializer_context).data
                return Response(response_data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneInjectionSite.DoesNotExist:
            # Create new injection site
            serializer = BiomethaneInjectionSiteInputSerializer(data=request.data, context=serializer_context)
            if serializer.is_valid():
                injection_site = serializer.save()
                response_data = BiomethaneInjectionSiteSerializer(injection_site, context=serializer_context).data
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
