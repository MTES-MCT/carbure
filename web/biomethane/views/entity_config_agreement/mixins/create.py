from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.models.biomethane_entity_config_agreement import BiomethaneEntityConfigAgreement
from biomethane.serializers.entity_config_agreement.add import BiomethaneEntityConfigAgreementAddSerializer


class BiomethaneEntityConfigAgreementCreateMixin:
    @extend_schema(
        operation_id="create_biomethane_entity_config_agreement",
        description="Create a new agreement.",
        parameters=[
            OpenApiParameter(
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Authorised entity ID.",
                required=True,
            ),
        ],
        request=BiomethaneEntityConfigAgreementAddSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneEntityConfigAgreementAddSerializer, description="The newly created agreement."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid input data."),
        },
    )
    @action(detail=False, methods=["post"], url_path="agreement")
    def create_agreement(self, request, *args, **kwargs):
        serializer = BiomethaneEntityConfigAgreementAddSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        validated_data["entity"] = request.entity

        BiomethaneEntityConfigAgreement.objects.create(**validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
