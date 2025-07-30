from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.models.biomethane_entity_config_agreement import BiomethaneEntityConfigAgreement
from biomethane.serializers.entity_config_agreement.add import BiomethaneEntityConfigAgreementAddSerializer


class BiomethaneEntityConfigAgreementPatchMixin:
    @extend_schema(
        operation_id="patch_biomethane_entity_config_agreement",
        description="Patch a biomethane entity config agreement",
        request=BiomethaneEntityConfigAgreementAddSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneEntityConfigAgreementAddSerializer, description="The updated agreement."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid input data."),
        },
    )
    @action(detail=False, methods=["patch"], url_path="patch")
    def patch_agreement(self, request, *args, **kwargs):
        agreement = BiomethaneEntityConfigAgreement.objects.get(entity=request.entity)
        serializer = BiomethaneEntityConfigAgreementAddSerializer(agreement, data=request.data, partial=True)

        if not agreement:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
