from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.models.biomethane_entity_config_agreement import BiomethaneEntityConfigAgreement
from biomethane.serializers.entity_config_agreement.list import BiomethaneEntityConfigAgreementSerializer


class BiomethaneEntityConfigAgreementListMixin:
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
    @action(detail=False, methods=["get"], url_path="list")
    def list_agreement(self, request, *args, **kwargs):
        try:
            agreement = BiomethaneEntityConfigAgreement.objects.get(entity=request.entity)
            data = BiomethaneEntityConfigAgreementSerializer(agreement).data
            return Response(data)
        except BiomethaneEntityConfigAgreement.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
