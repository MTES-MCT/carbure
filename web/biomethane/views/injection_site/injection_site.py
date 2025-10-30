from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.mixins import EntityProducerFilter
from biomethane.models import BiomethaneInjectionSite
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers import BiomethaneInjectionSiteInputSerializer, BiomethaneInjectionSiteSerializer
from biomethane.views.mixins.retrieve import RetrieveSingleObjectMixin


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
class BiomethaneInjectionSiteViewSet(RetrieveSingleObjectMixin, GenericViewSet):
    queryset = BiomethaneInjectionSite.objects.all()
    serializer_class = BiomethaneInjectionSiteSerializer
    filterset_class = EntityProducerFilter
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert"], self.action)

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
