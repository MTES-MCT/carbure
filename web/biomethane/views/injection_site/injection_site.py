from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

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
    mixins.CreateModelMixin,
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
        if self.action in ["create", "injection_site_put"]:
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

    def update(self, request, *args, **kwargs):
        try:
            injection_site = BiomethaneInjectionSite.objects.get(entity=request.entity)
            serializer = self.get_serializer(injection_site, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneInjectionSite.DoesNotExist:
            return Response({"detail": "Aucun site d'injection trouvé pour cette entité"}, status=status.HTTP_404_NOT_FOUND)
