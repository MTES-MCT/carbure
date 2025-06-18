from django.db.models import Sum
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from elec.models import ElecProvisionCertificate, ElecTransferCertificate


class BalanceActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        examples=[
            OpenApiExample(
                "Example of assign response.",
                value={},
                request_only=False,
                response_only=True,
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {"balance": {"type": "integer"}},
            }
        },
    )
    @action(methods=["GET"], detail=False)
    def balance(self, request, id=None):
        entity = request.entity
        provisions = ElecProvisionCertificate.objects.filter(cpo=entity)
        transfers = ElecTransferCertificate.objects.filter(supplier=entity)
        total_provision = provisions.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0
        total_transfer = transfers.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0
        return Response({"balance": round(total_provision - total_transfer, 2) or 0})
