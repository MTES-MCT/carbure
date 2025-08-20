from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from biomethane.filters.digestate import BiomethaneDigestateFilter
from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.serializers.digestate import (
    BiomethaneDigestateAddSerializer,
    BiomethaneDigestatePatchSerializer,
    BiomethaneDigestateSerializer,
)
from core.models import Entity
from core.permissions import HasUserRights


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class BiomethaneDigestateViewSet(ModelViewSet):
    queryset = BiomethaneDigestate.objects.all()
    serializer_class = BiomethaneDigestateSerializer
    permission_classes = [HasUserRights(entity_type=[Entity.BIOMETHANE_PRODUCER])]
    filterset_class = BiomethaneDigestateFilter
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["year"] = getattr(self.request, "year", None)
        return context

    def get_serializer_class(self):
        if self.action == "upsert":
            return BiomethaneDigestatePatchSerializer
        return BiomethaneDigestateSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "year",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Year",
                required=True,
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Digestate not found for this entity."),
        },
        description="Retrieve the digestate for the current entity and the current year. Returns a single digestate object.",
    )
    def retrieve(self, request, *args, **kwargs):
        year = request.query_params.get("year")
        try:
            digestate = BiomethaneDigestate.objects.get(producer=request.entity, year=year)
            data = self.get_serializer(digestate, many=False).data
            return Response(data)

        except BiomethaneDigestate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate updated successfully",
            ),
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate created successfully",
            ),
        },
        description="Create or update the digestate for the current entity (upsert operation).",
    )
    def upsert(self, request, *args, **kwargs):
        serializer_context = self.get_serializer_context()
        try:
            # Try to get existing digestate
            digestate = BiomethaneDigestate.objects.get(producer=request.entity, year=request.query_params.get("year"))
            # Update existing digestate
            serializer = BiomethaneDigestatePatchSerializer(
                digestate, data=request.data, partial=True, context=serializer_context
            )
            if serializer.is_valid():
                serializer.save()
                response_data = BiomethaneDigestateSerializer(digestate, context=serializer_context).data
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneDigestate.DoesNotExist:
            # Create new digestate
            serializer = BiomethaneDigestateAddSerializer(data=request.data, context=serializer_context)
            if serializer.is_valid():
                digestate = serializer.save()
                response_data = BiomethaneDigestateSerializer(digestate, context=serializer_context).data
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
