from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneInjectionSite
from biomethane.serializers import BiomethaneInjectionSiteInputSerializer, BiomethaneInjectionSiteSerializer
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
class BiomethaneInjectionSiteViewSet(GenericViewSet):
    queryset = BiomethaneInjectionSite.objects.all()
    serializer_class = BiomethaneInjectionSiteSerializer
    permission_classes = [HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_permissions(self):
        if self.action in [
            "upsert",
        ]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "upsert":
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
            injection_site = BiomethaneInjectionSite.objects.get(producer=request.entity)
            data = self.get_serializer(injection_site, many=False).data
            return Response(data)
        except BiomethaneInjectionSite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneInjectionSiteSerializer,
                description="Injection site updated successfully",
            ),
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneInjectionSiteSerializer,
                description="Injection site created successfully",
            ),
        },
        request=BiomethaneInjectionSiteInputSerializer,
        description="Create or update the injection site for the current entity (upsert operation).",
    )
    def upsert(self, request, *args, **kwargs):
        """Create or update injection site using upsert logic."""
        try:
            injection_site = BiomethaneInjectionSite.objects.get(producer=request.entity)
            serializer = self.get_serializer(injection_site, data=request.data, partial=True)
            status_code = status.HTTP_200_OK
        except BiomethaneInjectionSite.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            status_code = status.HTTP_201_CREATED

        if serializer.is_valid():
            injection_site = serializer.save()
            return Response(status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
